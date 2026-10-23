#!/usr/bin/env python3
"""Review-only verification and adversarial simulation for existing V6.9 gates.
No network or production writes; no signing, DoneCheck, merge, or owner authority.
"""
import argparse
import copy
import json
import re
from pathlib import Path

SOURCE=Path(__file__).with_name('plan.json')
GATES=['G1','G2','G3','G4','G5','G6']
AUTH={'G1':'TECHNICAL_VALIDATOR','G2':'OSi_CANONICAL_OWNER_TRUST','G3':'AUTHORIZED_HUMAN_REVIEWER','G4':'DONECHECK_AUTHORIZED_RUNTIME','G5':'HUMAN_OWNER_RESERVED_MERGE','G6':'CANONICAL_HUMAN_THRESHOLD'}
TYPES={'G2':'REAL_OSI_OWNER_CRYPTOGRAPHIC_SCOPE_PROOF','G3':'REAL_OWNER_SIGNED_REVIEW_AND_BRIDGE','G4':'CANONICAL_DONECHECK_RECEIPT_AND_AUDIT','G5':'AUTHORIZED_MERGE_AND_POST_MERGE_EXACT_MAIN_CI','G6':'INDEPENDENT_OFFICIAL_VERIFIED_FINISH'}

class Hold(Exception):pass

def require(check, code):
    if not check: raise Hold('HOLD_'+code)

def validate(p):
    require(p.get('schema')=='enguru.management-v69.execution-block-plan/v1','SCHEMA')
    require(p.get('taskId')=='ENGURU_MANAGEMENT_V69_PR_203','TASK_ID')
    require(p.get('verificationResultId')=='MGMT69_VR_GITHUB_RUN_39852715540','RESULT_ID')
    require(p.get('canonical_gate_ids')==GATES,'GATE_IDS')
    g=p.get('gates',{});require(set(g)==set(GATES),'GATE_COVERAGE')
    require(g['G1']['state']=='PASS_TECHNICAL_ONLY','G1_NOT_OFFICIAL')
    for i,gate in enumerate(GATES):
        row=g[gate]
        require(row.get('authority')==AUTH[gate],'AUTH_'+gate)
        require(row.get('prerequisites')==([] if i==0 else [GATES[i-1]]),'ORDER_'+gate)
        require(isinstance(row.get('acceptance'),str) and len(row['acceptance'])>=36,'ACCEPTANCE_'+gate)
        if i>0:
            require(row.get('state','').startswith('HOLD_'),'OFFICIAL_GATE_'+gate)
            require(row.get('evidence_type')==TYPES[gate],'EVIDENCE_'+gate)
    blocks=p.get('blocks',[])
    require([b.get('id') for b in blocks]==['B00','B01','B02','B03'],'BLOCK_IDS')
    require(blocks[0]['gate_ids']==['G1'],'G1_PRESERVE')
    require(blocks[1]['gate_ids']==GATES[1:],'G2_G6_UNIFIED')
    require(blocks[1]['mode']=='SINGLE_ACTIVE_INTEGRATED_EXECUTION','ONE_ACTIVE')
    require(blocks[1]['owner']=='OSi_CANONICAL_OWNER_AND_DONECHECK','OWNER')
    require(blocks[2]['mode']=='PARALLEL_NON_BLOCKING_SUPPORT' and blocks[2]['gate_ids']==[],'SUPPORT_IND')
    require(blocks[3]['mode']=='DEFER_AFTER_VERIFIED_FINISH' and blocks[3]['gate_ids']==[],'POST_FINISH')
    require(len(blocks[1]['sequence'])==11 and len(set(blocks[1]['sequence']))==11,'SINGLE_SEQUENCE')
    require('POST_MERGE_EXACT_MAIN_CI' in blocks[1]['sequence'],'POST_MERGE_CI')
    require('RECONCILE_LEDGER_AFTER_INTERRUPTION' in blocks[1]['sequence'],'LEDGER_RECOVERY')
    require('REFRESH_EXACT_CURRENT_MAIN_AND_REVIEW' in blocks[1]['sequence'],'CURRENT_MAIN_REVIEW')
    require('VERIFY_INDEPENDENT_DONECHECK_AND_HUMAN_THRESHOLD' in blocks[1]['sequence'],'INDEPENDENT_FINAL_REVIEW')
    require(blocks[1]['sequence'].index('REFRESH_EXACT_CURRENT_MAIN_AND_REVIEW')<blocks[1]['sequence'].index('AUTHORIZED_PR203_MERGE'),'MAIN_BEFORE_MERGE')
    require(blocks[1]['sequence'].index('RECONCILE_LEDGER_AFTER_INTERRUPTION')<blocks[1]['sequence'].index('AUTHORIZED_PR203_MERGE'),'LEDGER_RECOVERY_BEFORE_MERGE')
    require(blocks[1]['sequence'].index('VERIFY_EXACT_TASK_RESULT_GRANT')<blocks[1]['sequence'].index('SIGN_CANONICAL_HUMAN_REVIEW'),'GRANT_BEFORE_SIGN')
    require(blocks[1]['sequence'].index('CANONICAL_DONECHECK_LEDGER')<blocks[1]['sequence'].index('AUTHORIZED_PR203_MERGE'),'AUDIT_BEFORE_MERGE')
    require(blocks[1]['sequence'].index('AUTHORIZED_PR203_MERGE')<blocks[1]['sequence'].index('INDEPENDENT_VERIFIED_FINISH'),'MERGE_BEFORE_FINAL')
    inv=p['invariants']
    for key in ['no_parallel_gate_authority','main_and_pr203_immutable_until_authorized_merge','never_use_historical_gate12_as_v69_grant','private_key_remains_under_mac_owner_control','no_automatic_human_threshold_or_merge','simulation_cannot_produce_official_pass','official_finished_requires_all_six_independently_verified','resume_requires_current_github_and_canonical_authority_read','new_conversation_reads_latest_mk_record','positive_language_and_eight_stages','evidence_claims_are_never_self_authorizing','audit_partial_append_recovery_before_retry','private_repo_data_owner_redacted_relay_only']:
        require(inv.get(key) is True,'INVARIANT_'+key)
    require(inv['single_active_product_block']=='B01','ACTIVE_BLOCK')
    s=p['source']
    for key in ('management_head','last_main'):
        require(bool(re.fullmatch('[0-9a-f]{40}',s.get(key,''))),'SHA_'+key)
    for key in ('mac_os_contract_report_sha256','canonical_v3_source_sha256'):
        require(bool(re.fullmatch('[0-9a-f]{64}',s.get(key,''))),'SHA_'+key)
    require(s['management_pr']==203 and s['engineer_private_pr']==14,'PR_SCOPE')
    require(p['progress']=={'technical_gate_pass':1,'gate_total':6,'fully_accepted_g2_g6':0,'g2_g6_total':5,'official_verified_finish':'HOLD','official_authority_pass':0},'COUNTERS')
    require('OWNER_GRANT' in p['next_single_action'],'NEXT_G2')
    return {'design_state':'PASS_ISOLATED_PLAN_CONTRACT','official_finish':'HOLD','covered':GATES,'active':'B01'}

