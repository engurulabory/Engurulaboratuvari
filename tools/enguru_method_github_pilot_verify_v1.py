#!/usr/bin/env python3
"""Distinct verifier for GitHub workspace pilot. No production authority."""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

REQUIRED = ["CORE","ENGINE","AGENT","WEB","APP","COMMERCE"]

def verify(repo,workspace):
    source = repo/"governance/enguru-suzgeci/ENGURU_ALTI_URETIM_ALANI_V1.json"
    db=workspace/"checkpoint.sqlite3"
    artifact=workspace/"evidence"/"method-production-map.json"
    if not all(x.is_file() for x in (source, db, artifact)):
        return {"status":"HOLD_FILES_MISSING"}
    source_bytes=source.read_bytes()
    obj=json.loads(source_bytes)
    raw=artifact.read_bytes()
    packet=json.loads(raw)
    expected={
        "schema":"enguru.method.production-6.provenance/v1",
        "input_sha256":hashlib.sha256(source_bytes).hexdigest(),
        "six_fields":REQUIRED,
        "controls_per_field":16,
        "total_field_control_instances":96,
        "user_co_design":"HOLD_REAL_CASE_CONSENSUS",
        "osi_field":"HOLD_NOT_EXECUTED",
        "verified_finish":"HOLD",
    }
    try:
        con=sqlite3.connect(f"file:{db}?mode=ro",uri=True)
        rows=con.execute("SELECT task_id,source_sha,artifact_sha,complete FROM receipts ORDER BY task_id").fetchall()
        con.close()
    except (sqlite3.Error, OSError):
        return {"status":"HOLD_SQLITE_PROVENANCE"}
    if (len(rows)!=1 or rows[0][0]!="GH-PILOT-ENGINE-001"
            or rows[0][1]!=expected["input_sha256"]
            or rows[0][2]!=hashlib.sha256(raw).hexdigest()
            or rows[0][3]!=1):
        return {"status":"HOLD_LEDGER_MISMATCH","count":len(rows)}
    if packet!=expected:
        return {"status":"HOLD_ARTIFACT_CONTENT_MISMATCH"}
    ids=[x["id"] for x in obj["domains"]]
    if ids!=REQUIRED or len(obj["shared_controls"])!=12 or any(len(x["domain_controls"])!=4 for x in obj["domains"]):
        return {"status":"HOLD_SOURCE_CONTENT"}
    return {
        "status":"PASS_GITHUB_ISOLATED_PILOT",
        "task_id":rows[0][0],
        "ledger_rows":len(rows),
        "source_sha256":rows[0][1],
        "artifact_sha256":rows[0][2],
        "six_domains":len(ids),
        "verified_field_control_instances":96,
        "verified_finish":"HOLD",
    }

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: verifier REPO WORKSPACE")
    try:
        outcome=verify(Path(sys.argv[1]),Path(sys.argv[2]))
    except (OSError,ValueError,KeyError,json.JSONDecodeError) as exc:
        outcome={"status":"HOLD_VERIFICATION_ERROR","error_type":type(exc).__name__}
    print(json.dumps(outcome,sort_keys=True))
    raise SystemExit(0 if outcome["status"]=="PASS_GITHUB_ISOLATED_PILOT" else 3)
