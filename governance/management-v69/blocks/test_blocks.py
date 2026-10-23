import copy
import json
import unittest
from pathlib import Path
from verify_blocks import validate,evaluate_real_acceptance,Hold,TYPES,AUTH,GATES
P=json.loads(Path(__file__).with_name('plan.json').read_text())
FAKE='a'*64

def real(g):
  return {'gateId':g,'taskId':P['taskId'],'verificationResultId':P['verificationResultId'],'kind':TYPES[g],'independentlyVerified':True,'authority':AUTH[g],'provenance':'REAL_CANONICAL_EXTERNAL','evidenceSha256':FAKE,'simulation':False,'reviewerId':P['source']['reviewer_candidate'],'keyId':P['source']['rotated_reviewer_key_id'],'verifierIdentity':'OSi_CANONICAL_OWNER_TEST_FIXTURE',**({'ownerSignerControl':True,'exactScopedGrantVerified':True,'historicalGate12Used':False,'canonicalRootAdmissionVerified':True,'admissionPolicySourceVerified':True,'rootKeyId':P['source']['proposed_owner_root_key_id']} if g=='G2' else {}),**({'realEd25519AttestationVerified':True,'pinnedPemDigestVerified':True} if g=='G3' else {}),**({'ledgerChainVerified':True,'canonicalReceiptVerified':True} if g=='G4' else {}),**({'ownerMergeAuthorized':True,'postMergeExactMainCiPassed':True,'currentMainShaVerified':True} if g=='G5' else {}),**({'humanThresholdAccepted':True,'officialReceiptVerified':True} if g=='G6' else {})}

def fake_mismatch(g,field,value):
    e={x:real(x) for x in GATES[1:]};e[g][field]=value;return e

