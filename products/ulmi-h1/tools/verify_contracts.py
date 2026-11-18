#!/usr/bin/env python3
"""Read-only ULMi H1 immutable V22 and Pilot A/B/C source contract preflight."""
import hashlib, json, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
checks=[]
def ck(k,condition):
    checks.append((k,bool(condition)))
    print(('PASS' if condition else 'FAIL')+' '+k,flush=True)
def load(name,pin):
    p=root/name; b=p.read_bytes(); ck('SOURCE_SHA_'+name.split('/')[-1],hashlib.sha256(b).hexdigest()==pin); return json.loads(b)
v=load('ORIGINALS/V22_IMMUTABLE_SOURCE.json','069c03b0f299e76ef46e26a25eb4284474ae5219353185a88386ee5df9f39304')
a=load('ORIGINALS/PILOT_ABC_IMMUTABLE_SOURCE.json','5beb10d407dc550d7f979062fef6bdcfd451791103d5b02fc1c2d05a1786d79b')
ids=[t['id'] for t in v['tasks']]
ck('ORIGINAL_12_UNIQUE',len(ids)==12 and len(set(ids))==12 and set(ids)=={f'{i:02d}' for i in range(1,13)})
ck('POSITIVE_NEGATIVE_ORACLES',all(t.get('positive_oracle') and t.get('negative_oracle') and t.get('required_completion_evidence') for t in v['tasks']))
ck('PILOT_A_B_C',len(a['pilots'])==3 and {p['pilot_id'] for p in a['pilots']}=={'ULMI-A','ULMI-B','ULMI-C'})
ck('PILOTS_8_EACH_NOT_EXECUTED',all(len(p['tests'])==8 and all(x['status']=='NOT_TESTED' for x in p['tests']) for p in a['pilots']))
ck('HUMAN_THRESHOLD',all(p.get('execution_grant') is None for p in a['pilots'] if p['pilot_id'] in ('ULMI-B','ULMI-C')))
ck('NO_FORMAL_PROMOTION',v.get('verified_full_closeouts') in (0,'0',None))
print('SOURCE_CONTRACTS',sum(v for _,v in checks),'/',len(checks))
sys.exit(0 if all(v for _,v in checks) else 1)
