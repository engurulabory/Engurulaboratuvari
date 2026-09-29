#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HOME = Path.home()

CONTROL = HOME / "Enguru/Projects/Engurulaboratuvari"
PRODUCT = HOME / "Enguru/Projects/enguru-mac-engineer"

APP = HOME / "Applications/ENGÜRÜ Mac Engineer.app"
APP_RELEASE = APP / "Contents/Resources/release.json"

TECHNICAL = (
    HOME
    / "Enguru/Evidence/MacEngineer/package08-field-campaign"
    / "20260929T174321739032000Z/capability-13"
    / "release-lifecycle-technical-candidate.json"
)

HT_CANDIDATE = (
    HOME
    / "Enguru/Evidence/MacEngineer/package08-field-campaign"
    / "20260929T174321739032000Z/capability-13"
    / "human-threshold-candidate.json"
)

HT_RECEIPT = (
    HOME
    / "Enguru/Evidence/MacEngineer/package08-field-campaign"
    / "20260929T174321739032000Z/capability-13"
    / "human-threshold-accept-receipt.json"
)

POST_HUMAN = (
    HOME
    / "Enguru/Evidence/MacEngineer/package08-field-campaign"
    / "20260929T174945301330000Z/capability-13"
    / "post-human-active-lifecycle.json"
)

P09_ACCEPTANCE = (
    HOME
    / "Enguru/Evidence/MacEngineer/v0.8"
    / "gate11-p09-lifecycle/20260929T174945Z"
    / "p09-final-acceptance.json"
)

EXPECTED = {
    "technical":
        "e5140854036d1ee332dcfb4f863d85aa5abc922cafe245d1dc3acc75ae89d782",

    "htCandidate":
        "259e6ca109d31b03dceed0af80d915bc529fc0d4744074cac793e59bb238d3e2",

    "htReceipt":
        "5f0d34425a05472a8376544fa2b9604b96cd9f3f1a1945f0f200ed4d80a3ce96",

    "postHuman":
        "46f81b7dd6d5291c1116e027c51808963f453a09af5aef0e2276f257a7d4889f",

    "p09":
        "638bd13a48f3070125571e22c38fe3735c30b0157da604513125c35c27b232f2",
}

CONTROL_HEAD = (
    "35fc0cebfeddaaa9faf33f2f635eea568fe21bf7"
)

PRODUCT_HEAD = (
    "0ca33cc7b70fee915d02de72946bbd4bb0e40065"
)


