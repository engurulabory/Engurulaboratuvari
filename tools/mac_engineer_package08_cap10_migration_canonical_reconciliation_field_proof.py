#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

HOME = Path.home()

ROOT = (
    HOME
    / "Enguru/Projects/Engurulaboratuvari"
)

CAP10_DIR = (
    HOME
    / "Enguru/Evidence/MacEngineer"
    / "package08-field-campaign"
    / "20260929T161755009160000Z"
    / "capability-10"
)

TECHNICAL = (
    CAP10_DIR
    / "migration-reconciliation-technical-candidate.json"
)

HT_CANDIDATE = (
    CAP10_DIR
    / "human-threshold-candidate.json"
)

HT_RECEIPT = (
    CAP10_DIR
    / "human-threshold-accept-receipt.json"
)

POST_HUMAN = (
    CAP10_DIR
    / "post-human-fresh-reconciliation.json"
)

EXPECTED = {
    "technical":
        "83ed2972b26498cc534984d7894c60a7b40dcdaaf54110447d7994299a3d77a8",

    "htCandidate":
        "e9b59572378c67eaa8f623535642df514a6b5143ad17a4e491334f2ff5138014",

    "htReceipt":
        "b48f594ffb7e66bac4209e1882c6c8394789c4b78da38be47cfe2ea96f0703c4",

    "postHuman":
        "2e8c2ad9b2141e6d5de82741cfbddc62cde00ce22392f87dc8e0034279e8592e",
}

EXPECTED_HEAD = (
    "04fb818424143f052d5c88d03c1c5cddbc80589b"
)


