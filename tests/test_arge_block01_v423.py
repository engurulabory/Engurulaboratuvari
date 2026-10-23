"""Block 01 A01-A09 combined simulation: conservative, review-only."""
import unittest
from itertools import combinations

TASKS = tuple(f"A{i:02d}" for i in range(1, 10))
def block_judgment(states):
    return "PASS_CANDIDATE_ONLY" if set(states) == set(TASKS) and all(states.get(k) == "PASS_WITH_EVIDENCE" for k in TASKS) else "HOLD"

class Block01Simulation(unittest.TestCase):
    def test_entry_inventory(self):
        self.assertEqual(len(TASKS), 9)
        self.assertEqual(len(set(TASKS)), 9)
        self.assertEqual(block_judgment(dict.fromkeys(TASKS,"HOLD")), "HOLD")

    def test_20_percent_pairwise_loss(self):
        # 2/9 tasks ~= 22.2%, rounding up for fault injection.
        baseline=dict.fromkeys(TASKS,"PASS_WITH_EVIDENCE")
        for omitted in combinations(TASKS,2):
            with self.subTest(omitted=omitted):
                case=dict(baseline)
                for task in omitted: case[task]="HOLD"
                self.assertEqual(block_judgment(case),"HOLD")

    def test_each_single_critical_gap(self):
        baseline=dict.fromkeys(TASKS,"PASS_WITH_EVIDENCE")
        for task in TASKS:
            with self.subTest(task=task):
                case=dict(baseline);case[task]="HOLD"
                self.assertEqual(block_judgment(case),"HOLD")

    def test_missing_and_extra_task_holds(self):
        baseline=dict.fromkeys(TASKS,"PASS_WITH_EVIDENCE")
        self.assertEqual(block_judgment({k:v for k,v in baseline.items() if k!="A09"}),"HOLD")
        self.assertEqual(block_judgment({**baseline,"B01":"PASS_WITH_EVIDENCE"}),"HOLD")

    def test_hypothetical_positive_does_not_count_official(self):
        baseline=dict.fromkeys(TASKS,"PASS_WITH_EVIDENCE")
        self.assertEqual(block_judgment(baseline),"PASS_CANDIDATE_ONLY")

    def test_exit_same_gate(self):
        self.assertEqual(block_judgment(dict.fromkeys(TASKS,"HOLD")),"HOLD")

if __name__=="__main__":unittest.main()
