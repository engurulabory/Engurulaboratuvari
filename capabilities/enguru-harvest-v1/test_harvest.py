import hashlib
import unittest
from harvest import evaluate, verify_bytes

SOURCE = b"safe example"
BASE = {"id": "SRC-01", "library": "skills", "source_url": "https://example.org/open",
        "source_sha256": hashlib.sha256(SOURCE).hexdigest(), "license": "MIT",
        "security_review": "PASS", "mandatory_paid_api": 0}

class HarvestTests(unittest.TestCase):
    def test_invalid(self):
        self.assertEqual(evaluate(None)["state"], "HOLD")
        self.assertEqual(evaluate({})["state"], "HOLD")
    def test_candidate(self):
        self.assertEqual(evaluate(BASE)["state"], "CANDIDATE")
    def test_tested(self):
        self.assertEqual(evaluate({**BASE, "test_receipt": "test-1"})["state"], "TESTED")
    def test_proven(self):
        self.assertEqual(evaluate({**BASE, "test_receipt": "test-1", "real_task_receipt": "task-1", "independent_review": "PASS"})["state"], "PROVEN")
    def test_adopted(self):
        self.assertEqual(evaluate({**BASE, "test_receipt": "test-1", "real_task_receipt": "task-1", "independent_review": "PASS", "human_authority": "PASS"})["state"], "ADOPTED")
    def test_paid(self):
        self.assertEqual(evaluate({**BASE, "mandatory_paid_api": 1})["state"], "HOLD")
    def test_license(self):
        self.assertEqual(evaluate({**BASE, "license": "unknown"})["state"], "HOLD")
    def test_security(self):
        self.assertEqual(evaluate({**BASE, "security_review": "HOLD"})["state"], "HOLD")
    def test_sha(self):
        self.assertEqual(verify_bytes(BASE, b"tampered")["state"], "HOLD")
        self.assertEqual(verify_bytes(BASE, SOURCE)["state"], "CANDIDATE")
    def test_library(self):
        self.assertEqual(evaluate({**BASE, "library": "other"})["state"], "HOLD")

if __name__ == "__main__":
    unittest.main()
