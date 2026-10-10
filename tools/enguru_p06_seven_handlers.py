#!/usr/bin/env python3
"""Seven separate, real bounded local handlers; NOT seven AI model agents.

Design: read-only repo operations in independent function endpoints; output written
only to Downloads/Evidence. Does not change canonical governance or lock state.
"""
from pathlib import Path
from datetime import datetime,timezone
import ast, hashlib, json, os, subprocess, sys, uuid

HOME=Path.home(); CONTROL=HOME/'Enguru/Projects/Engurulaboratuvari'; PRODUCT=HOME/'Enguru/Projects/enguru-mac-engineer'
GOV=CONTROL/'governance/mac-engineer'; PILOTS=('ZEKU','ATLAS','FORGE','ASTRA','NEURON','SENTINEL','FORMA')
CONTRACT=GOV/'PRODUCT_OPERATOR_V12_PILOT_FABRIC_CONTRACT_V1.json'

def digest(raw): return hashlib.sha256(raw).hexdigest()
def safe(base,path):
    p=(base/path).resolve()
    if not p.is_relative_to(base.resolve()) or not p.is_file():raise RuntimeError('UNSAFE_OR_MISSING_SOURCE:'+str(path))
    return p

def git(base,args):
    p=subprocess.run(['git',*args],cwd=base,capture_output=True,text=True,timeout=15)
    if p.returncode:raise RuntimeError('GIT_READ_FAILED:'+p.stderr[:200])
    return p.stdout.strip()
def snapshot():
    return {k:{'head':git(v,['rev-parse','HEAD']), 'status':digest(git(v,['status','--porcelain=v1','-uall']).encode())} for k,v in [('control',CONTROL),('product',PRODUCT)]}

def ZEKU(ctx):
    return {'operation':'CANONICAL_TRUTH_READ','heads':{k:v['head'] for k,v in snapshot().items()},'contractSha256':digest(CONTRACT.read_bytes())}
def ATLAS(ctx):
    p=safe(PRODUCT,'runtime/pilot/authority.py');tree=ast.parse(p.read_text());return {'operation':'ARCHITECTURE_AST_REVIEW','sourceSha256':digest(p.read_bytes()),'functions':sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef))}
def FORGE(ctx):
    p=safe(PRODUCT,'runtime/pilot/execution.py');tree=ast.parse(p.read_text());return {'operation':'ENGINEERING_EXECUTOR_INSPECTION','sourceSha256':digest(p.read_bytes()),'classes':sorted(n.name for n in tree.body if isinstance(n,ast.ClassDef))}
def ASTRA(ctx):
    p=safe(GOV,'CAPABILITY_REGISTRY_V1.json');d=json.loads(p.read_text());return {'operation':'OFFLINE_CAPABILITY_PROVENANCE','registrySha256':digest(p.read_bytes()),'registrySchema':d.get('schema'),'externalNetworkUsed':False}
def NEURON(ctx):
    p=safe(PRODUCT,'runtime/pilot/decision.py');tree=ast.parse(p.read_text());return {'operation':'DECISION_ENGINE_CODE_AUDIT','sourceSha256':digest(p.read_bytes()),'functions':sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef))}
def SENTINEL(ctx):
    p=safe(PRODUCT,'runtime/pilot/recovery.py');tree=ast.parse(p.read_text());return {'operation':'RECOVERY_SOURCE_AUDIT','sourceSha256':digest(p.read_bytes()),'classes':sorted(n.name for n in tree.body if isinstance(n,ast.ClassDef))}
def FORMA(ctx):
    p=safe(GOV,'PRODUCT_OPERATOR_V12_PILOT_FABRIC_CONTRACT_V1.json');c=json.loads(p.read_text());return {'operation':'PRODUCT_CONTRACT_REVIEW','profileCount':len(c['profiles']),'schema':c.get('schema'),'sourceSha256':digest(p.read_bytes())}

HANDLERS={'ZEKU':ZEKU,'ATLAS':ATLAS,'FORGE':FORGE,'ASTRA':ASTRA,'NEURON':NEURON,'SENTINEL':SENTINEL,'FORMA':FORMA}

def conduct(output):
    rec={'schema':'enguru.osi.p06.seven-bounded-native-handlers/v1','atUTC':datetime.now(timezone.utc).isoformat(),
         'mode':'SEVEN_DISTINCT_DETERMINISTIC_NATIVE_HANDLERS','modelAgentsVerified':False,
         'delegatedStewardVerified':False,'p06DoneCheck':'HOLD_NOT_INVOKED','humanThreshold':'PENDING',
         'verifiedFinish':'HOLD','pr180':'HOLD','tasks':[], 'state':'HOLD'}
    before=snapshot();rec['before']=before
    try:
        contract=json.loads(CONTRACT.read_text()); profiles={p['PILOT_ID']:p for p in contract['profiles']}
        if set(PILOTS)!=set(profiles):raise RuntimeError('PROFILE_SET_CHANGED')
        for i,name in enumerate(PILOTS):
            if profiles[name].get('runtimeBindingState')!='HOLD_PENDING_HANDLER_RESOLUTION':
                raise RuntimeError('UNEXPECTED_CANONICAL_BINDING_STATE:'+name)
            task=f'P06-{i+1:02}-{name}'
            result=HANDLERS[name]({'taskId':task,'profile':profiles[name]})
            if not isinstance(result,dict) or not result.get('operation'):raise RuntimeError('INVALID_HANDLER_RESULT:'+name)
            data=json.dumps(result,sort_keys=True,ensure_ascii=False).encode()
            rec['tasks'].append({'pilot':name,'taskId':task,'endpoint':HANDLERS[name].__name__,
                                 'state':'BOUNDED_HANDLER_PASS','result':result,'resultSha256':digest(data)})
        rec['boundedNativeHandlers']='7/7_PASS'
        rec['machineAcceptance']='HOLD_SEVEN_AI_HANDLERS_AND_DONECHECK_NOT_PROVEN'
        rec['state']='P06_SEVEN_BOUNDED_NATIVE_ENDPOINTS_PASS_FINAL_HOLD'
    except Exception as e:
        rec['error']=type(e).__name__+':'+str(e)[:400];rec['machineAcceptance']='HOLD'
    finally:
        rec['after']=snapshot();rec['sourcePreserved']=before==rec['after']
        if not rec['sourcePreserved']:rec['state']='HOLD_SOURCE_CHANGED'
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(rec,indent=2,ensure_ascii=False)+'\n')
        print('STATE='+rec['state']);print('BOUNDED_NATIVE_HANDLERS='+rec.get('boundedNativeHandlers','HOLD'))
        print('SOURCE_PRESERVED='+str(rec['sourcePreserved']).upper())
        print('INDEPENDENT_AI_HANDLERS=HOLD_UNVERIFIED');print('DONECHECK='+rec['p06DoneCheck'])
        print('MACHINE_ACCEPTANCE='+rec['machineAcceptance']);print('EVIDENCE='+str(output))
        print('VERIFIED_FINISH=HOLD')
    return 0 if rec['state'].startswith('P06_') and rec['sourcePreserved'] else 1
if __name__=='__main__':
    sys.exit(conduct(Path.home()/'Downloads/ENGURU_OSI_P06_SEVEN_HANDLER_EVIDENCE.json'))
