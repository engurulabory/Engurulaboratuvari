#!/usr/bin/env python3
"""Review-only adversarial state-machine simulation; no OSi access."""
import json
STAGES=tuple("T%02d"%i for i in range(13))
REQUIRED=("source","inventory","dependency","build","artifact","rollback","three_ci","reviewer","owner","field","donecheck")
def assess(evidence):
    if set(evidence)!=set(REQUIRED):return "HOLD_SCHEMA"
    if any(type(v) is not bool for v in evidence.values()):return "HOLD_TYPE"
    if not evidence["source"]:return "HOLD_SOURCE"
    if not evidence["inventory"]:return "HOLD_INVENTORY"
    if not evidence["dependency"]:return "HOLD_DEPENDENCY"
    if not evidence["build"]:return "HOLD_BUILD"
    if not evidence["artifact"]:return "HOLD_ARTIFACT"
    if not evidence["rollback"]:return "HOLD_ROLLBACK"
    if not evidence["three_ci"]:return "HOLD_THREE_CI"
    if not evidence["reviewer"]:return "HOLD_REVIEWER"
    if not evidence["owner"]:return "HOLD_OWNER"
    if not evidence["field"]:return "HOLD_FIELD"
    if not evidence["donecheck"]:return "HOLD_DONECHECK"
    return "PASS_MODEL_ONLY"
def run():
    full={k:True for k in REQUIRED}
    cases=[("all_hypothetical",full,"PASS_MODEL_ONLY")]
    cases += [(k,dict(full,**{k:False}),"HOLD_"+k.upper()) for k in REQUIRED]
    cases += [("missing",dict((k,True) for k in REQUIRED[:-1]),"HOLD_SCHEMA"),
              ("non_boolean",dict(full,source=1),"HOLD_TYPE"),
              ("extra",dict(full,unexpected=True),"HOLD_SCHEMA")]
    checks=0
    for round_id in range(3):
        for label,e,expected in cases:
            got=assess(e)
            assert got==expected,(round_id,label,got,expected)
            checks+=1
    print(json.dumps({"state":"PASS_THEORETICAL_GATE_SIM","rounds":3,"scenarios":len(cases),"checks":checks,"formal_70_70":"NOT_VERIFIED","real_three_ci":"HOLD","osi_mutation":0},sort_keys=True))
if __name__=="__main__":run()
