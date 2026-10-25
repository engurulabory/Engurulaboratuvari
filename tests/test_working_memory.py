import tempfile
import unittest
import json
import os
from pathlib import Path
import signal
import selectors
import subprocess
import sys

from shared_ai.working_memory import (
    GovernedLearningPromotion,
    PersistentWorkingMemory,
    WorkingMemoryError,
)


class PersistentWorkingMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.memory = PersistentWorkingMemory(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def create_task(self):
        return self.memory.create_task(
            task_id="task-001",
            objective="Repair the verified repository with the smallest safe change.",
            authority_snapshot={"mode": "SAFE_AUTO", "human_threshold": ["merge"]},
            required_capabilities=("git", "tests", "evidence"),
        )

    def test_task_survives_process_style_reload_with_one_identity(self):
        created = self.create_task()
        reloaded = PersistentWorkingMemory(self.tmp.name).load_task("task-001")
        self.assertEqual(reloaded.task_id, created.task_id)
        self.assertEqual(reloaded.objective, created.objective)
        self.assertEqual(reloaded.authority_snapshot["mode"], "SAFE_AUTO")
        self.assertEqual(reloaded.required_capabilities, ("git", "tests", "evidence"))
        self.assertEqual(reloaded.state, "ACTIVE")
        self.assertEqual(reloaded.revision, 1)

    def test_stale_revision_cannot_overwrite_newer_truth(self):
        task = self.create_task()
        updated = self.memory.update_task(
            task.task_id,
            expected_revision=task.revision,
            evidence_refs=("test:pass",),
        )
        self.assertEqual(updated.revision, 2)
        with self.assertRaisesRegex(WorkingMemoryError, "stale_task_revision"):
            self.memory.update_task(
                task.task_id,
                expected_revision=1,
                evidence_refs=("stale:write",),
            )

    def test_checkpoint_resumes_after_store_restart(self):
        task = self.create_task()
        checkpointed = self.memory.update_task(
            task.task_id,
            expected_revision=task.revision,
            evidence_refs=("ci:123",),
            checkpoint={
                "checkpoint_id": "cp-001",
                "summary": "Patch applied and tests are green.",
                "next_action": "Run independent DoneCheck.",
                "evidence_refs": ["ci:123"],
            },
        )
        restarted = PersistentWorkingMemory(self.tmp.name)
        resumed = restarted.resume_task(task.task_id, checkpoint_id="cp-001")
        self.assertEqual(resumed.revision, checkpointed.revision)
        self.assertEqual(resumed.resume_checkpoint["next_action"], "Run independent DoneCheck.")
        self.assertIn("ci:123", resumed.evidence_refs)

    def test_human_decision_is_bound_to_authority_and_evidence(self):
        task = self.create_task()
        updated = self.memory.update_task(
            task.task_id,
            expected_revision=task.revision,
            human_decision={
                "decision": "APPROVE_DIRECTION",
                "authority": "HUMAN_ARTISTIC_AUTHORITY",
                "evidence_ref": "human:direction-7",
            },
        )
        self.assertEqual(updated.human_decisions[0]["decision"], "APPROVE_DIRECTION")
        self.assertIn("human:direction-7", updated.evidence_refs)

    def test_pass_final_outcome_requires_evidence(self):
        task = self.create_task()
        with self.assertRaisesRegex(WorkingMemoryError, "pass_requires_evidence"):
            self.memory.update_task(
                task.task_id,
                expected_revision=task.revision,
                state="PASS",
                reason="donecheck",
                final_summary="Finished.",
            )

    def test_final_pass_persists_and_cannot_resume_as_active_work(self):
        task = self.create_task()
        finished = self.memory.update_task(
            task.task_id,
            expected_revision=task.revision,
            state="PASS",
            reason="mandatory_donecheck_pass",
            evidence_refs=("donecheck:pass",),
            checkpoint={
                "checkpoint_id": "cp-final",
                "summary": "Verified finish recorded.",
                "next_action": "Archive task.",
            },
            final_summary="All scoped success criteria are evidenced.",
        )
        self.assertEqual(finished.final_outcome["verdict"], "PASS")
        with self.assertRaisesRegex(WorkingMemoryError, "task_already_verified_finish"):
            self.memory.resume_task(task.task_id, checkpoint_id="cp-final")

    def test_task_identity_blocks_path_traversal(self):
        with self.assertRaisesRegex(WorkingMemoryError, "invalid_task_id"):
            self.memory.create_task(
                task_id="../escape",
                objective="unsafe",
                authority_snapshot={"mode": "SAFE_AUTO"},
                required_capabilities=("git",),
            )

    def checkpoint_task(self):
        task = self.create_task()
        return self.memory.update_task(
            task.task_id, expected_revision=task.revision, state="HOLD",
            reason="checkpoint_saved", checkpoint={"checkpoint_id": "cp-restart",
                "summary": "Source checked; execution pending.",
                "next_action": "Resume one source-bound update."})

    def start_worker(self, mode="normal"):
        code = '''
import json, sys
from shared_ai.working_memory import PersistentWorkingMemory, WorkingMemoryError
memory = PersistentWorkingMemory(sys.argv[1])
mode = sys.argv[2]
if mode == "pause_after_read":
    original = memory.load_task
    def paused(task_id):
        value = original(task_id)
        print("CHECKPOINT_READ", flush=True)
        sys.stdin.readline()
        return value
    memory.load_task = paused
elif mode == "pause_after_commit":
    original = memory._write
    def paused(path, payload):
        original(path, payload)
        print("CHECKPOINT_COMMITTED", flush=True)
        sys.stdin.readline()
    memory._write = paused
try:
    result = memory.update_task("task-001", expected_revision=2, state="ACTIVE",
                                reason="resume_once", evidence_refs=("runtime:resume",))
    print(json.dumps({"state":"UPDATED", "revision":result.revision}), flush=True)
except WorkingMemoryError as error:
    print(json.dumps({"state":"HOLD", "reason":str(error)}), flush=True)
'''
        process = subprocess.Popen(
            [sys.executable, "-B", "-c", code, self.tmp.name, mode],
            cwd=Path(__file__).resolve().parents[1], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        def cleanup():
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=10)
        self.addCleanup(cleanup)
        return process

    def expect_marker(self, process, marker):
        with selectors.DefaultSelector() as ready:
            ready.register(process.stdout, selectors.EVENT_READ)
            self.assertTrue(ready.select(timeout=10), "Worker readiness timeout")
        self.assertEqual(process.stdout.readline().strip(), marker)

    @unittest.skipUnless(os.name == "posix", "POSIX process-lock acceptance")
    def test_two_processes_same_revision_commit_once(self):
        self.checkpoint_task()
        first = self.start_worker("pause_after_read")
        self.expect_marker(first, "CHECKPOINT_READ")
        second = self.start_worker()
        try:
            second_output, second_error = second.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            # A serialized writer waits while the first owns the revision.
            second_output = None
        first_output, first_error = first.communicate(input="continue\n", timeout=10)
        if second_output is None:
            second_output, second_error = second.communicate(timeout=10)
        self.assertEqual(first.returncode, 0, first_error)
        self.assertEqual(second.returncode, 0, second_error)
        outcomes = [json.loads(first_output), json.loads(second_output)]
        self.assertEqual(sum(row["state"] == "UPDATED" for row in outcomes), 1, outcomes)
        self.assertEqual(sum(row.get("reason") == "stale_task_revision" for row in outcomes), 1)
        raw = json.loads((Path(self.tmp.name) / "tasks/task-001.json").read_bytes())
        self.assertEqual(raw["revision"], 3)
        self.assertEqual(sum(t["reason"] == "resume_once" for t in raw["transitions"]), 1)
        self.assertEqual(raw["evidence_refs"], ["runtime:resume"])
        print("ENGINE_CONCURRENT_REPLAY=PASS; UPDATES=1; STALE_REJECTED=1; REVISION=3")

    @unittest.skipUnless(os.name == "posix", "Requires actual SIGKILL")
    def test_killed_writer_releases_lock_and_resumes_exact_checkpoint(self):
        self.checkpoint_task()
        path = Path(self.tmp.name) / "tasks/task-001.json"
        before = path.read_bytes()
        interrupted = self.start_worker("pause_after_read")
        self.expect_marker(interrupted, "CHECKPOINT_READ")
        os.kill(interrupted.pid, signal.SIGKILL)
        interrupted.communicate(timeout=10)
        self.assertEqual(interrupted.returncode, -signal.SIGKILL)
        self.assertEqual(path.read_bytes(), before)
        resumed = PersistentWorkingMemory(self.tmp.name).resume_task("task-001", checkpoint_id="cp-restart")
        self.assertEqual(resumed.revision, 2)
        retry = self.start_worker()
        output, error = retry.communicate(timeout=10)
        self.assertEqual(retry.returncode, 0, error)
        self.assertEqual(json.loads(output), {"state": "UPDATED", "revision": 3})
        replay = self.start_worker()
        output, error = replay.communicate(timeout=10)
        self.assertEqual(replay.returncode, 0, error)
        self.assertEqual(json.loads(output), {"state": "HOLD", "reason": "stale_task_revision"})
        self.assertEqual(json.loads(path.read_bytes())["revision"], 3)
        print("ENGINE_REAL_SIGKILL_RECOVERY=PASS; CHECKPOINT=cp-restart; REVISION=3; COMMITS=1")

    @unittest.skipUnless(os.name == "posix", "Requires actual SIGKILL")
    def test_lost_ack_after_commit_replay_preserves_single_update(self):
        self.checkpoint_task()
        path = Path(self.tmp.name) / "tasks/task-001.json"
        interrupted = self.start_worker("pause_after_commit")
        self.expect_marker(interrupted, "CHECKPOINT_COMMITTED")
        committed = path.read_bytes()
        os.kill(interrupted.pid, signal.SIGKILL)
        interrupted.communicate(timeout=10)
        self.assertEqual(interrupted.returncode, -signal.SIGKILL)
        replay = self.start_worker()
        output, error = replay.communicate(timeout=10)
        self.assertEqual(replay.returncode, 0, error)
        self.assertEqual(json.loads(output), {"state": "HOLD", "reason": "stale_task_revision"})
        self.assertEqual(path.read_bytes(), committed)
        self.assertEqual(json.loads(committed)["revision"], 3)
        print("ENGINE_LOST_ACK_RECOVERY=PASS; REPLAY=HOLD_STALE; COMMITTED_BYTES_PRESERVED=1")


class GovernedLearningPromotionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.learning = GovernedLearningPromotion(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_one_observation_never_becomes_canonical_learning(self):
        self.learning.create(
            learning_id="learn-001",
            producer_id="producer-a",
            observation_count=1,
        )
        with self.assertRaisesRegex(WorkingMemoryError, "repeated_observation_required"):
            self.learning.to_candidate("learn-001")

    def test_fresh_review_requires_independent_reviewer(self):
        self.learning.create(
            learning_id="learn-002",
            producer_id="producer-a",
            observation_count=3,
        )
        self.learning.to_candidate("learn-002")
        self.learning.attach_evidence(
            "learn-002",
            evidence_refs=("case:1", "case:2", "case:3"),
            benchmark_pass=True,
        )
        with self.assertRaisesRegex(WorkingMemoryError, "fresh_review_requires_independence"):
            self.learning.fresh_review(
                "learn-002",
                reviewer_id="producer-a",
                review_evidence=("review:1",),
            )

    def test_accept_requires_human_threshold_then_versioned_promotion(self):
        self.learning.create(
            learning_id="learn-003",
            producer_id="producer-a",
            observation_count=4,
        )
        self.learning.to_candidate("learn-003")
        self.learning.attach_evidence(
            "learn-003",
            evidence_refs=("case:1", "case:2", "case:3"),
            benchmark_pass=True,
        )
        self.learning.fresh_review(
            "learn-003",
            reviewer_id="reviewer-b",
            review_evidence=("fresh-review:pass",),
        )
        with self.assertRaisesRegex(WorkingMemoryError, "human_threshold_required"):
            self.learning.decide(
                "learn-003",
                decision="ACCEPT",
                reason="Repeated evidence is strong.",
                human_approved=False,
            )
        accepted = self.learning.decide(
            "learn-003",
            decision="ACCEPT",
            reason="Repeated evidence and independent review support promotion.",
            human_approved=True,
        )
        self.assertEqual(accepted.state, "ACCEPTED")
        promoted = self.learning.promote(
            "learn-003",
            version="v1.1",
            target="memory:responsive-repair",
        )
        self.assertEqual(promoted.state, "PROMOTED")
        self.assertEqual(promoted.promoted_version, "v1.1")
        reloaded = GovernedLearningPromotion(self.tmp.name).load("learn-003")
        self.assertEqual(reloaded.promoted_target, "memory:responsive-repair")

    def test_rejected_learning_cannot_be_promoted(self):
        self.learning.create(
            learning_id="learn-004",
            producer_id="producer-a",
            observation_count=3,
        )
        self.learning.to_candidate("learn-004")
        self.learning.attach_evidence(
            "learn-004",
            evidence_refs=("case:1",),
            benchmark_pass=True,
        )
        self.learning.fresh_review(
            "learn-004",
            reviewer_id="reviewer-b",
            review_evidence=("fresh-review:reject",),
        )
        rejected = self.learning.decide(
            "learn-004",
            decision="REJECT",
            reason="Cross-brief evidence shows overfitting.",
        )
        self.assertEqual(rejected.state, "REJECTED")
        with self.assertRaisesRegex(WorkingMemoryError, "learning_state_requires_accept"):
            self.learning.promote(
                "learn-004",
                version="v1.0",
                target="skill:bad-pattern",
            )


if __name__ == "__main__":
    unittest.main()
