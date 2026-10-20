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
                "stdout": completed.stdout.decode("utf-8", "replace")[:18000],
                "_stdoutBytes": completed.stdout[:65536],
                "_stderrBytes": completed.stderr[:65536]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"returnCode": None, "error": type(exc).__name__}



def parse_signed_entitlements(command_result: dict) -> dict:
    """Inspect the actual signed-binary plist; codesign may use either stream."""
    if command_result.get("returnCode") != 0:
        return {"state": "HOLD_CODESIGN_COMMAND"}
    for key in ("_stdoutBytes", "_stderrBytes"):
        raw = command_result.get(key, b"")
        if not isinstance(raw, bytes) or len(raw) > 65536:
            continue
        candidates = [raw]
        xml_start = raw.find(b"<?xml")
        if xml_start == -1:
            xml_start = raw.find(b"<plist")
        if xml_start > 0:
            candidates.append(raw[xml_start:])
        for blob in candidates:
            try:
                parsed = plistlib.loads(blob)
            except (ValueError, TypeError, plistlib.InvalidFileException, OverflowError):
                continue
            if type(parsed) is not dict or any(type(k) is not str for k in parsed):
                return {"state": "HOLD_ENTITLEMENTS_NOT_DICTIONARY"}
            groups = parsed.get("keychain-access-groups", [])
            if type(groups) is not list or any(type(x) is not str for x in groups):
                return {"state": "HOLD_ENTITLEMENT_GROUPS_INVALID"}
            app_id = parsed.get("com.apple.application-identifier",
                                parsed.get("application-identifier"))
            if app_id is not None and type(app_id) is not str:
                return {"state": "HOLD_ENTITLEMENT_APP_ID_INVALID"}
            return {"state": "PASS_EMBEDDED_ENTITLEMENTS_PARSED_ONLY",
                    "entitlementNames": sorted(parsed),
                    "appIdentifierPresent": bool(app_id),
                    "keychainAccessGroupCount": len(groups)}
    return {"state": "HOLD_EMBEDDED_ENTITLEMENTS_UNPARSEABLE"}


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
    # Apple TN3125: --xml requests a plist rather than human-readable DER output.
    # Inspect the signed binary itself; no source .entitlements assumptions.
    ent = command(["/usr/bin/codesign", "--display", "--entitlements", "-", "--xml", str(candidate)])
    ent_inspection = parse_signed_entitlements(ent)
    report["checks"]["embeddedEntitlementsInspection"] = ent_inspection
    report["checks"]["entitlementsRead"] = (
        ent_inspection["state"] == "PASS_EMBEDDED_ENTITLEMENTS_PARSED_ONLY")
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
    # Exit status is never success when the CLI has not established native issuer
    # qualification. Successful policy-source checks are evidence only.
    return 0 if result.get("issuerQualified") is True and result.get("state") == "PASS_G3A_NATIVE_AUTHORITY" else 50


if __name__ == "__main__":
    raise SystemExit(main())
