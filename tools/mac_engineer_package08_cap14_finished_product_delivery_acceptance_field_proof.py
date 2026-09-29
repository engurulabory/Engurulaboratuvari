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

BASE = (
    HOME
    / "Enguru/Evidence/MacEngineer/package08-field-campaign"
    / "20260929T180813740202000Z/capability-14"
)

DELIVERY = BASE / "immutable-delivery-package.json"
TECHNICAL = BASE / "technical-delivery-candidate.json"
HT_CANDIDATE = BASE / "human-threshold-candidate.json"
HT_RECEIPT = BASE / "human-threshold-accept-receipt.json"

POST_HUMAN = (
    HOME
    / "Enguru/Evidence/MacEngineer/package08-field-campaign"
    / "20260929T181255361970000Z/capability-14"
    / "post-human-delivery-acceptance.json"
)

EXPECTED = {
    "delivery":
        "c92cafc7da9763acdacc1b267a168d62b6cf7c92c30354838127c740516c6c13",

    "technical":
        "b0e24a77ab0bce86cb548073aa95c799da4d9834cdd897ebdceae9a2933a90c0",

    "htCandidate":
        "40b88fd4b601a91e5c86ab36997c45bd5f18a0318775a22cb9308c25f74740ae",

    "htReceipt":
        "744c8919f84ffb222f363ccfd5b5e85ac493d6297a2a46e4eb3c5aceffa72bb0",

    "postHuman":
        "b34e072246ea77655a521a0198ba130a3bf8bc7cc08cfb8e82447aed69aa5b64",
}

