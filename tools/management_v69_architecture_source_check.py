#!/usr/bin/env python3
"""Architecture acceptance against checked-in contracts, not fabricated hash placeholders."""
import hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
MAIN=ROOT/"governance/management-v69/handoff/THEORETICAL_FINAL_V2.md"
NINE=ROOT/"governance/management-v69/handoff/NINE_CAPABILITY_SEQUENCE_V3.md"
AGENTS=ROOT/"AGENTS.md"
STAGES=[f"T{i:02d}" for i in range(13)]
def evaluate(content, spec, engineer_excerpt):
 if not all(s in content for s in STAGES):return "HOLD_STAGE_COVERAGE"
 if any(content.count(s+" ")!=1 for s in STAGES):return "HOLD_DUPLICATE_STAGE"
 if not all(x in content for x in ("SHA256","rollback","reviewer","owner","HOLD","exact HEAD")):return "HOLD_SAFETY_CONTRACT"
 if not all(x in engineer_excerpt for x in ("canonical_source_commit","required_evidence","rollback_plan","independent_reviewer","target_inventory_pin")):return "HOLD_ENGINEER_CONTRACT"
 if not all(x in spec for x in ("01 | Mimarlık","02 | İş yapma","08 | Mühendislik","09 | İç işleyiş")):return "HOLD_SEQUENCE"
 return "PASS_ARCHITECTURE_CONTRACT_SCOPE"
def run():
 content=MAIN.read_text();spec=NINE.read_text()
 engineer=(ROOT/"governance/management-v69/handoff/ENGINEER_CONTRACT_EXCERPT_V1.txt").read_text()
 assert AGENTS.exists()
 checks=0
 for _ in range(3):
  assert evaluate(content,spec,engineer)=="PASS_ARCHITECTURE_CONTRACT_SCOPE";checks+=1
  for mutated,target in [(content.replace("T06 ","TXX "), "HOLD_STAGE_COVERAGE"),(content+"\nT00 duplicate","HOLD_DUPLICATE_STAGE")]:
   assert evaluate(mutated,spec,engineer)==target;checks+=1
  assert evaluate(content,spec,engineer.replace("independent_reviewer","none"))=="HOLD_ENGINEER_CONTRACT";checks+=1
  assert evaluate(content,spec.replace("09 | İç işleyiş","09 | UNKNOWN"),engineer)=="HOLD_SEQUENCE";checks+=1
 print(json.dumps({"model_rounds":3,"checks":checks,"state":"PASS_CHECKED_IN_ARCHITECTURE_SCOPE","sha256_main":hashlib.sha256(MAIN.read_bytes()).hexdigest(),"sha256_engineer_excerpt":hashlib.sha256(engineer.encode().strip().encode() if False else engineer.encode()).hexdigest(),"external_live_equivalence":"HOLD","osi_mutation":0}))
if __name__=="__main__":run()
