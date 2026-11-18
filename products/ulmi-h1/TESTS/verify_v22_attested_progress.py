#!/usr/bin/env python3
"""ULMi V22 unprivileged evidence reconciliation, not an independent signer.

No author-manufactured acceptance. Count IDs, not test checks. Fail closed on
immutable contract identity, recorded source byte mismatch and missing negative proof.
"""
from pathlib import Path
import hashlib,json,sys,re,copy

R=Path(__file__).resolve().parents[1]
E=R/'EVIDENCE'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CONTRACT=R/'ORIGINALS/V22_IMMUTABLE_SOURCE.json'
PILOTS=R/'ORIGINALS/PILOT_ABC_IMMUTABLE_SOURCE.json'
EXPECTED_V22='069c03b0f299e76ef46e26a25eb4284474ae5219353185a88386ee5df9f39304'
EXPECTED_ABC='5beb10d407dc550d7f979062fef6bdcfd451791103d5b02fc1c2d05a1786d79b'
assert sha(CONTRACT)==EXPECTED_V22, 'immutable original V22 drift'
assert sha(PILOTS)==EXPECTED_ABC, 'immutable original A/B/C drift'
v=json.loads(CONTRACT.read_text());p=json.loads(PILOTS.read_text());
assert len(v['tasks'])==12 and len({x['id'] for x in v['tasks']})==12
assert {x['id'] for x in v['tasks']}=={f'{n:02d}' for n in range(1,13)}
assert all(x['positive_oracle'] and x['negative_oracle'] and x['required_completion_evidence'] for x in v['tasks'])
assert len(p['pilots'])==3 and all(x['execution_grant'] is None for x in p['pilots'])

# Each actual executed log must be present, have expected typed result, and is
# bound by SHA. These logs prove only their precise test scopes.
proofs={
 'W02_STRUCTURE':('RETEST_reconcile_v22_12_original_tasks.log',r'RECOUNT_STRUCTURE 16 / 16'),
 'W04_FIFO_RED':('W04_FIFO_RED_BEFORE_PATCH.log',r'FAIL_FIFO_BLOCKED'),
 'W04_FIFO_GREEN':('W04_FIFO_GREEN_AFTER_PATCH.log',r'W04_FIFO_NONBLOCK=PASS'),
 'W04_NOFOLLOW':('W04_NOFOLLOW_REGRESSION_AFTER_FIFO.log',r'RACE_ACTUALLY_TRIGGERED'),
 'W04_ARCHIVED':('W04_ARCHIVED_REGRESSION_AFTER_FIFO.log',r'W04_ARCHIVED_RESEARCH_CONTEXT 8 / 8'),
 'W04_HTTP':('W04_HTTP_REGRESSION_AFTER_FIFO.log',r'NO_WRITTEN_ENGINEERING_TASKS 0'),
 'W04_BOUNDARY':('RETEST_test_w04_role_context_contract.log',r'W04_SYNTHETIC_ROLE_AND_32768_BYTE_TESTS=PASS'),
 'W04_V7_RED_V71_GREEN':('RETEST_verify_w04_red_green.log',r'GREEN_V71_RACED_SYMLINK_DENIED'),
 'W01_SOURCE':('W01_W02_W04_SOURCE_RECOUNT.log',r'W01_GITHUB 4 / 4'),
 'W08_ROLLBACK':('RETEST_run_v4_safe_rollback.log',r'Ran 6 tests in .*\n\nOK'),
 'W08_HTTP_ROLLBACK':('RETEST_run_v4_http_rollback_e2e.log',r'PASS'),
 'W10_TECHNICAL':('RETEST_run_final_e2e.log',r'FINAL_REAL_CHECKS 49 / 49 RUNS 3'),
 'W05_W06_MODEL_SYNTHETIC':('RETEST_run_v7_model_provenance_e2e.log',r'V7_PROVIDER_RED_GREEN 25 / 25'),
 'W06_SHARED_AI_SYNTHETIC':('RETEST_run_v7_shared_ai_source_boundary.log',r'PASS'),
 'W11_SOURCE_HTTP':('RETEST_run_v7_source_build_identity_e2e.log',r'SUMMARY 7 / 7'),
 'W02_PROJECT':('RETEST_run_project_bound_e2e.log',r'PASS'),
 'W02_GENERATED_TASKBOARD':('RETEST_run_generated_taskboard_e2e.log',r'PASS'),
}
actual={}
for key,(filename,pattern) in proofs.items():
 file=E/filename
 assert file.is_file(),('MISSING_PROOF',filename)
 contents=file.read_text()
 assert re.search(pattern,contents),('PROOF_ORACLE_FAIL',key,filename)
 actual[key]={'file':f'EVIDENCE/{filename}','sha256':sha(file),'scope':'AUTHOR_EXECUTED_SCOPED','pattern':pattern}

source_original=R/'RESEARCH_ARCHIVE'/'canonical_sources'/'AGENTS.md'
assert source_original.is_file(), 'missing canonical AGENTS archive'
assert sha(R/'PRODUCT/chat_bridge.py')!= '826d09aac3dd430b6bde55b726d166d5acb7b141939d874bbbbd60498712d968', 'W04 patch missing'
assert 'os.O_NONBLOCK' in (R/'PRODUCT/chat_bridge.py').read_text(), 'FIFO patch missing'

