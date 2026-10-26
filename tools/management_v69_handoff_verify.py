#!/usr/bin/env python3
"""Pure, fail-closed review verifier. No OS actions or writes."""
import json,sys,re
FIELDS={"schema","task_id","source_commit","source_sha256","required_evidence","executor_scope","rollback_plan","reviewer","producer","authority_ref","previous_state","acceptance","target_inventory_sha256"}
SHA=re.compile(r"[0-9a-f]{64}\Z")
HEAD=re.compile(r"[0-9a-f]{40}\Z")
def validate(x):
    if not isinstance(x,dict) or set(x)!=FIELDS:return "HOLD_SCHEMA"
    if x["schema"]!="enguru.management.handoff/v1":return "HOLD_SCHEMA_VERSION"
    if not isinstance(x["task_id"],str) or not x["task_id"].startswith("ENGURU_"):return "HOLD_TASK"
    if not isinstance(x["source_commit"],str) or not HEAD.fullmatch(x["source_commit"]):return "HOLD_SOURCE_COMMIT"
    for k in ("source_sha256","target_inventory_sha256"):
        if not isinstance(x[k],str) or not SHA.fullmatch(x[k]):return "HOLD_HASH"
    if not isinstance(x["required_evidence"],list) or not x["required_evidence"] or any(not isinstance(v,str) or not v.strip() for v in x["required_evidence"]):return "HOLD_EVIDENCE"
    for k in ("executor_scope","rollback_plan","reviewer","producer","authority_ref","previous_state"):
        if not isinstance(x[k],str) or not x[k].strip():return "HOLD_"+k.upper()
    if x["reviewer"]==x["producer"]:return "HOLD_REVIEW_INDEPENDENCE"
    if x["executor_scope"]!="GITHUB_REVIEW_ONLY":return "HOLD_SCOPE"
    if x["acceptance"] not in ("HOLD","REVIEW_CANDIDATE"):return "HOLD_FALSE_ACCEPTANCE"
    return "PASS_REVIEW_SCHEMA_ONLY"

def three_rounds(receipts):
    if not isinstance(receipts,list) or len(receipts)!=3:return "HOLD_ROUND_COUNT"
    if any(not isinstance(r,dict) or set(r)!={"head","run_id","tests","outcome"} for r in receipts):return "HOLD_RECEIPT_SCHEMA"
    heads={r["head"] for r in receipts}; runs={r["run_id"] for r in receipts}
    if len(heads)!=1 or any(not isinstance(h,str) or not HEAD.fullmatch(h) for h in heads):return "HOLD_EXACT_HEAD"
    if len(runs)!=3 or any(not isinstance(v,str) or not v.strip() for v in runs):return "HOLD_RUN_ID"
    if any(r["outcome"]!="PASS" or not isinstance(r["tests"],int) or isinstance(r["tests"],bool) or r["tests"]<1 for r in receipts):return "HOLD_TEST_EVIDENCE"
    return "PASS_THREE_RECEIPT_STRUCTURE_ONLY"

def strict_pairs(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError("duplicate key: "+k)
        d[k]=v
    return d

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("Usage: python management_v69_handoff_verify.py JSON_PATH")
    with open(sys.argv[1],encoding="utf8") as f:
        data=json.load(f,object_pairs_hook=strict_pairs)
    print(validate(data))
