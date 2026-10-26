"""Executable local tests; all artefacts live in temporary private directories."""
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from engine import Contract, LocalJournal, assess, execute, sha, GATES


class CycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.record = self.root / "actual-output.json"
        self.record.write_text(json.dumps({"A": False, "B": False, "C": False, "D": False}, sort_keys=True))
        self.state = {"location": str(self.record), "checks": {"A": False, "B": False, "C": False, "D": False}}
        self.source = self.root / "pinned_goal_source.txt"
        self.source.write_text("VERIFIED_GOAL_SOURCE", encoding="utf8")
        self.goal = Contract("REAL_TEST_GOAL", "Finish four concrete verified outputs", "T01", tuple(self.state["checks"]), hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.journal = LocalJournal(self.root)
        self.calls = []

    def simulate(self, state, goal):
        self.calls.append("simulate")
        return {"valid": True, "scenario": "READ_ONLY_PREDICTION"}

    def evaluate(self, state, goal):
        self.calls.append("assess")
        real = json.loads(Path(state["location"]).read_text())
        return {c: (real[c] is True and state["checks"][c] is True) for c in goal["criteria"]}

    def repair(self, state, gaps, goal):
        self.calls.append("repair")
        state["checks"][gaps[0]] = True
        Path(state["location"]).write_text(json.dumps(state["checks"], sort_keys=True))
        return state

    def real_test(self, state, goal):
        self.calls.append("real-test")
        path = Path(state["location"])
        # Native OS SHA process, independent of in-process Python state; a
        # second in-process verifier separately checks semantic correctness.
        command = (["sha256sum", str(path)] if shutil.which("sha256sum") else
                   ["shasum", "-a", "256", str(path)])
        p = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return {"processObserved": True, "exitCode": p.returncode, "scope": "LOCAL_DISPOSABLE_PROOF", "artifactSha256": p.stdout.split()[0] if p.returncode == 0 else ""}

    def verify(self, state, goal, receipt):
        self.calls.append("verify")
        raw = Path(state["location"]).read_bytes()
        return receipt["artifactSha256"] == hashlib.sha256(raw).hexdigest() and json.loads(raw) == state["checks"]

    def source_probe(self, goal_record):
        return hashlib.sha256(self.source.read_bytes()).hexdigest() == goal_record["sourcePin"]

    def drive(self, rounds=4, **replacement):
        ops = {"simulator": self.simulate, "evaluator": self.evaluate, "repairer": self.repair,
               "real_tester": self.real_test, "independent_verifier": self.verify, "source_probe": self.source_probe}
        ops.update(replacement)
        return execute(self.goal, self.state, self.journal, max_rounds=rounds, source_file=self.source, **ops)

    def test_01_four_real_repair_cycles(self):
        x = self.drive()
        self.assertEqual(x["state"], "STAGE_100_CANDIDATE_EXTERNAL_REVIEW_REQUIRED")
        self.assertEqual([r["afterDiagnostic"] for r in x["rounds"]], [25,50,75,100])
        self.assertFalse(x["stagePassIssued"])

    def test_02_order_of_first_round(self):
        self.drive(1)
        self.assertEqual(self.calls[:7], ["simulate","assess","repair","real-test","verify","simulate","assess"])

    def test_03_limited_cycles_continue(self):
        x=self.drive(2)
        self.assertEqual(x["reason"], "BOUNDED_CYCLE_CONTINUE")
        self.assertEqual(len(x["rounds"]), 2)

    def test_04_no_owner_issuer_or_field_pass(self):
        x=self.drive()
        self.assertIsNone(x["acceptedScore"])
        self.assertEqual(x["productVerifiedFinish"], "NOT_ISSUED")
        self.assertFalse(x["executorAuthorityCreated"])

    def test_05_real_subprocess_four_times(self):
        self.drive()
        self.assertEqual(self.calls.count("real-test"), 4)
        self.assertEqual(self.calls.count("verify"), 4)

    def test_06_journal_is_hash_chained(self):
        self.drive()
        self.assertEqual(len(LocalJournal(self.root).events), 4)
        self.assertTrue(all(len(e["hash"]) == 64 for e in self.journal.events))

    def test_07_detect_journal_payload_tamper(self):
        self.drive(1)
        changed=self.journal.path.read_text().replace('"afterDiagnostic":25', '"afterDiagnostic":99')
        self.journal.path.write_text(changed)
        with self.assertRaises(ValueError):LocalJournal(self.root)

    def test_08_detect_concurrent_writer_drift(self):
        self.drive(1)
        other=LocalJournal(self.root)
        other.append({"contractSha256": "spoofed", "stateSha256": "invalid"})
        with self.assertRaises(ValueError): self.journal.append({"a":1})

    def test_09_resume_requires_same_contract(self):
        self.drive(1)
        self.goal=Contract("CHANGED", self.goal.goal_text, "T01", self.goal.criteria, "a"*64)
        x=self.drive()
        self.assertEqual(x["reason"], "CONTRACT_SWITCH_FORBIDDEN")

    def test_10_resume_rejects_unverified_initial_state(self):
        self.drive(1)
        x=self.drive()
        self.assertEqual(x["reason"], "RESUME_STATE_DIFFERS_FROM_VERIFIED_CHECKPOINT")

    def test_11_resume_after_partial_with_observed_state(self):
        first=self.drive(2)
        self.assertEqual(len(first["rounds"]),2)
        latest=json.loads(self.record.read_text())
        self.state["checks"]=latest
        second=self.drive(2)
        self.assertEqual(second["state"], "STAGE_100_CANDIDATE_EXTERNAL_REVIEW_REQUIRED")
        self.assertEqual(len(LocalJournal(self.root).events),4)

    def test_12_resume_100_is_idempotent(self):
        self.drive()
        self.state["checks"]=json.loads(self.record.read_text())
        count=len(self.calls)
        r=self.drive()
        self.assertTrue(r["replayedVerifiedCheckpoint"])
        self.assertEqual(self.calls[count:], ["verify", "assess"])

    def test_13_rejected_simulation(self):
        r=self.drive(simulator=lambda *_:{"valid":False})
        self.assertEqual(r["reason"],"SIMULATION_REJECTED")

    def test_14_resimulation_rejected(self):
        calls=[0]
        def bad(state,goal):
            calls[0]+=1
            return {"valid":calls[0]==1}
        self.assertEqual(self.drive(simulator=bad)["reason"],"RESIMULATION_REJECTED")

    def test_15_nonzero_real_test(self):
        self.assertEqual(self.drive(real_tester=lambda *_:{"exitCode":2,"processObserved":True,"scope":"LOCAL_DISPOSABLE_PROOF","artifactSha256":"a"*64})["reason"],"REAL_TEST_OR_INDEPENDENT_VERIFY_FAILED")

    def test_16_fake_subprocess_claim_missing(self):
        self.assertEqual(self.drive(real_tester=lambda *_:{"exitCode":0,"processObserved":False,"scope":"LOCAL_DISPOSABLE_PROOF","artifactSha256":"a"*64})["reason"],"REAL_TEST_OR_INDEPENDENT_VERIFY_FAILED")

    def test_17_unsafe_scope(self):
        self.assertEqual(self.drive(real_tester=lambda *_:{"exitCode":0,"processObserved":True,"scope":"REMOTE_MAC","artifactSha256":"a"*64})["reason"],"REAL_TEST_OR_INDEPENDENT_VERIFY_FAILED")

    def test_18_independent_verifier_rejects(self):
        self.assertEqual(self.drive(independent_verifier=lambda *_:False)["reason"],"REAL_TEST_OR_INDEPENDENT_VERIFY_FAILED")

    def test_19_nonprogress_repair_rejected(self):
        self.assertEqual(self.drive(repairer=lambda s,*_:s)["reason"],"REPAIR_INVALID_OR_NO_PROGRESS")

    def test_20_invalid_repair_type(self):
        self.assertEqual(self.drive(repairer=lambda *_:[1])["reason"],"REPAIR_INVALID_OR_NO_PROGRESS")

    def test_21_rollback_proven_gain_rejected(self):
        self.state["checks"]["A"]=True
        self.record.write_text(json.dumps(self.state["checks"]))
        def regression(s,g,c):
            s["checks"]["A"]=False
            s["checks"]["B"]=True
            self.record.write_text(json.dumps(s["checks"]))
            return s
        self.assertEqual(self.drive(repairer=regression)["reason"],"REPAIR_CAUSED_REGRESSION")

    def test_22_missing_criterion_rejected(self):
        self.assertEqual(self.drive(evaluator=lambda *_:{"A":True})["reason"],"SAFE_FAILURE_ValueError")

    def test_23_forged_integer_true_rejected(self):
        self.assertEqual(self.drive(evaluator=lambda *_:{c:1 for c in self.goal.criteria})["reason"],"SAFE_FAILURE_ValueError")

    def test_24_same_100_checks_also_require_test(self):
        self.state["checks"]={k:True for k in self.state["checks"]}
        self.record.write_text(json.dumps(self.state["checks"]))
        r=self.drive(1)
        self.assertEqual(r["state"],"STAGE_100_CANDIDATE_EXTERNAL_REVIEW_REQUIRED")
        self.assertEqual(self.calls.count("real-test"),1)

    def test_25_wrong_target_ids_rejected(self):
        self.goal=Contract("X","Y","FORGED_GATE",("A",),"a"*64)
        self.assertEqual(self.drive()["reason"],"SAFE_FAILURE_ValueError")

    def test_26_duplicate_criterion_rejected(self):
        self.goal=Contract("X","Y","T01",("A","A"),"a"*64)
        self.assertEqual(self.drive()["reason"],"SAFE_FAILURE_ValueError")

    def test_27_no_goal_text_rejected(self):
        self.goal=Contract("X","","T01",("A",),"a"*64)
        self.assertEqual(self.drive()["reason"],"SAFE_FAILURE_ValueError")

    def test_28_invalid_source_pin(self):
        self.goal=Contract("X","Y","T01",("A",),"NOT_SHA")
        self.assertEqual(self.drive()["reason"],"SAFE_FAILURE_ValueError")

    def test_29_forbid_other_execution_scope(self):
        self.goal=Contract("X","Y","T01",("A",),"a"*64,"MAC_NATIVE")
        self.assertEqual(self.drive()["reason"],"SAFE_FAILURE_ValueError")

    def test_30_reject_boolean_round_limit(self):
        self.assertEqual(self.drive(True)["reason"],"SAFE_FAILURE_ValueError")

    def test_31_reject_more_than_maximum(self):
        self.assertEqual(self.drive(13)["reason"],"SAFE_FAILURE_ValueError")

    def test_32_all_eight_gates_listed(self):
        self.assertEqual(GATES,("T01","T02","A01","A02","A03","A04","A05","A06"))

    def test_33_diagnostic_only_1_to_99(self):
        for n in range(1,100):
            d={str(i):i<n for i in range(100)}
            self.assertEqual(assess(d,list(d)),n)

    def test_34_journal_dir_link_rejected(self):
        target=self.root/"another"
        target.mkdir()
        l=self.root/"symlink"
        l.symlink_to(target, target_is_directory=True)
        with self.assertRaises(ValueError):LocalJournal(l)

    def test_36_source_sha_is_checked_from_real_bytes(self):
        self.source.write_text("TAMPERED")
        self.assertEqual(self.drive()["reason"], "ACTUAL_SOURCE_DIGEST_MISMATCH")

    def test_37_source_drift_during_test_rejected(self):
        def tampering_test(state, goal):
            proof=self.real_test(state, goal)
            self.source.write_text("CHANGED_AFTER_TEST")
            return proof
        result=self.drive(real_tester=tampering_test)
        self.assertEqual(result["reason"], "SOURCE_CHANGED_DURING_REAL_TEST")
        self.assertIsNone(result["acceptedScore"])

    def test_38_source_change_after_resimulation_prevents_checkpoint(self):
        counter=[0]
        def altered_second_simulation(state,goal):
            counter[0]+=1
            if counter[0] == 2:
                self.source.write_text("CHANGED_IN_RESIMULATION")
            return {"valid":True}
        outcome=self.drive(simulator=altered_second_simulation)
        self.assertEqual(outcome["reason"], "SOURCE_CHANGED_BEFORE_CHECKPOINT")
        self.assertEqual(len(self.journal.events),0)

    def test_35_checkpoint_has_actual_state_sha(self):
        self.drive(1)
        e=self.journal.events[-1]["payload"]
        self.assertEqual(e["stateSha256"],sha({"location":str(self.record),"checks":json.loads(self.record.read_text())}))

if __name__ == "__main__":
    unittest.main(verbosity=2)
