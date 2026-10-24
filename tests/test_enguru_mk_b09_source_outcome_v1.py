"""B09 adversarial tests: synthetic REST data are never counted as field proof."""
import copy
from pathlib import Path
import sqlite3
import unittest
from tools import enguru_mk_b09_source_outcome_v1 as m
from tools import enguru_mk_intelligence_v5 as v5

class Gate(unittest.TestCase):
 def setUp(self):
  self.root=Path(__file__).resolve().parents[1]
  self.data={}
  for id,(event,path) in m.RUNS.items():
   self.data[f"/repos/{m.REPO}/actions/runs/{id}"]={
     "id":id,"head_sha":m.HEAD,"head_branch":m.BRANCH,"event":event,
     "path":path,"status":"completed","conclusion":"success","workflow_id":42,
     "repository":{"full_name":m.REPO},"actor":{"login":"engurulabory"}}
  self.job=f"/repos/{m.REPO}/actions/runs/40116627850/jobs?per_page=100"
  self.data[self.job]={"jobs":[{"name":"independent-regression","status":"completed","conclusion":"success"}]}
  self.pr=f"/repos/{m.REPO}/pulls/218"
  self.data[self.pr]={"number":218,"state":"open","head":{"sha":m.HEAD,"ref":m.BRANCH}}
 def get(self,path):return copy.deepcopy(self.data[path])
 def rejection(self):
  with self.assertRaises(m.Hold):m.verify(self.get,self.root)
 def test_true_mock_case_bounded(self):
  r=m.check_learning(self.get,self.root)
  self.assertEqual(r["verifiedCases"],1)
  self.assertEqual(r["generalizedLearning"],"HOLD_MULTI_CASE_FIELD")
 def test_repeat_determinism(self):self.assertEqual(m.verify(self.get,self.root),m.verify(self.get,self.root))
 def test_pins(self):self.assertEqual(len(m.PINS),4)
 def test_bad_sha(self):self.data[f"/repos/{m.REPO}/actions/runs/40116627850"]["head_sha"]="0"*40;self.rejection()
 def test_bad_actor(self):self.data[f"/repos/{m.REPO}/actions/runs/40116627850"]["actor"]={"login":"github-actions[bot]"};self.rejection()
 def test_bad_repo(self):self.data[f"/repos/{m.REPO}/actions/runs/40116627850"]["repository"]={"full_name":"other/repo"};self.rejection()
 def test_failed_ci(self):self.data[f"/repos/{m.REPO}/actions/runs/40116627850"]["conclusion"]="failure";self.rejection()
 def test_wrong_workflow(self):self.data[f"/repos/{m.REPO}/actions/runs/40116627850"]["path"]="fake.yml";self.rejection()
 def test_wrong_event(self):self.data[f"/repos/{m.REPO}/actions/runs/40116627850"]["event"]="workflow_dispatch";self.rejection()
 def test_wrong_id_type(self):self.data[f"/repos/{m.REPO}/actions/runs/40116627850"]["id"]="40116627850";self.rejection()
 def test_missing_job(self):self.data[self.job]["jobs"]=[];self.rejection()
 def test_failed_job(self):self.data[self.job]["jobs"][0]["conclusion"]="failure";self.rejection()
 def test_bad_step(self):self.data[self.job]["jobs"][0]["steps"]=[{"conclusion":"failure"}];self.rejection()
 def test_wrong_pr(self):self.data[self.pr]["head"]["sha"]="b"*40;self.rejection()
 def test_closed_pr(self):self.data[self.pr]["state"]="closed";self.rejection()
 def test_unknown_case(self):
  with self.assertRaises(m.Hold):
   self.fake_verifier()("CASE-OTHER0001",("SOURCE_AUDIT","PASS",m.SOURCE))
 def fake_verifier(self):
  def cb(case,candidate):
   if case!=m.CASE or tuple(candidate)!=("SOURCE_AUDIT","PASS",m.SOURCE):raise m.Hold("HOLD_CASE_BINDING")
   return "INDEPENDENT_CI",m.verify(self.get,self.root)
  return cb
 def test_wrong_proof(self):
  with self.assertRaises(m.Hold):self.fake_verifier()(m.CASE,("SOURCE_AUDIT","PASS","0"*64))
 def test_provisional_no_ranking(self):
  with sqlite3.connect(":memory:") as db:
   v5.candidate(db,m.CASE,"SOURCE_AUDIT","PASS",m.SOURCE)
   self.assertEqual(v5.trusted_stats(db),{})
 def test_duplicate_not_double_counted(self):
  with sqlite3.connect(":memory:") as db:
   v5.candidate(db,m.CASE,"SOURCE_AUDIT","PASS",m.SOURCE)
   self.assertEqual(v5.promote(db,m.CASE,self.fake_verifier()),"VERIFIED_EVIDENCE_ONLY")
   self.assertEqual(v5.promote(db,m.CASE,self.fake_verifier()),"IDEMPOTENT")
   self.assertEqual(v5.trusted_stats(db),{"SOURCE_AUDIT":(1,1)})
 def test_token_required(self):
  with self.assertRaises(m.Hold):m.api("")
 def test_restricted_api_scope(self):
  get=m.api("fictional-token-1234567")
  with self.assertRaises(m.Hold):get("/arbitrary/path")
 def test_canonical_receipt(self):self.assertEqual(m.canon({"z":2,"a":1}),b'{"a":1,"z":2}\n')

if __name__=="__main__":unittest.main()
