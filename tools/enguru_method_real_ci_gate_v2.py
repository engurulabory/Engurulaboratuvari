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
    if (type(spec)!=dict or
        len(spec.get("shared_controls",[]))!=12 or
        tuple(d.get("id") for d in spec.get("domains",[]))!=AREAS or
        not HEX40.fullmatch(str(current_sha))):
        return {"verdict":"HOLD_CANONICAL_OR_SHA_INPUT"}
    control_ids=[c.get("id") for c in spec["shared_controls"]]
    if len(set(control_ids))!=12:
        return {"verdict":"HOLD_FIXED_SCOPE"}
    for d in spec["domains"]:
        ids=[c.get("id") for c in d.get("domain_controls",[])]
        if (len(ids)!=4 or len(set(ids))!=4 or
            set(ids).intersection(control_ids) or
            any(not c.get("required") or not c.get("negative") for c in d["domain_controls"])):
            return {"verdict":"HOLD_FIXED_SCOPE"}
    current_valid=(type(commit_record)==dict
                   and commit_record.get("sha")==current_sha
                   and bool(re.fullmatch(r"[0-9a-f]{40}",
                       str(commit_record.get("commit",{}).get("tree",{}).get("sha","")))))
    run_valid=(type(run_record)==dict
              and run_record.get("id")==RUN_ID
              and run_record.get("head_sha")==RUN_SHA
              and run_record.get("event")=="push"
              and run_record.get("status")=="completed"
              and run_record.get("conclusion")=="success"
              and run_record.get("head_repository",{}).get("full_name")==REPO)
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
      "historic_method_ci_run_id":RUN_ID,
      "historic_method_ci_sha":RUN_SHA,
      "source_evidence":source_result,"ci_evidence":history_result,
      "areas":results,
      "pass_count_real_source":sum(x["source_evidence"].startswith("PASS")
                                   and x["method_ci_evidence"].startswith("PASS") for x in results),
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
