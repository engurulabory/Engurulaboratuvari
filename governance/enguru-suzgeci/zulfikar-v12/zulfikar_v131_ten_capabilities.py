#!/usr/bin/env python3
"""Zulfikar v1.3.1 ten capability evidence routing on ONE six-domain contract.

Checks actual committed source bytes. A routing/structural PASS is not proof
that the ten capabilities can accomplish a real user's goal or Verified Finish.
This executable has NO runtime dispatch/issuer permissions.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess

import zulfikar_v131_operational_bridge as source
import zulfikar_v131_universal_100_gate as umbrella

ROOT=source.ROOT
SCORECARD=umbrella.SCORECARD_PATH
POLICY=umbrella.POLICY_PATH
GOAL=umbrella.GOAL_PATH
IDS=tuple(f"K{i:02d}" for i in range(1,11))
SIX=frozenset(("GOAL","GITHUB_ENGINE","TEST_CI","GOVERNANCE","PORTABILITY","E2E_REAL"))
STAGES=umbrella.PHASE_IDS
METHOD_PREFIX="governance/enguru-suzgeci/zulfikar-v12/"
EXPECTED_STAGES=(
 "GOAL_ARCHITECTURE","PREPARATION","REAL_EXECUTION","PREPARATION",
 "REAL_EXECUTION","PRODUCT_FINISH","REAL_EXECUTION","PREPARATION",
 "PREPARATION","PRODUCT_FINISH")


def committed_file_sha(relative, head):
    """SHA256 of local bytes only when they match the exact immutable Git blob."""
    if not isinstance(relative,str) or not relative.startswith(METHOD_PREFIX):
        raise ValueError("UNTRUSTED_CAPABILITY_SOURCE")
    p=Path(relative)
    if p.is_absolute() or ".." in p.parts or "." in p.parts:
        raise ValueError("UNTRUSTED_CAPABILITY_PATH")
    local=source.read_no_symlink(ROOT,relative,2_000_000)
    proc=subprocess.run(["git","-C",str(ROOT),"show",head+":"+relative],
                        capture_output=True,timeout=15,check=False)
    if proc.returncode or proc.stdout!=local:
        raise ValueError("CAPABILITY_HEAD_DRIFT")
    return hashlib.sha256(local).hexdigest()


def simulate_repair_loop(initial, patches, max_rounds=3):
    """Toy diagnostic test fixture ONLY, never authorizes implementation/field PASS."""
    if not isinstance(initial,dict) or not initial or any(type(v) is not bool for v in initial.values()):
        return {"decision":"INVALID_DIAGNOSTIC","history":[],"acceptedScore":None}
    if not isinstance(patches,list) or type(max_rounds) is not int or not 1<=max_rounds<=12:
        return {"decision":"INVALID_DIAGNOSTIC","history":[],"acceptedScore":None}
    state=dict(initial)
    history=[]
    for index in range(max_rounds):
        eligible=all(state.values())
        history.append({"round":index+1,"diagnostic":sum(state.values())*100//len(state),
                        "open":[k for k,v in state.items() if not v]})
        if eligible:
            return {"decision":"SIMULATED_100_NOT_FIELD_ACCEPTANCE","history":history,
                    "acceptedScore":None}
        if index>=len(patches):
            break
        patch=patches[index]
        if not isinstance(patch,dict) or any(k not in state or type(v) is not bool for k,v in patch.items()):
            return {"decision":"INVALID_PATCH","history":history,"acceptedScore":None}
        # Tests may repair false checks; real score never changes based on claims.
        state.update(patch)
    return {"decision":"CONTINUE_IMPROVEMENT","history":history,"acceptedScore":None}


def inspect(scorecard,policy,goal,head,agent_text,verify_files=True):
    faults=[]
    if not isinstance(scorecard,dict) or not isinstance(policy,dict) or not isinstance(goal,dict):
        return {"decision":"CONTINUE_IMPROVEMENT","faults":["INVALID_AUTHORITY_SOURCE"],
                "capabilities":[],"actualFullyAcceptedCapabilities":0,"officialVerifiedFinish":"AWAIT_AUTHORIZED_EVIDENCE"}
    cc=scorecard.get("canonicalClosure",{})
    ten=cc.get("tenCapabilityMap",{}) if isinstance(cc,dict) else {}
    data=ten.get("capabilities",[]) if isinstance(ten,dict) else []
    if not isinstance(data,list) or len(data)!=10 or any(not isinstance(x,dict) for x in data):
        faults.append("TEN_CAPABILITIES_REQUIRED")
        data=[]
    if policy.get("acceptanceUniverse",{}).get("passThreshold")!=100 or \
       scorecard.get("acceptedOperationalScore") is not None or \
       scorecard.get("overallOperationalVerdict")!="CONTINUE_REAL_EVIDENCE_NOT_ACCEPTED":
        faults.append("ORIGINAL_ONE_HUNDRED_ONLY_AUTHORITY_DRIFT")
    if goal.get("universalUmbrella",{}).get("policyRef")!=POLICY:
        faults.append("GOAL_TO_POLICY_LINK_DRIFT")
    if "ZULFIKAR_V131_EVRENSEL_100_KABUL_ILKESI_V1.json" not in agent_text:
        faults.append("GLOBAL_SESSION_ENTRYPOINT_DRIFT")
    if ten.get("schema")!="enguru.zulfikar.v131-ten-capabilities-single-scorecard-map/v1" or \
       ten.get("stageDependency")!=list(STAGES) or \
       ten.get("goalToOutcomeRule")!="FIRST_STAGE_VERIFIED_100_IS_PREREQUISITE_NOT_SUFFICIENT_TO_GRANT_SUCCESSOR_100":
        faults.append("TEN_METHOD_SINGLE_AUTHORITY_DRIFT")
    glob=ten.get("globalAcceptance",{})
    if not isinstance(glob,dict) or glob.get("allTenVerified") is not False or \
       glob.get("acceptedCapabilities")!=0 or \
       glob.get("sourceCIAndSimulationCannotAutopromoteRealWork") is not True or \
       glob.get("existingDoneCheckAndHumanRequired") is not True or \
       glob.get("productVerifiedFinish")!="AWAIT_AUTHORIZED_EVIDENCE":
        faults.append("PREMATURE_TEN_CAPABILITY_ACCEPTANCE")
    orig=scorecard.get("domains",[])
    if not isinstance(orig,list) or len(orig)!=6 or {d.get("id") for d in orig if isinstance(d,dict)}!=SIX:
        faults.append("ORIGINAL_SIX_DOMAINS_CHANGED")
    results=[]
    for index,row in enumerate(data):
        errors=[]
        id_=row.get("id")
        if id_!=IDS[index] or not isinstance(row.get("code"),str) or not row["code"]:
            errors.append("CAPABILITY_ID_OR_CODE_DRIFT")
        if row.get("stage")!=EXPECTED_STAGES[index]:
            errors.append("CAPABILITY_STAGE_DRIFT")
        refs=row.get("existingDomainRefs")
        if not isinstance(refs,list) or not refs or any(not isinstance(v,str) or v not in SIX for v in refs) or len(set(refs))!=len(refs):
            errors.append("ORIGINAL_DOMAIN_LINK_DRIFT")
        paths=row.get("preparationSourceFiles")
        if not isinstance(paths,list) or len(paths)<2 or len(paths)!=len(set(x for x in paths if isinstance(x,str))) or \
           any(not isinstance(p,str) or not p.startswith(METHOD_PREFIX) for p in paths):
            errors.append("SOURCE_EVIDENCE_ROUTE_MISSING")
            paths=[]
        srcpins={}
        if not errors and verify_files:
            for p in paths:
                try:
                    srcpins[p]=committed_file_sha(p,head)
                except (OSError,ValueError,subprocess.TimeoutExpired):
                    errors.append("SOURCE_BYTES_OR_GIT_HEAD_MISMATCH")
                    break
        if not row.get("acceptanceRequirement") or not row.get("realFieldRequirement") or \
           not isinstance(row.get("name"),str) or not row["name"]:
            errors.append("REQUIRED_CAPABILITY_PROOF_MISSING")
        if row.get("verifiedFull100") is not False or row.get("finalPassGranted") is not False or \
           row.get("realAuthority")!="AWAIT_TRUSTED_RUNTIME_OR_OWNER":
            errors.append("PREMATURE_FULL_CAPABILITY_PASS")
        results.append({"id":id_,"name":row.get("name"),"stage":row.get("stage"),
          "sourceRoutingChecked":not errors,
          "sourcePins":srcpins,
          "assessment":"SOURCE_ROUTE_REVIEWED_ONLY" if not errors else "CONTINUE_SOURCE_REPAIR",
          "fullCapabilityPass":False,"acceptedScore":None,
          "realFieldOrOwnerEvidence":"AWAIT_AUTHORIZED_PROOF",
          "faults":sorted(set(errors))})
    route_ok=len(results)==10 and all(r["sourceRoutingChecked"] for r in results)
    if not route_ok:
        faults.append("CAPABILITY_ROUTE_REQUIREMENTS_OPEN")
    return {"schema":"enguru.zulfikar.v131-ten-capability-routing/v1",
       "singleAcceptanceAuthority":SCORECARD,"sourceHead":head,
       "checksPassed":sum(r["sourceRoutingChecked"] for r in results),
       "checksRequired":10,
       "sourceRoutesDecision":"TEN_SOURCE_ROUTES_VERIFIED_CI_REVIEW_REQUIRED" if not faults else "CONTINUE_IMPROVEMENT",
       "faults":sorted(set(faults)),"capabilities":results,
       "fullyVerifiedCapabilityCount":0,
       "verifiedFullCapabilityPass":False,
       "acceptedOverallScore":None,
       "firstStage100CannotAutoAcceptLaterStages":True,
       "ongoingGoal":"TEN_INDEPENDENTLY_EVIDENCED_100_OF_100_CAPABILITIES",
       "realMacField":"AWAIT_AUTHORIZED_EVIDENCE",
       "officialVerifiedFinish":"AWAIT_AUTHORIZED_DONECHECK_HUMAN_THRESHOLD"}


def main():
    head=source.head_sha(ROOT)
    scorecard,score_hash=source.source_read(ROOT,SCORECARD)
    policy,policy_hash=source.source_read(ROOT,POLICY)
    goal,goal_hash=source.source_read(ROOT,GOAL)
    agents=source.read_no_symlink(ROOT,"AGENTS.md",100_000)
    tracked=subprocess.run(["git","-C",str(ROOT),"show",head+":AGENTS.md"],
                           capture_output=True,timeout=15,check=False)
    if tracked.returncode or tracked.stdout!=agents or head!=source.head_sha(ROOT):
        raise ValueError("AGENTS_HEAD_DRIFT")
    result=inspect(scorecard,policy,goal,head,agents.decode("utf8"))
    result["sourceHashes"]={SCORECARD:score_hash,POLICY:policy_hash,GOAL:goal_hash}
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))
    return 0 if result["sourceRoutesDecision"]=="TEN_SOURCE_ROUTES_VERIFIED_CI_REVIEW_REQUIRED" else 2


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except (OSError,ValueError,TypeError,KeyError,subprocess.TimeoutExpired):
        print(json.dumps({"sourceRoutesDecision":"CONTINUE_IMPROVEMENT",
          "faults":["UNTRUSTED_SOURCE_OR_RUNTIME"],
          "fullyVerifiedCapabilityCount":0,"acceptedOverallScore":None,
          "officialVerifiedFinish":"AWAIT_AUTHORIZED_DONECHECK_HUMAN_THRESHOLD"},sort_keys=True))
        raise SystemExit(2)
