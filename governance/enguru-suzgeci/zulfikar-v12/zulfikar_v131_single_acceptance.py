#!/usr/bin/env python3
"""Single authoritative 6-domain Zulfikar v1.3.1 work-to-evidence closure.

Runs solely read-only. Never creates a second issuer, executor, or owner grant.
No JSON claim is capable of issuing official PASS or human authorization.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

import zulfikar_v131_operational_bridge as preflight

ROOT=preflight.ROOT
CONTRACT="governance/enguru-suzgeci/zulfikar-v12/ZULFIKAR_V131_OPERATIONAL_SCORECARD_V1.json"
SCHEMA="enguru.zulfikar.single-authority-closure/v1.3.1"
SIX=("GOAL","GITHUB_ENGINE","TEST_CI","GOVERNANCE","PORTABILITY","E2E_REAL")
OPEN=("GOVERNANCE","PORTABILITY","E2E_REAL")
WEIGHTS=(10,10,10,25,30,15)
OBSERVED=(100,100,100,98,90,65)
CLOSURES=("ZF.G1.01","ZF.G1.02","ZF.G1.03")
FAMILIES=("NATIVE_SWIFTUI_PRODUCT","LOCAL_RECOVERY_IDEMPOTENCY","WEB_BUILD_TEST_REPAIR")
PHASES=("SOURCE_RECONCILE","OWNER_SCOPE","EXISTING_ACTION_PREFLIGHT",
 "EXISTING_EXECUTOR_ACTUAL_TASK","TEST_REPAIR_AND_RECOVERY",
 "INDEPENDENT_EVIDENCE_VERIFICATION","EXISTING_DONECHECK_AND_HUMAN_THRESHOLD",
 "EACH_SIX_DOMAIN_SCORE_AT_100","GOAL1_OFFICIAL_VERIFIED_FINISH","UNLOCK_GOAL2")
EVIDENCE_FIELDS=("taskId","contractId","sourceHead","preStateSha256","registeredHandler",
 "authorityRecord","testCommandAndExit","postStateSha256","actualOutputDigest",
 "workReceiptSha256","independentVerify","noFalsePass","idempotencyEvidence","ownerDecision")


def valid_contract(doc):
    """Freeze the original denominator and three HOLD operations; no score inflation."""
    faults=[]
    if not isinstance(doc,dict):
        return ["CONTRACT_INVALID"]
    c=doc.get("canonicalClosure",{})
    domains=doc.get("domains",[])
    if not isinstance(c,dict) or c.get("schema")!=SCHEMA:
        faults.append("SINGLE_AUTHORITY_SCHEMA")
        c={}
    if not isinstance(domains,list) or len(domains)!=6 or \
        any(not isinstance(d,dict) for d in domains):
        faults.append("SIX_DOMAINS_REQUIRED")
        domains=[]
    if (tuple(d.get("id") for d in domains)!=SIX or
        tuple(d.get("weight") for d in domains)!=WEIGHTS or
        tuple(d.get("review") for d in domains)!=OBSERVED):
        faults.append("FROZEN_SIX_DOMAIN_BASELINE_DRIFT")
    if len(domains)==6:
        if (sum(d.get("weight",0) for d in domains)!=100 or
            doc.get("weightedAfterBridge")!=91.25 or
            doc.get("roundedCurrentOverall")!=91 or
            doc.get("overallOperationalVerdict")!="HOLD_91_100"):
            faults.append("WEIGHTED_SCORE_AUTHORITY_DRIFT")
        if any(d.get("verdict")!=("PASS_SCOPE_LIMITED" if d.get("id") not in OPEN
                    else "HOLD_UNDER_100") for d in domains):
            faults.append("UNSUPPORTED_DOMAIN_PASS_CLAIM")
    op=c.get("closureOperations",[])
    if not isinstance(op,list) or len(op)!=3 or \
       any(not isinstance(t,dict) for t in op):
        faults.append("THREE_CLOSURE_OPERATIONS_REQUIRED")
        op=[]
    if (tuple(o.get("id") for o in op)!=CLOSURES or
        tuple(o.get("dimension") for o in op)!=OPEN or
        tuple(o.get("current") for o in op)!=(98,90,65) or
        any(o.get("targetScore")!=100 or o.get("completion")!="HOLD" or
        not o.get("requiredEvidence") or not o.get("acceptance") or
        not o.get("task") or not o.get("authorization") for o in op)):
        faults.append("CLOSURE_TARGET_OR_HOLD_DRIFT")
    pilots=c.get("pilotProfiles",[])
    if not isinstance(pilots,list) or len(pilots)!=3 or \
        any(not isinstance(p,dict) for p in pilots):
        faults.append("THREE_PILOTS_REQUIRED")
        pilots=[]
    if (tuple(p.get("family") for p in pilots)!=FAMILIES or
        len({p.get("taskId") for p in pilots})!=3 or
        any(not p.get("scopeNote") or p.get("runtimeStatus","").startswith("PASS")
            or not p.get("project") for p in pilots)):
        faults.append("PILOT_SCOPE_OR_IDENTITY_DRIFT")
    if tuple(c.get("phaseSequence",[]))!=PHASES:
        faults.append("PHASE_SEQUENCE_DRIFT")
    p=c.get("protected",{})
    if not isinstance(p,dict) or not all(p.get(k) is True for k in (
        "zeroAdditionalPaidServices","oneHumanOwner","oneActiveEngineeringWriter",
        "noSecondCore","noSecondIssuer")) or p.get("mainMutationWithoutReview") is not False or \
        p.get("macRuntimeMutationWithoutOwner") is not False:
        faults.append("PROTECTED_AUTHORITY_DRIFT")
    final=c.get("strictFinish",{})
    if not isinstance(final,dict) or any(final.get(k) is not False for k in (
        "allSixDomains100","allThreeClosureOperationsAccepted","ownerAccepted")) or \
        final.get("realMacTaskPasses")!=0 or final.get("requiredRealMacTasks")!=3 or \
        final.get("existingDoneCheck")!="HOLD" or final.get("officialVerifiedFinish")!="HOLD":
        faults.append("REAL_FINISH_UNJUSTIFIED")
    if c.get("goal2State")!="LOCKED_UNTIL_GOAL1_HUMAN_AUTHORIZED_VERIFIED_FINISH" or \
       c.get("currentState")!="GOAL1_REAL_FIELD_HOLD":
        faults.append("PREMATURE_GOAL2_UNLOCK")
    if doc.get("allSixDimensions100") is not False or \
       doc.get("allSixDimensionsPass") is not False or \
       doc.get("verifiedFinishVerdict")!="HOLD":
        faults.append("FALSE_CANONICAL_FINISH")
    return sorted(set(faults))


def existing_bindings(bindings,actions,p):
    """Checks current registry identity, never a user/task-specific permission."""
    bind_list=bindings.get("bindings",[]) if isinstance(bindings,dict) else []
    action_map=actions.get("actions",{}) if isinstance(actions,dict) else {}
    cap=p.get("capability")
    matches=[b for b in bind_list if isinstance(b,dict) and b.get("CAPABILITY_ID")==cap]
    b=matches[0] if len(matches)==1 else {}
    key=p.get("action")
    a=action_map.get(key) if isinstance(key,str) and isinstance(action_map,dict) else None
    correct=(len(matches)==1 and b.get("BINDING_TYPE")=="REGISTERED_ACTION"
        and b.get("ACTION")==key and isinstance(a,dict)
        and a.get("handler")==b.get("REGISTERED_HANDLER")
        and a.get("authority")==b.get("AUTHORITY")
        and b.get("EXECUTION_AUTHORITY_CREATED") is False)
    return {"matchingExistingRegistry":bool(correct),
       "handler":b.get("REGISTERED_HANDLER") if correct else None,
       "registeredAuthority":b.get("AUTHORITY") if correct else None,
       "specificTaskAuthorityGranted":False,
       "actualHandlerInvoked":False,
       "registeredActionIsNotProductAcceptance":True}


def calculate(doc, source_head, registry_hashes, bind,actions):
    faults=valid_contract(doc)
    closure=doc.get("canonicalClosure",{}) if isinstance(doc,dict) else {}
    pilots=closure.get("pilotProfiles",[]) if isinstance(closure,dict) else []
    if not isinstance(pilots,list):
        pilots=[]
    paths=[{"taskId":p.get("taskId"),
        "family":p.get("family"),
        "project":p.get("project"),
        "githubPR":p.get("githubPR"),
        "sourceHead":source_head,
        "capability":p.get("capability"),
        "action":p.get("action"),
        "scope":p.get("scopeNote"),
        "binding":existing_bindings(bind,actions,p)}
        for p in pilots if isinstance(p,dict)]
    if len(paths)!=3 or any(not p["binding"]["matchingExistingRegistry"] for p in paths):
        faults.append("EXISTING_ACTION_BINDING_NOT_VERIFIED")
    operations=[]
    for entry in closure.get("closureOperations",[]) if isinstance(closure,dict) else []:
        if not isinstance(entry,dict):
            continue
        operations.append({"id":entry.get("id"),
          "dimension":entry.get("dimension"),"current":entry.get("current"),
          "target":entry.get("targetScore"),"currentStatus":"HOLD",
          "executor":entry.get("executor"),"task":entry.get("task"),
          "requiredEvidence":entry.get("requiredEvidence"),
          "authorization":entry.get("authorization"),
          "acceptedExternalEvidenceCount":0,
          "nextProof":entry.get("requiredEvidence",[None])[0],
          "closed":False})
    return {
      "schema":"enguru.zulfikar.single-acceptance-live-status/v1.3.1",
      "singleAcceptanceSource":CONTRACT,
      "sourceHead":source_head,
      "contractValid":not faults,
      "sourceRegistryHashes":registry_hashes,
      "faults":sorted(set(faults)),
      "target":"ALL_SIX_DOMAINS_100_100",
      "sixDomains":[{"id":d["id"],"recordedScore":d["review"],"target":100,
        "verdict":d["verdict"]} for d in doc.get("domains",[]) if isinstance(d,dict)],
      "recordedOverall":91,
      "goal1":"HOLD_REAL_TASK_AND_OWNER_AUTHORITY",
      "goal2":"LOCKED_UNTIL_GOAL1_VERIFIED_FINISH",
      "operations":operations,
      "existingExecutorPaths":paths,
      "workflow":{"stages":list(PHASES),
        "dispatch":"EXISTING_AUTHORIZED_WORK_OR_MAC_ENGINEER_ONLY",
        "mainWriterCreated":False,"newIssuerCreated":False,"remotePush":False,
        "readOnlyReconciliation":True},
      "realMacExecutionAuthenticated":False,
      "realUserOutcomeIndependentlyVerified":False,
      "ownerSignatureAuthenticated":False,
      "threeHeterogeneousRealTasksAccepted":0,
      "peerRealTrialsAuthenticated":False,
      "doneCheck":"HOLD","humanThreshold":"HOLD",
      "preparedGithubScope":"PASS_SCOPED_HISTORICAL_SOURCE_CI",
      "officialVerifiedFinish":"HOLD",
      "nextSingleAction":"Upon actual PiLive Work completion, owner-authorized real Mac native source/binary/UI task evidence must be independently reconciled; then perform next authorized task in order.",
      "message":"No further subjective scorecards; 91/65/90 remain HOLD until trusted external facts justify moving this single six-domain acceptance contract."}


def main(argv=None):
    parser=argparse.ArgumentParser(description="Read-only canonical six-domain Zulfikar closure")
    parser.add_argument("--mode",choices=("status","plan"),default="status")
    args=parser.parse_args(argv)
    head=preflight.head_sha(ROOT)
    doc,sha=preflight.source_read(ROOT,CONTRACT)
    bindings,bhash=preflight.source_read(ROOT,preflight.BINDING_PATH)
    actions,ahash=preflight.source_read(ROOT,preflight.ACTION_PATH)
    if preflight.head_sha(ROOT)!=head:
        raise ValueError("HEAD_CHANGE_DURING_CLOSURE_CHECK")
    result=calculate(doc,head,{CONTRACT:sha,preflight.BINDING_PATH:bhash,
            preflight.ACTION_PATH:ahash},bindings,actions)
    if args.mode=="plan":
        # Task plans are proposals only. Owner must authorize actual execution.
        result["mode"]="READ_ONLY_EXISTING_OPERATOR_HANDOFF_PLAN"
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))
    return 2 if result["faults"] else 0


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except (ValueError,OSError,TypeError,KeyError,ImportError):
        print(json.dumps({"schema":"enguru.zulfikar.single-acceptance-live-status/v1.3.1",
             "goal1":"HOLD_SOURCE_OR_RUNTIME_ERROR","goal2":"LOCKED",
             "officialVerifiedFinish":"HOLD",
             "faults":["SOURCE_RUNTIME_UNTRUSTED"]},sort_keys=True))
        raise SystemExit(2)
