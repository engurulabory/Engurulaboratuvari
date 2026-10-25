#!/usr/bin/env python3
"""External-to-simulator adversarial test oracle: reject every damaged contract field.

Same repository, separate executable; no claim of independent human reviewer.
"""
from __future__ import annotations
import copy
import json
from enguru_method_dynamic_loop_v2 import (
    CONFIG, CASES, KINDS, DOMAIN_IDS, ordered_controls, diagnose, run_case, run_all
)

def expect_holds(spec):
    checks=0
    errors=[]
    models={d["id"]:d for d in spec["domains"]}
    corruptions={
        "missing":lambda obs,cid:obs.pop(cid),
        "need":lambda obs,cid:obs[cid].__setitem__("negative",""),
        "requirement":lambda obs,cid:obs[cid].__setitem__("positive",""),
        "error":lambda obs,cid:obs[cid].__setitem__("negative","ACCEPT_NEGATIVE"),
        "incorrectness":lambda obs,cid:obs[cid].__setitem__("positive","WRONG_REQUIREMENT"),
        "provenance":lambda obs,cid:obs[cid].__setitem__("origin","FORGED_SOURCE"),
    }
    for area in DOMAIN_IDS:
        controls=ordered_controls(spec,models[area])
        for c in controls:
            cid=c["id"]
            for kind,apply in corruptions.items():
                observed={x["id"]:{"positive":x["required"],"negative":x["negative"],
                                   "origin":"CONTRACT_SOURCE"} for x in controls}
                apply(observed,cid)
                verdict=diagnose(controls,observed)
                checks+=1
                if (verdict["raw"]!=15 or verdict["score"]!=93.75
                      or verdict["verdict"]!="HOLD_DESIGN_GAPS"
                      or len(verdict["gaps"])!=1
                      or verdict["gaps"][0]["kind"]!=kind
                      or verdict["gaps"][0]["id"]!=cid):
                    errors.append(f"{area}/{cid}/{kind}")
    return checks,errors

def expect_cases(spec,registry):
    checked=0
    errors=[]
    for case in registry["cases"]:
        r=run_case(spec,case)
        want="PASS_THREE_ROUND_THEORETICAL_CASE" if case["oracle_expected_final"]=="PASS" else "HOLD_UNRESOLVED_DESIGN_GAPS"
        checked+=1
        if r["state"]!=want:
            errors.append(case["id"]+"/oracle")
        if len(r["rounds"])!=3 or r["round_scores"]!=[x["score"] for x in r["rounds"]]:
            errors.append(case["id"]+"/round_consistency")
        tampered=copy.deepcopy(case)
        tampered["reported_score"]=100
        tampered["oracle_expected_final"]="PASS" if case["oracle_expected_final"]=="HOLD" else "HOLD"
        r2=run_case(spec,tampered)
        checked+=1
        if r2["state"]!=r["state"] or r2["round_scores"]!=r["round_scores"]:
            errors.append(case["id"]+"/self_claim_invariance")
    # 3-round engine must obey *input* budgets, never embed fixed score targets.
    sample=copy.deepcopy(registry["cases"][0])
    sample["budgets"]=[0,0]
    nofix=run_case(spec,sample)
    checked+=1
    if len(set(nofix["round_scores"]))!=1 or nofix["state"]!="HOLD_UNRESOLVED_DESIGN_GAPS":
        errors.append("zero_budget_falsification")
    sample["budgets"]=[16,16]
    fullfix=run_case(spec,sample)
    checked+=1
    if (fullfix["round_scores"][1]!=100 or fullfix["round_scores"][2]!=100
            or fullfix["state"]!="PASS_THREE_ROUND_THEORETICAL_CASE"):
        errors.append("variable_budget_falsification")
    sample["faults"]=sample["faults"]+[copy.deepcopy(sample["faults"][0])]
    try:
        run_case(spec,sample)
        errors.append("duplicate_mutation_pass")
    except ValueError:
        pass
    checked+=1
    sample=copy.deepcopy(registry["cases"][0])
    sample["faults"][0]["control"]="UNKNOWN_CONTROL_FORGED"
    try:
        run_case(spec,sample)
        errors.append("unknown_control_pass")
    except ValueError:
        pass
    checked+=1
    return checked,errors

def main():
    spec=json.loads(CONFIG.read_text())
    registry=json.loads(CASES.read_text())
    oracle_checks,errors1=expect_holds(spec)
    case_checks,errors2=expect_cases(spec,registry)
    final=run_all()
    ok=(oracle_checks==6*16*len(KINDS) and case_checks==52
        and not errors1 and not errors2
        and final["verdict"]=="PASS_VARIABLE_DIAGNOSTIC_DESIGN"
        and final["pass_cases"]==12 and final["hold_cases"]==12)
    out={"schema":"enguru.methods.independent-adversarial-falsification/v2",
         "verdict":"PASS_ADVERSARIAL_SOURCE_CHALLENGES" if ok else "HOLD_FINDINGS",
         "control_mutations":oracle_checks,"scenario_checks":case_checks,
         "expected_pass_cases":12,"expected_hold_cases":12,
         "false_positive_count":len(errors1)+len(errors2),
         "findings":errors1+errors2,"independent_human_review":"HOLD",
         "mac_osi":"HOLD","donecheck":"HOLD","verified_finish":"HOLD"}
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0 if ok else 2

if __name__=="__main__":
    raise SystemExit(main())
