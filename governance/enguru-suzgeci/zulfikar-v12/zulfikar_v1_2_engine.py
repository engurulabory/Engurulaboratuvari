#!/usr/bin/env python3
"""ENGURU Zulfikar V1.2 — offline DESIGN ORACLE ONLY.

Checks supplied observations as fixture data.  This is not a GitHub, Mac OSi,
DoneCheck, or Human Threshold verifier. No network, secrets, or repository writes.
"""
from __future__ import annotations
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re

SHA = re.compile(r"^[0-9a-f]{64}$")
STATES = {'SUCCESS', 'FAILURE', 'PARTIAL', 'INTERRUPTED', 'FALSE_PASS', 'RECOVERED'}
CHAIN = ('INTENT', 'GOAL', 'CONTRACT', 'PLAN', 'SOURCE', 'EXECUTION', 'TEST', 'USER_OUTCOME', 'AUTHORITY')
FROZEN_SCORE_93 = (10, 9, 9, 9, 9, 10, 10, 9, 10, 8)
CLOSURES = {
 'Z02_EVENT': ('Z02',1), 'Z03_TRANSFER':('Z03',1), 'Z04_LINEAGE':('Z04',1),
 'Z05_BENCHMARK':('Z05',1), 'Z08_IMPACT':('Z08',1),
 'Z10_CONCURRENCY':('Z10',1), 'Z10_SAFE_FIN':('Z10',1),
}


def canonical_digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()


def valid_sha(x):
    return isinstance(x,str) and SHA.fullmatch(x) is not None


def decimal_nonnegative(x):
    if isinstance(x, bool) or not isinstance(x,(int,float,str,Decimal)):
        return None
    try:
        d=Decimal(str(x))
        return d if d.is_finite() and d>=0 else None
    except (ValueError,InvalidOperation):
        return None


def check_event(x):
    """K01: observed event truth and cause confidence, not score manufacturing."""
    e=[]
    for key in ('event_id','task_id','owner','source_uri','provenance_digest','observed_at'):
        if not isinstance(x.get(key),str) or not x[key].strip():e.append('MISSING_'+key.upper())
    if not valid_sha(x.get('provenance_digest')):e.append('INVALID_EVENT_PROVENANCE')
    if x.get('outcome') not in STATES:e.append('INVALID_EVENT_OUTCOME')
    if x.get('cause_status') not in ('HYPOTHESIS','EVIDENCE_CONFIRMED','UNKNOWN'):e.append('INVALID_CAUSE_STATE')
    if x.get('cause_status')=='EVIDENCE_CONFIRMED' and not x.get('cause_evidence_uri'):
        e.append('CAUSE_CONFIRMED_WITHOUT_EVIDENCE')
    if x.get('outcome')=='FALSE_PASS' and x.get('promote_as_success'):
        e.append('FALSE_PASS_MISCLASSIFIED')
    return sorted(set(e))


def check_transfer(x):
    """K01: fixed cohort of 3 downstream real-task candidates with paired results."""
    e=[]
    cohort=x.get('cohort')
    if not isinstance(cohort,list) or len(cohort)!=3:
        return ['TRANSFER_REQUIRES_THREE_COMPARABLE_TASKS']
    taskids=[]
    for i,t in enumerate(cohort):
        prefix=f'TRANSFER_{i+1}_'
        if not isinstance(t,dict):e.append(prefix+'INVALID');continue
        taskids.append(t.get('task_id'))
        if t.get('family')!=x.get('family') or not x.get('family'):e.append(prefix+'FAMILY_MISMATCH')
        if not t.get('baseline_evidence') or not t.get('candidate_evidence'):
            e.append(prefix+'MISSING_REAL_PAIR_EVIDENCE')
        if t.get('independent_reviewed') is not True or t.get('reviewer_id')==t.get('author_id'):
            e.append(prefix+'INDEPENDENT_REVIEW_REQUIRED')
        b=decimal_nonnegative(t.get('baseline_effort'))
        a=decimal_nonnegative(t.get('candidate_effort'))
        if b is None or a is None or b<=0 or a>=b:
            e.append(prefix+'NO_VERIFIED_EFFORT_GAIN')
        if t.get('regression') is not False:e.append(prefix+'REGRESSION_UNCLEARED')
        if t.get('real_task_observed') is not True:e.append(prefix+'REAL_TASK_NOT_OBSERVED')
    if not all(isinstance(i,str) and i for i in taskids) or len(set(repr(i) for i in taskids))!=3:
        e.append('TRANSFER_TASK_IDENTITIES_NOT_DISTINCT')
    if x.get('cohort_frozen_before_results') is not True:
        e.append('TRANSFER_SURVIVORSHIP_SELECTION_RISK')
    return sorted(set(e))


