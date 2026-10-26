import unittest
from skill_kernel import execute
from run_k01_real_benchmark import old_duplicate_check, trial_input

class BaselineParityTests(unittest.TestCase):
    def test_k01_five_inputs_identity(self):
        for seed in (11,17,23,31,47):
            ids=trial_input(seed)
            self.assertEqual(execute("duplicate-check",{"identifiers":ids})["duplicates"],old_duplicate_check(ids))
    def test_empty_identifier_fail_closed(self):
        self.assertEqual(execute("duplicate-check",{"identifiers":[""]})["state"],"HOLD")
    def test_duplicate_sorted_deterministically(self):
        a=execute("duplicate-check",{"identifiers":["b","b","a","a","c"]})
        self.assertEqual(a["duplicates"],["a","b"])
        self.assertEqual(a["state"],"HOLD")
    def test_unique_identity(self):
        self.assertEqual(execute("duplicate-check",{"identifiers":["a","b"]})["state"],"UNIQUE")
    def test_unsorted_base_exact(self):
        self.assertEqual(old_duplicate_check(["z","a","z","b","b"]),["b","z"])

if __name__=="__main__":
    unittest.main()
