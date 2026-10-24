import importlib.util
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
p=Path(__file__).resolve().parents[1]/"tools/emus_g07_mac_provider_live_field.py"
s=importlib.util.spec_from_file_location("emus_live",p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)
class EmusG07LiveBoundaryTests(TestCase):
    def test_exact_loopback_router(self):
        self.assertTrue(m.local_url("http://127.0.0.1:8787",8787))
        for u in ("https://127.0.0.1:8787","http://outside.example:8787","http://127.0.0.1:9876"):
            self.assertFalse(m.local_url(u,8787))
    def test_non_mac_fails_before_loading_provider(self):
        with patch.object(m.platform,"system",return_value="Linux"),patch.object(m,"load_provider") as load:
            self.assertEqual(m.collect(Path("/none"),"abc")["state"],"HOLD")
            load.assert_not_called()
    def test_external_override_holds_before_provider(self):
        with patch.object(m.platform,"system",return_value="Darwin"),patch.dict(m.os.environ,{"ENGURU_SHARED_AI_BASE_URL":"https://outside.example:8787"}),patch.object(m,"load_provider") as load:
            self.assertEqual(m.collect(Path("/none"),"abc")["reason"],"ROUTER_NOT_LOOPBACK_8787")
            load.assert_not_called()
