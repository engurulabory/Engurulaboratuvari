"""EMUS task identity compatibility probe; isolated, no production writes.

Run from the Labory repo with ENGURU_MAC_ENGINEER_RUNTIME pointing at a
checked-out, source-pinned Mac Engineer runtime directory.
This tests an explicit handoff, not an already-installed runtime adapter.
"""
import hashlib
import importlib.util
import os
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from shared_ai.working_memory import PersistentWorkingMemory

RUNTIME = os.environ.get("ENGURU_MAC_ENGINEER_RUNTIME", "")
PINNED_RELIABILITY_BLOB_SHA1 = "ee0f53e4a1fb899aecd637f059ce840979bb02d4"


class EmusTaskIdentityProbe(unittest.TestCase):
    def test_emus_working_memory_checkpoint_identity_and_authority(self):
        with tempfile.TemporaryDirectory() as root:
            memory = PersistentWorkingMemory(root)
            created = memory.create_task(
                task_id="emus-ci-task-01",
                objective="Keep one task identity through a verified checkpoint",
                authority_snapshot={"mode": "READ_ONLY_PROBE", "human_threshold": ["finish"]},
                required_capabilities=("verification",),
            )
            updated = memory.update_task(
                created.task_id,
                expected_revision=created.revision,
                evidence_refs=("ci:emus-identity",),
                checkpoint={
                    "checkpoint_id": "emus-ci-checkpoint-01",
                    "summary": "Identity persisted",
                    "next_action": "Require independent review",
                    "evidence_refs": ["ci:emus-identity"],
                },
            )
            reloaded = PersistentWorkingMemory(root).resume_task(
                created.task_id, checkpoint_id="emus-ci-checkpoint-01"
            )
            self.assertEqual(reloaded.task_id, created.task_id)
            self.assertEqual(reloaded.revision, updated.revision)
            self.assertEqual(reloaded.authority_snapshot, created.authority_snapshot)
            self.assertEqual(reloaded.resume_checkpoint["next_action"], "Require independent review")
            self.assertIn("ci:emus-identity", reloaded.evidence_refs)

    def test_missing_pinned_runtime_fails_closed(self):
        with mock.patch.dict(
            globals(), {"RUNTIME": ""}, clear=False
        ):
            with self.assertRaisesRegex(AssertionError, "SOURCE_HOLD"):
                self.test_task_id_survives_two_stores_and_restart()

    def test_source_drift_fails_before_import(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, "reliability.py").write_text(
                "raise RuntimeError('IMPORTED_UNTRUSTED_SOURCE')\n",
                encoding="utf-8",
            )
            with mock.patch.dict(globals(), {"RUNTIME": root}, clear=False):
                with mock.patch("importlib.util.spec_from_file_location") as loader:
                    with self.assertRaisesRegex(AssertionError, "SOURCE_DRIFT"):
                        self.test_task_id_survives_two_stores_and_restart()
                    loader.assert_not_called()

    def test_task_id_survives_two_stores_and_restart(self):
        if not RUNTIME or not (Path(RUNTIME) / "reliability.py").is_file():
            self.fail("SOURCE_HOLD: pinned Mac Engineer runtime path required")
        raw = (Path(RUNTIME) / "reliability.py").read_bytes()
        blob_hash = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        self.assertEqual(blob_hash, PINNED_RELIABILITY_BLOB_SHA1, "SOURCE_DRIFT")
        spec = importlib.util.spec_from_file_location(
            "_emus_pinned_reliability", Path(RUNTIME) / "reliability.py"
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ReliabilityManager = module.ReliabilityManager

        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            mac = ReliabilityManager(base / "mac")
            result = mac.begin("emus-probe-key")
            task_id = result["task"]["task_id"]
            self.assertFalse(result["duplicate"])

            memory = PersistentWorkingMemory(base / "memory")
            memory.create_task(
                task_id=task_id,
                objective="Task ID continuity probe",
                authority_snapshot={"mode": "READ_ONLY_PROBE"},
                required_capabilities=("verification",),
            )
            self.assertEqual(
                PersistentWorkingMemory(base / "memory").load_task(task_id).task_id,
                task_id,
            )
            mac.transition(task_id, "RUNNING")
            mac.checkpoint(task_id, {"step": 1}, verified=True)
            restarted = ReliabilityManager(base / "mac")
            resumed = restarted.resume(task_id)
            self.assertTrue(resumed["ok"])
            self.assertEqual(resumed["task"]["task_id"], task_id)
            self.assertEqual(resumed["checkpoint"]["task_id"], task_id)
            self.assertEqual(resumed["checkpoint"]["payload"], {"step": 1})
            self.assertTrue(resumed["checkpoint"]["verified"])
            self.assertEqual(
                PersistentWorkingMemory(base / "memory").load_task(task_id).task_id,
                task_id,
            )
            duplicate = ReliabilityManager(base / "mac").begin("emus-probe-key")
            self.assertTrue(duplicate["duplicate"])
            self.assertEqual(duplicate["task"]["task_id"], task_id)

            # DoneCheck TaskId is a string contract; this is only an input
            # identity assertion, not a verifyTask or authorized finish.
            donecheck_task_id = task_id
            self.assertEqual(donecheck_task_id, task_id)


if __name__ == "__main__":
    unittest.main()
