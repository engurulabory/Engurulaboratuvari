#!/usr/bin/env python3
"""G3-A native signer qualification: READ-ONLY metadata, no signing or Keychain access.
No entitlement guessing, issuer enrollment, grant issuance, or canonical mutation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess

POLICY_SHA = "48f46754c4a94e28d66e7e6a272284afae60791d631f556d6826f6775744fb9e"
DECISION_SHA = "ef65263a26e48193ac36f8f3045ff69cc6e294322d3fdbc85b4c34eaaf1765a2"
ROOT_REL = "Enguru/Projects/Engurulaboratuvari"
POLICY_REL = "governance/plive-p02-user-screen/ENGURU_PLIVE_P02_TEK_INSAN_GUVEN_G3_POLITIKASI_V1.md"
DECISION_REL = "governance/plive-p02-user-screen/ENGURU_PLIVE_P02_TEK_INSAN_POLITIKA_KARARI_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(argv: list[str]) -> dict:
    try:
        completed = subprocess.run(argv, capture_output=True, timeout=12, check=False)
        return {"returnCode": completed.returncode,
                "stdoutSha256": hashlib.sha256(completed.stdout).hexdigest(),
                "stderrSha256": hashlib.sha256(completed.stderr).hexdigest(),
                "stdout": completed.stdout.decode("utf-8", "replace")[:18000]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"returnCode": None, "error": type(exc).__name__}


def qualify(root: Path, candidate: Path | None) -> dict:
    report = {"schema": "enguru.plive.p02.g3a.readonly-signing-metadata/v1",
              "state": "HOLD_G3A_NATIVE_AUTHORITY",
              "policySha256": POLICY_SHA, "canonicalWrites": 0,
              "keychainOperations": 0, "signatureOperations": 0,
              "grantIssued": False, "issuerQualified": False,
              "verifiedFinish": "HOLD", "checks": {}}
    for name, rel, expected in (
        ("policy", POLICY_REL, POLICY_SHA),
        ("decision", DECISION_REL, DECISION_SHA),
    ):
        path = root / rel
        report["checks"][name] = ("PASS_PIN" if path.is_file() and
                                   not path.is_symlink() and sha(path) == expected
                                   else "HOLD_PIN_OR_FILE")
    if "HOLD_PIN_OR_FILE" in report["checks"].values():
        return report

    decision = json.loads((root / DECISION_REL).read_text(encoding="utf-8"))
    report["checks"]["noGrantFromPolicy"] = bool(
        decision.get("policyCreatesNoGrant") is True
        and decision.get("scope", {}).get("grantIssued") is False
        and decision.get("scope", {}).get("writerApproved") is False)
    if not report["checks"]["noGrantFromPolicy"]:
        return report
    if candidate is None:
        report["checks"]["candidate"] = "HOLD_NO_EXACT_SIGNER_PATH"
        return report
    if candidate.is_symlink() or not candidate.is_file():
        report["checks"]["candidate"] = "HOLD_NOT_REGULAR_FILE"
        return report
    report["checks"]["candidate"] = {"path": str(candidate),
                                      "sha256": sha(candidate)}
    # Codesign metadata is untrusted unless it is verified and matched with
    # expected canonical bundle ID, team ID, and provisioning evidence.
    cs = command(["/usr/bin/codesign", "--verify", "--strict", "--verbose=2", str(candidate)])
    report["checks"]["codesignIntegrity"] = ("PASS" if cs["returnCode"] == 0 else "HOLD")
    details = command(["/usr/bin/codesign", "-d", "--verbose=4", str(candidate)])
    report["checks"]["codesignMetadataCaptured"] = details["returnCode"] == 0
    report["checks"]["codesignMetadataOutputSha256"] = details.get("stderrSha256")
    # Metadata content is intentionally not printed: avoid paths/account IDs
    # and avoid asserting app identity from a signature alone.
    ent = command(["/usr/bin/codesign", "-d", "--entitlements", ":-", str(candidate)])
    report["checks"]["entitlementsRead"] = ent["returnCode"] == 0
    if ent["returnCode"] == 0:
        try:
            parsed = plistlib.loads(ent["stdout"].encode("utf-8"))
            names = sorted(k for k in parsed if isinstance(k, str))
            report["checks"]["entitlementNames"] = names
        except (ValueError, TypeError, plistlib.InvalidFileException):
            report["checks"]["entitlementNames"] = "HOLD_PARSE"
    report["checks"]["expectedBundleAndTeamBinding"] = "HOLD_NOT_ATTESTED"
    report["checks"]["provisioningAndAccessGroups"] = "HOLD_NOT_ATTESTED"
    report["checks"]["ownerPresenceAndKeyUse"] = "HOLD_NOT_ATTESTED"
    report["checks"]["previousMinus34018Resolved"] = "HOLD_NOT_ATTESTED"
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, default=None)
    args = parser.parse_args()
    root = Path.home() / ROOT_REL
    result = qualify(root, args.candidate)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["checks"].get("policy") == "PASS_PIN" and result["checks"].get("decision") == "PASS_PIN" else 50


if __name__ == "__main__":
    raise SystemExit(main())
