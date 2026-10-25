"""Adversarial checks for the GitHub-only hybrid contract preflight."""
import copy
import json
import unittest
from unittest.mock import patch
import os
import selectors
import subprocess
import sys
import tempfile
from pathlib import Path
from validate_hybrid_handoff import (validate, source_snapshot, assess_project,
                                     simulate_project, independent_source_check)

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "governance/mac-engineer/ENGURU_MAC_ENGINEER_HYBRID_HANDOFF_TEMPLATE_V1.json"


class HybridValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_template_is_valid(self):
        self.assertEqual(validate(self.base), [])

    def test_wrong_schema_fails(self):
        x = copy.deepcopy(self.base)
        x["schema"] = "other"
        self.assertIn("SCHEMA_MISMATCH", validate(x))

    def test_premature_lock_fails(self):
        x = copy.deepcopy(self.base)
        x["verifiedFinish"] = "LOCKED"
        self.assertIn("GITHUB_CANNOT_LOCK_OSI_VERIFIED_FINISH", validate(x))

    def test_missing_suzgec_fails(self):
        x = copy.deepcopy(self.base)
        x.pop("suzgec")
        self.assertIn("SUZGEC_DECISION_SEQUENCE_MISSING", validate(x))

    def test_unsupported_pass_fails(self):
        x = copy.deepcopy(self.base)
        x["suzgec"]["judgment"] = "PASS"
        self.assertIn("UNSUPPORTED_PASS", validate(x))

    def test_missing_project_identity_fails(self):
        self.assertIn("PROJECT_IDENTITY_MISSING", validate(self.base, mode="handoff"))

    def test_invalid_mode_fails(self):
        x = self._handoff()
        x["executionMode"] = "MAGIC"
        self.assertIn("EXECUTION_MODE_INVALID", validate(x, mode="handoff"))

    def test_invalid_digest_fails(self):
        x = self._handoff()
        x["artifactDigest"] = "not-a-digest"
        self.assertIn("ARTIFACT_DIGEST_INVALID", validate(x, mode="handoff"))

    def test_github_cannot_attest_osi_field(self):
        x = self._handoff()
        x["fieldReceipt"]["osiFieldState"] = "PASS"
        self.assertIn("GITHUB_FIELD_ATTESTATION_FORBIDDEN", validate(x, mode="handoff"))

    def test_scoped_handoff_is_valid_but_not_locked(self):
        self.assertEqual(validate(self._handoff(), mode="handoff"), [])

    def _handoff(self):
        x = copy.deepcopy(self.base)
        x.update(projectId="sample", subproduct="sample", executionMode="HYBRID",
                 canonicalRepo="owner/repo", sourceRef="refs/heads/main",
                 sourceCommit="a" * 40, artifactDigest="b" * 64)
        return x

    def test_malformed_nested_fields_hold_instead_of_crashing(self):
        for field in (None, [], "PASS", 1):
            x = self._handoff()
            x["fieldReceipt"] = field
            self.assertIn("FIELDRECEIPT_MISSING", validate(x, mode="handoff"))
        x = self._handoff()
        x["executionMode"] = []
        self.assertIn("EXECUTION_MODE_INVALID", validate(x, mode="handoff"))
        self.assertEqual(validate(x, mode="unknown"), ["MODE_INVALID"])

    def test_handoff_shape_cannot_claim_finish(self):
        x = self._handoff()
        for claim in ("PASS", "VERIFIED_FINISH", True):
            x["verifiedFinish"] = claim
            self.assertIn("GITHUB_FINISH_AUTHORITY_HOLD", validate(x, mode="handoff"))


class ProjectPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "source"
        self.source.mkdir()
        self.run_git(self.source, "init", "-b", "main")
        self.run_git(self.source, "config", "user.name", "Preparation Test")
        self.run_git(self.source, "config", "user.email", "test@example.invalid")
        self.run_git(self.source, "remote", "add", "origin", "https://github.com/fixture/project.git")
        (self.source / "keep.txt").write_text("first\n")
        self.run_git(self.source, "add", ".")
        self.run_git(self.source, "commit", "-m", "first")
        (self.source / "keep.txt").write_text("second\n")
        self.run_git(self.source, "commit", "-am", "second")
        self.run_git(self.source, "branch", "preserved")
        self.data = json.loads((ROOT / "tools/hybrid_handoff/labory-osi-project.example.json").read_text())
        snap = source_snapshot(self.source)
        self.data.update(canonicalRepo="fixture/project", sourceCommit=snap["commit"],
                         artifactDigest=snap["artifactDigest"])
        self.data["projectPlan"]["refsDigest"] = snap["refsDigest"]

    @staticmethod
    def run_git(root, *args):
        return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE, timeout=15)

    def test_normal_three_stage_preparation_keeps_authority_hold(self):
        before = source_snapshot(self.source)
        result = simulate_project(self.data, self.source)
        self.assertEqual(result["state"], "PASS_GITHUB_PREPARATION_5X100")
        self.assertEqual(result["scores"], {key: 100 for key in
            ("THEORY", "DESIGN", "SIM1", "SIM2", "SIM3")})
        self.assertEqual(result["gates"]["PREPARED"], "PASS")
        self.assertEqual(result["nextAction"], "STOP_FOR_OSI_READ_ONLY_PREFLIGHT_AND_HUMAN_DECISION")
        self.assertEqual(len(result["cases"]), 11)
        self.assertTrue(all(x["observed"] == x["expected"] for x in result["cases"]))
        self.assertEqual(result["baseline"]["scores"], {d: 20 for d in
            ("scope", "feasibility", "resilience", "authoritySafety", "provability")})
        self.assertEqual(result["baseline"]["gates"], {"PREPARED": "HOLD", "FIELD_READY": "HOLD",
            "HUMAN_AUTHORIZED": "HOLD", "VERIFIED_FINISH": "HOLD"})
        self.assertEqual(result["independentCommittedBytes"], "PASS")
        self.assertEqual(source_snapshot(self.source), before)

    def test_empty_handoff_shape_is_not_preparation(self):
        self.data.pop("projectPlan")
        self.assertEqual(validate(self.data, mode="handoff"), [])
        self.assertEqual(assess_project(self.data, self.source)["gates"]["PREPARED"], "HOLD")

    def test_every_preparation_requirement_is_fail_closed(self):
        keys = list(self.data["projectPlan"])
        for key in keys:
            x = copy.deepcopy(self.data)
            x["projectPlan"].pop(key)
            with self.subTest(key=key):
                self.assertEqual(assess_project(x, self.source)["gates"]["PREPARED"], "HOLD")
        for value in (None, [], "bad", 1):
            x = copy.deepcopy(self.data)
            x["projectPlan"] = value
            self.assertEqual(assess_project(x, self.source)["gates"]["PREPARED"], "HOLD")

    def test_duplicate_acceptance_dependency_cycles_and_budget_types_hold(self):
        for mutate in (
            lambda p: p["acceptance"].append(copy.deepcopy(p["acceptance"][0])),
            lambda p: p.update(dependencies=[{"id":"a","requires":["a"]}]),
            lambda p: p.update(dependencies=[{"id":"a","requires":["unknown"]}]),
            lambda p: p["budget"].update(paidApi=False),
            lambda p: p["budget"].update(purchases=1),
            lambda p: p["target"].update(collisionPolicy="OVERWRITE"),
        ):
            x = copy.deepcopy(self.data)
            mutate(x["projectPlan"])
            self.assertEqual(assess_project(x, self.source)["gates"]["PREPARED"], "HOLD")

    def test_real_dirty_bytes_head_refs_and_shallow_source_hold(self):
        (self.source / "keep.txt").write_text("changed\n")
        self.assertEqual(assess_project(self.data, self.source)["gates"]["PREPARED"], "HOLD")
        self.assertFalse(independent_source_check(
            dict(self.data, artifactDigest=source_snapshot(self.source)["artifactDigest"]), self.source))
        self.run_git(self.source, "checkout", "--", "keep.txt")
        self.run_git(self.source, "branch", "new-ref")
        self.assertEqual(assess_project(self.data, self.source)["gates"]["PREPARED"], "HOLD")
        self.run_git(self.source, "branch", "-D", "new-ref")
        shallow = Path(self.temp.name) / "shallow"
        subprocess.run(["git", "clone", "--depth=1", self.source.as_uri(), str(shallow)],
                       check=True, capture_output=True, timeout=15)
        snap = source_snapshot(shallow)
        x = copy.deepcopy(self.data)
        x["projectPlan"]["refsDigest"] = snap["refsDigest"]
        self.run_git(shallow, "remote", "set-url", "origin", "https://github.com/fixture/project.git")
        self.assertTrue(snap["shallow"])
        self.assertEqual(assess_project(x, shallow)["gates"]["PREPARED"], "HOLD")
        self.run_git(self.source, "checkout", "HEAD~1")
        self.assertEqual(assess_project(self.data, self.source)["gates"]["PREPARED"], "HOLD")

    def test_claimed_field_human_or_finish_never_promotes_authority(self):
        x = copy.deepcopy(self.data)
        x["humanAuthorityScope"].update(state="PASS", scope="all")
        result = assess_project(x, self.source)
        self.assertEqual(result["gates"]["HUMAN_AUTHORIZED"], "HOLD")
        x["verifiedFinish"] = "PASS"
        self.assertEqual(assess_project(x, self.source)["gates"]["PREPARED"], "HOLD")

    def test_two_identical_attempts_require_rediagnosis(self):
        attempt = {"hypothesis":"h", "intervention":"i", "evidenceDigest":"a"*64}
        x = copy.deepcopy(self.data)
        x["projectPlan"]["attempts"] = [attempt, copy.deepcopy(attempt)]
        result = assess_project(x, self.source)
        self.assertEqual(result["gates"]["PREPARED"], "HOLD")
        self.assertTrue(any("GÜVENLİ_DUR_REDIAGNOSE" in c["evidence"] for c in result["checks"]))
        x["projectPlan"]["attempts"][-1]["evidenceDigest"] = "b"*64
        self.assertEqual(assess_project(x, self.source)["structureReady"], "PASS")

    def test_critical_third_stage_archive_mismatch_holds_preparation(self):
        (self.source / ".gitattributes").write_text("keep.txt export-ignore\n")
        self.run_git(self.source, "add", ".gitattributes")
        self.run_git(self.source, "commit", "-m", "archive excludes a tracked file")
        snap = source_snapshot(self.source)
        x = copy.deepcopy(self.data)
        x.update(sourceCommit=snap["commit"], artifactDigest=snap["artifactDigest"])
        x["projectPlan"]["refsDigest"] = snap["refsDigest"]
        self.assertEqual(assess_project(x, self.source)["structureReady"], "PASS")
        result = simulate_project(x, self.source)
        self.assertEqual(result["independentCommittedBytes"], "HOLD")
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["gates"]["PREPARED"], "HOLD")

    def test_structure_alone_is_not_github_prepared(self):
        result = assess_project(self.data, self.source)
        self.assertEqual(result["structureReady"], "PASS")
        self.assertEqual(result["preparationChecklistScore"], 100)
        self.assertEqual(result["gates"]["PREPARED"], "HOLD")
        self.assertEqual(result["nextAction"], "VERIFY_FIVE_INDEPENDENT_100_GATES")

    def test_any_one_global_five_axis_shortfall_holds_entire_handoff(self):
        for axis in ("THEORY", "DESIGN", "SIM1", "SIM2", "SIM3"):
            scores = {key: 100 for key in ("THEORY", "DESIGN", "SIM1", "SIM2", "SIM3")}
            scores[axis] = 99
            with self.subTest(axis=axis), patch(
                    "validate_hybrid_handoff.read_theoretical_main_balance",
                    return_value={"state": "HOLD", "scores": scores, "verdict": "HOLD_TEST"}):
                result = simulate_project(self.data, self.source)
                self.assertEqual(result["scores"][axis], 99)
                self.assertEqual(result["state"], "HOLD")
                self.assertEqual(result["gates"]["PREPARED"], "HOLD")
                self.assertEqual(result["gates"]["FIELD_READY"], "HOLD")

    def test_unavailable_theoretical_verifier_fails_closed(self):
        with patch("validate_hybrid_handoff.read_theoretical_main_balance",
                   return_value={"state": "HOLD",
                       "scores": {key: 0 for key in ("THEORY", "DESIGN", "SIM1", "SIM2", "SIM3")}}):
            result = simulate_project(self.data, self.source)
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(all(score == 0 for score in result["scores"].values()))
        self.assertEqual(result["gates"]["PREPARED"], "HOLD")

    def test_fake_input_scores_do_not_authorize_preparation(self):
        fake = copy.deepcopy(self.data)
        fake.update(scores={"THEORY": 100, "DESIGN": 100,
                            "SIM1": 100, "SIM2": 100, "SIM3": 100},
                    fieldReady=True, authorized=True)
        fake["projectPlan"]["tools"] = []
        self.assertEqual(simulate_project(fake, self.source)["state"], "HOLD")

    def test_actual_cli_exit_and_malformed_json(self):
        manifest = Path(self.temp.name) / "plan.json"
        command = [sys.executable, "-B", str(ROOT / "tools/hybrid_handoff/validate_hybrid_handoff.py"),
                   str(manifest), "--mode", "project", "--source-root", str(self.source)]
        manifest.write_text(json.dumps(self.data))
        run = subprocess.run(command, capture_output=True, text=True, timeout=15)
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        self.assertEqual(json.loads(run.stdout)["baseline"]["gates"]["VERIFIED_FINISH"], "HOLD")
        for raw in ('{"projectPlan":{},"projectPlan":{}}', '['*1500, 'null', '[]'):
            manifest.write_text(raw)
            run = subprocess.run(command, capture_output=True, text=True, timeout=15)
            self.assertEqual(run.returncode, 2, run.stderr + run.stdout)
            self.assertNotIn("Traceback", run.stderr)

    @unittest.skipUnless(os.name == "posix", "Requires SIGKILL")
    def test_real_git_staging_interruption_collision_replay_and_rollback(self):
        # Executes real Git in disposable local sandbox, independently of the
        # plan evaluator. This is not a Mac field test or an install utility.
        target = Path(self.temp.name) / "foreign-target"
        target.mkdir()
        (target / "foreign.txt").write_bytes(b"PRESERVE")
        staged = Path(self.temp.name) / "owned-staging"
        code = '''
import subprocess,sys
subprocess.run(["git","clone","--no-hardlinks",sys.argv[1],sys.argv[2]],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
print("STAGED_NOT_PUBLISHED",flush=True)
sys.stdin.read()
'''
        child = subprocess.Popen([sys.executable, "-B", "-c", code, str(self.source), str(staged)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(child.stdout, selectors.EVENT_READ)
                self.assertTrue(selector.select(timeout=15))
            self.assertEqual(child.stdout.readline().strip(), "STAGED_NOT_PUBLISHED")
            child.kill()
            child.communicate(timeout=10)
            self.assertEqual(child.returncode, -9)
        finally:
            if child.poll() is None:
                child.kill()
                child.communicate(timeout=10)
        for _ in range(2):
            self.run_git(staged, "fsck", "--full")
            self.assertTrue(independent_source_check(self.data, staged))
            self.assertEqual((target / "foreign.txt").read_bytes(), b"PRESERVE")
        # Retry clone refuses an existing path rather than replacing it.
        retry = subprocess.run(["git", "clone", str(self.source), str(target)], capture_output=True, timeout=15)
        self.assertNotEqual(retry.returncode, 0)
        self.assertEqual((target / "foreign.txt").read_bytes(), b"PRESERVE")
        import shutil
        shutil.rmtree(staged)  # Test-owned temporary staging only.
        self.assertFalse(staged.exists())
        self.assertEqual((target / "foreign.txt").read_bytes(), b"PRESERVE")
        print("PROJECT_REAL_GIT_SANDBOX=PASS; SIGKILL=PASS; REVERIFY_REPLAY=PASS; "
              "FOREIGN_COLLISION_PRESERVED=PASS; OWNED_STAGING_ROLLBACK=PASS; MAC_FIELD=NOT_EXECUTED")


if __name__ == "__main__":
    unittest.main()
