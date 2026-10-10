#!/usr/bin/env python3
"""P06 bounded native pilot dispatch; extends existing adapter, no new authority.

The contract is restricted to native registered proof consumption + real native
read-only handler invocation. It is NOT an autonomous specialist or general-purpose
source-changing task handler. Never infer authority from supplied task fields.
"""
from __future__ import annotations
import hashlib, importlib.util, json, os, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GOV=ROOT/'governance/mac-engineer'
PROOF_ROOT=Path.home()/'Enguru/Evidence/MacEngineer'
PILOTS=('ZEKU','ATLAS','FORGE','ASTRA','NEURON','SENTINEL','FORMA')
if __package__:
    from .enguru_p06_task_specific_policy import objective as task_specific_objective, qualify_native_result
else:
    from enguru_p06_task_specific_policy import objective as task_specific_objective, qualify_native_result

def digest(p):
    if not p.is_file() or p.is_symlink(): raise ValueError('EVIDENCE_MISSING_OR_SYMLINK')
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    if not p.is_file() or p.is_symlink(): raise ValueError('SOURCE_NOT_FILE')
    o=json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(o,dict): raise ValueError('NOT_OBJECT')
    return o
def githead():
    r=subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],capture_output=True,text=True,timeout=15)
    if r.returncode: raise ValueError('SOURCE_HEAD_UNAVAILABLE')
    return r.stdout.strip()
def check(task):
    c=load(GOV/'PRODUCT_OPERATOR_V12_PILOT_FABRIC_CONTRACT_V1.json')
    b=load(GOV/'CAPABILITY_EXECUTION_BINDING_V1.json')
    a=load(GOV/'OPERATOR_ACTION_REGISTRY_V1.json')
    manifest=load(GOV/'P06_PREHUMAN_MACHINE_CRITERIA_V1.json')
    profiles={p['PILOT_ID']:p for p in c['profiles']}
    name=task.get('PILOT_ID')
    if name not in profiles: raise ValueError('UNKNOWN_PILOT')
    p=profiles[name]; caps=p['CAPABILITY_IDS']
    if not isinstance(task.get('WORK_ID'),str) or not task['WORK_ID'].startswith('P06-'+name+'-'):
        raise ValueError('WORK_ID_SCOPE')
    approved={'PROVE_BOUND_NATIVE_TASK_FOR_'+name, task_specific_objective(name)}
    if task.get('OBJECTIVE') not in approved: raise ValueError('OBJECTIVE_SCOPE')
    if task.get('EXACT_SCOPE')!=caps: raise ValueError('CAPABILITY_SCOPE_ESCALATION')
    if task.get('FRESH_SOURCE_IDENTITY')!=githead():raise ValueError('STALE_SOURCE_IDENTITY')
    if task.get('DEPENDENCIES')!=['PINNED_P06_NATIVE_EVIDENCE','LOCAL_PROMOTION_COMMIT']:
        raise ValueError('DEPENDENCY_SCOPE')
    if task.get('NETWORK_MUTATION') is not False or task.get('REMOTE_WRITE') is not False or task.get('HUMAN_APPROVAL') is not False:
        raise ValueError('SIDE_EFFECT_AUTHORITY')
    m={x['CAPABILITY_ID']:x for x in b['bindings']}
    authorities={}
    for cap in caps:
        binding=m.get(cap)
        if binding is None: raise ValueError('NO_CAPABILITY_BINDING')
        if binding.get('BINDING_TYPE')=='DIRECT_RUNTIME':
            if cap!='CURRENT_TECHNICAL_TRUTH_READ' or binding.get('READ_ONLY_CONFIRMED') is not True:
                raise ValueError('DIRECT_RUNTIME_NOT_QUALIFIED')
            authorities[cap]='READ_ONLY_NATIVE_CURRENT_TRUTH'
        elif binding.get('BINDING_TYPE')=='REGISTERED_ACTION':
            action=a['actions'].get(binding.get('ACTION'))
            if not isinstance(action,dict) or action.get('authority')!=binding.get('AUTHORITY') or action.get('remotePush') is not False or action.get('failClosed') is not True:
                raise ValueError('REGISTERED_ACTION_NOT_QUALIFIED')
            authorities[cap]=binding['AUTHORITY']
        else: raise ValueError('CAPABILITY_NOT_EXECUTABLE')
    if task.get('AUTHORITY')!=authorities:raise ValueError('AUTHORITY_ESCALATION')
    proofs=task.get('PROOFS')
    if not isinstance(proofs,list) or [q.get('capability') for q in proofs]!=caps:
        raise ValueError('PROOF_SCOPE')
    checked=[]
    for q in proofs:
        cap=q['capability'];actual=manifest['pinnedEvidence'].get(cap)
        if q.get('sha256')!=actual:raise ValueError('PROOF_UNPINNED')
        target=Path(q.get('path') or '')
        if not target.is_file() or target.is_symlink() or not target.resolve().is_relative_to(PROOF_ROOT.resolve()):
            raise ValueError('EVIDENCE_PATH_OUT_OF_SCOPE')
        if digest(target)!=actual:raise ValueError('EVIDENCE_BYTES_CHANGED')
        checked.append({'capability':cap,'sha256':actual,'path':str(target)})
    return p,checked,manifest

