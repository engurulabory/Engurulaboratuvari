import importlib.util
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("g07v2",root/"tools/emus_g07_osi_field_v2.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class G07V2Tests(TestCase):
    def test_unsupported_os_hold(self):
        with patch.object(m.platform,"system",return_value="Linux"), patch.object(m,"get") as network:
            self.assertEqual(m.measure("qwen3:14b",True)["state"],"HOLD_MAC_REQUIRED")
            network.assert_not_called()
    def test_missing_digest_hold(self):
        with patch.object(m.platform,"system",return_value="Darwin"), patch.object(m,"get",return_value={"models":[{"name":"qwen3:14b"}]}):
            self.assertEqual(m.measure("qwen3:14b",False)["state"],"HOLD_EXACT_MODEL_IDENTITY")
    def test_present_digest_no_probe(self):
        def fake(path,timeout=10):
            return {"models":[{"name":"qwen3:14b","digest":"sha256-test"}]} if path=="/api/tags" else {"models":[{"name":"qwen3:14b","size_vram":2048}]}
        with patch.object(m.platform,"system",return_value="Darwin"), patch.object(m,"get",side_effect=fake), patch.object(m.subprocess,"run") as run, patch.object(m,"urlopen") as network:
            run.return_value.stdout="vm fixture"
            result=m.measure("qwen3:14b",False)
        self.assertEqual(result["state"],"FIELD_COLLECTED_ACCEPTANCE_PENDING")
        self.assertEqual(result["model"]["digest"],"sha256-test")
        self.assertEqual(result["loaded_after"][0]["size_vram"],2048)
        network.assert_not_called()
