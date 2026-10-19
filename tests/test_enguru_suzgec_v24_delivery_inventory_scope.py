"""Candidate source inventory coverage regression; no OSi source writes."""
import unittest
from tools.enguru_suzgec_v24_delivery_inventory import FILES

class InventoryCoverageTests(unittest.TestCase):
    def test_final_sequence_sources_mandatory(self):
        expected={
            "tools/enguru_suzgec_v24_goal_acceptance_loop.py",
            "tests/test_enguru_suzgec_v24_goal_acceptance_loop.py",
            "tests/test_enguru_suzgec_v24_final_sequence_lock.py",
            "governance/work-protocol/ENGURU_SUZGEC_V24_LANGUAGE_ALIGNMENT_CONTRACT_V1.json",
        }
        self.assertTrue(expected.issubset(set(FILES)))
    def test_no_duplicate_paths(self):
        self.assertEqual(len(FILES),len(set(FILES)))
    def test_no_unsafe_or_absolute_paths(self):
        from pathlib import PurePosixPath
        for p in FILES:
            with self.subTest(path=p):
                x=PurePosixPath(p)
                self.assertFalse(x.is_absolute())
                self.assertNotIn("..",x.parts)
                self.assertEqual(p,x.as_posix())
if __name__=="__main__":
    unittest.main()
