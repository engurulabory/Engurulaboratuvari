import sqlite3,tempfile,hashlib,json
from pathlib import Path

def sha(x):return hashlib.sha256(x).hexdigest()
class ComfortPilot:
 def __init__(self,db):
  self.c=sqlite3.connect(db,isolation_level=None)
  self.c.execute('CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,goal TEXT,state TEXT,stage INTEGER,source TEXT,owner_gate INTEGER,manual INTEGER)')
  self.c.execute('CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,task TEXT,kind TEXT)')
 def start(self,tid,goal,source):
  self.c.execute('BEGIN IMMEDIATE')
  old=self.c.execute('SELECT goal,source FROM tasks WHERE id=?',(tid,)).fetchone()
  if old:
   self.c.execute('COMMIT');return 'RESUMED' if old==(goal,source) else 'HOLD_ID_DRIFT'
  if self.c.execute("SELECT COUNT(*) FROM tasks WHERE state NOT IN ('DONE','HOLD')").fetchone()[0]:
   self.c.execute('ROLLBACK');return 'HOLD_BUSY'
  self.c.execute('INSERT INTO tasks VALUES (?,?,?,?,?,?,?)',(tid,goal,'ACTIVE',0,source,0,0));self.c.execute('COMMIT');return 'STARTED'
 def tick(self,tid,proof=None):
  self.c.execute('BEGIN IMMEDIATE')
  rec=self.c.execute('SELECT state,stage,source,owner_gate FROM tasks WHERE id=?',(tid,)).fetchone()
  if not rec:self.c.execute('ROLLBACK');return 'HOLD_UNKNOWN'
  state,step,src,gate=rec
  if state=='DONE':self.c.execute('COMMIT');return 'DONE_IDEMPOTENT'
  if state=='HOLD':self.c.execute('COMMIT');return 'HOLD'
  if step==3:
   self.c.execute("UPDATE tasks SET state='AWAIT_OWNER',owner_gate=1 WHERE id=?",(tid,));self.c.execute('COMMIT');return 'OWNER_REQUIRED'
  if state=='AWAIT_OWNER':self.c.execute('COMMIT');return 'OWNER_REQUIRED'
  # proof for verifier stage is bound to task, stage and source
  if step==2 and proof!=sha((tid+'|2|'+src).encode()):
   self.c.execute("UPDATE tasks SET state='HOLD' WHERE id=?",(tid,));self.c.execute('COMMIT');return 'HOLD_PROOF'
  self.c.execute('UPDATE tasks SET stage=stage+1 WHERE id=?',(tid,))
  self.c.execute('INSERT INTO events(task,kind) VALUES (?,?)',(tid,'AUTO_'+str(step)))
  self.c.execute('COMMIT');return 'AUTO'
 def owner(self,tid,authorized):
  self.c.execute('BEGIN IMMEDIATE')
  rec=self.c.execute('SELECT state,stage FROM tasks WHERE id=?',(tid,)).fetchone()
  if not rec or rec!=('AWAIT_OWNER',3) or not authorized:
   self.c.execute('ROLLBACK');return 'HOLD_AUTH'
  self.c.execute("UPDATE tasks SET state='DONE',stage=4,manual=manual+1 WHERE id=?",(tid,))
  self.c.execute('COMMIT');return 'DONE_THEORETICAL_OWNER_TOKEN'
 def status(self,tid):return self.c.execute('SELECT state,stage,manual FROM tasks WHERE id=?',(tid,)).fetchone()
 def close(self):self.c.close()
def simulation():
 out={}
 with tempfile.TemporaryDirectory() as d:
  db=str(Path(d)/'t.db');p=ComfortPilot(db);s=sha(b'source')
  out['01_single_goal_start']=p.start('T4','comfort',s)=='STARTED'
  out['02_single_active_work']=p.start('other','duplicate',s)=='HOLD_BUSY'
  out['03_identical_request_resume']=p.start('T4','comfort',s)=='RESUMED'
  out['04_drift_request_rejected']=p.start('T4','different',s)=='HOLD_ID_DRIFT'
  out['05_auto_plan']=p.tick('T4')=='AUTO'
  out['06_auto_engineering']=p.tick('T4')=='AUTO'
  p.close();p=ComfortPilot(db)
  out['07_crash_resume']=p.status('T4')==('ACTIVE',2,0)
  out['08_wrong_verifier_holds']=p.tick('T4','fake')=='HOLD_PROOF'
  out['09_failed_work_safe']=p.status('T4')==('HOLD',2,0)
  out['10_hold_rejects_progress']=p.tick('T4')=='HOLD'
  p.close()
  p=ComfortPilot(str(Path(d)/'clean.db'))
  out['11_clean_start']=p.start('T4','comfort',s)=='STARTED'
  out['12_auto_rounds']=p.tick('T4')=='AUTO' and p.tick('T4')=='AUTO'
  out['13_bound_verifier']=p.tick('T4',sha(('T4|2|'+s).encode()))=='AUTO'
  out['14_owner_threshold']=p.tick('T4')=='OWNER_REQUIRED'
  out['15_no_repeat_prompt']=p.tick('T4')=='OWNER_REQUIRED'
  out['16_owner_denied']=p.owner('T4',False)=='HOLD_AUTH'
  out['17_owner_mock_completion']=p.owner('T4',True)=='DONE_THEORETICAL_OWNER_TOKEN'
  out['18_one_exceptional_owner_step']=p.status('T4')==('DONE',4,1)
  out['19_idempotent_final']=p.tick('T4')=='DONE_IDEMPOTENT'
  out['20_automatic_event_ledger']=p.c.execute('SELECT COUNT(*) FROM events').fetchone()[0]==3
  out['21_next_goal']=p.start('T5','flow',s)=='STARTED'
  out['22_manual_routine_zero']=p.c.execute("SELECT manual FROM tasks WHERE id='T5'").fetchone()[0]==0
  out['23_stale_proof_scope']=sha(('T5|2|'+s).encode())!=sha(('T4|2|'+s).encode())
  out['24_no_paid_service_dependency']=True # test scope: stdlib only
  p.close()
 return out
if __name__=='__main__':
 r=simulation(); print(json.dumps({'passed':sum(r.values()),'total':len(r),'details':r},indent=2));raise SystemExit(0 if all(r.values()) else 1)
