"""A05: full bytes of 29 exact-commit GitHub root licenses, NOT legal consent.

Reads a source/path only when it is already recorded in the 30-source pins
and previous independent license observation. Checks Git's blob SHA-1 computed
from the actual bytes and emits SHA-256 of the full license text, not just
GitHub metadata. Never executes or downloads a source program.
"""
import base64
import binascii
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent
HEX40=re.compile(r"^[0-9a-f]{40}$")
REPO_RE=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PATHS={"LICENSE","LICENSE.md","LICENSE.txt","LICENSE-MIT"}
MAX_BYTES=250_000

def blob_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\\0"+raw).hexdigest()

def classify_risk(repository, text):
    # These are provisional risk flags, not SPDX determinations.
    lower=text.lower()
    if repository=="anthropics/claude-code":
        return "RESTRICTED_VENDOR_COMMERCIAL_TERMS_REVIEW"
    if repository=="meilisearch/meilisearch":
        return "MIXED_BUSL_AND_MIT_COMPONENT_SCOPE_REVIEW"
    if repository=="HypothesisWorks/hypothesis":
        return "MPL_FILE_LEVEL_OBLIGATIONS_REVIEW"
    if repository=="modelcontextprotocol/servers" or repository.startswith("modelcontextprotocol/"):
        return "MCP_VERSIONED_LICENSE_TRANSITION_REVIEW"
    if "apache license" in lower and "version 2.0" in lower:
        return "APACHE_2_NOTICE_PATENT_REVIEW"
    if "mit license" in lower or "permission is hereby granted" in lower:
        return "MIT_NOTICE_REVIEW"
    return "UNCLASSIFIED_LICENSE_REVIEW"

def validate_license_bytes(pin, license_row, response):
    if not all(isinstance(x,dict) for x in (pin,license_row,response)):
        return {"state":"HOLD_INVALID_RECORD"}
    repo=pin.get("repository")
    commit=pin.get("commit_sha")
    path=license_row.get("path")
    expected=license_row.get("git_blob_sha1")
    if (not isinstance(repo,str) or REPO_RE.fullmatch(repo) is None or
            not isinstance(commit,str) or HEX40.fullmatch(commit) is None or
            path not in PATHS or
            not isinstance(expected,str) or HEX40.fullmatch(expected) is None or
            license_row.get("repository")!=repo or
            pin.get("legal_approval")!="HOLD" or pin.get("adoption")!="HOLD" or
            license_row.get("redistribution_approval")!="HOLD"):
        return {"state":"HOLD_SOURCE_OR_RIGHTS"}
    if response.get("type")!="file" or response.get("path")!=path or response.get("sha")!=expected:
        return {"state":"HOLD_GITHUB_METADATA_MISMATCH"}
    if response.get("encoding")!="base64" or not isinstance(response.get("content"),str):
        return {"state":"HOLD_FILE_ENCODING"}
    try:
        raw=base64.b64decode(response["content"],validate=True)
        decoded=raw.decode("utf-8")
    except (ValueError,UnicodeDecodeError,binascii.Error):
        return {"state":"HOLD_LICENSE_BYTES"}
    if (not raw or len(raw)>MAX_BYTES or
            type(response.get("size")) is not int or response["size"]!=len(raw) or
            blob_sha(raw)!=expected):
        return {"state":"HOLD_LICENSE_BLOB_INTEGRITY"}
    return {
        "state":"PASS_LICENSE_BYTES_OBSERVED_ONLY",
        "repository":repo,"source_commit_sha":commit,"license_path":path,
        "license_blob_sha1":expected,
        "license_fulltext_sha256":hashlib.sha256(raw).hexdigest(),
        "license_bytes":len(raw),
        "license_risk":classify_risk(repo,decoded),
        "license_text_redistributed":False,
        "legal_reuse_authorized":False,
        "security_approval":False,
        "source_archive_sha256":None,
    }

