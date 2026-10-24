"""EMUS G05/G06 source-pinned security gates; evidence presence != authority."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EmusSecuritySourceBoundaryTests(unittest.TestCase):
    def test_threat_contract_and_existing_tests_exist(self):
        contract = ROOT / "governance/security/SECURITY_REVIEW_CONTRACT_V1.md"
        engine = ROOT / "shared_ai/security_review.py"
        tests = ROOT / "tests/test_security_review.py"
        self.assertTrue(all(p.is_file() for p in (contract, engine, tests)))
        text = contract.read_text(encoding="utf8")
        self.assertIn("STRIDE coverage", text)
        self.assertIn("Missing required category evidence produces HOLD", text)
        for term in ("authentication", "authorization", "secret handling", "logging"):
            self.assertIn(term, text)
        self.assertIn("untrusted_review_source", engine.read_text(encoding="utf8"))
        self.assertIn("test_incomplete_stride_coverage_holds", tests.read_text(encoding="utf8"))

    def test_v3_source_sha256_and_git_blob_match_lock(self):
        lock = json.loads((ROOT / "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json").read_text(encoding="utf8"))
        raw = (ROOT / "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), lock["sha256"])
        self.assertEqual(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(), lock["git_blob_sha1"])

    def test_source_presence_cannot_claim_authorized_finish(self):
        matrix = (ROOT / "governance/emus/EMUS_V11_SUBCRITERION_PROGRESS_V1.json")
        data = json.loads(matrix.read_text(encoding="utf8"))
        self.assertEqual(data["counting_rules"]["official_accepted_tasks"], 0)
        for item in (17, 18, 19):
            self.assertTrue(all(c["state"] == "HOLD_UNVERIFIED" for c in data["rows"][item - 1]["criteria"]))


if __name__ == "__main__":
    unittest.main()
