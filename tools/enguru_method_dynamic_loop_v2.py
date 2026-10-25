#!/usr/bin/env python3
"""Three-round six-domain design simulator with discovered faults, not planned scores.

Synthetic fixtures only; no real-user consent, OSi evidence, or DoneCheck authority.
Scores derive from observed contract state; explicit evaluator gets no expected scores.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "governance/enguru-suzgeci/ENGURU_ALTI_URETIM_ALANI_V1.json"
CASES = ROOT / "governance/enguru-suzgeci/ENGURU_DINAMIK_SIMULASYON_V2_CASES.json"
DOMAIN_IDS = ("CORE", "ENGINE", "AGENT", "WEB", "APP", "COMMERCE")
KINDS = ("missing", "need", "requirement", "error", "incorrectness", "provenance")
FIELDS = {"need":"negative", "requirement":"positive", "error":"negative",
          "incorrectness":"positive", "provenance":"origin"}
CORRUPT = {"need":"", "requirement":"", "error":"ACCEPT_RISK",
           "incorrectness":"UNSUPPORTED_ASSERTION", "provenance":"UNTRUSTED_SELF_ASSERTION"}
PRIORITY = {"error":0,"incorrectness":1,"provenance":2,"missing":3,"requirement":4,"need":5}

def ordered_controls(spec, domain):
    controls = spec["shared_controls"] + domain["domain_controls"]
    ids = [c["id"] for c in controls]
    if len(controls) != 16 or len(set(ids)) != 16 or any(
        not c.get("required") or not c.get("negative") or not c.get("key")
        for c in controls
    ):
        raise ValueError("HOLD_FIXED_CONTRACT_INVALID")
    return controls

def gold(c):
    return {"positive":c["required"],"negative":c["negative"],"origin":"CONTRACT_SOURCE"}

def seed(controls, defects):
    lookup = {c["id"]:c for c in controls}
    if len(defects) != len({d["control"] for d in defects}):
        raise ValueError("HOLD_DUPLICATE_CONTROL_MUTATION")
    observed = {cid:gold(c) for cid,c in lookup.items()}
    for fault in defects:
        cid,kind = fault["control"],fault["kind"]
        if cid not in lookup or kind not in KINDS:
            raise ValueError("HOLD_UNKNOWN_CONTROL_OR_FAULT")
        if kind == "missing":
            observed.pop(cid)
        else:
            observed[cid][FIELDS[kind]] = CORRUPT[kind]
    return observed

def diagnose(controls, observed):
    if not isinstance(observed, dict):
        raise ValueError("HOLD_OBSERVATION_FORMAT")
    expected_ids = {c["id"] for c in controls}
    if set(observed) - expected_ids:
        raise ValueError("HOLD_UNAUTHORIZED_CONTROL_ADDITION")
    gaps=[]
    for c in controls:
        cid=c["id"]
        obj=observed.get(cid)
        kind=None
        if obj is None:
            kind="missing"
        elif not isinstance(obj,dict):
            kind="incorrectness"
        elif obj.get("positive") == "":
            kind="requirement"
        elif obj.get("positive") != c["required"]:
            kind="incorrectness"
        elif obj.get("negative") == "":
            kind="need"
        elif obj.get("negative") != c["negative"]:
            kind="error"
        elif obj.get("origin") != "CONTRACT_SOURCE":
            kind="provenance"
        if kind:
            gaps.append({"id":cid,"kind":kind,
                "observed":"SYNTHETIC_CONTRACT_OBSERVATION",
                "expected":"CONTRACT_GOLDEN_REFERENCE",
                "root_cause_level":"DETERMINISTIC_SYNTHETIC_FIELD_DIAGNOSIS"})
    points=len(controls)-len(gaps)
    return {"raw":points,"total":len(controls),
            "score":round(points*100/len(controls),4),
            "gaps":gaps, "verdict":"PASS_DESIGN_FIXTURE" if not gaps else "HOLD_DESIGN_GAPS"}

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def run_case(spec, case):
    domains={d["id"]:d for d in spec["domains"]}
    if case["area"] not in domains:
        raise ValueError("HOLD_UNKNOWN_DOMAIN")
    controls=ordered_controls(spec,domains[case["area"]])
    expected={c["id"]:c for c in controls}
    if len(case["budgets"]) != 2 or any(type(n)!=int or not 0<=n<=16 for n in case["budgets"]):
        raise ValueError("HOLD_REPAIR_BUDGET")
    unrepairable=set(case.get("unrepairable",[]))
    if not unrepairable.issubset(expected):
        raise ValueError("HOLD_UNKNOWN_REPAIR_AUTHORITY")
    observed=seed(controls,case["faults"])
    rounds=[]
    all_repairs=[]
    for idx in range(3):
        outcome=diagnose(controls,observed)
        round_info={"round":idx+1,"score":outcome["score"],"raw":outcome["raw"],
                    "gap_ids":[x["id"] for x in outcome["gaps"]],
                    "diagnosis":outcome["gaps"],"state_hash":digest(observed),
                    "consent":"MOCK_ONLY_REAL_USER_CASE_HOLD"}
        if idx<2:
            available=[x for x in sorted(outcome["gaps"],
                       key=lambda x:(PRIORITY[x["kind"]],x["id"]))
                       if x["id"] not in unrepairable]
            selected=available[:case["budgets"][idx]]
            repair_receipts=[]
            for gap in selected:
                cid=gap["id"]
                before=digest(observed.get(cid))
                observed[cid]=gold(expected[cid])
                after=digest(observed[cid])
                if before==after:
                    raise ValueError("HOLD_NO_OBSERVABLE_REPAIR")
                repair_receipts.append({"id":cid,"classified_kind":gap["kind"],
                    "before_sha256":before,"after_sha256":after,
                    "evidence":"SYNTHETIC_CONTRACT_FIELD_REPAIR"})
            after_outcome=diagnose(controls,observed)
            if after_outcome["raw"]-outcome["raw"]!=len(selected):
                raise ValueError("HOLD_REPAIR_EFFECT_MISMATCH")
            round_info["repairs_after_round"]=repair_receipts
            round_info["new_score_after_repair"]=after_outcome["score"]
            all_repairs.extend(repair_receipts)
        rounds.append(round_info)
    final=rounds[-1]
    return {"id":case["id"],"area":case["area"],"round_scores":[x["score"] for x in rounds],
        "rounds":rounds,"repairs":len(all_repairs),"fixed_denominator":16,
        "state":"PASS_THREE_ROUND_THEORETICAL_CASE" if final["score"]==100
                else "HOLD_UNRESOLVED_DESIGN_GAPS",
        "remaining":final["gap_ids"],
        "claimed_points_ignored":True,"real_user_decision":"HOLD",
        "field":"HOLD","official_verified_finish":"HOLD"}

def run_all():
    cb=CONFIG.read_bytes()
    fb=CASES.read_bytes()
    spec=json.loads(cb)
    registry=json.loads(fb)
    if tuple(x["id"] for x in spec["domains"])!=DOMAIN_IDS:
        raise ValueError("HOLD_SIX_AREA_CANONICAL_SCOPE")
    cases=registry["cases"]
    if len(cases)!=24 or len({c["id"] for c in cases})!=24:
        raise ValueError("HOLD_FIXTURE_COVERAGE")
    results=[run_case(spec,c) for c in cases]
    by_area={area:sum(x["area"]==area for x in results) for area in DOMAIN_IDS}
    passed=sum(x["state"]=="PASS_THREE_ROUND_THEORETICAL_CASE" for x in results)
    held=sum(x["state"]=="HOLD_UNRESOLVED_DESIGN_GAPS" for x in results)
    variable=len({tuple(x["round_scores"]) for x in results}) >= 3
    ok=(all(x==4 for x in by_area.values()) and passed==12 and held==12 and variable
       and all(x["rounds"][0]["consent"]=="MOCK_ONLY_REAL_USER_CASE_HOLD"
               for x in results))
    return {"schema":"enguru.methods.dynamic-repair-6domains/v2",
      "verdict":"PASS_VARIABLE_DIAGNOSTIC_DESIGN" if ok else "HOLD_TEST_CONTRACT",
      "area_coverage":by_area,"cases":len(results),"pass_cases":passed,
      "hold_cases":held,"score_sequences":len({tuple(x["round_scores"]) for x in results}),
      "cases_detail":results,"canonical_config_sha256":hashlib.sha256(cb).hexdigest(),
      "fixture_sha256":hashlib.sha256(fb).hexdigest(),"outcomes_not_fixed_per_round":True,
      "user_co_design":"HOLD_REAL_CASE","mac_osi":"HOLD","donecheck":"HOLD",
      "verified_finish":"HOLD"}

def main():
    r=run_all()
    print(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True))
    return 0 if r["verdict"]=="PASS_VARIABLE_DIAGNOSTIC_DESIGN" else 2

if __name__=="__main__":
    raise SystemExit(main())
