"""Regression gate: Block 01 task IDs must retain the original V4.2 meaning."""
import re
import unittest
from pathlib import Path

FILE = (Path(__file__).resolve().parents[1] /
    "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_A01_A09_V423.md")

# V4.2 40-task design contract: canonical task semantics (not an approval grant).
CANONICAL = {
    "A01": ("18 vaka", "kaynak"),
    "A02": ("234", "K01"),
    "A03": ("K01", "owner"),
    "A04": ("Upstream kanıt", "CVE", "SBOM"),
    "A05": ("Müşteri dağıtım", "18"),
    "A06": ("E5 bağımsız kabul", "18"),
    "A07": ("G01", "G02", "G03", "saldırı", "orakel"),
    "A08": ("K12", "5 yıllık", "duyarlılık"),
    "A09": ("Birleşik", "devri"),
}

def task_rows(doc):
    rows = {}
    for line in doc.splitlines():
        m = re.match(r"^\| (A0[1-9]) \| (.*?) \| (.*?) \| (HOLD|PASS) \|$", line)
        if m:
            if m[1] in rows:
                raise ValueError("duplicate task row")
            rows[m[1]] = (m[2], m[3], m[4])
    return rows

class OriginalTaskMeaning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = FILE.read_text(encoding="utf-8")
        cls.rows = task_rows(cls.doc)

    def test_all_nine_original_tasks_present(self):
        self.assertEqual(set(self.rows), set(CANONICAL))

    def test_each_id_preserves_v42_mandate(self):
        for task, terms in CANONICAL.items():
            with self.subTest(task=task):
                row = " ".join(self.rows[task][:2])
                for term in terms:
                    self.assertIn(term, row, (task, term))

    def test_no_advisory_work_promoted_to_official(self):
        self.assertTrue(all(row[2] == "HOLD" for row in self.rows.values()))
        self.assertIn("0/9", self.doc)

    def test_a06_and_a07_never_swap(self):
        self.assertIn("E5 bağımsız kabul", self.rows["A06"][0])
        self.assertIn("G01 dış etki", self.rows["A07"][0])
        self.assertNotIn("G01 dış etki", self.rows["A06"][0])

if __name__ == "__main__":
    unittest.main()
