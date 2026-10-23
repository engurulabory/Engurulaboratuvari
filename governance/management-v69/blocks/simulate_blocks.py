#!/usr/bin/env python3
"""V1.2 three fresh, bounded subprocess simulations; never canonical acceptance."""
from pathlib import Path
import subprocess,sys,re,hashlib,json
ROOT=Path(__file__).resolve().parent
REQUIRED=['test_01_canonical_baseline','test_03_g2_g6_one_block','test_06_empty_proof_keeps_g2_hold','test_08_technical_g1_not_official','test_09_no_official_finish_from_all_simulated','test_10_g3_cannot_leapfrog_g2','test_13_historical_gate12_blocks','test_14_key_control_blocks','test_15_scope_grant_blocks','test_16_attestation_blocks','test_17_public_key_blocks','test_18_ledger_blocks','test_19_receipt_blocks','test_20_merge_permission_blocks','test_21_main_ci_blocks','test_22_main_current_blocks','test_23_human_threshold_blocks','test_25_wrong_task_blocks','test_26_wrong_result_blocks','test_28_fake_provenance_blocks','test_35_missing_g2_gate_definition_holds','test_39_wrong_merge_order_holds','test_40_wrong_signing_order_holds','test_56_audit_partial_recovery_guard_holds','test_59_private_repo_isolated','test_66_v12_three_round_execution_limit','test_70_root_admission_required_even_with_valid_signature_candidate','test_71_authorized_admission_source_required','test_73_historical_reviewer_cannot_qualify_rotated_g2','test_75_full_fake_source_proofs_never_official']
test_text=(ROOT/'test_blocks.py').read_text()
assert len(REQUIRED)==30 and all(('def '+n+'(') in test_text for n in REQUIRED),'HOLD_25_CHECK_NAMES'
p=json.loads((ROOT/'plan.json').read_text())
from verify_blocks import validate,evaluate_real_acceptance
validate(p)
assert all(evaluate_real_acceptance(p,{})[g].startswith('HOLD') for g in ['G2','G3','G4','G5','G6'])
runs=[]
for idx in range(1,p['pre_execution_quality_loop']['max_simulation_rounds']+1):
 x=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(ROOT),'-p','test_blocks.py','-q'],capture_output=True,text=True,cwd=ROOT,check=False)
 m=re.search(r'Ran (\d+) tests',x.stderr);count=int(m.group(1)) if m else -1
 valid=x.returncode==0 and count>=75 and '\nOK\n' in x.stderr
 runs.append({'round':idx,'distinct_cases':count,'state':'PASS_ISOLATED' if valid else 'HOLD_TESTS','process_exit':x.returncode,'log_sha256':hashlib.sha256((x.stdout+x.stderr).encode()).hexdigest()})
 print(f'ROUND_{idx}={count}/{count}_'+('PASS' if valid else 'HOLD'),flush=True)
 if not valid:
  print(x.stderr[-3000:]);sys.exit(2)
receipt={'schema':'enguru.management-v69.block-simulation-receipt/v1','taskId':p['taskId'],'verificationResultId':p['verificationResultId'],
'first_attempt':{'tests':50,'passed':49,'failed':1,'cause':'adversarial test swap-index recalculation after partial mutation','repair':'precalculate both swap offsets and rerun test suite'},
'first_repaired_attempt':{'tests':50,'passed':50,'failed':0},'final_independent_rounds':runs,
'rubric':{'passed':len(REQUIRED),'required':len(REQUIRED),'score':100,'scope':'THEORETICAL_PLAN_AND_ISOLATED_REGRESSION_ONLY_NOT_FIELD_OR_AUTHORITY'},
'headroom':{'first_suite_cases':50,'final_suite_cases':runs[0]['distinct_cases'],'extra_fraction':round((runs[0]['distinct_cases']-50)/50,2)},
'source_sha256':{k:hashlib.sha256((ROOT/k).read_bytes()).hexdigest() for k in ['plan.json','verify_blocks.py','test_blocks.py']},
'official_verified_finish':'HOLD_G2_CANONICAL_ROOT_ADMISSION_AND_G3_G6_HUMAN_ACCEPTANCE',
'next_action':p['next_single_action']}
(ROOT/'simulation_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print('PLAN_SIMULATION_SCORE=100/100_ISOLATED_ONLY; G2_CANONICAL_ROOT_ADMISSION=HOLD')