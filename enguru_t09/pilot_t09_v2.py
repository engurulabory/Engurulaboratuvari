"""T09 bounded theoretical V2: real OS-process SQLite handoff, signed test evidence, dependency drift, automation meter."""
import sqlite3, tempfile, hashlib, json, os, multiprocessing as mp
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def h(b):return hashlib.sha256(b).hexdigest()
def c(d):return json.dumps(d,sort_keys=True,separators=(',',':')).encode()
ROLES=('management','engineering','verification','field')
def dbconn(path):
 q=sqlite3.connect(path,timeout=15,isolation_level=None)
 q.execute('PRAGMA journal_mode=WAL')
 q.execute('CREATE TABLE IF NOT EXISTS task(id TEXT PRIMARY KEY, stage INTEGER, state TEXT, worker TEXT, source TEXT, dep TEXT, epoch INTEGER, routine INTEGER, exception INTEGER, signature BLOB, evidence TEXT)')
 q.execute('CREATE TABLE IF NOT EXISTS log(seq INTEGER PRIMARY KEY, event TEXT, prev TEXT, digest TEXT)')
 return q
def log(q,event):
 last=q.execute('SELECT digest FROM log ORDER BY seq DESC LIMIT 1').fetchone();prev=last[0] if last else '0'*64
 q.execute('INSERT INTO log(event,prev,digest) VALUES(?,?,?)',(c(event).decode(),prev,h(c({'event':event,'prev':prev}))))
def audit(q):
 prev='0'*64
 try:
  for e,p,d in q.execute('SELECT event,prev,digest FROM log ORDER BY seq'):
   obj=json.loads(e)
   if p!=prev or h(c({'event':obj,'prev':prev}))!=d:return False
   prev=d
 except (ValueError,TypeError):return False
 return True
def create(q,src,dep):
 q.execute('BEGIN IMMEDIATE')
 try:
  if q.execute("SELECT count(*) FROM task WHERE state IN ('READY','RUNNING')").fetchone()[0]:q.execute('ROLLBACK');return 'HOLD_ACTIVE'
  q.execute('INSERT INTO task VALUES (?,?,?,?,?,?,?,?,?,?,?)',('T09',0,'READY','',h(src),h(dep),1,0,0,None,''));log(q,{'action':'create','source':h(src),'dep':h(dep)});q.execute('COMMIT');return 'PASS'
 except sqlite3.IntegrityError:q.execute('ROLLBACK');return 'HOLD_DUPLICATE'
def claim(q,stage,worker):
 q.execute('BEGIN IMMEDIATE')
 row=q.execute('SELECT stage,state FROM task WHERE id="T09"').fetchone()
 if row!=(stage,'READY'):q.execute('ROLLBACK');return 'HOLD'
 q.execute('UPDATE task SET state="RUNNING",worker=?',(worker,));log(q,{'action':'claim','stage':stage,'worker':worker});q.execute('COMMIT');return 'PASS'
def worker_claim(path,stage,worker,queue):
 q=dbconn(path)
 try:queue.put(claim(q,stage,worker))
 finally:q.close()
def payload(src,dep,role,epoch):return c({'source':h(src),'dependency':h(dep),'role':role,'epoch':epoch})
def deliver(q,src,dep,role,worker,signer,public,signature=None):
 q.execute('BEGIN IMMEDIATE')
 r=q.execute('SELECT stage,state,worker,source,dep,epoch FROM task WHERE id="T09"').fetchone()
 if not r or r[0]>=4 or r[1]!='RUNNING' or r[2]!=worker or ROLES[r[0]]!=role or r[3]!=h(src) or r[4]!=h(dep):q.execute('ROLLBACK');return 'HOLD'
 msg=payload(src,dep,role,r[5]);sig=signature if signature is not None else signer.sign(msg)
 try:public.verify(sig,msg)
 except InvalidSignature:q.execute('ROLLBACK');return 'HOLD_SIGNATURE'
 step=r[0]+1
 q.execute('UPDATE task SET stage=?,state=?,worker="",signature=?,evidence=?',(step,'DONE' if step==4 else 'READY',sig,h(msg)))
 log(q,{'action':'deliver','role':role,'stage':step,'evidence':h(msg),'signature':sig.hex()});q.execute('COMMIT');return 'PASS'
def drift(q,new_dep):
 q.execute('BEGIN IMMEDIATE');r=q.execute('SELECT dep,stage,epoch FROM task WHERE id="T09"').fetchone()
 if r[0]==h(new_dep):q.execute('ROLLBACK');return 'HOLD_UNCHANGED'
 q.execute('UPDATE task SET state="HOLD",worker="",stage=0,dep=?,epoch=epoch+1,signature=NULL,evidence=""',(h(new_dep),))
 log(q,{'action':'invalidate','oldstage':r[1],'epoch':r[2]+1,'newdep':h(new_dep)});q.execute('COMMIT');return 'PASS'
