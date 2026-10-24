#!/usr/bin/env python3
"""Real GitHub runner filesystem pilot for the ENGINE method adapter.

Reads the existing six-area source, persists SQLite state, produces actual bytes,
runs separate verifier, tests restart/idempotency, tamper and source drift.
All writes are isolated to disposable tempfile on the GitHub runner.
No Mac OSi action, external payment, credential, production engine or final authority.
"""
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOL=Path(__file__).resolve()
VERIFY=ROOT/"tools/enguru_method_github_pilot_verify_v1.py"
SOURCE_REL=Path("governance/enguru-suzgeci/ENGURU_ALTI_URETIM_ALANI_V1.json")
TASK_ID="GH-PILOT-ENGINE-001"
DOMAIN_IDS=["CORE","ENGINE","AGENT","WEB","APP","COMMERCE"]

def read_input(repo):
    raw=(repo/SOURCE_REL).read_bytes()
    obj=json.loads(raw)
    if ([x["id"] for x in obj["domains"]]!=DOMAIN_IDS
            or len(obj["shared_controls"])!=12
            or any(len(x["domain_controls"])!=4 for x in obj["domains"])):
        raise ValueError("HOLD_INVALID_REAL_REPO_SOURCE")
    return hashlib.sha256(raw).hexdigest()

def packet(sha):
    return {
        "schema":"enguru.method.production-6.provenance/v1",
        "input_sha256":sha,
        "six_fields":DOMAIN_IDS,
        "controls_per_field":16,
        "total_field_control_instances":96,
        "user_co_design":"HOLD_REAL_CASE_CONSENSUS",
        "osi_field":"HOLD_NOT_EXECUTED",
        "verified_finish":"HOLD",
    }

