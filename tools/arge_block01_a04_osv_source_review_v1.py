#!/usr/bin/env python3
"""HYM2 A04: source-scoped OSV advisory snapshot for pinned CycloneDX *candidates*.

Reuses existing source candidate generation. A passing scan means all mapped
exact source-version queries returned a bounded, complete API response.
It NEVER means absence of vulnerabilities, complete SBOM, deployed packages,
legal clearance or product/official approval.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.request

ENDPOINT = "https://api.osv.dev/v1/querybatch"
MAX_QUERIES = 4000
MAX_BATCH = 500
MAX_PAGES_PER_BATCH = 5
API_TIMEOUT = 25
ECOSYSTEMS = {
    "cargo": "crates.io",
    "pypi": "PyPI",
    "npm": "npm",
    "golang": "Go",
}
SUPPORTED = frozenset({"LOCKFILE_EXACT_CANDIDATE",
                       "DIRECT_GO_MOD_DECLARATION_NOT_BUILD_GRAPH"})


def read_cdxbom(bom: dict, original_receipt: dict, raw_bytes: bytes) -> list[dict]:
    if (bom.get("bomFormat") != "CycloneDX" or bom.get("specVersion") != "1.5"):
        raise ValueError("NOT_CYCLONEDX_1_5")
    if (original_receipt.get("state") !=
            "PASS_SOURCE_SCOPED_COMPONENT_CANDIDATES_ONLY" or
        original_receipt.get("source_count_verified") != 7):
        raise ValueError("SOURCE_SEVEN_PIN_PROOF_MISSING")
    if hashlib.sha256(raw_bytes).hexdigest() != original_receipt.get("candidate_sbom_sha256"):
        raise ValueError("CANDIDATE_SOURCE_SHA256_DRIFT")
    components = bom.get("components")
    if (not isinstance(components, list) or not components or len(components)>MAX_QUERIES
            or len(components)!=original_receipt.get("candidate_components_with_version")):
        raise ValueError("COMPONENT_ROSTER_OR_BUDGET")
    out=[]; seen=set()
    for item in components:
        if not isinstance(item,dict):
            raise ValueError("COMPONENT_FORMAT")
        purl=item.get("purl"); name=item.get("name"); version=item.get("version")
        props=item.get("properties")
        if (not isinstance(purl,str) or not isinstance(name,str) or not name
                or not isinstance(version,str) or not version or
                item.get("bom-ref")!=purl or not isinstance(props,list)):
            raise ValueError("CANDIDATE_FIELDS")
        tags={p.get("name"):p.get("value") for p in props if isinstance(p,dict)}
        relation=tags.get("enguru:a04:precision"); parent=tags.get("enguru:a04:source")
        if relation not in SUPPORTED:
            raise ValueError("UNRESOLVED_RANGE_PROMOTED_TO_EXACT")
        if parent not in ("Meilisearch","Medusa","Saleor","Temporal","OpenFGA"):
            raise ValueError("UNAUTHORIZED_SOURCE_PARENT")
        kind=purl.removeprefix("pkg:").split("/",1)[0]
        ecosystem=ECOSYSTEMS.get(kind)
        if (ecosystem is None or purl==kind or
            (parent in ("Temporal","OpenFGA"))!=(kind=="golang")):
            raise ValueError("UNSUPPORTED_ECOSYSTEM")
        if purl in seen:
            raise ValueError("DUPLICATE_COMPONENT")
        seen.add(purl)
        out.append({"purl":purl,"name":name,"version":version,
                    "ecosystem":ecosystem,"upstream":parent,"precision":relation})
    return out


def send_batch(queries: list[dict], timeout=API_TIMEOUT) -> dict:
    payload=json.dumps({"queries":queries},separators=(",",":")).encode("utf-8")
    req=urllib.request.Request(
        ENDPOINT,data=payload,method="POST",
        headers={"Content-Type":"application/json",
                 "User-Agent":"ENGURU-HYM2-A04-OSV-source-only/1"})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        if response.geturl()!=ENDPOINT:
            raise ValueError("OSV_UNTRUSTED_REDIRECT")
        data=response.read(12_000_000)
        if len(data)==12_000_000:
            raise ValueError("OSV_RESPONSE_SIZE_BOUND")
    return json.loads(data)


def query_all(components:list[dict], send=send_batch, batch_size=400) -> dict:
    if not 1<=batch_size<=MAX_BATCH:
        raise ValueError("BATCH_LIMIT")
    findings={}
    pages=0
    for start in range(0,len(components),batch_size):
        batch=components[start:start+batch_size]
        pending=[(i,{"package":{"name":x["name"],"ecosystem":x["ecosystem"]},
                     "version":x["version"]}) for i,x in enumerate(batch,start)]
        depth=0
        while pending:
            depth+=1
            if depth>MAX_PAGES_PER_BATCH:
                raise ValueError("OSV_PAGINATION_LIMIT")
            raw=send([q for _,q in pending])
            if not isinstance(raw,dict) or not isinstance(raw.get("results"),list):
                raise ValueError("OSV_INVALID_BATCH_RESPONSE")
            results=raw["results"]
            if len(results)!=len(pending):
                raise ValueError("OSV_RESPONSE_COUNT_MISMATCH")
            later=[]
            for (idx,query),data in zip(pending,results):
                if not isinstance(data,dict):
                    raise ValueError("OSV_INVALID_QUERY_RESULT")
                vulns=data.get("vulns",[])
                if not isinstance(vulns,list):
                    raise ValueError("OSV_INVALID_ADVISORIES")
                bucket=findings.setdefault(idx,{})
                for item in vulns:
                    if not isinstance(item,dict):
                        raise ValueError("OSV_MALFORMED_VULNERABILITY")
                    vid=item.get("id")
                    if not isinstance(vid,str) or not vid or len(vid)>150:
                        raise ValueError("OSV_MALFORMED_ADVISORY_ID")
                    bucket[vid]={"id":vid, "modified":item.get("modified")}
                token=data.get("next_page_token")
                if token is not None:
                    if not isinstance(token,str) or not token or len(token)>3000:
                        raise ValueError("OSV_INVALID_PAGINATION")
                    later.append((idx,{**query,"page_token":token}))
            pending=later
            pages+=1
    return {"findings":findings,"api_requests":pages}


def assessment(bom:dict,receipt:dict,raw_bytes:bytes,send=send_batch,batch_size=400):
    result={
        "schema":"enguru.hym2.a04.osv-source-advisory-snapshot/v1",
        "state":"HOLD", "api":ENDPOINT,
        "source_scope":"PINNED_DEPENDENCY_SOURCE_CANDIDATE_ONLY",
        "osv_query_status":"HOLD",
        "known_vulns_absent":"UNDETERMINED",
        "complete_sbom":"HOLD", "deployed_sbom":"HOLD",
        "cve_security_clearance":"HOLD", "license_legal_clearance":"HOLD",
        "a03_official":"HOLD","a04_official":"HOLD",
        "independent_e5":"HOLD_0_OF_18","verified_finish":"HOLD",
        "query_coverage":0, "advisory_matches":0, "affected_package_candidates":0,
        "unresolved_range_count":len(receipt.get("unresolved_declarations",[])),
        "provider_limit":"OSV knowledge and snapshot at request time; not an absence-of-risk guarantee"
    }
    try:
        components=read_cdxbom(bom,receipt,raw_bytes)
        result["source_candidate_sha256"]=hashlib.sha256(raw_bytes).hexdigest()
        result["eligible_source_components"]=len(components)
        result["batch_size"]=batch_size
        scan=query_all(components,send=send,batch_size=batch_size)
        observations=[]
        for idx,c in enumerate(components):
            vuln=sorted(scan["findings"].get(idx,{}).values(),key=lambda x:x["id"])
            observations.append({**c,"advisories":vuln})
        result["query_coverage"]=len(observations)
        result["batch_requests_with_pagination"]=scan["api_requests"]
        result["affected_package_candidates"]=sum(bool(v["advisories"]) for v in observations)
        result["advisory_matches"]=sum(len(v["advisories"]) for v in observations)
        result["observed_at_utc"]=dt.datetime.now(dt.timezone.utc).isoformat()
        result["osv_query_status"]="PASS_ALL_SOURCE_CANDIDATES_QUERIED"
        result["state"]="PASS_OSV_SOURCE_SNAPSHOT_ONLY"
        return result, {"schema":result["schema"],"source_candidate_sha256":result["source_candidate_sha256"],
                        "observed_at_utc":result["observed_at_utc"],"observations":observations,
                        "completeness":"RESEARCH_SOURCE_CANDIDATE_ONLY"}
    except (ValueError,KeyError,TypeError,UnicodeError,OSError,urllib.error.URLError,TimeoutError,
            json.JSONDecodeError) as err:
        result["hold_reason"]=type(err).__name__+":"+str(err)[:160]
        return result,None


def no_dupes(pairs):
    obj={}
    for k,v in pairs:
        if k in obj:raise ValueError("DUPLICATE_INPUT_KEY")
        obj[k]=v
    return obj


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cdx",type=pathlib.Path,required=True)
    p.add_argument("--source-receipt",type=pathlib.Path,required=True)
    p.add_argument("--output",type=pathlib.Path,required=True)
    p.add_argument("--batch-size",type=int,default=400)
    a=p.parse_args()
    try:
        raw=a.cdx.read_bytes()
        bom=json.loads(raw,object_pairs_hook=no_dupes)
        source=json.loads(a.source_receipt.read_text(encoding="utf-8"),object_pairs_hook=no_dupes)
        result,report=assessment(bom,source,raw,batch_size=a.batch_size)
        if report is not None:
            a.output.write_text(json.dumps(report,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    except (OSError,ValueError,TypeError,UnicodeError) as e:
        result={"state":"HOLD_INPUT","reason":type(e).__name__}
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))
    return 0 if result["state"]=="PASS_OSV_SOURCE_SNAPSHOT_ONLY" else 2


if __name__=="__main__":
    raise SystemExit(main())
