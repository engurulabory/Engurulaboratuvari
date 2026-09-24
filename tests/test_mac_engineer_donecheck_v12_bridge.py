from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_donecheck_v12_bridge.py"
A10_COMMAND = ROOT / "governance" / "mac-engineer" / "V07_A10_DONECHECK_V12_ACCEPTANCE.command"
SPEC = importlib.util.spec_from_file_location("mac_engineer_donecheck_v12_bridge", MODULE_PATH)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


class DoneCheckV12BridgeTests(unittest.TestCase):
    def test_a10_command_keeps_syntax_check_bytecode_free(self):
        text = A10_COMMAND.read_text(encoding="utf-8")
        self.assertIn("export PYTHONDONTWRITEBYTECODE=1", text)
        self.assertNotIn("python3 -m py_compile", text)
        self.assertIn('compile(source, str(path), "exec")', text)
        self.assertIn("python3 -B tools/mac_engineer_donecheck_v12_bridge.py verify", text)

    def test_vitest_reporter_matches_supported_v4_builtin(self):
        self.assertEqual(bridge.VITEST_REPORTER, "minimal")
        self.assertNotEqual(bridge.VITEST_REPORTER, "basic")

    def _fixture(self, *, a09_state: str):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        evidence = {}
        for i in range(1, 10):
            gate = f"V07-A{i:02d}"
            path = root / f"{gate}.md"
            path.write_text(f"{gate} evidence\n", encoding="utf-8")
            evidence[gate] = path

        fabric = root / "fabric.json"
        fabric.write_text(
            json.dumps({
                "state": "PASS",
                "repositoryCount": 12,
                "mirrorPassCount": 12,
                "offlineQueueProof": {"state": "PASS"},
            }),
            encoding="utf-8",
        )
        session = root / "session.json"
        session.write_text(
            json.dumps({
                "currentV07": {
                    "passedGates": [f"V07-A{i:02d}" for i in range(1, 9)],
                    "a09State": "HOLD",
                },
                "observedV07A09LocalFallback": {
                    "canonicalA09State": a09_state,
                },
            }),
            encoding="utf-8",
        )
        return temp, root, evidence, fabric, session

    def test_realistic_current_state_is_inconclusive_only_at_a09(self):
        temp, root, evidence, fabric, session = self._fixture(a09_state="HOLD")
        self.addCleanup(temp.cleanup)
        out = root / "out"

        with (
            mock.patch.object(bridge, "GATE_EVIDENCE", evidence),
            mock.patch.object(bridge, "FABRIC_STATE", fabric),
            mock.patch.object(bridge, "SESSION_STATE", session),
        ):
            payload = bridge.prepare_input(out)

        outcomes = {x["gate"]: x["expectedOutcome"] for x in payload["criteria"]}
        for i in range(1, 9):
            self.assertEqual(outcomes[f"V07-A{i:02d}"], "pass")
        self.assertEqual(outcomes["V07-A09"], "inconclusive")
        self.assertEqual(payload["expectedAggregateOutcome"], "inconclusive")
        self.assertEqual(payload["producer"]["id"], "enguru.mac-engineer")
        self.assertTrue(all(x["artifactDigest"].startswith("sha256:") for x in payload["criteria"]))

    def test_a09_pass_promotes_expected_aggregate_to_pass(self):
        temp, root, evidence, fabric, session = self._fixture(a09_state="PASS")
        self.addCleanup(temp.cleanup)
        out = root / "out"

        with (
            mock.patch.object(bridge, "GATE_EVIDENCE", evidence),
            mock.patch.object(bridge, "FABRIC_STATE", fabric),
            mock.patch.object(bridge, "SESSION_STATE", session),
        ):
            payload = bridge.prepare_input(out)

        self.assertTrue(all(x["expectedOutcome"] == "pass" for x in payload["criteria"]))
        self.assertEqual(payload["expectedAggregateOutcome"], "pass")

    def test_fabric_must_be_12_of_12_with_offline_queue_pass(self):
        temp, root, evidence, fabric, session = self._fixture(a09_state="HOLD")
        self.addCleanup(temp.cleanup)
        fabric.write_text(
            json.dumps({
                "state": "PASS",
                "repositoryCount": 12,
                "mirrorPassCount": 11,
                "offlineQueueProof": {"state": "PASS"},
            }),
            encoding="utf-8",
        )

        with (
            mock.patch.object(bridge, "GATE_EVIDENCE", evidence),
            mock.patch.object(bridge, "FABRIC_STATE", fabric),
            mock.patch.object(bridge, "SESSION_STATE", session),
        ):
            with self.assertRaisesRegex(RuntimeError, "12_OF_12"):
                bridge.prepare_input(root / "out")


if __name__ == "__main__":
    unittest.main()
