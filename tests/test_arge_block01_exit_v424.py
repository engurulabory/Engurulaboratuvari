"""Block 01 evidence-matrix exit replay — review-only."""
import json
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_EVIDENCE_MATRIX_V424.json"
TASK_IDS={f"A{i:02d}" for i in range(1,10)}
REQUIRED={"independent_e5","g01_external_effect","g02_relational_authorization","g03_temporal_knowledge","k12_measured_roi_tco","kasifi_canonical_identity","a03_scope_bound_grant","independent_reviewer","authorized_donecheck"}

def exit_gate(data):
    if set(data.get("tasks",{}))!=TASK_IDS:return "HOLD"
    if not REQUIRED.issubset(data.get("reconciled",{})):return "HOLD"
    if any(v.get("official")!="PASS" or v.get("authority")!="PASS" for v in data["tasks"].values()):return "HOLD"
    if any(data["reconciled"][k]!="PASS" for k in REQUIRED):return "HOLD"
    return "SIMULATED_CANDIDATE_ONLY"

class Block01ExitReplay(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(PATH.read_text(encoding="utf8"))
    def test_current_exit_holds(self):
        self.assertEqual(exit_gate(self.data),"HOLD")
        self.assertEqual(self.data["official_pass"],"0/9")
    def test_each_task_missing_holds(self):
        for k in TASK_IDS:
            with self.subTest(task=k):
                d={**self.data,"tasks":{x:dict(v,official="PASS",authority="PASS") for x,v in self.data["tasks"].items()},"reconciled":{x:"PASS" for x in REQUIRED}}
                d["tasks"][k]["official"]="HOLD"
                self.assertEqual(exit_gate(d),"HOLD")
    def test_each_critical_evidence_missing_holds(self):
        for k in REQUIRED:
            with self.subTest(field=k):
                d={**self.data,"tasks":{x:dict(v,official="PASS",authority="PASS") for x,v in self.data["tasks"].items()},"reconciled":{x:"PASS" for x in REQUIRED}}
                d["reconciled"][k]="HOLD"
                self.assertEqual(exit_gate(d),"HOLD")
    def test_positive_fixture_not_authorization(self):
        d={**self.data,"tasks":{x:dict(v,official="PASS",authority="PASS") for x,v in self.data["tasks"].items()},"reconciled":{x:"PASS" for x in REQUIRED}}
        self.assertEqual(exit_gate(d),"SIMULATED_CANDIDATE_ONLY")

if __name__=="__main__":unittest.main()
