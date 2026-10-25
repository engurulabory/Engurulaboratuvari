#!/usr/bin/env python3
"""ENGURU Design48 v2: frozen independently recomputed design-contract rubric.

Only synthetic positive/negative/missing mock cases. NOT a product, OSi,
international certification, independent human review, or DoneCheck acceptance.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "governance/enguru-suzgeci/ENGURU_TASARIM_48_KONTROL_MATRISI_V1.json"
FIXTURES = ROOT / "governance/enguru-suzgeci/ENGURU_TASARIM_48_ORACLE_FIXTURES_V2.json"
EXPECTED = json.loads(r'''{"D01":["user_outcome","measurable_benefit","vague_benefit","NIST_AI_RMF"],"D02":["goal_scope","single_measurable_goal","competing_goals","DORA"],"D03":["locked_decisions","version_pinned","silently_changed","SLSA"],"D04":["impact_baseline","baseline_with_observation","claim_without_baseline","GOOGLE_SRE"],"D05":["suzgec_phases","eight_stages_preserved","missing_stages","NIST_AI_RMF"],"D06":["acceptance_gates","k1_to_k8_nested","new_untrusted_authority","NIST_SSDF"],"D07":["stop_decision","evidence_bounded","auto_advance_without_proof","NIST_AI_RMF"],"D08":["language_contract","state_claim_evidence_next","unsupported_pass","ANTHROPIC_EVALS"],"D09":["control_execution_planes","producer_verifier_owner_separate","same_authority_everywhere","SLSA"],"D10":["reuse_priority","reuse_extend_adapter_first","duplicate_core","NIST_SSDF"],"D11":["capability_scope","least_privilege_per_task","cross_product_grant","OPENSSF"],"D12":["integration_handshake","schema_timeout_authority","unspecified_adapter","LANGGRAPH"],"D13":["v3_lock","canonical_sha_match","unverified_digest","SLSA"],"D14":["head_freshness","exact_head_provenance","stale_branch","SLSA"],"D15":["naming_governance","single_canonical_term","drifted_names","NIST_AI_RMF"],"D16":["repo_reconciliation","explicit_repo_coverage","unexamined_repos_counted","OPENSSF"],"D17":["acceptance_matrix","ids_verifiers_and_evidence","unowned_conditions","ANTHROPIC_EVALS"],"D18":["dependency_graph","acyclic_with_external_gates","hidden_cycle","DORA"],"D19":["work_blocks","dependency_preserving_batches","double_counted_evidence","DORA"],"D20":["session_handoff","source_pinned_continuity","memory_overrides_head","LANGGRAPH"],"D21":["preflight_scenarios","happy_negative_disruption","happy_path_only","ANTHROPIC_EVALS"],"D22":["simulation_rounds","three_fixed_denominator","inflated_round_score","ANTHROPIC_EVALS"],"D23":["root_cause_standard","evidence_before_remediation","hypothesis_promoted","NIST_SSDF"],"D24":["scenario_oracle","expected_and_forbidden_verdict","test_without_oracle","ANTHROPIC_EVALS"],"D25":["git_change_control","scoped_pr_ci_exact_head","commit_called_merge","SLSA"],"D26":["runtime_observation","real_executor_receipt","design_claim_as_run","DORA"],"D27":["github_osi_binding","artifact_and_native_proof","ci_as_osi_proof","SLSA"],"D28":["automated_loop","bounded_and_checkpointed","unauthorized_autonomy","LANGGRAPH"],"D29":["regression_suite","golden_and_regression","unexecuted_test_pass","ANTHROPIC_EVALS"],"D30":["security_negatives","prompt_secret_negative_tests","unsafe_fixture_pass","NIST_SSDF"],"D31":["ci_evidence","run_sha_and_conclusion","green_different_commit","OPENSSF"],"D32":["review_independence","different_reviewer_identity","producer_self_approval","ANTHROPIC_EVALS"],"D33":["evidence_claim_binding","claim_tied_to_observation","llm_claim_only","ANTHROPIC_EVALS"],"D34":["build_provenance","builder_source_artifact_chain","hash_without_builder","SLSA"],"D35":["independent_recheck","second_method_and_freshness","duplicate_receipt_as_review","SLSA"],"D36":["finish_accounting","execution_evidence_authority","simulation_as_finish","NIST_AI_RMF"],"D37":["privacy_boundary","classified_secret_egress","private_to_public","NIST_SSDF"],"D38":["human_authority","scoped_signer_review","chat_ack_as_signature","NIST_AI_RMF"],"D39":["fail_closed","hold_or_blocked_on_unknown","unknown_as_pass","OPENSSF"],"D40":["cost_guard","budget_before_paid_action","unapproved_spend","DORA"],"D41":["durable_checkpoint","task_id_and_fingerprint","lost_state_after_restart","LANGGRAPH"],"D42":["idempotent_replay","single_effect_per_fingerprint","duplicate_side_effect","LANGGRAPH"],"D43":["schedule_observability","timestamps_not_only_cron","cron_claim_as_proof","GOOGLE_SRE"],"D44":["recovery_acceptance","restart_and_rollback_receipts","restart_claim_only","GOOGLE_SRE"],"D45":["atlas_traceability","source_linked_single_index","unlinked_canonical_claim","SLSA"],"D46":["human_friction","single_clear_next_action","manual_every_step","GOOGLE_SRE"],"D47":["impact_metrics","baseline_leadtime_rework","percent_gain_without_data","DORA"],"D48":["verified_service","real_delivery_and_acceptance","report_as_product_finish","ANTHROPIC_EVALS"]}''')
PEERS = json.loads(r'''{"NIST_AI_RMF":"https://airc.nist.gov/airmf-resources/playbook/","NIST_SSDF":"https://csrc.nist.gov/pubs/sp/800/218/final","DORA":"https://dora.dev/guides/dora-metrics/","SLSA":"https://slsa.dev/spec/v1.2/provenance","OPENSSF":"https://openssf.org/projects/scorecard/","LANGGRAPH":"https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/persistence.mdx","ANTHROPIC_EVALS":"https://www.anthropic.com/research/demystifying-evals-for-ai-agents","GOOGLE_SRE":"https://sre.google/workbook/implementing-slos/"}''')
BASELINE = [5,5,4,4,5,5,5,4,5,4,5,4,5,4,4,4,5,5,4,4,5,5,4,4,4,4,4,3,4,5,4,4,5,5,5,4,5,5,4,5,4,5,4,4,4,4,4,4]
V3_PIN = "11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc"
CONTROL_IDS = [f"D{i:02}" for i in range(1, 49)]

def decision(identifier, sample):
    """Frozen grader: values come from EXPECTED, not the subject matrix/fixtures."""
    if identifier not in EXPECTED or type(sample) is not dict:
        return "HOLD_DESIGN_CASE"
    key, positive, _, _ = EXPECTED[identifier]
    if set(sample) != {key} or type(sample[key]) is not str:
        return "HOLD_DESIGN_CASE"
    return "DESIGN_CASE_PASS_ONLY" if sample[key] == positive else "HOLD_DESIGN_CASE"

def score_one(c, fixture, index):
    identifier = CONTROL_IDS[index]
    signal, positive, negative, peer_id = EXPECTED[identifier]
    checks = {}
    checks["identity"] = (
        c.get("id") == identifier and
        c.get("area_id") == f"A{index//4+1:02}" and
        c.get("baseline_design_points") == BASELINE[index] and
        c.get("criterion") and c.get("design_status") == "SPECIFIED")
    source = c.get("canonical_source")
    checks["contract"] = (
        isinstance(c.get("pass_design_condition"), str)
        and len(c["pass_design_condition"].strip()) >= 24
        and isinstance(c.get("reject_case"), str)
        and any(w in c["reject_case"] for w in ("HOLD", "BLOCKED"))
        and isinstance(source, str)
        and source.startswith("governance/")
        and (ROOT / source).is_file()
        and c.get("implementation_state") == "NOT_ASSESSED"
        and c.get("real_field_state") == "NOT_ASSESSED")
    binding = c.get("oracle_binding") or {}
    fixture_ok = (
        fixture.get("control_id") == identifier
        and fixture.get("case_id") == f"ORACLE_{identifier}"
        and binding.get("case_id") == fixture.get("case_id")
        and binding.get("fixture_ref") == str(FIXTURES.relative_to(ROOT))
        and binding.get("input_key") == signal
        and binding.get("expected_design_value") == positive
        and binding.get("negative_value") == negative
        and fixture.get("input_key") == signal
        and fixture.get("positive") == {signal: positive}
        and fixture.get("negative") == {signal: negative}
        and fixture.get("missing") == {}
        and fixture.get("expect_positive") == "DESIGN_CASE_PASS_ONLY"
        and fixture.get("expect_negative") == "HOLD_DESIGN_CASE"
        and fixture.get("expect_missing") == "HOLD_DESIGN_CASE")
    checks["golden_oracle"] = bool(fixture_ok and
        decision(identifier, fixture["positive"]) == "DESIGN_CASE_PASS_ONLY")
    checks["adversarial_oracle"] = bool(fixture_ok and
        decision(identifier, fixture["negative"]) == "HOLD_DESIGN_CASE"
        and decision(identifier, fixture["missing"]) == "HOLD_DESIGN_CASE"
        and decision(identifier, {signal: "false"}) == "HOLD_DESIGN_CASE"
            if positive != "false" else fixture_ok)
    peer = c.get("peer_evidence") or {}
    checks["peer_provenance"] = (
        peer.get("source_id") == peer_id and
        peer.get("url") == PEERS[peer_id] and
        peer.get("source_section") and
        peer.get("source_title") and
        isinstance(peer.get("mechanism"), str) and len(peer["mechanism"]) >= 3 and
        isinstance(peer.get("design_transfer_rationale"), str) and
        len(peer["design_transfer_rationale"].strip()) >= 16 and
        peer.get("claim_type") == "METHODOLOGICAL_ANALOGY_NOT_CERTIFICATION")
    return {k:bool(v) for k,v in checks.items()}

def audit(matrix, registry):
    controls=matrix.get("controls")
    fixtures=registry.get("fixtures")
    if type(controls) is not list or type(fixtures) is not list:
        return {"error":"INVALID_TYPE","score":0}
    if (len(controls)!=48 or len(fixtures)!=48 or
        [c.get("id") for c in controls]!=CONTROL_IDS or
        [f.get("control_id") for f in fixtures]!=CONTROL_IDS or
        len(matrix.get("areas",[]))!=12 or
        matrix.get("canonical_v3_sha256") != V3_PIN or
        matrix.get("baseline_20261024",{}).get("raw_points")!=211):
        return {"error":"CANONICAL_BOUNDARY","score":0}
    results=[]
    for i,(c,fx) in enumerate(zip(controls,fixtures)):
        checks=score_one(c,fx,i)
        results.append({"control":CONTROL_IDS[i],"checks":checks,
                        "derived_points":sum(checks.values())})
    raw=sum(r["derived_points"] for r in results)
    return {"raw":raw,"max":240,"score":round(raw*100/240,4),
            "control_count":48,"results":results,
            "every_control_5":all(r["derived_points"]==5 for r in results)}

def mutate_test(matrix,registry):
    """Adversarial proof the grader rejects damaged oracles/peers.
    Candidate-design points are explicitly EXCLUDED from all scoring functions.
    """
    problems=[]
    for i in range(48):
        bad=copy.deepcopy(registry)
        k=EXPECTED[CONTROL_IDS[i]][0]
        bad["fixtures"][i]["positive"][k]="invalid-mutated-evidence"
        r=audit(matrix,bad)
        if r.get("raw",240)>=240:
            problems.append(f"ORACLE_TAMPER_{i+1:02}")
        bad=copy.deepcopy(matrix)
        bad["controls"][i]["peer_evidence"]["url"]="https://invalid.example/peer"
        r=audit(bad,registry)
        if r.get("raw",240)>=240:
            problems.append(f"PEER_TAMPER_{i+1:02}")
        bad=copy.deepcopy(matrix)
        bad["controls"][i]["oracle_binding"]["expected_design_value"]="forged"
        r=audit(bad,registry)
        if r.get("raw",240)>=240:
            problems.append(f"BINDING_TAMPER_{i+1:02}")
    scored=copy.deepcopy(matrix)
    for c in scored["controls"]:
        c["candidate_design_points"]=0
    if audit(scored,registry).get("raw")!=audit(matrix,registry).get("raw"):
        problems.append("SELF_REPORTED_POINTS_AFFECT_DERIVED_SCORE")
    return {"attempts":48*3+1,"correctly_rejected_or_score_invariant":48*3+1-len(problems),"errors":problems}

def main():
    matrix_bytes=MATRIX.read_bytes()
    fixture_bytes=FIXTURES.read_bytes()
    matrix=json.loads(matrix_bytes)
    registry=json.loads(fixture_bytes)
    rounds=[]
    for i in range(1,4):
        r=audit(matrix,registry)
        t=mutate_test(matrix,registry)
        rounds.append({"round":i,"raw_points":r.get("raw",0),
                       "max_points":240,"derived_score":r["score"],
                       "per_control_golden":48 if r["every_control_5"] else
                           sum(bool(x["checks"]["golden_oracle"]) for x in r["results"]),
                       "per_control_adversarial":sum(
                           bool(x["checks"]["adversarial_oracle"]) for x in r["results"]),
                       "crosswalk_verified":sum(
                           bool(x["checks"]["peer_provenance"]) for x in r["results"]),
                       "mutation_checks":t["correctly_rejected_or_score_invariant"],
                       "mutation_total":t["attempts"],"errors":t["errors"]})
    ok=all(x["raw_points"]==240 and x["per_control_golden"]==48
           and x["per_control_adversarial"]==48 and x["crosswalk_verified"]==48
           and x["mutation_checks"]==145 and not x["errors"] for x in rounds)
    receipt={"schema":"enguru.methods.design48.hardening/v2",
             "verdict":"PASS_THEORETICAL_DESIGN_48" if ok else "HOLD_DESIGN",
             "derived_score":"100/100_THEORETICAL" if ok else "HOLD",
             "matrix_sha256":hashlib.sha256(matrix_bytes).hexdigest(),
             "oracles_sha256":hashlib.sha256(fixture_bytes).hexdigest(),
             "rounds":rounds,
             "per_control_oracle_assertions":48*3*3,
             "matrix_mutation_attempts":145*3,
             "source_verification":"PEER_URL_CATALOG_VERIFIED_EXTERNALLY_NOT_CERTIFICATION",
             "self_reported_candidate_points_used":False,
             "official_donecheck":"HOLD","independent_human_review":"HOLD",
             "mac_osi_field":"HOLD","verified_finish":"HOLD"}
    print(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True))
    return 0 if ok else 2

if __name__=="__main__":
    raise SystemExit(main())
