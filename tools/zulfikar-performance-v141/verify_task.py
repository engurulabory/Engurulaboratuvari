"""Reopens each actual task artifact in a separate process; no DÖM imports."""
import hashlib,json,sqlite3,subprocess,sys,zipfile
from pathlib import Path
p=Path(sys.argv[1]);i=int(sys.argv[2]);r=json.loads((p/'task-result.json').read_text())
assert r['pass'] is True and all(r['semanticChecks']) and r['ADVERSARIAL']['faultObserved'] is True
if i==1:
 for arg,result in [('[2,3,7]','12'),('[]','0'),('[-3,1]','-2')]:
  x=subprocess.run([sys.executable,'-B',str(p/'total.py'),arg],capture_output=True,text=True,timeout=10)
  assert x.returncode==0 and x.stdout.strip()==result
elif i==2:
 for name in ('tasks.sqlite','crash.sqlite'):
  c=sqlite3.connect(f'file:{p/name}?mode=ro',uri=True)
  assert c.execute('select count(*),sum(value) from rows').fetchone()==(3,12)
  assert c.execute('select count(*) from operations').fetchone()==(1,)
  assert c.execute('pragma integrity_check').fetchone()==('ok',);c.close()
elif i==3:
 with zipfile.ZipFile(p/'handoff.zip') as z:
  assert z.namelist()==['goal.txt','result.txt'] and z.read('result.txt')==b'12' and z.read('goal.txt')==b'fixed target'
elif i==4:
 assert (p/'output.txt').read_text()=='12'
 assert r['ADVERSARIAL']['staleOutputRejected'] is True
 assert r['REPAIR_RETEST'][0]['replayedVerifiedCheckpoint'] is True
 e=json.loads((p/'dom-events.jsonl').read_text())
 assert e['payload']['artifactSha256']==hashlib.sha256((p/'output.txt').read_bytes()).hexdigest()
elif i==5:
 assert (p/'output.txt').read_text()=='actual output'
 assert [x['state'] for x in r['ADVERSARIAL']['observations']]==['EVIDENCE_HOLD','EVIDENCE_HOLD','COMPLETION_HOLD','FINISH_HOLD']
else:raise AssertionError('unknown task')
print('ACTUAL_PERSISTED_TASK_OUTPUT_VERIFIED')