def check_lineage(x):
    """K02: trace coherent scope and source across each provided stage."""
    e=[]
    chain=x.get('chain')
    if not isinstance(chain,list) or tuple(y.get('stage') for y in chain if isinstance(y,dict))!=CHAIN or len(chain)!=len(CHAIN):
        return ['CHAIN_ORDER_OR_LENGTH_INVALID']
    project=x.get('project_id'); target=x.get('target_sha'); controls=x.get('contract_controls')
    if not valid_sha(target):e.append('LINEAGE_INVALID_SOURCE_PIN')
    if not isinstance(controls,list) or not controls or not all(isinstance(c,str) for c in controls) or len(controls)!=len(set(repr(c) for c in controls)):
        e.append('LINEAGE_INVALID_CONTRACT_CONTROLS')
    for i,node in enumerate(chain):
        prefix=f'CHAIN_{CHAIN[i]}_'
        if not isinstance(node,dict):e.append(prefix+'INVALID_NODE');continue
        if node.get('project_id')!=project or not project:e.append(prefix+'PROJECT_DRIFT')
        if node.get('source_sha')!=target:e.append(prefix+'SOURCE_DRIFT')
        if node.get('control_id') not in (controls or []):e.append(prefix+'CONTROL_DRIFT')
        if not node.get('evidence_ref'):e.append(prefix+'EVIDENCE_MISSING')
    if x.get('claim_scope') != x.get('contract_scope'):
        e.append('CHAIN_CLAIM_SCOPE_DRIFT')
    return sorted(set(e))


def check_benchmark(x):
    """K03: comparability gate, never assertion of product superiority."""
    e=[]
    for key in ('task_manifest_sha','input_manifest_sha','rubric_sha'):
        if not valid_sha(x.get(key)):e.append('BENCHMARK_MISSING_'+key.upper())
    if x.get('peer_id')==x.get('candidate_id') or not x.get('peer_id') or not x.get('candidate_id'):
        e.append('BENCHMARK_INVALID_PAIR')
    for key in ('same_task','same_inputs','equalized_budget','metric_equivalence','environment_disclosed',
                'versions_pinned','capability_parity_or_limitations_reported','blinded_grader','all_trials_accounted'):
        if x.get(key) is not True:e.append('BENCHMARK_'+key.upper()+'_REQUIRED')
    trials=x.get('trials')
    if not isinstance(trials,list) or len(trials)<5:
        e.append('BENCHMARK_REQUIRES_FIVE_PAIRED_TRIALS')
    else:
        ids=[]
        for i,t in enumerate(trials):
            if not isinstance(t,dict):e.append(f'BENCHMARK_TRIAL_{i}_INVALID');continue
            ids.append(t.get('trial_id'))
            if not (t.get('candidate_proof') and t.get('peer_proof')):
                e.append(f'BENCHMARK_TRIAL_{i}_PAIR_PROOF_MISSING')
            if decimal_nonnegative(t.get('candidate_measure')) is None or decimal_nonnegative(t.get('peer_measure')) is None:
                e.append(f'BENCHMARK_TRIAL_{i}_MEASUREMENT_MISSING')
        if len(set(repr(i) for i in ids))!=len(ids) or any(not isinstance(i,str) or not i for i in ids):
            e.append('BENCHMARK_TRIAL_DUPLICATION')
    if x.get('real_peer_execution') is not True:
        e.append('BENCHMARK_REAL_PEER_RUNS_REQUIRED')
    return sorted(set(e))


def check_impact(x):
    """K04: paired real-user value; no estimated uplift is accepted as real."""
    e=[]
    for key in ('user_goal','metric','unit','baseline_evidence','after_evidence','observed_at_baseline',
                'observed_at_after','privacy_review'):
        if not x.get(key):e.append('IMPACT_MISSING_'+key.upper())
    if x.get('real_users_observed') is not True:e.append('IMPACT_REAL_USER_NOT_OBSERVED')
    if x.get('matched_cohort') is not True:e.append('IMPACT_UNMATCHED_COHORT')
    b=decimal_nonnegative(x.get('baseline'))
    a=decimal_nonnegative(x.get('after'))
    if b is None or a is None:e.append('IMPACT_INVALID_VALUES')
    elif x.get('direction')=='lower_is_better':
        if a>=b:e.append('IMPACT_NO_MEASURED_IMPROVEMENT')
    elif x.get('direction')=='higher_is_better':
        if a<=b:e.append('IMPACT_NO_MEASURED_IMPROVEMENT')
    else:e.append('IMPACT_DIRECTION_UNDEFINED')
    return sorted(set(e))


