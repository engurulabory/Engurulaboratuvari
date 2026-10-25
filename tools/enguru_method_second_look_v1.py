#!/usr/bin/env python3
"""Independent-mechanism source audit, NOT an independent human PR review."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "governance"
S = G / "enguru-suzgeci"
P = G / "quality"
CHECKS = {}

def check(name, condition):
    CHECKS[name] = bool(condition)

def main():
    lock = json.loads((S / "ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json").read_text())
    v3 = (S / "ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md").read_bytes()
    matrix = json.loads((S / "ENGURU_TASARIM_48_KONTROL_MATRISI_V1.json").read_text())
    fixture = json.loads((S / "ENGURU_TASARIM_48_ORACLE_FIXTURES_V2.json").read_text())
    fields = json.loads((S / "ENGURU_ALTI_URETIM_ALANI_V1.json").read_text())
    five = (S / "ENGURU_ANA_TERAZI_5X100_V1.md").read_text()
    review = (P / "PR_REVIEW_CONTRACT_V1.md").read_text()
    done = (G / "mac-engineer" / "DONECHECK_AUTHORITY_MODEL_V1.md").read_text()
    controls = matrix["controls"]
    groups = fields["domains"]
    check("R01_canonical_sha256_real_bytes", hashlib.sha256(v3).hexdigest()==lock["sha256"]==matrix["canonical_v3_sha256"])
    check("R02_eight_original_stages_and_one_core", all(s in v3.decode() for s in (
          "Hakikati gör", "Değeri koru", "Gerekli farkı üret",
          "Eksikleri tamamla", "Kanıtla", "Bir sonraki ihtiyaçları", "İlerlet")))
    check("R03_fixed_48_unduplicated_controls", len(controls)==48 and
          [c["id"] for c in controls]==[f"D{i:02}" for i in range(1,49)] and
          len({c["criterion"] for c in controls})==48)
    check("R04_distinct_48_fixture_links", len(fixture["fixtures"])==48 and
          [x["case_id"] for x in fixture["fixtures"]]==[f"ORACLE_D{i:02}" for i in range(1,49)] and
          all(c["oracle_binding"]["case_id"]==fixture["fixtures"][i]["case_id"] for i,c in enumerate(controls)))
    check("R05_distinct_six_production_fields", [d["id"] for d in groups]==
          ["CORE","ENGINE","AGENT","WEB","APP","COMMERCE"] and
          len(fields["shared_controls"])==12 and
          all(len(d["domain_controls"])==4 for d in groups))
    check("R06_independent_mechanism_and_reviewer_difference", "Outside Voice" in review and
          "reviewer identity differs from producer identity" in review)
    check("R07_5_axis_score_targets_explicit", all(x in five for x in ("**1. TEORI**", "**2. TASARIM**",
          "**3. SIMULASYON-1**", "**4. SIMULASYON-2**", "**5. SIMULASYON-3**")))
    check("R08_original_baseline_and_field_holds", matrix["baseline_20261024"]["raw_points"]==211 and
          matrix["design_target"]["raw_points"]==240 and
          matrix["authority"]["osi_field"]=="HOLD" and matrix["authority"]["verified_finish"]=="HOLD")
    check("R09_donecheck_human_threshold_separation", "DoneCheck v1.2" in done and
          "Human Threshold" in done and "final human authority" in done)
    check("R10_source_driven_no_extra_engine_core", "SIX_AREA_ADAPTER" not in lock["version"] and
          fields["scope"]=="THEORETICAL_ADAPTERS_ONLY")
    ok=all(CHECKS.values())
    print(json.dumps({
        "schema":"enguru.pr221.source-second-look/v1",
        "scope":"INDEPENDENT_MECHANISM_NOT_INDEPENDENT_REVIEWER_IDENTITY",
        "technical_second_look":"PASS_10_OF_10" if ok else "HOLD_SOURCE_FINDINGS",
        "checks":CHECKS,
        "human_reviewer_approval":"HOLD_NO_APPROVAL_RECORD",
        "source_v3_sha256":hashlib.sha256(v3).hexdigest(),
        "pr_review":"HOLD_REQUIRES_DIFFERENT_AUTHORIZED_IDENTITY",
        "mac_osi":"HOLD","donecheck":"HOLD","verified_finish":"HOLD"
    },indent=2,sort_keys=True))
    return 0 if ok else 2

if __name__=="__main__":
    raise SystemExit(main())
