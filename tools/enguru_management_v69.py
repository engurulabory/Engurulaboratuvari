#!/usr/bin/env python3
"""ENGÜRÜ Management V6.9: read-only governed worklist evaluator.
No GitHub write, task execution, or human acceptance authority.
"""
import argparse
import hashlib
import json
from pathlib import Path

STATES = {"READY", "HOLD", "PASS_EVIDENCE", "ACCEPTED", "PAUSED"}
REQUIRED = {"task_id", "goal", "state", "dependencies", "source_ref", "source_sha256", "evidence", "verifier", "authority"}
HEX = set("0123456789abcdef")


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def evaluate(doc):
    tasks = doc.get("tasks") if isinstance(doc, dict) else None
    if not isinstance(tasks, list):
        return {"state": "HOLD_GUVENLI_DUR", "reason": "INVALID_WORKLIST"}
    ids = set()
    for t in tasks:
        if not isinstance(t, dict) or not REQUIRED.issubset(t):
            return {"state": "HOLD_GUVENLI_DUR", "reason": "MISSING_REQUIRED_FIELD"}
        ident = t["task_id"]
        if not isinstance(ident, str) or not ident or ident in ids:
            return {"state": "HOLD_GUVENLI_DUR", "reason": "DUPLICATE_OR_INVALID_ID"}
        ids.add(ident)
        if t["state"] not in STATES or not isinstance(t["dependencies"], list):
            return {"state": "HOLD_GUVENLI_DUR", "reason": "INVALID_STATE_OR_DEPENDENCY"}
        if not isinstance(t["source_sha256"], str) or len(t["source_sha256"]) != 64 or set(t["source_sha256"]) - HEX:
            return {"state": "HOLD_GUVENLI_DUR", "reason": "SOURCE_DIGEST_REQUIRED"}
    index = {t["task_id"]: t for t in tasks}
    if any(not isinstance(d, str) or d not in index or d == t["task_id"] for t in tasks for d in t["dependencies"]):
        return {"state": "HOLD_GUVENLI_DUR", "reason": "INVALID_DEPENDENCY"}
    visiting, visited = set(), set()
    def visit(key):
        if key in visiting:
            raise ValueError("DEPENDENCY_CYCLE")
        if key in visited:
            return
        visiting.add(key)
        for dep in index[key]["dependencies"]:
            visit(dep)
        visiting.remove(key)
        visited.add(key)
    try:
        for ident in ids:
            visit(ident)
    except ValueError:
        return {"state": "HOLD_GUVENLI_DUR", "reason": "DEPENDENCY_CYCLE"}
    accepted = set()
    reasons = {}
    for t in tasks:
        tid = t["task_id"]
        if t["state"] == "ACCEPTED":
            if not all(isinstance(t[k], dict) and t[k].get("verified") is True for k in ("evidence", "verifier", "authority")):
                reasons[tid] = "ACCEPTANCE_EVIDENCE_MISSING"
            elif t["verifier"].get("identity") == t.get("executor_id") or not t["verifier"].get("identity"):
                reasons[tid] = "INDEPENDENCE_NOT_ATTESTED"
            elif any(index[d]["state"] != "ACCEPTED" for d in t["dependencies"]):
                reasons[tid] = "DEPENDENCY_NOT_ACCEPTED"
            else:
                accepted.add(tid)
        elif t["state"] == "PASS_EVIDENCE":
            reasons[tid] = "AUTHORITY_ACCEPTANCE_PENDING"
        elif t["state"] == "PAUSED":
            reasons[tid] = "PAUSED_BY_MANAGEMENT"
        else:
            reasons[tid] = "OPEN_OR_HOLD"
    # This report is a claim about supplied records, not authentication of those records.
    # No ACCEPTED counter is an independently verified GitHub/OSi authority receipt.
    ready = sorted(t["task_id"] for t in tasks if t["state"] == "READY" and all(d in accepted for d in t["dependencies"]))
    return {
        "state": "MANAGEMENT_REVIEW_ONLY",
        "task_count": len(tasks),
        "record_declared_accepted": len(accepted),
        "record_declared_open": len(tasks) - len(accepted),
        "ready_candidates": ready,
        "open_reasons": reasons,
        "evidence_authority": "UNVERIFIED_INPUT_RECORDS",
        "github_writes": 0,
        "human_threshold": "OWNER_RESERVED",
        "input_sha256_canonical": digest(doc),
        "next_action": "INDEPENDENT_SOURCE_EVIDENCE_AUTHORITY_RECONCILIATION",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worklist", required=True)
    args = parser.parse_args()
    path = Path(args.worklist)
    if path.is_symlink() or not path.is_file():
        print(json.dumps({"state": "HOLD_GUVENLI_DUR", "reason": "SOURCE_FILE_REQUIRED"}))
        return 50
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        print(json.dumps({"state": "HOLD_GUVENLI_DUR", "reason": "INVALID_SOURCE_JSON"}))
        return 50
    result = evaluate(doc)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 50 if result["state"] == "HOLD_GUVENLI_DUR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