def check_concurrency(x):
    """K02/K04: Work/GitHub/OSi lease + handoff plan integrity."""
    e=[]
    if x.get('active_writer_count')!=1:e.append('CONCURRENCY_ONE_WRITER_REQUIRED')
    if x.get('writer_id') != x.get('authorized_writer_id') or not x.get('writer_id'):
        e.append('CONCURRENCY_WRITER_AUTHORIZATION_REQUIRED')
    if not valid_sha(x.get('snapshot_sha')) or x.get('snapshot_sha')!=x.get('expected_snapshot_sha'):
        e.append('CONCURRENCY_SOURCE_DRIFT')
    if x.get('lease_current') is not True:e.append('CONCURRENCY_LEASE_MISSING')
    if x.get('idempotency_verified') is not True:e.append('CONCURRENCY_REPLAY_UNVERIFIED')
    if x.get('rollback_checkpoint') is None:e.append('CONCURRENCY_ROLLBACK_UNSPECIFIED')
    if x.get('work_session_mutation_allowed') is True:e.append('CONCURRENCY_ACTIVE_WORK_COLLISION')
    return sorted(set(e))


def check_fin(x):
    """K04: advisory readiness only. Never issue DoneCheck or Verified Finish."""
    e=[]
    gates=x.get('k_gates')
    if not isinstance(gates,dict):gates={}
    for i in range(1,8):
        if gates.get(f'K{i}') is not True:e.append(f'FIN_K{i}_REMAINS_OPEN')
    if x.get('unique_controls') is not True:e.append('FIN_DUPLICATE_CONTROL_RISK')
    if x.get('evidence_verified') is not True:e.append('FIN_EVIDENCE_UNVERIFIED')
    if x.get('independent_review') is not True:e.append('FIN_SECOND_LOOK_REQUIRED')
    if x.get('field_required') and x.get('field_evidence') is not True:e.append('FIN_FIELD_REQUIRED')
    if x.get('human_threshold_required') and x.get('human_authorization') is not True:
        e.append('FIN_HUMAN_DECISION_REQUIRED')
    if x.get('benchmark_claimed') and x.get('benchmark_real_evidence') is not True:
        e.append('FIN_BENCHMARK_CLAIM_UNSUPPORTED')
    if x.get('verified_finish_claim') is True:e.append('FIN_UNAUTHORIZED_FINISH_CLAIM')
    return sorted(set(e))

CHECKS={
 'Z02_EVENT':check_event, 'Z03_TRANSFER':check_transfer, 'Z04_LINEAGE':check_lineage,
 'Z05_BENCHMARK':check_benchmark, 'Z08_IMPACT':check_impact,
 'Z10_CONCURRENCY':check_concurrency, 'Z10_SAFE_FIN':check_fin,
}


def assess(case):
    """Fail-closed and stable advisory output for synthetic or declared inputs."""
    if not isinstance(case,dict):
        return {'state':'SIMULATED_HOLD','official_verdict':'NOT_EVALUATED',
                'eligible_for_automatic_signature':False,
                'holds':{'SCHEMA':['INVALID_CASE']}, 'next_action':'REPAIR_CASE_SCHEMA'}
    holds={}
    for key,fn in CHECKS.items():
        component=case.get(key,{})
        holds[key]=fn(component) if isinstance(component,dict) else ['INVALID_COMPONENT_SCHEMA']
    passed=all(not v for v in holds.values())
    first=next((k for k,v in holds.items() if v),None)
    return {'state': 'SIMULATED_DESIGN_READY_TO_REQUEST_REVIEW' if passed else 'SIMULATED_HOLD',
            'official_verdict':'NOT_EVALUATED', 'eligible_for_automatic_signature':False,
            'holds':{k:v for k,v in holds.items() if v},
            'next_action':'REQUEST_EXISTING_INDEPENDENT_REVIEW' if passed else f'REPAIR_{first}'}


def evaluate_design_coverage(contract, test_success):
    """Frozen 93+7 score, design coverage ONLY, with separately verified assertions."""
    if not isinstance(contract,dict):
        return {'baseline':93,'provisional':93,'design_coverage':'HOLD','open_closures':sorted(CHECKS)}
    expected=set(CHECKS)
    declared=set(contract.get('closure_ids',[]))
    mapped=set(contract.get('proof_mapping',{}))
    if declared!=expected or mapped!=expected or not test_success:
        return {'baseline':93,'provisional':93,'design_coverage':'HOLD','open_closures':sorted(expected-declared | expected-mapped)}
    for cid in expected:
        claim=contract['proof_mapping'][cid]
        if not (isinstance(claim,dict) and claim.get('positive_case') and claim.get('negative_case') and claim.get('fixed_scope') and claim.get('oracle')):
            return {'baseline':93,'provisional':93,'design_coverage':'HOLD','open_closures':[cid]}
    assert sum(FROZEN_SCORE_93)==93 and len(CLOSURES)==7
    return {'baseline':93,'provisional':100,'design_coverage':'DESIGN_CANDIDATE_100_OF_100',
            'real_benchmark':'HOLD_NOT_MEASURED','real_user_impact':'HOLD_NOT_OBSERVED',
            'github_exact_head_ci':'HOLD_NOT_RUN','mac_field':'HOLD_NOT_RUN',
            'official_verified_finish':'HOLD_NOT_AUTHORIZED'}