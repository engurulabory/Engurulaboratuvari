#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mac_engineer_automation_reliability_adapter as adapter


def load(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def write(path: Path, value):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


def sha(path: Path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def phase_start(
    plan: dict,
    durable_root: Path,
):
    result = adapter.begin_execution(
        plan,
        1,
        durable_root,
    )

    if result["DUPLICATE"]:
        raise RuntimeError(
            "START_PHASE_MUST_NOT_BE_DUPLICATE"
        )

    if (
        result["EFFECT_EXECUTION_ALLOWED"]
        is not True
    ):
        raise RuntimeError(
            "FIRST_EFFECT_MUST_BE_ALLOWED"
        )

    effect = (
        durable_root
        / "proof"
        / "durable-effect.txt"
    )

    effect.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if effect.exists():
        raise RuntimeError(
            "DURABLE_EFFECT_PREEXISTS"
        )

    effect.write_text(
        result["EXECUTION_ID"] + "\n",
        encoding="utf-8",
    )

    checkpoint = (
        adapter.checkpoint_execution(
            plan,
            1,
            durable_root,
            result["TASK_ID"],
            payload_extra={
                "phase": "BEFORE_RESTART",
                "durableEffect":
                    str(effect),
                "durableEffectSha256":
                    sha(effect),
            },
        )
    )

    receipt = {
        "phase": "START",
        **result,
        "CHECKPOINT":
            checkpoint,
        "DURABLE_EFFECT":
            str(effect),
        "DURABLE_EFFECT_SHA256":
            sha(effect),
    }

    write(
        durable_root
        / "proof"
        / "phase-start.json",
        receipt,
    )

    print(
        json.dumps(
            receipt,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


def phase_stale(
    plan: dict,
    durable_root: Path,
):
    result = adapter.resume_execution(
        plan,
        1,
        durable_root,
        fresh_truth_fingerprint=
            "INTENTIONAL_STALE_TRUTH",
    )

    ok = (
        result.get("STATE") == "HOLD"
        and result.get("HOLD_REASON")
        == "STALE_TRUTH_FINGERPRINT"
        and result.get(
            "EXECUTION_PERFORMED"
        ) is False
    )

    print(
        "STALE_TRUTH_REJECTED="
        + ("PASS" if ok else "HOLD")
    )

    if not ok:
        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            )
        )
        raise SystemExit(20)


def phase_resume(
    plan: dict,
    durable_root: Path,
):
    start = load(
        durable_root
        / "proof"
        / "phase-start.json"
    )

    effect = Path(
        start["DURABLE_EFFECT"]
    )

    before_sha = sha(effect)

    result = adapter.resume_execution(
        plan,
        1,
        durable_root,
        fresh_truth_fingerprint=
            plan["TRUTH_FINGERPRINT"],
    )

    if result.get("STATE") != "PASS":
        raise RuntimeError(
            "FRESH_RESUME_REQUIRED"
        )

    if result.get("DUPLICATE") is not True:
        raise RuntimeError(
            "DUPLICATE_BEGIN_REQUIRED"
        )

    if (
        result.get(
            "EFFECT_EXECUTION_ALLOWED"
        )
        is not False
    ):
        raise RuntimeError(
            "EFFECT_REPLAY_MUST_BE_SUPPRESSED"
        )

    if (
        result["TASK_ID"]
        != start["TASK_ID"]
    ):
        raise RuntimeError(
            "TASK_IDENTITY_CHANGED"
        )

    if sha(effect) != before_sha:
        raise RuntimeError(
            "DURABLE_EFFECT_CHANGED"
        )

    manager = adapter.ReliabilityManager(
        durable_root
    )

    manager.transition(
        result["TASK_ID"],
        "VERIFYING",
        note=
            "PACKAGE06_FRESH_REVALIDATION_PASS",
    )

    complete = manager.transition(
        result["TASK_ID"],
        "COMPLETE",
        note=
            "PACKAGE06_FIELD_PROOF_COMPLETE",
    )

    receipt = {
        "phase": "RESUME",
        **result,
        "TASK_STATE":
            complete["state"],
        "DURABLE_EFFECT_SHA256":
            sha(effect),
        "DURABLE_EFFECT_REPLAYED":
            False,
    }

    write(
        durable_root
        / "proof"
        / "phase-resume.json",
        receipt,
    )

    print(
        json.dumps(
            receipt,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


def phase_verify(
    plan: dict,
    durable_root: Path,
):
    start = load(
        durable_root
        / "proof"
        / "phase-start.json"
    )

    resume = load(
        durable_root
        / "proof"
        / "phase-resume.json"
    )

    manager = adapter.ReliabilityManager(
        durable_root
    )

    task = manager.get(
        start["TASK_ID"]
    )

    journal_path = (
        durable_root
        / "logs"
        / "task-journal.jsonl"
    )

    journal = [
        json.loads(line)
        for line in journal_path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    create_commits = [
        row
        for row in journal
        if row.get("phase") == "COMMIT"
        and row.get("op") == "CREATE_TASK"
    ]

    checkpoint_commits = [
        row
        for row in journal
        if row.get("phase") == "COMMIT"
        and row.get("op") == "CHECKPOINT"
    ]

    checks = {
        "SAME_EXECUTION_ID":
            start["EXECUTION_ID"]
            == resume["EXECUTION_ID"],

        "SAME_TASK_ID":
            start["TASK_ID"]
            == resume["TASK_ID"],

        "DUPLICATE_BEGIN":
            resume["DUPLICATE"] is True,

        "EFFECT_REPLAY_SUPPRESSED":
            resume[
                "DURABLE_EFFECT_REPLAYED"
            ] is False,

        "FRESH_TRUTH_REVALIDATED":
            resume[
                "FRESH_TRUTH_REVALIDATED"
            ] is True,

        "CHECKPOINT_VERIFIED":
            resume[
                "CHECKPOINT_VERIFIED"
            ] is True,

        "ONE_CREATE_TASK_COMMIT":
            len(create_commits) == 1,

        "CHECKPOINT_COMMIT_PRESENT":
            len(checkpoint_commits) >= 1,

        "FINAL_STATE_COMPLETE":
            task["state"] == "COMPLETE",
    }

    for name, ok in checks.items():
        print(
            name
            + "="
            + ("PASS" if ok else "HOLD")
        )

    passed = sum(
        1
        for ok in checks.values()
        if ok
    )

    evidence = {
        "schema":
            "enguru.mac-engineer.package06-automation-reliability-field-proof/v1",

        "state":
            "PASS"
            if passed == len(checks)
            else "HOLD",

        "checks":
            checks,

        "executionId":
            start["EXECUTION_ID"],

        "taskId":
            start["TASK_ID"],

        "planId":
            plan["PLAN_ID"],

        "truthFingerprint":
            plan["TRUTH_FINGERPRINT"],

        "artifacts": {
            "start":
                str(
                    durable_root
                    / "proof"
                    / "phase-start.json"
                ),
            "resume":
                str(
                    durable_root
                    / "proof"
                    / "phase-resume.json"
                ),
            "journal":
                str(journal_path),
        },
    }

    evidence_path = (
        durable_root
        / "proof"
        / "evidence.json"
    )

    write(
        evidence_path,
        evidence,
    )

    print(
        "CHECKS="
        + str(passed)
        + "_OF_"
        + str(len(checks))
        + "_PASS"
    )

    print(
        "EVIDENCE="
        + str(evidence_path)
    )

    print(
        "EVIDENCE_SHA256="
        + sha(evidence_path)
    )

    if passed != len(checks):
        raise SystemExit(20)

    print("STATE=PASS")
    print(
        "CLAIM=PACKAGE06_RESTART_IDEMPOTENCY_FIELD_PROOF_PASS"
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--phase",
        required=True,
        choices=[
            "start",
            "stale",
            "resume",
            "verify",
        ],
    )

    parser.add_argument(
        "--plan-json",
        required=True,
    )

    parser.add_argument(
        "--durable-root",
        required=True,
    )

    args = parser.parse_args()

    plan = load(
        Path(args.plan_json)
    )

    root = Path(
        args.durable_root
    ).expanduser()

    if args.phase == "start":
        phase_start(
            plan,
            root,
        )

    elif args.phase == "stale":
        phase_stale(
            plan,
            root,
        )

    elif args.phase == "resume":
        phase_resume(
            plan,
            root,
        )

    else:
        phase_verify(
            plan,
            root,
        )


if __name__ == "__main__":
    main()
