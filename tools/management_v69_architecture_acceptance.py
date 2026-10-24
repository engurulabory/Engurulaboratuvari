#!/usr/bin/env python3
"""Architecture graph acceptance; pure, deterministic, no OSi access."""
import json
NODES=tuple(f"T{i:02d}" for i in range(13))
ROLES={"MANAGEMENT","ENGINEER","REVIEWER","OWNER"}
EDGES=tuple((NODES[i],NODES[i+1]) for i in range(12))
def check(p):
 if not isinstance(p,dict) or set(p)!={"nodes","edges","roles","source","inventory","final"}:return "HOLD_SCHEMA"
 if p["nodes"]!=list(NODES):return "HOLD_NODES"
 if len(p["edges"])!=12 or p["edges"]!=[list(e) for e in EDGES]:return "HOLD_DEPENDENCIES"
 if set(p["roles"])!=ROLES or p["roles"]["MANAGEMENT"]==p["roles"]["ENGINEER"] or p["roles"]["REVIEWER"]==p["roles"]["ENGINEER"]:return "HOLD_ROLES"
 if any(not isinstance(p[k],str) or len(p[k])!=64 or any(c not in "0123456789abcdef" for c in p[k]) for k in ("source","inventory")):return "HOLD_PINS"
 if p["final"]!="HOLD_FIELD_AUTHORITY":return "HOLD_FALSE_FINISH"
 return "PASS_ARCHITECTURE_MODEL_ONLY"
def run():
 p=dict(nodes=list(NODES),edges=[list(e) for e in EDGES],roles=dict(MANAGEMENT="manager",ENGINEER="builder",REVIEWER="independent",OWNER="owner"),source="a"*64,inventory="b"*64,final="HOLD_FIELD_AUTHORITY")
 cases=[("good",p,"PASS_ARCHITECTURE_MODEL_ONLY"),("missing_node",dict(p,nodes=list(NODES[:-1])),"HOLD_NODES"),("reverse_edge",dict(p,edges=[list(e) for e in EDGES[::-1]]),"HOLD_DEPENDENCIES"),("self_review",dict(p,roles=dict(p["roles"],REVIEWER="builder")),"HOLD_ROLES"),("unknown_inventory",dict(p,inventory=""),"HOLD_PINS"),("premature_finish",dict(p,final="VERIFIED_FINISH"),"HOLD_FALSE_FINISH"),("missing_schema",dict((k,v) for k,v in p.items() if k!="source"),"HOLD_SCHEMA")]
 count=0
 for _ in range(3):
  for name,case,expected in cases:
   result=check(case)
   assert result==expected,(name,result)
   count+=1
 print(json.dumps({"architecture":"PASS_3_ROUNDS","checks":count,"osi_mutation":0,"scope":"MODEL_ONLY"}))
if __name__=="__main__":run()
