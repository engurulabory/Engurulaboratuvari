#!/usr/bin/env python3
"""Counter-tests for operational Zulfikar goal and infra gates."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_zulfikar_v1_2 import golden
from zulfikar_v1_2_engine import assess
from zulfikar_v1_3_gates import HERE, GOAL_IDS, INFRA_IDS, score, goal_gate, dag_ok, source_matches_checkout_head, root_matches


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
        self.assertEqual(self.baseline["authority"]["owner_id"],"engurulabory")
        self.assertIs(self.baseline["authority"]["peer_review_required"],False)
        self.assertEqual(self.baseline["authority"]["decision_scope"],"GITHUB_TECHNICAL_ACCEPTANCE_ONLY")
        self.assertEqual(
            {c["id"]:c["authority"] for c in self.baseline["controls"]},
            {f"C{i:02d}": ("Human Threshold" if i in (4,10)
                          else "Automated GitHub CI") for i in range(1,11)},
        )

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

    def test_non_text_and_unhashable_inputs_hold_without_crash(self):
        injections=[
          ("goal_id_number", lambda x: x.update(goal_id=17), "H01"),
          ("goal_text_number", lambda x: x.update(single_goal=17), "H01"),
          ("value_list", lambda x: x.update(user_value=["fake"]), "H02"),
          ("metric_not_text", lambda x: x["measurement"].update(metric=["fake"]), "H02"),
          ("unhashable_control_id", lambda x: x["controls"][0].update(id=[]), "H03"),
          ("unhashable_dag_reference", lambda x: x["dependencies"]["C02"].append([]), "H05"),
        ]
        for label,corrupt,expected_gate in injections:
            with self.subTest(case=label):
                altered=copy.deepcopy(self.baseline)
                corrupt(altered)
                got=goal_gate(altered)
                self.assertEqual(got["verdict"],"HOLD_GOAL_SPECIFICATION")
                self.assertIn(expected_gate,got["assessment"]["open_ids"])

    def test_dag_unhashable_reference_fail_closed(self):
        for item in ([],{},42,None):
            with self.subTest(item=repr(item)):
                broken=copy.deepcopy(self.baseline["dependencies"])
                broken["C02"].append(item)
                self.assertFalse(dag_ok(broken,set(broken)))

    def test_fixed_original_control_ids_survive_consistent_rewrite_attack(self):
        altered=copy.deepcopy(self.baseline)
        altered["controls"][0]["id"]="C11"
        altered["dependencies"]={
            ("C11" if k=="C01" else k):
            [("C11" if dep=="C01" else dep) for dep in val]
            for k,val in altered["dependencies"].items()
        }
        result=goal_gate(altered)
        self.assertEqual(result["verdict"],"HOLD_GOAL_SPECIFICATION")
        self.assertIn("H03",result["assessment"]["open_ids"])

    def test_acceptance_identity_and_typed_evidence_fail_closed(self):
        injections=[
          ("goal_id_rewrite",lambda x:x.update(goal_id="OTHER-GOAL"),"H01"),
          ("nontext_acceptance",lambda x:x["controls"][0].update(acceptance=42),"H03"),
          ("nontext_verifier",lambda x:x["controls"][0].update(verifier=["self"]),"H03"),
          ("nontext_authority",lambda x:x["controls"][0].update(authority=1),"H03"),
          ("nontext_risk",lambda x:x["risks"][0].update(mitigation={"fake":"claim"}),"H06"),
          ("duplicated_negative",lambda x:x["negative_cases"][1].update(case_id=x["negative_cases"][0]["case_id"]),"H07"),
          ("lost_negative",lambda x:x["negative_cases"][0].update(case_id="OTHER_CASE"),"H07"),
          ("nontext_evidence",lambda x:x["controls"][0].update(evidence_source=["fake"]),"H08"),
          ("bool_budget",lambda x:x["budget"].update(paid_api=False),"H10"),
        ]
        for label,mutate,expected in injections:
            with self.subTest(label=label):
                altered=copy.deepcopy(self.baseline)
                mutate(altered)
                result=goal_gate(altered)
                self.assertEqual(result["verdict"],"HOLD_GOAL_SPECIFICATION")
                self.assertIn(expected,result["assessment"]["open_ids"])

    def test_fixed_verifier_mapping_and_authority_class(self):
        corruptions=[
            ("verifier_forged", "C01", "verifier", "fake.check.H01"),
            ("verifier_swapped", "C02", "verifier", "goal_gate.H01"),
            ("ci_turned_owner", "C03", "authority", "Human Threshold"),
            ("ci_turned_fake_peer", "C03", "authority", "Independent reviewer"),
            ("human_turned_reviewer", "C04", "authority", "Independent reviewer"),
            ("last_human_turns_reviewer", "C10", "authority", "Independent reviewer"),
        ]
        for label,identity,key,alteration in corruptions:
            with self.subTest(label=label):
                modified=copy.deepcopy(self.baseline)
                next(c for c in modified["controls"] if c["id"]==identity)[key]=alteration
                verdict=goal_gate(modified)
                self.assertEqual(verdict["verdict"],"HOLD_GOAL_SPECIFICATION")
                self.assertIn("H03",verdict["assessment"]["open_ids"])

    def test_solo_maintainer_scope_and_identity_fail_closed(self):
        changes=[
            ("owner_id_forged",lambda x:x["authority"].update(owner_id="stranger"),"H04"),
            ("review_mode_removed",lambda x:x["authority"].pop("review_mode"),"H04"),
            ("review_mode_peer_only",lambda x:x["authority"].update(review_mode="PEER_REQUIRED"),"H04"),
            ("scope_forged",lambda x:x["authority"].update(decision_scope="VERIFIED_FINISH"),"H04"),
            ("peer_requirement_changed",lambda x:x["authority"].update(peer_review_required=True),"H04"),
            ("peer_requirement_nonboolean",lambda x:x["authority"].update(peer_review_required=0),"H04"),
            ("canonical_issuer_forged",lambda x:x["authority"].update(issuer="SOLO_OWNER_ISSUER"),"H04"),
            ("schema_drift",lambda x:x.update(schema="enguru.zulfikar.goal-contract/v1.3"),"H01"),
            ("negative_case_removed",lambda x:x["negative_cases"].pop(),"H07"),
        ]
        for name,mutate,gate in changes:
            with self.subTest(case=name):
                altered=copy.deepcopy(self.baseline)
                mutate(altered)
                result=goal_gate(altered)
                self.assertEqual(result["verdict"],"HOLD_GOAL_SPECIFICATION")
                self.assertIn(gate,result["assessment"]["open_ids"])
                self.assertEqual(result["human_authority"],"HOLD")

    def test_canonical_lock_requires_object_and_digest(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            v3=root/"V3.md"
            v3.write_bytes(b"canonical gate test")
            sha=hashlib.sha256(v3.read_bytes()).hexdigest()
            lock=root/"V3_LOCK.json"
            with (patch("zulfikar_v1_3_gates.V3",v3),
                  patch("zulfikar_v1_3_gates.LOCK",lock),
                  patch("zulfikar_v1_3_gates.V3_PIN",sha)):
                lock.write_text(json.dumps({"sha256":sha}),encoding="utf8")
                self.assertTrue(root_matches())
                for corrupt in ([],[{"sha256":sha}],None,"bad",True,{},{"sha256":"0"*64}):
                    with self.subTest(lock=repr(corrupt)):
                        lock.write_text(json.dumps(corrupt),encoding="utf8")
                        self.assertFalse(root_matches())

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

    def test_exact_git_head_source_bytes_and_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            source=root/"source.txt"
            source.write_text("trusted bytes",encoding="utf8")
            subprocess.run(["git","-C",folder,"init","-q"],check=True)
            subprocess.run(["git","-C",folder,"add","source.txt"],check=True)
            subprocess.run(
              ["git","-C",folder,"-c","user.name=ENGURU Test",
               "-c","user.email=local-test@example.invalid",
               "commit","-qm","source pin"],check=True,
            )
            self.assertTrue(source_matches_checkout_head(root,(source,)))
            source.write_text("modified bytes",encoding="utf8")
            self.assertFalse(source_matches_checkout_head(root,(source,)))
            source.unlink()
            self.assertFalse(source_matches_checkout_head(root,(source,)))

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
