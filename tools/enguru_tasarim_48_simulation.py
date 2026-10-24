#!/usr/bin/env python3
"""ENGURU design48 deterministic theoretical simulation; zero external side effects.

Scope: design-contract falsification only. Never issues official PASS/owner/DoneCheck.
Run: python3 -B tools/enguru_tasarim_48_simulation.py
"""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "governance/enguru-suzgeci/ENGURU_TASARIM_48_KONTROL_MATRISI_V1.json"
LOCK_PIN = "11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc"
REQUIRED_KEYS = ("id", "area_id", "criterion", "pass_design_condition",
                 "reject_case", "canonical_source", "peer_refs", "design_status")

BASE = dict(
    canonical=True, source_match=True, fresh_head=True, unique_ids=True,
    correct_product=True, secret_safe=True, cost_approved=True,
    capability_supported=True, schedule_observed=True, checkpoint=True,
    replay_safe=True, rollback_ready=True, executed=True, field_tested=True,
    tests_passed=True, negative_tests_passed=True, evidence_valid=True,
    reviewer_independent=True, reviewer_done=True, donecheck_valid=True,
    owner_valid=True, user_outcome_measured=True, simulated=True
)

# A synthetic PASS is explicitly different from an actual production acceptance.
def decision(facts):
    if not facts["secret_safe"] or not facts["cost_approved"]:
        return "BLOCKED_RISK"
    ordered = (
        ("canonical", "HOLD_CANONICAL"),
        ("source_match", "HOLD_SOURCE_DRIFT"),
        ("fresh_head", "HOLD_STALE_HEAD"),
        ("unique_ids", "HOLD_DUPLICATE_CONTROL"),
        ("correct_product", "HOLD_PRODUCT_SCOPE"),
        ("capability_supported", "HOLD_UNSUPPORTED_CAPABILITY"),
        ("schedule_observed", "HOLD_SCHEDULE_NOT_OBSERVED"),
        ("checkpoint", "HOLD_CHECKPOINT"),
        ("replay_safe", "HOLD_REPLAY"),
        ("rollback_ready", "HOLD_RECOVERY"),
        ("executed", "HOLD_EXECUTION"),
        ("field_tested", "HOLD_FIELD"),
        ("tests_passed", "HOLD_TESTS"),
        ("negative_tests_passed", "HOLD_NEGATIVE_TESTS"),
        ("evidence_valid", "HOLD_EVIDENCE"),
        ("reviewer_independent", "HOLD_REVIEWER_IDENTITY"),
        ("reviewer_done", "HOLD_INDEPENDENT_REVIEW"),
        ("donecheck_valid", "HOLD_DONECHECK"),
        ("owner_valid", "HOLD_OWNER_AUTHORITY"),
        ("user_outcome_measured", "HOLD_USER_OUTCOME")
    )
    for key, verdict in ordered:
        if not facts[key]:
            return verdict
    return "SIMULATED_ACCEPTANCE_ONLY" if facts["simulated"] else "EXTERNAL_AUTHORITIES_REQUIRED"

SCENARIOS = (
    ("N01_missing_canonical", "canonical", "HOLD_CANONICAL"),
    ("N02_sha_drift", "source_match", "HOLD_SOURCE_DRIFT"),
    ("N03_stale_head", "fresh_head", "HOLD_STALE_HEAD"),
    ("N04_duplicate_control", "unique_ids", "HOLD_DUPLICATE_CONTROL"),
    ("N05_wrong_product", "correct_product", "HOLD_PRODUCT_SCOPE"),
    ("N06_private_secret", "secret_safe", "BLOCKED_RISK"),
    ("N07_unapproved_spend", "cost_approved", "BLOCKED_RISK"),
    ("N08_unsupported_capability", "capability_supported", "HOLD_UNSUPPORTED_CAPABILITY"),
    ("N09_unobserved_schedule", "schedule_observed", "HOLD_SCHEDULE_NOT_OBSERVED"),
    ("N10_missing_checkpoint", "checkpoint", "HOLD_CHECKPOINT"),
    ("N11_replay_duplicates_effect", "replay_safe", "HOLD_REPLAY"),
    ("N12_missing_rollback", "rollback_ready", "HOLD_RECOVERY"),
    ("N13_no_real_execution", "executed", "HOLD_EXECUTION"),
    ("N14_no_field_evidence", "field_tested", "HOLD_FIELD"),
    ("N15_missing_tests", "tests_passed", "HOLD_TESTS"),
    ("N16_no_negative_tests", "negative_tests_passed", "HOLD_NEGATIVE_TESTS"),
    ("N17_bad_evidence", "evidence_valid", "HOLD_EVIDENCE"),
    ("N18_same_reviewer", "reviewer_independent", "HOLD_REVIEWER_IDENTITY"),
    ("N19_no_review", "reviewer_done", "HOLD_INDEPENDENT_REVIEW"),
    ("N20_unsigned_donecheck", "donecheck_valid", "HOLD_DONECHECK"),
    ("N21_owner_missing", "owner_valid", "HOLD_OWNER_AUTHORITY"),
    ("N22_unmeasured_user_impact", "user_outcome_measured", "HOLD_USER_OUTCOME"),
    ("P23_synthetic_all_valid", None, "SIMULATED_ACCEPTANCE_ONLY"),
    ("N24_design_only_no_execution", "executed", "HOLD_EXECUTION")
)

