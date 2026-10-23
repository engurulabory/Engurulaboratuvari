"""A04 upstream license evidence reconciliation against original 18-case research.

The tests check traceability, not legal clearance, customer deployment, CVE or E5.
Upstream file blobs were retrieved from 7 public Github repos at pinned commits.
"""
import json
import re
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "governance/enguru-suzgeci/reviews"
MANIFEST = BASE / "ENGURU_ARGE_BLOCK01_A04_UPSTREAM_LICENSE_PINS_V1.json"
CASES = BASE / "ENGURU_ARGE_BLOCK01_18_CASE_RECONCILIATION_V428.json"
SHA = re.compile(r"[0-9a-f]{40}\Z")

class A04SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.original = json.loads(CASES.read_text(encoding="utf-8"))

    def test_upstream_and_customer_scope_exactly_18_cases(self):
        self.assertEqual(len(self.data["tech"]), 7)
        actual = [cid for item in self.data["tech"] for cid in item["case_ids"]]
        self.assertEqual(sorted(actual), [f"{i:02d}" for i in range(1,19)])
        self.assertEqual(self.data["original_v19_matrix_sha256"], self.original["baseline"]["sha256"])
        cases = {x["case_id"]: x["technology"] for x in self.original["cases"]}
        for item in self.data["tech"]:
            for cid in item["case_ids"]:
                self.assertEqual(item["name"], cases[cid])

    def test_each_upstream_pin_is_exact_git_file_identifier(self):
        for item in self.data["tech"]:
            with self.subTest(repo=item["repository"]):
                self.assertRegex(item["source_commit_sha"], SHA)
                self.assertRegex(item["license_git_blob_sha"], SHA)
                uri = f"https://github.com/{item['repository']}/blob/{item['source_commit_sha']}/LICENSE"
                self.assertEqual(item["license_evidence_url"], uri)
                self.assertEqual(item["license_path"], "LICENSE")
                self.assertIn(item["default_branch"], ("main","master","develop"))

    def test_license_boundary_is_visible_for_mixed_rights(self):
        by_name = {item["name"]: item for item in self.data["tech"]}
        self.assertIn("BUSINESS_SOURCE_LICENSE", by_name["Meilisearch"]["license_observed"])
        self.assertIn("COMMERCIAL_ENTERPRISE", by_name["Medusa"]["license_observed"])
        self.assertEqual({f["path"] for f in by_name["Meilisearch"]["additional_license_files"]},
                         {"LICENSE-EE", "LICENSE-MIT"})
        self.assertEqual({f["path"] for f in by_name["Medusa"]["additional_license_files"]},
                         {"ENTERPRISE-LICENSE.md"})

    def test_cve_sbom_deployment_and_e5_not_promoted(self):
        for item in self.data["tech"]:
            for key in ("sbom_verified", "cve_review_verified",
                        "customer_deployment_version_verified",
                        "customer_deployment_sha_verified",
                        "independent_e5_verified", "legal_license_clearance"):
                with self.subTest(item=item["name"],key=key):
                    self.assertIs(item[key], False)
        x = self.data["acceptance_boundary"]
        self.assertEqual(x["a04_official"], "HOLD")
        self.assertEqual(x["customer_deployment"], "HOLD_0_OF_18")
        self.assertEqual(x["independent_e5"], "HOLD_0_OF_18")

    def test_conflicting_replit_use_stays_historical(self):
        self.assertIn("07", next(x for x in self.data["tech"] if x["name"]=="Temporal")["case_ids"])
        self.assertTrue(any(c["case_id"]=="07" for c in self.original["source_conflicts"]))

if __name__=="__main__":
    unittest.main()
