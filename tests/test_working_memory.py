import tempfile
import unittest

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
