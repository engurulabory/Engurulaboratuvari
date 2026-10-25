#!/usr/bin/env python3
"""ENGURU single-goal chain: DESIGN > THEORY > GITHUB > OSI_HANDOFF > STOP.

Policy/sequence checker, NOT an autonomous code repairer, GitHub remote attestor,
Mac terminal bridge, signer or official issuer. Passed control IDs MUST come from
independent existing project-specific source/test evaluators supplied by caller.
"""
from __future__ import annotations
import re
from .enguru_method_three_phase_gate_v1 import (
    review as review_three, _verified, _expected_ids, _hold, MIN_ROUNDS, MAX_ROUNDS,
)

HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
OSI_REQUIRED = (
    "SOURCE_MANIFEST", "TARGET_READ_ONLY", "TOOLCHAIN", "DISK_BUDGET",
    "PROTECTED_WORKTREE", "ROLLBACK", "CHECKPOINT_RESTART", "HUMAN_DECISION_SCOPE",
)


def _stop(reason, stage, core=None, rounds=None):
    return {
        "state": "HOLD", "reason": reason, "activeStage": stage,
        "priorStages": core, "osiRounds": rounds or [],
        "GITHUB_PREPARED": "HOLD" if stage in ("DESIGN", "THEORY", "GITHUB") else "PASS_EXTERNAL_CI",
        "OSI_HANDOFF_PREPARED": "HOLD",
        "OSI_FIELD_READY": "HOLD", "HUMAN_AUTHORIZED": "HOLD",
        "VERIFIED_FINISH": "HOLD", "macWrites": 0, "nextAction": "REPAIR_EVIDENCE_THEN_REEVALUATE",
    }


