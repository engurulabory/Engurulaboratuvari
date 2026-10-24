"""Four-round Pilot theoretical acceptance simulation; all field authority remains external."""
from tools.management_v69_pilot_dual_acceptance import assess, THEORY_KEYS, FIELD_KEYS

def simulate():
    cases = [
      ("baseline", {k:True for k in THEORY_KEYS}, {}),
      ("source_drift", {k:(k!="source_sha256") for k in THEORY_KEYS}, {}),
      ("false_field_claim", {k:True for k in THEORY_KEYS}, {k:True for k in FIELD_KEYS}),
      ("missing_ci", {k:(k!="github_ci") for k in THEORY_KEYS}, {}),
    ]
    results=[]
    for title,theory,field in cases:
        r=assess(theory,field)
        expected="THEORY_HOLD" if title in ("source_drift","missing_ci") else "THEORY_CANDIDATE_PASS"
        assert r["theory_state"]==expected,(title,r)
        assert r["field_state"]=="FIELD_HOLD_CANONICAL_RECEIPTS_REQUIRED"
        assert r["verified_finish"]=="HOLD" and r["osi_mutation"]==0
        results.append({"scenario":title,"expected":expected,"result":"PASS"})
    return {"state":"PASS_FOUR_ROUND_MODEL_SIMULATION","rounds":results,
        "theoretical_final":"HOLD_INDEPENDENT_END_TO_END_ACCEPTANCE",
        "official_field":"HOLD","osi_mutation":0}
if __name__=="__main__":
 import json
 print(json.dumps(simulate(),indent=2))
