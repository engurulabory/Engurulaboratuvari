"""Adversarial checks for G3 verifier candidate; no canonical or Keychain writes."""
import base64
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from plive_p02_g3_scoped_grant_verify_v1 import (
    POLICY_SHA256, canonical, exact_json, inspect, verify, load_pinned_trust_record,
)

NOW = "2026-10-20T12:00:00Z"
GOOD = {
    "schema": "enguru.plive.p02.scoped-grant/v1",
    "projectId": "ENGURU_PLIVE_P02_USER_SCREEN",
    "itemId": "P02.S01.01",
    "action": "P02_ITEM_PASS",
    "head": "a"*40,
    "preimageSha256": "b"*64,
    "evidenceSha256": "c"*64,
    "approvalSha256": "d"*64,
    "issuerId": "local-issuer-1",
    "keyId": "local-key-1",
    "nonce": "f"*32,
    "issuedAt": "2026-10-20T11:00:00Z",
    "expiresAt": "2026-10-20T13:00:00Z",
    "policySha256": POLICY_SHA256
}
TRUST = {"issuerId": "local-issuer-1", "keyId": "local-key-1",
         "policySha256": POLICY_SHA256, "status": "ACTIVE",
         "revocationChecked": True}
EXPECTED = {k: GOOD[k] for k in ("head", "preimageSha256", "evidenceSha256", "approvalSha256")}


class ScopedGrantNegativeTests(unittest.TestCase):
    def check_hold(self, change=None, trusted=None, nonces=frozenset(), observed_at=NOW):
        grant = dict(GOOD)
        if change:
            grant.update(change)
        result = inspect(grant, trusted=trusted or TRUST, expected=EXPECTED,
                         observed_at=observed_at, consumed_nonces=nonces)
        self.assertTrue(result, grant)

    def test_wrong_project(self):
        self.check_hold({"projectId": "P01"})

    def test_wrong_item(self):
        self.check_hold({"itemId": "P02.S01.02"})

    def test_wrong_action(self):
        self.check_hold({"action": "ISSUE_MORE_GRANTS"})

    def test_wrong_policy(self):
        self.check_hold({"policySha256": "0"*64})

    def test_source_head_drift(self):
        self.check_hold({"head": "1"*40})

    def test_evidence_drift(self):
        self.check_hold({"evidenceSha256": "1"*64})

    def test_state_preimage_drift(self):
        self.check_hold({"preimageSha256": "1"*64})

    def test_approval_mismatch(self):
        self.check_hold({"approvalSha256": "1"*64})

    def test_nonce_replay(self):
        self.check_hold(nonces=frozenset({GOOD["nonce"]}))

    def test_wrong_issuer(self):
        self.check_hold({"issuerId": "attacker"})

    def test_revoked(self):
        self.check_hold(trusted={**TRUST, "status": "REVOKED"})

    def test_missing_revocation_check(self):
        self.check_hold(trusted={**TRUST, "revocationChecked": False})

    def test_expiry(self):
        self.check_hold(observed_at="2026-10-20T14:00:00Z")

    def test_future_grant(self):
        self.check_hold(observed_at="2026-10-20T10:00:00Z")

    def test_noncanonical_time(self):
        self.check_hold({"issuedAt": "2026-10-20T11:00:00+00:00"})

    def test_extra_field(self):
        self.check_hold({"adminOverride": "true"})

    def test_duplicate_keys(self):
        with self.assertRaises(ValueError):
            exact_json(b'{"a":1,"a":2}')

    def test_nonfinite(self):
        with self.assertRaises(ValueError):
            exact_json(b'{"x":NaN}')

    def test_noncanonical_whitespace_rejected(self):
        with self.assertRaisesRegex(ValueError, "NONCANONICAL_GRANT_BYTES"):
            exact_json(b'{"a": 1}')

    def test_noncanonical_order_rejected(self):
        with self.assertRaisesRegex(ValueError, "NONCANONICAL_GRANT_BYTES"):
            exact_json(b'{"z":1,"a":2}')

    def test_invalid_calendar_day_rejected(self):
        self.check_hold({"issuedAt": "2026-02-30T11:00:00Z"})

    def test_invalid_calendar_month_rejected(self):
        self.check_hold({"issuedAt": "2026-13-20T11:00:00Z"})

    def test_leap_day_valid(self):
        grant = {**GOOD, "issuedAt": "2024-02-29T11:00:00Z",
                 "expiresAt": "2028-02-29T13:00:00Z"}
        self.assertEqual(inspect(grant, trusted=TRUST, expected=EXPECTED,
                         observed_at=NOW, consumed_nonces=frozenset()), [])

    def test_canonical_round_trip(self):
        self.assertEqual(exact_json(canonical(GOOD)), GOOD)

    def test_pinned_trust_rejects_wrong_pin(self):
        raw = canonical({"schema": "enguru.plive.p02.pinned-public-trust-candidate/v1"})
        with self.assertRaisesRegex(ValueError, "TRUST_SOURCE_PIN_MISMATCH"):
            load_pinned_trust_record(raw, approved_sha256="0"*64)

    def test_pinned_trust_rejects_missing_pin(self):
        with self.assertRaisesRegex(ValueError, "APPROVED_TRUST_PIN_REQUIRED"):
            load_pinned_trust_record(b"{}", approved_sha256="")

    def test_pinned_trust_rejects_fake_policy(self):
        raw = canonical({"schema": "enguru.plive.p02.pinned-public-trust-candidate/v1",
                         "issuerId": "fixture", "keyId": "fixture", "policySha256": "0"*64,
                         "publicKeyX963Hex": "04" + "0"*128,
                         "publicKeySha256": "0"*64, "status": "ACTIVE",
                         "revocationChecked": True})
        with self.assertRaisesRegex(ValueError, "TRUST_POLICY_MISMATCH"):
            load_pinned_trust_record(raw, approved_sha256=hashlib.sha256(raw).hexdigest())

    def test_signature_failure_no_writer(self):
        result = verify(canonical(GOOD), base64.b64encode(b"fake").decode(),
                        trusted=TRUST, expected=EXPECTED,
                        observed_at=NOW, consumed_nonces=frozenset())
        self.assertEqual(result["state"], "HOLD")
        self.assertFalse(result["authorizedToWrite"])

    def test_positive_crypto_still_no_writer(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            subprocess.run(["openssl", "ecparam", "-name", "prime256v1", "-genkey",
                            "-noout", "-out", str(p/"priv.pem")],
                           check=True, capture_output=True)
            subprocess.run(["openssl", "pkey", "-in", str(p/"priv.pem"), "-pubout",
                            "-outform", "DER", "-out", str(p/"pub.der")],
                           check=True, capture_output=True)
            pub = (p/"pub.der").read_bytes()[-65:]
            self.assertEqual(pub[0], 4)
            (p/"payload").write_bytes(canonical(GOOD))
            subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(p/"priv.pem"),
                            "-out", str(p/"sig"), str(p/"payload")],
                           check=True, capture_output=True)
            trust = {**TRUST, "publicKeyX963Hex": pub.hex(),
                     "publicKeySha256": hashlib.sha256(pub).hexdigest()}
            # Test-only key is injected: successful crypto != authorized issuer provenance.
            result = verify(canonical(GOOD),
                            base64.b64encode((p/"sig").read_bytes()).decode(),
                            trusted=trust, expected=EXPECTED,
                            observed_at=NOW, consumed_nonces=frozenset())
            self.assertEqual(result["state"], "CRYPTO_AND_SCOPE_VALID_ONLY")
            self.assertFalse(result["authorizedToWrite"])


if __name__ == "__main__":
    unittest.main()
