"""ENGURU V6.9 Target 10: deterministic orchestration theoretical verifier.
No real owner authority, GitHub mutation or OSi deployment.
"""
import hashlib,json,sqlite3,os,tempfile
from pathlib import Path
GOALS=('architecture','execution','finish','comfort','flow','security','osi_readiness','engineering','internal_integration')
CANONICAL=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
SHA=lambda b:hashlib.sha256(b).hexdigest()

class Pilot:
 def __init__(self,db):
  self.c=sqlite3.connect(str(db),isolation_level=None,timeout=4)
  self.c.execute('PRAGMA journal_mode=WAL')
  self.c.execute('CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY,goal INTEGER,kind TEXT,payload TEXT,prev TEXT,digest TEXT UNIQUE)')
  self.c.execute('CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1), active INTEGER, revision INTEGER)')
  self.c.execute('INSERT OR IGNORE INTO state VALUES(1,1,0)')
 def append(self,goal,kind,payload):
  self.c.execute('BEGIN IMMEDIATE')
  try:
   active,revision=self.c.execute('SELECT active,revision FROM state WHERE id=1').fetchone()
   if goal!=active or goal>9: self.c.execute('ROLLBACK');return 'HOLD_ORDER'
   if kind not in ('PROOF','FINISH','HOLD','REPAIR'):self.c.execute('ROLLBACK');return 'HOLD_KIND'
   if kind=='FINISH':
    last=self.c.execute('SELECT kind FROM events WHERE goal=? ORDER BY seq DESC LIMIT 1',(goal,)).fetchone()
    if last is None or last[0]!='PROOF' or payload.get('source')!=SHA(('source:'+GOALS[goal-1]).encode()) or payload.get('verifier')!='TEST_ONLY_VERIFIED':
     self.c.execute('ROLLBACK');return 'HOLD_EVIDENCE'
   if kind=='PROOF' and (payload.get('source')!=SHA(('source:'+GOALS[goal-1]).encode()) or payload.get('receipt')!=SHA(('proof:'+GOALS[goal-1]).encode())):
    self.c.execute('ROLLBACK');return 'HOLD_SOURCE'
   if kind=='REPAIR':
    last=self.c.execute('SELECT kind FROM events WHERE goal=? ORDER BY seq DESC LIMIT 1',(goal,)).fetchone()
    if last is None or last[0]!='HOLD':self.c.execute('ROLLBACK');return 'HOLD_REPAIR'
   if kind=='FINISH':
    self.c.execute('UPDATE state SET active=active+1,revision=revision+1 WHERE id=1')
   else:self.c.execute('UPDATE state SET revision=revision+1 WHERE id=1')
   prevrow=self.c.execute('SELECT digest FROM events ORDER BY seq DESC LIMIT 1').fetchone()
   prev=prevrow[0] if prevrow else '0'*64
   seq=self.c.execute('SELECT COALESCE(MAX(seq),0)+1 FROM events').fetchone()[0]
   entry={'seq':seq,'goal':goal,'kind':kind,'payload':payload,'prev':prev}
   digest=SHA(CANONICAL(entry))
   self.c.execute('INSERT INTO events VALUES(?,?,?,?,?,?)',(seq,goal,kind,CANONICAL(payload).decode(),prev,digest))
   self.c.execute('COMMIT');return 'PASS'
  except BaseException:
   self.c.execute('ROLLBACK');raise
 def snapshot(self):
  return {'state':self.c.execute('SELECT active,revision FROM state WHERE id=1').fetchone(),'events':self.c.execute('SELECT seq,goal,kind,payload,prev,digest FROM events ORDER BY seq').fetchall()}
 def audit(self):
  rows=self.snapshot()['events'];prev='0'*64
  for seq,goal,kind,p,pr,d in rows:
   try: payload=json.loads(p)
   except (ValueError,TypeError):return False
   if pr!=prev or SHA(CANONICAL({'seq':seq,'goal':goal,'kind':kind,'payload':payload,'prev':pr}))!=d:return False
   prev=d
  return True
 def close(self):self.c.close()

