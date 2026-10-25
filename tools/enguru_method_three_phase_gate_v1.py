#!/usr/bin/env python3
"""ENGURU project method: design -> theory -> GitHub, 3+2 evidence-gated rounds.

Policy verifier only: this module NEVER issues canonical acceptance, Mac authority,
GitHub CI success, or product 100s on its own. Callers must supply a *real*
project-specific verifier; self-reported scores and PASS flags are ignored.
"""
from __future__ import annotations
import re

PHASES = ("DESIGN", "THEORY", "GITHUB")
FINAL_FAMILIES = ("SIM1", "SIM2", "SIM3")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
MIN_ROUNDS = 3
MAX_ROUNDS = 5


def _hold(reason, phase="", history=()):
    return {
        "policyVerdict": "HOLD",
        "reason": reason, "activePhase": phase,
        "history": list(history),
        "GITHUB_PREPARED": "HOLD",
        "OSI_FIELD_READY": "HOLD",
        "HUMAN_AUTHORIZED": "HOLD",
        "VERIFIED_FINISH": "HOLD",
    }


def _expected_ids(plan, phase):
    values = plan.get("controls", {}).get(phase)
    if not isinstance(values, list) or not values or any(
        not isinstance(x, str) or not x.strip() for x in values
    ) or len(set(values)) != len(values):
        raise ValueError("HOLD_FIXED_ACCEPTANCE_IDS")
    return values


def _verified(plan, phase, challenge, verify):
    """Only a caller-supplied real evaluator can determine the passed IDs."""
    result = verify(phase, challenge)
    if not isinstance(result, dict):
        raise ValueError("HOLD_VERIFIER_UNAVAILABLE")
    expected = _expected_ids(plan, phase)
    passed = result.get("passedIds")
    source = result.get("sourceSha256")
    evidence = result.get("evidenceSha256")
    oracle = result.get("oracleId")
    if (not isinstance(passed, list) or len(set(passed)) != len(passed)
            or any(not isinstance(x, str) for x in passed)
            or not set(passed).issubset(expected)
            or not isinstance(source, str) or not HEX64.fullmatch(source)
            or not isinstance(evidence, str) or not HEX64.fullmatch(evidence)
            or not isinstance(oracle, str) or not oracle.strip()):
        raise ValueError("HOLD_BAD_VERIFIER_PROOF")
    return {
        "phase": phase, "score": round(100*len(passed)/len(expected), 6),
        "passedIds": sorted(passed), "missingIds": sorted(set(expected)-set(passed)),
        "sourceSha256": source, "evidenceSha256": evidence, "oracleId": oracle,
        "fixedDenominator": len(expected),
    }


def review(plan, verify):
    """Check sequencing; run 3-5 meaningful rounds per phase and 3 final families.

    This is a method policy check, not a second score issuer. Verified source
    bytes/tests and exact CI are owned by each project's existing evaluators.
    """
    if not isinstance(plan, dict) or not callable(verify):
        return _hold("HOLD_INVALID_PLAN_OR_VERIFIER")
    history = []
    try:
        if set(plan.get("rounds", {})) != set(PHASES):
            return _hold("HOLD_PHASE_ORDER_OR_COVERAGE")
        if set(plan.get("finalFamilies", {})) != set(FINAL_FAMILIES):
            return _hold("HOLD_FINAL_SIMULATION_COVERAGE")
        for phase in PHASES:
            _expected_ids(plan, phase)
            rounds = plan["rounds"][phase]
            if not isinstance(rounds, list) or not MIN_ROUNDS <= len(rounds) <= MAX_ROUNDS:
                return _hold("HOLD_ROUND_COUNT_3_TO_5", phase, history)
            prior = None
            first_oracle = None
            for index, challenge in enumerate(rounds):
                if not isinstance(challenge, dict) or not isinstance(challenge.get("caseId"), str):
                    return _hold("HOLD_ROUND_ID", phase, history)
                item = _verified(plan, phase, challenge, verify)
                item["round"] = index + 1
                item["caseId"] = challenge["caseId"]
                if index == 0:
                    first_oracle = item["oracleId"]
                if index == 2 and item["oracleId"] == first_oracle:
                    return _hold("HOLD_THIRD_ROUND_ORACLE_NOT_DISTINCT", phase, history)
                if prior is not None and (item["sourceSha256"], item["evidenceSha256"]) == (
                    prior["sourceSha256"], prior["evidenceSha256"]
                ):
                    return _hold("HOLD_REPEAT_WITHOUT_NEW_EVIDENCE", phase, history)
                if index >= 3 and prior is not None and not (
                    set(item["passedIds"]) - set(prior["passedIds"])
                ):
                    return _hold("HOLD_EXTRA_ROUND_WITHOUT_CLOSED_GAP", phase, history)
                history.append(item)
                prior = item
            if history[-1]["score"] != 100:
                return _hold("HOLD_PHASE_HAS_OPEN_CONTROLS", phase, history)
        # SIM1/2/3 are three independent final test families, not the
        # design/theory/GitHub repair rounds, and must share exact source.
        final = []
        expected_source = history[-1]["sourceSha256"]
        for family in FINAL_FAMILIES:
            _expected_ids(plan, family)
            case = plan["finalFamilies"][family]
            result = _verified(plan, family, case, verify)
            final.append(result)
        history.extend(final)
        if len({x["oracleId"] for x in final}) != 3:
            return _hold("HOLD_FINAL_ORACLES_NOT_DISTINCT", "GITHUB", history)
        if any(x["sourceSha256"] != expected_source for x in final):
            return _hold("HOLD_FINAL_SOURCE_DRIFT", "GITHUB", history)
        if any(x["score"] != 100 for x in final):
            return _hold("HOLD_FINAL_SIMULATION_GAPS", "GITHUB", history)
        return {
            "policyVerdict": "PASS_THREE_PHASE_POLICY_REQUIRES_EXTERNAL_CI",
            "phaseOrder": list(PHASES),
            "repairRounds": {phase: len(plan["rounds"][phase]) for phase in PHASES},
            "finalSimulationScores": {x["phase"]: x["score"] for x in final},
            "history": history,
            "GITHUB_PREPARED": "HOLD_PENDING_EXACT_SOURCE_AND_CI",
            "OSI_FIELD_READY": "HOLD",
            "HUMAN_AUTHORIZED": "HOLD",
            "VERIFIED_FINISH": "HOLD",
            "nextAction": "VERIFY_REAL_PROJECT_SOURCE_TESTS_EXACT_CI_THEN_READY_FOR_OSI_HANDOFF_DUR",
        }
    except (ValueError, KeyError, TypeError, RecursionError) as exc:
        return _hold("HOLD_VERIFIER_OR_PLAN:" + str(exc), phase if "phase" in locals() else "", history)
