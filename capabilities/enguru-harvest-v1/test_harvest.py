import hashlib
import unittest
from harvest import evaluate, verify_bytes

SOURCE = b"safe example"
BASE = {"id": "SRC-01", "library": "skills", "source_url": "https://example.org/open",
        "source_sha256": hashlib.sha256(SOURCE).hexdigest(), "license": "MIT",
        "security_review": "PASS", "mandatory_paid_api": 0}

class HarvestTests(unittest.TestCase):
    def test_invalid_and_missing(self):
        self.assertEqual(evaluate(None)["state"], "HOLD")
        self.assertEqual(evaluate({})["state"], "HOLD")
    def test_candidate(self):
        self.assertEqual(evaluate(BASE)["state"], "CANDIDATE")
    def test_no_self_granted_proven_or_adopted(self):
        claimed={**BASE, "test_receipt": "PASS", "real_task_receipt": "PASS",
                 "independent_review": "PASS", "human_authority": "PASS"}
        self.assertEqual(evaluate(claimed)["state"], "CANDIDATE")
    def test_paid(self):
        for amount in (1, -1, None, False, "0"):
            self.assertEqual(evaluate({**BASE, "mandatory_paid_api": amount})["state"], "HOLD")
    def test_license_unverified(self):
        for license_name in ("unknown","UNVERIFIED", [], {}, None):
            self.assertEqual(evaluate({**BASE, "license": license_name})["state"], "HOLD")
    def test_security(self):
        self.assertEqual(evaluate({**BASE, "security_review": "HOLD"})["state"], "HOLD")
    def test_sha_bytes(self):
        self.assertEqual(verify_bytes(BASE, b"tampered")["state"], "HOLD")
        self.assertEqual(verify_bytes(BASE, SOURCE)["state"], "CANDIDATE")
    def test_library(self):
        for value in ("other", [], None):
            self.assertEqual(evaluate({**BASE, "library": value})["state"], "HOLD")
    def test_url(self):
        for value in ("http://example.com","https://user:pass@example.com", "https://ok.example/a b", [], None):
            self.assertEqual(evaluate({**BASE, "source_url":value})["state"],"HOLD")
    def test_untrusted_schema_types(self):
        for key, value in (("id",[]),("source_sha256",{}),("security_review",[])):
            self.assertEqual(evaluate({**BASE,key:value})["state"],"HOLD")
if __name__ == "__main__":
    unittest.main()
