"""ENGURU T02 theoretical executable model. Test-only Ed25519; no canonical authority."""
import concurrent.futures
import hashlib
import json
import sqlite3
import tempfile
import threading
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def sha(data): return hashlib.sha256(data).hexdigest()
def canon(data): return json.dumps(data,sort_keys=True,separators=(',',':')).encode()

class Pilot:
 def __init__(self,path):
  self.db=sqlite3.connect(path,timeout=10,isolation_level=None,check_same_thread=False)
  self.db.execute('PRAGMA journal_mode=WAL')
  self.db.execute('CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, deps TEXT NOT NULL, source TEXT NOT NULL, state TEXT NOT NULL, lease_owner TEXT, lease_until INTEGER, generation INTEGER NOT NULL DEFAULT 0, receipt TEXT)')
  self.db.execute('CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,task TEXT NOT NULL,kind TEXT NOT NULL,body TEXT NOT NULL,prev TEXT NOT NULL,hash TEXT NOT NULL)')
 def event(self,tid,kind,body):
  prev=self.db.execute('SELECT hash FROM events ORDER BY seq DESC LIMIT 1').fetchone()
  prev=prev[0] if prev else '0'*64
  seq=self.db.execute('SELECT COALESCE(MAX(seq),0)+1 FROM events').fetchone()[0]
  h=sha(canon(dict(seq=seq,task=tid,kind=kind,body=body,prev=prev)))
  self.db.execute('INSERT INTO events(seq,task,kind,body,prev,hash) VALUES(?,?,?,?,?,?)',(seq,tid,kind,body,prev,h))
 def ledger_ok(self):
  prev='0'*64
  for seq,tid,kind,body,prior,h in self.db.execute('SELECT seq,task,kind,body,prev,hash FROM events ORDER BY seq'):
   if prior!=prev or h!=sha(canon(dict(seq=seq,task=tid,kind=kind,body=body,prev=prev))):return False
   prev=h
  return True
 def add(self,tid,deps,source):
  if not isinstance(source,str) or len(source)!=64 or any(c not in '0123456789abcdef' for c in source):return 'HOLD_SOURCE'
  if tid in deps or len(set(deps))!=len(deps):return 'HOLD_CYCLE'
  self.db.execute('BEGIN IMMEDIATE')
  try:
   existing={r[0] for r in self.db.execute('SELECT id FROM tasks')}
   if not set(deps)<=existing:self.db.execute('ROLLBACK');return 'HOLD_DEPENDENCY'
   if self.db.execute('SELECT 1 FROM tasks WHERE id=?',(tid,)).fetchone():self.db.execute('ROLLBACK');return 'HOLD_DUPLICATE'
   self.db.execute('INSERT INTO tasks(id,deps,source,state) VALUES(?,?,?,?)',(tid,json.dumps(deps),source,'READY'))
   self.event(tid,'REGISTER',source)
   self.db.execute('COMMIT');return 'READY'
  except Exception:
   self.db.execute('ROLLBACK');raise
 def claim(self,tid,worker,now,ttl=30):
  self.db.execute('BEGIN IMMEDIATE')
  row=self.db.execute('SELECT deps,state,lease_until,generation FROM tasks WHERE id=?',(tid,)).fetchone()
  if not row or ttl<=0 or (row[1]=='RUNNING' and (row[2] is None or row[2]>now)) or row[1]=='THEORETICAL_PASS':self.db.execute('ROLLBACK');return None
  deps=json.loads(row[0])
  if any(self.db.execute('SELECT state FROM tasks WHERE id=?',(d,)).fetchone()[0]!='THEORETICAL_PASS' for d in deps):self.db.execute('ROLLBACK');return None
  if row[1] not in ('READY','RUNNING'):self.db.execute('ROLLBACK');return None
  # One active task at a time across this Pilot.
  if self.db.execute("SELECT 1 FROM tasks WHERE id<>? AND state='RUNNING' AND lease_until>?",(tid,now)).fetchone():self.db.execute('ROLLBACK');return None
  gen=row[3]+1
  self.db.execute('UPDATE tasks SET state=?,lease_owner=?,lease_until=?,generation=? WHERE id=?',('RUNNING',worker,now+ttl,gen,tid))
  self.event(tid,'CLAIM',json.dumps([worker,gen],separators=(',',':')))
  self.db.execute('COMMIT');return gen
 def finish(self,tid,worker,generation,now,source,raw,receipt,public):
  self.db.execute('BEGIN IMMEDIATE')
  row=self.db.execute('SELECT state,lease_owner,generation,lease_until,source FROM tasks WHERE id=?',(tid,)).fetchone()
  if not row or row!=('RUNNING',worker,generation,row[3],source) or row[3] is None or now>=row[3]:
   self.db.execute('ROLLBACK');return 'HOLD_LEASE_OR_SOURCE'
  expected={'task':tid,'generation':generation,'source_sha256':source,'artifact_sha256':sha(raw),'verifier_scope':'THEORETICAL_TEST_ONLY'}
  if not isinstance(receipt,dict) or receipt.get('payload')!=expected or not isinstance(receipt.get('signature'),bytes):
   self.db.execute('ROLLBACK');return 'HOLD_RECEIPT'
  try: public.verify(receipt['signature'],canon(expected))
  except (InvalidSignature,ValueError,TypeError):self.db.execute('ROLLBACK');return 'HOLD_SIGNATURE'
  rh=sha(canon(expected)+receipt['signature'])
  self.db.execute('UPDATE tasks SET state=?,lease_owner=NULL,lease_until=NULL,receipt=? WHERE id=?',('THEORETICAL_PASS',rh,tid))
  self.event(tid,'THEORETICAL_PASS',rh)
  self.db.execute('COMMIT');return 'PASS'
 def close(self):self.db.close()