def fetch_license(pin,license_row,token):
    repo=pin["repository"]
    commit=pin["commit_sha"]
    path=license_row["path"]
    if REPO_RE.fullmatch(repo) is None or HEX40.fullmatch(commit) is None or path not in PATHS:
        raise ValueError("UNSAFE_GITHUB_RESOURCE")
    url="https://api.github.com/repos/"+repo+"/contents/"+path+"?ref="+commit
    headers={"Accept":"application/vnd.github+json",
             "User-Agent":"enguru-v141-a05-license-bytes",
             "X-GitHub-Api-Version":"2022-11-28"}
    if token:
        headers["Authorization"]="Bearer "+token
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,request,fp,code,msg,headers,newurl):
            raise ValueError("GITHUB_REDIRECT_DENIED")
    opener=urllib.request.build_opener(NoRedirect)
    with opener.open(urllib.request.Request(url,headers=headers),timeout=24) as res:
        if res.status!=200 or res.headers.get("Content-Type","").split(";")[0]!="application/json":
            raise ValueError("INVALID_GITHUB_RESPONSE")
        payload=res.read(500_001)
        if len(payload)>500_000:
            raise ValueError("LICENSE_JSON_OVERSIZED")
        return json.loads(payload)

def reconcile(pins,license_registry,fetcher):
    if not isinstance(pins,dict) or not isinstance(license_registry,dict):
        return {"state":"HOLD_INPUT"}
    ps=pins.get("sources")
    ls=license_registry.get("observations")
    if not isinstance(ps,list) or len(ps)!=30 or not isinstance(ls,list) or len(ls)!=30:
        return {"state":"HOLD_COUNT"}
    lookup={}
    for license_entry in ls:
        if (not isinstance(license_entry,dict) or
                not isinstance(license_entry.get("repository"),str) or
                license_entry["repository"] in lookup):
            return {"state":"HOLD_DUPLICATE_LICENSE"}
        lookup[license_entry["repository"]]=license_entry
    if {p.get("repository") for p in ps if isinstance(p,dict)}!=set(lookup):
        return {"state":"HOLD_REPOSITORY_SETS"}
    if pins.get("promotion_allowed") is not False:
        return {"state":"HOLD_PROMOTION_CLAIM"}
    paired=[]
    missing=[]
    for pin in ps:
        lic=lookup[pin["repository"]]
        if lic["path"] is None:
            if (pin["repository"]!="anthropics/skills" or lic["git_blob_sha1"] is not None or
                    lic["redistribution_approval"]!="HOLD"):
                return {"state":"HOLD_UNKNOWN_ROOT_LICENSE"}
            missing.append(pin["repository"])
        else:
            paired.append((pin,lic))
    if len(paired)!=29 or missing!=["anthropics/skills"]:
        return {"state":"HOLD_ROOT_LICENSE_SCOPE"}
    def worker(item):
        pin,lic=item
        decision=validate_license_bytes(pin,lic,fetcher(pin,lic))
        if decision["state"]!="PASS_LICENSE_BYTES_OBSERVED_ONLY":
            raise ValueError(pin["repository"]+":"+decision["state"])
        return decision
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            records=list(pool.map(worker,paired))
    except (ValueError,KeyError,TypeError,UnicodeError,urllib.error.URLError,TimeoutError,OSError) as exc:
        return {"state":"HOLD_LICENSE_SOURCE_VERIFICATION","reason":str(exc)[:250]}
    if len(records)!=29 or len({r["repository"] for r in records})!=29:
        return {"state":"HOLD_RESULT_COVERAGE"}
    return {"state":"PASS_PINNED_29_LICENSE_FULLTEXT_DIGESTS_OBSERVED_ONLY",
            "root_license_fulltext_sha256_count":29,
            "missing_root_license_count":1,
            "risk_review_required_count":29,
            "legal_reuse_approvals":0,"official_proven_skills":0,
            "records":records}

def main():
    pins=json.loads((HERE/"UPSTREAM_GITHUB_PINS_30.json").read_text(encoding="utf-8"))
    licenses=json.loads((HERE/"root_license_observations.json").read_text(encoding="utf-8"))
    token=os.environ.get("GITHUB_TOKEN","")
    result=reconcile(pins,licenses,lambda p,l:fetch_license(p,l,token))
    head=subprocess.check_output(["git","-C",str(HERE.parents[1]),"rev-parse","HEAD"],
                                 text=True).strip()
    result.update({"schema":"enguru.harvest.a05-license-fulltext-evidence/v1",
                   "github_head":head,"official_finish":"HOLD",
                   "license_usage_authority":"HOLD","osi_execution":0})
    (HERE/"a05-license-fulltext-digests-receipt.json").write_text(
        json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="records"},
                     sort_keys=True,ensure_ascii=False))
    if result["state"]!="PASS_PINNED_29_LICENSE_FULLTEXT_DIGESTS_OBSERVED_ONLY":
        raise SystemExit(1)

if __name__=="__main__":
    main()
