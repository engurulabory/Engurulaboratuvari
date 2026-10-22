#!/usr/bin/env python3
"""Read-only ENGÜRÜ management handoff projection (not an acceptance verifier)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

SCHEMA = "enguru.management.handoff/v1"
IDS = ("F01", "F02", "F03", "F04", "F05", "F06")
OPEN_STATES = {"OPEN", "HOLD_AUTHORITY", "HOLD_EVIDENCE", "BLOCKED"}
STATES = OPEN_STATES | {"PASS_CLOSED"}


class HandoffError(ValueError):
    pass


def integer(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise HandoffError(f"{name}: nonnegative integer required")
    return value


def project(handoff: dict) -> dict:
    if not isinstance(handoff, dict) or handoff.get("schema") != SCHEMA:
        raise HandoffError("unsupported handoff schema")
    source = handoff.get("source")
    if not isinstance(source, dict) or not isinstance(source.get("report"), str) or not source["report"].strip():
        raise HandoffError("source.report required")
    sha = source.get("sha256")
    if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha.lower()):
        raise HandoffError("source.sha256 requires 64 hex characters")

    goals = handoff.get("goals")
    if not isinstance(goals, dict):
        raise HandoffError("goals required")
    accepted = {}
    for name in ("H1", "H2", "H3"):
        item = goals.get(name)
        if not isinstance(item, dict):
            raise HandoffError(f"{name} required")
        passed = integer(item.get("passed"), f"{name}.passed")
        total = integer(item.get("total"), f"{name}.total")
        if total != 4 or passed > 4:
            raise HandoffError(f"{name} requires an exact 4-criterion boundary")
        accepted[name] = passed
    for name in ("native", "verifiedFinish"):
        if goals.get(name) not in ("PASS", "HOLD", "BLOCKED"):
            raise HandoffError(f"{name}: PASS/HOLD/BLOCKED required")

    blockers = handoff.get("blockers")
    if not isinstance(blockers, list) or len(blockers) != 6:
        raise HandoffError("exactly F01–F06 records required")
    by_id = {}
    for item in blockers:
        if not isinstance(item, dict) or item.get("id") not in IDS or item["id"] in by_id:
            raise HandoffError("unknown or duplicate blocker")
        status = item.get("status")
        if status not in STATES:
            raise HandoffError(f"{item['id']}: unknown state")
        if status == "PASS_CLOSED":
            receipt = item.get("acceptanceReceipt")
            if not isinstance(receipt, str) or not receipt.strip():
                raise HandoffError(f"{item['id']}: closure receipt required")
        by_id[item["id"]] = item
    if set(by_id) != set(IDS):
        raise HandoffError("missing F01–F06")
    for blocker, goal in (("F02", "H1"), ("F03", "H2"), ("F04", "H3")):
        if by_id[blocker]["status"] == "PASS_CLOSED" and accepted[goal] != 4:
            raise HandoffError(f"{blocker}: cannot close with {goal} below 4/4")
    if by_id["F05"]["status"] == "PASS_CLOSED" and goals["native"] != "PASS":
        raise HandoffError("F05 closure requires Native PASS")
    if by_id["F06"]["status"] == "PASS_CLOSED":
        if sum(accepted.values()) != 12 or goals["native"] != "PASS" or goals["verifiedFinish"] != "PASS":
            raise HandoffError("F06 closure requires all final acceptance prerequisites")
        if any(by_id[x]["status"] != "PASS_CLOSED" for x in IDS[:-1]):
            raise HandoffError("F06 closure requires F01–F05 closed")

    closed = sum(by_id[x]["status"] == "PASS_CLOSED" for x in IDS)
    accepted_count = sum(accepted.values())
    open_ids = [x for x in IDS if by_id[x]["status"] != "PASS_CLOSED"]
    primary = open_ids[0] if open_ids else None
    support = "F05_SCOPE_AND_SOURCE_PREPARATION" if primary not in (None, "F05", "F06") and "F05" in open_ids else None
    done = not open_ids and accepted_count == 12 and goals["native"] == "PASS" and goals["verifiedFinish"] == "PASS"
    return {
        "state": "PROJECTION_ONLY_NOT_AUTHORITY",
        "sourceReport": source["report"],
        "sourceClaimedSha256": sha.lower(),
        "canonicalOrOsiWrites": 0,
        "designMethodTarget": "100/100_NOT_FIELD_ACCEPTED",
        "officialAccepted": {**accepted, "sum": accepted_count, "total": 12, "percent": round(100 * accepted_count / 12, 2)},
        "blockers": {"closed": closed, "total": 6, "open": open_ids, "closedPercent": round(100 * closed / 6, 2)},
        "nextWork": {"primary": primary, "independentSupport": support},
        "native": goals["native"],
        "verifiedFinish": goals["verifiedFinish"],
        "terminalProjection": "READY_FOR_INDEPENDENT_FINAL_ACCEPTANCE" if done else "HOLD_PENDING_AUTHORIZED_ACCEPTANCE",
        "note": "Numbers project supplied handoff; verify authority, source, signature and OSi independently.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        record = json.loads(args.input.read_text(encoding="utf-8"))
        output = project(record)
    except (OSError, ValueError, TypeError) as error:
        print(f"STATE=HOLD_INVALID_HANDOFF {error}", file=sys.stderr)
        return 50
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
