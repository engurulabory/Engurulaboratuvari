#!/usr/bin/env python3
"""ENGURU V2: deterministic decisions about *real* GitHub evidence, six domains.

This extends the existing method, NOT an issuer/approval authority. A successful
repository or CI verification does not prove six real products were delivered.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"governance/enguru-suzgeci/ENGURU_ALTI_URETIM_ALANI_V1.json"
REPO="engurulabory/Engurulaboratuvari"
AREAS=("CORE","ENGINE","AGENT","WEB","APP","COMMERCE")
HEX40=re.compile(r"^[0-9a-f]{40}$")
RUN_ID=40167298239  # Historical exact-main source-method CI, not new task delivery
RUN_SHA="f754b3a48e46224251d2717f1b28e6cf60bf2812"
WORKFLOW_PATH=".github/workflows/enguru-design48-theoretical.yml"
WORKFLOW_ID=395375091
# Semantic projection of the existing V1 controls at main 5623bfae. A contract
# change requires explicit review of this pin; caller claims stay non-authoritative.
CONTROLS_SHA256="8e7ced3e9d30c98d3237b68171bac6269b67e29a3aa185571d74b4e9aade3f09"


def control_projection(spec):
    return {"shared_controls":spec["shared_controls"],
            "domains":[{"id":d["id"],"domain_controls":d["domain_controls"]}
                       for d in spec["domains"]]}


def nested(record, *keys):
    for key in keys:
        if type(record) is not dict:
            return None
        record=record.get(key)
    return record


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def actual_github(path):
    req=urllib.request.Request("https://api.github.com/repos/"+REPO+"/"+path,
       headers={"Accept":"application/vnd.github+json",
                **({"Authorization":"Bearer "+os.environ["GITHUB_TOKEN"]}
                   if os.environ.get("GITHUB_TOKEN") else {}),
                "User-Agent":"ENGURU-real-source-evidence/2"})
    with urllib.request.urlopen(req,timeout=12) as resp:
        return json.load(resp)


def evaluate(spec,current_sha,commit_record,run_record):
    """Pure deterministic gate: identical verified snapshots => identical bytes."""
    if (type(spec) is not dict or type(spec.get("shared_controls")) is not list
        or len(spec["shared_controls"])!=12
        or type(spec.get("domains")) is not list
        or any(type(d) is not dict for d in spec["domains"])
        or tuple(d.get("id") for d in spec["domains"])!=AREAS
        or type(current_sha) is not str or not HEX40.fullmatch(current_sha)):
        return {"verdict":"HOLD_CANONICAL_OR_SHA_INPUT"}
    try:
        projection=control_projection(spec)
        if digest(projection)!=CONTROLS_SHA256:
            return {"verdict":"HOLD_FIXED_SCOPE"}
    except (KeyError, TypeError, ValueError):
        return {"verdict":"HOLD_FIXED_SCOPE"}
    control_ids=[c["id"] for c in spec["shared_controls"]]
    current_valid=(nested(commit_record,"sha")==current_sha
                   and nested(commit_record,"url")==
                       "https://api.github.com/repos/"+REPO+"/commits/"+current_sha
                   and bool(HEX40.fullmatch(str(nested(commit_record,"commit","tree","sha")))))
    run_valid=(type(nested(run_record,"id")) is int
              and nested(run_record,"id")==RUN_ID
              and nested(run_record,"head_sha")==RUN_SHA
              and nested(run_record,"event")=="push"
              and nested(run_record,"status")=="completed"
              and nested(run_record,"conclusion")=="success"
              and nested(run_record,"head_repository","full_name")==REPO
              and nested(run_record,"repository","full_name")==REPO
              and nested(run_record,"path")==WORKFLOW_PATH
              and nested(run_record,"workflow_id")==WORKFLOW_ID)
    # "GitHub verified" applies only to this source/method snapshot; it has
    # no authority to declare any product's 16 distinct controls completed.
    source_result="PASS_REAL_GITHUB_COMMIT_IDENTITY" if current_valid else "HOLD_SOURCE_IDENTITY"
    history_result="PASS_HISTORICAL_GITHUB_METHOD_CI" if run_valid else "HOLD_CI_PROVENANCE"
    results=[]
    for domain in spec["domains"]:
        controls=control_ids+[c["id"] for c in domain["domain_controls"]]
        results.append({
            "area":domain["id"],"acceptance_controls":controls,"fixed_denominator":16,
            "source_evidence":source_result,"method_ci_evidence":history_result,
            "real_product_task_controls_completed":0,
            "product_verified_finish":"HOLD_ORIGINAL_REAL_TASK_EVIDENCE",
            "real_owner_or_independent_review":"HOLD",
            "mac_osi_field":"HOLD_NOT_EXECUTED",
            "official_donecheck":"HOLD_NOT_EXECUTED",
        })
    receipt={
      "schema":"enguru.methods.real-github-source-six-domains/v2",
      "current_source_commit":current_sha,
      "canonical_controls_sha256":CONTROLS_SHA256,
      "commit_snapshot_sha256":digest(commit_record),
      "historical_ci_snapshot_sha256":digest(run_record),
      "current_commit_ci":"HOLD_REQUIRES_SEPARATE_COMPLETED_EXACT_COMMIT_RUN",
      "historic_method_ci_run_id":RUN_ID,
      "historic_method_ci_sha":RUN_SHA,
      "source_evidence":source_result,"ci_evidence":history_result,
      "areas":results,
      "pass_count_real_source":sum(x["source_evidence"].startswith("PASS")
                                   and x["method_ci_evidence"].startswith("PASS") for x in results),
      "unique_source_commits_verified":int(current_valid),
      "unique_historical_ci_runs_verified":int(run_valid),
      "pass_count_real_products":0,
      "safety":"PRODUCT_PASS_REQUIRES_ITS_OWN_REAL_EVIDENCE_AND_AUTHORITY",
      "verdict":"PASS_SOURCE_METHOD_VERIFIED_PRODUCTS_HOLD" if current_valid and run_valid
                else "HOLD_INSUFFICIENT_REAL_GITHUB_EVIDENCE",
    }
    receipt["receipt_sha256"]=digest(receipt)
    return receipt


def run():
    parser=argparse.ArgumentParser()
    parser.add_argument("--commit",required=True,help="Exact GitHub commit checked out by CI")
    parser.add_argument("--output",help="Optional receipt path in runner temporary directory")
    args=parser.parse_args()
    try:
        local=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
        if local!=args.commit:
            raise ValueError("HOLD_LOCAL_CHECKOUT_SHA_MISMATCH")
        raw=SPEC.read_bytes()
        spec=json.loads(raw)
        receipt=evaluate(spec,args.commit,
            actual_github("commits/"+args.commit),
            actual_github("actions/runs/"+str(RUN_ID)))
        receipt["canonical_six_area_spec_sha256"]=hashlib.sha256(raw).hexdigest()
    except (OSError,ValueError,KeyError,urllib.error.URLError,subprocess.CalledProcessError,
            json.JSONDecodeError) as exc:
        receipt={"schema":"enguru.methods.real-github-source-six-domains/v2",
                 "verdict":"HOLD_REAL_EVIDENCE_UNAVAILABLE","reason_type":type(exc).__name__,
                 "pass_count_real_products":0}
    receipt["receipt_sha256"]=digest({k:v for k,v in receipt.items() if k!="receipt_sha256"})
    content=json.dumps(receipt,sort_keys=True,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        Path(args.output).write_text(content,encoding="utf-8")
    print(content,end="")
    return 0 if receipt["verdict"]=="PASS_SOURCE_METHOD_VERIFIED_PRODUCTS_HOLD" else 2


if __name__=="__main__":
    raise SystemExit(run())
