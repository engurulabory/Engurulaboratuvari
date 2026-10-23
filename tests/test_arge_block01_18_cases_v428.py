"""18-case V19 evidence reconciliation, GitHub-only review."""
import json
import unittest
from pathlib import Path
P = Path(__file__).resolve().parents[1] / "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_18_CASE_RECONCILIATION_V428.json"
REQUIRED = ("independent_e5", "g01", "g02", "g03", "k12", "exact_customer_deployment_sha")
def exit_decision(data):
    entries = data.get("cases", [])
    if len(entries) != 18 or {x.get("case_id") for x in entries} != {f"{i:02d}" for i in range(1,19)}:
        return "HOLD_SCOPE"
    if data.get("baseline", {}).get("rows") != 234:
        return "HOLD_BASELINE"
    if any(x.get(field) != "PASS_VERIFIED" for x in entries for field in REQUIRED):
        return "HOLD_REAL_EVIDENCE"
    return "SIMULATION_ONLY_NO_AUTHORIZED_FINISH"
class ReconciliationTests(unittest.TestCase):
    def setUp(self): self.record=json.loads(P.read_text(encoding="utf-8"))
    def test_baseline(self):
        self.assertEqual(len(self.record["cases"]),18)
        self.assertEqual(self.record["rollup"]["independent_e5_pass"],0)
        self.assertEqual(exit_decision(self.record),"HOLD_REAL_EVIDENCE")
    def test_twenty_percent_four_missing_cases(self):
        for first in range(0,15):
            x=dict(self.record)
            x["cases"]=self.record["cases"][:first]+self.record["cases"][first+4:]
            self.assertEqual(exit_decision(x),"HOLD_SCOPE")
    def test_each_evidence_type_failure(self):
        for field in REQUIRED:
            x=dict(self.record)
            x["cases"]=[dict(v, **{g:"PASS_VERIFIED" for g in REQUIRED}) for v in self.record["cases"]]
            x["cases"][0][field]="HOLD"
            self.assertEqual(exit_decision(x),"HOLD_REAL_EVIDENCE")
    def test_fully_simulated_state_stays_unofficial(self):
        x=dict(self.record)
        x["cases"]=[dict(v,**{g:"PASS_VERIFIED" for g in REQUIRED}) for v in self.record["cases"]]
        self.assertEqual(exit_decision(x),"SIMULATION_ONLY_NO_AUTHORIZED_FINISH")
if __name__=="__main__": unittest.main()
