"""EMUS GH-05-C1 contract validator for original 19 task acceptance records."""
import json
import re
from pathlib import Path

REQUIRED=("CONTROL_ID","TASK_ID","SOURCE_REPO","SOURCE_COMMIT","ACCEPTANCE_VERSION",
"REQUIRED_EVIDENCE","INDEPENDENT_VERIFIER","OWNER_AUTHORITY","EXECUTION_STATE",
"EVIDENCE_STATE","AUTHORITY_STATE","NEXT_ACTION")
def validate(record):
    errors=[]
    for field in REQUIRED:
        if field not in record: errors.append("MISSING:"+field)
    if errors:return errors
    if not re.fullmatch(r"GH-(0[1-9]|1[0-9])",str(record["TASK_ID"])):
        errors.append("TASK_ID")
    if record["CONTROL_ID"]!=record["TASK_ID"]:errors.append("CONTROL_BINDING")
    if not re.fullmatch(r"[a-f0-9]{40}",str(record["SOURCE_COMMIT"])):errors.append("SOURCE_COMMIT")
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+",str(record["SOURCE_REPO"])):errors.append("SOURCE_REPO")
    if not isinstance(record["REQUIRED_EVIDENCE"],list) or not record["REQUIRED_EVIDENCE"]:errors.append("EVIDENCE_REQUIREMENT")
    if record["AUTHORITY_STATE"]=="PASS" and (record["OWNER_AUTHORITY"] in ("","UNVERIFIED",None) or record["INDEPENDENT_VERIFIER"] in ("","UNVERIFIED",None)):
        errors.append("UNAUTHORIZED_ACCEPTANCE")
    if record["EVIDENCE_STATE"]=="PASS" and not all(isinstance(x,str) and x for x in record["REQUIRED_EVIDENCE"]):
        errors.append("EVIDENCE_PROVENANCE")
    return errors
def main():
    p=Path(__file__).resolve().parents[1]/"governance/emus/EMUS_V11_TASK_SCHEMA_FIXTURE_V1.json"
    items=json.loads(p.read_text())
    result=[(i+1,validate(item)) for i,item in enumerate(items)]
    ok=len(items)==19 and all(not e for _,e in result)
    print("GH_05_C1_SCHEMA="+("PASS" if ok else "HOLD"))
    print("TASK_COUNT="+str(len(items)))
    return 0 if ok else 2
if __name__=="__main__":raise SystemExit(main())
