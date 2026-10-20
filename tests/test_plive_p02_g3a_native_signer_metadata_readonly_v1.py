"""Offline G3-A metadata qualification adversarial tests. No signer execution."""
import hashlib
import json
import plistlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from plive_p02_g3a_native_signer_metadata_readonly_v1 import (
    POLICY_REL, DECISION_REL, POLICY_SHA, DECISION_SHA, qualify, parse_signed_entitlements,
)


class NativeSignerQualificationTests(unittest.TestCase):
    def test_empty_root_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            x = qualify(Path(d), None)
            self.assertEqual(x["state"], "HOLD_G3A_NATIVE_AUTHORITY")
            self.assertEqual(x["checks"]["policy"], "HOLD_PIN_OR_FILE")
            self.assertFalse(x["issuerQualified"])

    def test_missing_candidate_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            x = qualify(Path(d), Path(d) / "absent")
            self.assertFalse(x["grantIssued"])
            self.assertEqual(x["canonicalWrites"], 0)
            self.assertEqual(x["keychainOperations"], 0)

    def test_candidate_never_signs(self):
        with tempfile.TemporaryDirectory() as d:
            x = qualify(Path(d), Path(d) / "absent")
            self.assertEqual(x["signatureOperations"], 0)
            self.assertEqual(x["verifiedFinish"], "HOLD")

    def test_policy_pin_is_not_issuer(self):
        self.assertEqual(len(POLICY_SHA), 64)
        self.assertEqual(len(DECISION_SHA), 64)
        with tempfile.TemporaryDirectory() as d:
            x = qualify(Path(d), None)
            self.assertFalse(x["issuerQualified"])

    def test_no_external_commands_on_invalid_policy(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("plive_p02_g3a_native_signer_metadata_readonly_v1.command",
                       side_effect=AssertionError("command unexpectedly called")):
                qualify(Path(d), Path(d) / "absent")

    def test_signed_entitlements_stdout_and_stderr(self):
        sample = {"com.apple.application-identifier": "TEAM123456.local.enguru.app",
                  "keychain-access-groups": ["TEAM123456.local.enguru.app"]}
        xml = plistlib.dumps(sample, fmt=plistlib.FMT_XML)
        bplist = plistlib.dumps(sample, fmt=plistlib.FMT_BINARY)
        for name, capture in (
            ("stdout_xml", {"returnCode": 0, "_stdoutBytes": xml, "_stderrBytes": b""}),
            ("stderr_xml", {"returnCode": 0, "_stdoutBytes": b"", "_stderrBytes": xml}),
            ("stderr_prefix", {"returnCode": 0, "_stdoutBytes": b"",
                                "_stderrBytes": b"codesign: displaying entitlements\\n"+xml}),
            ("stdout_binary", {"returnCode": 0, "_stdoutBytes": bplist,
                               "_stderrBytes": b""}),
        ):
            with self.subTest(name=name):
                out = parse_signed_entitlements(capture)
                self.assertEqual(out["state"], "PASS_EMBEDDED_ENTITLEMENTS_PARSED_ONLY")
                self.assertTrue(out["appIdentifierPresent"])
                self.assertEqual(out["keychainAccessGroupCount"], 1)

    def test_entitlements_parse_fails_closed(self):
        bad_groups = plistlib.dumps({"keychain-access-groups": "wrong-type"})
        for capture in (
            {"returnCode": 1, "_stdoutBytes": b"", "_stderrBytes": b""},
            {"returnCode": 0, "_stdoutBytes": b"", "_stderrBytes": b""},
            {"returnCode": 0, "_stdoutBytes": b"not a plist", "_stderrBytes": b""},
            {"returnCode": 0, "_stdoutBytes": bad_groups, "_stderrBytes": b""},
        ):
            with self.subTest(capture=capture):
                self.assertTrue(parse_signed_entitlements(capture)["state"].startswith("HOLD"))

    def test_qualify_requests_xml_from_actually_signed_binary(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            policy = root / POLICY_REL
            decision = root / DECISION_REL
            policy.parent.mkdir(parents=True, exist_ok=True)
            policy.write_text("fixture")
            decision.write_text(json.dumps({
                "policyCreatesNoGrant": True,
                "scope": {"grantIssued": False, "writerApproved": False},
            }))
            signer = root / "signed-helper"
            signer.write_bytes(b"test-only-no-signature")
            xml = plistlib.dumps({"com.apple.application-identifier":
                                    "TEAM123456.local.enguru.test"})
            captured = []
            def simulated_command(args):
                captured.append(args)
                return {"returnCode": 0, "stdout": "",
                        "stderrSha256": "0"*64,
                        "_stdoutBytes": xml, "_stderrBytes": b""}
            def pin_or_file(p):
                if p == policy:
                    return POLICY_SHA
                if p == decision:
                    return DECISION_SHA
                return hashlib.sha256(p.read_bytes()).hexdigest()
            with patch("plive_p02_g3a_native_signer_metadata_readonly_v1.sha",
                       side_effect=pin_or_file), patch(
                       "plive_p02_g3a_native_signer_metadata_readonly_v1.command",
                       side_effect=simulated_command):
                outcome = qualify(root, signer)
            self.assertEqual(captured[-1], [
                "/usr/bin/codesign", "--display", "--entitlements", "-",
                "--xml", str(signer),
            ])
            self.assertTrue(outcome["checks"]["entitlementsRead"])
            self.assertFalse(outcome["issuerQualified"])
            self.assertEqual(outcome["state"], "HOLD_G3A_NATIVE_AUTHORITY")

    def test_policy_paths_scoped(self):
        self.assertIn("plive-p02-user-screen/", POLICY_REL)
        self.assertIn("plive-p02-user-screen/", DECISION_REL)


if __name__ == "__main__":
    unittest.main()
