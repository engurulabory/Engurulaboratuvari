"""The twelve upstream test cases are plans, never false proven skills."""
import copy
import json
from pathlib import Path
import unittest
from skill_kernel import OPERATIONS

BASE=Path(__file__).resolve().parent
PLAN=json.loads((BASE/"external_skill_proof_plan.json").read_text(encoding="utf-8"))
SOURCE=json.loads((BASE/"source_candidates.json").read_text(encoding="utf-8"))
LIC=json.loads((BASE/"root_license_observations.json").read_text(encoding="utf-8"))

def check(plan=PLAN):
    if not isinstance(plan,dict) or plan.get("measured_proven")!=0:
        return "HOLD"
    cases=plan.get("cases")
    if not isinstance(cases,list) or len(cases)!=12:
        return "HOLD"
    repos={x["repository"] for x in SOURCE["candidates"]}
    observed={x["repository"] for x in LIC["observations"]}
    ids=set()
    seen=set()
    for n,case in enumerate(cases,1):
        if not isinstance(case,dict) or case.get("id")!="P"+str(n).zfill(2):
            return "HOLD"
        repository=case.get("repository")
        if not isinstance(repository,str) or repository not in repos or repository not in observed or repository in seen:
            return "HOLD"
        seen.add(repository)
        if case.get("status") not in ("HOLD_RUNTIME_AND_TERMS","HOLD_LICENSE_AND_REAL_RUN","HOLD_REAL_TOOL_EXECUTION","HOLD_SOURCE_EXECUTION"):
            return "HOLD"
        if any(case.get(key) is not None for key in ("source_sha256","actual_run_receipt","independent_review")):
            return "HOLD"
        if any(not isinstance(case.get(k),str) or not case[k] for k in ("capability","real_task","required_evidence")):
            return "HOLD"
        ids.add(case["id"])
    return "EXTERNAL_TEST_PLAN_PASS" if len(ids)==12 and len(OPERATIONS)==12 else "HOLD"

class ExternalProofPlanTests(unittest.TestCase):
    def test_plan(self):
        self.assertEqual(check(),"EXTERNAL_TEST_PLAN_PASS")
    def test_counts_are_distinct(self):
        self.assertNotEqual(set(x["repository"] for x in PLAN["cases"]),set(OPERATIONS))
        self.assertEqual(len(PLAN["cases"]),12)
    def test_no_fabricated_proven(self):
        p=copy.deepcopy(PLAN)
        p["measured_proven"]=12
        self.assertEqual(check(p),"HOLD")
    def test_fake_receipt(self):
        p=copy.deepcopy(PLAN)
        p["cases"][0]["actual_run_receipt"]="PASS"
        self.assertEqual(check(p),"HOLD")
    def test_unknown_source(self):
        p=copy.deepcopy(PLAN)
        p["cases"][0]["repository"]="unknown/unknown"
        self.assertEqual(check(p),"HOLD")
    def test_bad_id(self):
        p=copy.deepcopy(PLAN)
        p["cases"][0]["id"]="P99"
        self.assertEqual(check(p),"HOLD")

if __name__=="__main__":
    unittest.main()
