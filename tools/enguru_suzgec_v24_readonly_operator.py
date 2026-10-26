#!/usr/bin/env python3
"""ENGURU v2.4 T01 user-approved read-only operator; source-locked, no issuer grant."""
from __future__ import annotations
import hashlib,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
POLICY='governance/work-protocol/ENGURU_SUZGEC_V24_T01_READONLY_OPERATOR_AUTHORITY_V1.json'
POLICY_SHA='f2907195f2d02d87b251b29293fb49b35f439bac3bc761b4e0602a2480ee9e1b'
ENGINE_BRIDGE='tools/enguru_suzgec_v24_task_producer_bridge.py'

def sha(b):return hashlib.sha256(b).hexdigest()
def unique(items):
 d={}
 for k,v in items:
  if k in d:raise ValueError('JSON_DUPLICATE:'+k)
  d[k]=v
 return d

def file(root,rel,pin):
 p=Path(rel)
 if p.is_absolute() or '..' in p.parts or not rel or '\\' in rel:raise ValueError('SCOPE:'+rel)
 target=root/rel
 if not target.is_file() or target.is_symlink() or not target.resolve(strict=True).is_relative_to(root.resolve(strict=True)):
  raise ValueError('MISSING_OR_SYMLINK:'+rel)
 raw=target.read_bytes()
 if sha(raw)!=pin:raise ValueError('SOURCE_PIN:'+rel)
 return target

def truth(root):
 if root.is_symlink() or not root.is_dir():raise ValueError('ROOT_SCOPE')
 policy=json.loads(file(root,POLICY,POLICY_SHA).read_text('utf-8'),object_pairs_hook=unique)
 keys=['actionId','decision','authorityScope','project','workItem','canonicalTaskId','gitHead','approvedScopeSha256','approvedPilots','p01','doneCheckIssuerAuthority','verifiedFinish']
 expected=['ENGURU_SUZGEC_V24_T01_READONLY_FIELD','USER_APPROVED_READ_ONLY_ENGINEERING_SCOPE','READ_ONLY_TESTS','suzgec_v24','T01_REAL_TASK_PRODUCER','ENGURU_SUZGEC_V24_PILOT8_T01_T02','269854b8a42a27e9419eae65a3c9e349bdcc7300','c438dfc846a21a3d381a653321c83b976082790692e45b033c4e0f0a2ff22aed',['B01-01','B02-01','B03-01','B04-01','B05-01','B06-01','B07-01','B08-01'],'SUSPENDED','HOLD_UNBOUND','HOLD']
 if [policy.get(k) for k in keys]!=expected:raise ValueError('AUTHORIZATION_SCOPE_DRIFT')
 if policy.get('executor')!='tools/enguru_suzgec_v24_readonly_operator.py' or policy.get('fileMutationAllowance')!=[] or policy.get('githubPush') is not False:raise ValueError('MUTATION_AUTHORITY_DRIFT')
 pins=policy.get('sourcePins');producers=policy.get('producerSourcePins')
 if not isinstance(pins,dict) or len(pins)!=24 or not isinstance(producers,dict) or len(producers)!=2:raise ValueError('SOURCE_PINSET_DRIFT')
 if len(set(pins)|set(producers))!=26 or set(pins)&set(producers):raise ValueError('SOURCE_DUPLICATE')
 verified={rel:sha(file(root,rel,dig).read_bytes()) for rel,dig in sorted({**pins,**producers}.items())}
 head=subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True,timeout=15)
 if head.returncode or head.stdout.strip()!=policy['gitHead']:raise ValueError('OSI_HEAD_DRIFT')
 scope=json.loads(file(root,'governance/work-protocol/ENGURU_SUZGEC_V24_PILOT8_SCOPE_APPROVED_V1.json',policy['approvedScopeSha256']).read_text('utf-8'),object_pairs_hook=unique)
 if scope.get('scopeApproval',{}).get('approvedPilotIds')!=policy['approvedPilots'] or scope.get('scopeApproval',{}).get('state')!='APPROVED_T01_T02_ENGINEERING_SCOPE':raise ValueError('PILOT_SCOPE')
 state=json.loads(file(root,'governance/work-protocol/ENGURU_SUZGEC_V24_FIELD_WORK_STATE_V1.json',pins['governance/work-protocol/ENGURU_SUZGEC_V24_FIELD_WORK_STATE_V1.json']).read_text('utf-8'),object_pairs_hook=unique)
 contract=json.loads(file(root,'governance/work-protocol/ENGURU_SUZGEC_V24_FIELD_WORK_CONTRACT_V1.json',pins['governance/work-protocol/ENGURU_SUZGEC_V24_FIELD_WORK_CONTRACT_V1.json']).read_text('utf-8'),object_pairs_hook=unique)
 if state.get('taskId')!=policy['canonicalTaskId'] or state.get('packages',{}).get('T01',{}).get('items',{}).get('T01_REAL_TASK_PRODUCER',{}).get('state')!='ACTIVE':raise ValueError('CANONICAL_ACTIVE_TASK')
 if state.get('p01')!='SUSPENDED' or state.get('verifiedFinish')!='HOLD' or state.get('benchmarkRealTested')!=0 or contract.get('realProducerAuthorization')!='HOLD_UNBOUND':raise ValueError('ISSUER_BOUNDARY_DRIFT')
 allow=policy.get('readOnlyTestAllowlist')
 if allow!=[{'module':a,'expectedCount':b} for a,b in [('test_enguru_suzgec_v23_forecast.py',13),('test_enguru_suzgec_v23_goal_acceptance.py',25),('test_enguru_language_pre_send_linter.py',28),('test_enguru_suzgec_v24_language_presend.py',18)]]:raise ValueError('TEST_ALLOWLIST_DRIFT')
 return policy, verified

