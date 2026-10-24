"""G07 field collector negative/contract tests: no host state mutation."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("emus_g07", ROOT / "tools/emus_g07_osi_field_evidence.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class G07FieldCollectorTests(unittest.TestCase):
    def test_non_mac_host_holds_before_any_command(self):
        with patch.object(module.platform, "system", return_value="Linux"), patch.object(module, "command") as cmd:
            result = module.inspect("qwen3:14b", run_inference=True)
        self.assertEqual(result["state"], "HOLD_MAC_OSI_REQUIRED")
        cmd.assert_not_called()

    def test_mac_snapshot_no_inference_and_no_install(self):
        with patch.object(module.platform, "system", return_value="Darwin"), patch.object(module, "command", return_value={"exit_code": 0, "stdout": "ok"}) as cmd, patch.object(module.shutil, "disk_usage", return_value=(100, 40, 60)), patch.object(module.urllib.request, "urlopen") as network:
            result = module.inspect("qwen3:14b")
        self.assertEqual(result["state"], "FIELD_EVIDENCE_COLLECTED_NOT_ACCEPTED")
        self.assertEqual(result["disk"]["free_bytes"], 60)
        network.assert_not_called()
        calls = [" ".join(c.args) for c in cmd.call_args_list]
        self.assertTrue(any("show qwen3:14b --license" in v for v in calls))
        self.assertFalse(any("pull" in v or "install" in v for v in calls))


if __name__ == "__main__":
    unittest.main()
