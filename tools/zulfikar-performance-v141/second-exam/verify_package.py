"""Read-only evidence verification for a later review session; no task execution or owner issuance."""
import hashlib,json,sys,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def verify(root):
 plan=json.loads((HERE/'PLAN.json').read_text());summary=json.loads((root/'summary.json').read_text())
 assert summary['goalId']==plan['goalId'] and summary['tasksPassed']==3
 assert summary['initialMet']==6 and summary['finalMet']==summary['totalCriteria']==12
 assert summary['planSha256']==digest(HERE/'PLAN.json')
 assert summary['officialVerifiedFinish']=='HOLD'
 for task in plan['tasks']:
  d=root/task['id'];r=json.loads((d/'task-result.json').read_text());contract=json.loads((d/'fixed-task.json').read_text())
  assert r['originalCriteria']==task['criteria'] and contract['task']==task
  assert r['allOriginalCriteriaBound'] and r['openTechnicalItems']==[] and r['pass']
  assert r['sourceContractSha256']==digest(d/'fixed-task.json') and r['outputSha256']==digest(d/'final-output/checks.json')
  assert r['replay']['processObserved'] is False and r['replay']['previousExecutionProof']['processObserved'] is True
  assert r['replay']['executionMode']=='CHECKPOINT_REVALIDATION_NO_NEW_TASK_PROCESS' and r['duplicateTaskProcesses']==0
  data=json.loads((d/'final-output/checks.json').read_text());assert set(data['criteria'])==set(task['criteria']) and all(data['criteria'].values())
  assert data['observations']['regression']['exitCode']==0
  # Recompute journal without importing the engine under review.
  prior='0'*64;events=[json.loads(line) for line in (d/'journal/dom-events.jsonl').read_text().splitlines()]
  assert len(events)==1
  for index,e in enumerate(events,1):
   assert e['number']==index and e['prior']==prior
   assert e['hash']==hashlib.sha256(canonical({k:v for k,v in e.items() if k!='hash'})).hexdigest();prior=e['hash']
   v=e['payload'];assert v['artifactSha256']==r['outputSha256']
   assert digest(d/'journal'/v['artifactSnapshot'])==v['artifactSha256']
   assert v['executionProof']==r['replay']['previousExecutionProof']
  if task['id']=='S01':
   def reject(x):raise ValueError('nonfinite')
   expected={'goalId':'ZF.SECOND.S01','result':'makbuz doğru ve kalıcı','value':12}
   assert json.loads((d/'final-output/receipts/task/result.json').read_text(),parse_constant=reject)==expected
   assert not list((d/'final-output/receipts/invalid').glob('*.json'))
  elif task['id']=='S02':
   inventory=json.loads((d/'final-output/inventory.json').read_text());assert inventory['task_count']==3 and inventory['independently_accepted']==0
   assert all(x['state']=='HOLD_GUVENLI_DUR' for x in data['observations']['cycles']+data['observations']['malformed'])
  else:
   with zipfile.ZipFile(d/'final-output/handoff.zip') as z:
    m=json.loads(z.read('HANDOFF_MANIFEST.json'));assert len(m['sources'])==9
    for name,pin in m['sources'].items():assert hashlib.sha256(z.read(name)).hexdigest()==pin['sha256']
    assert m['github_head']==json.loads((d/'repair-source.json').read_text())['isolatedHead']
   assert data['observations']['expandedAttack']['state']=='HOLD_EXPANDED_PACKAGE_BUDGET'
  source=d/'repaired-repo'/task['source']
  assert source.is_file()
 result={'state':'PASS_SEPARATE_EVIDENCE_MECHANISM','tasks':3,'criteria':12,'independentHumanAcceptance':'HOLD','peerBenchmark':'HOLD_NO_PEER_EXECUTOR','officialVerifiedFinish':'HOLD'}
 print(json.dumps(result,sort_keys=True));return result
if __name__=='__main__':verify(Path(sys.argv[1]))
