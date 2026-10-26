"""Test actual Zülfikar V1.4.1 source-binding and no premature finish."""
import copy
import json
import unittest
from pathlib import Path
from reuse_zulfikar_v141 import validate_contract,check_seal,evaluate_report

BASE=Path(__file__).resolve().parent
CONTRACT=json.loads((BASE/"ZULFIKAR_V141_SOURCE_REUSE.json").read_text(encoding="utf-8"))
SEAL={
  "schema":"enguru.zulfikar.v141.github-source-sha-seal/v1",
  "archiveSha256":CONTRACT["archive_sha256"],
  "repository":CONTRACT["source_repository"],
  "ownerDoneCheck":"NOT_ISSUED",
  "actualMacOsi":"NOT_EXECUTED",
  "verifiedFinish":"NOT_ISSUED",
  "stageFiles":[
    {"path":CONTRACT["source_prefix"]+name,"sha256":"a"*64} for name in
       ("preflight.py","dom/engine.py","dom/test_engine.py","dom/test_final_hardening.py",
        "architecture/zulfikar_v141_8_gate_architecture.json",
        "architecture/dom_v10_design.json","README.md","FINAL_KABUL_RAPORU.md",
        "SON_ACIMASIZ_DENETIM.md","evidence/.gitkeep")
  ]+[{"path":".github/workflows/enguru-zulfikar-v141-dom-preflight.yml","sha256":"b"*64}]
REPORT={
 "engineerPreparationScore":100,"architectureDesignControlsPassed":10,
 "architectureDesignControlsRequired":10,"realLocalUnittestExecutions":177,
 "GitHubCommitOrCI":"ACTION_RUNNER_TEST_SCOPE_ONLY",
 "productVerifiedFinish":"NOT_ISSUED",
 "threeRealLocalTestRounds":[{"pass":True,"tests":59} for _ in range(3)]
}
class SourceReuseTests(unittest.TestCase):
    def test_contract(self):
        self.assertTrue(validate_contract(CONTRACT))
        self.assertEqual([g["id"] for g in CONTRACT["gates"]],
                         ["T01","T02","A01","A02","A03","A04","A05","A06"])
    def test_seal_shape(self):
        self.assertEqual(len(check_seal(SEAL,CONTRACT)),11)
    def test_preflight_evidence_parser(self):
        self.assertTrue(evaluate_report(REPORT))
    def test_no_false_finish(self):
        for key,val in (("owner_acceptance","PASS"),("official_finish","PASS"),
                        ("osi_execution",1),("github_merge",1)):
            x={**CONTRACT,key:val}
            with self.assertRaises(ValueError):
                validate_contract(x)
    def test_wrong_engine_ref(self):
        for newref in ("main","a"*40,"",None):
            x={**CONTRACT,"source_git_commit":newref}
            if newref==CONTRACT["source_git_commit"]:
                continue
            if newref=="a"*40:
                self.assertTrue(validate_contract(x)) # syntactically valid but runtime SHA check still required
            else:
                with self.assertRaises(ValueError):
                    validate_contract(x)
    def test_stage_order_mutation(self):
        x=copy.deepcopy(CONTRACT)
        x["gates"][0],x["gates"][1]=x["gates"][1],x["gates"][0]
        with self.assertRaises(ValueError):
            validate_contract(x)
    def test_no_unapproved_P05(self):
        x=copy.deepcopy(CONTRACT)
        x["gates"][6]["state"]="PASS"
        with self.assertRaises(ValueError):
            validate_contract(x)
    def test_bad_seal(self):
        for field,value in (("ownerDoneCheck","PASS"),("actualMacOsi","PASS"),("verifiedFinish","PASS")):
            x={**SEAL,field:value}
            with self.assertRaises(ValueError):
                check_seal(x,CONTRACT)
    def test_source_drift(self):
        x=copy.deepcopy(SEAL)
        x["stageFiles"][0]["sha256"]="x"*64
        with self.assertRaises(ValueError):
            check_seal(x,CONTRACT)
    def test_result_forgery(self):
        for field,value in (("realLocalUnittestExecutions",178),
                            ("productVerifiedFinish","PASS"),("GitHubCommitOrCI","OFFICIAL_PASS")):
            self.assertFalse(evaluate_report({**REPORT,field:value}))
    def test_missing_round(self):
        self.assertFalse(evaluate_report({**REPORT,"threeRealLocalTestRounds":REPORT["threeRealLocalTestRounds"][:2]}))

if __name__=="__main__":
    unittest.main()
