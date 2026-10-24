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

def verify_against_sources(records, root, exact_head, independently_verified_runs):
    """Verify candidate control evidence against actual bytes and confirmed run IDs.

    Caller must source exact_head and run IDs from an independent GitHub API
    observation; this code never promotes the result to owner/field approval.
    """
    import hashlib
    from pathlib import Path
    base = Path(root).resolve()
    result = assess(records)
    valid = []
    if not isinstance(exact_head, str) or not re.fullmatch(r"[0-9a-f]{40}", exact_head):
        return {"state":"HOLD_EXACT_HEAD","confirmed_controls":0,"total":len(IDS)}
    for key in IDS:
        p = records.get(key) if isinstance(records, dict) else None
        if not isinstance(p, dict) or key in result["missing_controls"]:
            continue
        src = base / p["source_path"]
        if src.is_symlink() or not src.is_file() or not src.resolve().is_relative_to(base):
            continue
        if hashlib.sha256(src.read_bytes()).hexdigest()!=p["source_sha256"]:
            continue
        if p["test_run_id"] not in independently_verified_runs:
            continue
        run = independently_verified_runs[p["test_run_id"]]
        if run.get("head_sha")!=exact_head or run.get("conclusion")!="success":
            continue
        valid.append(key)
    return {"state":"HOLD_INDEPENDENT_FINAL_REVIEW" if len(valid)==len(IDS) else "HOLD_EVIDENCE_GAPS",
            "confirmed_controls":len(valid),"total":len(IDS),
            "missing_controls":[i for i in IDS if i not in valid],
            "theory_final":"HOLD","field_final":"HOLD","osi_mutation":0}
