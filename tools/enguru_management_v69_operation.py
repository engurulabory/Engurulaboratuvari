#!/usr/bin/env python3
"""Check pinned operational observation without converting it into owner acceptance."""
import json
from pathlib import Path

def evaluate(record, task_ids):
    def hold(reason): return {"state":"HOLD_GUVENLI_DUR","reason":reason}
    if not isinstance(record,dict) or record.get("schema")!="enguru.management-v69.operational-observation/v1":
        return hold("SCHEMA")
    if record.get("task_id") not in task_ids: return hold("TASK_ID_UNBOUND")
    if not isinstance(record.get("source_commit"),str) or len(record["source_commit"])!=40:
        return hold("COMMIT_REQUIRED")
    if not isinstance(record.get("receipt_comment_id"),int) or not isinstance(record.get("producer_run_id"),int):
        return hold("RECEIPT_ID_REQUIRED")
    for field in ("receipt_full_sha256","public_receipt_sha256"):
        val=record.get(field)
        if not isinstance(val,str) or len(val)!=64 or set(val)-set("0123456789abcdef"):
            return hold("INVALID_RECEIPT_DIGEST")
    if record.get("worker_job_conclusion")!="success" or record.get("receipt_state")!="PASS" or record.get("receipt_verification")!="PASS":
        return hold("OBSERVED_EXECUTION_UNPROVEN")
    if record.get("donecheck_state")!="HOLD_EXTERNAL_DONECHECK_V1_2" or record.get("official_finish")!="HOLD_DONECHECK_HUMAN_GATE" or record.get("task_owner_acceptance")!="HOLD":
        return hold("FALSE_FINAL_ACCEPTANCE")
    return {"state":"PASS_RECORDED_OPERATION_PROVENANCE_OFFICIAL_HOLD",
            "task_id":record["task_id"],"worker_job_id":record["worker_job_id"],
            "source_commit":record["source_commit"],"receipt_comment_id":record["receipt_comment_id"],
            "source_refresh":"REQUIRED","live_authentication":"REQUIRED",
            "independent_acceptance":"HOLD","donecheck":"HOLD","human_threshold":"OWNER_RESERVED",
            "official_finish":"HOLD"}
if __name__=="__main__":
    data=json.loads(Path("governance/management-v69/OPERATION_OBSERVATION.json").read_text())
    tasks=json.loads(Path("governance/controller/TASKS.json").read_text())
    result=evaluate(data,{t["id"] for t in tasks["tasks"]})
    print(json.dumps(result,sort_keys=True,indent=2))
    raise SystemExit(0 if result["state"].startswith("PASS_") else 50)
