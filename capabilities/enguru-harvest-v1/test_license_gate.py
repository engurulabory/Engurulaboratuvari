import copy
import json
import unittest
from pathlib import Path
from license_gate import check

BASE=Path(__file__).resolve().parent
C=json.loads((BASE/"source_candidates.json").read_text(encoding="utf-8"))
LICENSE_OBSERVATIONS=json.loads((BASE/"root_license_observations.json").read_text(encoding="utf-8"))

class LicenseTests(unittest.TestCase):
    def test_join_and_counts(self):
        x=check(C,LICENSE_OBSERVATIONS)
        self.assertEqual(x["state"],"LICENSE_OBSERVATION_PASS")
        self.assertEqual(x["root_files_observed"],29)
        self.assertEqual(x["approved_for_reuse"],0)
        self.assertEqual(x["missing_root_files"],["anthropics/skills"])
    def test_no_auto_clearance(self):
        o=copy.deepcopy(LICENSE_OBSERVATIONS)
        o["observations"][0]["redistribution_approval"]="PASS"
        self.assertEqual(check(C,o)["state"],"HOLD")
    def test_no_fake_pin(self):
        o=copy.deepcopy(LICENSE_OBSERVATIONS)
        o["observations"][0]["git_blob_sha1"]="a"
        self.assertEqual(check(C,o)["state"],"HOLD")
    def test_duplicate_repo(self):
        o=copy.deepcopy(LICENSE_OBSERVATIONS)
        o["observations"][1]["repository"]=o["observations"][0]["repository"]
        self.assertEqual(check(C,o)["state"],"HOLD")
    def test_tampered_source_registry(self):
        c=copy.deepcopy(C)
        c["candidates"][0]["license"]="MIT"
        self.assertEqual(check(c,LICENSE_OBSERVATIONS)["state"],"HOLD")
    def test_malformed(self):
        for a,b in (([],LICENSE_OBSERVATIONS),(C,[]),({},LICENSE_OBSERVATIONS),(C,{"observations":[None]*30})):
            self.assertEqual(check(a,b)["state"],"HOLD")
    def test_restricted_sources_remain_hold(self):
        observed={x["repository"]:x for x in LICENSE_OBSERVATIONS["observations"]}
        self.assertEqual(observed["anthropics/claude-code"]["content_signal"],"COMMERCIAL_TERMS_REFERENCE")
        self.assertEqual(observed["meilisearch/meilisearch"]["content_signal"],"MIXED_COMMUNITY_ENTERPRISE")
        self.assertEqual(observed["semgrep/semgrep"]["content_signal"],"LGPL_2_1_TEXT")
        self.assertTrue(all(x["redistribution_approval"]=="HOLD" for x in LICENSE_OBSERVATIONS["observations"]))

if __name__=="__main__":
    unittest.main()