CONTROL_HEAD = (
    "11090cc70f04cd77169765bf0da330eb449ce6d5"
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
    sources = {
        "delivery": DELIVERY,
        "technical": TECHNICAL,
        "htCandidate": HT_CANDIDATE,
        "htReceipt": HT_RECEIPT,
        "postHuman": POST_HUMAN,
    }

    for key, path in sources.items():
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

    delivery = load(DELIVERY)
    technical = load(TECHNICAL)
    receipt = load(HT_RECEIPT)
    post = load(POST_HUMAN)

    if (
        delivery.get("state")
        != "READY_FOR_HUMAN_ACCEPTANCE"
        or delivery.get("capabilityId")
        != "FINISHED_PRODUCT_DELIVERY_ACCEPTANCE"
    ):
        raise RuntimeError(
            "DELIVERY_PACKAGE_REQUIRED"
        )

    identity = (
        delivery.get(
            "deliveryIdentity"
        )
        or {}
    )

    if (
        identity.get("productHead")
        != PRODUCT_HEAD
        or identity.get("sourceCommit")
        != PRODUCT_HEAD
    ):
        raise RuntimeError(
            "DELIVERY_PRODUCT_IDENTITY_REQUIRED"
        )

    if (
        technical.get("state")
        != "PASS"
        or technical.get("capabilityId")
        != "FINISHED_PRODUCT_DELIVERY_ACCEPTANCE"
    ):
        raise RuntimeError(
            "TECHNICAL_CANDIDATE_REQUIRED"
        )

    technical_truth = (
        technical.get(
            "technicalTruth"
        )
        or {}
    )

    required_technical = [
        "productIdentity",
        "codesign",
        "freshRuntime",
        "deliveryManifest",
        "acceptanceCriteria",
        "cap13ReleaseLifecycleBound",
        "noHumanAcceptanceProducesPass",
        "staleAcceptanceRejected",
    ]

    if not all(
        technical_truth.get(key)
        is True
        for key in required_technical
    ):
        raise RuntimeError(
            "TECHNICAL_DELIVERY_PROOF_INCOMPLETE"
        )

    human = (
        receipt.get(
            "humanThreshold"
        )
        or {}
    )

    if (
        receipt.get("state") != "ACCEPT"
        or receipt.get("capabilityId")
        != "FINISHED_PRODUCT_DELIVERY_ACCEPTANCE"
        or human.get("decision")
        != "ACCEPT"
        or human.get("scope")
        != "ACCEPT_EXACT_IMMUTABLE_FINISHED_PRODUCT_DELIVERY_PACKAGE"
        or human.get("deliveryPackageSha256")
        != EXPECTED["delivery"]
        or human.get("productHead")
        != PRODUCT_HEAD
        or human.get("sourceCommit")
        != PRODUCT_HEAD
    ):
        raise RuntimeError(
            "EXACT_HUMAN_ACCEPTANCE_REQUIRED"
        )

    if (
        human.get("productMutation")
        is not False
        or human.get("releaseMutation")
        is not False
        or human.get("remotePush")
        is not False
        or human.get("cloudPublication")
        is not False
        or human.get("doneCheckGranted")
        is not False
        or human.get("fieldVerifiedGranted")
        is not False
    ):
        raise RuntimeError(
            "HUMAN_ACCEPTANCE_BOUNDARY_VIOLATION"
        )

    post_ht = (
        post.get("humanThreshold")
        or {}
    )

    accepted = (
        post.get(
            "deliveryAcceptance"
        )
        or {}
    )

    fresh = (
        post.get(
            "freshPostHumanTruth"
        )
        or {}
    )

    boundary = (
        post.get(
            "authorityBoundary"
        )
        or {}
    )

    if (
        post.get("state") != "PASS"
        or post.get("capabilityId")
        != "FINISHED_PRODUCT_DELIVERY_ACCEPTANCE"
        or post_ht.get("decision")
        != "ACCEPT"
        or post_ht.get(
            "exactDeliveryPackageBound"
        )
        is not True
        or post_ht.get(
            "exactProductIdentityBound"
        )
        is not True
    ):
        raise RuntimeError(
            "POST_HUMAN_ACCEPTANCE_REQUIRED"
        )

    if (
        accepted.get(
            "deliveryPackageSha256"
        )
        != EXPECTED["delivery"]
        or accepted.get(
            "humanAccepted"
        )
        is not True
        or accepted.get(
            "finishedProductDelivered"
        )
        is not True
        or accepted.get(
            "packageImmutableAfterAcceptance"
        )
        is not True
    ):
        raise RuntimeError(
            "DELIVERY_ACCEPTANCE_REQUIRED"
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
            "FRESH_RUNTIME_REQUIRED"
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

    if (
        fresh.get("productHead")
        != PRODUCT_HEAD
        or fresh.get(
            "installedReleaseCommit"
        )
        != PRODUCT_HEAD
        or fresh.get(
            "runtimeFreshReverify"
        )
        is not True
    ):
        raise RuntimeError(
            "POST_HUMAN_FRESH_TRUTH_REQUIRED"
        )

    if (
        boundary.get("productMutation")
        is not False
        or boundary.get("releaseMutation")
        is not False
        or boundary.get("remotePush")
        is not False
        or boundary.get("cloudPublication")
        is not False
        or boundary.get("doneCheckGranted")
        is not False
        or boundary.get("fieldVerifiedGranted")
        is not False
    ):
        raise RuntimeError(
            "POST_HUMAN_BOUNDARY_VIOLATION"
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
        / "capability-14"
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
            "enguru.mac-engineer.package08-capability14-registered-action/v1",

        "observedAt":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "state":
            "PASS",

        "capabilityId":
            "FINISHED_PRODUCT_DELIVERY_ACCEPTANCE",

        "authority":
            "RED",

        "riskClass":
            "HIGH",

        "fieldModel":
            "IMMUTABLE_DELIVERY_PACKAGE_WITH_HUMAN_ACCEPTANCE_RECEIPT",

        "mutationScope":
            "EVIDENCE_AND_ACCEPTANCE_ONLY",

        "humanThreshold": {
            "required":
                True,

            "decision":
                "ACCEPT",

            "receiptPath":
                str(HT_RECEIPT),

            "receiptSha256":
                sha(HT_RECEIPT),

            "deliveryPackageSha256":
                sha(DELIVERY),

            "acceptanceAlreadyConsumed":
                True,

            "acceptanceReexecutedByRegisteredAction":
                False,
        },

        "deliveryAcceptance": {
            "deliveryPackagePath":
                str(DELIVERY),

            "deliveryPackageSha256":
                sha(DELIVERY),

            "postHumanEvidencePath":
                str(POST_HUMAN),

            "postHumanEvidenceSha256":
                sha(POST_HUMAN),

            "exactProductIdentityBound":
                True,

            "finishedProductDelivered":
                True,

            "humanAccepted":
                True,

            "packageImmutable":
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
            "productMutation":
                False,

            "releaseMutation":
                False,

            "remotePush":
                False,

            "cloudPublication":
                False,

            "executionAuthorityCreated":
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
    print(
        "CAP14_FINISHED_PRODUCT_DELIVERY_ACCEPTANCE=PASS"
    )
    print(
        "HUMAN_THRESHOLD_ACCEPT=PASS"
    )
    print(
        "HT_ACCEPTANCE_ALREADY_CONSUMED=PASS"
    )
    print(
        "DELIVERY_PACKAGE_IMMUTABLE=PASS"
    )
    print(
        "EXACT_PRODUCT_IDENTITY_BOUND=PASS"
    )
    print(
        "FINISHED_PRODUCT_DELIVERED=PASS"
    )
    print(
        "HUMAN_DELIVERY_ACCEPTANCE=PASS"
    )
    print(
        "FRESH_CODESIGN=PASS"
    )
    print(
        "FRESH_RUNTIME_REVERIFY=PASS"
    )
    print(
        "PRODUCT_MUTATION=false"
    )
    print(
        "RELEASE_MUTATION=false"
    )
    print(
        "REMOTE_PUSH=false"
    )
    print(
        "CLOUD_PUBLICATION=false"
    )
    print(
        "EXECUTION_AUTHORITY_CREATED=false"
    )
    print(
        "CRITICAL_FALSE_PASS_COUNT=0"
    )
    print(
        "CANONICAL_TRUTH_PRESERVED=PASS"
    )
    print(
        "AUTHORITY=RED"
    )
    print(
        "MUTATION_SCOPE=EVIDENCE_AND_ACCEPTANCE_ONLY"
    )
    print(
        "DELIVERY_PACKAGE_SHA256="
        + sha(DELIVERY)
    )
    print(
        "HUMAN_THRESHOLD_RECEIPT_SHA256="
        + sha(HT_RECEIPT)
    )
    print(
        "POST_HUMAN_EVIDENCE_SHA256="
        + sha(POST_HUMAN)
    )
    print(
        "EVIDENCE="
        + str(evidence)
    )

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
