#!/usr/bin/env python3
"""Read-only pre-send evidence coverage gate; never grants ENGURU acceptance."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = "enguru.batch.evidence/v2"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^B[0-9]{2}-[0-9]{2}$")


class EvidenceError(ValueError):
    """Fail-closed invalid source/packet."""


def sha(value: object, regex: re.Pattern[str]) -> bool:
    return isinstance(value, str) and regex.fullmatch(value) is not None


def ledger_checks(ledger: dict) -> dict:
    if not isinstance(ledger, dict) or ledger.get("total_units") != 100:
        raise EvidenceError("ledger requires 100 original controls")
    checks = ledger.get("checks")
    if not isinstance(checks, list) or len(checks) != 100:
        raise EvidenceError("ledger must carry exactly 100 checks")
    ids = {}
    for row in checks:
        if not isinstance(row, dict) or not ID.fullmatch(str(row.get("id", ""))):
            raise EvidenceError("invalid original control ID")
        if row["id"] in ids or row.get("state") not in ("PASS_EVIDENCE", "HOLD"):
            raise EvidenceError("duplicate ID or invalid state")
        if not isinstance(row.get("name"), str) or not row["name"].strip():
            raise EvidenceError("original condition is required")
        ids[row["id"]] = row
    accepted = sum(row["state"] == "PASS_EVIDENCE" for row in checks)
    if (type(ledger.get("verified_units")) is not int or
        type(ledger.get("remaining_units")) is not int or
        accepted != ledger["verified_units"] or
        ledger["remaining_units"] != 100 - accepted):
        raise EvidenceError("original ledger counter invariant mismatch")
    return ids


def evaluate(ledger: dict, packet: dict) -> dict:
    originals = ledger_checks(ledger)
    if not isinstance(packet, dict) or packet.get("schema") != SCHEMA:
        raise EvidenceError("unsupported batch packet schema")
    if (type(packet.get("baseline")) is not int or
        packet["baseline"] != ledger["verified_units"]):
        raise EvidenceError("stale baseline")
    if packet.get("verified_finish") is True or packet.get("official_acceptance") in ("PASS", "PASS_EVIDENCE"):
        raise EvidenceError("producer cannot claim official Verified Finish or acceptance")
    items = packet.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= 10:
        raise EvidenceError("expected 1..10 original control items")
    ids = [x.get("id") if isinstance(x, dict) else None for x in items]
    if len(set(ids)) != len(ids):
        raise EvidenceError("duplicate batch candidate")
    result = []
    for item in items:
        if not isinstance(item, dict):
            raise EvidenceError("candidate must be an object")
        cid = item.get("id")
        if cid not in originals:
            raise EvidenceError(f"unknown original control: {cid}")
        original = originals[cid]
        if original["state"] != "HOLD":
            raise EvidenceError(f"already accepted original control: {cid}")
        if item.get("original_condition") != original["name"]:
            raise EvidenceError(f"original condition mismatch: {cid}")
        if item.get("claim") in ("PASS_EVIDENCE", "VERIFIED_FINISH", "BITTI_DUR"):
            raise EvidenceError(f"unearned authority claim: {cid}")
        missing = []
        if not isinstance(item.get("real_execution"), str) or not item["real_execution"].strip():
            missing.append("REAL_EXECUTION")
        if not sha(item.get("source_head"), HEX40):
            missing.append("SOURCE_HEAD_SHA")
        if not sha(item.get("evidence_sha256"), HEX64):
            missing.append("EVIDENCE_SHA")
        for label in ("positive_test", "negative_test"):
            test = item.get(label)
            if (not isinstance(test, dict) or test.get("state") != "PASS" or
                not sha(test.get("receipt_sha256"), HEX64)):
                missing.append(label.upper() + "_RECEIPT")
        owner = item.get("owner")
        if not isinstance(owner, dict) or type(owner.get("required")) is not bool:
            missing.append("OWNER_AUTHORITY_CLASSIFICATION")
        elif owner["required"]:
            if owner.get("state") != "APPROVED" or not sha(owner.get("receipt_sha256"), HEX64):
                missing.append("OWNER_APPROVED_SCOPE_RECEIPT")
        elif owner.get("state") != "NOT_REQUIRED":
            missing.append("OWNER_NOT_REQUIRED_SCOPE")
        result.append({"id": cid,
                       "status": "READY_FOR_INDEPENDENT_MANAGER_REVIEW" if not missing else "HOLD_EVIDENCE",
                       "missing": missing})
    ready = sum(x["status"] == "READY_FOR_INDEPENDENT_MANAGER_REVIEW" for x in result)
    return {
        "state": "PRE_SEND_STRUCTURAL_CHECK_ONLY_NOT_AUTHORITY",
        "baseline": ledger["verified_units"],
        "candidates": len(items),
        "structurally_ready": ready,
        "needs_completion": len(items) - ready,
        "structural_coverage_percent": round(100 * ready / len(items), 2),
        "official_pass_added": 0,
        "items": result,
        "next": "MANAGEMENT_INDEPENDENT_SOURCE_TEST_OWNER_REVIEW",
        "warning": "SHA format and receipt fields are claims, not independent file/hash/owner verification.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--packet", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
        report = evaluate(ledger, packet)
    except (OSError, ValueError, TypeError) as error:
        print(f"STATE=HOLD_INVALID_EVIDENCE {error}", file=sys.stderr)
        return 50
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
