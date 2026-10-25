#!/usr/bin/env python3
"""ENGURU Ana Terazi V1: THEORY, DESIGN, SIM1, SIM2, SIM3 separately scored.

Read-only, offline, deterministic, versioned 5-axis design rehearsal.
Real native acceptance, human review, DoneCheck and execution are separate gates.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from enguru_tasarim_48_validation_v2 import (
    MATRIX, FIXTURES, CONTROL_IDS, V3_PIN, EXPECTED, PEERS,
    audit, decision,
)
from enguru_tasarim_48_simulation import BASE, decision as guarded_decision

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md"
LOCK = ROOT / "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json"

THEORY_AXIOMS = (
    "T01_CANONICAL_LOCK", "T02_EIGHT_STAGES",
    "T03_SINGLE_GOAL", "T04_FIXED_ACCEPTANCE_DENOMINATOR",
    "T05_THREE_PART_FINISH_ACCOUNTING", "T06_INDEPENDENT_VERIFIER",
    "T07_SIMULATION_REALITY_SEPARATION", "T08_FAIL_CLOSED_SECURITY",
    "T09_TRACEABLE_THEORY_TO_DESIGN", "T10_HUMAN_OFFICIAL_FINISH_SEPARATION",
)

def theory_checks(m, v3, lock):
    controls = m.get("controls", [])
    has_48 = (type(controls) is list and len(controls) == 48
              and [c.get("id") for c in controls] == CONTROL_IDS)
    eight = (
        "Hakikati gör", "Değeri koru", "Eksikleri ve ihtiyaçları",
        "Gerekli farkı üret", "Eksikleri tamamla", "Kanıtla",
        "Bir sonraki ihtiyaçları", "İlerlet."
    )
    theory = {
        "T01_CANONICAL_LOCK": (
            lock.get("sha256") == V3_PIN
            and hashlib.sha256(v3.encode("utf-8")).hexdigest() == V3_PIN
            and m.get("canonical_v3_sha256") == V3_PIN),
        "T02_EIGHT_STAGES": all(x in v3 for x in eight),
        "T03_SINGLE_GOAL": (
            "TEK ANA HEDEF" in v3
            and has_48 and "Tek ana hedef" in controls[1].get("criterion", "")),
        "T04_FIXED_ACCEPTANCE_DENOMINATOR": (
            has_48 and len(m.get("areas", [])) == 12
            and all(a.get("control_count") == 4 for a in m.get("areas", []))
            and m.get("baseline_20261024", {}).get("raw_points") == 211
            and m.get("design_target", {}).get("raw_points") == 240),
        "T05_THREE_PART_FINISH_ACCOUNTING": all(x in v3 for x in (
            "ÜÇLÜ TAMAMLAMA MUHASEBESİ", "EXECUTION=100%",
            "EVIDENCE=100%", "ALL_REQUIRED_AUTHORITY_GATES=PASS")),
        "T06_INDEPENDENT_VERIFIER": (
            "Bağımsız doğrulayıcının" in v3 and has_48
            and "HOLD" in controls[31].get("reject_case", "")
            and guarded_decision({**BASE, "reviewer_independent": False})
                == "HOLD_REVIEWER_IDENTITY"),
        "T07_SIMULATION_REALITY_SEPARATION": (
            "Simülasyonu gerçek çalıştırmadan ayrı" in v3
            and has_48
            and all(c.get("implementation_state") == "NOT_ASSESSED"
                    and c.get("real_field_state") == "NOT_ASSESSED"
                    for c in controls)),
        "T08_FAIL_CLOSED_SECURITY": (
            has_48 and "BLOCKED" in controls[36].get("reject_case", "")
            and "BLOCKED" in controls[39].get("reject_case", "")
            and guarded_decision({**BASE, "secret_safe": False}) == "BLOCKED_RISK"
            and guarded_decision({**BASE, "cost_approved": False}) == "BLOCKED_RISK"),
        "T09_TRACEABLE_THEORY_TO_DESIGN": (
            has_48 and m.get("design_v2", {}).get("fixed_denominator") == 240
            and all(c.get("oracle_binding", {}).get("case_id") == f"ORACLE_{c['id']}"
                    and c.get("peer_evidence", {}).get("source_id") in PEERS
                    and c.get("peer_evidence", {}).get("url") ==
                    PEERS[c["peer_evidence"]["source_id"]]
                    for c in controls)),
        "T10_HUMAN_OFFICIAL_FINISH_SEPARATION": (
            has_48
            and m.get("authority", {}).get("independent_review") == "HOLD"
            and m.get("authority", {}).get("osi_field") == "HOLD"
            and m.get("authority", {}).get("verified_finish") == "HOLD"
            and "HOLD" in controls[35].get("reject_case", "")
            and guarded_decision({**BASE, "simulated": False})
               == "EXTERNAL_AUTHORITIES_REQUIRED"),
    }
    assert tuple(theory) == THEORY_AXIOMS
    return {key:bool(value) for key,value in theory.items()}

def theory_challenges(m, v3, lock):
    # Exactly one falsification attempt per theoretical axiom; no input overwrites.
    issues=[]
    tests=(
        lambda x,y,z: z.update(sha256="tampered"),
        lambda x,y,z: y.replace("Hakikati gör", "SENTINEL_WRONG_STAGE"),
        lambda x,y,z: y.replace("TEK ANA HEDEF", "OTHER_GOAL"),
        lambda x,y,z: x["areas"].pop(),
        lambda x,y,z: y.replace("ÜÇLÜ TAMAMLAMA MUHASEBESİ", "BROKEN_ACCOUNTING"),
        lambda x,y,z: x["controls"][31].update(reject_case="ACCEPT"),
        lambda x,y,z: x["controls"][0].update(real_field_state="PASS"),
        lambda x,y,z: x["controls"][36].update(reject_case="ACCEPT"),
        lambda x,y,z: x["controls"][0]["peer_evidence"].update(url="https://invalid.example"),
        lambda x,y,z: x["authority"].update(verified_finish="PASS"),
    )
    for i,corrupt in enumerate(tests):
        x,z=copy.deepcopy(m),copy.deepcopy(lock)
        changed=corrupt(x,v3,z)
        y=changed if isinstance(changed,str) else v3
        axioms=theory_checks(x,y,z)
        if axioms[THEORY_AXIOMS[i]]:
            issues.append(THEORY_AXIOMS[i])
    return {"attempts":10,"caught":10-len(issues),"misses":issues}

def positive_negative_missing(m,fx):
    errors=[]
    for i,fixture in enumerate(fx["fixtures"]):
        cid=CONTROL_IDS[i]
        for kind,expected_result in (
            ("positive","DESIGN_CASE_PASS_ONLY"),
            ("negative","HOLD_DESIGN_CASE"),
            ("missing","HOLD_DESIGN_CASE"),
        ):
            if decision(cid,fixture[kind]) != expected_result:
                errors.append(f"{cid}:{kind}")
    return {"cases":144,"pass":144-len(errors),"errors":errors}

def adversarial_tamper(m,fx):
    errors=[]
    original=audit(m,fx)
    if original.get("raw") != 240:
        errors.append("BASELINE_DESIGN_HOLD")
    for i,cid in enumerate(CONTROL_IDS):
        key=EXPECTED[cid][0]
        for category in ("fixture","peer","binding"):
            mx,fy=copy.deepcopy(m),copy.deepcopy(fx)
            if category=="fixture":
                fy["fixtures"][i]["positive"][key]="tampered-positive"
            elif category=="peer":
                mx["controls"][i]["peer_evidence"]["url"]="https://invalid.example"
            else:
                mx["controls"][i]["oracle_binding"]["expected_design_value"]="forged"
            if audit(mx,fy).get("raw",0) >= 240:
                errors.append(f"{cid}:{category}")
    return {"cases":144,"pass":144-len(errors),"errors":errors}

def metamorphic_checks(m,fx):
    errors=[]
    original=audit(m,fx).get("raw")
    for i,cid in enumerate(CONTROL_IDS):
        for category in ("claim-invariance","baseline-drift","field-claim"):
            x=copy.deepcopy(m)
            if category=="claim-invariance":
                x["controls"][i]["candidate_design_points"]=0
                correct=audit(x,fx).get("raw")==original
            elif category=="baseline-drift":
                x["controls"][i]["baseline_design_points"]=0
                correct=audit(x,fx).get("raw",0)<original
            else:
                x["controls"][i]["real_field_state"]="PASS"
                correct=audit(x,fx).get("raw",0)<original
            if not correct:
                errors.append(f"{cid}:{category}")
    return {"cases":144,"pass":144-len(errors),"errors":errors}

def main():
    mb=MATRIX.read_bytes()
    fb=FIXTURES.read_bytes()
    vb=V3.read_bytes()
    lb=LOCK.read_bytes()
    m,fx,lock=json.loads(mb),json.loads(fb),json.loads(lb)
    v3=vb.decode("utf-8")
    theory=theory_checks(m,v3,lock)
    falsification=theory_challenges(m,v3,lock)
    theory_p=sum(theory.values())*10 if falsification["caught"]==10 else 0
    design_raw=audit(m,fx)
    design_p=design_raw.get("score",0) if design_raw.get("every_control_5") else 0
    simulator=[
        ("SIM1_GOLDEN_NEGATIVE_MISSING",positive_negative_missing(m,fx)),
        ("SIM2_ADVERSARIAL_SOURCE_BINDING",adversarial_tamper(m,fx)),
        ("SIM3_METAMORPHIC_INVARIANCE",metamorphic_checks(m,fx)),
    ]
    sim_scores=[]
    for name,result in simulator:
        sim_scores.append({"id":name,"score":round(result["pass"]*100/result["cases"],5),
                           "passed":result["pass"],"total":result["cases"],
                           "errors":result["errors"]})
    scores={"THEORY":theory_p,"DESIGN":design_p}
    scores.update({f"SIM{i+1}":x["score"] for i,x in enumerate(sim_scores)})
    gate=(len(theory)==10 and all(theory.values())
          and falsification["caught"]==10
          and all(value==100 for value in scores.values()))
    receipt={
        "schema":"enguru.methods.main-balance/v1",
        "verdict":"PASS_THEORETICAL_PREPARATION_5X100" if gate else "HOLD_THEORETICAL_PREPARATION",
        "fixed_denominator":"THEORY=10x10, DESIGN=48x5, SIM1/2/3=144 distinct checks each",
        "scores":scores,
        "theory_axioms":theory,
        "theory_falsification":falsification,
        "design_control_points":design_raw.get("raw",0),
        "design_control_count":len(design_raw.get("results",[])),
        "three_simulations":sim_scores,
        "matrix_sha256":hashlib.sha256(mb).hexdigest(),
        "oracles_sha256":hashlib.sha256(fb).hexdigest(),
        "canonical_v3_sha256":hashlib.sha256(vb).hexdigest(),
        "v3_lock_sha256":hashlib.sha256(lb).hexdigest(),
        "self_claimed_points_used":False,
        "simulation_cases_are_synthetic":True,
        "human_independent_design_review":"HOLD",
        "product_real_execution":"HOLD",
        "mac_osi_field":"HOLD",
        "official_donecheck":"HOLD",
        "verified_finish":"HOLD",
    }
    print(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True))
    return 0 if gate else 2

if __name__=="__main__":
    raise SystemExit(main())
