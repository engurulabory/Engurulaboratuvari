#!/usr/bin/env python3
"""HYM2/Zülfikar: locate GH-preparation vs official-acceptance circular dependency.

A project- and source-bound planning sufficiency rubric (goal, design, theory).
Every score uses a frozen 10-condition denominator and actual repository data.
Never upgrades ORIGINAL V4.7 50/100, A03/A04, E5, OSi, reviewer or DoneCheck.
The CI 'GitHub 100' claim additionally requires SUCCESS on the exact PR HEAD,
outside this script's own authority.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
from tools.arge_hym2_zulfikar_v12_bridge import (
    ROOT,BLOCKS,TASKS,CASES,MATRIX,PROVENANCE,V3_SHA,SOURCE_PINS,
    crosswalk,read_zulfikar,
)

GATE_FILE="governance/enguru-suzgeci/reviews/ENGURU_ARGE_B01_M01_GITHUB_PREP_GATE_RECONCILIATION_V1.json"
LOCK_FILE="governance/enguru-suzgeci/ENGURU_KALICI_CALISMA_DISIPLINI_V1_LOCK.json"
DISCIPLINE_FILE="governance/enguru-suzgeci/ENGURU_KALICI_CALISMA_DISIPLINI_V1.md"
METHOD_FILE="governance/enguru-suzgeci/ENGURU_ANA_TERAZI_5X100_V1.md"
Z_ENGINE="governance/enguru-suzgeci/zulfikar-v12/zulfikar_v1_2_engine.py"
Z_CONTRACT="governance/enguru-suzgeci/zulfikar-v12/zulfikar_v1_2_design_contract.json"
EXPECTED_DISCIPLINE_SHA="6e288ae18e8249d3a3a954891a75fbec20da23349e371faac07b5cc6e294c50c"
EXPECTED_GH_STATES=("GITHUB_SOURCE_OBSERVED",)*5+("HOLD_REQUIRED_INDEPENDENT_AUTHORITY",)*5


def snapshot(root=ROOT,fetch=None):
    files={p:(root/p).read_bytes() for p in
           (MATRIX,CASES,PROVENANCE,GATE_FILE,LOCK_FILE,DISCIPLINE_FILE,METHOD_FILE)}
    def decode(p):
        return json.loads(files[p])
    if fetch is None:
        mod,contract,zpins=read_zulfikar()
    else:
        mod,contract,zpins=read_zulfikar(fetch=fetch)
    return {
        "files":files, "matrix":decode(MATRIX),"cases":decode(CASES),
        "provenance":decode(PROVENANCE),"gate":decode(GATE_FILE),
        "lock":decode(LOCK_FILE),"discipline":files[DISCIPLINE_FILE].decode("utf8"),
        "method":files[METHOD_FILE].decode("utf8"),
        "zulfi":contract,"zulfi_mod":mod,"zulfi_pins":zpins,
        "mapping":crosswalk(),
    }


def checks(d):
    m=d["matrix"]; c=d["cases"]; p=d["provenance"]; g=d["gate"]
    z=d["zulfi"]; f=d["files"]; lock=d["lock"]; mapping=d["mapping"]
    reg=g["proposed_readiness_trace_gates"]
    state=tuple(q.get("management_state") for q in reg)
    dlock=hashlib.sha256(f[DISCIPLINE_FILE]).hexdigest()
    digests={k:hashlib.sha256(v).hexdigest() for k,v in f.items()}
    scope=p.get("a04_canonical_scope_boundary",{})
    valid_z=set(z.get("closure_ids",[]))=={
        "Z02_EVENT","Z03_TRANSFER","Z04_LINEAGE","Z05_BENCHMARK",
        "Z08_IMPACT","Z10_CONCURRENCY","Z10_SAFE_FIN"}
    # Goal: measurable original aim without using product outcomes as planning prerequisites.
    GOAL={
        "G01_ORIGINAL_40":len(TASKS)==40 and len(set(TASKS))==40,
        "G02_ORIGINAL_6":list(map(len,BLOCKS))==[9,9,7,7,4,4],
        "G03_H1_SCOPE":set(m.get("tasks",{}))==set(BLOCKS[0]) and m.get("block")=="BLOCK01",
        "G04_18_CASES":len(c.get("cases",[]))==18 and c["baseline"].get("cases")==18,
        "G05_234_CONTROLS":c["baseline"].get("rows")==234 and c["baseline"].get("criteria")==13,
        "G06_E5_BOUNDARY":c["baseline"].get("all_18_e5_original_status")=="HOLD",
        "G07_NO_FAKE_OFFICIAL":m.get("official_pass")=="0/9" and p.get("acceptance")=="HOLD",
        "G08_A03_TASK_GRANT":m["reconciled"].get("a03_scope_bound_grant")=="HOLD",
        "G09_A04_RESEARCH_SCOPE":scope.get("status")=="HOLD_OWNER_PRIVATE_CANONICAL_OR_EXPLICIT_RESEARCH_SCOPE",
        "G10_FINISH_SEPARATE":p.get("osi")=="NOT_STARTED" and p.get("acceptance")=="HOLD",
    }
    # Design: project-specific reusable source, boundaries and exactly identifiable tests.
    DESIGN={
        "D01_CANONICAL_V3":lock.get("canonical_v3_sha256")==V3_SHA,
        "D02_DISCIPLINE_LOCK":dlock==EXPECTED_DISCIPLINE_SHA and lock.get("sha256")==EXPECTED_DISCIPLINE_SHA,
        "D03_TEN_ORIGINAL_GH_KEYS":[x.get("gate_id") for x in reg]==[f"GH{i:02d}" for i in range(1,11)],
        "D04_FIXED_GH_BOUNDARY":state==EXPECTED_GH_STATES,
        "D05_TWO_SEPARATE_SCORES":g["score_accounting"].get("github_preparation_last_authoritative_record")=="50/100",
        "D06_PRIVATE_CANONICAL":scope.get("public_review_contract")=="ONLY_NONSECRET_STATUS_REFERENCES_AND_BOUNDED_EVIDENCE",
        "D07_A03_A04_ORIGINAL":all(m["tasks"][x].get("official")=="HOLD" for x in ("A03","A04")),
        "D08_ZULFI_FOUR_PACKAGES":set(z.get("packages",{}))=={"K01","K02","K03","K04"},
        "D09_ZULFI_SEVEN_CLOSURES":valid_z,
        "D10_SINGLE_OWNER_AND_MAPPING":len(mapping)==40 and scope.get("owner_authority")=="SINGLE_HUMAN_OWNER",
    }
    # Theory: distinguish policy hypothesis, real evidence and official acceptance.
    THEORY={
        "T01_SOURCE_BOUND_Z":len(d["zulfi_pins"])==len(SOURCE_PINS)==2,
        "T02_Z_DESIGN_ONLY":z.get("scope")=="DESIGN_ONLY / LOCAL_OFFLINE_VALIDATOR",
        "T03_Z_NO_CORE_OR_OWNER":z.get("new_owner_created") is False and z.get("new_core_created") is False,
        "T04_CI_VS_CANONICAL":g["score_accounting"].get("github_preparation_original_rubric","").startswith("V4.7 5/10"),
        "T05_LATER_STAGES_SEPARATE":state[5:]==EXPECTED_GH_STATES[5:],
        "T06_EXTERNAL_E5_HOLD":g["score_accounting"].get("independent_e5")=="0/18",
        "T07_AUTHORITY_HOLD":p.get("verified_sources")=={} and scope.get("owner_scope_decision")=="HOLD_EXPLICIT_DECISION_PENDING",
        "T08_FIELD_HOLD":g["score_accounting"].get("field")=="0/100",
        "T09_Z_PEER_UNMEASURED":z.get("benchmark_state")=="FEATURE_REFERENCES_ONLY / REAL_PEER_TRIALS_NOT_MEASURED",
        "T10_STAGE_ORDER":"TASARIM" in d["method"] and "TEORİ" in d["method"] and "GITHUB" in d["method"] and "OSI_HANDOFF_PREPARED" in d["method"],
    }
    return {"GOAL":GOAL,"DESIGN":DESIGN,"THEORY":THEORY},digests


def score(d):
    result,hashes=checks(d)
    grades={name:{"passed":sum(v.values()),"total":len(v),
                  "score":round(100*sum(v.values())/len(v),2),
                  "failedIds":[k for k,passed in v.items() if not passed]}
            for name,v in result.items()}
    return {"grades":grades,"source_sha256":hashes}


def simulations(d):
    """Three distinct real source-mutation families: identity, authority, metamorphic."""
    baseline=score(d)["grades"]
    if any(v["score"]!=100 for v in baseline.values()):
        return {"state":"HOLD_BASELINE_GAPS","failed":[k for k,v in baseline.items() if v["score"]!=100]}
    cases=[
        ("SIM1_SOURCE_GOAL",
         (("cases","baseline","rows",999),"GOAL")),
        ("SIM1_SOURCE_DESIGN",
         (("lock","sha256","x"*64),"DESIGN")),
        ("SIM1_SOURCE_THEORY",
         (("zulfi","benchmark_state","FICTIONAL_REAL_BENCHMARK"),"THEORY")),
        ("SIM2_FALSE_A04",
         (("provenance","a04_canonical_scope_boundary","status","PASS_OFFICIAL"),"GOAL")),
        ("SIM2_FALSE_OWNER",
         (("provenance","a04_canonical_scope_boundary","owner_authority","SECOND_OWNER"),"DESIGN")),
        ("SIM2_FAKE_GH",
         (("gate","proposed_readiness_trace_gates",5,"management_state","PASS_UNPROVEN"),"DESIGN")),
        ("SIM3_FAKE_E5",
         (("gate","score_accounting","independent_e5","18/18"),"THEORY")),
        ("SIM3_PREMATURE_FIN",
         (("matrix","official_pass","9/9"),"GOAL")),
        ("SIM3_OWNER_GRANT_SHORTCUT",
         (("provenance","a04_canonical_scope_boundary","owner_scope_decision","PASS_NO_SOURCE"),"THEORY")),
    ]
    observed={}
    for name,(path,phase) in cases:
        case=copy.deepcopy({k:v for k,v in d.items() if k!="zulfi_mod"})
        obj=case
        for key in path[:-2 if len(path)>2 and isinstance(path[-2],int) else 1]:
            obj=obj[key]
        # Mutations are explicit and independently scored with unchanged denominators.
        if isinstance(path[-2],int):
            obj=case
            for key in path[:-1]:obj=obj[key]
            obj[path[-1]]=None # overwritten below
        else:
            obj[path[-1]]=None
        # Locate parent exactly and apply adversarial value.
        # All tuples except the six-component GH row mutation end in value.
        # Reconstruct from pristine object for deterministic outcome.
        case=copy.deepcopy({k:v for k,v in d.items() if k!="zulfi_mod"})
        keys=list(path)
        newval=keys.pop()
        dest=case
        for key in keys[:-1]:dest=dest[key]
        dest[keys[-1]]=newval
        verdict=score(case)["grades"][phase]
        observed[name]={"expected":"HOLD","result":"PASS_EXPECTED_HOLD" if verdict["score"]<100 else "FAIL_FALSE_PASS",
                        "affectedPhase":phase,"detectedFailedIds":verdict["failedIds"]}
    total=sum(v["result"]=="PASS_EXPECTED_HOLD" for v in observed.values())
    return {"state":"PASS_THREE_DISTINCT_SIMULATION_FAMILIES" if total==len(cases) else "HOLD_MUTATION_ESCAPED",
            "passed":total,"total":len(cases),
            "families":{"SIM1_SOURCE":3,"SIM2_AUTHORITY":3,"SIM3_METAMORPHIC":3},
            "observations":observed}


def run(root=ROOT,fetch=None):
    out={"schema":"enguru.hym2.zulfikar.deadlock-preparation/v1",
         "state":"HOLD","official_progress":"0/40",
         "legacy_github_preparation":"50/100_HOLD",
         "field":"0/100","verified_finish":"HOLD",
         "owner":"ONE_HUMAN_OWNER"}
    try:
        d=snapshot(root,fetch)
        s=score(d);sim=simulations(d)
        out.update(goal_design_theory=s["grades"],source_sha256=s["source_sha256"],
            three_simulations=sim,
            source_of_deadlock="V4.7_GH06_GH10_LATER_AUTHORITY_EVIDENCE_BLOCKS_PREFIELD_GITHUB_SCORE",
            original_GH06_GH10=[{"id":x["gate_id"],"state":x["management_state"]}
                for x in d["gate"]["proposed_readiness_trace_gates"][5:]],
            original_40_work_ids=list(TASKS),original_blocks=[list(x) for x in BLOCKS],
            zulfikar_verified_pins=d["zulfi_pins"],
            github_actual_ci="REQUIRES_EXACT_HEAD_HOST_CONFIRMATION",
            git_preparation_5x100="PRESERVED_IN_EXISTING_SEPARATE_VERIFIER",
            task_preparation_acceptance="HOLD_UNTIL_ALL_ORIGINAL_GH_GATES_SATISFIED",
            next_action="FINISH_PROJECT_SPECIFIC_GITHUB_PREFLIGHT_THEN_REAL_OWNER_SCOPE_A03_A04_WITHOUT_CIRCULAR_DEPENDENCY")
        if all(v["score"]==100 for v in s["grades"].values()) and sim["state"]=="PASS_THREE_DISTINCT_SIMULATION_FAMILIES":
            out["state"]="PASS_SCOPED_GOAL_DESIGN_THEORY_EVIDENCE_ONLY"
    except (OSError,ValueError,KeyError,TypeError,UnicodeError) as e:
        out["reason"]=type(e).__name__+":"+str(e)[:180]
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--receipt",type=Path,required=True)
    args=parser.parse_args()
    res=run()
    args.receipt.write_text(json.dumps(res,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"state":res["state"],
        "grades":res.get("goal_design_theory",{}),
        "simulations":res.get("three_simulations",{}).get("state"),
        "official":res["official_progress"],
        "github_legacy":res["legacy_github_preparation"]},sort_keys=True))
    return 0 if res["state"]=="PASS_SCOPED_GOAL_DESIGN_THEORY_EVIDENCE_ONLY" else 2


if __name__=="__main__":
    raise SystemExit(main())
