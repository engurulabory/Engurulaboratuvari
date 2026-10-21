#!/usr/bin/env python3
"""ENGURU governed five-minute controller pilot; read-only execution adapter."""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

def sha(raw): return hashlib.sha256(raw).hexdigest()
def hold(reason, **extra): return dict(state="HOLD_GUVENLI_DUR", reason=reason, **extra)

def management_select(worklist):
    tasks=worklist.get("tasks")
    if not isinstance(tasks, list) or any(not isinstance(t, dict) or not isinstance(t.get("id"),str) for t in tasks):
        return None,"INVALID_WORKLIST"
    if len({t["id"] for t in tasks}) != len(tasks): return None,"DUPLICATE_TASK_IDS"
    complete=set(worklist.get("verified_task_ids", []))
    ready=[]
    for t in tasks:
        deps=t.get("dependencies",[])
        if not isinstance(deps,list): return None,"INVALID_DEPENDENCIES"
        if t.get("state")=="READY" and t["id"] not in complete and set(deps).issubset(complete):
            ready.append(t)
    if not ready: return None,"NO_READY_TASK"
    ready.sort(key=lambda t:(int(t.get("priority",100)),t["id"]))
    return ready[0],None

def safe_path(root,relative):
    if not isinstance(relative,str) or not relative or relative.startswith("/") or ".." in Path(relative).parts or ".git" in Path(relative).parts: return None
    try:
        base=root.resolve(strict=True); target=(base/relative).resolve(strict=True);target.relative_to(base)
        return target if target.is_file() else None
    except (OSError, ValueError): return None

def engineer_observe(task,root):
    if task.get("action")!="verify_file_digest": return hold("EXPLICIT_ACTION_GRANT_REQUIRED")
    path=safe_path(root,task.get("path"))
    if path is None: return hold("SOURCE_SCOPE_HOLD")
    expected=task.get("expected_sha256")
    if not isinstance(expected,str) or len(expected)!=64: return hold("EXPECTED_SHA256_REQUIRED")
    raw=path.read_bytes(); observed=sha(raw)
    if observed!=expected: return hold("SOURCE_SHA256_DIFFERENCE")
    return dict(state="PASS",evidence=dict(path=task["path"],sha256=observed,bytes=len(raw)))

def management_audit(task,observed,root):
    if observed.get("state")!="PASS": return hold("ENGINEER_EVIDENCE_HOLD")
    path=safe_path(root,task.get("path"))
    if path is None: return hold("MANAGEMENT_SOURCE_SCOPE_HOLD")
    again=sha(path.read_bytes())
    if again!=task.get("expected_sha256") or again!=observed.get("evidence",{}).get("sha256"): return hold("MANAGEMENT_RECHECK_HOLD")
    return dict(state="PASS",verification="INDEPENDENT_FUNCTION_SHA256_RECHECK")

def cycle(root,worklist,gate,pilot=False):
    if not pilot:
        if gate.get("state")!="PASS" or not gate.get("donecheck_verified_finish_receipt"): return hold("B1_SIGNED_DONECHECK_FINISH_REQUIRED")
        return hold("CANONICAL_RECEIPT_VERIFIER_BINDING_REQUIRED")
    task,error=management_select(worklist)
    if error: return hold(error)
    engineer=engineer_observe(task,root);management=management_audit(task,engineer,root)
    result=dict(schema="enguru.controller.pilot/v1",task_id=task["id"],state="PASS" if management["state"]=="PASS" else "HOLD_GUVENLI_DUR",engineer=engineer,management=management,human_authority="OWNER_RESERVED",executed_count=1)
    result["sha256"]=sha(json.dumps(result,sort_keys=True,separators=(",",":")).encode())
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",required=True);parser.add_argument("--worklist",required=True);parser.add_argument("--gate",required=True);parser.add_argument("--output",required=True);parser.add_argument("--pilot",action="store_true")
    a=parser.parse_args()
    state=cycle(Path(a.root),json.loads(Path(a.worklist).read_text()),json.loads(Path(a.gate).read_text()),pilot=a.pilot)
    state["observed_at"]=datetime.now(timezone.utc).isoformat()
    outfile=Path(a.output);outfile.parent.mkdir(parents=True,exist_ok=True);outfile.write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n")
    print("STATE="+state["state"])
    raise SystemExit(0 if state["state"]=="PASS" or not a.pilot else 50)
