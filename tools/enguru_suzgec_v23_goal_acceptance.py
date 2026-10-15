"""ENGURU Suzgec v2.3 — Goal and Runtime Outcome Acceptance (T02/T03).

Adds a fail-closed acceptance boundary to existing E01; no new core,
producer authority, Human Threshold or automatic Verified Finish.
"""
from __future__ import annotations
import hashlib
import json
import re

SCHEMA = 'enguru.suzgec.v23.goal-outcome-acceptance/v1'
EVIDENCE_SCHEMA = 'enguru.suzgec.v23.goal-outcome-observation/v1'
CRITERIA = (
    'K01_GOAL_ACHIEVED', 'K02_SCOPE_COMPLETED',
    'K03_RUNTIME_OPERABLE', 'K04_BEHAVIOR_VERIFIED',
    'K05_EXISTING_VALUE_PRESERVED', 'K06_EVIDENCE_VERIFIED',
    'K07_TECHNICAL_GATES_PASS',
)
_SHA = re.compile(r'^[0-9a-f]{64}$')

class AcceptanceHold(ValueError):
    pass

def pin(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
             allow_nan=False,separators=(',', ':')).encode('utf-8')).hexdigest()

def _check(predicate, reason):
    if not predicate:
        raise AcceptanceHold(reason)

def validate_boundary(boundary, contract, state):
    """Structural check of criteria + measurable target (NOT human/field approval)."""
    _check(isinstance(boundary,dict) and isinstance(contract,dict)
           and isinstance(state,dict), 'BOUNDARY_TYPE')
    _check(boundary.get('schema')==SCHEMA, 'SCHEMA')
    _check(boundary.get('project')==contract.get('project')==state.get('project'), 'PROJECT_DRIFT')
    _check(bool(contract.get('goal')) and boundary.get('goal')==contract['goal'],'GOAL_DRIFT')
    _check(boundary.get('sourcePins')==contract.get('sourcePins'), 'SOURCE_DRIFT')
    _check(boundary.get('humanScopeAuthority')=='HUMAN_ONLY', 'SCOPE_HUMAN_AUTHORITY')
    _check(boundary.get('verifiedFinishAuthority')=='HUMAN_ONLY', 'FINISH_HUMAN_AUTHORITY')
    _check(boundary.get('decision') in ('SCOPE_REVIEW_PENDING','SCOPE_REVIEWED_NEEDS_AUTHENTICATED_PROOF'), 'SCOPE_DECISION_BOUNDARY')
    criteria=boundary.get('criteria')
    _check(isinstance(criteria,list) and len(criteria)==len(CRITERIA),'CRITERIA_COUNT')
    _check([x.get('id') if isinstance(x,dict) else None for x in criteria]==list(CRITERIA),'CRITERIA_ORDER')
    for item in criteria:
        code=item['id']
        _check(item.get('required') is True,'CRITERION_OPTIONAL:'+code)
        _check(isinstance(item.get('description'),str) and len(item['description'].strip())>=12,'CRITERION_MEANING:'+code)
        _check(isinstance(item.get('measurement'),dict),'MEASUREMENT_REQUIRED:'+code)
        measure=item['measurement']
        _check(measure.get('type') in ('BOOLEAN','MINIMUM','EXACT'),'MEASUREMENT_TYPE:'+code)
        expected=measure.get('target')
        kind=measure['type']
        _check((type(expected) is bool if kind=='BOOLEAN' else
                (type(expected) in (int,float) and not isinstance(expected,bool) if kind=='MINIMUM' else
                 isinstance(expected,str) and bool(expected.strip()))), 'MEASUREMENT_TARGET:'+code)
        _check(isinstance(item.get('environment'),str) and item['environment'].strip(),'TARGET_ENVIRONMENT:'+code)
        _check(isinstance(item.get('evidenceSource'),str) and item['evidenceSource'].strip(),'EVIDENCE_PRODUCER:'+code)
        _check(isinstance(item.get('holdReason'),str) and item['holdReason'].startswith('HOLD_'),'HOLD_RULE:'+code)
    # Same exact criteria govern the real, pinned E01 contract and its acceptance boundary.
    _check(contract.get('acceptanceCriteria')==criteria, 'CRITERIA_MISMATCH')
    return {'state':'PASS_ACCEPTANCE_BOUNDARY_STRUCTURE_ONLY','boundarySha256':pin(boundary),
            'humanScopeApproved':False,'fieldVerified':False,'verifiedFinish':'HOLD'}

