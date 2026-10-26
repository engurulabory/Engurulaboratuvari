"""Separate mechanism: reopens persisted outputs without DOM imports or repair callbacks."""
import hashlib,json,sqlite3,subprocess,sys,zipfile
from pathlib import Path
p=Path(sys.argv[1]);s=json.loads((p/'summary.json').read_text())
assert s['tasks']==s['passed']==5 and s['verifiedFinish']=='HOLD'
assert [x['taskId'] for x in s['results']]==['R01','R02','R03','R04','R05']
for r in s['results']:
 assert r['pass'] is True and all(r['semanticChecks']) and r['ADVERSARIAL']['faultObserved'] is True
 assert all(k in r for k in ('BASELINE','ADVERSARIAL','REPAIR_RETEST'))
 assert r['domCoordinator']['diagnostic']==100 and r['domCoordinator']['stagePassIssued'] is False
 assert all(x['realTestVerified'] is True for x in r['domCoordinator']['rounds'])
 for phase in ('BASELINE','REPAIR_RETEST'):
  assert r[phase]
# Independently invoke repaired CLI rather than accepting the recorded claim.
for arg,result in [('[2,3,7]','12'),('[]','0'),('[-3,1]','-2')]:
 x=subprocess.run([sys.executable,'-B',str(p/'R01/total.py'),arg],capture_output=True,text=True,timeout=10)
 assert x.returncode==0 and x.stdout.strip()==result
for name in ('tasks.sqlite','crash.sqlite'):
 c=sqlite3.connect(f'file:{p/"R02"/name}?mode=ro',uri=True)
 assert c.execute('select count(*),sum(value) from rows').fetchone()==(3,12)
 assert c.execute('select count(*) from operations').fetchone()==(1,)
 assert c.execute('pragma integrity_check').fetchone()==('ok',);c.close()
with zipfile.ZipFile(p/'R03/handoff.zip') as z:
 assert z.namelist()==['goal.txt','result.txt'] and z.read('result.txt')==b'12' and z.read('goal.txt')==b'fixed target'
r=s['results'][3];assert r['ADVERSARIAL']['staleOutputRejected'] is True
assert (p/'R04/output.txt').read_text()=='12'
assert r['REPAIR_RETEST'][0]['replayedVerifiedCheckpoint'] is True
prior='0'*64;entries=[json.loads(l) for l in (p/'R04/dom-events.jsonl').read_text().splitlines()]
assert len(entries)==1
for i,e in enumerate(entries,1):
 payload={k:v for k,v in e.items() if k!='hash'}
 digest=hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
 assert e['number']==i and e['prior']==prior and e['hash']==digest;prior=digest
assert entries[0]['payload']['artifactSha256']==hashlib.sha256((p/'R04/output.txt').read_bytes()).hexdigest()
f=s['results'][4]['ADVERSARIAL']['observations']
assert [x['state'] for x in f]==['EVIDENCE_HOLD','EVIDENCE_HOLD','COMPLETION_HOLD','FINISH_HOLD']
assert all(x.get('verifiedFinishIssued',False) is False for x in f)
manifest={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.rglob('*')) if f.is_file() and f.name!='independent-verification.json'}
report={'state':'PASS_SEPARATE_MECHANISM_5_TASKS','files':manifest,'humanReviewer':'NOT_AUTHENTICATED','doneCheck':'HOLD','verifiedFinish':'HOLD'}
(p/'independent-verification.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print('PASS: five persisted real outputs, fault records and final journal; official acceptance HOLD')
