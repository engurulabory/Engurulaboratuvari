import copy,json,unittest
from pathlib import Path
from tools.emus_gap_matrix import evaluate
P=Path(__file__).resolve().parents[1]/"governance/emus/EMUS_V11_SUBCRITERION_PROGRESS_V1.json"
class GapTests(unittest.TestCase):
 def test_real_19_and_gap_counts(self):
  d=json.loads(P.read_text())
  m=evaluate(d)
  self.assertEqual(len(m),19)
  self.assertEqual(sum(len(r["missing"]) for r in m),76-d["counting_rules"]["evidenced_total"])
  self.assertEqual([r["task_id"] for r in m],[f"GH-{i:02d}" for i in range(1,20)])
  self.assertTrue(all(r["acceptance"]=="HOLD" for r in m))
 def test_missing_task_detected(self):
  d=json.loads(P.read_text());d["rows"].pop()
  with self.assertRaises(ValueError):evaluate(d)
 def test_partial_criterion_detected(self):
  d=json.loads(P.read_text());d["rows"][0]["criteria"].pop()
  with self.assertRaises(ValueError):evaluate(d)
