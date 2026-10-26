#!/usr/bin/env python3
"""Target 02 task execution discipline: bounded pure simulation, no OSi changes."""
import json
STATES=("DEFINED","READY","RUNNING","TESTED","EVIDENCED","REVIEWED")
def plan(tasks):
 if not isinstance(tasks,list) or not tasks:return "HOLD_EMPTY"
 ids=[t.get("id") for t in tasks if isinstance(t,dict)]
 if len(ids)!=len(tasks) or any(not isinstance(x,str) or not x for x in ids) or len(set(ids))!=len(ids):return "HOLD_TASK_IDS"
 if any(set(t)!={"id","depends","evidence","owner"} or not isinstance(t["depends"],list) or not isinstance(t["evidence"],str) or not t["evidence"] or not isinstance(t["owner"],str) or not t["owner"] for t in tasks):return "HOLD_SCHEMA"
 done=set()
 for t in tasks:
  if any(d not in done for d in t["depends"]):return "HOLD_DAG_ORDER"
  done.add(t["id"])
 return "PASS_TASK_PLAN_MODEL"
def finish(execution):
 if set(execution)!={"build","tests","evidence","reviewer_independent","rollback","source_pinned"}:return "HOLD_SCHEMA"
 if any(type(v)!=bool for v in execution.values()):return "HOLD_TYPE"
 for k,v in execution.items():
  if not v:return "HOLD_"+k.upper()
 return "PASS_EXECUTION_MODEL_ONLY"
def simulate():
 tasks=[dict(id="GOAL",depends=[],evidence="scope",owner="manager"),dict(id="BUILD",depends=["GOAL"],evidence="build_receipt",owner="engineer"),dict(id="TEST",depends=["BUILD"],evidence="ci_receipt",owner="engineer")]
 okay=dict(build=True,tests=True,evidence=True,reviewer_independent=True,rollback=True,source_pinned=True)
 cases=0
 for _ in range(3):
  assert plan(tasks)=="PASS_TASK_PLAN_MODEL";cases+=1
  assert plan(tasks[::-1])=="HOLD_DAG_ORDER";cases+=1
  assert plan(tasks+[tasks[0]])=="HOLD_TASK_IDS";cases+=1
  assert finish(okay)=="PASS_EXECUTION_MODEL_ONLY";cases+=1
  for k in okay:
   assert finish(dict(okay,**{k:False}))=="HOLD_"+k.upper();cases+=1
 print(json.dumps({"target":"02_IS_YAPMA_YETENEGI","rounds":3,"checks":cases,"state":"PASS_THEORETICAL_EXECUTION_MODEL","real_task_execution":"HOLD","osi_mutation":0}))
if __name__=="__main__":simulate()
