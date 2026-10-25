#!/usr/bin/env python3
"""Counter-tests for operational Zulfikar goal and infra gates."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from test_zulfikar_v1_2 import golden
from zulfikar_v1_2_engine import assess
from zulfikar_v1_3_gates import HERE, GOAL_IDS, INFRA_IDS, score, goal_gate, dag_ok


class TestGoalGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline=json.loads((HERE/"ZULFIKAR_GOAL_V1_3.json").read_text(encoding="utf8"))

    def test_real_canonical_and_frozen_goal_100(self):
        got=goal_gate(self.baseline)
        self.assertEqual(got["verdict"],"GOAL_SPECIFICATION_100_CANDIDATE")
        self.assertEqual(got["assessment"]["score"],100)
        self.assertEqual(tuple(sorted(got["assessment"]["checks"])),GOAL_IDS)
        self.assertEqual(got["human_authority"],"HOLD")

    def test_ten_fail_closed_goal_mutations(self):
        mutations=[
          lambda x:x.update(single_goal=""),
          lambda x:x.update(user_value=""),
          lambda x:x["controls"].pop(),
          lambda x:x["authority"].update(issuer="NEW_SIGNATURE"),
          lambda x:x["dependencies"]["C01"].append("C10"),
          lambda x:x["risks"].clear(),
          lambda x:x["negative_cases"].clear(),
          lambda x:x["controls"][2].update(state="PASS_UNPROVEN"),
          lambda x:x["canonical"].update(v3_sha256="b"*64),
          lambda x:x.update(osi_field="PASS"),
        ]
        for i,corrupt in enumerate(mutations):
            with self.subTest(gate=i+1):
                altered=copy.deepcopy(self.baseline);corrupt(altered)
                got=goal_gate(altered)
                self.assertEqual(got["verdict"],"HOLD_GOAL_SPECIFICATION")
                self.assertIn(GOAL_IDS[i],got["assessment"]["open_ids"])
                self.assertLess(got["assessment"]["score"],100)

    def test_structural_goal_schema_fail_closed(self):
        for bad in (None,{},[],False,"bad"):
            with self.subTest(bad=bad):
                self.assertLess(goal_gate(bad)["assessment"]["score"],100)

    def test_dag_cycle_and_unknown_reference(self):
        dependencies=self.baseline["dependencies"]
        self.assertTrue(dag_ok(dependencies,set(dependencies)))
        broken=copy.deepcopy(dependencies);broken["C01"]=["C10"]
        self.assertFalse(dag_ok(broken,set(broken)))
        broken=copy.deepcopy(dependencies);broken["C02"]=["UNKNOWN"]
        self.assertFalse(dag_ok(broken,set(broken)))

    def test_immutable_denominators(self):
        self.assertEqual(len(GOAL_IDS),10)
        self.assertEqual(len(INFRA_IDS),10)
        full=score({k:True for k in GOAL_IDS})
        self.assertEqual(full["score"],100)
        partial=score({k:k!="H04" for k in GOAL_IDS})
        self.assertEqual(partial["score"],90)
        self.assertEqual(partial["open_ids"],["H04"])


class TestOperationalCommands(unittest.TestCase):
    def call(self,command,stdin=None):
        return subprocess.run([sys.executable,"-B",str(HERE/"zulfikar_v1_3_gates.py"),command],
                              input=stdin,capture_output=True,text=True,timeout=20)

    def test_status_available_without_side_effects(self):
        r=self.call("status")
        self.assertEqual(r.returncode,0,r.stderr)
        data=json.loads(r.stdout)
        self.assertEqual(data["official_finish"],"HOLD")

    def test_goal_command_real_json(self):
        r=self.call("goal")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout)["assessment"]["score"],100)

    def test_assess_real_cli_roundtrip(self):
        fixture=golden()
        r=self.call("assess",json.dumps(fixture))
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout),assess(fixture))
        self.assertFalse(json.loads(r.stdout)["eligible_for_automatic_signature"])

    def test_bad_inputs_rejected(self):
        for raw in ("{bad","[]","{}"):
            with self.subTest(raw=raw):
                r=self.call("assess",raw)
                self.assertEqual(r.returncode,2)
                self.assertIn(json.loads(r.stdout)["state"],("HOLD_INVALID_INPUT","SIMULATED_HOLD"))

    def test_output_determinism(self):
        self.assertEqual(self.call("goal").stdout,self.call("goal").stdout)


if __name__=="__main__":
    unittest.main(verbosity=2)
