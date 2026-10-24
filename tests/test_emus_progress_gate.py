import copy
import json
from pathlib import Path
import unittest
from tools.emus_progress_gate import inspect

PATH=Path(__file__).resolve().parents[1]/"governance/emus/EMUS_V11_SUBCRITERION_PROGRESS_V1.json"
class EvidenceGateTests(unittest.TestCase):
    def setUp(self):self.data=json.loads(PATH.read_text(encoding="utf-8"))
    def test_baseline_counts(self):
        r=inspect(self.data)
        self.assertEqual(r["state"],"PASS_REVIEW_MAPPING_ONLY",r["errors"])
        self.assertEqual(r["counts"]["evidenced_total"],sum(c["state"]!="HOLD_UNVERIFIED" for row in self.data["rows"] for c in row["criteria"]))
        self.assertEqual(len(r["evidence_map"]),r["counts"]["evidenced_total"])
        self.assertEqual(r["counts"]["official_accepted_tasks"],0)
    def test_seven_adversarial_mutations(self):
        mutations=[
          lambda d:d["counting_rules"].__setitem__("evidenced_total",16),
          lambda d:d["rows"][0]["criteria"][0].__setitem__("id","GH-01-C2"),
          lambda d:d["rows"][0]["criteria"][1].__setitem__("evidence_run",None),
          lambda d:d["rows"][8]["criteria"][1].__setitem__("evidence_sha256","invalid"),
          lambda d:d["counting_rules"].__setitem__("official_accepted_tasks",1),
          lambda d:d.__setitem__("status","CANONICAL"),
          lambda d:d["rows"][1]["criteria"][0].__setitem__("state","PASS"),
        ]
        for change in mutations:
            with self.subTest(change=repr(change)):
                case=copy.deepcopy(self.data);change(case)
                self.assertEqual(inspect(case)["state"],"HOLD")
    def test_execution_authority_separation(self):
        result=inspect(self.data)
        self.assertEqual(result["CI_RUN_STATUS"],"EXTERNAL_VERIFICATION_REQUIRED")
        self.assertEqual(result["LIVE_ROUTER"],"HOLD")
        self.assertEqual(result["VERIFIED_FINISH"],"HOLD")
