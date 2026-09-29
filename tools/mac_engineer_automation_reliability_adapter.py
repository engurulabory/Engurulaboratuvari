#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PRODUCT = (
    Path.home()
    / "Enguru"
    / "Projects"
    / "enguru-mac-engineer"
)

RELIABILITY_PATH = (
    PRODUCT
    / "runtime"
    / "reliability.py"
)


def _load_reliability_module():
    if not RELIABILITY_PATH.is_file():
        raise RuntimeError(
            "RELIABILITY_RUNTIME_MISSING"
        )

    spec = importlib.util.spec_from_file_location(
        "enguru_product_reliability",
        RELIABILITY_PATH,
    )

    if not spec or not spec.loader:
        raise RuntimeError(
            "RELIABILITY_RUNTIME_IMPORT_FAILED"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


RELIABILITY = _load_reliability_module()
ReliabilityManager = RELIABILITY.ReliabilityManager


def execution_id(
    plan: dict[str, Any],
    step_index: int,
) -> str:

    if plan.get("STATE") != "PLAN_READY":
        raise ValueError("PLAN_NOT_READY")

    if plan.get("EXECUTION_AUTHORIZED") is not False:
        raise ValueError(
            "PACKAGE04_EXECUTION_AUTHORITY_VIOLATION"
        )

    plan_id = str(
        plan.get("PLAN_ID") or ""
    ).strip()

    truth = str(
        plan.get("TRUTH_FINGERPRINT") or ""
    ).strip()

    capabilities = plan.get(
        "CAPABILITY_PLAN"
    )

    if not plan_id:
        raise ValueError("PLAN_ID_MISSING")

    if not truth:
        raise ValueError(
            "TRUTH_FINGERPRINT_MISSING"
        )

    if not isinstance(capabilities, list):
        raise ValueError(
            "CAPABILITY_PLAN_MISSING"
        )

    if (
        step_index < 1
        or step_index > len(capabilities)
    ):
        raise ValueError(
            "PLAN_STEP_INDEX_INVALID"
        )

    capability_id = capabilities[
        step_index - 1
    ]

    raw = "|".join(
        [
            plan_id,
            truth,
            str(step_index),
            capability_id,
        ]
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def retry_limit_from_max_attempts(
    max_attempts: int,
) -> int:

    if not isinstance(max_attempts, int):
        raise ValueError(
            "MAX_ATTEMPTS_NOT_INT"
        )

    if max_attempts < 1:
        raise ValueError(
            "MAX_ATTEMPTS_BELOW_MINIMUM"
        )

    if max_attempts > 2:
        raise ValueError(
            "MAX_ATTEMPTS_EXCEEDS_CONTRACT"
        )

    return max_attempts - 1


def begin_execution(
    plan: dict[str, Any],
    step_index: int,
    durable_root: Path,
) -> dict[str, Any]:

    eid = execution_id(
        plan,
        step_index,
    )

    capability_id = plan[
        "CAPABILITY_PLAN"
    ][step_index - 1]

    manager = ReliabilityManager(
        durable_root
    )

    started = manager.begin(
        eid,
        metadata={
            "executionId": eid,
            "planId": plan["PLAN_ID"],
            "truthFingerprint":
                plan["TRUTH_FINGERPRINT"],
            "stepIndex": step_index,
            "capabilityId":
                capability_id,
        },
    )

    task = started["task"]
    duplicate = bool(
        started.get("duplicate")
    )

    if not duplicate:
        task = manager.transition(
            task["task_id"],
            "RUNNING",
            note=
                "PACKAGE06_GENERIC_EXECUTION_BEGIN",
        )

    return {
        "STATE": "PASS",
        "EXECUTION_ID": eid,
        "TASK_ID": task["task_id"],
        "TASK_STATE": task["state"],
        "DUPLICATE": duplicate,
        "EFFECT_EXECUTION_ALLOWED":
            not duplicate,
        "CAPABILITY_ID":
            capability_id,
        "PLAN_ID":
            plan["PLAN_ID"],
        "TRUTH_FINGERPRINT":
            plan["TRUTH_FINGERPRINT"],
        "STEP_INDEX": step_index,
    }


def checkpoint_execution(
    plan: dict[str, Any],
    step_index: int,
    durable_root: Path,
    task_id: str,
    payload_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:

    eid = execution_id(
        plan,
        step_index,
    )

    payload = {
        "executionId": eid,
        "planId": plan["PLAN_ID"],
        "truthFingerprint":
            plan["TRUTH_FINGERPRINT"],
        "stepIndex": step_index,
        "capabilityId":
            plan["CAPABILITY_PLAN"][
                step_index - 1
            ],
    }

    if payload_extra:
        payload.update(payload_extra)

    manager = ReliabilityManager(
        durable_root
    )

    checkpoint = manager.checkpoint(
        task_id,
        payload,
        verified=True,
    )

    return {
        "STATE": "PASS",
        "TASK_ID": task_id,
        "EXECUTION_ID": eid,
        "CHECKPOINT_DIGEST":
            checkpoint["payload_digest"],
        "CHECKPOINT_VERIFIED":
            checkpoint["verified"],
    }


def resume_execution(
    plan: dict[str, Any],
    step_index: int,
    durable_root: Path,
    fresh_truth_fingerprint: str,
) -> dict[str, Any]:

    eid = execution_id(
        plan,
        step_index,
    )

    manager = ReliabilityManager(
        durable_root
    )

    started = manager.begin(
        eid,
        metadata={
            "executionId": eid,
            "planId": plan["PLAN_ID"],
            "truthFingerprint":
                plan["TRUTH_FINGERPRINT"],
            "stepIndex": step_index,
            "capabilityId":
                plan["CAPABILITY_PLAN"][
                    step_index - 1
                ],
        },
    )

    task = started["task"]

    if not started.get("duplicate"):
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "DURABLE_EXECUTION_IDENTITY_MISSING",
            "EXECUTION_PERFORMED": False,
        }

    checkpoint_result = (
        manager.load_checkpoint(
            task["task_id"]
        )
    )

    if not checkpoint_result.get("ok"):
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "VERIFIED_CHECKPOINT_REQUIRED",
            "EXECUTION_PERFORMED": False,
        }

    checkpoint = checkpoint_result[
        "checkpoint"
    ]

    if checkpoint.get("verified") is not True:
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "UNVERIFIED_CHECKPOINT",
            "EXECUTION_PERFORMED": False,
        }

    payload = checkpoint.get(
        "payload"
    ) or {}

    checkpoint_truth = str(
        payload.get(
            "truthFingerprint"
        ) or ""
    )

    if (
        checkpoint_truth
        != plan["TRUTH_FINGERPRINT"]
    ):
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "CHECKPOINT_PLAN_TRUTH_MISMATCH",
            "EXECUTION_PERFORMED": False,
        }

    if (
        fresh_truth_fingerprint
        != checkpoint_truth
    ):
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "STALE_TRUTH_FINGERPRINT",
            "EXECUTION_PERFORMED": False,
        }

    resumed = manager.resume(
        task["task_id"]
    )

    if not resumed.get("ok"):
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "RELIABILITY_RESUME_FAILED",
            "EXECUTION_PERFORMED": False,
            "RESULT": resumed,
        }

    return {
        "STATE": "PASS",
        "EXECUTION_ID": eid,
        "TASK_ID": task["task_id"],
        "DUPLICATE": True,
        "EFFECT_EXECUTION_ALLOWED": False,
        "CHECKPOINT_VERIFIED": True,
        "FRESH_TRUTH_REVALIDATED": True,
        "RESUME_RESULT": resumed,
    }
