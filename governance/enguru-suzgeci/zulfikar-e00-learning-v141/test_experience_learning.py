"""Adversarial and real subprocess tests for the E00 adapter + existing DÖM."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from experience_learning import (
    SCHEMA, SCOPE, experience_plan, run_isolated_learning
)


class E00Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.source = root / "source.txt"
        self.source.write_text("AUTHORITATIVE_SOURCE", encoding="utf8")
        self.artifact = root / "artifact.json"
        self.artifact.write_text('{"ok":false}', encoding="utf8")
        self.journal = root / "journal"
        self.journal.mkdir()
        self.event = {
            "schema": SCHEMA, "eventId": "E00-TEST-001",
            "goalId": "ZF-LOCAL-001", "userValue": "Repair actual disposable output",
            "sourceSha256": hashlib.sha256(self.source.read_bytes()).hexdigest(),
            "scope": SCOPE, "kind": "FAILURE", "need": "RELIABILITY",
            "criteria": ["artifact_correct"],
            "observedCriteria": {"artifact_correct": False},
            "lesson": "Reverify repaired output before a checkpoint",
        }
        self.calls = []
        self.initial_state = {"artifactPath": str(self.artifact), "fixed": False}

    def evaluate(self, state, contract):
        self.calls.append("evaluate")
        row = json.loads(self.artifact.read_text())
        return {"artifact_correct": row["ok"] is True and state["fixed"] is True}

    def simulate(self, state, contract):
        return {"valid": True}

    def repair(self, state, missing, contract):
        self.calls.append("repair")
        self.artifact.write_text('{"ok":true}', encoding="utf8")
        state["fixed"] = True
        return state

    def run_real_test(self, state, contract):
        self.calls.append("process")
        run = subprocess.run(
            [sys.executable, "-B", "-c",
             "import hashlib,pathlib,sys;print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())",
             str(self.artifact)],
            capture_output=True, text=True, timeout=10, check=False)
        return {
            "processObserved": True, "exitCode": run.returncode,
            "artifactPath": str(self.artifact), "artifactSha256": run.stdout.strip(),
            "scope": SCOPE,
        }

    def verify(self, state, contract, proof):
        self.calls.append("verify")
        return (proof["artifactSha256"] ==
                hashlib.sha256(self.artifact.read_bytes()).hexdigest() and
                json.loads(self.artifact.read_text())["ok"] is True)

    def run_cycle(self, **overrides):
        args = dict(event=self.event, source_file=self.source,
                    journal_folder=self.journal, start_state=self.initial_state,
                    simulator=self.simulate, evaluator=self.evaluate,
                    repairer=self.repair, real_tester=self.run_real_test,
                    independent_verifier=self.verify, source_probe=lambda _: True,
                    max_rounds=2)
        args.update(overrides)
        return run_isolated_learning(**args)

    def test_01_valid_failure_becomes_plan_not_pass(self):
        p = experience_plan(self.event, self.source)
        self.assertEqual(p["state"], "E00_REPAIR_TASK_CANDIDATE")
        self.assertEqual(p["reportedMissingCriteria"], ["artifact_correct"])
        self.assertFalse(p["officialPassIssued"])
        self.assertFalse(p["observationIndependentlyVerified"])

    def test_02_local_real_process_repairs_and_proves_candidate(self):
        r = self.run_cycle()
        self.assertEqual(r["state"], "E00_ISOLATED_TEST_CANDIDATE")
        self.assertEqual(r["diagnostic"], 100)
        self.assertTrue(r["realTestObserved"])
        self.assertEqual(json.loads(self.artifact.read_text()), {"ok": True})
        self.assertIn("process", self.calls)
        self.assertIn("verify", self.calls)
        self.assertEqual(len(r["journalHeadSha256"]), 64)
        self.assertFalse(r["officialPassIssued"])
        self.assertEqual(r["productVerifiedFinish"], "NOT_ISSUED")

    def test_03_wrong_source_sha_is_hold(self):
        self.event["sourceSha256"] = "0" * 64
        self.assertEqual(self.run_cycle()["state"], "HOLD_INVALID_EXPERIENCE")
        self.assertEqual(self.calls, [])

    def test_04_changed_actual_source_is_hold(self):
        self.source.write_text("MUTATED", encoding="utf8")
        self.assertEqual(self.run_cycle()["state"], "HOLD_INVALID_EXPERIENCE")
        self.assertEqual(self.calls, [])

    def test_05_reported_all_true_is_no_change_not_pass(self):
        self.event["observedCriteria"] = {"artifact_correct": True}
        r = self.run_cycle()
        self.assertEqual(r["state"], "E00_NO_CHANGE_REPORTED")
        self.assertFalse(r["officialPassIssued"])
        self.assertEqual(self.calls, [])

    def test_06_extra_observation_criterion_rejected(self):
        self.event["observedCriteria"]["invented"] = True
        self.assertEqual(self.run_cycle()["state"], "HOLD_INVALID_EXPERIENCE")

    def test_07_int_is_not_boolean_proof(self):
        self.event["observedCriteria"]["artifact_correct"] = 1
        self.assertEqual(self.run_cycle()["state"], "HOLD_INVALID_EXPERIENCE")

    def test_08_missing_event_field_rejected(self):
        del self.event["lesson"]
        self.assertEqual(self.run_cycle()["state"], "HOLD_INVALID_EVENT_SCHEMA")

    def test_09_illegal_scope_rejected(self):
        self.event["scope"] = "AUTONOMOUS_PRODUCTION"
        self.assertEqual(self.run_cycle()["state"], "HOLD_INVALID_EXPERIENCE")

    def test_10_unknown_need_rejected(self):
        self.event["need"] = "SELF_APPROVED"
        self.assertEqual(self.run_cycle()["state"], "HOLD_INVALID_EXPERIENCE")

    def test_11_unhashable_kind_fails_closed(self):
        self.event["kind"] = ["FAILURE"]
        self.assertEqual(self.run_cycle()["state"], "HOLD_INVALID_EXPERIENCE")

    def test_12_repair_callback_without_progress_is_hold(self):
        result = self.run_cycle(repairer=lambda state, *_: state)
        self.assertEqual(result["state"], "E00_REPAIR_HOLD")
        self.assertFalse(result["realTestObserved"])

    def test_13_forged_independent_verifier_is_hold(self):
        result = self.run_cycle(independent_verifier=lambda *_: False)
        self.assertEqual(result["state"], "E00_REPAIR_HOLD")
        self.assertFalse(result["officialPassIssued"])

    def test_14_four_rounds_rejected(self):
        result = self.run_cycle(max_rounds=4)
        self.assertEqual(result["state"], "HOLD_UNBOUNDED_REPAIR")
        self.assertEqual(self.calls, [])

    def test_15_non_integer_round_count_rejected(self):
        result = self.run_cycle(max_rounds=True)
        self.assertEqual(result["state"], "HOLD_UNBOUNDED_REPAIR")
        self.assertEqual(self.calls, [])

    def test_16_duplicate_criteria_rejected(self):
        self.event["criteria"] = ["artifact_correct", "artifact_correct"]
        self.assertEqual(self.run_cycle()["state"], "HOLD_INVALID_EXPERIENCE")

    def test_17_no_unverified_bypass_on_output_tamper(self):
        def verifier_then_tamper(state, contract, run):
            good = self.verify(state, contract, run)
            if good:
                self.artifact.write_text('{"ok":false}', encoding="utf8")
            return good
        r = self.run_cycle(independent_verifier=verifier_then_tamper)
        self.assertEqual(r["state"], "E00_REPAIR_HOLD")
        self.assertFalse(r["officialPassIssued"])

    def test_18_positive_experience_without_gap_does_not_rewrite(self):
        self.event["kind"] = "SUCCESS"
        self.event["observedCriteria"]["artifact_correct"] = True
        r = self.run_cycle()
        self.assertEqual(r["state"], "E00_NO_CHANGE_REPORTED")
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
