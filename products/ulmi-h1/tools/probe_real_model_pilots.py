#!/usr/bin/env python3
"""Read-only Qwen reachability + original A/B/C execution-grant gate.

Never sends a user prompt, changes environment or starts a pilot.
A reachable model is discovery only; quality and real model output remain untested.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, socket, urllib.error, urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]
PILOT=ROOT/'ORIGINALS'/'PILOT_ABC_IMMUTABLE_SOURCE.json'
EXPECTED='5beb10d407dc550d7f979062fef6bdcfd451791103d5b02fc1c2d05a1786d79b'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def probe_model():
    url='http://127.0.0.1:11434/api/tags'
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(url, timeout=1.5) as rsp:
            if rsp.status != 200: return {'state':'HOLD_MODEL_DISCOVERY_HTTP','http_status':rsp.status}
            raw=rsp.read(65537)
            if len(raw)>65536: return {'state':'HOLD_MODEL_DISCOVERY_RESPONSE_SIZE'}
            x=json.loads(raw)
            names=[y.get('name') for y in x.get('models',[]) if type(y) is dict and type(y.get('name')) is str]
            return {'state':'MODEL_AVAILABLE_QUALITY_NOT_TESTED' if 'qwen3:14b' in names else 'HOLD_QWEN3_14B_NOT_FOUND',
                    'model':'qwen3:14b','available_names':names, 'real_generation':'NOT_EXECUTED'}
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ConnectionError, OSError, ValueError) as e:
        return {'state':'HOLD_REAL_QWEN_ENDPOINT_UNAVAILABLE','local_endpoint':url,
                'reason_class':type(e).__name__,'real_generation':'NOT_EXECUTED'}

def main():
    a=argparse.ArgumentParser();a.add_argument('--output',required=True);args=a.parse_args()
    source_sha=sha(PILOT)
    if source_sha!=EXPECTED: raise SystemExit('HOLD_IMMUTABLE_PILOT_SHA_MISMATCH')
    x=json.loads(PILOT.read_text(encoding='utf8'))
    status=[]
    for p in x['pilots']:
        ids=[t['id'] for t in p['tests']]
        assert len(ids)==8 and len(set(ids))==8 and p['pilot_id'] in ('ULMI-A','ULMI-B','ULMI-C')
        grant=p.get('execution_grant')
        status.append({'pilot_id':p['pilot_id'],'required_test_ids':ids,
                       'owner_execution_grant':'ABSENT' if grant is None else 'PRESENT_REQUIRES_VALIDATION',
                       'execution':'NOT_EXECUTED','formal_acceptance':'HOLD_AUTHORITY_AND_REAL_EVIDENCE',
                       'tests_passed':0,'tests_total':8})
    assert len(status)==3 and sum(s['tests_total'] for s in status)==24
    result={'schema':'ulmi.h1.real-model-pilot-readiness/v1',
      'source':'ORIGINAL_IMMUTABLE_PILOT_ABC', 'pilot_contract_sha256':source_sha,
      'owner_approval_design':x.get('owner_approval'),
      'model':probe_model(), 'pilots':status,'pilot_oracle_count':24,
      'authority_outcome':'HOLD_NO_OWNER_EXECUTION_GRANT' if all(p['owner_execution_grant']=='ABSENT' for p in status) else 'VERIFY_INDEPENDENT_EXECUTION_GRANT',
      'new_cost':0,'github_actions':'HOLD_EXTERNAL_ACCOUNT', 'h2':'PARKED'}
    out=pathlib.Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'source_sha_verified':True,'model_state':result['model']['state'],
       'pilots':[(p['pilot_id'],p['owner_execution_grant']) for p in status],
       'execution':result['authority_outcome']},ensure_ascii=False))

if __name__=='__main__': main()
