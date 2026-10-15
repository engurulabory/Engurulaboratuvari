#!/usr/bin/env python3
"""Source-bound Progress Core + DoneCheck v1.2 read-only v2.4 field qualification.
Project PASS and Verified Finish retain their independent authorities.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
HEAD='269854b8a42a27e9419eae65a3c9e349bdcc7300'
SCOPE_SHA='c438dfc846a21a3d381a653321c83b976082790692e45b033c4e0f0a2ff22aed'
PROGRESS_SHA='f3e2610c6e325f6fd620baa84ec412437a015109dde88ac38cab7f08b2a365b4'
DONECHECK_BRIDGE_SHA='098d2a384d0371d96eed237703d98608312af988b50ecb3545fd97263b959e29'
PREFIX='governance/work-protocol/'
IDS=['B01-01','B02-01','B03-01','B04-01','B05-01','B06-01','B07-01','B08-01']


def sha(data):return hashlib.sha256(data).hexdigest()
def safe(root, rel, expected=None):
    r=root.resolve(strict=True);p=r/rel
    if Path(rel).is_absolute() or '..' in Path(rel).parts or not p.is_file() or p.is_symlink() or not p.resolve(strict=True).is_relative_to(r):
        raise ValueError('SOURCE_SCOPE:'+rel)
    if expected and sha(p.read_bytes())!=expected:raise ValueError('SOURCE_SHA_DRIFT:'+rel)
    return p

def read(p):
    def unique(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('DUPLICATE_JSON_KEY:'+k)
            d[k]=v
        return d
    d=json.loads(p.read_text('utf-8'),object_pairs_hook=unique)
    if not isinstance(d,dict):raise ValueError('JSON_OBJECT_REQUIRED')
    return d

def baseline(root):
    actual=subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True,timeout=15)
    if actual.returncode or actual.stdout.strip()!=HEAD:raise ValueError('OSI_HEAD_DRIFT')
    a=read(safe(root,PREFIX+'ENGURU_SUZGEC_V24_PILOT8_SCOPE_APPROVED_V1.json',SCOPE_SHA))
    if a.get('scopeApproval',{}).get('approvedPilotIds')!=IDS or a.get('p01')!='SUSPENDED' or a.get('verifiedFinish')!='HOLD':raise ValueError('SCOPE_AUTHORITY_DRIFT')
    pins=a.get('pinned19SourceSha256')
    if not isinstance(pins,dict) or len(pins)!=19:raise ValueError('EXPECTED_19_PINS')
    for rel,pin in pins.items():safe(root,rel,pin)
    safe(root,'tools/enguru_progress.py',PROGRESS_SHA)
    safe(root,'tools/mac_engineer_donecheck_v12_bridge.py',DONECHECK_BRIDGE_SHA)
    c=read(safe(root,PREFIX+'ENGURU_SUZGEC_V24_FIELD_WORK_CONTRACT_V1.json'))
    s=read(safe(root,PREFIX+'ENGURU_SUZGEC_V24_FIELD_WORK_STATE_V1.json'))
    w=read(safe(root,PREFIX+'ENGURU_SUZGEC_V24_FIELD_WORKLIST_V1.json'))
    if c.get('realProducerAuthorization')!='HOLD_UNBOUND' or c.get('progressBinding',{}).get('name')!='suzgec_v24':raise ValueError('CONTRACT_AUTHORITY_DRIFT')
    if s.get('activeTaskAuthorization')!='HOLD_REAL_AUTHORITY_AND_PRODUCER_REQUIRED' or s.get('verifiedFinish')!='HOLD' or s.get('p01')!='SUSPENDED' or s.get('benchmarkRealTested')!=0:raise ValueError('FIELD_STATE_DRIFT')
    if sorted(s.get('packages',{}).get('T02',{}).get('items',{}))!=sorted(IDS):raise ValueError('PILOT_IDS_DRIFT')
    if [p['id'] for p in w['packages']]!=['T01','T02','T03','T04']:raise ValueError('GATE_ORDER_DRIFT')
    return {'state':'PASS_SOURCE_BOUND','sourceHead':HEAD,'verifiedSourceCount':19,'approvedScopeSHA256':SCOPE_SHA}

def progress_observation(root):
    if str(root) not in sys.path:sys.path.insert(0,str(root))
    from tools import enguru_progress as progress
    summary=progress.summarize('suzgec_v24')
    verify=progress.structural_verify('suzgec_v24')
    if summary['total']!=11 or summary['declaredPass']!=0 or summary['activePackage']!='T01' or summary['activeItem']!='T01_REAL_TASK_PRODUCER' or verify['countedPass']!=0 or verify['unverifiedPass']!=0 or verify['stateDrift']!='NONE' or summary['verifiedFinish']!='HOLD':
        raise ValueError('PROGRESS_RESULT_BOUNDARY')
    return {'state':'PASS_REAL_PROJECT_DISCOVERY','project':'suzgec_v24','countedPass':0,'total':11,'activeItem':summary['activeItem'],'progressIntegrity':verify['progressIntegrity'],'finishState':verify['finishState'],'worklistSHA256':summary['worklistDigest'],'stateSHA256':summary['stateDigest']}

def donecheck_probe(root):
    """Tests actual verifyTask with empty evidence; only inconclusive can be accepted."""
    if str(root) not in sys.path:sys.path.insert(0,str(root))
    try:
        from tools import mac_engineer_donecheck_v12_bridge as bridge
        runtime=bridge.DONECHECK_RUNTIME
        if runtime.is_symlink() or not runtime.is_dir():raise ValueError('RUNTIME_UNAVAILABLE')
        git=subprocess.run(['git','rev-parse','HEAD'],cwd=runtime,capture_output=True,text=True,timeout=15)
        if git.returncode or git.stdout.strip()!=bridge.DONECHECK_SHA:raise ValueError('RUNTIME_PIN')
        core=runtime/'dist/donecheck-core.js'
        if not core.is_file() or core.is_symlink():raise ValueError('CORE_BUILD_MISSING')
        now=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'); taskid='enguru-suzgec-v24-pilot8'
        payload={'task':{'id':taskid,'title':'Approved ENGURU v2.4 eight pilot field outcome','requestText':'Require real OSi authorized evidence for each approved pilot','status':'awaiting_review','createdAt':now},'criteria':[{'id':id,'taskId':taskid,'statement':'Approved field outcome '+id,'verificationInstruction':'Verify criterion-scoped actual OSi field evidence','kind':'objective','required':True} for id in IDS], 'aiOutput':'Awaiting real field producer','evidence':[],'resultId':'enguru-v24-empty-'+sha(now.encode())[:12], 'verifiedAt':now,'policy':{'requireEvidenceProvenance':True,'trustedProducerIds':['enguru.suzgec.v24.field']}}
        output=bridge.reproduce_verification_result(payload)
        if output.get('outcome')!='inconclusive':raise ValueError('EMPTY_EVIDENCE_RESULT_UNSAFE:'+str(output.get('outcome')))
        return {'state':'PASS_REAL_DONECHECK_ENGINE_PROBE','actualOutcome':'inconclusive','producerAuthority':'HOLD_UNBOUND','runtimeHead':bridge.DONECHECK_SHA}
    except Exception as exc:
        return {'state':'HOLD_DONECHECK_ENGINE_PROBE','holdReason':type(exc).__name__+':'+str(exc)[:180],'producerAuthority':'HOLD_UNBOUND'}

def observe(root=ROOT):
    out={'schema':'enguru.suzgec.v24.t01-t02.progress-donecheck-boundary/v1','state':'HOLD','p01':'SUSPENDED','verifiedFinish':'HOLD','t01FullE01':'HOLD','realPilotsTested':0,'realPilotsPassed':0,'humanThreshold':'PENDING'}
    try:
        out['source']=baseline(root);out['progress']=progress_observation(root);out['doneCheck']=donecheck_probe(root)
        out['state']='PASS_PROJECT_REGISTERED_REAL_ISSUER_HOLD'
    except Exception as e:out['holdReason']=type(e).__name__+':'+str(e)[:220]
    return out

if __name__=='__main__':
    d=observe(); print(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2));raise SystemExit(0 if d['state'].startswith('PASS_PROJECT_') else 2)
