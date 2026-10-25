import json,unittest
from pathlib import Path
from tools.emus_dependency_lock import decision
P=Path(__file__).resolve().parents[1]/"governance/emus/EMUS_V11_SUBCRITERION_PROGRESS_V1.json"
class LockTests(unittest.TestCase):
 def test_current_state_holds(self):
  result=decision(json.loads(P.read_text()))
  self.assertEqual(result["osi_field"],"WAIT_GITHUB_READINESS")
  self.assertEqual(result["finish"],"HOLD")
  self.assertEqual(result["official_accepted_tasks"],0)
 def test_empty_gaps_still_need_review(self):
  data=json.loads(P.read_text())
  for row in data["rows"]:
   for c in row["criteria"]:c["state"]="CI_EVIDENCED"
  result=decision(data)
  self.assertEqual(result["osi_field"],"GITHUB_PREPARATION_REVIEW_REQUIRED")
  self.assertEqual(result["finish"],"HOLD")
 def test_b5_independent_remains_hold(self):
  data=json.loads(P.read_text())
  for row in data["rows"][:16]:
   for c in row["criteria"]:c["state"]="CI_EVIDENCED"
  result=decision(data)
  self.assertEqual(result["osi_field"],"GITHUB_PREPARATION_REVIEW_REQUIRED")
  self.assertEqual(result["blocks"]["B5"]["state"],"HOLD")
