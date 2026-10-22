"""ENGÜRÜ V3 canonical read-only SHA-256 lock acceptance and negative tests."""
import json
from pathlib import Path
import tempfile
import unittest

from tools.verify_enguru_universal_v3_lock import ROOT, LOCK, EXPECTED_PATH, verify


class UniversalV3LockTests(unittest.TestCase):
    def test_real_checked_in_v3_source_matches_pinned_lock(self):
        report = verify()
        self.assertEqual(report["state"], "PASS_V3_SOURCE_SHA256_LOCK_READ_ONLY")
        self.assertEqual(report["source_writes"], 0)
        self.assertEqual(report["official_field_acceptance"], "NOT_ASSERTED")

    def with_scratch(self, mutate):
        with tempfile.TemporaryDirectory(prefix="enguru-v3-lock-") as directory:
            root = Path(directory)
            source = root / EXPECTED_PATH
            source.parent.mkdir(parents=True)
            source.write_bytes((ROOT / EXPECTED_PATH).read_bytes())
            lock = root / LOCK.relative_to(ROOT)
            lock.write_bytes(LOCK.read_bytes())
            mutate(root, source, lock)
            return verify(root)

    def test_changed_source_fails_closed(self):
        def mutate(root, source, lock):
            source.write_bytes(source.read_bytes() + b"DRIFT")
        with self.assertRaisesRegex(ValueError, "HOLD_SHA256_SOURCE_DRIFT"):
            self.with_scratch(mutate)

    def test_invalid_scope_fails_closed(self):
        def mutate(root, source, lock):
            j = json.loads(lock.read_text())
            j["canonical_path"] = "README.md"
            lock.write_text(json.dumps(j))
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_SCOPE"):
            self.with_scratch(mutate)

    def test_wrong_sha_fails_closed(self):
        def mutate(root, source, lock):
            j = json.loads(lock.read_text())
            j["sha256"] = "0" * 64
            lock.write_text(json.dumps(j))
        with self.assertRaisesRegex(ValueError, "HOLD_SHA256_SOURCE_DRIFT"):
            self.with_scratch(mutate)

    def test_unexpected_schema_fails_closed(self):
        def mutate(root, source, lock):
            j = json.loads(lock.read_text())
            j["schema"] = "other"
            lock.write_text(json.dumps(j))
        with self.assertRaisesRegex(ValueError, "HOLD_SCHEMA"):
            self.with_scratch(mutate)

    def test_wrong_git_blob_fails_closed(self):
        def mutate(root, source, lock):
            j = json.loads(lock.read_text())
            j["git_blob_sha1"] = "0" * 40
            lock.write_text(json.dumps(j))
        with self.assertRaisesRegex(ValueError, "HOLD_GIT_BLOB_MISMATCH"):
            self.with_scratch(mutate)

    def test_symlink_source_fails_closed(self):
        def mutate(root, source, lock):
            data = source.read_bytes()
            other = root / "other.md"
            other.write_bytes(data)
            source.unlink()
            source.symlink_to(other)
        with self.assertRaisesRegex(ValueError, "HOLD_SYMLINK_SOURCE"):
            self.with_scratch(mutate)


if __name__ == "__main__":
    unittest.main()
