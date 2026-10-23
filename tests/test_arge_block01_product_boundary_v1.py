"""A07 product boundary: preserve pinned main billing sources during research.

Expected Git object SHA values verified from main on 2026-10-23.
A main update requires explicit source reconciliation rather than silent drift.
These tests safeguard engineering scope, not official acceptance.
"""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_BLOBS = {
    "cores/billing/billing_core.py": "909eb8c1ac6e50e5591d5e7ed87b2d522cf85e8c",
    "cores/billing/invoice_record.py": "223739eb8295686319b649a39aadb27ea1228609",
    "cores/billing/evidence_store.py": "bb666491824cf082ed45867576d05dbcf2276fd6",
    "cores/billing/persistent_store.py": "b1668eb24cf9dce0838dfc880aa479e9b9c9b0b3",
    "cores/billing/monthly_report.py": "29b64f4937be2a334590dbdd802cd981b6a67540",
    "tests/test_billing_v1.py": "3b57674b12f99b868986840d5649cb890e5b5fb5",
    "tests/test_billing_persistent_store.py": "43ba2deb759dadbb6e7c72633eeebb49dd659580",
}

def git_blob_sha(content):
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\\0" + content).hexdigest()


class ResearchBoundaryTests(unittest.TestCase):
    def test_untouched_production_paths_match_main_blob(self):
        for rel, sha in MAIN_BLOBS.items():
            with self.subTest(path=rel):
                self.assertEqual(git_blob_sha((ROOT / rel).read_bytes()), sha)

    def test_experimental_runtime_not_in_product_package(self):
        self.assertFalse((ROOT / "cores/billing/access_gate.py").exists())
        self.assertFalse((ROOT / "cores/billing/sqlite_idempotency_reservation_v1.py").exists())

    def test_experimental_implementations_remain_in_research(self):
        names = [
            "tools/arge_block01_g01_billing_core_prototype_v1.py",
            "tools/arge_block01_g01_sqlite_reservation_v1.py",
            "tools/arge_block01_g02_access_gate_v1.py",
            "tests/test_arge_block01_g01_sqlite_v1.py",
            "tests/test_arge_block01_g02_existing_gap_v1.py",
        ]
        for rel in names:
            with self.subTest(path=rel):
                self.assertTrue((ROOT / rel).is_file())

if __name__ == "__main__":
    unittest.main()
