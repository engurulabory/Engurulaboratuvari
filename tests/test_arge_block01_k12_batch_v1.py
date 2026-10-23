"""Block01 K12 full-scope adversarial replay on canonical V19 identities."""
import copy
import json
import unittest
from pathlib import Path
from tools.arge_block01_k12_batch_v1 import audit_k12_batch, V19_SHA
from tools.arge_block01_k12_tco_v1 import REQUIRED

CATALOG_PATH = (Path(__file__).resolve().parents[1] /
    "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_18_CASE_RECONCILIATION_V428.json")

def costs(value=10, unit="TRY_2026_CONSTANT"):
    return dict(
        workload_ref="CASE_SIMULATION_NOT_REAL", measurement_period="2026_SIMULATION",
        price_basis="SYNTHETIC",
        years=[{x: {"value": value, "unit": unit, "source_ref": "TEST_ONLY"}
                for x in REQUIRED} for _ in range(5)],
    )

def synthetic(catalog):
    return {"cases": [
        {"case_id": c["case_id"], "customer": c["customer"], "technology": c["technology"],
         "baseline": costs(10), "candidate": costs(9)}
        for c in catalog["cases"]
    ]}

class K12BatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    def setUp(self):
        self.data = synthetic(self.catalog)

    def test_canonical_18x13_pin(self):
        self.assertEqual(self.catalog["baseline"]["sha256"], V19_SHA)
        self.assertEqual(len(self.catalog["cases"]), 18)
        self.assertEqual(self.catalog["baseline"]["rows"], 234)

    def test_full_synthetic_stays_unofficial(self):
        x = audit_k12_batch(self.catalog, self.data)
        self.assertEqual(x["state"], "CALCULATIONS_REVIEW_REQUIRED")
        self.assertEqual(x["calculable_unverified"], 18)
        self.assertEqual(x["actual_measured_tco_independently_verified"], 0)
        self.assertEqual(x["official_pass"], 0)
        self.assertEqual({c["state"] for c in x["cases"]},
                         {"CALCULATION_ONLY_NEEDS_INDEPENDENT_REVIEW"})

    def test_20_percent_missing_cases_holds(self):
        for start in range(15):
            t = copy.deepcopy(self.data)
            del t["cases"][start:start+4]
            self.assertEqual(audit_k12_batch(self.catalog, t)["state"], "HOLD_18_CASE_SCOPE")

    def test_duplicate_case_id_holds(self):
        t = copy.deepcopy(self.data)
        t["cases"][5]["case_id"] = "01"
        self.assertEqual(audit_k12_batch(self.catalog, t)["state"], "HOLD_18_CASE_SCOPE")

    def test_case_identity_tamper_holds(self):
        t = copy.deepcopy(self.data)
        t["cases"][2]["technology"] = "different"
        x = audit_k12_batch(self.catalog, t)
        self.assertEqual(x["state"], "HOLD_K12_SOURCE_OR_COMPARABILITY")
        self.assertEqual(x["cases"][2]["state"], "HOLD_CUSTOMER_TECH_IDENTITY")

    def test_missing_cost_source_holds(self):
        t = copy.deepcopy(self.data)
        t["cases"][0]["candidate"]["years"][0]["license"]["source_ref"] = ""
        self.assertEqual(audit_k12_batch(self.catalog, t)["calculable_unverified"], 17)

    def test_unmatched_currency_holds(self):
        t = copy.deepcopy(self.data)
        t["cases"][0]["candidate"] = costs(9, unit="USD")
        x = audit_k12_batch(self.catalog, t)
        self.assertEqual(x["cases"][0]["state"], "HOLD_CURRENCY_MISMATCH")

    def test_baseline_hash_tamper_holds(self):
        t = copy.deepcopy(self.catalog)
        t["baseline"]["sha256"] = "0" * 64
        self.assertEqual(audit_k12_batch(t, self.data)["state"], "HOLD_CANONICAL_BASELINE")

    def test_malformed_ids_hold_without_exception(self):
        t = copy.deepcopy(self.data)
        t["cases"][0]["case_id"] = None
        self.assertEqual(audit_k12_batch(self.catalog, t)["state"], "HOLD_18_CASE_SCOPE")

    def test_missing_catalog_id_holds_without_exception(self):
        t = copy.deepcopy(self.catalog)
        t["cases"][0]["case_id"] = None
        self.assertEqual(audit_k12_batch(t, self.data)["state"], "HOLD_CANONICAL_IDENTITIES")

    def test_untrusted_empty_input_holds(self):
        self.assertEqual(audit_k12_batch(self.catalog, {})["state"], "HOLD_INPUT_FORMAT")
        self.assertEqual(audit_k12_batch(None, self.data)["state"], "HOLD_FORMAT")

if __name__ == "__main__":
    unittest.main()
