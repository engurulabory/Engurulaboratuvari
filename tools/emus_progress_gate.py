"""EMUS review-only counter and evidence mapping gate."""
import json
import re
from pathlib import Path

STATES = {"HOLD_UNVERIFIED", "CI_EVIDENCED", "FIELD_EVIDENCED"}
def inspect(data):
    errors=[]; ids=[]; counts={s:0 for s in STATES}; mapped=[]
    rows=data.get("rows",[])
    if [r.get("id") for r in rows] != list(range(1,20)): errors.append("TASK_SET")
    for row in rows:
        for c in row.get("criteria",[]):
            cid=c.get("id",""); state=c.get("state","")
            ids.append(cid)
            if cid not in {f"GH-{row.get('id',0):02d}-C{i}" for i in range(1,5)}: errors.append("ID:"+cid)
            if state not in STATES: errors.append("STATE:"+cid); continue
            counts[state]+=1
            if state=="CI_EVIDENCED":
                run=str(c.get("evidence_run") or "")
                if not re.fullmatch(r"[1-9][0-9]+",run): errors.append("CI_RUN:"+cid)
                mapped.append({"criterion":cid,"kind":"CI","run":run})
            elif state=="FIELD_EVIDENCED":
                sha=str(c.get("evidence_sha256") or "")
                name=str(c.get("evidence_file") or "")
                if not re.fullmatch(r"[a-f0-9]{64}",sha) or not name.endswith(".json") or "/" in name:
                    errors.append("FIELD_PROVENANCE:"+cid)
                mapped.append({"criterion":cid,"kind":"FIELD","sha256":sha,"file":name})
    expected=[f"GH-{i:02d}-C{j}" for i in range(1,20) for j in range(1,5)]
    if ids!=expected: errors.append("DUPLICATE_OR_MISSING_CRITERION")
    rule=data.get("counting_rules",{})
    want={"denominator":76,"ci_evidenced_count":counts["CI_EVIDENCED"],
          "field_evidenced_count":counts["FIELD_EVIDENCED"],
          "evidenced_total":counts["CI_EVIDENCED"]+counts["FIELD_EVIDENCED"],
          "official_accepted_tasks":0}
    for key,value in want.items():
        if rule.get(key)!=value: errors.append("COUNTER:"+key)
    if data.get("status")!="REVIEW_DRAFT_NOT_CANONICAL":errors.append("AUTHORITY_STATUS")
    return {"state":"PASS_REVIEW_MAPPING_ONLY" if not errors else "HOLD",
            "errors":sorted(set(errors)),"counts":want,
            "evidence_map":mapped,"CI_RUN_STATUS":"EXTERNAL_VERIFICATION_REQUIRED",
            "LIVE_ROUTER":"HOLD","HUMAN_AUTHORITY":"HOLD","VERIFIED_FINISH":"HOLD"}
def main():
    path=Path(__file__).resolve().parents[1]/"governance/emus/EMUS_V11_SUBCRITERION_PROGRESS_V1.json"
    r=inspect(json.loads(path.read_text(encoding="utf-8")))
    print(json.dumps({k:v for k,v in r.items() if k!="evidence_map"},sort_keys=True,indent=2))
    print("MAPPED_CRITERIA="+str(len(r["evidence_map"])))
    return 0 if r["state"].startswith("PASS") else 2
if __name__=="__main__":
    raise SystemExit(main())
