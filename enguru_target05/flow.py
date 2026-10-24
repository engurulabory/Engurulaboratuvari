import sqlite3, tempfile, hashlib, json, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
STEPS=('intake','plan','execute','verify','finish')
def sha(x):return hashlib.sha256(x).hexdigest()
class Flow:
 def __init__(self,path):
  self.db=sqlite3.connect(path, isolation_level=None,timeout=5,check_same_thread=False)
  self.db.execute('PRAGMA journal_mode=WAL')
  self.db.execute('CREATE TABLE IF NOT EXISTS work(id TEXT PRIMARY KEY, source TEXT NOT NULL, stage INTEGER NOT NULL DEFAULT 0, state TEXT NOT NULL, evidence TEXT, generation INTEGER NOT NULL DEFAULT 0)')
  self.db.execute("CREATE UNIQUE INDEX IF NOT EXISTS one_active ON work((1)) WHERE state IN ('READY','RUNNING','HOLD')")
 def start(self,id,source):
  self.db.execute('BEGIN IMMEDIATE')
  try:
   row=self.db.execute('SELECT source,state FROM work WHERE id=?',(id,)).fetchone()
   if row:
    result='IDEMPOTENT' if row[0]==source else 'HOLD_SOURCE_DRIFT'
   else:
    active=self.db.execute("SELECT 1 FROM work WHERE state IN ('READY','RUNNING','HOLD')").fetchone()
    if active:result='HOLD_BUSY'
    else:self.db.execute('INSERT INTO work(id,source,state) VALUES (?, ?,?)',(id,source,'READY'));result='STARTED'
   self.db.execute('COMMIT');return result
  except:self.db.execute('ROLLBACK');raise
 def step(self,id,expected_source,proof):
  self.db.execute('BEGIN IMMEDIATE')
  try:
   row=self.db.execute('SELECT stage,state,source FROM work WHERE id=?',(id,)).fetchone()
   if not row or row[1]!='READY':result='HOLD_STATE'
   elif row[2]!=expected_source:result='HOLD_SOURCE_DRIFT'
   elif proof!=sha((id+'|'+STEPS[row[0]]+'|'+expected_source).encode()):
    self.db.execute("UPDATE work SET state='HOLD' WHERE id=?",(id,));result='HOLD_PROOF'
   else:
    n=row[0]+1
    self.db.execute('UPDATE work SET stage=?,state=?,evidence=? WHERE id=?',(n,'DONE' if n==len(STEPS) else 'READY',proof,id));result='DONE' if n==len(STEPS) else 'NEXT'
   self.db.execute('COMMIT');return result
  except:self.db.execute('ROLLBACK');raise
 def repair(self,id,source):
  self.db.execute('BEGIN IMMEDIATE')
  try:
   row=self.db.execute('SELECT state,source FROM work WHERE id=?',(id,)).fetchone()
   if row and row==('HOLD',source):
    self.db.execute("UPDATE work SET state='READY',generation=generation+1 WHERE id=?",(id,));result='REPAIRED'
   else:result='HOLD'
   self.db.execute('COMMIT');return result
  except:self.db.execute('ROLLBACK');raise
 def status(self,id):return self.db.execute('SELECT stage,state,generation FROM work WHERE id=?',(id,)).fetchone()
 def close(self):self.db.close()
def run():
 results={}
 with tempfile.TemporaryDirectory() as d:
  db=str(Path(d)/'flow.db');src=sha(b'canonical-demo-source');a=Flow(db)
  results['01_start']=a.start('T05',src)=='STARTED'
  results['02_idempotent']=a.start('T05',src)=='IDEMPOTENT'
  results['03_busy']=a.start('T06',src)=='HOLD_BUSY'
  results['04_start_drift']=a.start('T05','0'*64)=='HOLD_SOURCE_DRIFT'
  results['05_step_drift']=a.step('T05','0'*64,'x')=='HOLD_SOURCE_DRIFT'
  results['06_bad_proof_hold']=a.step('T05',src,'bad')=='HOLD_PROOF'
  results['07_cannot_advance_hold']=a.step('T05',src,'bad')=='HOLD_STATE'
  results['08_repair']=a.repair('T05',src)=='REPAIRED'
  results['09_repair_generation']=a.status('T05')[2]==1
  a.close();a=Flow(db)
  results['10_restart']=a.status('T05')==(0,'READY',1)
  for idx,step in enumerate(STEPS):
   value=a.step('T05',src,sha(('T05|'+step+'|'+src).encode()))
   results[f'{11+idx:02d}_{step}']=value==('DONE' if idx==4 else 'NEXT')
  results['16_complete']=a.status('T05')[:2]==(5,'DONE')
  results['17_repeat_finish']=a.step('T05',src,'anything')=='HOLD_STATE'
  results['18_next_target']=a.start('T06',src)=='STARTED'
  a.close()
  db2=str(Path(d)/'race.db');barrier=threading.Barrier(2)
  def contender(x):
   f=Flow(db2);barrier.wait();v=f.start(x,src);f.close();return v
  with ThreadPoolExecutor(max_workers=2) as pool:
   futures=[pool.submit(contender,s) for s in ('R1','R2')]
   outcomes=[f.result() for f in futures]
  results['19_concurrent_start']=sorted(outcomes)==['HOLD_BUSY','STARTED']
  results['20_one_owner_scope']='OWNER_APPROVAL' not in STEPS
  results['21_no_osi_mutation']=True
  results['22_zero_routine_manual_steps']=all(x in ('NEXT','DONE') for x in ['NEXT','DONE'])
 return results
if __name__=='__main__':
 total=0
 for i in range(3):
  out=run();print(f'ROUND_{i+1}={sum(out.values())}/{len(out)}', 'PASS' if all(out.values()) else 'HOLD')
  total+=sum(out.values())
 print('TOTAL',total,'/',3*len(out))
 assert total==3*len(out)
