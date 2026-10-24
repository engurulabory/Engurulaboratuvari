"""Evidence-bound theoretical acceptance: proof tuples for all 70 formal controls."""
import re
from tools.management_v69_formal70 import IDS
HEX=re.compile(r"^[0-9a-f]{64}$")
def assess(records):
    if not isinstance(records,dict):
        return {"state":"HOLD_SCHEMA","accepted":0,"total":len(IDS)}
    passed=[]
    for control in IDS:
        proof=records.get(control)
        if not isinstance(proof,dict):
            continue
        if set(proof)!={"state","source_path","source_sha256","test_run_id","reviewer"}:
            continue
        if proof["state"]!="PASS" or not isinstance(proof["source_path"],str) or not proof["source_path"].strip():
            continue
        if proof["source_path"].startswith("/") or ".." in proof["source_path"].split("/"):
            continue
        if not isinstance(proof["source_sha256"],str) or not HEX.fullmatch(proof["source_sha256"]):
            continue
        if type(proof["test_run_id"]) is not int or proof["test_run_id"]<=0:
            continue
        if not isinstance(proof["reviewer"],str) or not proof["reviewer"].strip():
            continue
        passed.append(control)
    # Evidence tuple structure is required but insufficient: current HEAD and real runs
    # need GitHub API independent verification before final approval.
    return {"state":"HOLD_EXTERNAL_INDEPENDENT_EVIDENCE_RECHECK",
            "accepted_candidate_controls":len(passed),"total":len(IDS),
            "missing_controls":[x for x in IDS if x not in passed],
            "theory_final":"HOLD","field_final":"HOLD","osi_mutation":0}
if __name__=="__main__":
 import json
 print(json.dumps(assess({}),sort_keys=True))
