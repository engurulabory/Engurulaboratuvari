"""Zülfikar V1.4.1 HYM T01+T02: real Git evidence and three fail-closed simulations."""
import copy
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest
from tools import arge_hym_v141_crosswalk_v1 as m


def actual_records():
    root=m.ROOT
    handoff=json.loads((root/m.HANDOFF).read_text(encoding="utf8"))
    cases=json.loads((root/m.CASES).read_text(encoding="utf8"))
    return handoff,cases


def method_scope():
    return {"state":"PASS_METHOD_SOURCE_CROSSWALK_ONLY",
            "verifiedFinish":"HOLD",
            "stageAcceptance":{s:"HOLD_STAGE_100_EVIDENCE_REQUIRED" for s in m.STAGES}}


class HYMT01T02ReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h,cls.c=actual_records()
        cls.proof=m.proof_from_git()

    def check(self,h=None,c=None,proof=None,method=None):
        return m.assess_foundations(
            self.h if h is None else h,
            self.c if c is None else c,
            self.proof if proof is None else proof,
            method_scope() if method is None else method)

    def test_actual_head_files_and_canonical_v3_are_verified(self):
        self.assertEqual(self.proof["state"],"PASS_GIT_HEAD_SOURCE_BYTES_ONLY",
                         self.proof.get("reason"))
        self.assertEqual(len(self.proof["files"]),7)
        self.assertEqual(len(self.proof["head"]),40)
        self.assertEqual(self.proof["files"][m.FOUNDATION_SOURCE_PATHS[1]]["sha256"],m.V3_SHA)

    def test_t01_and_t02_source_preparation_100_but_official_is_hold(self):
        result=self.check()
        self.assertEqual(result["state"],"PASS_T01_T02_GITHUB_SOURCE_PREPARATION_ONLY")
        self.assertEqual(result["T01"]["score"],100)
        self.assertEqual(result["T02"]["score"],100)
        self.assertEqual(result["stagesAccepted"],{"T01":"HOLD","T02":"HOLD"})
        self.assertEqual(result["originalOfficial"],"0/40")
        self.assertEqual(result["independentE5"],"0/18")
        self.assertEqual(result["verifiedFinish"],"HOLD")

    def test_sim1_goal_owner_source_failure(self):
        cases=(
          ("goal",lambda d:d["governance"].update(fixed_goal="OTHER_GOAL"),"F01_goal_identity"),
          ("owner",lambda d:d["solo_owner_github_preparation_v2"].update(approved_owner="fictitious"),"F03_owner_scope"),
          ("official",lambda d:d["current_counters"].update(overall_official="40/40"),"F04_protected_assets"),
        )
        for name,alter,gate in cases:
            with self.subTest(name=name):
                h=copy.deepcopy(self.h);alter(h)
                score=self.check(h=h)
                self.assertEqual(score["T01"]["state"],"HOLD")
                self.assertFalse(score["T01"]["checks"][gate])
                self.assertEqual(score["verifiedFinish"],"HOLD")

    def test_sim2_contract_cases_and_dependencies(self):
        for name,alter,gate in (
          ("ids",lambda d:d["single_active_execution_queue"][0]["scope"].pop(),"G02_original_ids"),
          ("order",lambda d:d["single_active_execution_queue"][0].update(id="22"),"G04_dependency_order"),
          ("block",lambda d:d["preserved_scope"].update(chosen=["A01"]),"G01_fixed_target"),
        ):
            with self.subTest(name=name):
                h=copy.deepcopy(self.h);alter(h)
                outcome=self.check(h=h)
                self.assertEqual(outcome["T02"]["state"],"HOLD")
                self.assertFalse(outcome["T02"]["checks"][gate])

    def test_sim3_external_authority_and_missing_method_proof(self):
        for name,alter,gate in (
          ("fake_deployment",lambda d:d["A05_A06"].update(customer_deployment="18/18"),"F05_initial_risks"),
          ("fake_donecheck",lambda d:d["solo_owner_github_preparation_v2"].update(
              official_donecheck_issuer="INVENTED"),"G05_safe_stop"),
        ):
            with self.subTest(name=name):
                h=copy.deepcopy(self.h);alter(h)
                out=self.check(h=h)
                self.assertFalse(out["T01"]["checks"].get(gate,True)
                                 and out["T02"]["checks"].get(gate,True))
                self.assertEqual(out["verifiedFinish"],"HOLD")
        for fake in (
          {"state":"FAKE_PASS","verifiedFinish":"HOLD","stageAcceptance":method_scope()["stageAcceptance"]},
          {"state":"PASS_METHOD_SOURCE_CROSSWALK_ONLY","verifiedFinish":"PASS",
           "stageAcceptance":method_scope()["stageAcceptance"]},
          {"state":"PASS_METHOD_SOURCE_CROSSWALK_ONLY","verifiedFinish":"HOLD",
           "stageAcceptance":{}},
        ):
            with self.subTest(fake=fake):
                self.assertEqual(self.check(method=fake)["T02"]["state"],"HOLD")

    def test_real_git_head_mutation_rejected_after_disposable_commit(self):
        with tempfile.TemporaryDirectory(prefix="hym-foundation-proof-") as folder:
            root=pathlib.Path(folder)
            for rel in m.FOUNDATION_SOURCE_PATHS:
                dest=root/rel
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(m.ROOT/rel,dest)
            for args in (
                ["git","init","-q"],
                ["git","add","."],
                ["git","-c","user.name=Proof Test","-c",
                 "user.email=proof@example.invalid","commit","-qm","controlled source snapshot"],
            ):
                subprocess.run(args,cwd=root,check=True,capture_output=True,timeout=15)
            self.assertEqual(m.proof_from_git(root)["state"],"PASS_GIT_HEAD_SOURCE_BYTES_ONLY")
            target=root/m.FOUNDATION_SOURCE_PATHS[-1]
            target.write_bytes(target.read_bytes()+b"\nunauthorized source delta")
            changed=m.proof_from_git(root)
            self.assertEqual(changed["state"],"HOLD")
            self.assertIn("SOURCE_GIT_HEAD_BYTES_DRIFT",changed["reason"])

    def test_missing_source_or_malformed_shapes_safe_hold(self):
        for invalid in (
           {"state":"PASS_GIT_HEAD_SOURCE_BYTES_ONLY","files":{}},
           {"state":"HOLD","files":{}},
        ):
            self.assertEqual(self.check(proof=invalid)["T01"]["state"],"HOLD")
        for invalid in ({},[],False):
            self.assertEqual(m.assess_foundations(invalid,self.c,self.proof,method_scope())["state"],
                             "HOLD_FOUNDATION_SOURCE_PREPARATION")

if __name__=="__main__":
    unittest.main()