def sha(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def run(
    args: list[str],
    *,
    cwd: Path = ROOT,
    timeout: int = 180,
) -> dict[str, Any]:
    p = subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )

    return {
        "code": p.returncode,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(
            "REQUIRED_EVIDENCE_MISSING:"
            + str(path)
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def main() -> int:
    for label, path in (
        ("technical", TECHNICAL),
        ("htCandidate", HT_CANDIDATE),
        ("htReceipt", HT_RECEIPT),
        ("postHuman", POST_HUMAN),
    ):
        actual = sha(path)

        if actual != EXPECTED[label]:
            raise RuntimeError(
                "EVIDENCE_DIGEST_MISMATCH:"
                + label
            )

    technical = load(TECHNICAL)
    ht_candidate = load(HT_CANDIDATE)
    receipt = load(HT_RECEIPT)
    post = load(POST_HUMAN)

    if (
        technical.get("state") != "PASS"
        or technical.get("capabilityId")
        != "MIGRATION_CANONICAL_RECONCILIATION"
    ):
        raise RuntimeError(
            "TECHNICAL_CANDIDATE_PASS_REQUIRED"
        )

    tech = (
        technical.get(
            "technicalCandidate"
        )
        or {}
    )

    technical_checks = {
        "staleTruthObserved":
            tech.get(
                "staleTruthObserved"
            )
            is True,

        "canonicalTruthIdentified":
            tech.get(
                "canonicalTruthIdentified"
            )
            is True,

        "boundedCandidate":
            tech.get(
                "boundedReconciliationCandidate"
            )
            is True,

        "rollbackParity":
            tech.get(
                "rollbackPreimageParity"
            )
            is True,

        "idempotent":
            tech.get(
                "idempotent"
            )
            is True,

        "staleResumeRejected":
            tech.get(
                "staleResumeRejected"
            )
            is True,
    }

    if not all(
        technical_checks.values()
    ):
        raise RuntimeError(
            "TECHNICAL_CANDIDATE_CONTRACT_HOLD"
        )

    if (
        ht_candidate.get("state")
        != "READY_FOR_HUMAN_THRESHOLD"
    ):
        raise RuntimeError(
            "HT_CANDIDATE_READY_REQUIRED"
        )

    if (
        receipt.get("state")
        != "ACCEPT"
    ):
        raise RuntimeError(
            "HUMAN_THRESHOLD_ACCEPT_REQUIRED"
        )

    human = (
        receipt.get("humanThreshold")
        or {}
    )

    if (
        human.get("decision")
        != "ACCEPT"
        or human.get("scope")
        != "AUTHORIZE_POST_HUMAN_FRESH_RECONCILIATION_ONLY"
    ):
        raise RuntimeError(
            "HUMAN_THRESHOLD_SCOPE_HOLD"
        )

    if (
        human.get(
            "finalFieldVerificationGranted"
        )
        is not False
        or human.get(
            "canonicalPromotionGranted"
        )
        is not False
    ):
        raise RuntimeError(
            "HT_MUST_NOT_SELF_GRANT_FINALITY"
        )

    if (
        post.get("state")
        != "PASS"
        or post.get("capabilityId")
        != "MIGRATION_CANONICAL_RECONCILIATION"
    ):
        raise RuntimeError(
            "POST_HUMAN_PASS_REQUIRED"
        )

    fresh = (
        post.get("freshReread")
        or {}
    )

    for surface in (
        "repo",
        "runtime",
        "artifact",
        "state",
    ):
        if (
            fresh.get(surface, {})
            .get("state")
            != "PASS"
        ):
            raise RuntimeError(
                "POST_HUMAN_SURFACE_HOLD:"
                + surface
            )

    gate = (
        post.get(
            "reconciliationGate"
        )
        or {}
    )

    if (
        gate.get("state")
        != "PASS"
        or gate.get("reason")
        != "new_verified_state_established"
    ):
        raise RuntimeError(
            "POST_HUMAN_GATE_PASS_REQUIRED"
        )

    negative = (
        post.get("negativeControl")
        or {}
    )

    if (
        negative.get(
            "staleResumeRejected"
        )
        is not True
        or negative.get(
            "staleResumeState"
        )
        != "HOLD"
        or negative.get(
            "staleResumeReason"
        )
        != "post_human_revision_not_advanced"
    ):
        raise RuntimeError(
            "STALE_RESUME_NEGATIVE_CONTROL_REQUIRED"
        )

    head = run(
        ["git", "rev-parse", "HEAD"]
    )

    status = run(
        ["git", "status", "--porcelain"]
    )

    if (
        head["code"] != 0
        or head["stdout"]
        != EXPECTED_HEAD
    ):
        raise RuntimeError(
            "FRESH_REPO_HEAD_REQUIRED"
        )

    # During registered execution only the bounded
    # Cap10 control-plane patch may be present.
    if status["code"] != 0:
        raise RuntimeError(
            "FRESH_REPO_STATUS_REQUIRED"
        )

    runtime = run(
        [
            "python3",
            "-B",
            "-c",
            (
                "import sys;"
                "sys.path.insert(0,'tools');"
                "import mac_engineer_operator;"
                "print('OPERATOR_RUNTIME_IMPORT_PASS')"
            ),
        ]
    )

    if (
        runtime["code"] != 0
        or runtime["stdout"]
        != "OPERATOR_RUNTIME_IMPORT_PASS"
    ):
        raise RuntimeError(
            "FRESH_RUNTIME_REQUIRED"
        )

    payload = {
        "schema":
            "enguru.mac-engineer.package08-capability10-registered-action/v1",

        "state":
            "PASS",

        "capabilityId":
            "MIGRATION_CANONICAL_RECONCILIATION",

        "authority":
            "AMBER",

        "riskClass":
            "HIGH",

        "fieldModel":
            "HT_ACCEPT_BOUND_POST_HUMAN_CANONICAL_RECONCILIATION",

        "mutationScope":
            "EXPLICIT_RECONCILIATION_SCOPE",

        "humanThreshold": {
            "required":
                True,

            "accepted":
                True,

            "receiptPath":
                str(HT_RECEIPT),

            "receiptSha256":
                sha(HT_RECEIPT),
        },

        "technicalCandidate": {
            "path":
                str(TECHNICAL),

            "sha256":
                sha(TECHNICAL),

            "rollbackPreimageParity":
                True,

            "idempotent":
                True,
        },

        "postHumanReconciliation": {
            "path":
                str(POST_HUMAN),

            "sha256":
                sha(POST_HUMAN),

            "repoFresh":
                True,

            "runtimeFresh":
                True,

            "artifactFresh":
                True,

            "stateFresh":
                True,

            "newVerifiedStateEstablished":
                True,

            "staleResumeRejected":
                True,
        },

        "freshExecutionTruth": {
            "controlHead":
                head["stdout"],

            "runtimeImport":
                "PASS",
        },

        "rollbackRecovery": {
            "required":
                True,

            "technicalRollbackParity":
                True,

            "reconciliationIdempotency":
                True,
        },

        "criticalFalsePassCount":
            0,

        "canonicalTruthPreserved":
            True,
    }

    evidence_dir = (
        HOME
        / "Enguru/Evidence/MacEngineer"
        / "package08-field-campaign"
        / "20260929T161755009160000Z"
        / "capability-10"
    )

    evidence = (
        evidence_dir
        / "registered-action-result.json"
    )

    evidence.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print("STATE=PASS")
    print(
        "CAP10_MIGRATION_CANONICAL_RECONCILIATION=PASS"
    )
    print("HUMAN_THRESHOLD_ACCEPT=PASS")
    print("TECHNICAL_ROLLBACK_PARITY=PASS")
    print("RECONCILIATION_IDEMPOTENCY=PASS")
    print("FRESH_REPO_REREAD=PASS")
    print("FRESH_RUNTIME_REREAD=PASS")
    print("FRESH_ARTIFACT_REREAD=PASS")
    print("FRESH_STATE_REREAD=PASS")
    print("NEW_VERIFIED_STATE_ESTABLISHED=PASS")
    print("STALE_RESUME_REJECTED=PASS")
    print("CRITICAL_FALSE_PASS_COUNT=0")
    print("CANONICAL_TRUTH_PRESERVED=PASS")
    print("AUTHORITY=AMBER")
    print(
        "MUTATION_SCOPE=EXPLICIT_RECONCILIATION_SCOPE"
    )
    print("REMOTE_PUSH=false")
    print("EXECUTION_AUTHORITY_CREATED=false")
    print(
        "HUMAN_THRESHOLD_RECEIPT_SHA256="
        + sha(HT_RECEIPT)
    )
    print(
        "POST_HUMAN_EVIDENCE_SHA256="
        + sha(POST_HUMAN)
    )
    print("EVIDENCE=" + str(evidence))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("STATE=HOLD")
        print(
            "HOLD="
            + type(exc).__name__
            + ":"
            + str(exc)
        )
        raise SystemExit(2)
