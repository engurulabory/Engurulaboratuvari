"""Fixed independent acceptance harness; unchanged between red and green."""
import unittest
from unique_jobs import unique_jobs


class Acceptance(unittest.TestCase):
    def test_empty(self): self.assertEqual(unique_jobs([]), [])
    def test_single(self): self.assertEqual(unique_jobs(['a']), ['a'])
    def test_repeat(self): self.assertEqual(unique_jobs(['a','a']), ['a'])
    def test_order(self):
        # Both a sequence and its reverse cannot match the same unordered set.
        for values in [list(range(32)),list(reversed(range(32)))]:
            self.assertEqual(unique_jobs(values+values), values)


if __name__=='__main__': unittest.main(verbosity=2)
