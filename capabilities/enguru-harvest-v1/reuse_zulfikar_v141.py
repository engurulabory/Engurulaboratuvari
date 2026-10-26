"""Reuse the sealed Zülfikar V1.4.1 engine in an isolated GitHub runner.

Fetch by an immutable Git commit, validate source file SHA256 from the real
seal, run the original preflight in a disposable directory, and issue a
technical observation receipt. Neither ownership nor official FINISH is minted.
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DIR=Path(__file__).resolve().parent
CONTRACT=DIR/"ZULFIKAR_V141_SOURCE_REUSE.json"
RECEIPT=DIR/"v141-source-reuse-receipt.json"
SHA40=re.compile(r"^[0-9a-f]{40}$")
SHA64=re.compile(r"^[0-9a-f]{64}$")

def git(*args, check=True):
    return subprocess.run(["git","-C",str(ROOT),*args],capture_output=True,check=check,timeout=75).stdout

def validate_contract(data):
    if not isinstance(data,dict) or data.get("schema")!="enguru.harvest.zulfikar-v141-source-reuse/v1":
        raise ValueError("V141_CONTRACT_SCHEMA")
    if data.get("source_repository")!="engurulabory/Engurulaboratuvari":
        raise ValueError("V141_REPOSITORY")
    if not isinstance(data.get("source_git_commit"),str) or SHA40.fullmatch(data["source_git_commit"]) is None:
        raise ValueError("V141_COMMIT_PIN")
    if data.get("source_seal_path")!="governance/enguru-suzgeci/zulfikar-v12/v141/GITHUB_SOURCE_SHA_SEAL_V1.json":
        raise ValueError("V141_SEAL_PATH")
    if data.get("source_prefix")!="governance/enguru-suzgeci/zulfikar-v12/v141/":
        raise ValueError("V141_STAGE_PREFIX")
    if data.get("archive_sha256")!="366d906c3f44e86d834a311365c2bead51f82509faec7568c6374209b5c9224e":
        raise ValueError("V141_ARCHIVE_PIN")
    if (data.get("allowed_mode")!="TEMPORARY_GITHUB_RUNNER_COPIED_SOURCE_ONLY" or
        data.get("official_finish")!="HOLD" or data.get("owner_acceptance")!="HOLD" or
        type(data.get("osi_execution")) is not int or data["osi_execution"]!=0 or
        type(data.get("github_merge")) is not int or data["github_merge"]!=0):
        raise ValueError("V141_AUTHORITY_BOUNDARY")
    stages=data.get("gates")
    if not isinstance(stages,list) or [x.get("id") for x in stages if isinstance(x,dict)]!=[
            "T01","T02","A01","A02","A03","A04","A05","A06"]:
        raise ValueError("V141_EIGHT_GATES")
    if stages[6].get("state")!="HOLD_REAL_TASKS_AND_AUTHORITY":
        raise ValueError("V141_REAL_TASKS_ARE_NOT_PROVEN")
    return True

def check_seal(seal, contract):
    if not isinstance(seal,dict) or seal.get("schema")!="enguru.zulfikar.v141.github-source-sha-seal/v1":
        raise ValueError("V141_SOURCE_SEAL")
    if (seal.get("archiveSha256")!=contract["archive_sha256"] or
        seal.get("repository")!=contract["source_repository"] or
        seal.get("ownerDoneCheck")!="NOT_ISSUED" or
        seal.get("actualMacOsi")!="NOT_EXECUTED" or
        seal.get("verifiedFinish")!="NOT_ISSUED"):
        raise ValueError("V141_SOURCE_SEAL_AUTHORITY")
    rows=seal.get("stageFiles")
    if not isinstance(rows,list) or len(rows)!=11:
        raise ValueError("V141_SOURCE_FILE_COUNT")
    names=set()
    for item in rows:
        if not isinstance(item,dict):
            raise ValueError("V141_SOURCE_ENTRY")
        p=item.get("path")
        s=item.get("sha256")
        if (not isinstance(p,str) or p in names or not isinstance(s,str) or SHA64.fullmatch(s) is None or
            (not p.startswith(contract["source_prefix"]) and
             p!=".github/workflows/enguru-zulfikar-v141-dom-preflight.yml") or
            p.startswith("/") or ".." in Path(p).parts):
            raise ValueError("V141_UNSAFE_FILE")
        names.add(p)
    for required in ("preflight.py","dom/engine.py","dom/test_engine.py","dom/test_final_hardening.py"):
        if contract["source_prefix"]+required not in names:
            raise ValueError("V141_ENGINE_MISSING")
    return rows

def git_blob(commit,path):
    if not isinstance(path,str) or path.startswith("/") or ".." in Path(path).parts:
        raise ValueError("UNSAFE_SOURCE_PATH")
    return git("show",commit+":"+path)

def inspect_sources(commit,seal,contract,source_dir):
    matched=0
    for row in check_seal(seal,contract):
        raw=git_blob(commit,row["path"])
        if hashlib.sha256(raw).hexdigest()!=row["sha256"]:
            raise ValueError("V141_SOURCE_SHA_MISMATCH")
        if row["path"].startswith(contract["source_prefix"]):
            relative=row["path"][len(contract["source_prefix"]):]
            if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
                raise ValueError("V141_RELATIVE_PATH")
            output=source_dir/relative
            output.parent.mkdir(parents=True,exist_ok=True)
            output.write_bytes(raw)
        matched+=1
    return matched

def evaluate_report(report):
    if not isinstance(report,dict):
        return False
    rounds=report.get("threeRealLocalTestRounds")
    return (report.get("engineerPreparationScore")==100 and
        report.get("architectureDesignControlsPassed")==10 and
        report.get("architectureDesignControlsRequired")==10 and
        report.get("realLocalUnittestExecutions")==177 and
        isinstance(rounds,list) and len(rounds)==3 and
        all(isinstance(r,dict) and r.get("tests")==59 and r.get("pass") is True for r in rounds) and
        report.get("productVerifiedFinish")=="NOT_ISSUED" and
        report.get("GitHubCommitOrCI")=="ACTION_RUNNER_TEST_SCOPE_ONLY")

def main():
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    commit=contract["source_git_commit"]
    # The sole remote mutation is a FETCH into the disposable checkout's Git object store.
    # This writes no tracked source, canonical files, refs or human-owned Mac paths.
    git("fetch","--no-tags","--depth=1","origin",commit)
    observed=git("rev-parse",commit).decode().strip()
    if observed!=commit:
        raise ValueError("V141_COMMIT_ID_DRIFT")
    seal=json.loads(git_blob(commit,contract["source_seal_path"]))
    with tempfile.TemporaryDirectory(prefix="enguru-v141-github-readonly-") as tmp:
        stage=Path(tmp)/"v141"
        stage.mkdir()
        files=inspect_sources(commit,seal,contract,stage)
        p=subprocess.run([sys.executable,"-B","preflight.py"],cwd=stage,
                         text=True,capture_output=True,timeout=180)
        report_path=stage/"evidence/pre_github_readiness_report.json"
        report=json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
        valid=p.returncode==0 and evaluate_report(report)
        receipt={
            "schema":"enguru.harvest.v141-original-engine-run/v1",
            "harvest_head":git("rev-parse","HEAD").decode().strip(),
            "zulfikar_source_commit":commit,
            "source_file_sha256_verified":files,
            "source_archive_sha256_claim":seal["archiveSha256"],
            "original_preflight_exit":p.returncode,
            "three_rounds":report.get("threeRealLocalTestRounds",[]),
            "real_local_unittests":report.get("realLocalUnittestExecutions",0),
            "design_only_engineering_score":report.get("engineerPreparationScore",0),
            "source_scope":"PINNED_UPSTREAM_GITHUB_REVIEW_BRANCH_TEMPORARY_RUN",
            "run_success":valid,
            "official_harvest_verified_finish":"HOLD",
            "independent_real_user_value":"HOLD",
            "owner_authority":"HOLD",
            "mac_osi_execution":0,
            "new_engine_duplicated":False,
            "stderr_tail":p.stderr[-1200:] if not valid else "",
        }
        RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2))
        if not valid:
            raise SystemExit("V141_REAL_SOURCE_PREFLIGHT_HOLD")

if __name__=="__main__":
    main()
