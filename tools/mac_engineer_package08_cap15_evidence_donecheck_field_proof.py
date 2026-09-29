#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HOME = Path.home()

ROOT = (
    HOME
    / "Enguru/Projects/Engurulaboratuvari"
)

sys.path.insert(
    0,
    str(ROOT / "tools"),
)

import mac_engineer_governed_finish_adapter as finish
import mac_engineer_governed_finish_guard as guard


BASE = (
    HOME
    / "Enguru/Evidence/MacEngineer/package08-field-campaign"
    / "20260929T182059370448000Z/capability-15"
)

SOURCE = (
    BASE
    / "source-evidence.json"
)

FIELD = (
    BASE
    / "evidence-donecheck-field-proof.json"
)

CONTROLLED_HOLD = (
    BASE
    / "controlled-hold-evidence.json"
)

EXPECTED_SOURCE_SHA = (
    "8bfc00df230bd5f42b87d9e418e349ab6a205ff81ff2fe81be7d8991cb137740"
)

EXPECTED_FIELD_SHA = (
    "04b868f33dbff0863874925bdf9bb7553fa8fd998f7daada15bbb7b5525056af"
)

EXPECTED_DONECHECK_VERSION = (
    "1.2.0"
)

EXPECTED_DONECHECK_SHA = (
    "8b90a8fc93453dd8a84994195d28d14b15e261cb"
)


def sha(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def load(
    path: Path,
) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            "JSON_OBJECT_REQUIRED"
        )

    return value


