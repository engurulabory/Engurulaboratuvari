"""Zulfikar V1.3.1 single-authority, two strictly sequenced goals."""
import copy
import json
import subprocess
import sys
from pathlib import Path
import unittest

import zulfikar_v131_single_acceptance as engine
import zulfikar_v131_operational_bridge as bridge

HERE=Path(__file__).resolve().parent
class SingleAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc,cls.pin=bridge.source_read(bridge.ROOT,engine.CONTRACT)
        cls.bind,cls.bhash=bridge.source_read(bridge.ROOT,bridge.BINDING_PATH)
        cls.actions,cls.ahash=bridge.source_read(bridge.ROOT,bridge.ACTION_PATH)
        cls.head=bridge.head_sha(bridge.ROOT)
    def clone(self):return copy.deepcopy(self.doc)
    def accept(self,doc=None,bindings=None,actions=None):
        return engine.calculate(doc if doc is not None else self.doc,self.head,
            {engine.CONTRACT:self.pin,bridge.BINDING_PATH:self.bhash,bridge.ACTION_PATH:self.ahash},
            bindings if bindings is not None else self.bind,
            actions if actions is not None else self.actions)
    def broken(self,modify,flag):
        x=self.clone();modify(x)
        out=self.accept(x)
        self.assertFalse(out["contractValid"])
        self.assertIn(flag,out["faults"])
        self.assertEqual(out["officialVerifiedFinish"],"HOLD")
        self.assertNotEqual(out["goal2"],"PASS")

    def test_one_source_six_exact_domains(self):
        o=self.accept()
        self.assertTrue(o["contractValid"])
        self.assertEqual(len(o["sixDomains"]),6)
        self.assertEqual(o["singleAcceptanceSource"],engine.CONTRACT)
        self.assertEqual(tuple(d["recordedScore"] for d in o["sixDomains"]),engine.OBSERVED)

    def test_goal2_remains_locked(self):
        r=self.accept();self.assertTrue(r["goal2"].startswith("LOCKED"))
        self.assertEqual(r["goal1"],"HOLD_REAL_TASK_AND_OWNER_AUTHORITY")
        self.assertEqual(r["officialVerifiedFinish"],"HOLD")

    def test_source_registries_are_real_existing(self):
        o=self.accept()
        self.assertEqual(len(o["existingExecutorPaths"]),3)
        self.assertTrue(all(p["binding"]["matchingExistingRegistry"] for p in o["existingExecutorPaths"]))

    def test_bindings_do_not_authenticate_dispatch(self):
        for p in self.accept()["existingExecutorPaths"]:
            self.assertIs(p["binding"]["specificTaskAuthorityGranted"],False)
            self.assertIs(p["binding"]["actualHandlerInvoked"],False)
            self.assertIs(p["binding"]["registeredActionIsNotProductAcceptance"],True)

    def test_closure_operations_exact(self):
        o=self.accept()
        self.assertEqual(len(o["operations"]),3)
        self.assertEqual(tuple(t["id"] for t in o["operations"]),engine.CLOSURES)
        self.assertEqual(tuple(t["dimension"] for t in o["operations"]),engine.OPEN)
        self.assertTrue(all(t["closed"] is False for t in o["operations"]))

    def test_six_frozen_scores_cannot_auto_raise(self):
        self.broken(lambda x:x["domains"][3].update(review=100),"FROZEN_SIX_DOMAIN_BASELINE_DRIFT")

    def test_weights_cannot_change(self):
        self.broken(lambda x:x["domains"][3].update(weight=5),"FROZEN_SIX_DOMAIN_BASELINE_DRIFT")

    def test_91_not_relabelled_pass(self):
        self.broken(lambda x:x.update(overallOperationalVerdict="PASS"),"WEIGHTED_SCORE_AUTHORITY_DRIFT")

    def test_unauthorized_six_pass(self):
        self.broken(lambda x:x.update(allSixDimensionsPass=True),"FALSE_CANONICAL_FINISH")

    def test_unauthorized_six_100(self):
        self.broken(lambda x:x.update(allSixDimensions100=True),"FALSE_CANONICAL_FINISH")

    def test_auth_grant_faked(self):
        self.broken(lambda x:x["canonicalClosure"]["strictFinish"].update(ownerAccepted=True),"REAL_FINISH_UNJUSTIFIED")

    def test_fake_3_of_3_tasks(self):
        self.broken(lambda x:x["canonicalClosure"]["strictFinish"].update(realMacTaskPasses=3),"REAL_FINISH_UNJUSTIFIED")

    def test_new_issuer_forbidden(self):
        self.broken(lambda x:x["canonicalClosure"]["protected"].update(noSecondIssuer=False),"PROTECTED_AUTHORITY_DRIFT")

    def test_payment_forbidden(self):
        self.broken(lambda x:x["canonicalClosure"]["protected"].update(zeroAdditionalPaidServices=False),"PROTECTED_AUTHORITY_DRIFT")

    def test_single_writer_cannot_expand(self):
        self.broken(lambda x:x["canonicalClosure"]["protected"].update(oneActiveEngineeringWriter=False),"PROTECTED_AUTHORITY_DRIFT")

    def test_phase_order_must_be_preserved(self):
        self.broken(lambda x:x["canonicalClosure"]["phaseSequence"].reverse(),"PHASE_SEQUENCE_DRIFT")

    def test_goal2_cannot_unlock_from_manifest(self):
        self.broken(lambda x:x["canonicalClosure"].update(goal2State="PASS"),"PREMATURE_GOAL2_UNLOCK")

    def test_real_donecheck_required(self):
        self.broken(lambda x:x["canonicalClosure"]["strictFinish"].update(existingDoneCheck="PASS"),"REAL_FINISH_UNJUSTIFIED")

    def test_forged_official_finish(self):
        self.broken(lambda x:x.update(verifiedFinishVerdict="PASS"),"FALSE_CANONICAL_FINISH")

    def test_duplicate_task_identity_rejected(self):
        self.broken(lambda x:x["canonicalClosure"]["pilotProfiles"][2].update(
            taskId=x["canonicalClosure"]["pilotProfiles"][0]["taskId"]),"PILOT_SCOPE_OR_IDENTITY_DRIFT")

    def test_task_family_cannot_swap(self):
        self.broken(lambda x:x["canonicalClosure"]["pilotProfiles"][0].update(family="OTHER"),"PILOT_SCOPE_OR_IDENTITY_DRIFT")

    def test_required_evidence_cannot_be_empty(self):
        self.broken(lambda x:x["canonicalClosure"]["closureOperations"][2].update(requiredEvidence=[]),"CLOSURE_TARGET_OR_HOLD_DRIFT")

    def test_no_false_case_for_new_handler(self):
        b=copy.deepcopy(self.bind)
        for x in b["bindings"]:
            if x.get("CAPABILITY_ID")=="BUILD":
                x["REGISTERED_HANDLER"]="FAKE_BINDING"
        got=self.accept(bindings=b)
        self.assertIn("EXISTING_ACTION_BINDING_NOT_VERIFIED",got["faults"])
        self.assertEqual(got["officialVerifiedFinish"],"HOLD")

    def test_no_false_case_for_new_action(self):
        a=copy.deepcopy(self.actions)
        a["actions"]["PACKAGE08_CAP07_BUILD_FIELD_PROOF"]["authority"]="FORGED"
        got=self.accept(actions=a)
        self.assertIn("EXISTING_ACTION_BINDING_NOT_VERIFIED",got["faults"])

    def test_real_action_is_bounded_build_scope(self):
        p=self.accept()["existingExecutorPaths"][0]
        self.assertIn("NOT PiLive production binary",p["scope"])
        self.assertFalse(p["binding"]["specificTaskAuthorityGranted"])

    def test_no_overwriting_main_or_source(self):
        x=self.accept()
        self.assertFalse(x["workflow"]["mainWriterCreated"])
        self.assertFalse(x["workflow"]["newIssuerCreated"])
        self.assertFalse(x["workflow"]["remotePush"])

    def test_current_task_is_one_hinge(self):
        self.assertIn("PiLive",self.accept()["nextSingleAction"])

    def test_cli_status_is_source_bound_and_hold(self):
        x=subprocess.run([sys.executable,"-B",str(HERE/"zulfikar_v131_single_acceptance.py"),
                          "--mode","status"],cwd=HERE,text=True,capture_output=True,timeout=20)
        self.assertEqual(x.returncode,0,x.stdout+x.stderr)
        result=json.loads(x.stdout)
        self.assertEqual(result["goal1"],"HOLD_REAL_TASK_AND_OWNER_AUTHORITY")
        self.assertEqual(result["officialVerifiedFinish"],"HOLD")
        self.assertTrue(result["contractValid"])

    def test_cli_plan_never_dispatches(self):
        x=subprocess.run([sys.executable,"-B",str(HERE/"zulfikar_v131_single_acceptance.py"),
                          "--mode","plan"],cwd=HERE,text=True,capture_output=True,timeout=20)
        self.assertEqual(x.returncode,0,x.stdout+x.stderr)
        result=json.loads(x.stdout)
        self.assertEqual(result["mode"],"READ_ONLY_EXISTING_OPERATOR_HANDOFF_PLAN")
        self.assertEqual(result["threeHeterogeneousRealTasksAccepted"],0)
        self.assertFalse(result["realMacExecutionAuthenticated"])

if __name__=="__main__":
    unittest.main(verbosity=2)
