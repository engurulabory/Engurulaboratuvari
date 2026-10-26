"""ENGURU Suzgec v2.3 E01.FORESIGHT: full finish path prior to execution.
This module is a validation helper for existing eight-stage / E01 Work Protocol.
It never grants dispatch authority, simulates a PASS, or produces Human Threshold.
"""
from __future__ import annotations
import hashlib
import json

SCHEMA = "enguru.suzgec.v23.finish-path-forecast/v1"
STAGES = ("T01", "T02", "T03", "T04")
MANDATORY_SCENARIOS = (
    "AUTHORIZED_NORMAL", "UNREGISTERED_ACTION", "SOURCE_DRIFT",
    "PRECHECK_HOLD", "POSTCHECK_HOLD", "REPEATED_HOLD",
    "DONECHECK_INCONCLUSIVE", "HUMAN_DECISION_PENDING",
)

def sha256_json(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()

def _require(test, code):
    if not test:
        raise ValueError(code)

def validate_forecast(forecast, contract, state):
    """Validate *plan* and its fixed gate structure, never confuse plan with real evidence."""
    _require(isinstance(forecast, dict), "MISSING_FORECAST")
    _require(isinstance(contract, dict) and isinstance(state, dict), "BAD_INPUT")
    _require(forecast.get("schema") == SCHEMA, "SCHEMA")
    _require(forecast.get("project") == contract.get("project") == state.get("project"), "PROJECT")
    _require(bool(contract.get("goal")) and forecast.get("goal") == contract.get("goal"), "GOAL_DRIFT")
    _require(forecast.get("sourcePins") == contract.get("sourcePins"), "SOURCE_PINS")
    _require(forecast.get("canonicalStateSha256") == sha256_json(state), "STATE_PIN")
    _require(forecast.get("humanThreshold") == "HUMAN_ONLY", "HUMAN_BOUNDARY")
    _require(forecast.get("version") == "2.3", "VERSION")
    steps = forecast.get("steps")
    _require(isinstance(steps, list) and len(steps) == 4, "GATE_COUNT")
    _require([s.get("id") if isinstance(s, dict) else None for s in steps] == list(STAGES), "GATE_ORDER")
    for i, step in enumerate(steps):
        for k in ("owner", "holdConditions", "passEvidence", "authorizedRecovery", "status"):
            _require(k in step and step[k] not in (None, "", []), "STEP_" + step["id"] + "_" + k)
        _require("dependencies" in step, "STEP_" + step["id"] + "_dependencies")
        _require(isinstance(step["dependencies"], list), "DEPENDENCY_TYPE")
        _require(all(d in STAGES[:i] for d in step["dependencies"]), "DEPENDENCY_NOT_PRIOR")
        _require(isinstance(step["holdConditions"], list) and all(isinstance(x, str) and x for x in step["holdConditions"]), "HOLD_CONDITIONS")
        _require(isinstance(step["passEvidence"], list) and all(isinstance(x, str) and x for x in step["passEvidence"]), "PASS_EVIDENCE")
        _require(step["status"] in ("HOLD", "PENDING", "PENDING_HUMAN", "PASS"), "STATUS")
        if step["status"] == "PASS":
            _require(bool(step.get("verifiedProofRefs")) and bool(step.get("proofVerified")), "UNVERIFIED_STEP_PASS")
        if step["id"] == "T04":
            _require(step["owner"] == "HUMAN_ONLY", "HUMAN_OWNER")
            _require(step["status"] in ("PENDING_HUMAN", "HOLD"), "AUTO_HUMAN_ACCEPTANCE")
    simulations = forecast.get("simulations")
    _require(isinstance(simulations, list), "SIMULATION_LIST")
    keys = [v.get("scenario") for v in simulations if isinstance(v, dict)]
    _require(len(keys) == len(simulations) and set(keys) == set(MANDATORY_SCENARIOS) and len(keys)==len(set(keys)), "SCENARIO_COVERAGE")
    for row in simulations:
        _require(row.get("expectedState") in ("HOLD", "PENDING", "EXECUTION_READY"), "SIMULATION_EXPECTATION")
        if row["scenario"] != "AUTHORIZED_NORMAL":
            _require(row["expectedState"] in ("HOLD", "PENDING"), "UNSAFE_EXPECTED_PASS")
    _require(forecast.get("predictionVsObservation") == "REQUIRED_POST_EXECUTION", "RECONCILIATION")
    return {"state": "PASS_FORECAST_STRUCTURE_ONLY", "schema": SCHEMA,
            "forecastSha256": sha256_json(forecast), "verifiedFinish": "HOLD",
            "runtimeVerified": False, "humanThreshold": "PENDING"}

def simulate_missing_authority(forecast, contract, state):
    """Execute actual validation against bad inputs (not a simulated real world PASS)."""
    trials=[]
    for label, changes in (("PROJECT_DRIFT", {"project": "WRONG"}),
                           ("GOAL_DRIFT", {"goal": "WRONG"}),
                           ("STATE_PIN_DRIFT", {"canonicalStateSha256": "0"*64}),
                           ("HUMAN_BYPASS", {"humanThreshold": "ACCEPTED"})):
        altered=dict(forecast, **changes)
        try:
            validate_forecast(altered,contract,state)
            trials.append({"scenario":label,"state":"FAIL_UNSAFE_ACCEPTED"})
        except ValueError as exc:
            trials.append({"scenario":label,"state":"PASS_FAIL_CLOSED","reason":str(exc)})
    return {"state": "PASS" if all(x["state"]=="PASS_FAIL_CLOSED" for x in trials) else "HOLD",
            "scenarios":trials}
