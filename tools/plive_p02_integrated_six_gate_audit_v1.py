#!/usr/bin/env python3
"""ENGURU P02 six-gate engineering audit. Candidate evidence only; NEVER native authority.

No Keychain, codesign, signing, git, canonical state, or P02 writer operations.
Human/field attestation MUST be resolved by an independent native acceptance path.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

GATES = ("G3A_SIGNER", "G3B_GRANT", "G3C_DURABLE_WRITER",
         "G3D_FIRST_NATIVE_ITEM", "P02_FIELD_ACCEPTANCE", "HUMAN_VERIFIED_FINISH")
DEPS = ((), (0,), (0, 1), (0, 1, 2), (3,), (4,))
SHA = re.compile(r"^[0-9a-f]{64}$")
SCHEMA = "enguru.p02.six-gate.engineering-evidence/v1"


def audit(raw: bytes, *, expected_manifest_sha256: str | None = None) -> dict:
    """Verify input shape and immutable source digests. No user input can grant authority."""
    report = {"schema": "enguru.p02.six-gate.integrated-audit/v1",
              "inputSha256": hashlib.sha256(raw).hexdigest(),
              "nativeAuthority": "HOLD", "officialP02": "HOLD",
              "verifiedFinish": "HOLD", "canonicalWrites": 0,
              "signingOperations": 0, "keychainOperations": 0,
              "gates": [], "state": "HOLD_INVALID_INPUT"}
    try:
        if len(raw) > 1024 * 1024:
            raise ValueError("OVERSIZED")
        if expected_manifest_sha256 is not None and (
                not isinstance(expected_manifest_sha256, str) or
                not SHA.fullmatch(expected_manifest_sha256) or
                report["inputSha256"] != expected_manifest_sha256):
            raise ValueError("MANIFEST_PIN")
        def unique_pairs(pairs):
            result = {}
            for k, v in pairs:
                if k in result:
                    raise ValueError("DUPLICATE_KEY")
                result[k] = v
            return result
        value = json.loads(raw, object_pairs_hook=unique_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE")))
        if not isinstance(value, dict) or set(value) != {"schema", "gates", "policySha256", "localHead"}:
            raise ValueError("SCHEMA_FIELDS")
        if value["schema"] != SCHEMA or not isinstance(value["gates"], dict):
            raise ValueError("SCHEMA")
        if set(value["gates"]) != set(GATES):
            raise ValueError("GATE_SET")
        if not isinstance(value["policySha256"], str) or not SHA.fullmatch(value["policySha256"]):
            raise ValueError("POLICY_HASH")
        if not isinstance(value["localHead"], str) or not re.fullmatch(r"[0-9a-f]{40}", value["localHead"]):
            raise ValueError("LOCAL_HEAD")
        for index, name in enumerate(GATES):
            entry = value["gates"][name]
            if not isinstance(entry, dict) or set(entry) != {"engineeringEvidenceSha256", "reviewed"}:
                raise ValueError("GATE_FIELDS")
            if type(entry["reviewed"]) is not bool:
                raise ValueError("REVIEWED_TYPE")
            digest = entry["engineeringEvidenceSha256"]
            if digest is not None and (not isinstance(digest, str) or not SHA.fullmatch(digest)):
                raise ValueError("EVIDENCE_DIGEST")
            candidate = "REVIEW_CANDIDATE" if digest is not None and entry["reviewed"] else "HOLD_EVIDENCE"
            report["gates"].append({
                "name": name, "dependsOn": [GATES[i] for i in DEPS[index]],
                "engineering": candidate, "nativeAcceptance": "HOLD_UNVERIFIED_FIELD_AUTHORITY"
            })
        report["state"] = "PASS_BOUNDED_ENGINEERING_AUDIT__OFFICIAL_HOLD"
    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        report["reason"] = str(exc)
        report["gates"] = [{"name":name, "engineering":"HOLD_INPUT", "nativeAcceptance":"HOLD"}
                           for name in GATES]
    return report


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--sha256", help="External independently pinned evidence digest")
    a = p.parse_args()
    if a.evidence.is_symlink() or not a.evidence.is_file():
        print(json.dumps({"state":"HOLD_SOURCE_MISSING_OR_SYMLINK"}))
        return 50
    result = audit(a.evidence.read_bytes(), expected_manifest_sha256=a.sha256)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["state"].startswith("PASS_BOUNDED") else 50


if __name__ == "__main__":
    raise SystemExit(main())
