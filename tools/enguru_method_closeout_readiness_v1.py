#!/usr/bin/env python3
"""Non-authoritative stages 2-4 readiness; never calls official DoneCheck."""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOCK=ROOT/"governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json"
V3=ROOT/"governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md"

def main(paths):
    second, pilot, balance, six=[json.loads(Path(x).read_text()) for x in paths]
    lock=json.loads(LOCK.read_text())
    sig=hashlib.sha256(V3.read_bytes()).hexdigest()
    checks={
        "source_v3_pin":sig==lock["sha256"]==second["source_v3_sha256"],
        "technical_source_second_look":second["technical_second_look"]=="PASS_10_OF_10",
        "theoretical_5x100":balance["verdict"]=="PASS_THEORETICAL_PREPARATION_5X100"
            and len(balance["scores"])==5 and all(v==100 for v in balance["scores"].values()),
        "six_adapters_design":six["verdict"]=="PASS_6_AREAS_3_ROUND_DESIGN" and six["production_areas"]==6,
        "real_github_runtime_pilot":pilot["status"]=="PASS_GITHUB_REAL_ENGINE_PILOT" and pilot["passed"]==6,
        "distinct_mechanical_verifier":pilot["independent_verification_mechanism"]=="SEPARATE_EXECUTABLE_SAME_PRODUCER_TEAM",
        "reviewer_identity_reserved":second["human_reviewer_approval"]=="HOLD_NO_APPROVAL_RECORD",
        "osi_field_reserved":pilot["native_mac_osi_field"]=="HOLD",
        "donecheck_reserved":pilot["donecheck_v12"]=="HOLD",
        "human_threshold_reserved":pilot["human_threshold"]=="HOLD",
        "verified_finish_reserved":pilot["verified_finish"]=="HOLD"
    }
    ok=all(checks.values())
    out={
        "schema":"enguru.method.stages234.closeout-readiness/v1",
        "verdict":"PASS_READINESS_EVIDENCE_OFFICIAL_HOLD" if ok else "HOLD_EVIDENCE_CONFLICT",
        "identity":"NON_AUTHORITY_SOURCE_AUDIT_AND_GITHUB_RUNTIME_RECEIPT",
        "checks":checks,
        "stage_1_theoretical":"PASS_5X100",
        "stage_2":{"technical_second_mechanism":"PASS" if checks["technical_source_second_look"] else "HOLD",
                   "independent_human_design_review":"HOLD_DIFFERENT_AUTHORIZED_REVIEWER_REQUIRED",
                   "official_state":"HOLD"},
        "stage_3":{"real_github_engine_pilot":"PASS" if checks["real_github_runtime_pilot"] else "HOLD",
                   "mac_osi_native_field":"HOLD_REAL_MAC_SESSION_AND_EVIDENCE_REQUIRED",
                   "real_per_product_user_consent":"HOLD_REAL_CO_DESIGN_CASE_REQUIRED",
                   "official_state":"HOLD"},
        "stage_4":{"evidence_readiness":"PASS_PRODUCER_EVIDENCE_ONLY" if ok else "HOLD",
                   "donecheck_v12":"HOLD_CANONICAL_MACHINE_AUTHORITY",
                   "human_threshold":"HOLD_OWNER_APPROVAL_REQUIRED",
                   "verified_finish":"HOLD"},
        "exact_main_merge":"HOLD_UNMERGED_PR_221_READY_FOR_REVIEW",
        "immutable_authority":"DONECHECK_V12_AND_HUMAN_THRESHOLD",
        "next_actions":[
            "Independent reviewer with different authorized identity submits actual GitHub PR review",
            "User and engineer select real CORE/ENGINE/AGENT/WEB/APP/COMMERCE case and capture first-design decision",
            "Authorized Mac OSi executor performs signed/pinned real local commissioning and evidence",
            "Merge only under existing required GitHub branch protections and owner approval",
            "Canonical DoneCheck v1.2 + required Human Threshold issue official acceptance and ledger"
        ]
    }
    print(json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True))
    return 0 if ok else 2

if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("usage: script SECOND_LOOK PILOT BALANCE SIX_DOMAIN_RECEIPT")
    raise SystemExit(main(sys.argv[1:]))
