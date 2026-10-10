#!/usr/bin/env python3
"""Additive P06 pilot dispatch adapter: canonical fail-closed action resolution.

Qualification != independent AI handler execution. Default inspect mode does not
execute actions. Only explicitly opted-in SENTINEL TEST_REGRESSION is executable.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess, sys
if __package__:
    from .enguru_evidence_receipt_io import write_new_json
else:
    from enguru_evidence_receipt_io import write_new_json

PILOTS = ('ZEKU','ATLAS','FORGE','ASTRA','NEURON','SENTINEL','FORMA')
CONTROL = Path(__file__).resolve().parents[1]
GOV = CONTROL/'governance/mac-engineer'
CONTRACT = GOV/'PRODUCT_OPERATOR_V12_PILOT_FABRIC_CONTRACT_V1.json'
EXPECTED_HEAD = 'a056fd29f5a12f302216628e638a614640ff0d4e'
EXPECTED_GREEN = 'PACKAGE08_CAP08_TEST_REGRESSION_FIELD_PROOF'
EXPECTED_SHA = '213c23cead48f6185343f37292a1a5a240442dcd57add970e122e7237d098419'

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(args, cwd, timeout=200):
    try:
        p=subprocess.run(args,cwd=cwd,timeout=timeout,capture_output=True,text=True,
            env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        return {'rc':p.returncode,'stdoutTail':p.stdout[-8000:],'stderrTail':p.stderr[-4000:]}
    except (OSError,subprocess.TimeoutExpired) as e:
        return {'rc':124 if isinstance(e,subprocess.TimeoutExpired) else 127,'error':str(e)[:300]}
def get(path): return json.loads(path.read_text(encoding='utf-8'))
def safe_path(relative):
    p=(CONTROL/relative).resolve()
    if not p.is_relative_to(CONTROL.resolve()) or not p.is_file():
        raise ValueError('MISSING_OR_UNSAFE_PATH:'+relative)
    return p

def qualify():
    c=get(CONTRACT)
    if not (CONTROL/c['actionBinding']).is_file():
        raise ValueError('P06_LEGACY_ACTION_BINDING_SOURCE_UNAVAILABLE')
    reg={key:get(safe_path(c[key])) for key in ('capabilityRegistry','actionRegistry','actionBinding')}
    actions=reg['actionRegistry']['actions']
    links={v['CAPABILITY_ID']:v for v in get(GOV/'CAPABILITY_EXECUTION_BINDING_V1.json')['bindings']}
    profiles=c['profiles']
    results={}
    for pilot in PILOTS:
        matching=[p for p in profiles if p.get('PILOT_ID')==pilot]
        if len(matching)!=1: raise ValueError('INVALID_PILOT_PROFILE:'+pilot)
        profile=matching[0]
        records=[]
        for cap in profile['CAPABILITY_IDS']:
            bound=links.get(cap)
            action_id=bound.get('ACTION') if isinstance(bound,dict) else None
            action=actions.get(action_id) if action_id else None
            entry={'capability':cap,'action':action_id,'state':'HOLD_UNBOUND'}
            if isinstance(action,dict) and action.get('command'):
                try:
                    path=safe_path(action['command'])
                except ValueError:
                    entry.update(state='HOLD_REGISTERED_ACTION_SOURCE_MISSING',
                                 command=action['command'])
                else:
                    entry.update(state='REGISTERED_ACTION_PRESENT',command=action['command'],
                                 authority=action.get('authority'),sha256=digest(path))
            records.append(entry)
        results[pilot]={'canonicalBindingState':profile.get('runtimeBindingState'),
                        'capabilities':records,'independentHandlerExecuted':False}
    return results

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pilot',choices=PILOTS,default='SENTINEL')
    ap.add_argument('--capability',default='TEST_REGRESSION')
    ap.add_argument('--execute-green-cap08',action='store_true')
    ap.add_argument('--receipt-dir',default=str(Path.home()/'Enguru/Evidence/MacEngineer/P06/handler-engineering'))
    a=ap.parse_args()
    receipt={'schema':'enguru.osi.p06.pilot-dispatch-adapter/v1',
        'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'state':'HOLD','realSevenHandlerAcceptance':'HOLD','humanThreshold':'PENDING',
        'verifiedFinish':'HOLD','pr180':'HOLD','actualIndependentPilotHandler':False}
    pre=cmd(['git','rev-parse','HEAD'],CONTROL)
    before=cmd(['git','status','--porcelain=v1','-uall'],CONTROL)
    try:
        if pre['rc']!=0: raise ValueError('CONTROL_HEAD_UNAVAILABLE')
        receipt['currentHead']=pre['stdoutTail'].strip()
        receipt['bindings']=qualify()
        receipt['qualify']='PASS_CANONICAL_PROFILES_RESOLVED'
        selected=[x for x in receipt['bindings'][a.pilot]['capabilities'] if x['capability']==a.capability]
        if len(selected)!=1: raise ValueError('PILOT_CAPABILITY_NOT_DECLARED')
        target=selected[0]
        receipt['selected']={'pilot':a.pilot,**target}
        if target['state']!='REGISTERED_ACTION_PRESENT': raise ValueError('NO_REGISTERED_ACTION')
        if not a.execute_green_cap08:
            receipt['state']='P06_HANDLER_ADAPTER_QUALIFIED_EXECUTION_PENDING'
        else:
            if receipt['currentHead']!=EXPECTED_HEAD:raise ValueError('HEAD_CHANGED_FROM_ACCEPTED_BASELINE')
            if a.pilot!='SENTINEL' or a.capability!='TEST_REGRESSION' or target['action']!=EXPECTED_GREEN:
                raise ValueError('ACTION_NOT_IN_P06_GREEN_EXECUTION_ALLOWLIST')
            if target['sha256']!=EXPECTED_SHA:raise ValueError('REGISTERED_COMMAND_DIGEST_MISMATCH')
            record=get(GOV/'OPERATOR_ACTION_REGISTRY_V1.json')['actions'][EXPECTED_GREEN]
            if record.get('networkRequired') is not False or record.get('remotePush') is not False or record.get('failClosed') is not True:
                raise ValueError('GREEN_AUTHORITY_GUARD_FAILED')
            executed=cmd(['/bin/zsh',str(safe_path(target['command']))],CONTROL,300)
            receipt['executedAction']=executed
            receipt['state']='P06_REGISTERED_NATIVE_ACTION_PASS_SEVEN_HANDLERS_HOLD' if executed['rc']==0 and 'STATE=PASS' in executed.get('stdoutTail','') else 'HOLD_NATIVE_ACTION'
    except Exception as ex:
        receipt['error']=type(ex).__name__+':'+str(ex)
    finally:
        after=cmd(['git','status','--porcelain=v1','-uall'],CONTROL)
        post=cmd(['git','rev-parse','HEAD'],CONTROL)
        receipt['sourcePreserved']=(before==after and pre==post)
        receipt['beforeStatusSha256']=hashlib.sha256(before.get('stdoutTail','').encode()).hexdigest()
        if not receipt['sourcePreserved']:receipt['state']='HOLD_SOURCE_CHANGED'
        target=Path(a.receipt_dir)/('P06_HANDLER_ENGINEERING_RECEIPT_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
        try:
            write_new_json(target,receipt)
        except (OSError,ValueError) as ex:
            print('STATE=HOLD\nREASON=EVIDENCE_OUTPUT_AUTHORITY:'+type(ex).__name__)
            return 2
        print('STATE='+receipt['state'])
        print('SOURCE_PRESERVED='+str(receipt['sourcePreserved']).upper())
        print('REAL_SEVEN_HANDLERS=HOLD')
        print('EVIDENCE='+str(target))
        print('VERIFIED_FINISH=HOLD')
    return 0 if receipt['state'].startswith('P06_') and receipt['sourcePreserved'] else 1
if __name__=='__main__':
    if len(sys.argv)==4 and sys.argv[1]=='--p06-task':
        from enguru_p06_runtime_task_adapter import main as p06_task_main
        sys.exit(p06_task_main(sys.argv[2:]))
    sys.exit(main())
