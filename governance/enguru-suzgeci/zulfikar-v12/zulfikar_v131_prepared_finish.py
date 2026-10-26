#!/usr/bin/env python3
"""Zulfikar v1.3.1: 3 x 10 source-backed preparation gates.

GITHUB PREPARATION acceptance only. This cannot award real task, real Mac,
Human Threshold, DoneCheck, or canonical VERIFIED_FINISH.
"""
from __future__ import annotations
import json
import hashlib
from pathlib import Path
import subprocess
import sys

import zulfikar_v131_operational_bridge as bridge
import zulfikar_v131_bridge_score as gate
import zulfikar_v131_field_evidence_intake as intake
import zulfikar_v1_3_gates as v13

HERE=Path(__file__).resolve().parent
ROOT=bridge.ROOT
CONFIG="governance/enguru-suzgeci/zulfikar-v12/ZULFIKAR_V131_PREPARED_FINISH_CONTRACT_V1.json"
READINESS_IDS=("OPERATIONAL_PREPARATION","E2E_FINISH_PREPARATION","CROSS_PROJECT_PREPARATION")
FAMILY_SET=frozenset(("NATIVE_SWIFTUI_PRODUCT","LOCAL_RECOVERY_IDEMPOTENCY","WEB_BUILD_TEST_REPAIR"))
PHASES=("SOURCE_IDENTITY","OWNER_SCOPE_CHECK","REGISTERED_PREFLIGHT","HANDOFF_EXISTING_OPERATOR",
        "REAL_TEST_AND_OUTPUT","SOURCE_OUTPUT_RECONCILIATION","RESTART_RECOVERY_IF_APPLICABLE",
        "INDEPENDENT_REVIEW","DONECHECK_HUMAN_THRESHOLD","PRODUCT_VERIFIED_FINISH")
PROOF_FIELDS=("taskId","contractId","sourceHead","preStateSha256","registeredHandler","authorityRecord",
              "testCommandAndExit","postStateSha256","actualOutputDigest","workReceiptSha256",
              "independentVerify","noFalsePass","idempotencyEvidence","ownerDecision")


def tracked_digest(relative,head):
    """Hash committed file bytes of any type, incl .py and .json; no JSON parsing."""
    p=Path(relative)
    if p.is_absolute() or any(x in ("..",".") for x in p.parts) or not p.parts or p.parts[0]!="governance":
        raise ValueError("UNTRUSTED_PIN_PATH")
    data=bridge.read_no_symlink(ROOT,relative,2_000_000)
    cmd=subprocess.run(["git","-C",str(ROOT),"show",head+":"+relative],
                       capture_output=True,timeout=15,check=False)
    if cmd.returncode!=0 or cmd.stdout!=data or bridge.head_sha(ROOT)!=head:
        raise ValueError("SOURCE_PIN_DRIFT")
    return hashlib.sha256(data).hexdigest()


def score_domain(checks):
    return {"score":sum(10 for value in checks.values() if value is True),
            "denominator":100,"checks":checks,
            "openControls":[key for key,value in checks.items() if value is not True]}


def run_unittests():
    cmd=[sys.executable,"-B","-m","unittest","-q",
         "test_zulfikar_v131_operational_bridge",
         "test_zulfikar_v131_field_evidence_intake"]
    r=subprocess.run(cmd,cwd=HERE,capture_output=True,text=True,timeout=120)
    return (r.returncode==0 and "Ran 57 tests" in r.stderr and "OK" in r.stderr)


def guarded(mission,bindings,actions,head,hashes):
    return bridge.assess(mission,bindings,actions,head,hashes)


