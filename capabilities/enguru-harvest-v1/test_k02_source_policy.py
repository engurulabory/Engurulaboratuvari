import copy
import json
import unittest
from pathlib import Path
from k02_source_policy import reconcile

BASE=Path(__file__).resolve().parent
S=json.loads((BASE/"source_candidates.json").read_text(encoding="utf-8"))
L=json.loads((BASE/"root_license_observations.json").read_text(encoding="utf-8"))

class K02SourcePolicyTests(unittest.TestCase):
    def test_real_inventory_is_quarantined(self):
        r=reconcile(S,L)
        self.assertEqual(r["state"],"PASS_SAFE_QUARANTINE")
        self.assertEqual((r["observed"],r["proven"],r["licensed_for_adoption"]),(30,0,0))
    def test_does_not_promote_license(self):
        s=copy.deepcopy(S)
        s["candidates"][0]["license"]="MIT"
        self.assertEqual(reconcile(s,L)["state"],"HOLD")
    def test_does_not_promote_unsigned_source(self):
        s=copy.deepcopy(S)
        s["candidates"][0]["source_archive_sha256"]="a"*64
        self.assertEqual(reconcile(s,L)["state"],"HOLD")
    def test_does_not_promote_license_receipt(self):
        l=copy.deepcopy(L)
        l["observations"][0]["redistribution_approval"]="PASS"
        self.assertEqual(reconcile(S,l)["state"],"HOLD")
    def test_missing_source(self):
        s=copy.deepcopy(S)
        s["candidates"].pop()
        self.assertEqual(reconcile(s,L)["state"],"HOLD")
    def test_duplicate_repository(self):
        s=copy.deepcopy(S)
        s["candidates"][1]["repository"]=s["candidates"][0]["repository"]
        self.assertEqual(reconcile(s,L)["state"],"HOLD")
    def test_malformed_records(self):
        self.assertEqual(reconcile({},L)["state"],"HOLD")
        l=copy.deepcopy(L)
        l["observations"][2]={"repository":[]}
        self.assertEqual(reconcile(S,l)["state"],"HOLD")

if __name__=="__main__":
    unittest.main()