# Historical 4/12 has no per-original-acceptance proof; never convert it into
# current verified count. A test passing is not a task closing.
open_by_id={
'01':'READ_ONLY_CANONICAL_ROLE_SOURCE_PLUS_AUTHENTIC_PRODUCER_REQUIRED',
'02':'OWNER_ORIGINAL_ACCEPTANCE_GATE_OPEN',
'03':'ORIGINAL_A_B_C_SEPARATE_GRANTS_AND_REAL_8_EACH_OPEN',
'04':'LIVE_SHA_PINNED_CURRENT_EIGHT_ROLES_OWNER_GRANT_INDEPENDENT_REVIEW_OPEN',
'05':'REAL_QWEN_TURKISH_REPLY_AND_NEW_OWNER_SAFARI_UAT_OPEN',
'06':'REAL_QWEN_AND_SHARED_AI_AUTHORITATIVE_A_B_OPEN',
'07':'AUTHENTICATED_PRODUCER_AND_FULL_ORIGINAL_REPLAY_RESET_ORACLES_OPEN',
'08':'INDEPENDENT_ORIGINAL_AUTHORIZED_RECOVERY_ACCEPTANCE_OPEN',
'09':'REAL_MODEL_TURKISH_QUALITY_AND_INDEPENDENT_CRITIQUE_OPEN',
'10':'THREE_DISTINCT_REAL_OWNER_BROWSER_E2E_OPEN',
'11':'SINGLE_FINAL_SHA_INDEPENDENT_OWNER_HANDOFF_AND_TRANSFER_OPEN',
'12':'INDEPENDENT_AUTHORIZED_DONECHECK_AND_EXACT_BUILD_OWNER_ACCEPTANCE_OPEN'}
evidence_map={
'01':['W01_SOURCE','W04_ARCHIVED'],
'02':['W02_STRUCTURE','W02_PROJECT','W02_GENERATED_TASKBOARD'],
'03':[],
'04':['W04_FIFO_RED','W04_FIFO_GREEN','W04_NOFOLLOW','W04_ARCHIVED','W04_HTTP','W04_BOUNDARY','W04_V7_RED_V71_GREEN'],
'05':['W05_W06_MODEL_SYNTHETIC'],
'06':['W05_W06_MODEL_SYNTHETIC','W06_SHARED_AI_SYNTHETIC'],
'07':[],
'08':['W08_ROLLBACK','W08_HTTP_ROLLBACK'],
'09':[],
'10':['W10_TECHNICAL'],
'11':['W11_SOURCE_HTTP'],
'12':[]}

records=[]
for t in v['tasks']:
 id=t['id']
 records.append({'original_id':id,'original_block':t['block'],'title':t['title'],
 'positive_oracle':t['positive_oracle'],'negative_oracle':t['negative_oracle'],
 'original_required_evidence':t['required_completion_evidence'],'original_authority_field':t['authority'],
 'scoped_actual_proof_ids':evidence_map[id],
 'scoped_actual_test_sha':[actual[key]['sha256'] for key in evidence_map[id]],
 'technical_full_current':'HOLD_UNPROVEN_ORIGINAL_COMPLETION',
 'formal_original':'HOLD_NO_INDEPENDENT_OWNER_DECISION','exact_remaining':open_by_id[id]})

safari=E/'OWNER_V5_SAFARI_UAT_RAW.json'
s=json.loads(safari.read_text())
assert len(s['checks'])==60 and all(x['status']=='PASS' for x in s['checks'])
assert len(s['tasks'])==3 and s['independent_donecheck']=='NOT_EXECUTED'

# Deliberate independent-of-score adversarial cases in the validator logic.
forged=copy.deepcopy(v['tasks']);forged[1]['id']=forged[0]['id']
assert len(set(x['id'] for x in forged))<12
assert 'SIGNED' not in actual['W04_FIFO_GREEN']['scope']
assert not p['pilots'][1]['execution_grant']
assert len(s['tasks'])!=3 or len({s['started_at']})==1, '3 tasks must not be 3 browser runs'

record={'schema':'enguru.ulmi.h1.v22.12-evidence-closure-accounting-unprivileged/v1',
 'record_date':'2026-11-18','product':'ULMI_H1_V7_W04_ISOLATED_TECHNICAL_DELTA',
 'immutable_original_contract_sha256':sha(CONTRACT),'immutable_pilot_sha256':sha(PILOTS),
 'running_candidate_source_sha256':{'server':sha(R/'PRODUCT/server.py'),'chat_bridge':sha(R/'PRODUCT/chat_bridge.py')},
 'original_12':records,'scoped_actual_proofs':actual,
 'original_work_count':12,'historical_technical_claim':'4/12_NOT_RECALCULATED',
 'current_fully_verified_original_technical_work_count':'NOT_ESTABLISHED',
 'new_original_fully_closed_work_count':0,'formal_original_count':'0/12',
 'owner_v5_browser_sha256':sha(safari),'owner_v5_browser':'60/60_SCOPED_SINGLE_REAL_BROWSER_RUN',
 'owner_v7_browser':'NOT_EXECUTED','real_mac_qwen':'NOT_EXECUTED',
 'independent_donecheck':'NOT_EXECUTED','authenticated_producer':'NOT_PROVEN',
 'owner_final':'NOT_ISSUED','canonical_cas':'NOT_PERFORMED',
 'verified_finish':'HOLD','h2':'PARKED',
 'truth_boundary':'REEXECUTED_LOCAL_TESTS_AND_ARCHIVED_SHA_NOT_OWNER_MAC_OR_INDEPENDENT_ACCEPTANCE'}
output=E/'V22_12_ATTESTED_SCOPED_DELTA_20261118.json'
output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('VERIFIED_LOCAL_PROOF_FAMILIES',len(actual),'/',len(proofs))
print('ORIGINAL_WORK_ITEMS',len(records),'NEW_FULL',0,'FORMAL','0/12','HISTORICAL','4/12')
print('PRODUCT_FINAL','HOLD')