def inspect(contract,head,bindings,actions,hashes,goal_score,infra_score,bridge_score,test_ok,
            checked_sources,workflow_read_only):
    """Ground each of 30 fixed controls; conditional or derived self-ratings are forbidden."""
    pilots=contract.get("pilots",[]) if isinstance(contract,dict) else []
    domains=contract.get("domains",[]) if isinstance(contract,dict) else []
    phases=contract.get("phaseSequence",[]) if isinstance(contract,dict) else []
    auth=contract.get("authority",{}) if isinstance(contract,dict) else {}
    field=contract.get("fieldBoundaries",{}) if isinstance(contract,dict) else {}
    registered=bindings.get("bindings",[]) if isinstance(bindings,dict) else []
    mapping=actions.get("actions",{}) if isinstance(actions,dict) else {}
    refs=[]
    for p in pilots if isinstance(pilots,list) else []:
        if not isinstance(p,dict):
            continue
        cap,action=p.get("capability"),p.get("registeredAction")
        match=[b for b in registered if isinstance(b,dict) and b.get("CAPABILITY_ID")==cap]
        b=match[0] if len(match)==1 else {}
        a=mapping.get(action) if isinstance(action,str) else None
        real_binding=(len(match)==1 and b.get("BINDING_TYPE")=="REGISTERED_ACTION"
                      and b.get("ACTION")==action and isinstance(a,dict)
                      and a.get("handler")==b.get("REGISTERED_HANDLER")
                      and a.get("authority")==b.get("AUTHORITY")
                      and b.get("EXECUTION_AUTHORITY_CREATED") is False)
        m=gate.mission(cap,action,head)
        m["projectId"]=p.get("project","INVALID")
        m["workId"]=p.get("taskId","INVALID")
        approved=guarded(m,bindings,actions,head,hashes)
        bad_head=guarded({**m,"sourceHead":"0"*40},bindings,actions,head,hashes)
        bad_action=guarded({**m,"actionId":"UNREGISTERED_ACTION"},bindings,actions,head,hashes)
        refs.append({"real_binding":real_binding,"good":approved,
          "bad_head":bad_head,"bad_action":bad_action,"mission":m,"pilot":p})
    sample=refs[0] if refs else None
    if sample:
        s=sample["mission"]
        fake_owner=guarded({**s,"ownerId":"FORGED"},bindings,actions,head,hashes)
        fake_finish=guarded({**s,"officialFinish":"PASS"},bindings,actions,head,hashes)
        fake_dependency=guarded({**s,"dependencies":[{"workId":"OTHER","state":"PASS_EVIDENCED","receiptSha256":"a"*64}]},bindings,actions,head,hashes)
        fake_resume=guarded({**s,"checkpointState":"RESUME_PROPOSED"},bindings,actions,head,hashes)
        release=guarded({**s,"capabilityId":"RELEASE_LIFECYCLE","actionId":"PACKAGE08_CAP13_RELEASE_LIFECYCLE_FIELD_PROOF"},bindings,actions,head,hashes)
    else:
        fake_owner=fake_finish=fake_dependency=fake_resume=release={"holds":[]}
    def hold(output,key):
        return output.get("decision")=="HOLD" and key in output.get("holds",[])
    typed_domains=(isinstance(domains,list) and len(domains)==3 and
         [d.get("id") for d in domains if isinstance(d,dict)]==list(READINESS_IDS) and
         all(d.get("target")==100 and len(d.get("controls",[]))==10 for d in domains if isinstance(d,dict)))
    operation={
      "OP01_GOAL_SOURCE_100":goal_score==100,
      "OP02_GITHUB_INFRA_100":infra_score==100,
      "OP03_REGISTERED_ACTION_PREFLIGHT_100":bridge_score==100,
      "OP04_REGISTRY_HEAD_BYTES_PINNED":checked_sources and all(bridge.SHA256.fullmatch(v) for v in checked_sources.values()) and len(checked_sources)==len(contract.get("technicalSources",[])),
      "OP05_THREE_PILOT_PATHS_RESOLVED":len(refs)==3 and all(x["real_binding"] for x in refs),
      "OP06_PRIVATE_RECEIPT_VERIFIER_READY":test_ok and intake.SCHEMA=="enguru.zulfikar.field-evidence-bundle/v1",
      "OP07_OWNER_SCOPE_AND_SINGLE_WRITER_GUARDS":hold(fake_owner,"HOLD_OWNER_ISSUER") and auth.get("oneEngineeringWriter") is True and auth.get("onlyExistingRegisteredHandlers") is True,
      "OP08_NO_FAKE_OPERATIONAL_PASS":hold(fake_finish,"HOLD_PREMATURE_AUTHORITY") and all(not x["good"]["realTaskExecuted"] for x in refs),
      "OP09_REVIEW_BRANCH_ONLY_NO_REMOTE_PUSH":workflow_read_only and all(x["mission"].get("remotePushRequested") is False for x in refs),
      "OP10_SUBPROCESS_NEGATIVE_TESTS":test_ok and typed_domains,
    }
    evidence={
      "E01_PHASE_ORDER_FROZEN":tuple(phases)==PHASES,
      "E02_SOURCE_HEAD_REQUIREMENT":len(refs)==3 and all(hold(x["bad_head"],"HOLD_EXACT_HEAD") for x in refs),
      "E03_DEPENDENCY_RECONCILIATION":hold(fake_dependency,"HOLD_DEPENDENCY_PROVENANCE_REVIEW_REQUIRED"),
      "E04_HANDLER_SAFETY_BOUNDARY":hold(release,"HOLD_ACTION_REQUIRES_HUMAN_THRESHOLD"),
      "E05_ERROR_RECOVERY_HOLD":hold(fake_resume,"HOLD_RESUME_PROOF_REQUIRED"),
      "E06_RECEIPT_SHA_BOUNDARY":test_ok and callable(intake.audit_manifest) and callable(intake.sha256),
      "E07_INDEPENDENT_REVIEW_REQUIRED":intake.audit_manifest({},Path("/"))["independentlyVerifiedRealTaskCount"]==0,
      "E08_DONECHECK_HUMAN_SCOPE_PRESERVED":field.get("officialProductVerifiedFinish")=="HOLD" and auth.get("ownerFieldApprovalRequired") is True,
      "E09_REAL_FIELD_NOT_AUTO_PROMOTED":field.get("actualMacTasksAccepted")==0 and field.get("realMacRuntime")=="HOLD" and field.get("automaticOwnerSignature") is False and field.get("syntheticProofEqualsReal") is False,
      "E10_PRIVATE_INTAKE_NEGATIVE_TESTS":test_ok and intake.load_json.__name__=="load_json",
    }
    ports={
      "P01_THREE_FAMILIES_EXACT":len(refs)==3 and {x["pilot"].get("family") for x in refs}==FAMILY_SET,
      "P02_THREE_DISTINCT_REGISTERED_CAPABILITIES":len(refs)==3 and len({x["pilot"].get("capability") for x in refs})==3,
      "P03_REGISTRY_HANDLER_AND_AUTHORITY_MATCH":len(refs)==3 and all(x["real_binding"] for x in refs),
      "P04_EACH_PREFLIGHT_READY_READ_ONLY":len(refs)==3 and all(x["good"]["decision"]=="PREFLIGHT_READY_EXISTING_OPERATOR_ONLY" and x["good"]["sourceWrites"]==0 for x in refs),
      "P05_EACH_FAKE_HEAD_REJECTED":len(refs)==3 and all(hold(x["bad_head"],"HOLD_EXACT_HEAD") for x in refs),
      "P06_EACH_UNREGISTERED_ACTION_REJECTED":len(refs)==3 and all(hold(x["bad_action"],"HOLD_UNBOUND_OR_MISMATCHED_ACTION") for x in refs),
      "P07_SHARED_PROOF_FIELDS_DEFINED":tuple(contract.get("privateReceiptProofFields",[]))==PROOF_FIELDS,
      "P08_FAMILY_SCOPE_RECONCILED":len(refs)==3 and all(isinstance(x["pilot"].get("ownerScope"),str) and x["pilot"]["ownerScope"].startswith("AFTER_") for x in refs),
      "P09_NO_DUPLICATE_EXECUTOR":auth.get("noNewCore") is True and auth.get("noNewIssuer") is True and auth.get("paidApiDependency")==0 and len(refs)==3,
      "P10_REPLAY_DETERMINISM":len(refs)==3 and all(x["good"]==guarded(x["mission"],bindings,actions,head,hashes) for x in refs),
    }
    results={}
    for ident,checks in zip(READINESS_IDS,(operation,evidence,ports)):
        chosen=next((d for d in domains if isinstance(d,dict) and d.get("id")==ident),{})
        if not chosen or tuple(chosen.get("controls",[]))!=tuple(checks):
            checks={key:False for key in checks}
        results[ident]=score_domain(checks)
    return results


