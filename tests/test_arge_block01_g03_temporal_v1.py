"""A07 G03 proof: existing 18-case public witnesses have no signed time pin."""
import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tools.arge_block01_g03_temporal_v1 import asof_batch, asof_case_check

CATALOG = (Path(__file__).resolve().parents[1] /
    "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_18_CASE_RECONCILIATION_V428.json")
CLOCK = datetime(2026, 10, 23, 18, tzinfo=timezone.utc)

def sample(case):
    x = copy.deepcopy(case)
    x["temporal_evidence"] = {
        "url": x["current_public_source"]["url"],
        "sha256": "a" * 64,
        "published_at": "2026-09-01T00:00:00Z",
        "observed_at": "2026-10-20T00:00:00Z",
        "valid_until": "2026-11-01T00:00:00Z",
        "independent_verifier_receipt": "UNVERIFIED_TEST_MARKER"
    }
    return x

class G03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

    def test_current_18_are_all_temporally_unverified(self):
        r = asof_batch(self.catalog, CLOCK)
        self.assertEqual(len(r["cases"]), 18)
        self.assertEqual(r["source_time_approved"], 0)
        self.assertEqual({x["state"] for x in r["cases"]}, {"HOLD_NO_OBSERVED_SOURCE_PIN"})

    def test_undated_vendor_testimonial_holds(self):
        self.assertEqual(asof_case_check(self.catalog["cases"][0], CLOCK)["state"],
                         "HOLD_NO_OBSERVED_SOURCE_PIN")

    def test_replit_succeeding_vendor_claim_holds_even_with_proof(self):
        self.assertEqual(asof_case_check(sample(self.catalog["cases"][6]), CLOCK)["state"],
                         "HOLD_CONFLICTING_NEWER_SOURCE")

    def test_timestamp_future_holds(self):
        a = sample(self.catalog["cases"][0])
        a["temporal_evidence"]["observed_at"] = "2027-01-01T00:00:00Z"
        self.assertEqual(asof_case_check(a, CLOCK)["state"], "HOLD_TIME_ORDER")

    def test_stale_holds(self):
        a = sample(self.catalog["cases"][0])
        a["temporal_evidence"]["observed_at"] = "2026-01-01T00:00:00Z"
        self.assertEqual(asof_case_check(a, CLOCK)["state"], "HOLD_SOURCE_STALE")

    def test_mismatched_source_url_holds(self):
        a = sample(self.catalog["cases"][0])
        a["temporal_evidence"]["url"] = "https://example.org/other"
        self.assertEqual(asof_case_check(a, CLOCK)["state"], "HOLD_SOURCE_IDENTITY")

    def test_fake_sha_holds(self):
        a = sample(self.catalog["cases"][0])
        a["temporal_evidence"]["sha256"] = "not-the-digest"
        self.assertEqual(asof_case_check(a, CLOCK)["state"], "HOLD_SOURCE_DIGEST")

    def test_naive_clock_holds(self):
        a = sample(self.catalog["cases"][0])
        self.assertEqual(asof_case_check(a, datetime(2026,10,23))["state"], "HOLD_INPUT_OR_CLOCK")

    def test_self_claimed_receipt_stays_unofficial(self):
        a = sample(self.catalog["cases"][0])
        self.assertEqual(asof_case_check(a, CLOCK)["state"],
                         "SOURCE_TIME_PREFLIGHT_ONLY_REQUIRES_CRYPTO_VERIFICATION")

    def test_blank_receipt_holds(self):
        a = sample(self.catalog["cases"][0])
        a["temporal_evidence"]["independent_verifier_receipt"] = ""
        self.assertEqual(asof_case_check(a, CLOCK)["state"], "HOLD_INDEPENDENT_SOURCE_VERIFICATION")

if __name__=="__main__":
    unittest.main()
