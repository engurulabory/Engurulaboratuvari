#!/usr/bin/env python3
"""Source-bound read-only view of existing GitHub controller records.
Input files are already checked-out canonical snapshots; never writes or
treats controller READY, credentials or claims as management authorization.
"""
import argparse
import hashlib
import json
from pathlib import Path

REPO = "engurulabory/Engurulaboratuvari"

def sha(b): return hashlib.sha256(b).hexdigest()

def read(root, relative):
    p = root
    for part in Path(relative).parts:
        if part in (".", "..", ""): raise ValueError("UNSAFE_SOURCE_PATH")
        p = p / part
        if p.is_symlink(): raise ValueError("SYMLINK_SOURCE")
    if not p.is_file(): raise ValueError("SOURCE_MISSING")
    return p.read_bytes()

def reconcile(tasks, activation, source_commit, digests):
    if not isinstance(source_commit,str) or len(source_commit)!=40 or set(source_commit)-set("0123456789abcdef"):
        return {"state":"HOLD_GUVENLI_DUR","reason":"SOURCE_COMMIT_REQUIRED"}
    if not isinstance(activation,dict) or activation.get("repository")!=REPO or activation.get("human_final_authority")!="OWNER":
        return {"state":"HOLD_GUVENLI_DUR","reason":"AUTHORITY_BOUNDARY"}
    ts=tasks.get("tasks") if isinstance(tasks,dict) else None
    if not isinstance(ts,list): return {"state":"HOLD_GUVENLI_DUR","reason":"TASK_SCHEMA"}
    ids=set()
    rows=[]
    for t in ts:
        if not isinstance(t,dict) or not isinstance(t.get("id"),str) or not t["id"] or t["id"] in ids:
            return {"state":"HOLD_GUVENLI_DUR","reason":"TASK_ID"}
        ids.add(t["id"])
        if t.get("target_repo")!=REPO or not isinstance(t.get("dependencies"),list):
            return {"state":"HOLD_GUVENLI_DUR","reason":"SCOPE_OR_DEPENDENCY"}
        rows.append({"task_id":t["id"],"observed_controller_state":t.get("state"),"management_state":"PAUSED" if str(t.get("state","")).startswith("PAUSED") else "HOLD_EXTERNAL_VERIFICATION","control_id":t["id"],"dependencies":t["dependencies"],"authority":"OWNER_RESERVED","evidence":"NOT_INDEPENDENTLY_VERIFIED"})
    if any(not isinstance(d,str) or d not in ids for row in rows for d in row["dependencies"]):
        return {"state":"HOLD_GUVENLI_DUR","reason":"DEPENDENCY_MISSING"}
    return {"state":"MANAGEMENT_SNAPSHOT_READ_ONLY","source_commit":source_commit,"source_sha256":digests,"task_count":len(rows),"tasks":rows,"verified_acceptance":0,"ready_for_execution":[],"github_writes":0,"next_action":"INDEPENDENT_RECEIPT_AND_SOURCE_AUTHORITY_RECONCILIATION"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=".")
    p.add_argument("--source-commit",required=True)
    p.add_argument("--output")
    args=p.parse_args()
    try:
        root=Path(args.root)
        files=("governance/controller/TASKS.json","governance/controller/ACTIVATION.json")
        raw=[read(root,x) for x in files]
        obj=[json.loads(x) for x in raw]
        result=reconcile(*obj,args.source_commit,dict(zip(files,map(sha,raw))))
    except (OSError,ValueError,UnicodeError) as err:
        result={"state":"HOLD_GUVENLI_DUR","reason":"SOURCE_READ_OR_PARSE","detail":str(err)}
    payload=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.output:
        out=Path(args.output)
        if out.is_symlink() or out.exists(): raise SystemExit("HOLD_OUTPUT_EXISTS")
        out.write_text(payload,encoding="utf-8")
    print(payload,end="")
    return 50 if result["state"]=="HOLD_GUVENLI_DUR" else 0

if __name__=="__main__": raise SystemExit(main())
