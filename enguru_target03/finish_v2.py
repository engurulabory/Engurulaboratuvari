"""ENGURU target-03 isolated theoretical finish simulation. No owner authority."""
import sqlite3, hashlib, json, tempfile, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def h(b):return hashlib.sha256(b).hexdigest()
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':')).encode()
class Finish:
 def __init__(self,path,pub):
  self.db=sqlite3.connect(path,timeout=10,isolation_level=None,check_same_thread=False)
  self.db.execute('PRAGMA busy_timeout=10000')
  self.db.execute('CREATE TABLE IF NOT EXISTS goals(n INTEGER PRIMARY KEY,status TEXT NOT NULL,pin TEXT NOT NULL,receipt TEXT,decision TEXT,epoch INTEGER NOT NULL DEFAULT 0)')
  self.pub=pub
 def seed(self):
  self.db.execute('BEGIN IMMEDIATE')
  for n in range(1,10):self.db.execute('INSERT OR IGNORE INTO goals(n,status,pin) VALUES(?,?,?)',(n,'READY' if n==1 else 'QUEUED',h(f'goal-{n}'.encode())))
  self.db.execute('COMMIT')
 def item(self,n):return self.db.execute('SELECT status,pin,receipt,epoch FROM goals WHERE n=?',(n,)).fetchone()
 def active(self):return [v[0] for v in self.db.execute("SELECT n FROM goals WHERE status='READY'")]
 def finish(self,n,source,raw,receipt,sig):
  self.db.execute('BEGIN IMMEDIATE')
  try:
   row=self.item(n)
   if row is None or row[0]!='READY' or row[1]!=source or receipt.get('task')!=n or receipt.get('source_sha')!=source or receipt.get('evidence_sha')!=h(raw) or receipt.get('epoch')!=row[3] or receipt.get('scope')!='TEST_ONLY_VERIFIER':
    self.db.execute('ROLLBACK');return 'HOLD'
   try:self.pub.verify(sig,canon(receipt))
   except (InvalidSignature,ValueError,TypeError):self.db.execute('ROLLBACK');return 'HOLD'
   self.db.execute('UPDATE goals SET status=?,receipt=?,decision=? WHERE n=?',('SIM_PASS',h(canon(receipt)),'THEORETICAL_ONLY',n))
   self.db.execute("UPDATE goals SET status='READY' WHERE n=? AND status='QUEUED'",(n+1,))
   self.db.execute('COMMIT');return 'PASS'
  except Exception:
   self.db.execute('ROLLBACK');raise
 def drift(self,n,newpin):
  self.db.execute('BEGIN IMMEDIATE')
  self.db.execute("UPDATE goals SET pin=?,receipt=NULL,decision=NULL,status='READY',epoch=epoch+1 WHERE n=?",(newpin,n))
  self.db.execute("UPDATE goals SET status='QUEUED',receipt=NULL,decision=NULL,epoch=epoch+1 WHERE n>?",(n,))
  self.db.execute('COMMIT')
 def close(self):self.db.close()

def one_round():
 checks={};sk=Ed25519PrivateKey.generate();pub=sk.public_key()
 with tempfile.TemporaryDirectory() as d:
  db=str(Path(d)/'finish.sqlite');p=Finish(db,pub);p.seed();r=p.item(1);raw=b'finishing data'
  receipt={'task':1,'source_sha':r[1],'evidence_sha':h(raw),'epoch':r[3],'scope':'TEST_ONLY_VERIFIER'};sig=sk.sign(canon(receipt))
  checks['01_no_unverified']=p.finish(1,r[1],raw,receipt,b'0'*64)=='HOLD'
  checks['02_wrong_bytes']=p.finish(1,r[1],raw+b'bad',receipt,sig)=='HOLD'
  checks['03_wrong_source']=p.finish(1,'0'*64,raw,receipt,sig)=='HOLD'
  checks['04_wrong_scope']=p.finish(1,r[1],raw,{**receipt,'scope':'OWNER_APPROVED'},sig)=='HOLD'
  checks['05_wrong_signer']=p.finish(1,r[1],raw,receipt,Ed25519PrivateKey.generate().sign(canon(receipt)))=='HOLD'
  p.close();gate=threading.Barrier(2)
  def worker():
   z=Finish(db,pub);gate.wait();v=z.finish(1,r[1],raw,receipt,sig);z.close();return v
  with ThreadPoolExecutor(max_workers=2) as ex:
   futures=[ex.submit(worker) for _ in range(2)];res=[x.result() for x in futures]
  checks['06_atomic_race']=sorted(res)==['HOLD','PASS']
  p=Finish(db,pub);checks['07_next_only']=p.active()==[2]
  checks['08_duplicate_hold']=p.finish(1,r[1],raw,receipt,sig)=='HOLD'
  p.close();p=Finish(db,pub);checks['09_restart']=p.active()==[2]
  checks['10_nine_goals']=True
  for n in range(2,10):
   row=p.item(n);data=f'complete {n}'.encode();proof={'task':n,'source_sha':row[1],'evidence_sha':h(data),'epoch':row[3],'scope':'TEST_ONLY_VERIFIER'}
   if p.finish(n,row[1],data,proof,sk.sign(canon(proof)))!='PASS':checks['10_nine_goals']=False
  checks['11_nine_pass']=p.db.execute("SELECT COUNT(*) FROM goals WHERE status='SIM_PASS'").fetchone()[0]==9
  checks['12_no_next_goal']=p.active()==[]
  old_row=p.item(4);p.drift(4,h(b'new4'));checks['13_drift_reopen']=p.active()==[4]
  checks['14_downstream_invalidated']=p.db.execute("SELECT COUNT(*) FROM goals WHERE n>4 AND status='QUEUED'").fetchone()[0]==5
  oldproof={'task':4,'source_sha':old_row[1],'evidence_sha':h(b'old'),'epoch':old_row[3],'scope':'TEST_ONLY_VERIFIER'}
  checks['15_replay_protection']=p.finish(4,old_row[1],b'old',oldproof,sk.sign(canon(oldproof)))=='HOLD'
  checks['16_no_owner_authority']=p.db.execute("SELECT COUNT(*) FROM goals WHERE decision='OWNER_APPROVED'").fetchone()[0]==0
  for n in range(4,10):
   row=p.item(n);data=f'recovered-{n}'.encode();proof={'task':n,'source_sha':row[1],'evidence_sha':h(data),'epoch':row[3],'scope':'TEST_ONLY_VERIFIER'}
   if p.finish(n,row[1],data,proof,sk.sign(canon(proof)))!='PASS':checks['17_recovered_sequence']=False;break
  else:checks['17_recovered_sequence']=True
  checks['18_all_reclosed']=p.db.execute("SELECT COUNT(*) FROM goals WHERE status='SIM_PASS'").fetchone()[0]==9
  p.close()
 return checks
if __name__=='__main__':
 overall=True
 for i in range(1,4):
  x=one_round();ok=sum(x.values());overall &= all(x.values());print(f'ROUND={i} PASS={ok}/{len(x)} FAIL={[k for k,v in x.items() if not v]}')
 print('TARGET03_SIMULATION='+('PASS' if overall else 'HOLD'))
 raise SystemExit(0 if overall else 1)
