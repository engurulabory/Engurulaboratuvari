#!/usr/bin/env python3
"""Strict machine-checkable ID-by-ID V22 source/accepted-evidence reconciliation.
Never promotes scoped evidence to original formal or technical full closure.
"""
import hashlib,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
B=R
V=B/'ORIGINALS/V22_IMMUTABLE_SOURCE.json';P=B/'ORIGINALS/PILOT_ABC_IMMUTABLE_SOURCE.json'
SAFARI=R/'EVIDENCE/OWNER_V5_SAFARI_UAT_RAW.json'
RPT=R/'EVIDENCE/V22_12_ID_RECOUNT_EXECUTED.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
v=json.loads(V.read_text());p=json.loads(P.read_text());s=json.loads(SAFARI.read_text())
expect={'V22':'069c03b0f299e76ef46e26a25eb4284474ae5219353185a88386ee5df9f39304','ABC':'5beb10d407dc550d7f979062fef6bdcfd451791103d5b02fc1c2d05a1786d79b'}
checks=[]
def ck(id,good,observed):checks.append({'control':id,'passed':bool(good),'observed':str(observed)[:250]})
ck('SOURCE_SHA_V22',sha(V.read_bytes())==expect['V22'],sha(V.read_bytes()))
ck('SOURCE_SHA_ABC',sha(P.read_bytes())==expect['ABC'],sha(P.read_bytes()))
ids=[x['id'] for x in v['tasks']]
ck('EXACT_12_UNIQUE_IDS',len(ids)==12 and len(set(ids))==12 and set(ids)=={f'{x:02d}' for x in range(1,13)},ids)
ck('ALL_POSITIVE_NEGATIVE_AND_GATE',all(isinstance(x.get('positive_oracle'),str) and len(x['positive_oracle'])>10 and isinstance(x.get('negative_oracle'),str) and len(x['negative_oracle'])>10 and x.get('primary_gate') for x in v['tasks']),len(v['tasks']))
ck('ALL_ORIGINAL_COMPLETION_EVIDENCE',all(x.get('required_completion_evidence') and x.get('authority') for x in v['tasks']),len(v['tasks']))
blocks=[y for x in v['work_blocks'] for y in x['task_ids']]
ck('BLOCKS_COVER_EACH_ID_ONCE',sorted(blocks)==sorted(ids),blocks)
ck('PILOT_A_B_C_THREE',len(p['pilots'])==3 and {x['pilot_id'] for x in p['pilots']}=={'ULMI-A','ULMI-B','ULMI-C'},[x['pilot_id'] for x in p['pilots']])
ck('ORIGINAL_PILOTS_8_OF_8_DESIGN_ONLY',all(len(x['tests'])==8 and len({t['id'] for t in x['tests']})==8 and all(t['status']=='NOT_TESTED' for t in x['tests']) for x in p['pilots']),[len(x['tests']) for x in p['pilots']])
ck('PILOT_B_C_GRANTS_NULL',all(x['execution_grant'] is None for x in p['pilots'] if x['pilot_id'] in ('ULMI-B','ULMI-C')),['ULMI-B','ULMI-C'])
ck('OWNER_SAFARI_60_OF_60',len(s['checks'])==60 and all(t['status']=='PASS' for t in s['checks']) and s['phase']=='BROWSER_OBSERVATION_PASS_SCOPED',len(s['checks']))
ck('OWNER_SAFARI_ONE_SESSION_THREE_TASKS',len(s['tasks'])==3 and len({x['task_id'] for x in s['tasks']})==3 and 'reloaded_at' in s,s['started_at'])
ck('OWNER_SAFARI_NOT_PRODUCER_DONECHECK',s['owner_final']=='NOT_ISSUED' and s['independent_donecheck']=='NOT_EXECUTED',s['owner_final'])
# Negative / adversarial contract mutations are tests of the rule, not modifications to V22.
for case,transform in [('DUPLICATE_ID',lambda t:t.__setitem__(1,{**t[1],'id':t[0]['id']})),('EMPTY_NEGATIVE',lambda t:t[0].update(negative_oracle='')),('MISSING_ID',lambda t:t.pop()),('FAKE_GRANT',None)]:
 if case!='FAKE_GRANT':
  tasks=json.loads(json.dumps(v['tasks']));transform(tasks)
  ok=len(tasks)==12 and {x['id'] for x in tasks}==set(ids) and len(set(x['id'] for x in tasks))==12 and all(x.get('negative_oracle') for x in tasks)
 else:
  pilots=json.loads(json.dumps(p['pilots']));pilots[1]['execution_grant']='FORGED';ok=all(x['execution_grant'] is None for x in pilots if x['pilot_id'] in ('ULMI-B','ULMI-C'))
 ck('NEGATIVE_'+case+'_REFUSED',not ok,'Mutated evidence prevented a false success')
