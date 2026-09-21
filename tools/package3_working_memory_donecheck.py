from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared_ai.working_memory import (
    GovernedLearningPromotion,
    PersistentWorkingMemory,
    WorkingMemoryError,
)


def main() -> int:
    checks: list[dict[str, str]] = []

    with tempfile.TemporaryDirectory() as root:
        memory = PersistentWorkingMemory(root)
        task = memory.create_task(
            task_id="donecheck-task",
            objective="Verify Package 3 persistent working memory.",
            authority_snapshot={"mode": "SAFE_AUTO", "human_threshold": ["canonical_promotion"]},
            required_capabilities=("task_state", "evidence", "resume"),
        )
        checks.append({"check": "durable_task_identity", "state": "PASS"})

        task = memory.update_task(
            task.task_id,
            expected_revision=task.revision,
            evidence_refs=("unit:working-memory",),
            checkpoint={
                "checkpoint_id": "donecheck-cp",
                "summary": "State and evidence persisted.",
                "next_action": "Resume and finish.",
                "evidence_refs": ["unit:working-memory"],
            },
        )
        resumed = PersistentWorkingMemory(root).resume_task(
            task.task_id,
            checkpoint_id="donecheck-cp",
        )
        if resumed.task_id != task.task_id:
            raise AssertionError("task identity drift")
        checks.append({"check": "restart_resume", "state": "PASS"})

        try:
            memory.update_task(
                task.task_id,
                expected_revision=1,
                evidence_refs=("stale:write",),
            )
        except WorkingMemoryError as exc:
            if str(exc) != "stale_task_revision":
                raise
        else:
            raise AssertionError("stale write unexpectedly accepted")
        checks.append({"check": "stale_write_guard", "state": "PASS"})

        learning = GovernedLearningPromotion(root)
        learning.create(
            learning_id="donecheck-learning",
            producer_id="producer-a",
            observation_count=3,
        )
        learning.to_candidate("donecheck-learning")
        learning.attach_evidence(
            "donecheck-learning",
            evidence_refs=("case:1", "case:2", "case:3"),
            benchmark_pass=True,
        )
        learning.fresh_review(
            "donecheck-learning",
            reviewer_id="reviewer-b",
            review_evidence=("fresh-review:pass",),
        )
        accepted = learning.decide(
            "donecheck-learning",
            decision="ACCEPT",
            reason="Repeated evidence and fresh review support bounded promotion.",
            human_approved=True,
        )
        if accepted.state != "ACCEPTED":
            raise AssertionError("learning accept failed")
        promoted = learning.promote(
            "donecheck-learning",
            version="v1",
            target="memory:package3-donecheck",
        )
        if promoted.state != "PROMOTED":
            raise AssertionError("versioned promotion failed")
        checks.append({"check": "governed_learning_promotion", "state": "PASS"})

        finished = memory.update_task(
            task.task_id,
            expected_revision=task.revision,
            state="PASS",
            reason="mandatory_donecheck_pass",
            evidence_refs=("donecheck:package3",),
            final_summary="Package 3 acceptance scenario is verified.",
        )
        if finished.final_outcome is None or finished.final_outcome["verdict"] != "PASS":
            raise AssertionError("verified finish missing")
        checks.append({"check": "evidence_gated_verified_finish", "state": "PASS"})

    print(
        json.dumps(
            {
                "state": "PASS",
                "claim": "Package 3 Persistent Working Memory acceptance scenario passes.",
                "evidence": checks,
                "next_action": "Record exact-head CI evidence and reconcile canonical worklist.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
