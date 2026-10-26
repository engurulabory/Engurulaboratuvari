#!/usr/bin/env python3
"""Exactly ten REAL GitHub source/CLI controls, never field/finish acceptance."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys

import zulfikar_v131_operational_bridge as bridge
from zulfikar_v1_3_gates import goal_gate

HERE=Path(__file__).resolve().parent


def mission(cap,action,head):
    return {"schema":bridge.SCHEMA,"missionId":"ZF131.BENCH.SMOKE.01",
      "projectId":"ENGURU_PILIVE_P02_USER_SCREEN","workId":"P02.S01.01",
      "capabilityId":cap,"actionId":action,"writerId":"single-owner",
      "ownerId":"engurulabory","issuer":"EXISTING_CANONICAL_ONLY",
      "sourceHead":head,"dependencies":[],"singleWriter":True,"writerCount":1,
      "networkRequested":False,"remotePushRequested":False,"dryRunOnly":True,
      "humanThreshold":"HOLD","officialFinish":"HOLD","checkpointState":"NEW"}


def assess_github():
    head=bridge.head_sha(bridge.ROOT)
    bindings,bsha=bridge.source_read(bridge.ROOT,bridge.BINDING_PATH)
    actions,asha=bridge.source_read(bridge.ROOT,bridge.ACTION_PATH)
    sha={bridge.BINDING_PATH:bsha,bridge.ACTION_PATH:asha}
    def query(cap,action):
        m=mission(cap,action,head)
        return m,bridge.assess(m,bindings,actions,head,sha)
    task,reg=query("TEST_REGRESSION","PACKAGE08_CAP08_TEST_REGRESSION_FIELD_PROOF")
    _,build=query("BUILD","PACKAGE08_CAP07_BUILD_FIELD_PROOF")
    _,cont=query("OPERATOR_CONTINUE_DISPATCH","MAC_NATIVE_RESTART_RECOVERY_CONTINUITY_PROOF")
    def with_override(**changes):
        m={**task,**changes}
        return bridge.assess(m,bindings,actions,head,sha)
    def hold(m,expected):
        return m["decision"]=="HOLD" and expected in m["holds"] and not m["realTaskExecuted"]
    bad_action=with_override(actionId="PACKAGE08_CAP07_BUILD_FIELD_PROOF")
    fake_owner=with_override(ownerId="EVIL")
    fake_finish=with_override(officialFinish="PASS")
    bad_dep=with_override(dependencies=[{"workId":"PREVIOUS","state":"PASS_EVIDENCED","receiptSha256":"1"*64}])
    fake_resume=with_override(checkpointState="RESUME_PROPOSED")
    with_mismatched_head=with_override(sourceHead="0"*40)
    try:
        g=json.loads((HERE/"ZULFIKAR_GOAL_V1_3.json").read_text(encoding="utf-8"))
        goal=goal_gate(g)["assessment"]["score"]==100
    except (OSError,ValueError):
        goal=False
    proc=subprocess.run([sys.executable,"-B","-m","unittest","-q","test_zulfikar_v131_operational_bridge"],
                        cwd=HERE,capture_output=True,text=True,timeout=90)
    checks={
       "B01":goal,
       "B02":all(bridge.SHA256.fullmatch(s) for s in (bsha,asha)),
       "B03":reg["decision"]=="PREFLIGHT_READY_EXISTING_OPERATOR_ONLY",
       "B04":build["decision"]=="PREFLIGHT_READY_EXISTING_OPERATOR_ONLY",
       "B05":cont["decision"]=="PREFLIGHT_READY_EXISTING_OPERATOR_ONLY",
       "B06":hold(bad_action,"HOLD_UNBOUND_OR_MISMATCHED_ACTION") and hold(with_mismatched_head,"HOLD_EXACT_HEAD"),
       "B07":hold(fake_owner,"HOLD_OWNER_ISSUER") and hold(fake_finish,"HOLD_PREMATURE_AUTHORITY"),
       "B08":hold(bad_dep,"HOLD_DEPENDENCY_PROVENANCE_REVIEW_REQUIRED") and hold(fake_resume,"HOLD_RESUME_PROOF_REQUIRED"),
       "B09":reg==bridge.assess(task,bindings,actions,head,sha) and reg["realTaskExecuted"] is False and reg["officialVerifiedFinish"]=="HOLD",
       "B10":proc.returncode==0 and "Ran 27 tests" in proc.stderr and "OK" in proc.stderr,
    }
    output={
      "schema":"enguru.zulfikar.bridge-github-score/v1.3.1",
      "score":sum(10 for v in checks.values() if v is True),
      "fixedDenominator":100,"checks":checks,
      "checkoutHead":head,"sourceRegistryHashes":sha,
      "unittestReturnCode":proc.returncode,
      "technicalMeaning":"GITHUB_READ_ONLY_EXISTING_HANDLER_PREFLIGHT_ONLY",
      "actualTaskExecution":"NOT_RUN","durableRecovery":"HOLD",
      "osiField":"HOLD","realPeerBenchmark":"NOT_RUN",
      "observedUserValue":"NOT_MEASURED","officialVerifiedFinish":"HOLD",
    }
    return output


if __name__=="__main__":
    r=assess_github()
    print(json.dumps(r,sort_keys=True))
    raise SystemExit(0 if r["score"]==100 else 2)
