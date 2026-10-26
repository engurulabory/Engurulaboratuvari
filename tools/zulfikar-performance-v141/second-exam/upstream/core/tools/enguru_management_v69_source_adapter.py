#!/usr/bin/env python3
"""Read-only adapter: real controller worklist -> V6.9 management inventory.
The controller's operational authority remains entirely separate.
"""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_REPO = "engurulabory/Engurulaboratuvari"
def sha256(data): return hashlib.sha256(data).hexdigest()

def reconcile(tasks_bytes, gate_bytes, source_ref, source_commit):
    try:
        work = json.loads(tasks_bytes)
        gate = json.loads(gate_bytes)
    except (ValueError, UnicodeError):
        return {"state":"HOLD_GUVENLI_DUR","reason":"SOURCE_JSON_INVALID"}
    if not isinstance(source_ref,str) or not source_ref or not isinstance(source_commit,str) or len(source_commit)!=40 or any(c not in "0123456789abcdef" for c in source_commit):
        return {"state":"HOLD_GUVENLI_DUR","reason":"COMMIT_PIN_REQUIRED"}
    if not isinstance(work,dict) or not isinstance(work.get("tasks"),list) or not isinstance(gate,dict) or gate.get("repository")!=EXPECTED_REPO:
        return {"state":"HOLD_GUVENLI_DUR","reason":"CONTROLLER_CONTRACT_MISMATCH"}
    required={"id","state","action","target_repo","path"}
    tasks,seen=[],set()
    for t in work["tasks"]:
        if not isinstance(t,dict) or not required.issubset(t) or not isinstance(t["id"],str) or not t["id"] or t["id"] in seen or t["target_repo"]!=EXPECTED_REPO:
            return {"state":"HOLD_GUVENLI_DUR","reason":"TASK_AUTHORITY_INVALID"}
        seen.add(t["id"])
        tasks.append({"task_id":t["id"],"source_state":t["state"],"action":t["action"],"source_path":t["path"],
                      "dependencies":t.get("dependencies",[]),"source_commit":source_commit,
                      "evidence":"REQUIRES_INDEPENDENT_TASK_RECEIPT","verifier":"NOT_CONFIRMED","authority":"OWNER_RESERVED",
                      "management_state":"OBSERVED_ONLY"})
    if any(not isinstance(x["dependencies"],list) or any(d not in seen for d in x["dependencies"]) for x in tasks):
        return {"state":"HOLD_GUVENLI_DUR","reason":"DEPENDENCY_CONTRACT_INVALID"}
    return {"state":"PASS_SOURCE_BOUND_MANAGEMENT_INVENTORY","task_count":len(tasks),
            "tasks":tasks,"source_ref":source_ref,"source_commit":source_commit,
            "tasks_sha256":sha256(tasks_bytes),"gate_sha256":sha256(gate_bytes),
            "independently_accepted":0,"operational_acceptance":"HOLD_INDEPENDENT_OPERATION_ACCEPTANCE",
            "controller_activation_observed":gate.get("state"),"github_writes":0,
            "human_threshold":"OWNER_RESERVED"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--tasks",required=True)
    parser.add_argument("--gate",required=True)
    parser.add_argument("--source-ref",required=True)
    parser.add_argument("--source-commit",required=True)
    args=parser.parse_args()
    try:
        t,g=Path(args.tasks),Path(args.gate)
        if t.is_symlink() or g.is_symlink(): raise OSError("SYMLINK")
        result=reconcile(t.read_bytes(),g.read_bytes(),args.source_ref,args.source_commit)
    except OSError:
        result={"state":"HOLD_GUVENLI_DUR","reason":"SOURCE_UNREADABLE"}
    print(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False))
    return 0 if result["state"]=="PASS_SOURCE_BOUND_MANAGEMENT_INVENTORY" else 50

if __name__=="__main__": raise SystemExit(main())
