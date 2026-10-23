"""Review-only Block 01 provenance inventory verification."""
import json
import unittest
from itertools import combinations
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_PROVENANCE_V425.json"
IDS = {f"A{x:02d}" for x in range(1, 10)}

def reconcile(value):
    categories=value.get("required_categories", {})
    if set(categories) != IDS: return "HOLD_SCOPE"
    expected={(task, category) for task, names in categories.items() for category in names}
    entries=value.get("unverified_categories", [])
    observed={(entry.get("task_id"),entry.get("category")) for entry in entries if entry.get("state")=="HOLD_SOURCE_NOT_VERIFIED"}
    if len(entries)!=len(expected) or observed!=expected: return "HOLD_PROVENANCE_GAP"
    if value.get("verified_sources"): return "HOLD_INDEPENDENT_AUTHENTICATION"
    if value.get("acceptance")!="HOLD" or value.get("osi")!="NOT_STARTED": return "HOLD_PREMATURE_ACCEPTANCE"
    return "INVENTORY_COMPLETE_ACCEPTANCE_HOLD"

class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.item=json.loads(FILE.read_text(encoding="utf-8"))
    def test_inventory_complete(self):
        self.assertEqual(reconcile(self.item),"INVENTORY_COMPLETE_ACCEPTANCE_HOLD")
    def test_pair_loss_20_percent(self):
        for ids in combinations(sorted(IDS),2):
            with self.subTest(ids=ids):
                x=dict(self.item)
                x["required_categories"]={k:v for k,v in self.item["required_categories"].items() if k not in ids}
                self.assertEqual(reconcile(x),"HOLD_SCOPE")
    def test_missing_provenance_holds(self):
        for idx in range(len(self.item["unverified_categories"])):
            with self.subTest(idx=idx):
                x=dict(self.item)
                x["unverified_categories"]=self.item["unverified_categories"][:idx]+self.item["unverified_categories"][idx+1:]
                self.assertEqual(reconcile(x),"HOLD_PROVENANCE_GAP")
    def test_claimed_verified_source_needs_independent_validation(self):
        x=dict(self.item)
        x["verified_sources"]={"A03":"SELF_ASSERTED"}
        self.assertEqual(reconcile(x),"HOLD_INDEPENDENT_AUTHENTICATION")

if __name__=="__main__":
    unittest.main()
