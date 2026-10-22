#!/usr/bin/env python3
"""Management V6.9: verify a pinned GitHub task/CI evidence crosswalk.
The ledger is a candidate only. No authority can be inferred from its text.
"""
import argparse
import hashlib
import json
from pathlib import Path

TASKS="governance/controller/TASKS.json"
ACTIVATION="governance/controller/ACTIVATION.json"
HEX=set("0123456789abcdef")

def validate(ledger, tasks, activation, actual_digests):
    def hold(reason): return {"state":"HOLD_GUVENLI_DUR","reason":reason}
    if not isinstance(ledger,dict) or ledger.get("schema")!="enguru.management-v69.evidence-crosswalk/v1":
        return hold("LEDGER_SCHEMA")
    if ledger.get("source_sha256")!=actual_digests: return hold("SOURCE_DRIFT")
    if not isinstance(activation,dict) or activation.get("human_final_authority")!="OWNER": return hold("AUTHORITY_BOUNDARY")
    source_tasks=tasks.get("tasks") if isinstance(tasks,dict) else None
    records=ledger.get("records")
    if not isinstance(source_tasks,list) or not isinstance(records,list): return hold("RECORD_SHAPE")
    ids=[t.get("id") for t in source_tasks if isinstance(t,dict)]
    if len(ids)!=len(source_tasks) or len(ids)!=len(set(ids)):return hold("SOURCE_TASK_IDS")
    keyed={r.get("task_id"):r for r in records if isinstance(r,dict)}
    if len(keyed)!=len(records) or set(keyed)!=set(ids): return hold("TASK_ID_COVERAGE")
    ci=ledger.get("management_ci")
    if not isinstance(ci,dict) or ci.get("conclusion")!="success" or ci.get("workflow")!="ENGURU Management V6.9 Review":
        return hold("CI_PROOF")
    if not isinstance(ci.get("run_id"),int) or ci["run_id"]<=0:return hold("CI_RUN_ID")
    if not isinstance(ci.get("head_sha"),str) or len(ci["head_sha"])!=40 or set(ci["head_sha"])-HEX:return hold("CI_SOURCE_HEAD")
    for task in source_tasks:
        record=keyed[task["id"]]
        if record.get("observed_controller_state")!=task.get("state"):
            return hold("TASK_STATE_MISMATCH")
        if record.get("evidence_level")!="B_CI_SOURCE_READ" or record.get("task_execution_proven") is not False or record.get("independent_verifier")!="HOLD" or record.get("authority_acceptance")!="HOLD":
            return hold("FALSE_ACCEPTANCE_CLAIM")
    return {"state":"PASS_CROSSWALK_STRUCTURE_OFFICIAL_HOLD",
            "task_count":len(ids),"task_ids":sorted(ids),"ci_read_verified":True,
            "task_execution_accepted":0,"independent_verifier_accepted":0,
            "authority_accepted":0,"official_finish":"HOLD",
            "next_action":"INDEPENDENT_PER_TASK_EXECUTION_EVIDENCE_AND_OWNER_DECISION"}

def run(root,ledger_file):
    paths=[TASKS,ACTIVATION]
    raw=[]
    for name in paths:
        p=root/name
        if p.is_symlink() or not p.is_file():raise ValueError("SOURCE_MISSING_OR_SYMLINK")
        raw.append(p.read_bytes())
    return validate(json.loads(ledger_file.read_text(encoding="utf-8")),
                    json.loads(raw[0]),json.loads(raw[1]),
                    dict(zip(paths,[hashlib.sha256(b).hexdigest() for b in raw])))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=".")
    p.add_argument("--ledger",default="governance/management-v69/EVIDENCE_CROSSWALK.json")
    args=p.parse_args()
    try: result=run(Path(args.root),Path(args.ledger))
    except (OSError,ValueError,UnicodeError) as e:
        result={"state":"HOLD_GUVENLI_DUR","reason":"SOURCE_UNAVAILABLE_OR_INVALID","detail":str(e)}
    print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
    return 50 if result["state"]=="HOLD_GUVENLI_DUR" else 0
if __name__=="__main__":raise SystemExit(main())