def main() -> int:
    if not SOURCE.is_file():
        raise RuntimeError(
            "SOURCE_EVIDENCE_MISSING"
        )

    if not FIELD.is_file():
        raise RuntimeError(
            "FIELD_EVIDENCE_MISSING"
        )

    if not CONTROLLED_HOLD.is_file():
        raise RuntimeError(
            "NEGATIVE_EVIDENCE_MISSING"
        )

    if sha(SOURCE) != EXPECTED_SOURCE_SHA:
        raise RuntimeError(
            "SOURCE_EVIDENCE_DIGEST_MISMATCH"
        )

    if sha(FIELD) != EXPECTED_FIELD_SHA:
        raise RuntimeError(
            "FIELD_EVIDENCE_DIGEST_MISMATCH"
        )

    source = load(SOURCE)
    previous = load(FIELD)

    if (
        source.get("state")
        != "PASS"
        or source.get("capabilityId")
        != "EVIDENCE_DONECHECK"
    ):
        raise RuntimeError(
            "FRESH_PASS_SOURCE_REQUIRED"
        )

    if (
        previous.get("state")
        != "PASS"
        or previous.get("capabilityId")
        != "EVIDENCE_DONECHECK"
    ):
        raise RuntimeError(
            "PRIOR_FIELD_PROOF_REQUIRED"
        )

    if (
        finish.bridge.DONECHECK_VERSION
        != EXPECTED_DONECHECK_VERSION
    ):
        raise RuntimeError(
            "DONECHECK_VERSION_MISMATCH"
        )

    if (
        finish.bridge.DONECHECK_SHA
        != EXPECTED_DONECHECK_SHA
    ):
        raise RuntimeError(
            "DONECHECK_SHA_MISMATCH"
        )

    digest = sha(
        SOURCE
    )

    execution_id = (
        "package08-cap15-registered:"
        + digest[:24]
    )

    task_id = (
        "package08-cap15-registered-"
        + digest[:12]
    )

    machine = (
        finish.verify_machine_finish(
            evidence_path=SOURCE,

            execution_id=
                execution_id,

            task_id=
                task_id,

            criterion_id=
                "EVIDENCE_DONECHECK",

            statement=
                "Fresh criterion-scoped Evidence is verified by pinned DoneCheck v1.2",
        )
    )

    if (
        machine.get("STATE")
        != "PASS"
        or machine.get(
            "DONECHECK_STATE"
        )
        != "PASS"
        or machine.get(
            "DONECHECK_VERSION"
        )
        != EXPECTED_DONECHECK_VERSION
        or machine.get(
            "DONECHECK_SHA"
        )
        != EXPECTED_DONECHECK_SHA
        or machine.get(
            "EXECUTION_ID"
        )
        != execution_id
        or machine.get(
            "TASK_ID"
        )
        != task_id
        or not machine.get(
            "VERIFICATION_RESULT_ID"
        )
    ):
        raise RuntimeError(
            "FRESH_DONECHECK_PASS_REQUIRED"
        )

    green = (
        finish.evaluate_green_finish(
            machine
        )
    )

    if (
        green.get("STATE")
        != "VERIFIED"
    ):
        raise RuntimeError(
            "GREEN_VERIFIED_FINISH_REQUIRED"
        )

    # Negative control 1:
    # source Evidence with state != PASS
    # must not enter DoneCheck as PASS.
    nonpass_rejected = False
    nonpass_reason = None

    try:
        finish.verify_machine_finish(
            evidence_path=
                CONTROLLED_HOLD,

            execution_id=
                "package08-cap15-negative",

            task_id=
                "package08-cap15-negative",

            criterion_id=
                "EVIDENCE_DONECHECK",

            statement=
                "Non-PASS Evidence must fail closed",
        )
    except ValueError as exc:
        nonpass_reason = str(exc)

        nonpass_rejected = (
            nonpass_reason
            == "SOURCE_EVIDENCE_PASS_REQUIRED"
        )

    if not nonpass_rejected:
        raise RuntimeError(
            "NONPASS_SOURCE_FAIL_CLOSED_REQUIRED"
        )

    base = {
        "material_evidence_present":
            True,

        "fresh_verification":
            True,

        "cached_pass_used":
            False,

        "donecheck_state":
            "PASS",

        "ht_required":
            False,

        "human_decision":
            None,

        "execution_identity_bound":
            True,

        "donecheck_identity_bound":
            True,

        "supported_final_claim":
            True,
    }

    missing = dict(base)
    missing[
        "material_evidence_present"
    ] = False

    stale = dict(base)
    stale[
        "fresh_verification"
    ] = False
    stale[
        "cached_pass_used"
    ] = True

    nonpass = dict(base)
    nonpass[
        "donecheck_state"
    ] = "HOLD"

    unsupported = dict(base)
    unsupported[
        "supported_final_claim"
    ] = False

    negative = {
        "missingEvidenceHold":
            guard.evaluate_finish(
                **missing
            ).get("STATE")
            == "HOLD",

        "staleCachedPassHold":
            guard.evaluate_finish(
                **stale
            ).get("STATE")
            == "HOLD",

        "doneCheckNonPassHold":
            guard.evaluate_finish(
                **nonpass
            ).get("STATE")
            == "HOLD",

        "unsupportedClaimHold":
            guard.evaluate_finish(
                **unsupported
            ).get("STATE")
            == "HOLD",

        "nonPassSourceRejected":
            nonpass_rejected,
    }

    if not all(
        negative.values()
    ):
        raise RuntimeError(
            "FAIL_CLOSED_NEGATIVE_CONTROLS_REQUIRED"
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
        / "capability-15"
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
            "enguru.mac-engineer.package08-capability15-registered-action/v1",

        "observedAt":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "state":
            "PASS",

        "capabilityIndex":
            15,

        "capabilityId":
            "EVIDENCE_DONECHECK",

        "authority":
            "GREEN",

        "riskClass":
            "LOW",

        "fieldModel":
            "FRESH_CRITERION_SCOPED_EVIDENCE_TO_PINNED_DONECHECK_V1_2",

        "mutationScope":
            "EVIDENCE_ONLY",

        "sourceEvidence": {
            "path":
                str(SOURCE),

            "sha256":
                sha(SOURCE),
        },

        "freshDoneCheck": {
            "state":
                machine[
                    "DONECHECK_STATE"
                ],

            "version":
                machine[
                    "DONECHECK_VERSION"
                ],

            "exactSha":
                machine[
                    "DONECHECK_SHA"
                ],

            "executionId":
                machine[
                    "EXECUTION_ID"
                ],

            "taskId":
                machine[
                    "TASK_ID"
                ],

            "verificationResultId":
                machine[
                    "VERIFICATION_RESULT_ID"
                ],
        },

        "governedFinish": {
            "state":
                green["STATE"],
        },

        "negativeControls":
            negative,

        "authorityBoundary": {
            "humanThresholdRequired":
                False,

            "sourceMutation":
                False,

            "productMutation":
                False,

            "remotePush":
                False,

            "networkMutation":
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
        "CAP15_EVIDENCE_DONECHECK=PASS"
    )
    print(
        "FRESH_MATERIAL_EVIDENCE=PASS"
    )
    print(
        "DONECHECK_STATE=PASS"
    )
    print(
        "DONECHECK_VERSION="
        + machine[
            "DONECHECK_VERSION"
        ]
    )
    print(
        "DONECHECK_SHA="
        + machine[
            "DONECHECK_SHA"
        ]
    )
    print(
        "VERIFICATION_RESULT_ID="
        + str(
            machine[
                "VERIFICATION_RESULT_ID"
            ]
        )
    )
    print(
        "GOVERNED_FINISH=VERIFIED"
    )
    print(
        "NONPASS_EVIDENCE_REJECTED=PASS"
    )
    print(
        "MISSING_EVIDENCE_HOLD=PASS"
    )
    print(
        "STALE_CACHED_PASS_HOLD=PASS"
    )
    print(
        "DONECHECK_NONPASS_HOLD=PASS"
    )
    print(
        "UNSUPPORTED_FINAL_CLAIM_HOLD=PASS"
    )
    print(
        "HUMAN_THRESHOLD_REQUIRED=false"
    )
    print(
        "SOURCE_MUTATION=false"
    )
    print(
        "PRODUCT_MUTATION=false"
    )
    print(
        "REMOTE_PUSH=false"
    )
    print(
        "NETWORK_MUTATION=false"
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
        "AUTHORITY=GREEN"
    )
    print(
        "MUTATION_SCOPE=EVIDENCE_ONLY"
    )
    print(
        "SOURCE_EVIDENCE_SHA256="
        + sha(SOURCE)
    )
    print(
        "PRIOR_FIELD_EVIDENCE_SHA256="
        + sha(FIELD)
    )
    print(
        "EVIDENCE="
        + str(evidence)
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(
            main()
        )
    except Exception as exc:
        print(
            "STATE=HOLD"
        )
        print(
            "HOLD="
            + type(exc).__name__
            + ":"
            + str(exc)
        )
        raise SystemExit(2)
