"""A01-A06: regressions for actually rechecked public-source classifications.

A URL and a public testimonial are research inputs, not independent E5 or a
customer production version/SHA. Canonical V19 18x13 evidence stays HOLD.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "governance/enguru-suzgeci/reviews"
RECON = ROOT / "ENGURU_ARGE_BLOCK01_18_CASE_RECONCILIATION_V428.json"
SOURCES = ROOT / "ENGURU_ARGE_BLOCK01_PUBLIC_SOURCES_V427.json"

class OriginalPublicProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(RECON.read_text(encoding="utf-8"))
        cls.review=json.loads(SOURCES.read_text(encoding="utf-8"))
        cls.cases={c["case_id"]:c for c in cls.data["cases"]}

    def test_canonical_eighteen_and_234_and_six_domains(self):
        self.assertEqual(len(self.cases),18)
        self.assertEqual(self.data["baseline"]["rows"],234)
        self.assertEqual(self.data["baseline"]["criteria"],13)
        self.assertEqual(self.data["baseline"]["sha256"],
                         "3906f7bd6ae07d26547babc172d1337cfdfeff85244ece95efb76c3cb448df08")
        self.assertEqual({c["domain"] for c in self.cases.values()},
                         {"Web","Uygulama","Motor","Çekirdek","Ajan","Ticari"})

    def test_a06_e5_is_distinct_from_a07_guarantees(self):
        self.assertIn("independent E5",self.review["task_links"]["A06"])
        self.assertIn("G01",self.review["task_links"]["A07"])
        self.assertIn("installed versions",self.review["task_links"]["A05"])
        self.assertIn("CVE",self.review["task_links"]["A04"])

    def test_c17_dedicated_vodafone_source_used(self):
        s=self.cases["17"]["current_public_source"]
        self.assertEqual(s["url"],"https://www.langchain.com/blog/customers-vodafone-italy")
        self.assertEqual(s["publication_date"],"2025-12-16")
        self.assertEqual(s["source_class"],"LANGGRAPH_VENDOR_DEDICATED_CUSTOMER_CASE")

    def test_uber_supplier_claim_stays_supplier(self):
        s=self.cases["15"]["current_public_source"]
        self.assertEqual(s["source_class"],"LANGGRAPH_VENDOR_GENERAL_ADOPTION_CLAIM")
        self.assertEqual(s["reviewed_source_role"],"VENDOR_ASSERTION_ONLY")

    def test_linkedin_customer_first_party_not_e5(self):
        s=self.cases["14"]["current_public_source"]
        self.assertEqual(s["publication_date"],"2024-12-09")
        self.assertEqual(s["reviewed_source_role"],"CUSTOMER_ENGINEERING_FIRST_PARTY")

    def test_replit_temporal_historical_against_restate(self):
        s=self.cases["07"]["current_public_source"]
        self.assertEqual(s["freshness"],"HISTORICAL_SUPERSEDED_CLAIM")
        self.assertEqual(s["newer_contrary_source"],"https://restate.dev/use-cases/replit")
        self.assertEqual(self.cases["07"]["exact_customer_deployment_sha"],"HOLD")

    def test_auth0_openfga_lineage_not_external_customer(self):
        s=self.cases["08"]["current_public_source"]
        self.assertEqual(s["freshness"],"PRODUCT_LINEAGE_ONLY")
        self.assertEqual(s["reviewed_source_role"],"AUTH0_OPENFGA_PRODUCT_LINEAGE_ONLY")

    def test_seven_upstream_licensing_blobs_are_pinned(self):
        pins=self.review["upstream_license_pins"]
        self.assertEqual(len(pins),7)
        self.assertEqual({p["technology"] for p in pins},
                         {c["technology"] for c in self.cases.values()})
        self.assertEqual(len({p["repository"] for p in pins}),7)
        self.assertEqual(self.review["upstream_license_blob_pin_count"],7)
        for pin in pins:
            with self.subTest(technology=pin["technology"]):
                blob=pin["git_blob_sha1"]
                self.assertEqual(len(blob),40)
                self.assertTrue(all(x in "0123456789abcdef" for x in blob))
                self.assertIn("release",pin["evidence_scope"].lower()
                              + self.review["upstream_license_review_scope"].lower())

    def test_real_upstream_manifest_blob_pins_and_non_sbom_semantics(self):
        expected={
            "Meilisearch":("Cargo.lock","d018e8060a179a9d53c350d78ee04005422abc22"),
            "Medusa":("yarn.lock","660081e74b9be3799b3a0f25d5631df4e1cf0658"),
            "Saleor":("uv.lock","a71a6f59ffdec55dae1e5975a083abf969a89130"),
            "Supabase":("pnpm-lock.yaml","57212ada2d941ca4f1ad02d6d23c043072969191"),
            "Temporal":("go.sum","7bb84062f0806238f63f3a71ccc70375a98f8968"),
            "OpenFGA":("go.sum","46f0cd6c60028577eb92bf5a4be0af82c705edaa"),
            "LangGraph":("libs/langgraph/pyproject.toml","6aac18d6162e9f516e3f66113ce064f5da698b9a"),
        }
        manifests={p["technology"]:p for p in self.review["a04_upstream_dependency_evidence"]}
        self.assertEqual(set(manifests),set(expected))
        for technology,(path,sha) in expected.items():
            with self.subTest(technology=technology):
                record=manifests[technology]
                self.assertEqual((record["path"],record["git_blob_sha1"]),(path,sha))
                self.assertEqual(record["sbom_status"],"HOLD_NO_VERIFIED_SIGNED_SBOM")
                self.assertEqual(record["cve_status"],"HOLD_CUSTOMER_VERSION_UNRESOLVED")
                self.assertEqual(record["customer_release_status"],
                                 "HOLD_EXACT_DEPLOYED_RELEASE_UNAVAILABLE")
        self.assertEqual(self.review["a04_sbom_independently_verified"],0)
        self.assertEqual(self.review["a04_customer_cve_applicability_verified"],0)
        self.assertEqual(self.review["a04_release_sha256_verified"],0)

    def test_exact_license_and_enterprise_source_identity(self):
        verified={
            "Meilisearch":"edcaeebc4e866b1ebefc330c103560e41639601b",
            "Medusa":"2bc747bf4b0a88864584b033fdeab86012a44c79",
            "Saleor":"715b42cd6fe5d7073984ff7004b49dc8304adbcc",
            "Supabase":"49ea124025275674563eeff03af0f653ca49fdc0",
            "Temporal":"3349f76795f4409cba6ae18ea56adf9fbd8346f3",
            "OpenFGA":"4959a5e50d66e62e675d8d033d66cca0f390458d",
            "LangGraph":"fc0602feecdd6748623c852ab534e1ca612673c7",
        }
        observed={p["technology"]:p["git_blob_sha1"] for p in self.review["upstream_license_pins"]}
        self.assertEqual(observed,verified)
        licenses={e["technology"]:e["git_blob_sha1"]
                  for e in self.review["a04_enterprise_licensing_documents"]}
        self.assertEqual(licenses,{
            "Meilisearch":"87510480d5d8653a1a1583285c5ba5208b22826e",
            "Medusa":"56ec107aaf946c18f88955a031ba1dec9396111d"
        })

    def test_upstream_enterprise_licenses_require_actual_edition_pin(self):
        by_tech={p["technology"]:p for p in self.review["upstream_license_pins"]}
        self.assertEqual(by_tech["Meilisearch"]["observed_license"],
                         "MIT_AND_BUSL_1_1_EDITION_SPECIFIC")
        self.assertEqual(by_tech["Medusa"]["observed_license"],
                         "MIT_EXCEPT_ENTERPRISE_EDITION")
        self.assertIn("NOT SHA-256 release pins",
                      self.review["upstream_license_review_scope"])
        self.assertEqual(self.data["rollup"]["exact_deployment_sha_pass"],0)

    def test_public_sourcing_cannot_set_any_acceptance_pass(self):
        self.assertEqual(self.review["e5_independently_verified"],0)
        self.assertEqual(self.review["deployment_pins_independently_verified"],0)
        self.assertEqual(self.data["rollup"]["independent_e5_pass"],0)
        self.assertEqual(self.data["rollup"]["exact_deployment_sha_pass"],0)
        self.assertEqual(self.data["rollup"]["official_block01_pass"],"0/9")
        for c in self.cases.values():
            with self.subTest(c=c["case_id"]):
                self.assertEqual(c["independent_e5"],"HOLD")
                self.assertEqual(c["exact_customer_deployment_sha"],"HOLD")
                self.assertEqual(c["current_public_source"]["independent_E5_attestation"],
                                 "HOLD_NOT_ESTABLISHED")

if __name__ == "__main__":
    unittest.main()
