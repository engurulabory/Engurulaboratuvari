"""ENGURU Suzgec v2.3 E01: executable ownership readiness guard.
Existing 8 stages and v2.2 guard retain canonical authority.
This module is a gate, not a new core or an automatic repair agent.
"""
from __future__ import annotations
import copy, hashlib, json
from typing import Callable

class ExecutionHold(Exception): pass

def pin(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(",", ":")).encode()).hexdigest()

def readiness(contract, state, abilities):
    """Only real, resolved abilities can authorize the finish label."""
    if not all(isinstance(x,dict) for x in (contract,state,abilities)):
        raise ExecutionHold("INVALID_INPUT")
    must=("goal","acceptanceCriteria","sourcePins","allowedMutations","executorIdentity","precheckBound","postcheckBound","testCommands","donecheckBinding","githubPlan","humanThreshold")
    missing=[k for k in must if not contract.get(k)]
    if missing:raise ExecutionHold("CONTRACT_INCOMPLETE:"+",".join(missing))
    if contract["humanThreshold"] != "HUMAN_ONLY":raise ExecutionHold("HUMAN_THRESHOLD_AUTHORITY")
    if not isinstance(contract["acceptanceCriteria"],list) or not contract["acceptanceCriteria"]:raise ExecutionHold("CRITERIA_EMPTY")
    if not isinstance(contract["sourcePins"],dict) or not contract["sourcePins"]:raise ExecutionHold("PINS_EMPTY")
    if abilities.get("authorizedExecutor") is not True:raise ExecutionHold("AUTHORIZED_EXECUTOR_UNVERIFIED")
    if abilities.get("realCallerBound") is not True:raise ExecutionHold("REAL_CALLER_BINDING_UNVERIFIED")
    if abilities.get("testEnvironmentReady") is not True:raise ExecutionHold("TEST_ENVIRONMENT_UNVERIFIED")
    if abilities.get("donecheckAvailable") is not True:raise ExecutionHold("DONECHECK_UNVERIFIED")
    if abilities.get("scopeAuthorized") is not True:raise ExecutionHold("SCOPE_UNAUTHORIZED")
    if abilities.get("sourcePinsMatch") is not True:raise ExecutionHold("SOURCE_DRIFT")
    if not abilities.get("simulationEvidence"):raise ExecutionHold("SIMULATION_MISSING")
    if not abilities.get("realCallerEvidence"):raise ExecutionHold("CALLER_EVIDENCE_MISSING")
    if state.get("project") != contract.get("project"):raise ExecutionHold("PROJECT_SCOPE_MISMATCH")
    # v2.3: evidence-backed *plan* is a hard prerequisite for EXECUTION_READY.
    # The forecast validates the intended full path, never asserts execution PASS.
    if contract.get("project") == "ENGURU_SUZGEC_V23":
        try:
            from tools.enguru_suzgec_v23_forecast import validate_forecast
        except ModuleNotFoundError:
            from enguru_suzgec_v23_forecast import validate_forecast
        try:
            validate_forecast(contract.get("finishPathForecast"), contract, state)
        except ValueError as exc:
            raise ExecutionHold("FORECAST_" + str(exc)) from exc
        # E01.GOAL_OUTCOME_ACCEPTANCE: scope-defined measurable outcomes.
        # Human scope approval and field provenance remain external authorities.
        try:
            from tools.enguru_suzgec_v23_goal_acceptance import validate_boundary
        except ModuleNotFoundError:
            from enguru_suzgec_v23_goal_acceptance import validate_boundary
        try:
            validate_boundary(contract.get("goalOutcomeAcceptance"), contract, state)
        except ValueError as exc:
            raise ExecutionHold("ACCEPTANCE_" + str(exc)) from exc
    return {"state":"EXECUTION_READY","contractSha256":pin(contract),"canonicalSha256":pin(state),"evidence":"USER_SUPPLIED_MUST_BE_VERIFIED_BY_AUTHORIZED_FIELD_EXECUTOR"}

def execute_owned(contract, canonical_state, abilities, package, execute:Callable, guard):
    """Fails closed. Callback must be existing authorized executor, not an arbitrary new authority."""
    r=readiness(contract,canonical_state,abilities)
    snapshot=copy.deepcopy(canonical_state); original=pin(snapshot)
    before=guard.precheck(copy.deepcopy(package),copy.deepcopy(snapshot))
    if not isinstance(before,dict) or before.get("decision")!="EXECUTE":raise ExecutionHold("PRECHECK_HOLD")
    if pin(canonical_state)!=original:raise ExecutionHold("STATE_DRIFT_BEFORE_EXECUTION")
    result=execute(copy.deepcopy(package),copy.deepcopy(snapshot))
    if pin(canonical_state)!=original:raise ExecutionHold("STATE_DRIFT_AFTER_EXECUTION")
    if not isinstance(result,dict):raise ExecutionHold("RESULT_NOT_EVIDENCE")
    after=guard.postcheck(copy.deepcopy(result),canonical_state=copy.deepcopy(snapshot))
    if not isinstance(after,dict) or after.get("decision")!="ADVANCE":raise ExecutionHold("POSTCHECK_HOLD")
    if contract.get("project") == "ENGURU_SUZGEC_V23":
        # Do not manufacture a trusted producer, DoneCheck or PASS from user data.
        try:
            from tools.enguru_suzgec_v23_goal_acceptance import assess_outcome
        except ModuleNotFoundError:
            from enguru_suzgec_v23_goal_acceptance import assess_outcome
        observation = result.get("goalOutcomeObservation")
        if not observation:
            raise ExecutionHold("GOAL_OUTCOME_OBSERVATION_MISSING")
        verifier = getattr(guard,"verify_goal_outcome_evidence",None)
        scope_verifier = getattr(guard,"verify_goal_scope_approval",None)
        try:
            outcome = assess_outcome(contract["goalOutcomeAcceptance"], contract,
                                     snapshot, observation, verifier, scope_verifier)
        except ValueError as exc:
            raise ExecutionHold("ACCEPTANCE_OBSERVATION_" + str(exc)) from exc
        if outcome.get("state") != "PASS_PACKAGE_OUTCOME_MEASURED":
            raise ExecutionHold(outcome.get("reason") or "ACCEPTANCE_OUTCOME_HOLD")
    return {"state":"TECHNICAL_EXECUTION_OBSERVED","contractSha256":r["contractSha256"],"canonicalSha256":r["canonicalSha256"],"precheck":before,"postcheck":after,"technicalFinish":"REQUIRES_INDEPENDENT_DONECHECK_AND_FIELD_EVIDENCE","humanThreshold":"PENDING","verifiedFinish":"HOLD"}
