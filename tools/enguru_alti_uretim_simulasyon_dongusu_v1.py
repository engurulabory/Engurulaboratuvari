#!/usr/bin/env python3
"""ENGURU six production fields: collaborative first-draft and three repair rounds.

Pure deterministic synthetic contract simulation. NOT user approval, product field,
independent human review, DoneCheck or six finished products.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "governance/enguru-suzgeci/ENGURU_ALTI_URETIM_ALANI_V1.json"
DOMAINS = ("CORE", "ENGINE", "AGENT", "WEB", "APP", "COMMERCE")
CATEGORIES = ("missing", "need", "requirement", "error", "incorrectness")
MAX_ROUNDS = 3

def frozen_controls(spec, domain):
    controls = spec["shared_controls"] + domain["domain_controls"]
    if (len(controls) != 16 or len({c["id"] for c in controls}) != 16
            or len({c["key"] for c in controls}) != 16
            or any(not all(isinstance(c[k], str) and len(c[k]) >= 4
                           for k in ("id", "title", "key", "required", "negative"))
                   for c in controls)):
        raise ValueError("HOLD_INVALID_FIXED_CONTRACT")
    return controls

def synth_observation(control):
    return {
        "control_id": control["id"],
        "key": control["key"],
        "observed": control["required"],
        "reject_oracle": control["negative"],
        "evidence_kind": "SYNTHETIC_DESIGN_CASE",
    }

def grade(controls, payload):
    # No honor system, no predeclared score and no mutated denominator.
    if not isinstance(payload, dict) or any(k not in {c["id"] for c in controls}
                                             for k in payload):
        return {"verdict": "HOLD_INVALID_PAYLOAD", "raw": 0,
                "score": 0, "gaps": [c["id"] for c in controls]}
    gaps = []
    for c in controls:
        item = payload.get(c["id"])
        if item != synth_observation(c):
            gaps.append(c["id"])
    raw = 16 - len(gaps)
    return {"verdict": "PASS_SYNTHETIC_DESIGN" if raw == 16 else "HOLD_GAPS",
            "raw": raw, "max": 16, "score": round(raw * 100/16, 2), "gaps": gaps}

def adversarial(controls, complete):
    """Falsify each control through three distinct incorrect input mechanisms."""
    errors = []
    for c in controls:
        ident = c["id"]
        for kind in ("wrong_positive", "wrong_negative", "wrong_kind"):
            candidate = copy.deepcopy(complete)
            if kind == "wrong_positive":
                candidate[ident]["observed"] = c["negative"]
            elif kind == "wrong_negative":
                candidate[ident]["reject_oracle"] = "ACCEPT_UNTRUSTED"
            else:
                candidate[ident]["evidence_kind"] = "REAL_FIELD_PASS"
            verdict = grade(controls, candidate)
            if verdict["score"] == 100 or ident not in verdict["gaps"]:
                errors.append(f"{ident}/{kind}")
    return {"attempts": 48, "caught": 48 - len(errors), "errors": errors}

def simulate(spec, domain):
    controls = frozen_controls(spec, domain)
    # The first-draft user discussion is a synthetic rehearsal only.
    # Real projects require an actual user/owner recorded scope decision.
    ids = [c["id"] for c in controls]
    initial = ids[:8] + ids[12:14]  # 10/16 initial candidate; 6 gaps
    if len(set(initial)) != 10:
        raise ValueError("HOLD_INITIAL_FIXTURE")
    store = {c["id"]: synth_observation(c) for c in controls if c["id"] in initial}
    scores, log, meta = [], [], []
    first_gap_ids = [x for x in ids if x not in initial]
    taxonomy = {cid: CATEGORIES[i % len(CATEGORIES)]
                for i, cid in enumerate(first_gap_ids)}
    # Typed diagnostics are hypotheses about deliberately absent design evidence;
    # no operational root cause is claimed from a synthetic fixture.
    for round_id in range(1, MAX_ROUNDS + 1):
        verdict = grade(controls, store)
        scores.append(verdict["score"])
        diagnostic = [
            {"id": cid, "classification": taxonomy[cid],
             "observation": "SYNTHETIC_CONTROL_EVIDENCE_MISSING",
             "root_cause_status": "SYNTHETIC_GAP_OBSERVED_NOT_FIELD_CAUSE",
             "required_change": next(c["required"] for c in controls if c["id"] == cid)}
            for cid in verdict["gaps"]
        ]
        log.append({"round": round_id, "kind": (
            "USER_FIRST_DRAFT_SYNTHETIC" if round_id == 1
            else "AFTER_DIAGNOSIS_REPAIR_AND_RE_SIMULATION"),
            "checked": len(controls), "diagnostic": diagnostic,
            "raw": verdict["raw"],
            "score": verdict["score"], "gaps": verdict["gaps"],
            "verdict": verdict["verdict"],
            "root_cause": "missing synthetic contract evidence" if verdict["gaps"]
                          else "none",
            "user_co_design_status": "MOCK_ONLY_REAL_USER_APPROVAL_HOLD"})
        if round_id == MAX_ROUNDS:
            break
        gaps = verdict["gaps"]
        # Diagnosis precedes repair. Each bounded repair closes specific original IDs.
        to_repair = gaps[:4] if round_id == 1 else gaps
        for control in controls:
            if control["id"] in to_repair:
                store[control["id"]] = synth_observation(control)
        after = grade(controls, store)
        if (len(to_repair) == 0 or after["raw"] <= verdict["raw"]
                or len(verdict["gaps"]) - len(after["gaps"]) != len(to_repair)):
            raise ValueError("HOLD_NO_MEASURED_DESIGN_IMPROVEMENT")
        meta.append({"after_round": round_id, "gap_analysis": gaps,
                     "repair_ids": to_repair,
                     "repair_evidence": [
                         {"control_id": cid, "classification": taxonomy[cid],
                          "before": "EVIDENCE_MISSING",
                          "after": "SYNTHETIC_CONTROL_SPECIFIED",
                          "source": "FIXED_CONTROL_CONTRACT"}
                         for cid in to_repair
                     ],
                     "before_score": verdict["score"],
                     "score_after_repair": after["score"],
                     "remaining": after["gaps"],
                     "proof": "SYNTHETIC_CONTRACT_FIXTURE_ONLY"})
    bad = adversarial(controls, store)
    final = grade(controls, store)
    all_repaired = {cid for step in meta for cid in step["repair_ids"]}
    diagnosed_types = {x["classification"] for x in log[0]["diagnostic"]}
    repair_evidence = [x for step in meta for x in step["repair_evidence"]]
    ok = (scores == [62.5, 87.5, 100.0] and bad["caught"] == 48
          and diagnosed_types == set(CATEGORIES)
          and len(repair_evidence) == 6
          and all(x["before"] != x["after"] for x in repair_evidence)
          and len(all_repaired) == 6 and len(meta) == 2
          and final["verdict"] == "PASS_SYNTHETIC_DESIGN")
    return {"id": domain["id"], "area": domain["name"],
            "shared_controls": 12, "specific_controls": 4,
            "fixed_denominator": 16, "simulation_scores": scores,
            "rounds": log, "repairs": meta,
            "diagnostic_classifications": sorted(diagnosed_types),
            "adversarial": bad,
            "theoretical_adapter": "PASS_3_ROUND_REPAIR_DESIGN" if ok else "HOLD",
            "owner_real_co_design": "HOLD_PENDING_CASE_SPECIFIC_USER_DECISION",
            "actual_products_completed": 0}

def main():
    raw = SPEC_PATH.read_bytes()
    spec = json.loads(raw)
    if (spec.get("schema") != "enguru.production6.methods-adapter/v1"
            or spec.get("scope") != "THEORETICAL_ADAPTERS_ONLY"
            or tuple(x["id"] for x in spec.get("domains", [])) != DOMAINS
            or len(spec.get("shared_controls", [])) != 12
            or spec.get("simulation_loop", {}).get("max_rounds") != 3):
        print(json.dumps({"verdict": "HOLD_CANONICAL_SIX_AREA_SCOPE"}))
        return 2
    domains = [simulate(spec, item) for item in spec["domains"]]
    total_adversarial = sum(x["adversarial"]["caught"] for x in domains)
    ok = (len(domains) == 6
          and all(x["theoretical_adapter"] == "PASS_3_ROUND_REPAIR_DESIGN"
                  for x in domains)
          and total_adversarial == 288)
    receipt = {
        "schema": "enguru.methods.six-domains-three-iteration/v1",
        "scope": "SYNTHETIC_DESIGN_ONLY",
        "verdict": "PASS_6_AREAS_3_ROUND_DESIGN" if ok else "HOLD",
        "config_sha256": hashlib.sha256(raw).hexdigest(),
        "domains": domains, "production_areas": len(domains),
        "simulated_rounds": 18, "repair_events": 12,
        "falsification_pass": total_adversarial,
        "falsification_total": 288,
        "all_user_consent_real": "HOLD_PENDING_REAL_CO_DESIGN",
        "main_5x100_theoretical_terazi": "SEPARATELY_VERIFIED_IN_CI",
        "independent_design_review": "HOLD",
        "github_osi_real_product": "HOLD",
        "verified_finish": "HOLD",
    }
    print(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True))
    return 0 if ok else 2

if __name__ == "__main__":
    raise SystemExit(main())