def execute(task):
    profile,proofs,manifest=check(task)
    native=ROOT/'tools/enguru_p06_seven_handlers.py'
    if digest(native)!=manifest['pinnedNativeHandlerSha256']:
        raise ValueError('NATIVE_HANDLER_SOURCE_DRIFT')
    spec=importlib.util.spec_from_file_location('enguru_p06_real_seven',str(native))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    # Use the candidate contract identity, not the mutable live control-plane repo.
    module.CONTROL=ROOT;module.GOV=GOV
    module.CONTRACT=GOV/'PRODUCT_OPERATOR_V12_PILOT_FABRIC_CONTRACT_V1.json'
    result=module.HANDLERS[task['PILOT_ID']]({'taskId':task['WORK_ID'],'profile':profile})
    if not isinstance(result,dict) or not result.get('operation'):
        raise ValueError('BOUNDED_NATIVE_HANDLER_RESULT')
    task_qualified = (task['OBJECTIVE']==task_specific_objective(task['PILOT_ID']))
    if task_qualified:
        qualify_native_result(task['PILOT_ID'],result,profile)
    result_digest=hashlib.sha256(json.dumps(result,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return {'STATE':'PASS','CLAIM':'BOUNDED_NATIVE_TASK_AND_REGISTERED_EVIDENCE_VERIFIED',
            'EVIDENCE':proofs,'OPEN_DIFFERENCE':['AUTONOMOUS_PILOT_AUTHORITY_NOT_PROVEN','OFFICIAL_P06_ACCEPTANCE_PENDING'],
            'NEXT_ACTION':'P06_INDEPENDENT_MACHINE_CRITERIA',
            'WORK_ID':task['WORK_ID'],'PILOT_ID':task['PILOT_ID'],'SOURCE_HEAD':githead(),
            'nativeHandlerExecuted':True,'nativeHandlerResult':result,'nativeResultSha256':result_digest,
            'taskSpecificHandlerQualified':task_qualified,'taskSpecificObjective':task['OBJECTIVE'],
            'canonicalPilotAccepted':False,'generalTaskExecutionAuthorized':False}

def main(argv):
    if len(argv)!=2:raise SystemExit('Usage: --p06-task <task.json> <receipt.json>')
    task_file,output=map(Path,argv)
    receipt={'STATE':'HOLD','CLAIM':'UNVERIFIED','EVIDENCE':[],'OPEN_DIFFERENCE':[],
             'NEXT_ACTION':'CORRECT_TASK_INPUT','canonicalPilotAccepted':False}
    try:
        receipt=execute(load(task_file));rc=0
    except Exception as ex:
        receipt['CLAIM']=type(ex).__name__+':'+str(ex);rc=2
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(receipt,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
    print('STATE='+receipt['STATE']);print('PILOT='+str(receipt.get('PILOT_ID','HOLD')))
    return rc
if __name__=='__main__':raise SystemExit(main(sys.argv[1:]))
