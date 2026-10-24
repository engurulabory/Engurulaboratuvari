#!/usr/bin/env python3
"""GitHub MK V4 advisory worker: allowlisted suggestions and review-only next-step plans."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from tools import enguru_mk_bridge_github_v1 as prior

SCHEMA="enguru.mk.peer-advisory/v1"
MAP={
 "PILOT_HELLO":("SUCCESS","PILOT_RECEIPT","VERIFY_COUNTERPART_ACK","INSPECT_LOCAL_LEDGER"),
 "GITHUB_RECEIVED":("SUCCESS","REMOTE_RECEIPT","RECONCILE_DELIVERY","INSPECT_LOCAL_LEDGER"),
 "PILOT_RECOVERY":("WARNING","RECOVERY_REQUIRED","RECHECK_CURSOR_AND_SHA","INSPECT_LOCAL_LEDGER"),
 "RUNTIME_DRIFT":("MISMATCH","RUNTIME_DIFFERENCE","VERIFY_PYTHON_NODE_TAP","REVIEW_RUNTIME_COMPATIBILITY"),
 "PACKAGE_ABSENT":("MISSING","PACKAGE_REQUIRED","LOCATE_SHA_PINNED_PACKAGE","REVIEW_MISSING_PACKAGE"),
 "INTERACTIVE_TIMEOUT":("ERROR","OWNER_STEP_TIMED_OUT","REVIEW_INTERACTIVE_TIMEOUT","REVIEW_OWNER_TIME_POLICY"),
 "NODE_TAP_MISMATCH":("ERROR","TAP_FORMAT_DIFFERENCE","ADD_NODE_TAP_REGRESSION","PREPARE_TEST_REVIEW"),
}
PLAN_KEYS={"schema","advisoryId","sourceEvent","alignedNextStep","adoptedState","executedProductWrites","officialAcceptance"}
ADVICE_KEYS={"schema","advisoryId","eventId","taskId","blockId","producer","recipient","category","findingCode","suggestionCode","nextStepCode","evidenceEventSha256","visibility","authority","executionPolicy"}
REVIEW_ONLY={"REVIEW_RUNTIME_COMPATIBILITY","REVIEW_MISSING_PACKAGE","REVIEW_OWNER_TIME_POLICY","PREPARE_TEST_REVIEW","INSPECT_LOCAL_LEDGER"}

def event_validate(ev,producer):
    if producer=="MAC_OSI_MK":
        return prior.event(ev)
    if not isinstance(ev,dict) or set(ev)!=prior.EVENT_KEYS:
        raise prior.Hold("GH_EVENT_KEYS")
    if ev["producer"]!="GITHUB_MK" or ev["code"]!="GITHUB_RECEIVED":
        raise prior.Hold("GH_EVENT_SCOPE")
    mock=dict(ev)
    mock["producer"]="MAC_OSI_MK"
    mock["eventId"]="MAC-"+f'{ev["sequence"]:08d}'
    mock["code"]="PILOT_HELLO"
    prior.event(mock)
    if ev["eventId"]!="GH-"+f'{ev["sequence"]:08d}':raise prior.Hold("GH_EVENT_ID")
    return prior.digest(ev)

def advice_for(ev):
    event_validate(ev,ev["producer"])
    category,finding,suggestion,step=MAP[ev["code"]]
    return {"schema":SCHEMA,"advisoryId":"ADV-"+ev["eventId"],"eventId":ev["eventId"],
     "taskId":prior.TASK,"blockId":ev["blockId"],"producer":ev["producer"],
     "recipient":"GITHUB_MK" if ev["producer"]=="MAC_OSI_MK" else "MAC_OSI_MK",
     "category":category,"findingCode":finding,"suggestionCode":suggestion,
     "nextStepCode":step,"evidenceEventSha256":prior.digest(ev),
     "visibility":"PUBLIC_SANITIZED","authority":"SUGGESTION_ONLY",
     "executionPolicy":"READONLY_OR_REVIEW"}

def process(worktree,owner,actor):
    if not owner or owner!=actor or actor.lower().endswith("[bot]"):
        raise prior.Hold("HOLD_ACTOR")
    root=Path(worktree)/prior.ROOT
    dirs={key:root/key for key in ("streams/mac","streams/github","advice/mac","advice/github","plans/github")}
    for p in dirs.values():
        if p.is_symlink():raise prior.Hold("HOLD_DIR_SYMLINK")
        p.mkdir(parents=True,exist_ok=True)
    entries=sorted(dirs["streams/mac"].iterdir())
    if len(entries)>100:raise prior.Hold("HOLD_CAPACITY")
    reviewed=0;added=0
    for idx,p in enumerate(entries,1):
        if p.name!=f"MAC-{idx:08d}.json":raise prior.Hold("HOLD_SEQUENCE")
        ev=prior.read(p);event_validate(ev,"MAC_OSI_MK")
        incoming=dirs["advice/mac"]/p.name
        if not incoming.exists():continue
        if incoming.is_symlink():raise prior.Hold("HOLD_ADVICE_SYMLINK")
        got=prior.read(incoming)
        expected=advice_for(ev)
        if set(got)!=ADVICE_KEYS or got!=expected:
            raise prior.Hold("HOLD_ADVICE_BINDING")
        reviewed+=1
        step=got["nextStepCode"]
        plan={"schema":"enguru.mk.peer-plan/v1","advisoryId":got["advisoryId"],
              "sourceEvent":ev["eventId"],"alignedNextStep":step,
              "adoptedState":"READONLY_REVIEW_PLANNED" if step in REVIEW_ONLY else "REVIEW_REQUIRED",
              "executedProductWrites":0,"officialAcceptance":"HOLD"}
        if set(plan)!=PLAN_KEYS:raise prior.Hold("HOLD_PLAN_SCHEMA")
        added+=prior.write_once(dirs["plans/github"]/p.name,prior.canon(plan))
        reply_path=dirs["streams/github"]/f"GH-{idx:08d}.json"
        if not reply_path.is_file():raise prior.Hold("HOLD_REPLY_MISSING")
        reply=prior.read(reply_path)
        if reply!=dict(ev,eventId=f"GH-{idx:08d}",producer="GITHUB_MK",code="GITHUB_RECEIVED"):
            raise prior.Hold("HOLD_REPLY_DRIFT")
        added+=prior.write_once(dirs["advice/github"]/reply_path.name,prior.canon(advice_for(reply)))
    return {"state":"PASS_PEER_ADVISORY_REVIEW_ONLY","received":reviewed,
            "added":added,"productWrites":0,"officialAcceptance":"HOLD"}

def self_test():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td)/prior.ROOT
        for p in ("streams/mac","streams/github","advice/mac"):
            (base/p).mkdir(parents=True,exist_ok=True)
        ev={"schema":"enguru.mk.bridge-event/v1","eventId":"MAC-00000001",
            "taskId":prior.TASK,"blockId":"OSIBLOCK-20261024-PILOT",
            "producer":"MAC_OSI_MK","sequence":1,"type":"SUCCESS","code":"PILOT_HELLO",
            "sourceCommit":"a"*40,"evidenceSha256":"a"*64,
            "observedAt":"2026-10-24T14:00:00Z","visibility":"PUBLIC_SANITIZED"}
        prior.write_once(base/"streams/mac/MAC-00000001.json",prior.canon(ev))
        reply=dict(ev,eventId="GH-00000001",producer="GITHUB_MK",code="GITHUB_RECEIVED")
        prior.write_once(base/"streams/github/GH-00000001.json",prior.canon(reply))
        adv=advice_for(ev)
        prior.write_once(base/"advice/mac/MAC-00000001.json",prior.canon(adv))
        assert process(td,"owner","owner")["received"]==1
        assert process(td,"owner","owner")["added"]==0
        assert json.loads((base/"plans/github/MAC-00000001.json").read_text())["alignedNextStep"]=="INSPECT_LOCAL_LEDGER"
        note=json.loads((base/"advice/github/GH-00000001.json").read_text())
        assert note["authority"]=="SUGGESTION_ONLY" and note["nextStepCode"]=="INSPECT_LOCAL_LEDGER"
        (base/"advice/mac/MAC-00000001.json").write_bytes(prior.canon(dict(adv,authority="EXECUTE")))
        try:process(td,"owner","owner");raise AssertionError("tamper was accepted")
        except prior.Hold:pass
        try:process(td,"owner","intruder");raise AssertionError("actor was accepted")
        except prior.Hold:pass
    print("GH_ADVISORY_SELF_TEST=PASS")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    try:
        if args.self_test:self_test()
        else:print(json.dumps(process(".",os.getenv("ENGURU_MK_OWNER",""),os.getenv("ENGURU_MK_ACTOR","")),sort_keys=True))
    except prior.Hold as exc:
        print("STATE=HOLD_GH_ADVISORY; REASON="+str(exc))
        raise SystemExit(50)
