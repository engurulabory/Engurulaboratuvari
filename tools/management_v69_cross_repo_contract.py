#!/usr/bin/env python3
"""Management to engineering review-only cross-repository contract checks."""
import json,re
SHA40=re.compile("[0-9a-f]{40}$");SHA64=re.compile("[0-9a-f]{64}$")
KEYS={"task_id","management_head","engineer_head","source_sha256","inventory_sha256","evidence_ids","producer","reviewer","scope","rollback","authority_state"}
def verify(x):
 if not isinstance(x,dict) or set(x)!=KEYS:return "HOLD_SCHEMA"
 if any(not isinstance(x[k],str) or not SHA40.fullmatch(x[k]) for k in ("management_head","engineer_head")):return "HOLD_HEAD"
 if any(not isinstance(x[k],str) or not SHA64.fullmatch(x[k]) for k in ("source_sha256","inventory_sha256")):return "HOLD_SHA"
 if not isinstance(x["task_id"],str) or not x["task_id"].startswith("ENGURU_"):return "HOLD_TASK"
 if not isinstance(x["evidence_ids"],list) or len(x["evidence_ids"])!=len(set(x["evidence_ids"])) or not x["evidence_ids"]:return "HOLD_EVIDENCE"
 if not all(isinstance(v,str) and v for v in x["evidence_ids"]):return "HOLD_EVIDENCE"
 if x["producer"]==x["reviewer"] or not x["producer"] or not x["reviewer"]:return "HOLD_REVIEWER"
 if x["scope"]!="GITHUB_REVIEW_ONLY" or x["authority_state"]!="HOLD":return "HOLD_AUTHORITY"
 if not isinstance(x["rollback"],str) or not x["rollback"].strip():return "HOLD_ROLLBACK"
 return "PASS_HANDOFF_SCHEMA_ONLY"
def simulate():
 x=dict(task_id="ENGURU_MANAGEMENT_V69_PR_203",management_head="a"*40,engineer_head="b"*40,source_sha256="c"*64,inventory_sha256="d"*64,evidence_ids=["E1"],producer="maker",reviewer="other",scope="GITHUB_REVIEW_ONLY",rollback="restore prior",authority_state="HOLD")
 count=0
 for _ in range(3):
  assert verify(x)=="PASS_HANDOFF_SCHEMA_ONLY";count+=1
  for k,v,expected in [("reviewer","maker","HOLD_REVIEWER"),("management_head","bad","HOLD_HEAD"),("inventory_sha256","bad","HOLD_SHA"),("evidence_ids",["E1","E1"],"HOLD_EVIDENCE"),("scope","OSI_INSTALL","HOLD_AUTHORITY"),("rollback","","HOLD_ROLLBACK")]:
   y=dict(x,**{k:v});assert verify(y)==expected;count+=1
 print(json.dumps({"checks":count,"rounds":3,"state":"PASS_CROSS_REPO_SCHEMA_SIM","live_runtime_binding":"HOLD","osi_mutation":0}))
if __name__=="__main__":simulate()