def run(root=ROOT):
 result={'schema':'enguru.suzgec.v24.t01.readonly-operator-field/v1','state':'HOLD','action':'ENGURU_SUZGEC_V24_T01_READONLY_FIELD','precheckExecuted':False,'callbackExecuted':False,'postcheckExecuted':False,'doneCheckIssuerAuthority':'HOLD_UNBOUND','t01FullE01':'HOLD','t02RealField':'HOLD_0_OF_80','p01':'SUSPENDED','humanThreshold':'PENDING','verifiedFinish':'HOLD'}
 try:
  policy, verified=truth(root)
  result['precheckExecuted']=True
  result['precheck']={'state':'PASS_USER_APPROVED_READ_ONLY_SCOPE','sourcePinsVerified':len(verified),'head':policy['gitHead'],'canonicalTaskId':policy['canonicalTaskId'],'testAllowlistCount':len(policy['readOnlyTestAllowlist'])}
  before=verified
  outputs=[]
  for item in policy['readOnlyTestAllowlist']:
   env={k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONSTARTUP','PYTHONINSPECT','PYTHONPYCACHEPREFIX')}
   env['PYTHONDONTWRITEBYTECODE']='1'
   proc=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p',item['module']],cwd=root,env=env,capture_output=True,text=True,timeout=150)
   observed=re.search(r'Ran (\d+) tests?',proc.stderr)
   outputs.append({'module':item['module'],'expectedCount':item['expectedCount'],'observedCount':int(observed.group(1)) if observed else None,'exit':proc.returncode,'outputSha256':sha((proc.stdout+'\n'+proc.stderr).encode())})
   if proc.returncode!=0 or not observed or int(observed.group(1))!=item['expectedCount'] or not re.search(r'^OK\s*$',proc.stderr,re.M):raise ValueError('TEST_GATE:'+item['module'])
  result['callbackExecuted']=True
  result['regressions']={'state':'PASS_ACTUAL_SCOPED_READONLY_TESTS','count':sum(x['observedCount'] for x in outputs),'runs':outputs}
  afterPolicy, after=truth(root)
  if before!=after or afterPolicy!=policy:raise ValueError('SOURCE_STATE_DRIFT_AFTER_TESTS')
  result['postcheckExecuted']=True
  result['postcheck']={'state':'PASS_SOURCE_AND_TASK_UNCHANGED','sourcePinsVerified':len(after),'unauthorizedSourceMutations':0}
  env={k:v for k,v in os.environ.items() if k!='PYTHONPATH'}|{'PYTHONDONTWRITEBYTECODE':'1'}
  bridge=subprocess.run([sys.executable,'-B',ENGINE_BRIDGE],cwd=root,env=env,text=True,capture_output=True,timeout=180)
  if bridge.returncode:raise ValueError('DONECHECK_BRIDGE_PROBE:'+bridge.stderr[-160:])
  observation=json.loads(bridge.stdout,object_pairs_hook=unique)
  if (observation.get('state')!='PASS_PROJECT_REGISTERED_REAL_ISSUER_HOLD' or observation.get('progress',{}).get('countedPass')!=0 or observation.get('doneCheck',{}).get('actualOutcome')!='inconclusive' or observation.get('doneCheck',{}).get('producerAuthority')!='HOLD_UNBOUND'):raise ValueError('INDEPENDENT_BOUNDARY_DRIFT')
  result['doneCheck']={'engineProbe':observation['doneCheck']['state'],'outcome':'inconclusive','issuerAuthority':'HOLD_UNBOUND'}
  result['progress']={'project':'suzgec_v24','countedPass':0,'total':11,'integrity':observation['progress']['progressIntegrity']}
  result['state']='PASS_USER_AUTHORIZED_READONLY_OPERATOR_EXECUTED_ISSUER_HOLD'
 except Exception as exc:
  result['holdReason']=type(exc).__name__+':'+str(exc)[:260]
 return result

if __name__=='__main__':
 if sys.argv[1:]!=['--field']:
  print('STATE=HOLD_REQUIRED_FIELD_FLAG');raise SystemExit(2)
 out=run();print(json.dumps(out,sort_keys=True,ensure_ascii=False,indent=2));raise SystemExit(0 if out['state'].startswith('PASS_USER_') else 2)
