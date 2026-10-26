"""GH69-BASE read-only design boundary tests. Tests do not issue authority."""
import copy, hashlib, json, re, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MATRIX=ROOT/"governance/mac-engineer/ENGURU_MANAGEMENT_V69_FOUNDATION_ACCEPTANCE_V1.json"
DOC=ROOT/"governance/mac-engineer/ENGURU_MANAGEMENT_V69_GITHUB_FOUNDATION_V1.md"
EVIDENCE=ROOT/"evidence/ENGURU_MANAGEMENT_V69_FOUNDATION_REVIEW_V1.json"
ALLOWED={
 "governance/mac-engineer/ENGURU_MANAGEMENT_V69_GITHUB_FOUNDATION_V1.md",
 "governance/mac-engineer/ENGURU_MANAGEMENT_V69_FOUNDATION_ACCEPTANCE_V1.json",
 "tests/test_enguru_management_v69_foundation.py",
 "evidence/ENGURU_MANAGEMENT_V69_FOUNDATION_REVIEW_V1.json"}
REQUIRED={"CONTROL_ID","REQUIREMENT","PASS_CONDITION","REQUIRED_EVIDENCE","VERIFIER","AUTHORITY","STATE","DEPENDENCIES","SOURCE_PIN","RECENCY","GATE_TYPE","OWNER_ACTION"}
def load():
 return json.loads(MATRIX.read_text(encoding="utf-8"))
def facts():
 raw=b"gh69-contained-fixture"
 return dict(source=True,fresh=True,main=True,known=True,owner=True,issuer=True,verifier=True,active=True,
             raw=raw,sha=hashlib.sha256(raw).hexdigest(),handoff=True,batch=["B01-09"],count=27,
             duplicate=False,writer=False,retry=0,production=False,self_claim=False,donecheck=True,main_write=False)
def oracle(f):
 """Independent, synthetic design-only guard; never signs or grants VERIFIED_FINISH."""
 if not all(f.get(k) is True for k in ("source","fresh","main")):return "HOLD_SOURCE"
 batch=f.get("batch")
 if (f.get("known") is not True or not isinstance(batch,list) or not 1<=len(batch)<=10
     or any(type(x) is not str or x not in ("B01-09","B01-10","B05-05") for x in batch)
     or len(set(batch))!=len(batch) or type(f.get("count")) is not int or f["count"]<0):return "HOLD_SCOPE"
 if not all(f.get(k) is True for k in ("owner","issuer","verifier","active")) or f.get("main_write"):return "HOLD_AUTHORITY"
 if not isinstance(f.get("raw"),bytes) or not f["raw"] or not f.get("handoff") or f.get("sha")!=hashlib.sha256(f["raw"]).hexdigest():return "HOLD_EVIDENCE"
 if f.get("duplicate") or f.get("writer"):return "HOLD_DUPLICATE_EFFECT"
 if type(f.get("retry")) is not int or f["retry"]<0:return "HOLD_RETRY"
 if f.get("production") or f.get("self_claim") or f.get("donecheck") is not True:return "HOLD_EXTERNAL_BINDING"
 return "DESIGN_READY"
CASES={
 "wrong_v3_sha":("source",False),"stale_head":("fresh",False),"pr_as_main":("main",False),
 "wrong_control_id":("known",False),"model_claim_as_owner":("owner",False),
 "fake_issuer":("issuer",False),"verified_true_only":("self_claim",True),
 "bad_sha":("sha","0"*64),"one_control_project_finish":("production",True),
 "duplicate_batch_id":("batch",["B01-09","B01-09"]),
 "duplicate_external_effect":("duplicate",True),"missing_donecheck":("donecheck",False),
 "valid_design":(None,None),"production_without_provider":("production",True),
 "negative_retry":("retry",-1),"bool_as_counter":("count",True),
 "missing_handoff":("handoff",False),"expired_receipt":("active",False),
 "same_verifier_as_producer":("verifier",False),"raw_bytes_missing":("raw",b""),
 "unapproved_main_write":("main_write",True),"overlapping_writer":("writer",True),
 "valid_batch_design":("batch",["B01-09","B01-10"]),
 "out_of_range_batch":("batch",["B01-09"]*11)}