def receipt(key,tid,gen,src,raw):
 payload={'task':tid,'generation':gen,'source_sha256':src,'artifact_sha256':sha(raw),'verifier_scope':'THEORETICAL_TEST_ONLY'}
 return {'payload':payload,'signature':key.sign(canon(payload))}

def simulate():
 result={}
 with tempfile.TemporaryDirectory() as temp:
  db=str(Path(temp)/'pilot.db');src=sha(b'EXACT_SOURCE');key=Ed25519PrivateKey.generate();wrong=Ed25519PrivateKey.generate()
  a=Pilot(db)
  result['01_register']=a.add('A',[],src)=='READY'
  result['02_dag_unknown_dependency']=a.add('X',['Z'],src)=='HOLD_DEPENDENCY'
  result['03_dag_self_cycle']=a.add('X',['X'],src)=='HOLD_CYCLE'
  result['04_duplicate_blocked']=a.add('A',[],src)=='HOLD_DUPLICATE'
  result['05_dependency_registered']=a.add('B',['A'],src)=='READY'
  result['06_dependency_blocks_claim']=a.claim('B','w',100) is None
  a.close()
  gate=threading.Barrier(2)
  def race(w):
   p=Pilot(db);gate.wait();g=p.claim('A',w,100);p.close();return g
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   fut=[pool.submit(race,w) for w in ['w1','w2']];out=[f.result() for f in fut]
  result['07_two_real_sqlite_connections_single_winner']=sum(x is not None for x in out)==1
  winner='w1' if out[0] else 'w2';generation=next(x for x in out if x)
  p=Pilot(db)
  result['08_same_pilot_single_active']=p.claim('B','other',100) is None
  result['09_wrong_worker']=p.finish('A','wrong',generation,110,src,b'proof',receipt(key,'A',generation,src,b'proof'),key.public_key())=='HOLD_LEASE_OR_SOURCE'
  result['10_tampered_bytes']=p.finish('A',winner,generation,110,src,b'tamper',receipt(key,'A',generation,src,b'proof'),key.public_key())=='HOLD_RECEIPT'
  result['11_wrong_source']=p.finish('A',winner,generation,110,'0'*64,b'proof',receipt(key,'A',generation,src,b'proof'),key.public_key())=='HOLD_LEASE_OR_SOURCE'
  result['12_wrong_key']=p.finish('A',winner,generation,110,src,b'proof',receipt(wrong,'A',generation,src,b'proof'),key.public_key())=='HOLD_SIGNATURE'
  result['13_no_early_reclaim']=p.claim('A','w3',120) is None
  p.close();p=Pilot(db)
  result['14_restart_keeps_running']=p.db.execute("SELECT state FROM tasks WHERE id='A'").fetchone()[0]=='RUNNING'
  generation2=p.claim('A','w3',131)
  result['15_expired_lease_recovery']=generation2==generation+1
  result['16_fencing_old_worker']=p.finish('A',winner,generation,132,src,b'proof',receipt(key,'A',generation,src,b'proof'),key.public_key())=='HOLD_LEASE_OR_SOURCE'
  result['17_finish_current_owner']=p.finish('A','w3',generation2,132,src,b'proof',receipt(key,'A',generation2,src,b'proof'),key.public_key())=='PASS'
  result['18_idempotent_duplicate_finish']=p.finish('A','w3',generation2,132,src,b'proof',receipt(key,'A',generation2,src,b'proof'),key.public_key())=='HOLD_LEASE_OR_SOURCE'
  genb=p.claim('B','w4',140)
  result['19_dag_unblocked']=genb==1
  result['20_second_task_pass']=p.finish('B','w4',genb,141,src,b'Bproof',receipt(key,'B',genb,src,b'Bproof'),key.public_key())=='PASS'
  result['21_chained_ledger_integrity']=p.ledger_ok()
  p.db.execute("UPDATE events SET body='tampered' WHERE seq=1")
  result['22_ledger_tampering_detected']=not p.ledger_ok()
  result['23_theory_never_owner_pass']=all(r[0]=='THEORETICAL_PASS' for r in p.db.execute('SELECT state FROM tasks'))
  p.close()
 return result

if __name__=='__main__':
 for i in range(1,4):
  r=simulate();print('ROUND',i,'PASS',sum(r.values()),'/',len(r));[print(('PASS' if v else 'FAIL'),k) for k,v in r.items() if not v]
  if not all(r.values()):raise SystemExit(1)
 print('STATE=PASS_BOUNDED_TARGET02_V2; CANONICAL_OWNER=HOLD; OSI_MUTATION=0')
