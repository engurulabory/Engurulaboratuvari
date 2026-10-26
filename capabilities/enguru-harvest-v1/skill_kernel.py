"""ENGÜRÜ portable, standard-library skill kernel.

Twelve deterministic operations, no external code execution, no API requests,
no authority elevation. Script outputs are engineering evidence candidates only.
"""
import hashlib
import json
import math
import re
from pathlib import Path
from harvest import evaluate, _valid_https_url
from evidence_gate import validate

OPERATIONS = (
    "fingerprint", "source-url", "source-candidate", "catalog-check",
    "duplicate-check", "license-triage", "cost-bound", "prompt-audit",
    "readme-drift", "evidence-bytes", "paired-gain", "osi-handoff",
)

def result(state, reason, **extra):
    return dict(state=state, reason=reason, **extra)

def execute(operation, payload):
    if operation not in OPERATIONS or not isinstance(payload, dict):
        return result("HOLD", "INVALID_OPERATION_OR_INPUT")
    if operation == "fingerprint":
        value = payload.get("utf8_text")
        if not isinstance(value, str):
            return result("HOLD", "TEXT_REQUIRED")
        return result("DIGEST", "LOCAL_UTF8_BYTES_ONLY", sha256=hashlib.sha256(value.encode("utf-8")).hexdigest())
    if operation == "source-url":
        return result("CHECKED" if _valid_https_url(payload.get("url")) else "HOLD", "URL_FORMAT_ONLY")
    if operation == "source-candidate":
        return evaluate(payload.get("record"))
    if operation == "catalog-check":
        records=payload.get("candidates")
        if not isinstance(records,list) or len(records)!=30:
            return result("HOLD","EXPECTED_30_RECORDS")
        seen=set()
        libraries=set()
        for index,entry in enumerate(records,1):
            if not isinstance(entry,dict):
                return result("HOLD","INVALID_CATALOG_ENTRY")
            identifier="SRC-"+str(index).zfill(2)
            repo=entry.get("repository")
            url=entry.get("url")
            blob=entry.get("readme_git_blob_sha1")
            if entry.get("id")!=identifier or not isinstance(repo,str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repo):
                return result("HOLD","INVALID_ID_OR_REPO")
            if repo.casefold() in seen:
                return result("HOLD","DUPLICATE_REPO")
            seen.add(repo.casefold())
            if url!="https://github.com/"+repo or not isinstance(blob,str) or not re.fullmatch("[0-9a-f]{40}",blob):
                return result("HOLD","SOURCE_PROVENANCE_FORMAT")
            if entry.get("source_commit_sha") is not None or entry.get("source_archive_sha256") is not None:
                return result("HOLD","UNSUPPORTED_SOURCE_PIN_CLAIM")
            if entry.get("license")!="UNVERIFIED" or entry.get("security")!="PENDING" or entry.get("state")!="SOURCE_OBSERVED_ONLY":
                return result("HOLD","PREMATURE_ACCEPTANCE")
            library=entry.get("library")
            if not isinstance(library,str):
                return result("HOLD","INVALID_LIBRARY_TYPE")
            libraries.add(library)
        if not libraries.issubset(("skills","advanced_prompts","proven_sources","data_knowledge","engineering_recipes","evidence")):
            return result("HOLD","UNKNOWN_LIBRARY")
        return result("CATALOG_FORMAT_PASS","30_READMES_OBSERVED; NO_LICENSE_OR_SOURCE_ACCEPTANCE",count=30)
    if operation == "duplicate-check":
        ids=payload.get("identifiers")
        if not isinstance(ids,list) or not all(isinstance(x,str) and x for x in ids):
            return result("HOLD","INVALID_IDENTIFIERS")
        seen=set()
        repeated=set()
        for identifier in ids:
            if identifier in seen:
                repeated.add(identifier)
            else:
                seen.add(identifier)
        dup=sorted(repeated)
        return result("HOLD" if dup else "UNIQUE","DUPLICATES" if dup else "NO_DUPLICATES",duplicates=dup)
    if operation == "license-triage":
        value=payload.get("license_status")
        if value!="VERIFIED_WITH_PIN_AND_REVIEW":
            return result("HOLD","LICENSE_EVIDENCE_REQUIRED")
        if payload.get("review_receipt_verified") is not True:
            return result("HOLD","REVIEW_RECEIPT_REQUIRED")
        return result("REVIEW_CANDIDATE","LICENSE_REPORT_NEEDS_CANONICAL_VALIDATION")
    if operation == "cost-bound":
        count=payload.get("mandatory_paid_api")
        if type(count) is not int or count!=0:
            return result("HOLD","PAID_API_OR_UNKNOWN")
        if payload.get("compute_budget_recorded") is not True:
            return result("HOLD","LOCAL_RESOURCES_NOT_BUDGETED")
        return result("BUDGET_CONTRACT_PASS","ZERO_NEW_MANDATORY_PAID_API; HARDWARE_COSTS_EXCLUDED")
    if operation == "prompt-audit":
        obj=payload.get("prompt")
        fields=("state","claim","evidence","next_action")
        if not isinstance(obj,dict) or any(not isinstance(obj.get(x),str) or not obj[x].strip() for x in fields):
            return result("HOLD","MISSING_GOVERNANCE_FIELDS")
        return result("STRUCTURE_PASS","PROMPT_CONTENT_UNVERIFIED")
    if operation == "readme-drift":
        a=payload.get("recorded_git_blob_sha1")
        b=payload.get("observed_git_blob_sha1")
        if not all(isinstance(x,str) and re.fullmatch("[0-9a-f]{40}",x) for x in (a,b)):
            return result("HOLD","INVALID_GIT_BLOB_ID")
        return result("MATCH_RECORDED_README" if a==b else "HOLD", "LOCAL_BLOB_COMPARISON_ONLY" if a==b else "README_CHANGED")
    if operation == "evidence-bytes":
        assets=payload.get("assets")
        if not isinstance(assets,dict):
            return result("HOLD","MISSING_ASSETS")
        try:
            payload_bytes={key:bytes.fromhex(val) for key,val in assets.items() if isinstance(key,str) and isinstance(val,str)}
        except ValueError:
            return result("HOLD","INVALID_HEX_ASSETS")
        if len(payload_bytes)!=len(assets):
            return result("HOLD","INVALID_HEX_ASSETS")
        return validate(payload.get("manifest"),payload_bytes)
    if operation == "paired-gain":
        pairs=payload.get("paired_runs")
        if not isinstance(pairs,list) or len(pairs)<5:
            return result("HOLD","FIVE_PAIRED_RUNS_REQUIRED")
        task=None
        gains=[]
        for row in pairs:
            if not isinstance(row,dict):
                return result("HOLD","INVALID_RUN")
            if not isinstance(row.get("task_id"),str) or not row["task_id"]:
                return result("HOLD","TASK_ID_REQUIRED")
            if task is None:
                task=row["task_id"]
            if row["task_id"]!=task:
                return result("HOLD","UNMATCHED_TASKS")
            values=(row.get("baseline_seconds"),row.get("candidate_seconds"),row.get("baseline_quality"),row.get("candidate_quality"))
            if any(type(x) not in (int,float) or not math.isfinite(x) for x in values):
                return result("HOLD","INVALID_MEASUREMENTS")
            base_s,cand_s,base_q,cand_q=values
            if base_s<=0 or cand_s<=0 or not 0<=base_q<=100 or not 0<=cand_q<=100:
                return result("HOLD","INVALID_RANGE")
            if row.get("baseline_success") is not True or row.get("candidate_success") is not True or cand_q<base_q:
                return result("HOLD","SUCCESS_OR_QUALITY_REGRESSION")
            gains.append((base_s-cand_s)/base_s)
        average=sum(gains)/len(gains)
        if average<=0:
            return result("HOLD","NO_POSITIVE_TIME_GAIN")
        return result("MEASURED_GAIN_CANDIDATE","REQUIRES_REAL_PROVENANCE_AND_INDEPENDENT_REVIEW",paired_runs=len(gains),mean_relative_time_gain=round(average,4))
    if operation == "osi-handoff":
        if payload.get("osi_executed") is not False:
            return result("HOLD","OSI_EXECUTION_MUST_REMAIN_ZERO")
        required=("exact_head_ci_pass","independent_review_pass","canonical_pins_pass","three_real_sims_pass","proven_12_skills_pass")
        if any(payload.get(x) is not True for x in required):
            return result("HANDOFF_PREPARATION_ONLY","GITHUB_VERIFIED_FINISH_HOLD")
        return result("HANDOFF_CANDIDATE","HUMAN_THRESHOLD_AND_OSI_FIELD_STILL_REQUIRED")
    return result("HOLD","UNKNOWN_OPERATION")

if __name__ == "__main__":
    import sys
    if len(sys.argv)!=3 or sys.argv[1] not in OPERATIONS:
        raise SystemExit("usage: skill_kernel.py <operation> <json-file>")
    payload=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    print(json.dumps(execute(sys.argv[1],payload),ensure_ascii=False,sort_keys=True))
