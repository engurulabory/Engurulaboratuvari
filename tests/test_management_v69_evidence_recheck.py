import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.management_v69_formal70 import IDS
from tools.management_v69_theory_evidence_gate import verify_against_sources

class IndependentEvidence(unittest.TestCase):
 def test_real_bytes_and_exact_run(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"evidence.txt";p.write_bytes(b"actual evidence")
   h=hashlib.sha256(p.read_bytes()).hexdigest()
   proof={"state":"PASS","source_path":"evidence.txt","source_sha256":h,"test_run_id":777,"reviewer":"machine"}
   records={k:dict(proof) for k in IDS}
   runs={777:{"head_sha":"a"*40,"conclusion":"success"}}
   r=verify_against_sources(records,d,"a"*40,runs)
   self.assertEqual(r["confirmed_controls"],70)
   self.assertEqual(r["theory_final"],"HOLD")
   runs[777]["head_sha"]="b"*40
   self.assertEqual(verify_against_sources(records,d,"a"*40,runs)["confirmed_controls"],0)
   runs[777]["head_sha"]="a"*40
   p.write_text("modified")
   self.assertEqual(verify_against_sources(records,d,"a"*40,runs)["confirmed_controls"],0)
 def test_unverified_run(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(verify_against_sources({},d,"a"*40,{})["confirmed_controls"],0)
   self.assertEqual(verify_against_sources({},d,"not-a-sha",{})["state"],"HOLD_EXACT_HEAD")
if __name__=="__main__":unittest.main()
