#!/usr/bin/env python3
"""ENGURU HYM2/A04: exact upstream source-chain and advisory compatibility proof.

Tests Git object bytes at immutable third-party commits. Verdict applies only
to original research SOURCE GRAPH and possible patch range, never real deployed
Medusa, X-Forwarded-For configuration, OSI installation or official A04 PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

MEDUSA = "medusajs/medusa"
MEDUSA_COMMIT = "029fb31fd077ab9c6d6fd9d68c676c17c71294c7"
ADVISORY_REPO = "github/advisory-database"
ADVISORY_COMMIT = "a422b657c94bebb5c0e8c620017094d38eaad746"
ADVISORY_PATH = "advisories/github-reviewed/2026/10/GHSA-jqcg-44mw-7w3h/GHSA-jqcg-44mw-7w3h.json"
PINS = {
    (MEDUSA, MEDUSA_COMMIT, "yarn.lock"): "660081e74b9be3799b3a0f25d5631df4e1cf0658",
    (MEDUSA, MEDUSA_COMMIT, "packages/medusa/package.json"): "098f88ef04510bad2bf330c0569801aa2de12296",
    (MEDUSA, MEDUSA_COMMIT, "packages/core/framework/package.json"): "70bb89084b8864818d2387bf7178bda5d4db39fd",
    (ADVISORY_REPO, ADVISORY_COMMIT, ADVISORY_PATH): "1c5f475a60a2b179ac48f5a22138944728f11eb1",
}
MAX_SOURCE_BYTES = 2_000_000


def git_blob(data:bytes)->str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def remote(repo:str,commit:str,path:str,timeout=16)->bytes:
    url = "https://raw.githubusercontent.com/"+repo+"/"+commit+"/"+urllib.parse.quote(path)
    request=urllib.request.Request(url,headers={"User-Agent":"ENGURU-HYM2-A04-source-graph/1"})
    with urllib.request.urlopen(request,timeout=timeout) as stream:
        dst=urllib.parse.urlparse(stream.geturl())
        if dst.scheme!="https" or dst.hostname!="raw.githubusercontent.com":
            raise ValueError("UPSTREAM_SOURCE_REDIRECT")
        data=stream.read(MAX_SOURCE_BYTES+1)
    if not data or len(data)>MAX_SOURCE_BYTES:
        raise ValueError("SOURCE_BYTE_LIMIT")
    return data


def yarn_section(lock:str,key:str)->str:
    anchor='"'+key+'":\n'
    if lock.count(anchor)!=1:
        raise ValueError("LOCK_KEY_UNIQUE_REQUIRED_"+key)
    section=lock.split(anchor,1)[1]
    # Yarn v6 entries: one unindented descriptor header, indented fields.
    m=re.match(r"((?:[ \t]+[^\n]*\n|\n)*)",section)
    if not m or not m.group(1):
        raise ValueError("LOCK_ENTRY_FORMAT_"+key)
    return m.group(1)


def exact_field(section:str,name:str)->str:
    pat=r'(?m)^  '+re.escape(name)+r': "?([^"\n]+)"?\s*$'
    hits=re.findall(pat,section)
    if len(hits)!=1:
        raise ValueError("LOCK_FIELD_"+name)
    return hits[0].strip('"')


def range_allows(selector:str,version:str)->bool:
    # Restrict acceptance to ~2.0.x npm patch ranges; other range syntax
    # requires the repo's own exact-version package manager verification.
    if not re.fullmatch(r"~\d+\.\d+\.\d+",selector):
        raise ValueError("UNSUPPORTED_NPM_RANGE")
    if not re.fullmatch(r"\d+\.\d+\.\d+",version):
        raise ValueError("NONRELEASE_VERSION")
    major,minor,patch=(int(x) for x in selector[1:].split("."))
    vm,vn,vp=(int(x) for x in version.split("."))
    return vm==major and vn==minor and vp>=patch


def _validate(data:dict[tuple[str,str,str],bytes])->dict:
    lock=data[(MEDUSA,MEDUSA_COMMIT,"yarn.lock")].decode("utf-8")
    app=json.loads(data[(MEDUSA,MEDUSA_COMMIT,"packages/medusa/package.json")])
    framework=json.loads(data[(MEDUSA,MEDUSA_COMMIT,"packages/core/framework/package.json")])
    advisory=json.loads(data[(ADVISORY_REPO,ADVISORY_COMMIT,ADVISORY_PATH)])
    for item,name in ((app,"@medusajs/medusa"),(framework,"@medusajs/framework")):
        if item.get("name")!=name or item.get("dependencies",{}).get("express")!="^4.21.0":
            raise ValueError("WORKSPACE_EXPRESS_PATH_CHANGED_"+name)
    express=yarn_section(lock,"express@npm:^4.21.0")
    proxy=yarn_section(lock,"proxy-addr@npm:~2.0.7")
    ev=exact_field(express,"version")
    pv=exact_field(proxy,"version")
    if (ev!="4.22.1" or pv!="2.0.7"
        or exact_field(express,"resolution")!="express@npm:4.22.1"
        or exact_field(proxy,"resolution")!="proxy-addr@npm:2.0.7"
        or not re.search(r"(?m)^    proxy-addr: ~2\.0\.7$",express)):
        raise ValueError("SOURCE_EDGE_OR_RESOLUTION_CHANGED")
    if (advisory.get("id")!="GHSA-jqcg-44mw-7w3h"
        or "CVE-2026-90711" not in advisory.get("aliases",[])):
        raise ValueError("ADVISORY_IDENTITY_CHANGED")
    affected=advisory.get("affected")
    if not isinstance(affected,list) or len(affected)!=1:
        raise ValueError("ADVISORY_SCOPE")
    pkg=affected[0]
    if pkg.get("package")!={"ecosystem":"npm","name":"proxy-addr"}:
        raise ValueError("ADVISORY_PRODUCT")
    ranges=pkg.get("ranges")
    if not isinstance(ranges,list) or len(ranges)!=1:
        raise ValueError("ADVISORY_RANGE")
    events=ranges[0].get("events")
    if (ranges[0].get("type")!="ECOSYSTEM" or
        events!=[{"introduced":"1.1.0"},{"fixed":"2.0.8"}]):
        raise ValueError("ADVISORY_RANGE_CHANGED")
    patched=events[1]["fixed"]
    if not (range_allows("~2.0.7",pv) and range_allows("~2.0.7",patched)
            and tuple(map(int,pv.split(".")))<tuple(map(int,patched.split(".")))):
        raise ValueError("UPGRADE_RANGE_INCOMPATIBLE")
    return {
        "source_paths": [
            "@medusajs/medusa -> express@4.22.1 -> proxy-addr@2.0.7",
            "@medusajs/framework -> express@4.22.1 -> proxy-addr@2.0.7",
        ],
        "upstream_commit":MEDUSA_COMMIT,
        "express_selector":"^4.21.0",
        "resolved_express":ev,
        "express_proxy_addr_selector":"~2.0.7",
        "resolved_proxy_addr":pv,
        "advisory_id":advisory["id"],
        "cve":"CVE-2026-90711",
        "fixed_version":patched,
        "patch_in_existing_express_selector":True,
        "conditional_trigger":"Short-prefix IPv4-mapped IPv6 or zero-leading-bit IPv6 trusted proxy subnet (application configuration)"
    }


def verify(fetch=remote)->dict:
    verdict={
        "schema":"enguru.hym2.a04.proxy-addr-source-fix-path/v1",
        "state":"HOLD",
        "source_coverage":"PINNED_THIRD_PARTY_SOURCE_ONLY",
        "medusa_installation_proven":"HOLD",
        "application_proxy_trust_config_proven":"HOLD",
        "real_customer_exposure":"HOLD",
        "regression_for_real_installation":"HOLD",
        "a04_official":"HOLD",
        "osi_field":"HOLD",
        "verified_finish":"HOLD",
        "sources_verified":0,"expected_sources":len(PINS),"evidence":[]
    }
    data={}
    try:
        for repo,commit,path in PINS:
            body=fetch(repo,commit,path)
            if not isinstance(body,bytes) or not body or len(body)>MAX_SOURCE_BYTES:
                raise ValueError("INVALID_SOURCE_BYTES")
            observed=git_blob(body)
            if observed!=PINS[(repo,commit,path)]:
                raise ValueError("UPSTREAM_GIT_BLOB_DRIFT_"+path)
            data[(repo,commit,path)]=body
            verdict["evidence"].append({
                "repository":repo,"commit":commit,"path":path,
                "source_git_blob_sha1":observed,
                "source_sha256":hashlib.sha256(body).hexdigest(),
            })
            verdict["sources_verified"]+=1
        verdict.update(_validate(data))
        verdict["state"]="PASS_SOURCE_FIX_COMPATIBILITY_ONLY"
    except (OSError,ValueError,UnicodeError,KeyError,TypeError,json.JSONDecodeError) as exc:
        verdict["hold_reason"]=type(exc).__name__+":"+str(exc)[:120]
    return verdict


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--receipt",type=Path,required=True)
    a=p.parse_args()
    result=verify()
    a.receipt.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"state":result["state"],
        "source_count":result["sources_verified"],
        "advisory":result.get("advisory_id"),
        "patch_compatible":result.get("patch_in_existing_express_selector"),
        "real_installation":result["medusa_installation_proven"],
        "official":result["a04_official"],
        "error":result.get("hold_reason")},sort_keys=True))
    return 0 if result["state"]=="PASS_SOURCE_FIX_COMPATIBILITY_ONLY" else 2


if __name__=="__main__":
    raise SystemExit(main())
