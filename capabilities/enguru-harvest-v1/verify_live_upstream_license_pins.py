"""Independent read-only public GitHub commit/root-file observation for A05.

At exact recorded source commits, check README and root-license Git blob IDs
against GitHub Contents API; reject stale root labels and forged license approval.
No external code execution, redistribution authorization, or Mac OSi access.
"""
import concurrent.futures
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
HEX40=re.compile(r"^[a-f0-9]{40}$")
REPO_PATTERN=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ALLOWED_LICENSES={"LICENSE","LICENSE.md","LICENSE.txt","LICENSE-MIT"}

def _hold(reason):
    return {"state":"HOLD","reason":reason}

def inspect_response(pin,license_row,entries):
    if not all(isinstance(x,dict) for x in (pin,license_row)):
        return _hold("INVALID_RECORDS")
    repo=pin.get("repository")
    commit=pin.get("commit_sha")
    if (not isinstance(repo,str) or REPO_PATTERN.fullmatch(repo) is None or
            not isinstance(commit,str) or HEX40.fullmatch(commit) is None or
            repo!=license_row.get("repository")):
        return _hold("SOURCE_IDENTITY")
    if (pin.get("legal_approval")!="HOLD" or pin.get("security_acceptance")!="HOLD" or
            pin.get("adoption")!="HOLD" or pin.get("source_archive_sha256") is not None or
            license_row.get("redistribution_approval")!="HOLD"):
        return _hold("UNAUTHORIZED_PROMOTION")
    if not isinstance(entries,list) or len(entries)>1500:
        return _hold("INVALID_GITHUB_DIRECTORY")
    root={}
    for entry in entries:
        if not isinstance(entry,dict):
            return _hold("INVALID_DIRECTORY_ENTRY")
        name=entry.get("name")
        if not isinstance(name,str) or not name or name in root:
            return _hold("DUPLICATE_DIRECTORY_ENTRY")
        root[name]=entry
    readme=root.get("README.md")
    if (not isinstance(readme,dict) or readme.get("type")!="file" or
            readme.get("sha")!=pin.get("readme_git_blob_sha1") or
            not isinstance(readme.get("sha"),str) or HEX40.fullmatch(readme["sha"]) is None):
        return _hold("README_GIT_BLOB_DRIFT")
    path=license_row.get("path")
    if path is None:
        if license_row.get("git_blob_sha1") is not None or license_row.get("content_signal")!="ROOT_LICENSE_NOT_FOUND":
            return _hold("ROOT_LICENSE_MISSING_CONTRACT")
        if any(x in root and root[x].get("type")=="file" for x in ALLOWED_LICENSES):
            return _hold("UNEXPECTED_NEW_ROOT_LICENSE")
        return {"state":"PASS_PINNED_README_ROOT_LICENSE_ABSENT",
                "repository":repo,"source_commit":commit,"root_license_present":False}
    if path not in ALLOWED_LICENSES or license_row.get("state")!="ROOT_LICENSE_TEXT_OBSERVED_ONLY":
        return _hold("LICENSE_CONTRACT")
    present=root.get(path)
    if (not isinstance(present,dict) or present.get("type")!="file" or
            present.get("sha")!=license_row.get("git_blob_sha1") or
            not isinstance(present.get("sha"),str) or HEX40.fullmatch(present["sha"]) is None):
        return _hold("LICENSE_GIT_BLOB_DRIFT")
    return {"state":"PASS_PINNED_README_AND_LICENSE",
            "repository":repo,"source_commit":commit,
            "readme_blob_sha1":readme["sha"],"license_path":path,
            "license_blob_sha1":present["sha"],"root_license_present":True,
            "redistribution_authorized":False}

