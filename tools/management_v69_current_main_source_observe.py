#!/usr/bin/env python3
"""Read-only GitHub current-main source observation; never an owner/DoneCheck receipt."""
import argparse
import base64
import hashlib
import json
import os
import re
from urllib.parse import quote
from urllib.request import Request,urlopen

REPO="engurulabory/Engurulaboratuvari"
SOURCE="governance/controller/work/pilot-repair.txt"
HISTORICAL="1f7dfd708d652764ac74df27dcbbd393779e2b3b"

def observe(main_sha, content_bytes, api_sha):
    if not isinstance(main_sha,str) or not re.fullmatch("[a-f0-9]{40}",main_sha):
        return {"state":"HOLD_GUVENLI_DUR","reason":"MAIN_SHA_REQUIRED"}
    digest=hashlib.sha256(content_bytes).hexdigest()
    if digest!=api_sha:
        return {"state":"HOLD_GUVENLI_DUR","reason":"SOURCE_DIGEST_MISMATCH"}
    return {"schema":"enguru.v69.current-main-source-observation/v1",
            "state":"PASS_CURRENT_MAIN_SOURCE_OBSERVED",
            "repository":REPO,"source_path":SOURCE,"main_sha":main_sha,
            "source_sha256":digest,"historical_commit":HISTORICAL,
            "historical_receipt_reusable":False,
            "owner_signature":"HOLD_REAL_OWNER_SIGNER",
            "donecheck":"HOLD_SEPARATE_CANONICAL_GATE",
            "official_finish":"HOLD"}

def api(endpoint,token):
    req=Request("https://api.github.com/repos/"+REPO+"/"+endpoint,
                headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
                "User-Agent":"enguru-v69-readonly"})
    with urlopen(req,timeout=20) as r:return json.load(r)

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True);args=p.parse_args()
    token=os.environ.get("GITHUB_TOKEN")
    if not token:raise SystemExit("HOLD_GITHUB_READ_TOKEN_REQUIRED")
    sha=api("commits/main",token)["sha"]
    doc=api("contents/"+SOURCE+"?ref="+quote(sha),token)
    raw=base64.b64decode(doc["content"])
    tasks=api("contents/governance/controller/TASKS.json?ref="+quote(sha),token)
    task_doc=json.loads(base64.b64decode(tasks["content"]))
    matches=[t for t in task_doc.get("tasks",[]) if t.get("id")=="LABORY_SAFE_REPAIR" and t.get("path")==SOURCE and t.get("target_repo")==REPO]
    expected=matches[0].get("desired_sha256","") if len(matches)==1 else ""
    result=observe(sha,raw,expected)
    if result["state"].startswith("PASS_"):
        import pathlib
        dst=pathlib.Path(args.output)
        if dst.exists() or dst.is_symlink():raise SystemExit("HOLD_OUTPUT_EXISTS")
        with dst.open("x") as f:json.dump(result,f,sort_keys=True,indent=2)
    print(json.dumps(result,sort_keys=True))
    return 0 if result["state"].startswith("PASS_") else 50
if __name__=="__main__":raise SystemExit(main())