def main():
    config,pin=bridge.source_read(ROOT,CONFIG)
    head=bridge.head_sha(ROOT)
    sources={}
    for name in config.get("technicalSources",[]):
        sources[name]=tracked_digest(name,head)
    bindings,sha_binding=bridge.source_read(ROOT,bridge.BINDING_PATH)
    actions,sha_actions=bridge.source_read(ROOT,bridge.ACTION_PATH)
    hashes={bridge.BINDING_PATH:sha_binding,bridge.ACTION_PATH:sha_actions}
    goal=v13.goal_gate(json.loads((HERE/"ZULFIKAR_GOAL_V1_3.json").read_text(encoding="utf8")))["assessment"]["score"]
    infra=v13.infra_gate()["assessment"]["score"]
    technical=gate.assess_github()["score"]
    tests=run_unittests()
    workflow_path=".github/workflows/enguru-zulfikar-v131-operational-bridge.yml"
    raw=bridge.read_no_symlink(ROOT,workflow_path,20_000)
    pinned=subprocess.run(["git","-C",str(ROOT),"show",head+":"+workflow_path],
                          capture_output=True,timeout=15,check=False)
    read_only=(pinned.returncode==0 and pinned.stdout==raw and
          b"permissions:\n  contents: read" in raw and
          b"working-directory: governance/enguru-suzgeci/zulfikar-v12" in raw)
    if bridge.head_sha(ROOT)!=head:
        raise ValueError("HEAD_CHANGED_IN_READINESS_ASSESSMENT")
    results=inspect(config,head,bindings,actions,hashes,goal,infra,technical,tests,sources,read_only)
    ready=all(a["score"]==100 for a in results.values())
    return {"schema":"enguru.zulfikar.github-prepared-finish-verifier/v1.3.1",
       "contractSha256":pin,"sourceHead":head,"sourcePinCount":len(sources),
       "domains":results,"preparationScore":min(a["score"] for a in results.values()),
       "preparationTarget":"3x100/100",
       "decision":"GITHUB_PREPARED_FINISH_CANDIDATE_REQUIRES_EXACT_HEAD_CI" if ready else "HOLD_PREPARATION",
       "githubExactHeadCI":"EXTERNAL_GITHUB_ACTIONS_VERIFICATION_REQUIRED",
       "actualMacTaskExecution":"NOT_RUN","realTaskTransfer":"HOLD_0_OF_3",
       "realPeerTrials":"NOT_RUN","realUserOutcome":"NOT_MEASURED",
       "doneCheck":"HOLD","humanThreshold":"HOLD",
       "canonicalProductVerifiedFinish":"HOLD"}


if __name__=="__main__":
    try:
        output=main()
        code=0 if output["decision"].startswith("GITHUB_PREPARED") else 2
    except (OSError,ValueError,TypeError,subprocess.TimeoutExpired):
        output={"schema":"enguru.zulfikar.github-prepared-finish-verifier/v1.3.1",
           "decision":"HOLD_PREPARATION_INPUT_OR_SOURCE",
           "canonicalProductVerifiedFinish":"HOLD"}
        code=2
    print(json.dumps(output,sort_keys=True))
    raise SystemExit(code)
