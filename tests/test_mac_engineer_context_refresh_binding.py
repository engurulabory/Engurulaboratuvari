from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import tools.mac_engineer_control as control


class ContextRefreshBindingTests(unittest.TestCase):
    @patch("tools.mac_engineer_control.subprocess.run")
    def test_sync_pass_runs_target(self, run_mock):
        run_mock.side_effect = [
            subprocess.CompletedProcess([], 0),
            subprocess.CompletedProcess([], 0),
        ]

        target = [sys.executable, str(Path("/tmp/target.py"))]
        result = control.run_after_context_sync(target)

        self.assertEqual(result, 0)
        self.assertEqual(run_mock.call_count, 2)
        self.assertEqual(
            run_mock.call_args_list[0].args[0],
            [sys.executable, str(control.SYNC_CONTEXT)],
        )
        self.assertEqual(
            run_mock.call_args_list[1].args[0],
            target,
        )

    @patch("tools.mac_engineer_control.subprocess.run")
    def test_sync_hold_stops_target(self, run_mock):
        run_mock.return_value = subprocess.CompletedProcess([], 2)

        result = control.run_after_context_sync(
            [sys.executable, str(Path("/tmp/target.py"))]
        )

        self.assertEqual(result, 2)
        self.assertEqual(run_mock.call_count, 1)

    def test_session_start_and_runtime_refresh_use_context_sync(self):
        source = Path(control.__file__).read_text(encoding="utf-8")

        self.assertIn(
            'if args.command == "session-start":\n'
            '            return run_after_context_sync(command)',
            source,
        )
        self.assertIn(
            'if args.command == "refresh-real-task-runtime":\n'
            '        return run_after_context_sync(',
            source,
        )


if __name__ == "__main__":
    unittest.main()