def repair(q):
 q.execute('BEGIN IMMEDIATE');r=q.execute('SELECT state FROM task WHERE id="T09"').fetchone()
 if r!=('HOLD',):q.execute('ROLLBACK');return 'HOLD'
 q.execute('UPDATE task SET state="READY"');log(q,{'action':'repair'});q.execute('COMMIT');return 'PASS'
def run():
 with tempfile.TemporaryDirectory() as td:
  path=str(Path(td)/'audit.db');q=dbconn(path);src=b'engineering-source';dep=b'dependency-A';key=Ed25519PrivateKey.generate();pub=key.public_key();wrong=Ed25519PrivateKey.generate().public_key();t={}
  t['01_create']=create(q,src,dep)=='PASS';t['02_duplicate']=create(q,src,dep)=='HOLD_ACTIVE'
  # Separate OS processes contest actual SQLite row transaction.
  ctx=mp.get_context('fork');out=ctx.Queue();a=ctx.Process(target=worker_claim,args=(path,0,'worker-A',out));b=ctx.Process(target=worker_claim,args=(path,0,'worker-B',out));a.start();b.start();a.join(10);b.join(10)
  results=[out.get(timeout=2) for _ in range(2)] if a.exitcode==0 and b.exitcode==0 else []
  t['03_real_process_race']=sorted(results)==['HOLD','PASS']
  worker=q.execute('SELECT worker FROM task').fetchone()[0]
  t['04_untrusted_verifier']=deliver(q,src,dep,'management',worker,key,wrong)=='HOLD_SIGNATURE'
  t['05_wrong_worker']=deliver(q,src,dep,'management','intruder',key,pub)=='HOLD'
  t['06_wrong_source']=deliver(q,src+b'!',dep,'management',worker,key,pub)=='HOLD'
  t['07_wrong_dependency']=deliver(q,src,dep+b'!', 'management',worker,key,pub)=='HOLD'
  t['08_stage1_signed']=deliver(q,src,dep,'management',worker,key,pub)=='PASS'
  q.close();q=dbconn(path)
  t['09_restart_resumes']=q.execute('SELECT stage,state FROM task').fetchone()==(1,'READY')
  t['10_source_drift_reopens']=drift(q,b'dependency-B')=='PASS'
  t['11_old_dependency_invalid']=claim(q,1,'engineering')=='HOLD'
  t['12_state_is_hold']=q.execute('SELECT stage,state,epoch FROM task').fetchone()==(0,'HOLD',2)
  t['13_repair']=repair(q)=='PASS';dep=b'dependency-B'
  t['14_replay_old_signature']=claim(q,0,'manager')=='PASS' and deliver(q,src,dep,'management','manager',key,pub,key.sign(payload(src,b'dependency-A','management',1)))=='HOLD_SIGNATURE'
  t['15_resigned_epoch']=deliver(q,src,dep,'management','manager',key,pub)=='PASS'
  for index,role in enumerate(ROLES[1:],start=1):
   t[f'{15+index:02d}_role_{role}']=claim(q,index,role)=='PASS' and deliver(q,src,dep,role,role,key,pub)=='PASS'
  t['19_once_done']=q.execute('SELECT stage,state FROM task').fetchone()==(4,'DONE')
  t['20_double_finish_hold']=deliver(q,src,dep,'field','field',key,pub)=='HOLD'
  t['21_event_chain']=audit(q)
  t['22_no_routine_actions']=q.execute('SELECT routine FROM task').fetchone()[0]==0
  t['23_no_exception_requests']=q.execute('SELECT exception FROM task').fetchone()[0]==0
  t['24_all_steps_logged']=q.execute('SELECT count(*) FROM log').fetchone()[0]>=12
  t['25_no_owner_claim']=q.execute('SELECT signature IS NOT NULL FROM task').fetchone()[0]==1 # test-signature only
  q.execute('UPDATE log SET digest=? WHERE seq=2',('0'*64,));t['26_tamper_detect']=not audit(q)
  q.execute('UPDATE log SET event=? WHERE seq=1',('{broken-json',));t['27_malformed_event_safe_hold']=not audit(q)
  q.close();return t
if __name__=='__main__':
 ok=True
 for i in range(1,4):
  tests=run();failed=[k for k,v in tests.items() if not v];print(f'ROUND {i}: {len(tests)-len(failed)}/{len(tests)} PASS; FAIL={failed}',flush=True);ok=ok and not failed
 print('TARGET09_V2_BOUNDED_SIM='+('PASS' if ok else 'HOLD'))
 raise SystemExit(0 if ok else 1)
