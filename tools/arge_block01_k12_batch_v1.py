"""A08 / K12: inspect all 18 canonical cases, never issue an official verdict.

Read-only intake for authentic five-year baseline/candidate evidence. Public-source
testimonials and numeric examples do not establish real customer costs or E5.
"""
import argparse
import json
from pathlib import Path
from tools.arge_block01_k12_tco_v1 import compare_five_year_tco

V19_SHA = "3906f7bd6ae07d26547babc172d1337cfdfeff85244ece95efb76c3cb448df08"
REVIEW = "CALCULATION_ONLY_NEEDS_INDEPENDENT_REVIEW"
# Independently fixed from original V19 case roster; catalog cannot redefine identities.
ORIGINAL_V19_IDENTITIES = (
    ("01", "Bookshop.org", "Meilisearch"),
    ("02", "Matt Sleeps", "Medusa"),
    ("03", "Lush", "Saleor"),
    ("04", "Mobbin", "Supabase"),
    ("05", "Resend", "Supabase"),
    ("06", "Hugging Face Hub", "Meilisearch"),
    ("07", "Replit Agent", "Temporal"),
    ("08", "Auth0 FGA", "OpenFGA"),
    ("09", "Headspace", "OpenFGA"),
    ("10", "Xendit", "Supabase"),
    ("11", "Mapped", "OpenFGA"),
    ("12", "Temporal Cloud", "Temporal"),
    ("13", "Klarna", "LangGraph"),
    ("14", "LinkedIn", "LangGraph"),
    ("15", "Uber", "LangGraph"),
    ("16", "Tekla", "Medusa"),
    ("17", "Fastweb + Vodafone", "LangGraph"),
    ("18", "BFI Finance", "Temporal"),
)


def audit_k12_batch(catalog, evidence):
    """Fail closed on missing/duplicated/changed cases; preserve real approval gates."""
    if not isinstance(catalog, dict) or not isinstance(evidence, dict):
        return {"state": "HOLD_FORMAT"}
    base = catalog.get("baseline")
    cases = catalog.get("cases")
    if not isinstance(base, dict) or base.get("sha256") != V19_SHA or base.get("rows") != 234:
        return {"state": "HOLD_CANONICAL_BASELINE"}
    if not isinstance(cases, list) or len(cases) != 18 or any(not isinstance(c, dict) for c in cases):
        return {"state": "HOLD_CANONICAL_CASES"}
    ids = [c.get("case_id") for c in cases]
    if any(not isinstance(cid, str) for cid in ids) or sorted(ids) != [f"{i:02d}" for i in range(1, 19)]:
        return {"state": "HOLD_CANONICAL_IDENTITIES"}
    if tuple((c.get("case_id"), c.get("customer"), c.get("technology")) for c in cases) != ORIGINAL_V19_IDENTITIES:
        return {"state": "HOLD_CANONICAL_IDENTITIES"}

    provided = evidence.get("cases")
    if not isinstance(provided, list) or any(not isinstance(c, dict) for c in provided):
        return {"state": "HOLD_INPUT_FORMAT"}
    input_ids = [c.get("case_id") for c in provided]
    if (len(provided) != 18 or any(not isinstance(cid, str) for cid in input_ids)
            or sorted(input_ids) != sorted(ids) or len(set(input_ids)) != 18):
        return {"state": "HOLD_18_CASE_SCOPE", "expected": 18, "received": len(provided)}
    by_id = {c["case_id"]: c for c in provided}
    out = []
    for original in cases:
        cid = original["case_id"]
        current = by_id[cid]
        if current.get("customer") != original["customer"] or current.get("technology") != original["technology"]:
            out.append({"case_id": cid, "state": "HOLD_CUSTOMER_TECH_IDENTITY"})
            continue
        baseline, candidate = current.get("baseline"), current.get("candidate")
        if not isinstance(baseline, dict) or not isinstance(candidate, dict):
            out.append({"case_id": cid, "state": "HOLD_COST_INPUT"})
            continue
        result = compare_five_year_tco(baseline, candidate)
        # The calculator's source_ref is a pointer, not a retrieved/verified document.
        # There is deliberately no PASS_VERIFIED or receipt output in this module.
        out.append({"case_id": cid, **result})
    ready = sum(c["state"] == REVIEW for c in out)
    return {
        "state": "CALCULATIONS_REVIEW_REQUIRED" if ready == 18 else "HOLD_K12_SOURCE_OR_COMPARABILITY",
        "case_count": 18,
        "calculable_unverified": ready,
        "actual_measured_tco_independently_verified": 0,
        "official_pass": 0,
        "cases": out,
    }

def main():
    p = argparse.ArgumentParser(description="Read-only, untrusted-source K12 intake")
    p.add_argument("--catalog", required=True, type=Path)
    p.add_argument("--evidence", required=True, type=Path)
    args = p.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
        result = audit_k12_batch(catalog, evidence)
    except (OSError, ValueError, UnicodeError) as exc:
        result = {"state": "HOLD_FILE_OR_JSON", "error_type": type(exc).__name__}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    # Even 18/18 illustrative calculations are unreviewed: reserve success for
    # the separate canonical acceptance mechanism, never for this CLI.
    return 3 if result.get("state") == "CALCULATIONS_REVIEW_REQUIRED" else 2

if __name__ == "__main__":
    raise SystemExit(main())
