"""Conservative registry reconciliation. No legal or source-code authorization."""
import re
from pathlib import Path
import json

def check(candidates,observations):
    if not isinstance(candidates,dict) or not isinstance(observations,dict):
        return {"state":"HOLD","reason":"INVALID_INPUT"}
    records=candidates.get("candidates")
    found=observations.get("observations")
    if not isinstance(records,list) or len(records)!=30 or not isinstance(found,list) or len(found)!=30:
        return {"state":"HOLD","reason":"EXPECTED_30_EACH"}
    source={}
    for row in records:
        if not isinstance(row,dict) or not isinstance(row.get("repository"),str) or row["repository"] in source:
            return {"state":"HOLD","reason":"INVALID_SOURCE_REGISTRY"}
        source[row["repository"]]=row
    reviewed=set()
    observed=0
    missing=[]
    for row in found:
        if not isinstance(row,dict):
            return {"state":"HOLD","reason":"INVALID_LICENSE_RECORD"}
        name=row.get("repository")
        if not isinstance(name,str) or name not in source or name in reviewed:
            return {"state":"HOLD","reason":"MISALIGNED_OR_DUPLICATED_REPOSITORY"}
        reviewed.add(name)
        if row.get("state")!="ROOT_LICENSE_TEXT_OBSERVED_ONLY" or row.get("redistribution_approval")!="HOLD" or row.get("source_sha256")!="UNVERIFIED" or source[name].get("license")!="UNVERIFIED":
            return {"state":"HOLD","reason":"PREMATURE_LEGAL_APPROVAL"}
        path=row.get("path")
        sha=row.get("git_blob_sha1")
        if path is None and sha is None:
            if row.get("content_signal")!="ROOT_LICENSE_NOT_FOUND":
                return {"state":"HOLD","reason":"UNKNOWN_MISSING_LICENSE"}
            missing.append(name)
            continue
        if path not in ("LICENSE","LICENSE.md","LICENSE.txt","LICENSE-MIT") or not isinstance(sha,str) or re.fullmatch("[0-9a-f]{40}",sha) is None:
            return {"state":"HOLD","reason":"INVALID_LICENSE_BLOB"}
        if not isinstance(row.get("content_signal"),str) or not row["content_signal"]:
            return {"state":"HOLD","reason":"MISSING_LICENSE_TEXT_SIGNAL"}
        observed+=1
    if reviewed!=set(source):
        return {"state":"HOLD","reason":"REPOSITORY_SET_MISMATCH"}
    return {"state":"LICENSE_OBSERVATION_PASS","reason":"ROOT_FILE_IDENTITIES_ONLY; ALL_REDISTRIBUTION_APPROVALS_HOLD",
            "total":30,"root_files_observed":observed,"missing_root_files":missing,"approved_for_reuse":0}

if __name__=="__main__":
    root=Path(__file__).resolve().parent
    a=json.loads((root/"source_candidates.json").read_text(encoding="utf-8"))
    b=json.loads((root/"root_license_observations.json").read_text(encoding="utf-8"))
    response=check(a,b)
    print(json.dumps(response,sort_keys=True,ensure_ascii=False))
    if response["state"]!="LICENSE_OBSERVATION_PASS":
        raise SystemExit(1)