def worker(repo,ws):
    src_sha=read_input(repo)
    dest=ws/"evidence"/"method-production-map.json"
    db=ws/"checkpoint.sqlite3"
    if not db.is_file():
        return {"status":"HOLD_NO_PREPARED_LEDGER"}
    con=sqlite3.connect(db,timeout=10)
    try:
        con.execute("BEGIN IMMEDIATE")
        current=con.execute("SELECT source_sha,artifact_sha,complete FROM receipts WHERE task_id=?",
                            (TASK_ID,)).fetchone()
        if current is not None:
            if (current[0]!=src_sha or current[2]!=1 or
                    not dest.is_file() or
                    hashlib.sha256(dest.read_bytes()).hexdigest()!=current[1]):
                con.rollback()
                return {"status":"HOLD_SOURCE_OR_ARTIFACT_DRIFT"}
            con.commit()
            return {"status":"PASS_REPLAY_IDEMPOTENT"}
        data=(json.dumps(packet(src_sha),ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
        digest=hashlib.sha256(data).hexdigest()
        temp=ws/"evidence"/"method-production-map.tmp"
        with temp.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp,dest)
        con.execute("INSERT INTO receipts(task_id,source_sha,artifact_sha,complete) VALUES(?,?,?,1)",
                    (TASK_ID,src_sha,digest))
        con.commit()
        return {"status":"PASS_REAL_ARTIFACT_WRITTEN"}
    except (OSError,sqlite3.Error,ValueError):
        con.rollback()
        return {"status":"HOLD_WORKER_ERROR"}
    finally:
        con.close()

def cmd(*args):
    return subprocess.run([sys.executable,"-B",*map(str,args)],
                          capture_output=True,text=True,check=False)

def check_verifier(repo,ws):
    r=cmd(VERIFY,repo,ws)
    try:
        value=json.loads(r.stdout.strip())
    except (ValueError,TypeError):
        value={"status":"HOLD_BAD_VERIFIER_OUTPUT"}
    return r.returncode,value

def main():
    evidence=[]
    with tempfile.TemporaryDirectory(prefix="enguru-github-engine-pilot-") as tmp:
        ws=Path(tmp)
        (ws/"evidence").mkdir()
        db=ws/"checkpoint.sqlite3"
        with sqlite3.connect(db) as con:
            con.execute("CREATE TABLE receipts("
                        "task_id TEXT PRIMARY KEY,source_sha TEXT NOT NULL,"
                        "artifact_sha TEXT NOT NULL,complete INTEGER NOT NULL)")
            con.commit()
        expected=read_input(ROOT)

        first=cmd(TOOL,"--worker",ROOT,ws)
        worker1=json.loads(first.stdout)
        evidence.append({"id":"G01_REAL_FILE_AND_SQLITE_WRITE",
                         "pass":first.returncode==0 and worker1["status"]=="PASS_REAL_ARTIFACT_WRITTEN",
                         "worker":worker1["status"]})

        status,first_verified=check_verifier(ROOT,ws)
        evidence.append({"id":"G02_SEPARATE_VERIFIER",
                         "pass":status==0 and first_verified["status"]=="PASS_GITHUB_ISOLATED_PILOT",
                         "verdict":first_verified["status"]})

        second=cmd(TOOL,"--worker",ROOT,ws)
        replay=json.loads(second.stdout)
        evidence.append({"id":"G03_PROCESS_RESTART_AND_IDEMPOTENCY",
                         "pass":second.returncode==0 and replay["status"]=="PASS_REPLAY_IDEMPOTENT",
                         "worker":replay["status"]})

        artifact=ws/"evidence"/"method-production-map.json"
        baseline=artifact.read_bytes()
        artifact.write_bytes(baseline.replace(b"HOLD_NOT_EXECUTED",b"PASS",1))
        tamper_status,tamper=check_verifier(ROOT,ws)
        evidence.append({"id":"G04_TAMPER_REJECTION",
                         "pass":tamper_status!=0 and tamper["status"] in (
                             "HOLD_LEDGER_MISMATCH","HOLD_ARTIFACT_CONTENT_MISMATCH"),
                         "verdict":tamper["status"]})
        artifact.write_bytes(baseline)

        shadow=ws/"shadow-repo"/SOURCE_REL
        shadow.parent.mkdir(parents=True)
        shadow.write_bytes((ROOT/SOURCE_REL).read_bytes()+b"\n")
        drift=cmd(TOOL,"--worker",shadow.parents[2],ws)
        drift_value=json.loads(drift.stdout)
        evidence.append({"id":"G05_STALE_SOURCE_REJECTION",
                         "pass":drift.returncode!=0 and drift_value["status"]=="HOLD_SOURCE_OR_ARTIFACT_DRIFT",
                         "verdict":drift_value["status"]})

        status,verified=check_verifier(ROOT,ws)
        with sqlite3.connect(db) as con:
            receipt_count=con.execute("SELECT COUNT(*) FROM receipts").fetchone()[0]
        evidence.append({"id":"G06_REPAIR_VERIFY_AND_SINGLE_EFFECT",
                         "pass":status==0 and verified["status"]=="PASS_GITHUB_ISOLATED_PILOT"
                            and receipt_count==1 and hashlib.sha256(baseline).hexdigest()==verified["artifact_sha256"],
                         "ledger_rows":receipt_count,"verdict":verified["status"]})

        if verified.get("source_sha256")!=expected:
            evidence.append({"id":"G07_INPUT_SOURCE_SHA","pass":False})
        ok=all(x["pass"] for x in evidence) and len(evidence)==6
        result={
            "schema":"enguru.methods.github-engine-runtime-pilot/v1",
            "status":"PASS_GITHUB_REAL_ENGINE_PILOT" if ok else "HOLD_PILOT_FINDINGS",
            "task_id":TASK_ID,
            "test_scope":"REAL_GITHUB_RUNNER_TEMP_SQLITE_AND_ARTIFACTS",
            "checks":evidence,"checked":len(evidence),
            "passed":sum(x["pass"] for x in evidence),
            "source_sha256":expected,
            "artifact_sha256":verified.get("artifact_sha256",""),
            "independent_verification_mechanism":"SEPARATE_EXECUTABLE_SAME_PRODUCER_TEAM",
            "independent_human_review":"HOLD",
            "native_mac_osi_field":"HOLD",
            "donecheck_v12":"HOLD",
            "human_threshold":"HOLD",
            "verified_finish":"HOLD"
        }
        print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
        return 0 if ok else 2

if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--worker":
        try:
            res=worker(Path(sys.argv[2]),Path(sys.argv[3]))
        except (OSError,ValueError,KeyError,json.JSONDecodeError) as e:
            res={"status":"HOLD_WORKER_INVALID_INPUT","error_type":type(e).__name__}
        print(json.dumps(res,sort_keys=True))
        raise SystemExit(0 if res["status"].startswith("PASS") else 4)
    if len(sys.argv)==1:
        raise SystemExit(main())
    raise SystemExit("usage: script [--worker REPO WORKSPACE]")
