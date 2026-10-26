"""Real isolated subprocess test of the user-goal locked Zulfikar repair loop.

All writes are limited to disposable TemporaryDirectory fixtures, not project sources.
"""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

import zulfikar_v131_iterative_loop as loop


class LiveLoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.goal={"goalId":"ZULFIKAR.LOOP.TEST","stage":"PREPARATION",
                   "targetScore":100,"checkIds":["A","B","C"]}
        self.state={"checks":{"A":False,"B":False,"C":False},
                    "workspace":str(self.root),"revision":0}
        self.target=self.root/"task.json"
        self.target.write_text(json.dumps(self.state["checks"],sort_keys=True),encoding="utf8")
        self.order=[]
        self.last_patched=[]

    def assess(self,state,goal):
        self.order.append("ASSESS")
        self.assertEqual(goal,self.goal)
        actual=json.loads((Path(state["workspace"])/"task.json").read_text(encoding="utf8"))
        self.assertEqual(state["checks"],actual)
        return copy.deepcopy(state["checks"])

    def simulate(self,state,goal):
        self.order.append("SIMULATE")
        if sorted(state["checks"])!=sorted(goal["checkIds"]):
            return {"status":"HOLD_SIMULATION"}
        return {"status":"PASS_SIMULATION"}

    def repair(self,state,gaps,goal):
        self.order.append("REPAIR")
        self.last_patched.append(gaps)
        state["checks"][gaps[0]]=True
        state["revision"]+=1
        (Path(state["workspace"])/"task.json").write_text(
          json.dumps(state["checks"],sort_keys=True),encoding="utf8")
        return state

    def real_test(self,state,goal):
        self.order.append("REAL_TEST")
        script=("import json,hashlib,sys,pathlib;"
                "p=pathlib.Path(sys.argv[1]);"
                "expected=json.loads(sys.argv[2]);"
                "actual=json.loads(p.read_bytes());"
                "assert actual==expected;"
                "print(hashlib.sha256(p.read_bytes()).hexdigest())")
        cmd=[sys.executable,"-B","-c",script,str(Path(state["workspace"])/"task.json"),
             json.dumps(state["checks"],sort_keys=True)]
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=15,check=False)
        return {"exitCode":p.returncode,
                "actualSubprocessObserved":True,
                "receiptSha256":p.stdout.strip()}

    def verify(self,state,goal,receipt):
        self.order.append("VERIFY")
        if type(receipt) is not dict or receipt.get("exitCode")!=0:
            return False
        content=(Path(state["workspace"])/"task.json").read_bytes()
        return receipt.get("receiptSha256")==hashlib.sha256(content).hexdigest()

    def run(self,rounds=3):
        return loop.run(self.goal,self.state,self.assess,self.simulate,
                        self.repair,self.real_test,self.verify,max_rounds=rounds)

    def test_three_real_repair_and_test_rounds(self):
        r=self.run()
        self.assertEqual(r["decision"],"STAGE_100_CANDIDATE_EXTERNAL_ACCEPTANCE_REQUIRED")
        self.assertEqual([h["afterAssessment"]["diagnostic"] for h in r["history"]],[33,66,100])
        self.assertEqual(len(self.last_patched),3)
        self.assertEqual(json.loads(self.target.read_text()),{"A":True,"B":True,"C":True})
        self.assertIsNone(r["acceptedScore"])
        self.assertFalse(r["stagePassIssued"])

    def test_order_simulation_before_first_score_and_resimulation_after_real_test(self):
        self.run(1)
        self.assertEqual(self.order[:8],["SIMULATE","ASSESS","REPAIR","REAL_TEST","VERIFY",
                                           "SIMULATE","ASSESS"])

    def test_real_subprocess_was_used_each_round(self):
        r=self.run()
        self.assertEqual(sum(h["afterRealTest"]["actualSubprocessObserved"] is True for h in r["history"]),3)

    def test_no_more_repairs_after_candidate100(self):
        self.run()
        self.assertEqual(len(self.last_patched),3)

    def test_goal_is_immutable_even_if_callback_mutates_user_dict(self):
        def corrupt(state,goal):
            self.goal["goalId"]="CORRUPTED"
            return {"status":"PASS_SIMULATION"}
        r=loop.run(self.goal,self.state,self.assess,corrupt,self.repair,self.real_test,self.verify,3)
        self.assertEqual(r["holdReason"],"GOAL_IDENTITY_CHANGED")

    def test_incomplete_rounds_continue_without_passing(self):
        r=self.run(2)
        self.assertEqual(r["decision"],"CONTINUE_IMPROVEMENT")
        self.assertEqual(r["holdReason"],"ITERATION_LIMIT")
        self.assertEqual(len(r["history"]),2)
        self.assertIsNone(r["acceptedScore"])

    def test_zero_repair_return_prevents_infinite_noop(self):
        def no_change(state,gaps,goal):
            return state
        r=loop.run(self.goal,self.state,self.assess,self.simulate,
                   no_change,self.real_test,self.verify,3)
        self.assertEqual(r["holdReason"],"NO_AUTHORIZED_REPAIR_OR_PROGRESS")

    def test_failed_real_process_forces_hold(self):
        def bad_test(state,goal):
            return {"exitCode":1,"actualSubprocessObserved":True}
        r=loop.run(self.goal,self.state,self.assess,self.simulate,
                   self.repair,bad_test,self.verify,3)
        self.assertEqual(r["holdReason"],"REAL_TEST_OR_INDEPENDENT_MECHANISM_FAILED")

    def test_missing_process_proof_forces_hold(self):
        def fabricated(state,goal):
            return {"exitCode":0,"actualSubprocessObserved":False}
        r=loop.run(self.goal,self.state,self.assess,self.simulate,
                   self.repair,fabricated,lambda *_:True,3)
        self.assertEqual(r["holdReason"],"REAL_TEST_OR_INDEPENDENT_MECHANISM_FAILED")

    def test_refused_independent_mechanism_forces_hold(self):
        r=loop.run(self.goal,self.state,self.assess,self.simulate,
                   self.repair,self.real_test,lambda *_:False,3)
        self.assertEqual(r["holdReason"],"REAL_TEST_OR_INDEPENDENT_MECHANISM_FAILED")

    def test_refused_first_simulation(self):
        r=loop.run(self.goal,self.state,self.assess,
                   lambda *_:{"status":"HOLD_SIMULATION"},
                   self.repair,self.real_test,self.verify,3)
        self.assertEqual(r["holdReason"],"SIMULATION_FAILED")

    def test_refused_resimulation(self):
        calls=[0]
        def sim(state,goal):
            calls[0]+=1
            return {"status":"PASS_SIMULATION" if calls[0]==1 else "HOLD_SIMULATION"}
        r=loop.run(self.goal,self.state,self.assess,sim,
                   self.repair,self.real_test,self.verify,3)
        self.assertEqual(r["holdReason"],"RESIMULATION_FAILED")

    def test_bad_check_ids_fail_closed(self):
        def assess(state,goal):
            return {"A":True}
        r=loop.run(self.goal,self.state,assess,self.simulate,
                   self.repair,self.real_test,self.verify,3)
        self.assertEqual(r["holdReason"],"INVALID_SOURCE_OR_OPERATOR_RESULT")

    def test_int_instead_bool_check_fail_closed(self):
        def assess(state,goal):
            return {"A":1,"B":False,"C":False}
        r=loop.run(self.goal,self.state,assess,self.simulate,
                   self.repair,self.real_test,self.verify,3)
        self.assertEqual(r["holdReason"],"INVALID_SOURCE_OR_OPERATOR_RESULT")

    def test_fake_acceptance_not_issued_even_if_initial_100(self):
        self.state["checks"]={k:True for k in self.goal["checkIds"]}
        self.target.write_text(json.dumps(self.state["checks"],sort_keys=True),encoding="utf8")
        r=self.run()
        self.assertEqual(r["decision"],"STAGE_100_CANDIDATE_EXTERNAL_ACCEPTANCE_REQUIRED")
        self.assertEqual(len(r["history"]),1)
        self.assertFalse(r["history"][0]["repairApplied"])
        self.assertIsNone(r["acceptedScore"])

    def test_product_stage_requires_real_owner(self):
        self.goal["stage"]="PRODUCT_FINISH"
        r=self.run()
        self.assertEqual(r["officialVerifiedFinish"],"AWAIT_AUTHORIZED_DONECHECK_HUMAN_THRESHOLD")
        self.assertFalse(r["stagePassIssued"])

    def test_empty_goal_fails(self):
        self.goal["checkIds"]=[]
        self.assertEqual(self.run()["holdReason"],"INVALID_GOAL_OR_HANDLERS")

    def test_duplicate_check_id_fails(self):
        self.goal["checkIds"]=["A","A"]
        self.assertEqual(self.run()["holdReason"],"INVALID_GOAL_OR_HANDLERS")

    def test_bad_target_not_100_fails(self):
        self.goal["targetScore"]=99
        self.assertEqual(self.run()["holdReason"],"INVALID_GOAL_OR_HANDLERS")

    def test_boolean_maxrounds_is_invalid(self):
        self.assertEqual(self.run(True)["holdReason"],"INVALID_GOAL_OR_HANDLERS")

    def test_bad_stage_fails(self):
        self.goal["stage"]="FORGED_STAGE"
        self.assertEqual(self.run()["holdReason"],"INVALID_GOAL_OR_HANDLERS")

    def test_beyond_budget_fails(self):
        self.assertEqual(self.run(13)["holdReason"],"INVALID_GOAL_OR_HANDLERS")

    def test_regression_after_repair_is_rejected(self):
        self.state["checks"]["A"]=True
        self.target.write_text(json.dumps(self.state["checks"],sort_keys=True),encoding="utf8")
        def regression(state,gaps,goal):
            state["checks"]["A"]=False
            state["checks"]["B"]=True
            self.target.write_text(json.dumps(state["checks"],sort_keys=True),encoding="utf8")
            state["revision"]+=1
            return state
        r=loop.run(self.goal,self.state,self.assess,self.simulate,
                   regression,self.real_test,self.verify,3)
        self.assertEqual(r["holdReason"],"REGRESSION_AFTER_REPAIR")

    def test_invalid_patch_does_not_create_stage_pass(self):
        def invalid(state,gaps,goal):
            return ["BAD"]
        r=loop.run(self.goal,self.state,self.assess,self.simulate,
                   invalid,self.real_test,self.verify,3)
        self.assertEqual(r["holdReason"],"INVALID_SOURCE_OR_OPERATOR_RESULT")

    def test_digest_is_stable_for_key_order(self):
        self.assertEqual(loop.digest({"a":1,"b":2}),loop.digest({"b":2,"a":1}))

if __name__=="__main__":
    unittest.main(verbosity=2)