reason={
'01':'Canonical seven/eight role source identities and authoritative producer grant not fully attested.',
'02':'12/12 structural executable mapping passed here; owner-evidenced original acceptance still open.',
'03':'A/B/C distinct 8/8, scoped grants and independent oracle not accepted.',
'04':'Live V2.1 context with 8 SHA-pinned roles and 32 KB adversarial oracle not proven.',
'05':'Safari file/task flow passed; real Emin-Maya V1.9 model response not proven.',
'06':'Real independent Qwen/Shared AI provider A/B route provenance not proven.',
'07':'Request-framing negative RED->GREEN and 10,001 executor replay AND 10,001 forged real HTTP requests proven; authenticated producer and all original reset-set oracles not independently accepted.',
'08':'Actual rollback/restart/SHA proven; full original authorized recovery and independent acceptance open.',
'09':'Real Turkish Qwen reply and independent critique not proven.',
'10':'One independent Safari browser user session (3 tasks), not 3 independent runs.',
'11':'V5 ZIP byte-reproven, Safari session is V3 internal version, V6 exact build needs new browser attestation and separate owner handoff.',
'12':'Independent duly authorized reviewer and exact build owner final not performed.'}
scoped={
'01':['SHA_PINNED_V22_ABC_SOURCE'],'02':['REAL_12_ID_POS_NEG_CONTRACT_VALIDATOR'],
'03':['A_B_C_24_ORACLES_DESIGNED'],'04':['V6_RUNTIME_BUILD_SHA_ATTESTATION_SCOPED'],
'05':['OWNER_SAFARI_60_OF_60_3_TASKS'],'06':['PROVIDER_ROUTE_NEGATIVE_SCOPED'],
'07':['V6_HTTP_FRAMING_RED_GREEN','TEN_THOUSAND_PLUS_CORE_REPLAY','TEN_THOUSAND_PLUS_REAL_HTTP_DENIAL'],
'08':['V4_TRUE_ROLLBACK_AND_RESTART_REGRESSION'],'09':[],
'10':['ONE_OWNER_SAFARI_SESSION','THREE_HTTP_E2E_NOT_BROWSER'],
'11':['BYTE_IDENTICAL_PRIOR_ZIP','V6_SOURCE_SHA_BOUND_BROWSER_READY_BUT_NOT_OWNER_TESTED'],
'12':[]}
rows=[]
for t in v['tasks']:
 i=t['id'];rows.append({'original_id':i,'gate':t['primary_gate'],'title':t['title'],'original_positive_oracle':t['positive_oracle'],'original_negative_oracle':t['negative_oracle'],'required_completion_evidence':t['required_completion_evidence'],'owner_authority_original':t['authority'],'scoped_current_evidence':scoped[i],'technical_full_closure':'HOLD_ORIGINAL_ORACLE_OR_AUTHORITY','formal_closure':'HOLD','unmet_condition':reason[i]})
result={'schema':'enguru.ulmi.h1.v22.id-original-reconciliation-v11','original_V22_sha256':sha(V.read_bytes()),'original_ABC_sha256':sha(P.read_bytes()),'owner_safari_receipt_sha256':sha(SAFARI.read_bytes()),'h1_source_parent_sha256':'a7ff9d7e72066499c6f29b0a609bcf919db66e7a9356c27d3f2fcb4c3a631f5b','historical_technical_claim_preserved':'4/12 HISTORICAL, ID-level original acceptance proof insufficient to lift from historical claim','new_strict_verified_original_ids_in_this_run':[],'official_12_status':'0/12 HOLD','technical_current_full':'NOT_COMPUTABLE_FROM_SCOPED_ONLY_NO_OVERPROMOTION','all_original_task_ids':rows,'structural_checks_passed':sum(c['passed'] for c in checks),'structural_checks_total':len(checks),'tests':checks,'independent_reviewer':'NOT_EXECUTED','owner_final':'NOT_ISSUED','donecheck':'HOLD','verified_finish':'HOLD'}
RPT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('RECOUNT_STRUCTURE',result['structural_checks_passed'],'/',result['structural_checks_total'])
for x in checks:
 if not x['passed']:print('FAIL',x['control'],x['observed'])
print('UNCONDITIONALLY_VERIFIED_ORIGINAL_NEW',len(result['new_strict_verified_original_ids_in_this_run']),'/12','HISTORICAL',result['historical_technical_claim_preserved'])
if len(checks)!=16 or not all(c['passed'] for c in checks):sys.exit(1)
