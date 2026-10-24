#!/usr/bin/env python3
"""Pinned source architecture acceptance: 4 closure gates, 3 rounds, review-only."""
import hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
DIR=ROOT/"governance/management-v69/handoff"
EXPECTED_ENGINEER_GIT_BLOB="f5621c13916c497a081a63e8bdb84816311deb9a"
REQUIRED=("task_id","canonical_source_commit","canonical_source_sha256","required_evidence","executor_scope","rollback_plan","producer","independent_reviewer","owner_grant_ref","accepted_control_ids","open_control_ids","target_inventory_pin","exact_head","acceptance_state")
def gitblob(content):
 return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()
def verify(design, sequence, engineer):
 defs=[re.match(r"^(T\d\d) ",line) for line in design.splitlines()]
 defs=[m.group(1) for m in defs if m]
 if defs!=[f"T{i:02d}" for i in range(13)]:return "HOLD_STAGE_GRAPH"
 if any(f"| {i:02d} |" not in sequence for i in range(1,10)):return "HOLD_NINE_TARGETS"
 if any(field not in engineer.decode("utf-8") for field in REQUIRED):return "HOLD_ENGINEER_FIELDS"
 if gitblob(engineer)!=EXPECTED_ENGINEER_GIT_BLOB:return "HOLD_ENGINEER_SOURCE_DRIFT"
 if not all(s in design for s in ("Human Threshold","DoneCheck","rollback","T12","T00")):return "HOLD_AUTHORITY_BOUNDARY"
 return "PASS_PINNED_ARCHITECTURE_CONTRACT"
def main():
 design=(DIR/"THEORETICAL_FINAL_V2.md").read_text()
 sequence=(DIR/"NINE_CAPABILITY_SEQUENCE_V3.md").read_text()
 engineer=(DIR/"ENGINEER_CONTRACT_PINNED_SOURCE_V1.md").read_bytes()
 good=verify(design,sequence,engineer)
 assert good=="PASS_PINNED_ARCHITECTURE_CONTRACT",(good,gitblob(engineer))
 count=0
 for _ in range(3):
  tests=[(design,sequence,engineer,"PASS_PINNED_ARCHITECTURE_CONTRACT"),
   (design.replace("T06 ","TXX ",1),sequence,engineer,"HOLD_STAGE_GRAPH"),
   (design,sequence.replace("| 09 |","| XX |"),engineer,"HOLD_NINE_TARGETS"),
   (design,sequence,engineer.replace(b"rollback_plan",b"rollback_none"),"HOLD_ENGINEER_FIELDS"),
   (design,sequence,engineer+b"\n", "HOLD_ENGINEER_SOURCE_DRIFT"),
   (design.replace("Human Threshold","Human X"),sequence,engineer,"HOLD_AUTHORITY_BOUNDARY")]
  for d,s,e,expected in tests:
   result=verify(d,s,e)
   assert result==expected,(result,expected)
   count+=1
 print(json.dumps({"state":"PASS_PINNED_ARCHITECTURE_REVIEW","rounds":3,"checks":count,"engineer_git_blob":gitblob(engineer),"architecture_theoretical_scope":"PINNED_CONTRACTS_ONLY","independent_cross_repo_live_check":"HOLD","three_independent_ci":"HOLD","field":"HOLD","osi_mutation":0}))
if __name__=="__main__":main()
