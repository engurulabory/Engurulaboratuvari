"""A07 product boundary: preserve pinned main billing sources during research.

Expected Git object SHA values reconciled to canonical main 0b374b1469ef8a249509bd51dd5dfc8bce3e301e on 2026-10-25. Three old pins were invalidated by 20 official main commits; the research PR did not touch these production paths.
A main update requires explicit source reconciliation rather than silent drift.
These tests safeguard engineering scope, not official acceptance.
"""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_BLOBS = {
    "cores/billing/billing_core.py": "9e8b170c4d8ff76227be019e4e76062fd21d1811",
    "cores/billing/invoice_record.py": "223739eb8295686319b649a39aadb27ea1228609",
    "cores/billing/evidence_store.py": "bb666491824cf082ed45867576d05dbcf2276fd6",
    "cores/billing/persistent_store.py": "60bea414292530666158c7725e8efce3c0fb83b0",
    "cores/billing/monthly_report.py": "29b64f4937be2a334590dbdd802cd981b6a67540",
    "tests/test_billing_v1.py": "3b57674b12f99b868986840d5649cb890e5b5fb5",
    "tests/test_billing_persistent_store.py": "bf91de06de1c9816981bdb8a19a720b3a1987793",
}

def git_blob_sha(content):
    return hashlib.sha1(b"blob " + str(len(content)).encode() + bytes((0,)) + content).hexdigest()


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
