import copy
import unittest

from shared_ai.mac_local_commissioning import assess_mac_local_commissioning


def valid_payload():
    return {
        "schema": "enguru.mac-engineer.local-commissioning/v0.1",
        "platform": "Darwin",
        "github_engineering_state": "GITHUB_ENGINEERING_VERIFIED",
        "canonical_sync": {
            "branch": "main",
            "head_sha": "abc",
            "origin_main_sha": "abc",
            "clean": True,
            "evidence_refs": ["git:head=abc", "git:origin-main=abc"],
        },
        "runtime": {
            "state": "READY",
            "identity": "ENGURU_MAC_ENGINEER",
            "path": "/Applications/Enguru Mac Engineer.app",
            "shared_ai_state": "PASS",
            "provider": "local_runtime",
            "model": "qwen3:14b",
            "evidence_refs": ["runtime:ready", "shared-ai:pass", "ollama:qwen3:14b"],
        },
        "real_task": {
            "state": "PASS",
            "task_id": "task-001",
            "health_only": False,
            "artifact_refs": ["artifact:diff"],
            "test_refs": ["test:pass"],
            "evidence_refs": ["task:executed"],
        },
        "continuity": {
            "state": "PASS",
            "task_id_before": "task-001",
            "task_id_after": "task-001",
            "checkpoint_id": "cp-001",
            "restart_observed": True,
            "evidence_refs": ["restart:observed", "resume:cp-001"],
        },
        "recovery": {
            "state": "PASS",
            "failure_observed": True,
            "root_cause": "bounded fixture failure",
            "bounded_correction": "smallest sufficient repair",
            "reverified": True,
            "evidence_refs": ["failure:observed", "reverify:pass"],
        },
        "authority": {
            "state": "PASS",
            "human_threshold_preserved": True,
            "privilege_escalation": False,
            "evidence_refs": ["authority:unchanged"],
        },
        "critical_failures": {
            "unresolved": 0,
            "evidence_refs": ["critical:0"],
        },
        "mandatory_donecheck": [
            {"check": "real_mac_task", "state": "PASS", "evidence_refs": ["task:executed"]},
            {"check": "restart_resume", "state": "PASS", "evidence_refs": ["resume:cp-001"]},
            {"check": "recovery", "state": "PASS", "evidence_refs": ["reverify:pass"]},
            {"check": "evidence_complete", "state": "PASS", "evidence_refs": ["bundle:complete"]},
        ],
    }


class Package6MacLocalCommissioningTests(unittest.TestCase):
    def test_valid_real_mac_bundle_passes(self):
        result = assess_mac_local_commissioning(valid_payload())
        self.assertEqual(result.state, "PASS", result.issues)

    def test_non_mac_platform_holds(self):
        p = valid_payload()
        p["platform"] = "Linux"
        result = assess_mac_local_commissioning(p)
        self.assertIn("MACOS_REQUIRED", result.issues)

    def test_exact_main_sync_required(self):
        p = valid_payload()
        p["canonical_sync"]["origin_main_sha"] = "def"
        result = assess_mac_local_commissioning(p)
        self.assertIn("EXACT_MAIN_SYNC_REQUIRED", result.issues)

    def test_dirty_worktree_holds(self):
        p = valid_payload()
        p["canonical_sync"]["clean"] = False
        result = assess_mac_local_commissioning(p)
        self.assertIn("CLEAN_WORKTREE_REQUIRED", result.issues)

    def test_health_only_is_not_real_task(self):
        p = valid_payload()
        p["real_task"]["health_only"] = True
        result = assess_mac_local_commissioning(p)
        self.assertIn("HEALTH_ONLY_NOT_TASK_EVIDENCE", result.issues)

    def test_restart_resume_requires_same_task_identity(self):
        p = valid_payload()
        p["continuity"]["task_id_after"] = "task-002"
        result = assess_mac_local_commissioning(p)
        self.assertIn("TASK_IDENTITY_DRIFT", result.issues)

    def test_recovery_requires_observed_failure_and_reverify(self):
        p = valid_payload()
        p["recovery"]["failure_observed"] = False
        p["recovery"]["reverified"] = False
        result = assess_mac_local_commissioning(p)
        self.assertIn("RECOVERABLE_FAILURE_OBSERVATION_REQUIRED", result.issues)
        self.assertIn("RECOVERY_REVERIFY_REQUIRED", result.issues)

    def test_human_threshold_cannot_disappear(self):
        p = valid_payload()
        p["authority"]["human_threshold_preserved"] = False
        result = assess_mac_local_commissioning(p)
        self.assertIn("HUMAN_THRESHOLD_PRESERVATION_REQUIRED", result.issues)

    def test_any_unresolved_critical_failure_holds(self):
        p = valid_payload()
        p["critical_failures"]["unresolved"] = 1
        result = assess_mac_local_commissioning(p)
        self.assertIn("CRITICAL_FAILURES_NONZERO", result.issues)

    def test_donecheck_must_be_evidence_backed_pass(self):
        p = valid_payload()
        p["mandatory_donecheck"][0]["state"] = "HOLD"
        p["mandatory_donecheck"][1]["evidence_refs"] = []
        result = assess_mac_local_commissioning(p)
        self.assertIn("MAC_DONECHECK_NOT_PASS:real_mac_task", result.issues)
        self.assertIn("MAC_DONECHECK_EVIDENCE_REQUIRED:restart_resume", result.issues)


if __name__ == "__main__":
    unittest.main()
