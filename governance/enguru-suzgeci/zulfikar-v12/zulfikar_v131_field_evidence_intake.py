#!/usr/bin/env python3
"""Zulfikar 1.3.1 read-only evidence bytes and claims reconciliation.

This is NOT an owner signature check, runtime execution, or DoneCheck. A SHA
matches bytes; it does NOT prove that the described task actually happened.
Private Mac receipts remain local and are never uploaded by this tool.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

from zulfikar_v131_operational_bridge import read_no_symlink

SCHEMA="enguru.zulfikar.field-evidence-bundle/v1"
RECEIPT_SCHEMA="enguru.zulfikar.external-task-observation/v1"
SHA256=re.compile(r"^[a-f0-9]{64}$")
SHA40=re.compile(r"^[a-f0-9]{40}$")
IDENTITY=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:_-]{0,127}$")
FAMILIES=frozenset({"NATIVE_SWIFTUI_PRODUCT","LOCAL_RECOVERY_IDEMPOTENCY","WEB_BUILD_TEST_REPAIR"})
MAX_MANIFEST=120_000
MAX_RECEIPT=1_000_000


def no_duplicates(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key]=value
    return result


def load_json(data:bytes):
    return json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicates,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))


def sha256(data:bytes):
    return hashlib.sha256(data).hexdigest()


def format_receipt(record,plan):
    """Screen self-asserted facts against task identity. No remote validation."""
    if not isinstance(record,dict):
        return ["RECEIPT_NOT_OBJECT"]
    errors=[]
    for key in ("taskId","workId","sourceRepo","registeredHandler","contractId"):
        if not isinstance(record.get(key),str) or not IDENTITY.fullmatch(record[key]):
            errors.append("INVALID_"+key.upper())
    if record.get("taskId")!=plan.get("taskId"):
        errors.append("TASK_ID_MISMATCH")
    if record.get("family")!=plan.get("family"):
        errors.append("FAMILY_MISMATCH")
    if record.get("sourceHead")!=plan.get("sourceHead") or not isinstance(record.get("sourceHead"),str) or not SHA40.fullmatch(record["sourceHead"]):
        errors.append("SOURCE_HEAD_MISMATCH")
    for key in ("preStateSha256","postStateSha256","actualOutputDigest"):
        if not isinstance(record.get(key),str) or not SHA256.fullmatch(record[key]):
            errors.append("INVALID_"+key.upper())
    if record.get("claimedTaskExecuted") is not True:
        errors.append("NO_EXECUTION_CLAIM")
    if record.get("testReturnCode") != 0 or type(record.get("testReturnCode")) is not int:
        errors.append("NO_TEST_EXIT_ZERO_CLAIM")
    if type(record.get("testCount")) is not int or record["testCount"]<=0:
        errors.append("NO_TEST_COUNT_CLAIM")
    if record.get("independentReviewState") != "EXTERNAL_REVIEW_REQUIRED":
        errors.append("CLAIMED_INDEPENDENT_REVIEW")
    if record.get("officialVerifiedFinish")!="HOLD":
        errors.append("PREMATURE_OFFICIAL_FINISH")
    if record.get("ownerDecision")!="PENDING":
        errors.append("CLAIMED_OWNER_APPROVAL")
    return sorted(set(errors))


def audit_manifest(manifest,root:Path):
    """No mutations, no authority elevation, no unchecked receipt ingestion."""
    errors=[]
    checked=[]
    if not isinstance(manifest,dict) or manifest.get("schema")!=SCHEMA:
        errors.append("INVALID_MANIFEST_SCHEMA")
        manifest={}
    tasks=manifest.get("tasks",[])
    if not isinstance(tasks,list) or len(tasks)!=3:
        errors.append("THREE_TASK_FAMILIES_REQUIRED")
        tasks=[]
    family_ids=set()
    task_ids=set()
    for i,t in enumerate(tasks):
        errs=[]
        if not isinstance(t,dict):
            errors.append("INVALID_TASK_PLAN_"+str(i))
            continue
        family=t.get("family")
        task_id=t.get("taskId")
        if not isinstance(family,str) or family not in FAMILIES:
            errs.append("UNKNOWN_TASK_FAMILY")
        if not isinstance(task_id,str) or not IDENTITY.fullmatch(task_id):
            errs.append("INVALID_TASK_ID")
        if isinstance(family,str) and isinstance(task_id,str):
            if family in family_ids or task_id in task_ids:
                errs.append("DUPLICATE_FAMILY_OR_TASK")
            family_ids.add(family)
            task_ids.add(task_id)
        if not isinstance(t.get("sourceHead"),str) or not SHA40.fullmatch(t["sourceHead"]):
            errs.append("INVALID_EXPECTED_HEAD")
        pin=t.get("receiptSha256")
        filename=t.get("receiptFile")
        if not isinstance(pin,str) or not SHA256.fullmatch(pin):
            errs.append("INVALID_RECEIPT_SHA_PIN")
        if not isinstance(filename,str) or not IDENTITY.fullmatch(filename) or not filename.endswith(".json"):
            errs.append("INVALID_RECEIPT_FILENAME")
        byte_match=False
        semantic_eligible=False
        if not errs:
            try:
                data=read_no_symlink(root,filename,MAX_RECEIPT)
                byte_match=(sha256(data)==pin)
                if not byte_match:
                    errs.append("RECEIPT_PIN_MISMATCH")
                else:
                    receipt=load_json(data)
                    if not isinstance(receipt,dict) or receipt.get("schema")!=RECEIPT_SCHEMA:
                        errs.append("INVALID_RECEIPT_SCHEMA")
                    else:
                        semantic_errors=format_receipt(receipt,t)
                        errs.extend(semantic_errors)
                        semantic_eligible=(not semantic_errors)
            except (OSError,ValueError,UnicodeError):
                errs.append("RECEIPT_UNREADABLE_OR_INVALID")
        checked.append({"taskId":task_id if isinstance(task_id,str) else None,
                        "family":family if isinstance(family,str) else None,
                        "bytePinMatched":byte_match,
                        "semanticReviewEligible":semantic_eligible and not errs,
                        "actualExecutionVerified":False,
                        "holds":sorted(set(errs))})
        errors.extend(errs)
    if family_ids!=FAMILIES:
        errors.append("NOT_ALL_FAMILIES_PRESENT")
    if manifest.get("realMacAuthorityVerified") is not False or manifest.get("humanThreshold")!="HOLD":
        errors.append("PREMATURE_AUTHORITY_IN_MANIFEST")
    # A self-provided JSON record, even if hash-pinned, proves no real run.
    return {"schema":"enguru.zulfikar.field-evidence-decision/v1",
       "evidenceByteReconciliation":"CANDIDATE_REVIEW_ONLY" if not errors else "HOLD",
       "holds":sorted(set(errors)), "reviewedTasks":checked,
       "claimedTaskObservationsWithMatchingBytes":sum(1 for c in checked if c["bytePinMatched"]),
       "semanticallyEligibleTaskClaims":sum(1 for c in checked if c["semanticReviewEligible"]),
       "independentlyVerifiedRealTaskCount":0,
       "ownerIdentityCryptographicallyAuthenticated":False,
       "registeredHandlerExecutionAuthenticated":False,
       "durableRecoveryAuthenticated":False,
       "macOSFieldAccepted":False,
       "verifiedFinish":"HOLD",
       "nextAuthority":"Existing trusted Mac Engineer/owner/DoneCheck independent observation"}


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--bundle",required=True,help="Directory with private manifest and receipts")
    args=parser.parse_args(argv)
    root=Path(args.bundle).absolute()
    try:
        manifest=load_json(read_no_symlink(root,"manifest.json",MAX_MANIFEST))
        result=audit_manifest(manifest,root)
        rc=0 if not result["holds"] else 2
    except (OSError,ValueError,UnicodeError):
        result={"schema":"enguru.zulfikar.field-evidence-decision/v1",
                "evidenceByteReconciliation":"HOLD",
                "holds":["MANIFEST_UNREADABLE"],
                "independentlyVerifiedRealTaskCount":0,
                "verifiedFinish":"HOLD"}
        rc=2
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))
    return rc


if __name__=="__main__":
    raise SystemExit(main())
