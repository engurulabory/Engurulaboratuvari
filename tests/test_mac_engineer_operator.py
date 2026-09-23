from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_operator.py"
SPEC = importlib.util.spec_from_file_location("mac_engineer_operator", MODULE_PATH)
assert SPEC and SPEC.loader
operator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(operator)


class OperatorSurfaceTests(unittest.TestCase):
    def test_current_truth_reads_single_next_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = root / "session.json"
            roadmap = root / "roadmap.json"
            session.write_text(
                json.dumps({
                    "product": "ENGÜRÜ Mac Engineering™",
                    "currentV07": {
                        "state": "HOLD",
                        "nextAction": "V07_A09_CLEAR_GITHUB_PRIVATE_REPO_HOSTED_ACTIONS_EXECUTION_GATE",
                        "a09State": "HOLD_GATE",
                    },
                }),
                encoding="utf-8",
            )
            roadmap.write_text(
                json.dumps({
                    "current": {
                        "version": "v0.6",
                        "state": "VERIFIED_FINAL_LOCKED",
                        "activeObjective": "V0_7_LONG_RUNNING_RELIABILITY",
                    },
                    "versions": [{"version": "v0.7", "state": "HOLD"}],
                    "finalTarget": {"version": "v1.1"},
                }),
                encoding="utf-8",
            )
            with (
                mock.patch.object(operator, "SESSION_STATE", session),
                mock.patch.object(operator, "ROADMAP", roadmap),
            ):
                truth = operator.current_truth()

        self.assertEqual(
            truth["next_action"],
            "V07_A09_CLEAR_GITHUB_PRIVATE_REPO_HOSTED_ACTIONS_EXECUTION_GATE",
        )
        self.assertEqual(truth["v07_state"], "HOLD")
        self.assertEqual(truth["a09_state"], "HOLD_GATE")

    def test_receipt_contract_is_compact_and_machine_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp)
            runtime_receipts = evidence / "runtime"
            with (
                mock.patch.object(operator, "EVIDENCE", evidence),
                mock.patch.object(operator, "RUNTIME_RECEIPTS", runtime_receipts),
            ):
                payload = operator.write_receipt(
                    command="status",
                    state="PASS",
                    completed=["CANONICAL_STATE_READ"],
                    evidence=["state.json"],
                    hold="",
                    next_action="NEXT",
                    details={"sample": True},
                )

            latest_json = json.loads(
                (evidence / "latest-receipt.json").read_text(encoding="utf-8")
            )
            latest_txt = (
                evidence / "latest-receipt.txt"
            ).read_text(encoding="utf-8").splitlines()

        self.assertEqual(latest_json["state"], "PASS")
        self.assertEqual(latest_json["next_action"], "NEXT")
        self.assertEqual(len(latest_txt), 7)
        self.assertEqual(latest_txt[0], "STATE=PASS")
        self.assertTrue(latest_txt[-1].startswith("RECEIPT="))
        self.assertIn("operator-receipt/v1", payload["schema"])

    def test_continue_unknown_action_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp)
            truth = {
                "next_action": "FUTURE_UNREGISTERED_ACTION",
                "v07_state": "HOLD",
                "a09_state": None,
                "local_fallback": {},
            }
            runtime_receipts = evidence / "runtime"
            with (
                mock.patch.object(operator, "EVIDENCE", evidence),
                mock.patch.object(operator, "RUNTIME_RECEIPTS", runtime_receipts),
                mock.patch.object(operator, "canonical_boot", return_value={"state": "PASS"}),
                mock.patch.object(operator, "current_truth", return_value=truth),
                mock.patch.object(operator, "sync_mirrors", return_value={}),
                mock.patch.object(operator, "runner_status", return_value={"state": "UNCOMMISSIONED"}),
                mock.patch.object(operator, "offline_manifest", return_value={}),
                mock.patch.object(operator, "load_json", return_value={"actions": {}}),
            ):
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    code = operator.command_continue()

            receipt = json.loads(
                (evidence / "latest-receipt.json").read_text(encoding="utf-8")
            )

        self.assertEqual(code, 2)
        self.assertEqual(receipt["state"], "HOLD")
        self.assertEqual(receipt["hold"], "ACTION_HANDLER_NOT_REGISTERED")
        self.assertEqual(receipt["next_action"], "FUTURE_UNREGISTERED_ACTION")

    def test_local_mirror_is_recovery_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source"
            vault = base / "vault"
            source.mkdir()
            subprocess.run(["git", "init"], cwd=source, check=True, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "operator@test.invalid"],
                cwd=source,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Operator Test"],
                cwd=source,
                check=True,
            )
            (source / "truth.txt").write_text("truth\n", encoding="utf-8")
            subprocess.run(["git", "add", "truth.txt"], cwd=source, check=True)
            subprocess.run(["git", "commit", "-m", "truth"], cwd=source, check=True, capture_output=True)

            with mock.patch.object(operator, "GITVAULT", vault):
                result = operator._mirror_one(source, "source")
                mirror = operator.mirror_path("source")

            bare = subprocess.run(
                ["git", "--git-dir", str(mirror), "rev-parse", "--is-bare-repository"],
                text=True,
                capture_output=True,
                check=True,
            )

        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["authority"], "RECOVERY_MIRROR_NOT_CANONICAL")
        self.assertEqual(bare.stdout.strip(), "true")


if __name__ == "__main__":
    unittest.main()