class ContractTests(unittest.TestCase):
 def test_exact_file_scope(self):
  j=load()
  self.assertEqual(set(j["review_scope"]["allowed_files"]),ALLOWED)
  self.assertTrue(all((ROOT/p).is_file() for p in ALLOWED))
 def test_canonical_lock(self):
  j=load(); p=ROOT/j["governance"]["canonical_v3_path"]
  if not p.exists():self.skipTest("Complete GitHub checkout required")
  self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),j["governance"]["canonical_v3_sha256"])
 def test_12_original_conditions(self):
  j=load(); rows=j["controls"]
  self.assertEqual(len(rows),12)
  self.assertEqual(j["control_count"],12)
  self.assertEqual([x["CONTROL_ID"] for x in rows],[f"GH69-BASE-{i:02d}" for i in range(1,13)])
  for x in rows:
   self.assertTrue(REQUIRED<=x.keys())
   self.assertEqual(x["STATE"],"HOLD_REAL_GITHUB_EXECUTION")
   self.assertTrue(x["REQUIRED_EVIDENCE"])
   for k in ("REQUIREMENT","PASS_CONDITION","VERIFIER","AUTHORITY","SOURCE_PIN"):
    self.assertTrue(isinstance(x[k],str) and bool(x[k].strip()))
 def test_source_pins(self):
  s=load()["source_snapshot"]
  for k in ("control_main","control_pr191","product_main","product_pr14"):
   self.assertRegex(s[k],r"^[0-9a-f]{40}$")
  self.assertEqual((s["control_review_pass"],s["control_total"]),(27,100))
  self.assertEqual(s["b01_09"],"HOLD")
  self.assertEqual(s["official_h1_h2_h3"],"0/12")
 def test_preservation(self):
  j=load()
  self.assertEqual(j["governance"]["new_core"],0)
  self.assertFalse(j["governance"]["ninth_stage"])
  self.assertEqual(len(j["governance"]["eight_stages"]),8)
  self.assertEqual(j["review_scope"]["main_change"],0)
  self.assertEqual(j["review_scope"]["osi_change"],0)
  self.assertEqual(j["review_scope"]["product_ledger_change"],0)
  self.assertEqual(j["review_scope"]["merge_authority"],"NOT_GRANTED")
 def test_24_matrix(self):
  rows=load()["adversarial_scenarios"]
  self.assertEqual(len(rows),24)
  self.assertEqual([r["id"] for r in rows],[f"A{i:02d}" for i in range(1,25)])
  self.assertEqual(set(r["mutation"] for r in rows),set(CASES))
 def test_security_coverage(self):
  s=load()["security"]; valid={x["id"] for x in load()["adversarial_scenarios"]}
  self.assertEqual(len(s["stride"]),6)
  self.assertGreaterEqual(len(s["owasp"]),8)
  for g in s["stride"]+s["owasp"]:
   self.assertTrue(g["scenario_ids"])
   self.assertTrue(set(g["scenario_ids"])<=valid)
 def test_batch_boundaries(self):
  b=load()["batch_v2"]
  self.assertEqual((b["candidate_ids_min"],b["candidate_ids_max"]),(1,10))
  self.assertFalse(b["changes_existing_product_progress"])
  self.assertTrue(b["fixture_ids_not_production_authority"])
 def test_external_authority(self):
  j=load(); s=json.dumps(j["authority_adapter_contract"])
  self.assertIn("NONCE",s)
  self.assertIn("HOLD_EXTERNAL_BINDING",DOC.read_text(encoding="utf-8"))
  self.assertEqual(j["review_scope"]["specialized_gh69_ci"],"HOLD_WORKFLOW_NOT_IN_FOUR_FILE_ALLOWLIST")
 def test_competitor_benchmark_unmeasured(self):
  b=load()["benchmark"]
  self.assertEqual(b["current_state"],"NOT_MEASURED_IN_REAL_COMPETITOR_RUNTIME")
  self.assertGreaterEqual(b["run_count_per_scenario_min"],30)
 def test_evidence_is_only_candidate(self):
  e=json.loads(EVIDENCE.read_text())
  self.assertEqual(e["authority"]["verified_finish"],"HOLD")
  self.assertEqual(e["github"]["main_writes"],0)
  self.assertEqual(e["github"]["pr191_writes"],0)
 def test_no_self_issued_finish(self):
  f=facts(); f["production"]=True
  self.assertEqual(oracle(f),"HOLD_EXTERNAL_BINDING")
  f=facts();f["self_claim"]=True
  self.assertEqual(oracle(f),"HOLD_EXTERNAL_BINDING")
 def test_wrong_catalog_and_raw_sha(self):
  f=facts();f["known"]=False
  self.assertEqual(oracle(f),"HOLD_SCOPE")
  f=facts();f["raw"]=b"modified"
  self.assertEqual(oracle(f),"HOLD_EVIDENCE")
 def test_valid_design_scope(self):
  self.assertEqual(oracle(facts()),"DESIGN_READY")
  self.assertNotEqual(oracle(facts()),"PROJECT_VERIFIED_FINISH")
class AdversarialTests(unittest.TestCase):pass
def make_test(row):
 def test(self):
  f=facts(); key,value=CASES[row["mutation"]]
  if key is not None:f[key]=value
  self.assertEqual(oracle(f),row["expected"],row["id"]+" "+row["mutation"])
 return test
for row in load()["adversarial_scenarios"]:
 setattr(AdversarialTests,"test_"+row["id"].lower(),make_test(row))
if __name__=="__main__":unittest.main()
