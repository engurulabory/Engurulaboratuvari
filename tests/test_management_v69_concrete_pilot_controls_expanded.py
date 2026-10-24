"""Additional distinct Pilot behavioral assertions, review-only."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.management_v69_pilot_dual_acceptance import assess, THEORY_KEYS, FIELD_KEYS
from tools.management_v69_pilot_proof_gates import verify_source, owner_gate
from tools.management_v69_triple100_gate import evaluate
from tools.management_v69_historical_ci_classify import classify
from tools.management_v69_triple100_distinctness_audit import audit

class ExpandedPilotControls(unittest.TestCase):
 def test_design_005_field_missing_list(self):
  x=assess({},{});self.assertEqual(set(x["field_missing"]),set(FIELD_KEYS))
 def test_design_006_complete_theory_candidates_next(self):
  x=assess(dict.fromkeys(THEORY_KEYS,True),{});self.assertEqual(x["next_target"],"02")
 def test_design_007_incomplete_theory_retains_target(self):
  self.assertEqual(assess({}, {})["next_target"],"01")
 def test_design_008_duplicate_evidence_detected(self):
  r={"description":"Distinct architectural guarantee","assertion_id":"a","source_path":"tools/a.py"}
  self.assertEqual(len(audit({"DESIGN_005":r,"DESIGN_006":dict(r)})["duplicate_assertion_claims"]),2)
 def test_theory_005_source_drift_requires_new_receipt(self):
  self.assertEqual(classify({"source_commit":"a"*40},{"main_sha":"b"*40})["reason"],"NEW_CURRENT_MAIN_RECEIPT_REQUIRED")
 def test_theory_006_equal_commit_not_authority(self):
  self.assertEqual(classify({"source_commit":"a"*40},{"main_sha":"a"*40})["reason"],"AUTHENTIC_CURRENT_MAIN_RECEIPT_REQUIRED")
 def test_theory_007_invalid_commit_holds(self):
  self.assertEqual(classify({"source_commit":"bad"},{"main_sha":"a"*40})["reason"],"SOURCE_IDENTITY_REQUIRED")
 def test_theory_008_missing_ledger_schema_holds(self):
  self.assertFalse(evaluate({"DESIGN":{},"THEORY":{},"SIMULATION":{}})["triple_theoretical_candidate"])
 def test_simulation_005_symlink_scope_holds(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/"source").write_bytes(b"a");(p/"link").symlink_to("source")
   self.assertEqual(verify_source(d,"link",hashlib.sha256(b"a").hexdigest())["reason"],"SOURCE_SCOPE")
 def test_simulation_006_bad_sha_pin_holds(self):
  with tempfile.TemporaryDirectory() as d:
   (Path(d)/"source").write_bytes(b"a")
   self.assertEqual(verify_source(d,"source","false")["reason"],"INVALID_SHA_PIN")
 def test_simulation_007_absolute_path_holds(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(verify_source(d,"/etc/passwd","a"*64)["reason"],"PATH_SCOPE")
 def test_simulation_008_unproven_owner_rejected(self):
  self.assertEqual(owner_gate({"state":"PASS_SOURCE_SHA256"},"engurulabory")["reason"],"AUTHENTIC_OWNER_AUTHORITY_REQUIRED")

if __name__=="__main__":unittest.main()
