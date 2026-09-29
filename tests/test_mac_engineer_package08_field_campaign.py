#!/usr/bin/env python3

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LEDGER = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "CAPABILITY_FIELD_VERIFICATION_LEDGER_V1.json"
)

d = json.loads(
    LEDGER.read_text(
        encoding="utf-8"
    )
)

checks = {
    "CAPABILITY_COUNT_19":
        d["capabilityCount"] == 19
        and len(d["capabilities"]) == 19,

    "INDEX_1_TO_19":
        [
            x["index"]
            for x in d["capabilities"]
        ]
        == list(range(1, 20)),

    "UNIQUE_IDS":
        len({
            x["capabilityId"]
            for x in d["capabilities"]
        }) == 19,

    "ZERO_TOLERANCE_ZERO":
        all(
            value == 0
            for value in
            d["zeroTolerance"].values()
        ),

    "FIELD_COUNT_CONSISTENT":
        d["fieldVerifiedCount"]
        == sum(
            1
            for x in d["capabilities"]
            if x["fieldState"]
            == "FIELD_VERIFIED"
        ),
}

cap01 = d["capabilities"][0]

if d["fieldVerifiedCount"] == 1:

    evidence = (
        cap01.get("evidence")
        or {}
    )

    evidence_path = Path(
        str(
            evidence.get("path")
            or ""
        )
    )

    evidence_exists = (
        evidence_path.is_file()
    )

    digest_match = False
    donecheck_pass = False
    evidence_state_pass = False

    if evidence_exists:
        actual = hashlib.sha256(
            evidence_path.read_bytes()
        ).hexdigest()

        digest_match = (
            actual
            == evidence.get("sha256")
        )

        payload = json.loads(
            evidence_path.read_text(
                encoding="utf-8"
            )
        )

        evidence_state_pass = (
            payload.get("state")
            == "PASS"
        )

        donecheck_pass = (
            (
                payload.get(
                    "doneCheck"
                )
                or {}
            ).get("state")
            == "PASS"
        )

    checks.update({
        "CAP01_EXACT_ID":
            cap01["capabilityId"]
            == "CURRENT_TECHNICAL_TRUTH_READ",

        "CAP01_FIELD_VERIFIED":
            cap01["fieldState"]
            == "FIELD_VERIFIED",

        "CAP01_ALL_ACCEPTANCE_TRUE":
            all(
                value is True
                for value in
                cap01[
                    "acceptance"
                ].values()
            ),

        "CAP01_EVIDENCE_EXISTS":
            evidence_exists,

        "CAP01_EVIDENCE_DIGEST_MATCH":
            digest_match,

        "CAP01_EVIDENCE_STATE_PASS":
            evidence_state_pass,

        "CAP01_DONECHECK_PASS":
            donecheck_pass,
    })

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

print(
    "CHECKS="
    + str(passed)
    + "_OF_"
    + str(len(checks))
    + "_PASS"
)

if passed != len(checks):
    raise SystemExit(20)

print("STATE=PASS")
print(
    "CLAIM=PACKAGE08_FIELD_LEDGER_NATIVE_TEST_PASS"
)
