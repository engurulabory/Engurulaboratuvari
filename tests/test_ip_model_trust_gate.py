import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ip_model_trust_gate.py"
spec = importlib.util.spec_from_file_location("ip_model_trust_gate", MODULE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

FLEET_MODULE_PATH = ROOT / "tools" / "fleet_ip_gate.py"
fleet_spec = importlib.util.spec_from_file_location("fleet_ip_gate", FLEET_MODULE_PATH)
fleet_gate = importlib.util.module_from_spec(fleet_spec)
fleet_spec.loader.exec_module(fleet_gate)


class GateTests(unittest.TestCase):
    def test_t0_cloud_passes(self):
        result = gate.decision("openai-cloud", "T0", "public text")
        self.assertEqual(result["state"], "PASS")

    def test_t3_cloud_is_blocked_by_conservative_limit(self):
        result = gate.decision("openai-cloud", "T3", "core algorithm")
        self.assertEqual(result["state"], "BLOCKED")

    def test_t4_local_requires_human_threshold(self):
        result = gate.decision("local-self-hosted", "T4", "crown jewel")
        self.assertEqual(result["state"], "HOLD")
        approved = gate.decision("local-self-hosted", "T4", "crown jewel", human_approved=True)
        self.assertEqual(approved["state"], "PASS")

    def test_t5_is_always_blocked(self):
        result = gate.decision("local-self-hosted", "T5", "restricted")
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["reason"], "RESTRICTED_CLASS")

    def test_secret_zero_blocks_even_public_class(self):
        synthetic_secret = "api_key=" + ("a" * 16)
        result = gate.decision("local-self-hosted", "T0", synthetic_secret)
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["reason"], "SECRET_ZERO_RULE")

    def test_unknown_provider_fail_closed(self):
        result = gate.decision("mystery-provider", "T0", "hello")
        self.assertEqual(result["state"], "BLOCKED")

    def test_placeholder_is_not_secret(self):
        result = gate.decision("local-self-hosted", "T1", "api_key=<SECRET>")
        self.assertEqual(result["state"], "PASS")

    def test_fleet_generic_secret_literal_in_source_is_blocked(self):
        hits = fleet_gate.secret_hits(Path("src/config.ts"), "secret = 'synthetic-secret-value'")
        self.assertIn("hardcoded_quoted_secret", hits)

    def test_fleet_generic_secret_literal_in_test_filename_is_allowed(self):
        hits = fleet_gate.secret_hits(Path("src/config.test.ts"), "secret = 'synthetic-secret-value'")
        self.assertNotIn("hardcoded_quoted_secret", hits)

    def test_fleet_known_credential_format_is_blocked_even_in_test_filename(self):
        synthetic_github_token = "ghp_" + ("A" * 24)
        hits = fleet_gate.secret_hits(Path("src/config.test.ts"), synthetic_github_token)
        self.assertIn("github_token", hits)


if __name__ == "__main__":
    unittest.main()
