"""A05 use-rights hard gates; synthetic records test guards, not legal proof.

Real SHA256 records arrive from same GitHub Actions runner after live fetch.
"""
import copy
import json
import unittest
from pathlib import Path
from a05_license_scope_routing import classify, reconcile

ROOT=Path(__file__).resolve().parent
PINS=json.loads((ROOT/"UPSTREAM_GITHUB_PINS_30.json").read_text(encoding="utf-8"))
LICENSES=json.loads((ROOT/"root_license_observations.json").read_text(encoding="utf-8"))

def fake_receipt():
    rows=[]
    sources={s["repository"]:s for s in PINS["sources"]}
    for item in LICENSES["observations"]:
        if item["path"] is None:
            continue
        name=item["repository"]
        category=item["content_signal"]
        if category=="APACHE_2_TEXT":
            risk="APACHE_2_NOTICE_PATENT_REVIEW"
        elif "MIT" in category:
            risk="MIT_NOTICE_REVIEW"
        else:
            risk="UNCLASSIFIED_LICENSE_REVIEW"
        rows.append({
            "repository":name,"source_commit_sha":sources[name]["commit_sha"],
            "license_path":item["path"],"license_fulltext_sha256":"a"*64,
            "license_blob_sha1":item["git_blob_sha1"],"license_bytes":100,
            "license_risk":risk,"state":"PASS_LICENSE_BYTES_OBSERVED_ONLY",
            "legal_reuse_authorized":False,"security_approval":False,
            "source_archive_sha256":None,"license_text_redistributed":False,
        })
    return {
        "schema":"enguru.harvest.a05-license-fulltext-evidence/v1",
        "state":"PASS_PINNED_29_LICENSE_FULLTEXT_DIGESTS_OBSERVED_ONLY",
        "license_usage_authority":"HOLD","official_finish":"HOLD",
        "legal_reuse_approvals":0,"official_proven_skills":0,"osi_execution":0,
        "root_license_fulltext_sha256_count":29,
        "missing_root_license_count":1,"records":rows,
    }

class A05LicenseScopeTests(unittest.TestCase):
    def setUp(self):
        self.record=fake_receipt()
    def test_thirty_scope_coverage_with_zero_approvals(self):
        outcome=reconcile(self.record,PINS)
        self.assertEqual(outcome["state"],"PASS_DETAILED_30_SOURCE_USE_SCOPE_REVIEW_PLAN_ONLY")
        self.assertEqual((outcome["source_records"],outcome["permission_grants"]), (30,0))
        self.assertTrue(all(r["action_state"]=="HOLD_SCOPE_SPECIFIC_ACCEPTANCE" for r in outcome["records"]))
    def test_restricted_vendor_and_per_skill(self):
        x=reconcile(self.record,PINS)["records"]
        by={r["repository"]:r for r in x}
        self.assertEqual(by["anthropics/skills"]["review_category"],"NO_ROOT_PER_SKILL_VENDOR_RESTRICTED")
        self.assertEqual(by["anthropics/claude-code"]["review_category"],"VENDOR_TERMS_RESTRICTED")
        self.assertIs(by["anthropics/skills"]["product_adoption"],False)
    def test_mixed_meili_components(self):
        decision,requirements=classify("meilisearch/meilisearch","")
        self.assertEqual(decision,"MIXED_COMPONENT_LICENSE")
        self.assertIn("BUSL_ENTERPRISE_REVIEW",requirements)
    def test_license_obligations_not_promoted(self):
        for name in ("semgrep/semgrep","HypothesisWorks/hypothesis","astral-sh/uv"):
            category,checks=classify(name,"")
            self.assertTrue(category.endswith("REVIEW"))
            self.assertTrue(checks)
    def test_forged_owner_approval_is_hold(self):
        x=copy.deepcopy(self.record)
        x["license_usage_authority"]="PASS"
        self.assertEqual(reconcile(x,PINS)["state"],"HOLD_SOURCE_OR_AUTHORITY")
    def test_false_official_finish_is_hold(self):
        x=copy.deepcopy(self.record)
        x["official_finish"]="PASS"
        self.assertEqual(reconcile(x,PINS)["state"],"HOLD_SOURCE_OR_AUTHORITY")
    def test_wrong_count_is_hold(self):
        x=copy.deepcopy(self.record)
        x["records"].pop()
        self.assertEqual(reconcile(x,PINS)["state"],"HOLD_SOURCE_COUNT")
    def test_wrong_source_commit_is_hold(self):
        x=copy.deepcopy(self.record)
        x["records"][0]["source_commit_sha"]="b"*40
        self.assertEqual(reconcile(x,PINS)["state"],"HOLD_COMMIT_OR_LICENSE_MISSING")
    def test_fake_license_sha256_is_hold(self):
        x=copy.deepcopy(self.record)
        x["records"][0]["license_fulltext_sha256"]="INVALID"
        self.assertEqual(reconcile(x,PINS)["state"],"HOLD_UNTRUSTED_LICENSE_RECEIPT")
    def test_false_security_acceptance_is_hold(self):
        x=copy.deepcopy(self.record)
        x["records"][0]["security_approval"]=True
        self.assertEqual(reconcile(x,PINS)["state"],"HOLD_UNTRUSTED_LICENSE_RECEIPT")
    def test_source_adoption_is_hold(self):
        p=copy.deepcopy(PINS)
        p["sources"][0]["adoption"]="PASS"
        self.assertEqual(reconcile(self.record,p)["state"],"HOLD_SOURCE_PROMOTION")
    def test_redundant_license_is_hold(self):
        x=copy.deepcopy(self.record)
        x["records"][1]["repository"]=x["records"][0]["repository"]
        self.assertEqual(reconcile(x,PINS)["state"],"HOLD_UNTRUSTED_LICENSE_RECEIPT")
    def test_no_root_legal_scope(self):
        x=copy.deepcopy(self.record)
        x["records"].append(copy.deepcopy(x["records"][0]))
        self.assertEqual(reconcile(x,PINS)["state"],"HOLD_SOURCE_COUNT")
    def test_forged_no_mac_is_hold(self):
        x=copy.deepcopy(self.record)
        x["osi_execution"]=1
        self.assertEqual(reconcile(x,PINS)["state"],"HOLD_SOURCE_OR_AUTHORITY")
    def test_false_redistribution_is_hold(self):
        x=copy.deepcopy(self.record)
        x["records"][0]["license_text_redistributed"]=True
        self.assertEqual(reconcile(x,PINS)["state"],"HOLD_UNTRUSTED_LICENSE_RECEIPT")
    def test_source_license_no_stored_program(self):
        result=reconcile(self.record,PINS)
        for row in result["records"]:
            self.assertFalse(row["actual_skill_source_incorporation"])
            self.assertFalse(row["source_redistribution"])
            self.assertFalse(row["product_adoption"])
            self.assertFalse(row["legal_scope_accepted"])
if __name__=="__main__":
    unittest.main()