def evaluate_real_acceptance(p, evidence):
    """Review-only status projection; authoritative DoneCheck is independent.
    Each piece must carry an independently verified non-simulated owner/evidence check.
    """
    validate(p)
    result={'G1':'PASS_TECHNICAL_ONLY'}
    prior=True
    for gate in GATES[1:]:
        e=evidence.get(gate)
        valid=(isinstance(e,dict) and
          e.get('gateId')==gate and e.get('taskId')==p['taskId'] and
          e.get('verificationResultId')==p['verificationResultId'] and
          e.get('kind')==TYPES[gate] and e.get('independentlyVerified') is True and
          e.get('authority')==AUTH[gate] and e.get('provenance')=='REAL_CANONICAL_EXTERNAL' and
          isinstance(e.get('evidenceSha256'),str) and bool(re.fullmatch('[0-9a-f]{64}',e['evidenceSha256'])) and
          e.get('simulation') is False and
          e.get('reviewerId')==p['source']['reviewer_candidate'] and
          e.get('keyId')==p['source']['key_id'] and
          isinstance(e.get('verifierIdentity'),str) and len(e.get('verifierIdentity'))>=8)
        if gate=='G2':
            valid=valid and e.get('ownerSignerControl') is True and e.get('exactScopedGrantVerified') is True and e.get('historicalGate12Used') is False
        if gate=='G3': valid=valid and e.get('realEd25519AttestationVerified') is True and e.get('pinnedPemDigestVerified') is True
        if gate=='G4': valid=valid and e.get('ledgerChainVerified') is True and e.get('canonicalReceiptVerified') is True
        if gate=='G5': valid=valid and e.get('ownerMergeAuthorized') is True and e.get('postMergeExactMainCiPassed') is True and e.get('currentMainShaVerified') is True
        if gate=='G6': valid=valid and e.get('humanThresholdAccepted') is True and e.get('officialReceiptVerified') is True
        prior=bool(prior and valid)
        result[gate]='CANDIDATE_REQUIRES_CANONICAL_EXTERNAL_VERIFICATION' if prior else p['gates'][gate]['state']
    result['official']='REQUIRES_CANONICAL_EXTERNAL_DECISION_ALWAYS'
    return result

def run():
    parser=argparse.ArgumentParser();parser.add_argument('--plan',type=Path,default=SOURCE);parser.add_argument('--check',action='store_true');a=parser.parse_args()
    p=json.loads(a.plan.read_text())
    report=validate(p)
    if a.check:print(json.dumps(report,sort_keys=True))
    else:print(json.dumps({'plan':report,'empty_evidence':evaluate_real_acceptance(p,{})},sort_keys=True))

if __name__=='__main__':run()