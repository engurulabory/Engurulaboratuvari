"""K02: prove all 30 candidate sources remain quarantined by default.

README blob and root LICENSE blob identity give observation, not a source
archive SHA-256, legal opinion, paid API entitlement, security or user consent.
"""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def reconcile(candidates,licenses):
    if not isinstance(candidates,dict) or not isinstance(licenses,dict):
        return {"state":"HOLD","reason":"INVALID_INPUT"}
    source=candidates.get("candidates")
    legal=licenses.get("observations")
    if not isinstance(source,list) or len(source)!=30 or not isinstance(legal,list) or len(legal)!=30:
        return {"state":"HOLD","reason":"EXPECTED_30"}
    lookup={}
    for rec in legal:
        if not isinstance(rec,dict) or not isinstance(rec.get("repository"),str) or rec["repository"] in lookup:
            return {"state":"HOLD","reason":"BAD_LICENSE_REGISTRY"}
        lookup[rec["repository"]]=rec
    classifications=[]
    for rec in source:
        if not isinstance(rec,dict) or not isinstance(rec.get("repository"),str):
            return {"state":"HOLD","reason":"BAD_SOURCE_ROW"}
        lic=lookup.get(rec["repository"])
        if lic is None:
            return {"state":"HOLD","reason":"MISSING_LICENSE_ROW"}
        if (rec.get("license")!="UNVERIFIED" or rec.get("security")!="PENDING" or
            rec.get("source_archive_sha256") is not None or rec.get("source_commit_sha") is not None or
            lic.get("redistribution_approval")!="HOLD" or
            lic.get("state")!="ROOT_LICENSE_TEXT_OBSERVED_ONLY"):
            return {"state":"HOLD","reason":"PREMATURE_SOURCE_ADOPTION"}
        classifications.append({
            "id":rec["id"],"repository":rec["repository"],
            "source_state":"OBSERVED_QUARANTINE",
            "license_review":"HOLD",
            "security_review":"HOLD",
            "mandatory_paid_api":"NOT_EVALUATED",
            "real_source_sha256":"MISSING",
            "redistribution":"HOLD"
        })
    if len({r["repository"] for r in classifications})!=30 or len(lookup)!=30:
        return {"state":"HOLD","reason":"DUPLICATE_OR_MISSING"}
    return {"state":"PASS_SAFE_QUARANTINE","observed":30,"proven":0,
            "licensed_for_adoption":0,"mandatory_paid_api_approved":0,
            "records":classifications}

if __name__=="__main__":
    src=json.loads((HERE/"source_candidates.json").read_text(encoding="utf-8"))
    legal=json.loads((HERE/"root_license_observations.json").read_text(encoding="utf-8"))
    out=reconcile(src,legal)
    (HERE/"k02-source-quarantine-receipt.json").write_text(
        json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k!="records"},ensure_ascii=False))
    if out["state"]!="PASS_SAFE_QUARANTINE":
        raise SystemExit(1)