class BlockContract(unittest.TestCase):
 def assertHold(self,fn):
    with self.assertRaises(Hold):fn()
 def test_01_canonical_baseline(self):self.assertEqual(validate(P)['design_state'],'PASS_ISOLATED_PLAN_CONTRACT')
 def test_02_g1_preserved(self):self.assertEqual(P['blocks'][0]['gate_ids'],['G1'])
 def test_03_g2_g6_one_block(self):self.assertEqual(P['blocks'][1]['gate_ids'],GATES[1:])
 def test_04_support_separate(self):self.assertEqual(P['blocks'][2]['gate_ids'],[])
 def test_05_post_finish_preserved(self):self.assertEqual(P['blocks'][3]['mode'],'DEFER_AFTER_VERIFIED_FINISH')
 def test_06_empty_proof_keeps_g2_hold(self):self.assertTrue(evaluate_real_acceptance(P,{})['G2'].startswith('HOLD'))
 def test_07_empty_proof_keeps_g6_hold(self):self.assertTrue(evaluate_real_acceptance(P,{})['G6'].startswith('HOLD'))
 def test_08_technical_g1_not_official(self):self.assertEqual(evaluate_real_acceptance(P,{})['G1'],'PASS_TECHNICAL_ONLY')
 def test_09_no_official_finish_from_all_simulated(self):
    x={g:dict(real(g),simulation=True) for g in GATES[1:]};self.assertEqual(evaluate_real_acceptance(P,x)['official'],'REQUIRES_CANONICAL_EXTERNAL_DECISION_ALWAYS')
 def test_10_g3_cannot_leapfrog_g2(self):self.assertTrue(evaluate_real_acceptance(P,{'G3':real('G3')})['G3'].startswith('HOLD'))
 def test_11_only_g2_candidate(self):self.assertTrue(evaluate_real_acceptance(P,{'G2':real('G2')})['G3'].startswith('HOLD'))
 def test_12_full_fake_real_metadata_never_official(self):self.assertEqual(evaluate_real_acceptance(P,{g:real(g) for g in GATES[1:]})['official'],'REQUIRES_CANONICAL_EXTERNAL_DECISION_ALWAYS')
 def test_13_historical_gate12_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','historicalGate12Used',True))['G2'].startswith('HOLD'))
 def test_14_key_control_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','ownerSignerControl',False))['G2'].startswith('HOLD'))
 def test_15_scope_grant_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','exactScopedGrantVerified',False))['G2'].startswith('HOLD'))
 def test_16_attestation_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G3','realEd25519AttestationVerified',False))['G3'].startswith('HOLD'))
 def test_17_public_key_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G3','pinnedPemDigestVerified',False))['G3'].startswith('HOLD'))
 def test_18_ledger_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G4','ledgerChainVerified',False))['G4'].startswith('HOLD'))
 def test_19_receipt_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G4','canonicalReceiptVerified',False))['G4'].startswith('HOLD'))
 def test_20_merge_permission_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G5','ownerMergeAuthorized',False))['G5'].startswith('HOLD'))
 def test_21_main_ci_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G5','postMergeExactMainCiPassed',False))['G5'].startswith('HOLD'))
 def test_22_main_current_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G5','currentMainShaVerified',False))['G5'].startswith('HOLD'))
 def test_23_human_threshold_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G6','humanThresholdAccepted',False))['G6'].startswith('HOLD'))
 def test_24_final_receipt_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G6','officialReceiptVerified',False))['G6'].startswith('HOLD'))
 def test_25_wrong_task_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','taskId','OTHER'))['G2'].startswith('HOLD'))
 def test_26_wrong_result_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','verificationResultId','OTHER'))['G2'].startswith('HOLD'))
 def test_27_wrong_authority_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','authority','UNTRUSTED'))['G2'].startswith('HOLD'))
 def test_28_fake_provenance_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','provenance','SIMULATED'))['G2'].startswith('HOLD'))
 def test_29_fake_sha_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','evidenceSha256','AAAA'))['G2'].startswith('HOLD'))
 def test_30_wrong_verifier_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','independentlyVerified',False))['G2'].startswith('HOLD'))
 def test_31_wrong_gate_id_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','gateId','G6'))['G2'].startswith('HOLD'))
 def test_32_wrong_kind_blocks(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','kind',TYPES['G5']))['G2'].startswith('HOLD'))
 def test_33_no_key_leak_in_plan(self):self.assertNotIn('PRIVATE KEY',json.dumps(P))
 def test_34_simulator_has_no_write_actions(self):self.assertNotIn('AUTOMATIC_MERGE',json.dumps(P))
 def test_35_missing_g2_gate_definition_holds(self):
    x=copy.deepcopy(P);del x['gates']['G2'];self.assertHold(lambda:validate(x))
 def test_36_duplicate_gate_holds(self):
    x=copy.deepcopy(P);x['canonical_gate_ids'].append('G6');self.assertHold(lambda:validate(x))
 def test_37_wrong_g2_scope_holds(self):
    x=copy.deepcopy(P);x['gates']['G2']['authority']='TECHNICAL_VALIDATOR';self.assertHold(lambda:validate(x))
 def test_38_fake_g2_pass_holds(self):
    x=copy.deepcopy(P);x['gates']['G2']['state']='PASS';self.assertHold(lambda:validate(x))
 def test_39_wrong_merge_order_holds(self):
    x=copy.deepcopy(P);s=x['blocks'][1]['sequence'];i=s.index('AUTHORIZED_PR203_MERGE');j=s.index('CANONICAL_DONECHECK_LEDGER');s[i],s[j]=s[j],s[i];self.assertHold(lambda:validate(x))
 def test_40_wrong_signing_order_holds(self):
    x=copy.deepcopy(P);s=x['blocks'][1]['sequence'];i=s.index('VERIFY_EXACT_TASK_RESULT_GRANT');j=s.index('SIGN_CANONICAL_HUMAN_REVIEW');s[i],s[j]=s[j],s[i];self.assertHold(lambda:validate(x))
 def test_41_missing_post_merge_ci_holds(self):
    x=copy.deepcopy(P);x['blocks'][1]['sequence'].remove('POST_MERGE_EXACT_MAIN_CI');self.assertHold(lambda:validate(x))
 def test_42_sidecar_accepted_as_gate_holds(self):
    x=copy.deepcopy(P);x['blocks'][2]['gate_ids']=['G7'];self.assertHold(lambda:validate(x))
 def test_43_wrong_technical_progress_holds(self):
    x=copy.deepcopy(P);x['progress']['technical_gate_pass']=6;self.assertHold(lambda:validate(x))
 def test_44_temporary_issuer_holds(self):
    x=copy.deepcopy(P);x['invariants']['never_use_historical_gate12_as_v69_grant']=False;self.assertHold(lambda:validate(x))
 def test_45_no_owner_merge_automation(self):
    x=copy.deepcopy(P);x['invariants']['no_automatic_human_threshold_or_merge']=False;self.assertHold(lambda:validate(x))
 def test_46_private_key_protection(self):
    x=copy.deepcopy(P);x['invariants']['private_key_remains_under_mac_owner_control']=False;self.assertHold(lambda:validate(x))
 def test_47_exact_g2_no_override(self):self.assertEqual(P['next_single_action'],'G2_EXISTING_CANONICAL_OSI_ROOT_ADMISSION_AUTHORIZED_POLICY_AND_VERIFIED_RECEIPT')
 def test_48_g1_no_new_authority(self):self.assertEqual(P['gates']['G1']['authority'],'TECHNICAL_VALIDATOR')
 def test_49_support_5min_best_effort(self):self.assertIn('BEST_EFFORT',P['blocks'][2]['schedule'])
 def test_50_support_no_private_relay(self):self.assertEqual(P['blocks'][2]['private_data_boundary'],'OWNER_APPROVED_REDACTED_RELAY_ONLY')
 def test_51_wrong_reviewer_claim_stays_hold(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','reviewerId','SOMEONE'))['G2'].startswith('HOLD'))
 def test_52_wrong_key_claim_stays_hold(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','keyId','ed25519-sha256:'+'f'*64))['G2'].startswith('HOLD'))
 def test_53_missing_verifier_identity_stays_hold(self):self.assertTrue(evaluate_real_acceptance(P,fake_mismatch('G2','verifierIdentity',None))['G2'].startswith('HOLD'))
 def test_54_proof_metadata_remains_candidate(self):
    r=evaluate_real_acceptance(P,{g:real(g) for g in GATES[1:]})
    self.assertEqual(r['G6'],'CANDIDATE_REQUIRES_CANONICAL_EXTERNAL_VERIFICATION')
    self.assertEqual(r['official'],'REQUIRES_CANONICAL_EXTERNAL_DECISION_ALWAYS')
 def test_55_audit_partial_recovery_present(self):self.assertIn('RECONCILE_LEDGER_AFTER_INTERRUPTION',P['blocks'][1]['sequence'])
 def test_56_audit_partial_recovery_guard_holds(self):
    x=copy.deepcopy(P);x['blocks'][1]['sequence'].remove('RECONCILE_LEDGER_AFTER_INTERRUPTION');self.assertHold(lambda:validate(x))
 def test_57_main_refresh_guard_holds(self):
    x=copy.deepcopy(P);x['blocks'][1]['sequence'].remove('REFRESH_EXACT_CURRENT_MAIN_AND_REVIEW');self.assertHold(lambda:validate(x))
 def test_58_independent_finish_guard_holds(self):
    x=copy.deepcopy(P);x['blocks'][1]['sequence'].remove('VERIFY_INDEPENDENT_DONECHECK_AND_HUMAN_THRESHOLD');self.assertHold(lambda:validate(x))
 def test_59_private_repo_isolated(self):
    x=copy.deepcopy(P);x['invariants']['private_repo_data_owner_redacted_relay_only']=False;self.assertHold(lambda:validate(x))
 def test_60_fake_source_claim_cannot_authorize(self):
    x=copy.deepcopy(P);x['invariants']['evidence_claims_are_never_self_authorizing']=False;self.assertHold(lambda:validate(x))
 def test_61_incomplete_owner_scope_blocks_g5(self):
    e={g:real(g) for g in GATES[1:]};e['G2']['exactScopedGrantVerified']=False
    self.assertTrue(evaluate_real_acceptance(P,e)['G5'].startswith('HOLD'))
 def test_62_old_main_without_refresh_guard_fails(self):
    x=copy.deepcopy(P);x['blocks'][1]['sequence'].remove('REFRESH_EXACT_CURRENT_MAIN_AND_REVIEW');self.assertHold(lambda:validate(x))
 def test_63_post_merge_exact_main_ci_is_obligatory(self):
    x=copy.deepcopy(P);x['blocks'][1]['sequence'].remove('POST_MERGE_EXACT_MAIN_CI');self.assertHold(lambda:validate(x))
 def test_64_no_owner_scope_missing_from_control(self):
    x=copy.deepcopy(P);x['invariants']['no_automatic_human_threshold_or_merge']=False;self.assertHold(lambda:validate(x))
 def test_65_explicit_no_official_acceptance(self):
    self.assertEqual(evaluate_real_acceptance(P,{g:real(g) for g in GATES[1:]})['official'],'REQUIRES_CANONICAL_EXTERNAL_DECISION_ALWAYS')

 def test_66_v12_three_round_execution_limit(self):
    self.assertEqual(P['pre_execution_quality_loop']['max_simulation_rounds'],3)
 def test_67_v12_modified_max_rounds_holds(self):
    x=copy.deepcopy(P);x['pre_execution_quality_loop']['max_simulation_rounds']=4
    self.assertHold(lambda:validate(x))
 def test_68_v12_rubric_100_is_enforced(self):
    x=copy.deepcopy(P);x['pre_execution_quality_loop']['scoring']['dimensions'][0]['max']=25
    self.assertHold(lambda:validate(x))
 def test_69_v12_boundaries_are_required(self):
    x=copy.deepcopy(P);x['pre_execution_quality_loop']['engineering_boundaries']=[]
    self.assertHold(lambda:validate(x))
 def test_70_root_admission_required_even_with_valid_signature_candidate(self):
    e={g:real(g) for g in GATES[1:]};e['G2']['canonicalRootAdmissionVerified']=False
    self.assertTrue(evaluate_real_acceptance(P,e)['G2'].startswith('HOLD'))
 def test_71_authorized_admission_source_required(self):
    e={g:real(g) for g in GATES[1:]};e['G2']['admissionPolicySourceVerified']=False
    self.assertTrue(evaluate_real_acceptance(P,e)['G2'].startswith('HOLD'))
 def test_72_reject_unadmitted_root_identity(self):
    e={g:real(g) for g in GATES[1:]};e['G2']['rootKeyId']='ed25519-sha256:'+'f'*64
    self.assertTrue(evaluate_real_acceptance(P,e)['G2'].startswith('HOLD'))
 def test_73_historical_reviewer_cannot_qualify_rotated_g2(self):
    e={g:real(g) for g in GATES[1:]};e['G2']['keyId']=P['source']['key_id']
    self.assertTrue(evaluate_real_acceptance(P,e)['G2'].startswith('HOLD'))
 def test_74_g3_technical_ready_not_human_signed_review(self):
    x=copy.deepcopy(P);x['gates']['G3']['state']='PASS'
    self.assertHold(lambda:validate(x))
 def test_75_full_fake_source_proofs_never_official(self):
    e={g:real(g) for g in GATES[1:]}
    out=evaluate_real_acceptance(P,e)
    self.assertEqual(out['G6'],'CANDIDATE_REQUIRES_CANONICAL_EXTERNAL_VERIFICATION')
    self.assertEqual(out['official'],'REQUIRES_CANONICAL_EXTERNAL_DECISION_ALWAYS')

if __name__=='__main__':unittest.main()