def sha(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def run(
    args: list[str],
    *,
    cwd: Path,
    timeout: int = 60,
):
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def main() -> int:
    paths = {
        "technical": TECHNICAL,
        "htCandidate": HT_CANDIDATE,
        "htReceipt": HT_RECEIPT,
        "postHuman": POST_HUMAN,
        "p09": P09_ACCEPTANCE,
    }

    for key, path in paths.items():
        if not path.is_file():
            raise RuntimeError(
                "REQUIRED_EVIDENCE_MISSING:"
                + key
            )

        if sha(path) != EXPECTED[key]:
            raise RuntimeError(
                "EVIDENCE_DIGEST_MISMATCH:"
                + key
            )

    technical = load(TECHNICAL)
    receipt = load(HT_RECEIPT)
    post = load(POST_HUMAN)
    p09 = load(P09_ACCEPTANCE)

    if (
        technical.get("state") != "PASS"
        or technical.get("capabilityId")
        != "RELEASE_LIFECYCLE"
    ):
        raise RuntimeError(
            "TECHNICAL_CANDIDATE_REQUIRED"
        )

    human = (
        receipt.get("humanThreshold")
        or {}
    )

    if (
        receipt.get("state") != "ACCEPT"
        or human.get("decision") != "ACCEPT"
        or human.get("scope")
        != "ONE_BOUNDED_FRESH_ACTIVE_LOCAL_RELEASE_LIFECYCLE_EXECUTION"
    ):
        raise RuntimeError(
            "HT_ACCEPT_RECEIPT_REQUIRED"
        )

    if (
        human.get("finalFieldVerificationGranted")
        is not False
        or human.get("verifiedLiveGranted")
        is not False
    ):
        raise RuntimeError(
            "HT_MUST_NOT_SELF_GRANT_FINALITY"
        )

    active = (
        post.get("activeLifecycle")
        or {}
    )

    fresh = (
        post.get("freshPostHumanTruth")
        or {}
    )

    boundary = (
        post.get("authorityBoundary")
        or {}
    )

    if (
        post.get("state") != "PASS"
        or post.get("capabilityId")
        != "RELEASE_LIFECYCLE"
    ):
        raise RuntimeError(
            "POST_HUMAN_PASS_REQUIRED"
        )

    required_active = [
        "controlledReplacement",
        "stop",
        "restart",
        "knownGoodRollback",
        "rollbackReverify",
        "lifecycleProvenance",
        "evidenceContinuity",
    ]

    if not all(
        active.get(key) is True
        for key in required_active
    ):
        raise RuntimeError(
            "ACTIVE_LIFECYCLE_PROOF_INCOMPLETE"
        )

    if (
        active.get("finalKnownGood")
        != "P08_VERIFIED"
    ):
        raise RuntimeError(
            "FINAL_KNOWN_GOOD_REQUIRED"
        )

    p09_acceptance = (
        p09.get("acceptance")
        or {}
    )

    p09_required = [
        "P08_PASS",
        "CONTROLLED_REPLACEMENT_PASS",
        "STOP_PASS",
        "RESTART_PASS",
        "KNOWN_GOOD_ROLLBACK_PASS",
        "ROLLBACK_REVERIFY_PASS",
        "LIFECYCLE_PROVENANCE_PASS",
        "EVIDENCE_CONTINUITY_PASS",
    ]

    if (
        p09.get("state") != "PASS"
        or p09.get("package") != "P09"
        or not all(
            p09_acceptance.get(key)
            == "PASS"
            for key in p09_required
        )
        or p09.get("sourceMutation") is not False
        or p09.get("remoteMutation") is not False
    ):
        raise RuntimeError(
            "P09_ACCEPTANCE_REQUIRED"
        )

    if (
        boundary.get("cloudProductionPublication")
        is not False
        or boundary.get("remotePush")
        is not False
        or boundary.get("dnsMutation")
        is not False
        or boundary.get("domainMutation")
        is not False
        or boundary.get("verifiedLiveGranted")
        is not False
        or boundary.get("finalFieldVerificationGranted")
        is not False
    ):
        raise RuntimeError(
            "AUTHORITY_BOUNDARY_VIOLATION"
        )

    control = run(
        ["git", "rev-parse", "HEAD"],
        cwd=CONTROL,
    )

    product = run(
        ["git", "rev-parse", "HEAD"],
        cwd=PRODUCT,
    )

    product_status = run(
        ["git", "status", "--porcelain"],
        cwd=PRODUCT,
    )

    if (
        control.returncode != 0
        or control.stdout.strip()
        != CONTROL_HEAD
    ):
        raise RuntimeError(
            "CONTROL_HEAD_REQUIRED"
        )

    if (
        product.returncode != 0
        or product.stdout.strip()
        != PRODUCT_HEAD
        or product_status.returncode != 0
        or product_status.stdout.strip()
    ):
        raise RuntimeError(
            "PRODUCT_TRUTH_REQUIRED"
        )

    release = load(APP_RELEASE)

    if (
        release.get("sourceCommit")
        != PRODUCT_HEAD
    ):
        raise RuntimeError(
            "INSTALLED_RELEASE_IDENTITY_REQUIRED"
        )

    codesign = run(
        [
            "codesign",
            "--verify",
            "--deep",
            "--strict",
            str(APP),
        ],
        cwd=CONTROL,
    )

    if codesign.returncode != 0:
        raise RuntimeError(
            "FRESH_CODESIGN_REQUIRED"
        )

    status = run(
        [
            "curl",
            "--max-time",
            "5",
            "-fsS",
            "http://127.0.0.1:8765/api/status",
        ],
        cwd=CONTROL,
    )

    if status.returncode != 0:
        raise RuntimeError(
            "FRESH_RUNTIME_STATUS_REQUIRED"
        )

    runtime = json.loads(
        status.stdout
    )

    runtime_ok = all([
        runtime.get("service")
            == "ENGÜRÜ Mac Engineer™",

        runtime.get("state")
            == "RUNNING",

        runtime.get("host")
            == "127.0.0.1",

        runtime.get("port")
            == 8765,

        runtime.get("governance")
            == "ACTIVE",
    ])

    if not runtime_ok:
        raise RuntimeError(
            "FRESH_RUNTIME_IDENTITY_REQUIRED"
        )

    evidence_dir = (
        HOME
        / "Enguru/Evidence/MacEngineer"
        / "package08-field-campaign"
        / datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%dT%H%M%S%fZ"
        )
        / "capability-13"
    )

    evidence_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    evidence = (
        evidence_dir
        / "registered-action-result.json"
    )

    payload = {
        "schema":
            "enguru.mac-engineer.package08-capability13-registered-action/v1",

        "observedAt":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "state":
            "PASS",

        "capabilityId":
            "RELEASE_LIFECYCLE",

        "authority":
            "RED",

        "riskClass":
            "HIGH",

        "fieldModel":
            "HT_ACCEPT_BOUND_ACTIVE_LOCAL_RELEASE_LIFECYCLE_WITH_KNOWN_GOOD_ROLLBACK",

        "mutationScope":
            "CONTROLLED_RELEASE_SCOPE",

        "humanThreshold": {
            "required":
                True,

            "decision":
                "ACCEPT",

            "receiptPath":
                str(HT_RECEIPT),

            "receiptSha256":
                sha(HT_RECEIPT),

            "consumedExecution":
                True,

            "reexecutedByRegisteredAction":
                False,
        },

        "activeLifecycle": {
            "postHumanEvidencePath":
                str(POST_HUMAN),

            "postHumanEvidenceSha256":
                sha(POST_HUMAN),

            "p09AcceptancePath":
                str(P09_ACCEPTANCE),

            "p09AcceptanceSha256":
                sha(P09_ACCEPTANCE),

            "controlledReplacement":
                True,

            "restart":
                True,

            "knownGoodRollback":
                True,

            "rollbackReverify":
                True,

            "lifecycleProvenance":
                True,

            "evidenceContinuity":
                True,
        },

        "freshReadback": {
            "controlHead":
                CONTROL_HEAD,

            "productHead":
                PRODUCT_HEAD,

            "installedReleaseCommit":
                PRODUCT_HEAD,

            "codesign":
                "PASS",

            "runtime":
                runtime,

            "runtimeFresh":
                True,
        },

        "authorityBoundary": {
            "cloudProductionPublication":
                False,

            "remotePush":
                False,

            "dnsMutation":
                False,

            "domainMutation":
                False,

            "verifiedLiveGranted":
                False,
        },

        "criticalFalsePassCount":
            0,

        "canonicalTruthPreserved":
            True,
    }

    evidence.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print("STATE=PASS")
    print("CAP13_RELEASE_LIFECYCLE=PASS")
    print("HUMAN_THRESHOLD_ACCEPT=PASS")
    print("HT_EXECUTION_ALREADY_CONSUMED=PASS")
    print("ACTIVE_LIFECYCLE_EXECUTED=PASS")
    print("CONTROLLED_REPLACEMENT=PASS")
    print("KNOWN_GOOD_ROLLBACK=PASS")
    print("ROLLBACK_REVERIFY=PASS")
    print("LIFECYCLE_PROVENANCE=PASS")
    print("EVIDENCE_CONTINUITY=PASS")
    print("FRESH_CODESIGN=PASS")
    print("FRESH_RUNTIME_REVERIFY=PASS")
    print("SOURCE_MUTATION=false")
    print("REMOTE_MUTATION=false")
    print("REMOTE_PUSH=false")
    print("EXECUTION_AUTHORITY_CREATED=false")
    print("CLOUD_PRODUCTION=false")
    print("DNS_MUTATION=false")
    print("DOMAIN_MUTATION=false")
    print("VERIFIED_LIVE_GRANTED=false")
    print("CRITICAL_FALSE_PASS_COUNT=0")
    print("CANONICAL_TRUTH_PRESERVED=PASS")
    print("AUTHORITY=RED")
    print("MUTATION_SCOPE=CONTROLLED_RELEASE_SCOPE")
    print(
        "HUMAN_THRESHOLD_RECEIPT_SHA256="
        + sha(HT_RECEIPT)
    )
    print(
        "POST_HUMAN_EVIDENCE_SHA256="
        + sha(POST_HUMAN)
    )
    print(
        "P09_ACCEPTANCE_SHA256="
        + sha(P09_ACCEPTANCE)
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
