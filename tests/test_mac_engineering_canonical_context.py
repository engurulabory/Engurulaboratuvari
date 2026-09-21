from __future__ import annotations

import json
import unittest

import tools.mac_engineering_sync_context as sync


class MacEngineeringCanonicalContextTests(unittest.TestCase):
    def test_canonical_product_name(self):
        roadmap = sync.load_json(sync.ROADMAP)
        self.assertEqual(
            roadmap["product"]["canonicalName"],
            "ENGÜRÜ Mac Engineering™",
        )

    def test_final_target_is_v1(self):
        roadmap = sync.load_json(sync.ROADMAP)
        self.assertEqual(roadmap["finalTarget"]["version"], "v1.0")
        self.assertEqual(
            roadmap["finalTarget"]["title"],
            "Verified Product Engineering Operator",
        )

    def test_runtime_context_is_runtime_state(self):
        self.assertTrue(
            sync.OUTPUT.is_relative_to(sync.RUNTIME_STATE)
        )

    def test_roadmap_has_v06_through_v10(self):
        roadmap = sync.load_json(sync.ROADMAP)
        versions = [item["version"] for item in roadmap["versions"]]
        for version in ("v0.6", "v0.7", "v0.8", "v0.9", "v1.0"):
            self.assertIn(version, versions)

    def test_session_state_uses_canonical_product_name(self):
        state = sync.load_json(sync.SESSION_STATE)
        self.assertEqual(
            state["product"],
            "ENGÜRÜ Mac Engineering™",
        )


if __name__ == "__main__":
    unittest.main()
