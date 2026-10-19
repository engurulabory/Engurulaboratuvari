"""Negative and boundary tests of the v2.4 read-only source preflight."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from tools.enguru_suzgec_v24_source_preflight import assess

class SourcePreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "source.py").write_text("original", encoding="utf-8")
        self.files = {"source.py": hashlib.sha256(b"original").hexdigest()}

    def manifest(self, **overrides):
        source_set_sha = hashlib.sha256(json.dumps(self.files, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        data = {"goal_scope_id": "ENGURU_SUZGEC_V24", "source_files": self.files, "prediction_source_sha256": source_set_sha}
        data.update(overrides)
        path = self.root / "manifest.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exact_match_is_only_preflight(self):
        r = assess(self.root, self.manifest())
        self.assertEqual(r["state"], "PASS_SOURCE_PREFLIGHT_ONLY")
        self.assertEqual(r["verifiedFinish"], "HOLD")

    def test_changed_source_holds(self):
        m = self.manifest()
        (self.root / "source.py").write_text("changed")
        self.assertEqual(assess(self.root, m)["state"], "HOLD_GUVENLI_DUR")

    def test_stale_prediction_holds(self):
        self.assertEqual(assess(self.root, self.manifest(prediction_source_sha256="0"*64))["state"], "HOLD_GUVENLI_DUR")

    def test_parent_escape_holds(self):
        self.assertEqual(assess(self.root, self.manifest(source_files={"../secret": "0"*64}))["state"], "HOLD_GUVENLI_DUR")

    def test_missing_source_holds(self):
        self.assertEqual(assess(self.root, self.manifest(source_files={"missing": "0"*64}))["state"], "HOLD_GUVENLI_DUR")

    def test_empty_scope_holds(self):
        self.assertEqual(assess(self.root, self.manifest(goal_scope_id=""))["state"], "HOLD_GUVENLI_DUR")

    def test_symlink_holds(self):
        (self.root / "alias.py").symlink_to(self.root / "source.py")
        self.assertEqual(assess(self.root, self.manifest(source_files={"alias.py": self.files["source.py"]}))["state"], "HOLD_GUVENLI_DUR")

    def test_corrupt_manifest_holds(self):
        m = self.manifest()
        m.write_text("{", encoding="utf-8")
        self.assertEqual(assess(self.root, m)["state"], "HOLD_GUVENLI_DUR")

if __name__ == "__main__":
    unittest.main()