def review_full_chain(plan, verify_controls, verify_github, inspect_osi):
    """A fourth evidence-gated planning stage, after exact GitHub verification.

    All 3 callbacks must perform their own checks on real evidence. Supplying
    fake callbacks only tests policy logic and NEVER proves a real deployment.
    """
    if not isinstance(plan, dict) or not all(callable(x) for x in
                                             (verify_controls, verify_github, inspect_osi)):
        return _stop("HOLD_VERIFIER_REQUIRED", "DESIGN")
    goal = plan.get("userGoal")
    acceptance = plan.get("originalAcceptanceIds")
    if (not isinstance(goal, str) or not goal.strip()
            or not isinstance(acceptance, list) or not acceptance
            or any(not isinstance(x, str) or not x.strip() for x in acceptance)
            or len(acceptance) != len(set(acceptance))):
        return _stop("HOLD_USER_GOAL_AND_ORIGINAL_ACCEPTANCE", "DESIGN")
    core = review_three(plan, verify_controls)
    if core.get("policyVerdict") != "PASS_THREE_PHASE_POLICY_REQUIRES_EXTERNAL_CI":
        return _stop(core.get("reason", "HOLD_PRIOR_THREE_STAGES"),
                     core.get("activePhase", "GITHUB"), core)
    final_source = core["history"][-1]["sourceSha256"]
    try:
        # Confirm design and theory on the *final* source, not stale early rounds.
        rechecked = []
        for phase in ("DESIGN", "THEORY"):
            result = _verified(plan, phase,
                               {"caseId": "FINAL_SOURCE_REVALIDATION",
                                "sourceSha256": final_source},
                               verify_controls)
            if result["score"] != 100 or result["sourceSha256"] != final_source:
                return _stop("HOLD_FINAL_SOURCE_REVALIDATION", phase, core)
            rechecked.append(result)
        github = verify_github(final_source)
        if not isinstance(github, dict):
            return _stop("HOLD_GITHUB_RECEIPT", "GITHUB", core)
        github_head = github.get("head")
        if (not isinstance(github_head, str) or not HEX40.fullmatch(github_head)
                or github.get("sourceSha256") != final_source
                or github.get("ciHead") != github_head
                or github.get("checksState") != "SUCCESS"
                or github.get("canonicalLockVerified") is not True
                or github.get("originalAcceptanceIds") != acceptance
                or not isinstance(github.get("receiptSha256"), str)
                or not HEX64.fullmatch(github["receiptSha256"])):
            return _stop("HOLD_EXACT_GITHUB_SOURCE_CI_AND_SCOPE", "GITHUB", core)
        preflight = inspect_osi(github_head)
        if (not isinstance(preflight, dict)
                or preflight.get("readOnly") is not True
                or type(preflight.get("canonicalWrites")) is not int
                or preflight["canonicalWrites"] != 0
                or preflight.get("targetChecked") is not True
                or preflight.get("sourceHead") != github_head
                or not isinstance(preflight.get("receiptSha256"), str)
                or not HEX64.fullmatch(preflight["receiptSha256"])
                or not isinstance(preflight.get("targetHead"), str)
                or not HEX40.fullmatch(preflight["targetHead"])):
            return _stop("HOLD_OSI_REAL_READ_ONLY_PREFLIGHT", "OSI_HANDOFF", core)
        if tuple(plan.get("controls", {}).get("OSI_HANDOFF", ())) != OSI_REQUIRED:
            return _stop("HOLD_OSI_FIXED_CONTROL_SCOPE", "OSI_HANDOFF", core)
        rounds = plan.get("osiHandoffRounds")
        if not isinstance(rounds, list) or not MIN_ROUNDS <= len(rounds) <= MAX_ROUNDS:
            return _stop("HOLD_OSI_ROUND_COUNT_3_TO_5", "OSI_HANDOFF", core)
        history, previous, first_oracle, has_repair = [], None, None, False
        for idx, challenge in enumerate(rounds):
            if not isinstance(challenge, dict) or not isinstance(challenge.get("caseId"), str):
                return _stop("HOLD_OSI_ROUND_ID", "OSI_HANDOFF", core, history)
            item = _verified(plan, "OSI_HANDOFF",
                             {"caseId": challenge["caseId"],
                              "sourceSha256": final_source,
                              "preflightSha256": preflight["receiptSha256"]},
                             verify_controls)
            item["round"] = idx+1
            if item["sourceSha256"] != final_source:
                return _stop("HOLD_OSI_SOURCE_DRIFT", "OSI_HANDOFF", core, history)
            if idx == 0:
                first_oracle = item["oracleId"]
            if idx == 2 and item["oracleId"] == first_oracle:
                return _stop("HOLD_OSI_THIRD_INDEPENDENT_ORACLE", "OSI_HANDOFF", core, history)
            if previous is not None:
                if (item["sourceSha256"], item["evidenceSha256"]) == (
                        previous["sourceSha256"], previous["evidenceSha256"]):
                    return _stop("HOLD_OSI_REPLAY_WITHOUT_EVIDENCE", "OSI_HANDOFF", core, history)
                if idx >= 3 and not set(item["passedIds"]) - set(previous["passedIds"]):
                    return _stop("HOLD_OSI_EXTRA_ROUND_NO_NEW_PASS", "OSI_HANDOFF", core, history)
                has_repair |= bool(set(item["passedIds"]) - set(previous["passedIds"]))
            history.append(item)
            previous = item
        if history[-1]["score"] != 100:
            return _stop("HOLD_OSI_HANDOFF_CONTROL_GAPS", "OSI_HANDOFF", core, history)
        return {
            "state": "PASS_HANDOFF_POLICY_AWAIT_HUMAN",
            "userGoal": goal, "originalAcceptanceIds": acceptance,
            "stageOrder": ["DESIGN", "THEORY", "GITHUB", "OSI_HANDOFF"],
            "designTheoryRevalidated": True,
            "githubHead": github_head, "githubReceiptSha256": github["receiptSha256"],
            "osiPreflightReceiptSha256": preflight["receiptSha256"],
            "osiRoundScores": [x["score"] for x in history],
            "osiHandoffScore": history[-1]["score"],
            "osiHandoffRounds": history,
            "GITHUB_PREPARED": "PASS_EXTERNAL_CI",
            "OSI_HANDOFF_PREPARED": "PASS_READ_ONLY_PLAN_ONLY",
            "OSI_FIELD_READY": "HOLD_REAL_EXECUTION",
            "HUMAN_AUTHORIZED": "HOLD",
            "VERIFIED_FINISH": "HOLD", "macWrites": 0,
            "nextAction": "READY_FOR_OSI_TRANSFER_HUMAN_DECISION__DUR",
        }
    except (ValueError, TypeError, KeyError, OSError, RecursionError):
        return _stop("HOLD_EXTERNAL_VERIFICATION_EXCEPTION", "OSI_HANDOFF", core)