def assess_outcome(boundary, contract, state, observation, verified_evidence=None, verify_scope=None):
    """Measure each K01–K07. Only existing source-bound producer can verify evidence.

    `verified_evidence` is a callback provided ONLY from a pinned, authorized
    actual field adapter. An arbitrary user field or boolean is not trusted.
    Returned PASS is strictly a package outcome evaluation, not DoneCheck or HT.
    """
    gate=validate_boundary(boundary,contract,state)
    if boundary['decision'] != 'SCOPE_REVIEWED_NEEDS_AUTHENTICATED_PROOF' or not callable(verify_scope) or verify_scope(boundary, contract, state) is not True:
        return {'state':'HOLD','reason':'HOLD_HUMAN_SCOPE_APPROVAL_UNVERIFIED',
                'boundarySha256':gate['boundarySha256'],'verifiedFinish':'HOLD'}
    if not callable(verified_evidence):
        return {'state':'HOLD','reason':'HOLD_TRUSTED_EVIDENCE_VERIFIER_UNBOUND',
                'boundarySha256':gate['boundarySha256'],'verifiedFinish':'HOLD'}
    _check(isinstance(observation,dict),'OBSERVATION_MISSING')
    _check(observation.get('schema')==EVIDENCE_SCHEMA,'OBSERVATION_SCHEMA')
    _check(observation.get('project')==contract['project'],'OBSERVATION_PROJECT')
    _check(observation.get('goal')==contract['goal'],'OBSERVATION_GOAL')
    _check(observation.get('canonicalSha256')==pin(state),'CANONICAL_STATE_DRIFT')
    _check(observation.get('boundarySha256')==gate['boundarySha256'],'BOUNDARY_DRIFT')
    _check(observation.get('sourcePins')==contract['sourcePins'],'OBSERVATION_SOURCE_DRIFT')
    observations=observation.get('criteria')
    _check(isinstance(observations,list) and len(observations)==len(CRITERIA),'OBSERVATION_COUNT')
    _check([x.get('id') if isinstance(x,dict) else None for x in observations]==list(CRITERIA),'OBSERVATION_ORDER')
    results=[]
    for criterion,actual in zip(boundary['criteria'],observations):
        code=criterion['id']
        metric=criterion['measurement']
        _check(actual.get('environment')==criterion['environment'],'ENVIRONMENT_MISMATCH:'+code)
        ref=actual.get('evidenceRef')
        digest=actual.get('evidenceSha256')
        _check(isinstance(ref,str) and ref.strip(),'MISSING_ACTUAL_EVIDENCE:'+code)
        _check(isinstance(digest,str) and bool(_SHA.fullmatch(digest)),'MISSING_EVIDENCE_SHA256:'+code)
        value=actual.get('observedValue')
        expected=metric['target']
        if metric['type']=='BOOLEAN':
            met=type(value) is bool and value is expected
        elif metric['type']=='MINIMUM':
            met=type(value) in (int,float) and value>=expected
        else:
            met=isinstance(value,str) and value==expected
        if not met:
            return {'state':'HOLD','reason':criterion['holdReason'],
                    'criterion':code,'verifiedFinish':'HOLD'}
        # Field-owned verifier must validate origin, SHA, current source and scope.
        if verified_evidence(criterion,actual,state) is not True:
            return {'state':'HOLD','reason':'HOLD_EVIDENCE_PROVENANCE:'+code,
                    'criterion':code,'verifiedFinish':'HOLD'}
        results.append({'criterion':code,'measurement':'PASS','evidenceSha256':digest})
    return {'state':'PASS_PACKAGE_OUTCOME_MEASURED', 'criteriaPassed':len(results),
            'criteria':results,'boundarySha256':gate['boundarySha256'],
            'technicalFinish':'REQUIRES_INDEPENDENT_DONECHECK_AND_T03',
            'humanThreshold':'PENDING','verifiedFinish':'HOLD'}
