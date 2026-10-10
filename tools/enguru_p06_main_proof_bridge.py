#!/usr/bin/env python3
"""Read-only P06 MAIN proof bridge. Engineering candidate, never official issuer.

This is an additive adapter proposed for review; it does not mint authority.
Canonical HUMAN and DoneCheck gates remain owned by their existing mechanisms.
"""
from __future__ import annotations
from typing import Any

MAIN='a5f0887b87d120f2b627624635533affa62b1913'
PR='a28932e3c3c67cfbcc83f0d4e6aef68ec8a90921'
REQUIRED_G2=(
    'SOURCE_AND_HISTORY_PIN', 'G1_MERGE_PARENT_AND_TREE_PARITY',
    'MERGED_MAIN_NEW_SHA_MACHINE','NATIVE_7_OF_7','NEGATIVE_3_OF_3',
    'STEWARD_NATIVE','EVIDENCE_OUTPUT_AUTHORITY','P06_POLICY',
    'SWIFT_BOOTSTRAP','REGRESSION_1','REGRESSION_2')
REQUIRED_HUMAN=(
    'CANONICAL_P06_RUNTIME_ACCEPTANCE','OFFICIAL_P06_DONECHECK_PASS',
    'AUTHORIZED_ACCEPTED_CANDIDATE','EXPLICIT_HUMAN_REVIEW')
EXPECTED_V7={'EVIDENCE_IO_11':11,'P06_POLICY_8':8,
             'V08_CANDIDATE_AUTHORITY':9,'V08_OPERATOR':32}


def evaluate(g2:dict[str,Any], v7:dict[str,Any], manifest:dict[str,Any],
             *, observed_head:str) -> dict[str,Any]:
    """Fail-closed source proof assessment; cannot authorize official finish."""
    reasons=[]
    if observed_head!=MAIN:reasons.append('CURRENT_MAIN_HEAD_IDENTITY_REQUIRED')
    if g2.get('state')!='PASS_G2_NEW_MAIN_MACHINE_REVALIDATED_OFFICIAL_ISSUER_HOLD':
        reasons.append('G2_EXACT_MACHINE_RECEIPT_REQUIRED')
    if g2.get('preservation')!='PASS' or g2.get('issues')!=[]:
        reasons.append('G2_EVIDENCE_AND_PRESERVATION_REQUIRED')
    expected=g2.get('expected') or {}
    if expected.get('main')!=MAIN or expected.get('reviewedPr')!=PR:
        reasons.append('G2_PINNED_MAIN_AND_REVIEWED_HEAD_REQUIRED')
    g2main=(g2.get('evidence') or {}).get('main') or {}
    if (g2main.get('head')!=MAIN or g2main.get('reviewedPrHead')!=PR or
            g2main.get('tree')!=g2main.get('prTree')):
        reasons.append('G2_MERGED_MAIN_TREE_PARITY_REQUIRED')
    gates=g2.get('gates') or {}
    for k in REQUIRED_G2:
        if gates.get(k)!='PASS':reasons.append('G2_GATE_REQUIRED:'+k)
    legacy=(g2.get('evidence') or {}).get('officialReadOnlyEvaluation') or {}
    if legacy.get('authorized') is not False:
        reasons.append('LEGACY_V08_AUTHORITY_MUST_REMAIN_SEPARATE')
    if v7.get('state')!='PASS_DISPOSABLE_ONE_TEST_FIXTURE_COMPATIBILITY_ONLY_G2_OFFICIAL_HOLD':
        reasons.append('V7_DISPOSABLE_COMPATIBILITY_RECEIPT_REQUIRED')
    if v7.get('preservation')!='PASS' or v7.get('issues')!=[]:
        reasons.append('V7_EVIDENCE_AND_PRESERVATION_REQUIRED')
    if (v7.get('source') or {}).get('canonicalMain')!=MAIN:
        reasons.append('V7_CANONICAL_MAIN_PIN_REQUIRED')
    vg=v7.get('gates') or {}
    if (vg.get('FOUR_EXACT_FOCUSED_SUITES')!='PASS' or
        vg.get('HISTORICAL_861_FILE_ADOPTION')!='REJECTED' or
        vg.get('RESTORED_GENERAL_ACTION_BINDING')!='HOLD_REJECT_HISTORICAL_AUTHORITY_IMPORT'):
        reasons.append('V7_SCOPE_AND_GENERAL_AUTHORITY_BOUNDARY_REQUIRED')
    suites=v7.get('tests') or {}
    if set(suites)!=set(EXPECTED_V7):
        reasons.append('V7_EXACT_FOUR_SUITES_REQUIRED')
    else:
        for name,count in EXPECTED_V7.items():
            suite=suites[name]
            if (suite.get('state')!='PASS' or suite.get('returnCode')!=0 or
                suite.get('discovered')!=count or suite.get('executed')!=count):
                reasons.append('V7_SUITE_REAL_PASS_REQUIRED:'+name)
    if (manifest.get('authority')!='ENGINEERING_CANDIDATE_ONLY' or
        manifest.get('autoHumanDecision') is not False or
        manifest.get('autoVerifiedFinish') is not False or
        set(manifest.get('humanThresholdRequires') or [])!=set(REQUIRED_HUMAN) or
        manifest.get('scope')!='PINNED_BOUNDED_NATIVE_ONLY_NOT_OFFICIAL_ACCEPTANCE'):
        reasons.append('CANONICAL_PREHUMAN_AUTHORITY_BOUNDARY_REQUIRED')
    ready=not reasons
    return {
        'schema':'enguru.p06.main-machine-proof-bridge-candidate/v1',
        'state':'MACHINE_PROOF_BRIDGE_CANDIDATE_READY_OFFICIAL_HOLD' if ready else 'HOLD_MACHINE_PROOF_BRIDGE_INPUT',
        'machineProofCandidateReady':ready,
        'authorizedAcceptedCandidate':False,
        'officialP06DoneCheck':'HOLD',
        'humanThreshold':'HOLD',
        'verifiedFinish':'HOLD',
        'canonicalMain':MAIN,'reviewedPrHead':PR,
        'historical861PathMergeAdopted':False,
        'generalActionAuthorityImported':False,
        'reasons':reasons,
        'nextAction':'REVIEW_AND_AUTHORIZE_EXISTING_ISSUER_ADAPTER_CONTRACT' if ready else 'RECONCILE_PROOF_INPUTS',
    }