def fetch_root(pin,token):
    # Explicit sole allowlisted host; no user-provided URL or redirect accepted.
    repo=pin["repository"]
    commit=pin["commit_sha"]
    if REPO_PATTERN.fullmatch(repo) is None or HEX40.fullmatch(commit) is None:
        raise ValueError("UNSAFE_UPSTREAM_IDENTITY")
    url="https://api.github.com/repos/"+repo+"/contents?ref="+commit
    headers={"Accept":"application/vnd.github+json",
             "User-Agent":"enguru-v141-a05-pinned-license-validation",
             "X-GitHub-Api-Version":"2022-11-28"}
    if token:
        headers["Authorization"]="Bearer "+token
    req=urllib.request.Request(url,headers=headers)
    class RestrictRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,request,fp,code,msg,headers,newurl):
            raise ValueError("UNEXPECTED_GITHUB_REDIRECT")
    opener=urllib.request.build_opener(RestrictRedirect)
    with opener.open(req,timeout=24) as response:
        if response.status!=200 or response.headers.get("Content-Type","").split(";")[0]!="application/json":
            raise ValueError("INVALID_GITHUB_RESPONSE")
        raw=response.read(750_001)
        if len(raw)>750_000:
            raise ValueError("OVERSIZE_ROOT_DIRECTORY")
        return json.loads(raw)

def verify_all(pins,licenses,fetcher):
    if not isinstance(pins,dict) or not isinstance(licenses,dict):
        return _hold("BAD_INPUT")
    rows=pins.get("sources")
    lic=licenses.get("observations")
    if not isinstance(rows,list) or len(rows)!=30 or not isinstance(lic,list) or len(lic)!=30:
        return _hold("EXPECTED_30")
    if pins.get("promotion_allowed") is not False:
        return _hold("SOURCE_PROMOTION")
    lookup={}
    for license_entry in lic:
        if (not isinstance(license_entry,dict) or
                not isinstance(license_entry.get("repository"),str) or
                license_entry["repository"] in lookup):
            return _hold("INVALID_LICENSE_REGISTRY")
        lookup[license_entry["repository"]]=license_entry
    if set(lookup)!={row.get("repository") for row in rows if isinstance(row,dict)}:
        return _hold("DIFFERENT_REPO_SETS")
    def worker(pin):
        result=inspect_response(pin,lookup[pin["repository"]],fetcher(pin))
        if result["state"]=="HOLD":
            raise ValueError(pin["repository"]+":"+result["reason"])
        return result
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results=list(executor.map(worker,rows))
    except (ValueError,urllib.error.URLError,TimeoutError,KeyError,TypeError,OSError) as exc:
        return _hold("REMOTE_SOURCE_VERIFY_FAILED: "+str(exc)[:200])
    if len(results)!=30 or len({r["repository"] for r in results})!=30:
        return _hold("RESULT_COUNT")
    exact=sum(r["root_license_present"] for r in results)
    if exact!=29 or len(results)-exact!=1:
        return _hold("EXPECTED_29_LICENSES")
    return {"state":"PASS_GITHUB_PINNED_SOURCE_AND_LICENSE_BYTES_OBSERVED_ONLY",
            "source_commits_checked":30,"readme_blob_matches":30,
            "root_license_matches":29,"root_license_absent":1,
            "authorized_redistribution":0,"independently_proven_skills":0,
            "results":results}

def run():
    pins=json.loads((HERE/"UPSTREAM_GITHUB_PINS_30.json").read_text(encoding="utf-8"))
    lic=json.loads((HERE/"root_license_observations.json").read_text(encoding="utf-8"))
    token=os.environ.get("GITHUB_TOKEN","")
    result=verify_all(pins,lic,lambda x:fetch_root(x,token))
    head=subprocess.check_output(["git","-C",str(REPO),"rev-parse","HEAD"],text=True).strip()
    result["schema"]="enguru.harvest.a05-upstream-live-commit-license-proof/v1"
    result["github_head"]=head
    result["official_verified_finish"]="HOLD"
    result["source_license_authority"]="HOLD"
    result["osi_execution"]=0
    (HERE/"a05-github-root-license-receipt.json").write_text(
        json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="results"},sort_keys=True,ensure_ascii=False))
    if result["state"]!="PASS_GITHUB_PINNED_SOURCE_AND_LICENSE_BYTES_OBSERVED_ONLY":
        raise SystemExit(1)

if __name__=="__main__":
    run()