def proof(i):return {'source':SHA(('source:'+GOALS[i-1]).encode()),'receipt':SHA(('proof:'+GOALS[i-1]).encode())}
def finish(i):return {'source':proof(i)['source'],'verifier':'TEST_ONLY_VERIFIED'}

def trial():
 checks={}
 with tempfile.TemporaryDirectory() as td:
  path=Path(td)/'pilot.db';p=Pilot(path)
  checks['01_initial'] = p.snapshot()['state']==(1,0)
  checks['02_out_of_order']=p.append(2,'PROOF',proof(2))=='HOLD_ORDER'
  checks['03_no_proof_finish']=p.append(1,'FINISH',finish(1))=='HOLD_EVIDENCE'
  checks['04_wrong_source']=p.append(1,'PROOF',{'source':'0'*64,'receipt':proof(1)['receipt']})=='HOLD_SOURCE'
  checks['05_first_proof']=p.append(1,'PROOF',proof(1))=='PASS'
  checks['06_wrong_verifier']=p.append(1,'FINISH',{'source':proof(1)['source'],'verifier':'OWNER_APPROVED'})=='HOLD_EVIDENCE'
  checks['07_first_finish']=p.append(1,'FINISH',finish(1))=='PASS'
  checks['08_double_finish']=p.append(1,'FINISH',finish(1))=='HOLD_ORDER'
  p.close();p=Pilot(path)
  checks['09_restart']=p.snapshot()['state'][0]==2
  checks['10_chain_valid']=p.audit()
  checks['11_hold']=p.append(2,'HOLD',{'reason':'SOURCE_DRIFT'})=='PASS'
  checks['12_finish_blocked_after_hold']=p.append(2,'FINISH',finish(2))=='HOLD_EVIDENCE'
  checks['13_repair']=p.append(2,'REPAIR',{'fixed':'TEST_ONLY'})=='PASS'
  checks['14_repaired_proof']=p.append(2,'PROOF',proof(2))=='PASS'
  checks['15_repaired_finish']=p.append(2,'FINISH',finish(2))=='PASS'
  checks['16_no_early_goal4']=p.append(4,'PROOF',proof(4))=='HOLD_ORDER'
  results=[]
  for i in range(3,10):
   results.append(p.append(i,'PROOF',proof(i))=='PASS' and p.append(i,'FINISH',finish(i))=='PASS')
  checks['17_nine_in_order']=all(results)
  checks['18_closed']=p.snapshot()['state'][0]==10
  checks['19_no_tenth_capability']=len(GOALS)==9 and p.append(10,'PROOF',{})=='HOLD_ORDER'
  checks['20_audit_end']=p.audit()
  stable=p.snapshot();p.close();p=Pilot(path)
  checks['21_reboot_determinism']=p.snapshot()==stable
  checks['22_no_extra_operator']=p.append(1,'PROOF',proof(1))=='HOLD_ORDER'
  checks['23_no_osi_claim']='osi_installed' not in str(p.snapshot())
  checks['24_revision_consistency']=p.snapshot()['state'][1]==len(p.snapshot()['events'])
  checks['25_exact_event_count']=len(p.snapshot()['events'])==20
  checks['26_same_digest_on_canonical_data']=SHA(CANONICAL({'a':1,'b':2}))==SHA(CANONICAL({'b':2,'a':1}))
  last=p.snapshot()['events'][-1];p.close()
  conn=sqlite3.connect(path);conn.execute('UPDATE events SET payload=? WHERE seq=?',('tampered',last[0]));conn.commit();conn.close()
  p=Pilot(path);checks['27_tamper_detected']=not p.audit();p.close()
 return checks
if __name__=='__main__':
 for n in range(1,4):
  checks=trial();print('ROUND',n,sum(checks.values()),'/',len(checks))
  for k,v in checks.items():
   if not v:print('FAIL',k)
  if not all(checks.values()):raise SystemExit(1)
 print('STATE=PASS_BOUNDED_THEORETICAL_TARGET10')