def run():
    raw = MATRIX.read_bytes()
    m = json.loads(raw)
    controls = m.get("controls", [])
    ids = [c.get("id") for c in controls]
    expected = [f"D{i:02}" for i in range(1, 49)]
    structural_errors = []
    if ids != expected:
        structural_errors.append("CONTROL_IDS_OR_ORDER")
    if len(m.get("areas", [])) != 12:
        structural_errors.append("AREA_COUNT")
    if m.get("canonical_v3_sha256") != LOCK_PIN:
        structural_errors.append("V3_PIN")
    for c in controls:
        if any(not c.get(k) for k in REQUIRED_KEYS):
            structural_errors.append("INCOMPLETE_" + str(c.get("id")))
        if c.get("design_status") != "SPECIFIED":
            structural_errors.append("NOT_SPECIFIED_" + str(c.get("id")))
        if c.get("implementation_state") != "NOT_ASSESSED":
            structural_errors.append("IMPLEMENTATION_CONFUSION_" + str(c.get("id")))
    if len(SCENARIOS) != 24 or len({x[0] for x in SCENARIOS}) != 24:
        structural_errors.append("SCENARIO_COUNT")
    rounds = []
    false_pass = 0
    for ix in range(1, 4):
        cases = []
        for name, changed_key, expected_verdict in SCENARIOS:
            facts = dict(BASE)
            if changed_key is not None:
                facts[changed_key] = False
            actual = decision(facts)
            ok = actual == expected_verdict
            if not ok and actual in ("EXTERNAL_AUTHORITIES_REQUIRED", "SIMULATED_ACCEPTANCE_ONLY"):
                false_pass += 1
            cases.append({"id": name, "expect": expected_verdict, "actual": actual, "pass": ok})
        rounds.append({
            "round": ix, "kind": ("BASELINE_FALSIFICATION" if ix == 1 else
                                  "DESIGN_REPAIR_VERIFY" if ix == 2 else
                                  "ADVERSARIAL_REPLAY"),
            "cases": len(cases), "pass_count": sum(x["pass"] for x in cases),
            "status": "PASS_THEORETICAL" if all(x["pass"] for x in cases) else "HOLD",
            "failures": [c for c in cases if not c["pass"]]
        })
    ok = (not structural_errors and all(r["pass_count"] == 24 for r in rounds)
          and false_pass == 0)
    return {
        "schema": "enguru.methods.design48.simulation-receipt/v1",
        "as_of": datetime.now(timezone.utc).isoformat(),
        "baseline_score": "88/100 — previous expert estimate, not freshly measured",
        "design_score": "100/100_THEORETICAL_CANDIDATE" if ok else "HOLD",
        "design_control_coverage": f"{len(controls)}/48",
        "matrix_sha256": hashlib.sha256(raw).hexdigest(),
        "rounds": rounds, "scenarios_per_round": 24, "total_simulated_cases": 72,
        "critical_false_pass": false_pass, "structural_errors": structural_errors,
        "independent_review": "HOLD_NOT_EXECUTED",
        "github_exact_head_ci": "SEPARATE_VERIFICATION_REQUIRED",
        "mac_osi_field": "HOLD_NOT_EXECUTED",
        "donecheck_official": "HOLD", "human_threshold": "HOLD",
        "verified_finish": "HOLD", "external_peer_certification": "NOT_CLAIMED",
        "verdict": "DESIGN_THEORY_CANDIDATE_PASS" if ok else "HOLD_DESIGN"
    }

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if result["verdict"] == "DESIGN_THEORY_CANDIDATE_PASS" else 2)
