#!/usr/bin/env python3
"""ENGÜRÜ Hybrid Handoff v1: fail-closed GitHub preflight (not OSi finalization)."""
import argparse
import json
import re
from pathlib import Path

SCHEMA = "enguru.mac-engineer.hybrid-handoff/v1"
MODES = {"GITHUB_FIRST", "OSI_FIRST", "HYBRID"}
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
HEX40 = re.compile(r"^[0-9a-fA-F]{40}$")
GATES = ("state", "claim", "evidence", "judgment", "nextAction")


def validate(data, *, mode="template"):
    errors = []
    if not isinstance(data, dict):
        return ["ROOT_NOT_OBJECT"]
    if data.get("schema") != SCHEMA:
        errors.append("SCHEMA_MISMATCH")
    if mode == "template":
        if data.get("state") != "PENDING" or data.get("verifiedFinish") != "HOLD":
            errors.append("TEMPLATE_PREMATURE_FINISH")
    if mode == "handoff":
        if not data.get("projectId") or not data.get("subproduct"):
            errors.append("PROJECT_IDENTITY_MISSING")
        if data.get("executionMode") not in MODES:
            errors.append("EXECUTION_MODE_INVALID")
        if not data.get("canonicalRepo") or not data.get("sourceRef"):
            errors.append("SOURCE_IDENTITY_MISSING")
        if not HEX40.fullmatch(str(data.get("sourceCommit") or "")):
            errors.append("SOURCE_COMMIT_INVALID")
        if not HEX64.fullmatch(str(data.get("artifactDigest") or "")):
            errors.append("ARTIFACT_DIGEST_INVALID")
    suzgec = data.get("suzgec")
    if not isinstance(suzgec, dict) or any(k not in suzgec for k in GATES):
        errors.append("SUZGEC_DECISION_SEQUENCE_MISSING")
        suzgec = {}
    if data.get("verifiedFinish") == "LOCKED":
        # GitHub is deliberately incapable of asserting field acceptance.
        errors.append("GITHUB_CANNOT_LOCK_OSI_VERIFIED_FINISH")
    if suzgec.get("judgment") == "PASS" and not suzgec.get("evidence"):
        errors.append("UNSUPPORTED_PASS")
    for name in ("testEvidence", "negativeEvidence"):
        if not isinstance(data.get(name), list):
            errors.append(name.upper() + "_INVALID")
    for name in ("humanAuthorityScope", "progressProjectBinding", "fieldReceipt"):
        if not isinstance(data.get(name), dict):
            errors.append(name.upper() + "_MISSING")
    if mode == "handoff" and data.get("fieldReceipt", {}).get("osiFieldState") != "UNVERIFIED":
        errors.append("GITHUB_FIELD_ATTESTATION_FORBIDDEN")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--mode", choices=("template", "handoff"), default="template")
    args = parser.parse_args()
    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print("STATE=HOLD\nREASON=UNREADABLE_JSON:" + type(exc).__name__)
        return 2
    errors = validate(data, mode=args.mode)
    if errors:
        print("STATE=HOLD\nREASON=" + ",".join(errors))
        return 1
    print("STATE=GITHUB_PREFLIGHT_PASS\nFIELD_STATE=UNVERIFIED\nverifiedFinish=HOLD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
