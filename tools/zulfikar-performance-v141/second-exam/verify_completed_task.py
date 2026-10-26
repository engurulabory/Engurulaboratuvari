"""Different executable checks real output bytes, frozen criteria, patch scope and source identity."""
import hashlib,importlib.util,json,subprocess,sys,zipfile
from pathlib import Path

def strict_json(p):
 def reject(v):raise ValueError('non-finite JSON '+v)
 return json.loads(p.read_text(),parse_constant=reject)
def verify(task,repo,out):
 r=strict_json(out/'checks.json');assert r['taskId']==task and r['total']==r['met']==4
 assert len(r['criteria'])==4 and all(type(v) is bool and v for v in r['criteria'].values())
 if task=='S01':
  expected={'goalId':'ZF.SECOND.S01','result':'makbuz doğru ve kalıcı','value':12}
  assert strict_json(out/'receipts/task/result.json')==expected
  assert strict_json(out/'receipts/fault/interrupted.json')==expected
  assert not list((out/'receipts/invalid').glob('*.json'))
  assert r['observations']['fsyncObserved'].count('directory')>=2
 elif task=='S02':
  inv=strict_json(out/'inventory.json');assert inv['task_count']==3 and inv['independently_accepted']==0
  assert [x['task_id'] for x in inv['tasks']]==['A','B','C']
  assert [x['dependencies'] for x in inv['tasks']]==[[],['A'],['B']]
  assert all(x['state']=='HOLD_GUVENLI_DUR' for x in r['observations']['cycles']+r['observations']['malformed'])
  assert r['observations']['cli']['stdout']==r['observations']['replay']['stdout']
 elif task=='S03':
  with zipfile.ZipFile(out/'handoff.zip') as z:
   manifest=json.loads(z.read('HANDOFF_MANIFEST.json'));assert len(manifest['sources'])==9
   for name,entry in manifest['sources'].items():
    raw=z.read(name);assert hashlib.sha256(raw).hexdigest()==entry['sha256'] and len(raw)==entry['size']
   assert manifest['github_head']==subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
   assert manifest['package_execution_allowed'] is False and manifest['osi_execution_count']==0
  with zipfile.ZipFile(out/'oversized-expanded.zip') as z:assert sum(x.file_size for x in z.infolist())>2_000_000
  assert r['observations']['expandedAttack']['state'].startswith('HOLD')
  assert all(x['state'].startswith('HOLD') for x in r['observations']['malformed'])
 assert r['observations']['regression']['exitCode']==0
 return {'state':'PASS_ACTUAL_EXISTING_SOURCE_TASK_OUTPUT','taskId':task,'criteria':list(r['criteria']),'artifactSha256':hashlib.sha256((out/'checks.json').read_bytes()).hexdigest(),'independentHumanReview':'HOLD'}
if __name__=='__main__':print(json.dumps(verify(sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3])),sort_keys=True))
