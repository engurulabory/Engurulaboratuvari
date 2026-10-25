"""Lock falsifications: immutable eight positive stages, V3 preservation and PiLive target."""
from pathlib import Path
import json
import tempfile
import unittest

from tools.enguru_kalici_disiplin_lock_v1 import (
    verify, ROOT, SOURCE, LOCK, CANONICAL, CANONICAL_LOCK, BASE, PRODUCT, STAGES,
)


class EightStageLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        files = (SOURCE, LOCK, CANONICAL, CANONICAL_LOCK,
                 Path("AGENTS.md"), BASE / "ENGURU_GITHUB_METHOD_ENTRY_V2.md", PRODUCT)
        for name in files:
            out = self.root / name
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes((ROOT / name).read_bytes())

    def tearDown(self):
        self.temp.cleanup()

    def modify(self, path, fn):
        p = self.root / path
        p.write_text(fn(p.read_text(encoding="utf-8")), encoding="utf-8")

    def test_exact_eight_stage_contract_passes_with_separate_authority_hold(self):
        result = verify(self.root)
        self.assertEqual(result["status"], "PASS_METHOD_TEXT_LOCK", result["errors"])
        self.assertEqual(result["stages"], list(STAGES))
        self.assertEqual(result["realMacUserAcceptance"], "HOLD")
        self.assertEqual(result["productOfficialVerifiedFinish"], "HOLD")

    def test_stage_change_detected_by_source_sha(self):
        self.modify(SOURCE, lambda s: s.replace("5. Eksikleri tamamla", "5. Eksikleri tamamla!"))
        r = verify(self.root)
        self.assertEqual(r["status"], "HOLD")
        self.assertIn("SHA256_SOURCE_DRIFT", r["errors"])

    def test_stage_swap_is_rejected_even_when_other_text_preserved(self):
        self.modify(SOURCE, lambda s: s.replace("1. Hakikati gör\n2. Değeri koru",
                                                 "1. Değeri koru\n2. Hakikati gör"))
        self.assertIn("EIGHT_STAGE_ORDER", verify(self.root)["errors"])

    def test_forged_sha_is_rejected(self):
        self.modify(LOCK, lambda s: s.replace('"sha256": "', '"sha256": "f'))
        self.assertIn("SHA256_SOURCE_DRIFT", verify(self.root)["errors"])

    def test_source_absent_is_hold(self):
        (self.root / SOURCE).unlink()
        self.assertEqual(verify(self.root)["status"], "HOLD")

    def test_canonical_v3_drift_cannot_be_hidden_by_new_method_lock(self):
        self.modify(CANONICAL, lambda s: s+"\nUNAUTHORIZED_DRIFT\n")
        self.assertIn("CANONICAL_V3_LOCK", verify(self.root)["errors"])

    def test_agent_entry_missing_fails(self):
        self.modify(Path("AGENTS.md"),
                    lambda s: s.replace(SOURCE.as_posix(), "unrelated-file.md"))
        self.assertIn("AGENTS_LINK", verify(self.root)["errors"])

    def test_method_entry_missing_fails(self):
        self.modify(BASE / "ENGURU_GITHUB_METHOD_ENTRY_V2.md",
                    lambda s: s.replace("ENGURU_KALICI_CALISMA_DISIPLINI_V1.md", "unrelated.md"))
        self.assertIn("METHOD_ENTRY_LINK", verify(self.root)["errors"])

    def test_pilive_failed_visual_trial_boundary_stays_in_target(self):
        self.modify(PRODUCT, lambda s: s.replace("BAŞARISIZ GÖRSEL DENEME",
                                                 "ESKİ UI TAM KABUL EDİLDİ"))
        self.assertIn("PILIVE_TARGET_CONTRACT", verify(self.root)["errors"])

    def test_pilive_canonical_12_4_7_separation_is_mandatory(self):
        self.modify(PRODUCT, lambda s: s.replace("P02 12/12", "P02 9/12"))
        self.assertIn("PILIVE_TARGET_CONTRACT", verify(self.root)["errors"])


if __name__ == "__main__":
    unittest.main()
