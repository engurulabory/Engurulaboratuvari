#!/usr/bin/env python3
"""Zulfikar v1.3.1 universal 100-only policy; real authority is external.

A score below 100 is diagnostic only, never an acceptance verdict.
This code can check the policy/source. It cannot attest field or owner evidence.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

import zulfikar_v131_operational_bridge as source

ROOT=source.ROOT
POLICY_PATH="governance/enguru-suzgeci/zulfikar-v12/ZULFIKAR_V131_EVRENSEL_100_KABUL_ILKESI_V1.json"
SCORECARD_PATH="governance/enguru-suzgeci/zulfikar-v12/ZULFIKAR_V131_OPERATIONAL_SCORECARD_V1.json"
GOAL_PATH="governance/enguru-suzgeci/zulfikar-v12/ZULFIKAR_GOAL_V1_3.json"
PHASE_IDS=("GOAL_ARCHITECTURE","PREPARATION","REAL_EXECUTION","PRODUCT_FINISH")
EIGHT=("HAKIKATI_GOR","DEGERI_KORU","EKSIK_VE_IHTIYACI_TESPIT_ET",
       "GEREKLI_FARKI_URET","EKSIKLERI_TAMAMLA","KANITLA",
       "SONRAKI_IHTIYACI_BELIRLE","ILERLET")
LOOP=("ARCHITECT","ASSESS","DIAGNOSE","SIMULATE","REPAIR",
      "TEST_REAL_WHEN_AUTHORIZED","REASSESS","COUNTER_TEST","REPEAT_UNTIL_VERIFIED_100")


def classify(stage, diagnostic, evidence_origin="NONE"):
    """Pure proposed decision. Never mints an official PASS or owner authorization."""
    if stage not in PHASE_IDS:
        return {"decision":"INVALID_STAGE","acceptedScore":None,"diagnostic":None}
    if type(diagnostic) is not int or not 0<=diagnostic<=100:
        return {"decision":"INVALID_DIAGNOSTIC","acceptedScore":None,"diagnostic":None}
    if diagnostic!=100:
        return {"decision":"CONTINUE_IMPROVEMENT","acceptedScore":None,
                "diagnostic":diagnostic,"next":"DIAGNOSE_REPAIR_SIMULATE_TEST_REASSESS"}
    if evidence_origin in ("SIMULATION","SELF_REPORTED","NONE"):
        return {"decision":"AWAIT_VERIFIED_EVIDENCE","acceptedScore":None,
                "diagnostic":100,"next":"VERIFY_EVIDENCE_IN_CURRENT_SCOPE"}
    if stage in ("REAL_EXECUTION","PRODUCT_FINISH"):
        return {"decision":"AWAIT_AUTHORIZED_FIELD_AND_DONECHECK",
                "acceptedScore":None,"diagnostic":100,
                "next":"EXISTING_OWNER_DONECHECK_HUMAN_THRESHOLD"}
    if evidence_origin=="EXACT_HEAD_CI":
        return {"decision":"STAGE_100_CANDIDATE_EXACT_HEAD_CHECK_REQUIRED",
                "acceptedScore":None,"diagnostic":100,
                "next":"INDEPENDENTLY_CONFIRM_CI_RUN_AND_SCOPE"}
    return {"decision":"AWAIT_VERIFIED_EVIDENCE","acceptedScore":None,
            "diagnostic":100,"next":"VERIFY_EVIDENCE_IN_CURRENT_SCOPE"}


def controls(policy,scorecard,agents,goal):
    if not isinstance(policy,dict):policy={}
    if not isinstance(scorecard,dict):scorecard={}
    goal=goal if isinstance(goal,dict) else {}
    stages=policy.get("stageRoles",{})
    universe=policy.get("acceptanceUniverse",{})
    diagnostic=universe.get("diagnosticRange",{})
    decisions=policy.get("decisionModel",{})
    historical=scorecard.get("historicalDiagnosticBeforeCurrentPolicy",{})
    try:
        stage_keys=set(stages)==set(PHASE_IDS) and all(
          isinstance(stages[p],dict) and bool(stages[p].get("auth")) for p in PHASE_IDS)
    except (TypeError,AttributeError):
        stage_keys=False
    outcomes=[classify("PREPARATION",i,"EXACT_HEAD_CI") for i in (0,1,20,30,50,70,91,98,99)]
    checks={
      "U01_USER_GOAL_LOCKED":policy.get("governingPurpose","").startswith("Kullanıcının özgün hedefini") and "USER_GOAL" in policy.get("start",[]) and goal.get("universalUmbrella",{}).get("policyRef")==POLICY_PATH and goal.get("universalUmbrella",{}).get("neverSelfIssueRealFinish") is True,
      "U02_EIGHT_STAGES_UNCHANGED":tuple(policy.get("eightStages",[]))==EIGHT,
      "U03_ITERATIVE_LOOP_LOCKED":tuple(policy.get("loop",[]))==LOOP,
      "U04_ONLY_100_ACCEPTED":universe.get("passThreshold")==100 and universe.get("passOnlyWhenVerified") is True and decisions.get("onlyAcceptedNumericScore")==100,
      "U05_1_TO_99_DIAGNOSTIC_ONLY":diagnostic.get("min")==1 and diagnostic.get("max")==99 and diagnostic.get("authority")=="INTERNAL_DIAGNOSTIC_ONLY" and all(t["decision"]=="CONTINUE_IMPROVEMENT" and t["acceptedScore"] is None for t in outcomes),
      "U06_PREPARATION_VS_FIELD_SEPARATE":stage_keys and stages["PREPARATION"].get("auth")=="EXACT_HEAD_GITHUB_CI_AND_FROZEN_CONTROLS" and classify("REAL_EXECUTION",100,"EXACT_HEAD_CI")["acceptedScore"] is None and classify("PRODUCT_FINISH",100,"EXACT_HEAD_CI")["acceptedScore"] is None,
      "U07_SELF_REPORTED_100_REJECTED":all(classify("PREPARATION",100,x)["acceptedScore"] is None and classify("PREPARATION",100,x)["decision"]=="AWAIT_VERIFIED_EVIDENCE" for x in ("SIMULATION","SELF_REPORTED","NONE")),
      "U08_CANONICAL_91_IS_HISTORY":historical.get("score")==91 and historical.get("previousLabel")=="HOLD_91_100" and historical.get("preservedForAudit") is True and scorecard.get("overallOperationalVerdict")=="CONTINUE_REAL_EVIDENCE_NOT_ACCEPTED" and scorecard.get("acceptedOperationalScore") is None,
      "U09_OWNER_DONECHECK_PRESERVED":stages.get("PRODUCT_FINISH",{}).get("auth")=="EXISTING_DONECHECK_V12_PLUS_HUMAN_THRESHOLD" and all(k in policy.get("truthRules",[]) for k in ("ONE_HUMAN_OWNER","NO_NEW_ISSUER","SYNTHETIC_CANNOT_BE_FIELD_PROOF")),
      "U10_GLOBAL_START_AND_SAFE_END":"ZULFIKAR_V131_EVRENSEL_100_KABUL_ILKESI_V1.json" in agents and policy.get("scope")=="ALL_ENGURU_GITHUB_WORK_PROJECT_SESSIONS_ON_EXPLICIT_SOURCE_LOAD" and policy.get("completionSequence",[])[-2:]==["VERIFIED_FINISH","BITTI_DUR"] and decisions.get("noFiniteIterationCountGuarantee") is True,
    }
    return checks


def main():
    head=source.head_sha(ROOT)
    policy,policy_sha=source.source_read(ROOT,POLICY_PATH)
    score,score_sha=source.source_read(ROOT,SCORECARD_PATH)
    goal,goal_sha=source.source_read(ROOT,GOAL_PATH)
    raw=source.read_no_symlink(ROOT,"AGENTS.md",100_000)
    tracked=subprocess.run(["git","-C",str(ROOT),"show",head+":AGENTS.md"],
        capture_output=True,timeout=10)
    if tracked.returncode!=0 or tracked.stdout!=raw or source.head_sha(ROOT)!=head:
        raise ValueError("AGENTS_SOURCE_DRIFT")
    checks=controls(policy,score,raw.decode("utf-8"),goal)
    score100=sum(10 for v in checks.values() if v is True)
    result={
      "schema":"enguru.zulfikar.universal-100-policy-assessment/v1",
      "sourceHead":head,
      "pins":{POLICY_PATH:policy_sha,SCORECARD_PATH:score_sha,GOAL_PATH:goal_sha},
      "controls":checks,"codePolicyDiagnostic":score100,
      "policyDecision":"GITHUB_POLICY_100_CANDIDATE_EXACT_HEAD_CI_REQUIRED" if score100==100 else "CONTINUE_IMPROVEMENT",
      "legacy91":"HISTORICAL_DIAGNOSTIC_ONLY",
      "operationalAcceptedScore":None,
      "actualRealOperationalFinish":"AWAIT_AUTHORIZED_FIELD_EVIDENCE",
      "ownerDoneCheck":"EXTERNAL_AUTHORITY_ONLY",
      "productVerifiedFinish":"AWAIT_AUTHORIZED_EVIDENCE"
    }
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))
    return 0 if score100==100 else 2


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except (ValueError,OSError,TypeError,KeyError,UnicodeError,subprocess.TimeoutExpired):
        print(json.dumps({"policyDecision":"CONTINUE_IMPROVEMENT",
          "reason":"UNTRUSTED_SOURCE_OR_INVALID_POLICY",
          "operationalAcceptedScore":None,"productVerifiedFinish":"AWAIT_AUTHORIZED_EVIDENCE"},sort_keys=True))
        raise SystemExit(2)
