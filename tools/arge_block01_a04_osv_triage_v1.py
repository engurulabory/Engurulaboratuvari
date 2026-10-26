#!/usr/bin/env python3
"""HYM2 A04: classify real OSV source-only advisory matches with record metadata.

Critical boundaries: 'advisory match' != exploited vulnerability, deployed
binary, complete SBOM, security clearance, legal approval or A04 official PASS.
Uses real OSV GET /v1/vulns/{id} with source and response integrity controls.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ENDPOINT="https://api.osv.dev/v1/vulns/"
ID_RE=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,159}$")
RANK={"UNKNOWN":0,"LOW":1,"MODERATE":2,"HIGH":3,"CRITICAL":4}
LEVELS={"LOW":"LOW","MEDIUM":"MODERATE","MODERATE":"MODERATE",
        "HIGH":"HIGH","CRITICAL":"CRITICAL"}


def fetch_record(advisory_id:str, timeout=16.0):
    if not ID_RE.fullmatch(advisory_id):
        raise ValueError("ADVISORY_ID_INVALID")
    url=ENDPOINT+urllib.parse.quote(advisory_id,safe="")
    request=urllib.request.Request(url,headers={
        "User-Agent":"ENGURU-HYM2-A04-OSV-pinned-source-triage/1",
        "Accept":"application/json"})
    last=None
    for retry in range(3):
        try:
            with urllib.request.urlopen(request,timeout=timeout) as reply:
                final=reply.geturl()
                parsed=urllib.parse.urlparse(final)
                if parsed.scheme!="https" or parsed.hostname!="api.osv.dev":
                    raise ValueError("UNTRUSTED_OSV_REDIRECT")
                data=reply.read(2_000_001)
                if len(data)>2_000_000:
                    raise ValueError("OSV_RECORD_SIZE_BOUND")
            return json.loads(data)
        except (urllib.error.URLError,TimeoutError) as exc:
            last=exc
            if retry<2:time.sleep(0.25*(retry+1))
    raise OSError("OSV_RECORD_UNAVAILABLE:"+type(last).__name__)


def _source_roster(snapshot, summary, raw):
    if not isinstance(snapshot,dict) or not isinstance(summary,dict):
        raise ValueError("SOURCE_MALFORMED")
    if snapshot.get("schema")!="enguru.hym2.a04.osv-source-advisory-snapshot/v1":
        raise ValueError("SOURCE_SCHEMA")
    if (summary.get("state")!="PASS_OSV_SOURCE_SNAPSHOT_ONLY" or
        summary.get("source_candidate_sha256")!=snapshot.get("source_candidate_sha256")):
        raise ValueError("SOURCE_RECEIPT_MISMATCH")
    rows=snapshot.get("observations")
    if not isinstance(rows,list) or not rows or len(rows)>4000:
        raise ValueError("SOURCE_ROW_COUNT")
    if len(rows)!=summary.get("query_coverage"):
        raise ValueError("QUERY_COVERAGE")
    unique=set(); tally=0; affected=0; found={}
    for row in rows:
        if not isinstance(row,dict):
            raise ValueError("ROW_FORMAT")
        for key in ("upstream","purl","name","version","ecosystem","precision"):
            if not isinstance(row.get(key),str) or not row[key]:
                raise ValueError("SOURCE_COMPONENT_FIELDS")
        if row["purl"] in unique:
            raise ValueError("DUPLICATE_SOURCE_PURL")
        unique.add(row["purl"])
        advisories=row.get("advisories")
        if not isinstance(advisories,list):
            raise ValueError("ADVISORIES_FORMAT")
        affected+=int(bool(advisories))
        per_package=set()
        for a in advisories:
            if not isinstance(a,dict) or not isinstance(a.get("id"),str) or not ID_RE.fullmatch(a["id"]):
                raise ValueError("ADVISORY_ID_FORMAT")
            if a["id"] in per_package:
                raise ValueError("DUPLICATE_ADVISORY_ON_COMPONENT")
            per_package.add(a["id"])
            found[a["id"]]=True
            tally+=1
    if (tally!=summary.get("advisory_matches") or
        affected!=summary.get("affected_package_candidates") or
        snapshot.get("source_candidate_sha256") is None):
        raise ValueError("SOURCE_TOTALS_DRIFT")
    return rows,sorted(found)


def _declared_severity(entry, matching_affected):
    """Only explicit OSV qualitative labels; CVSS vector kept without guess."""
    claims=[]
    for obj in [entry.get("database_specific",{})]+[a.get("ecosystem_specific",{}) for a in matching_affected]+[a.get("database_specific",{}) for a in matching_affected]:
        if isinstance(obj,dict) and isinstance(obj.get("severity"),str):
            label=LEVELS.get(obj["severity"].upper())
            if label:claims.append(label)
    return max(claims,key=lambda x:RANK[x]) if claims else "UNKNOWN"


def _normalize_record(vid,record):
    if not isinstance(record,dict) or record.get("id")!=vid:
        raise ValueError("OSV_IDENTITY_DRIFT")
    sev=record.get("severity",[])
    if not isinstance(sev,list):
        raise ValueError("OSV_SEVERITY_FORMAT")
    vectors=[{"type":x.get("type"),"score":x.get("score")} for x in sev
             if isinstance(x,dict) and isinstance(x.get("score"),str)][:5]
    affected=record.get("affected",[])
    if not isinstance(affected,list):
        raise ValueError("OSV_AFFECTED_FORMAT")
    fixes=[]
    for a in affected:
        if not isinstance(a,dict):continue
        pkg=a.get("package",{})
        if not isinstance(pkg,dict):continue
        ranges=a.get("ranges",[])
        if not isinstance(ranges,list):continue
        for rng in ranges:
            if not isinstance(rng,dict):continue
            for event in rng.get("events",[]):
                if isinstance(event,dict) and isinstance(event.get("fixed"),str):
                    fixes.append({"ecosystem":pkg.get("ecosystem"),"package":pkg.get("name"),
                                  "fixed_event":event["fixed"],"range_type":rng.get("type")})
    return {"id":vid,"database_specific":record.get("database_specific",{}),
            "summary":str(record.get("summary",""))[:240],
            "modified":record.get("modified"),"published":record.get("published"),
            "cvss_vectors":vectors,"affected":affected,
            "fix_events":fixes,"url":"https://osv.dev/vulnerability/"+urllib.parse.quote(vid,safe="")}


def audit(snapshot,summary,raw,lookup=fetch_record,workers=8):
    receipt={"schema":"enguru.hym2.a04.osv-advisory-triage/v1",
             "state":"HOLD","source_scope":"PINNED_PUBLIC_SOURCE_CANDIDATES",
             "security_clearance":"HOLD","actual_deployed_sbom":"HOLD",
             "license_legal":"HOLD","a03_official":"HOLD",
             "a04_official":"HOLD","verified_finish":"HOLD"}
    try:
        if not 1<=workers<=12:
            raise ValueError("WORKER_BUDGET")
        rows,ids=_source_roster(snapshot,summary,raw)
        receipt.update(snapshot_sha256=hashlib.sha256(raw).hexdigest(),
                       matched_source_components=summary["affected_package_candidates"],
                       advisory_matches=summary["advisory_matches"],
                       advisory_ids_total=len(ids),metadata_records_observed=0)
        records={}
        with cf.ThreadPoolExecutor(max_workers=workers) as pool:
            futures={pool.submit(lookup,vid):vid for vid in ids}
            errors=[]
            for future in cf.as_completed(futures):
                vid=futures[future]
                try:
                    records[vid]=_normalize_record(vid,future.result())
                except (ValueError,TypeError,KeyError,OSError,urllib.error.URLError,
                        TimeoutError,json.JSONDecodeError) as exc:
                    errors.append({"id":vid,"error_type":type(exc).__name__})
        receipt["metadata_records_observed"]=len(records)
        if errors:
            receipt["metadata_failures"]=errors[:20]
            raise ValueError("OSV_METADATA_PARTIAL")
        if len(records)!=len(ids):
            raise ValueError("OSV_METADATA_COUNT_MISMATCH")
        affected_packages=[]; counts=Counter(); labels=Counter()
        for row in rows:
            if not row["advisories"]:continue
            severities=[]; fix_events=[]
            for a in row["advisories"]:
                info=records[a["id"]]
                matches=[x for x in info["affected"]
                         if isinstance(x,dict) and isinstance(x.get("package"),dict)
                         and x["package"].get("name")==row["name"]
                         and x["package"].get("ecosystem")==row["ecosystem"]]
                level=_declared_severity(info,matches)
                labels[level]+=1
                severities.append({"id":a["id"],"qualitative_severity":level,
                                   "cvss_vector_evidence_present":bool(info["cvss_vectors"]),
                                   "url":info["url"]})
                for event in info["fix_events"]:
                    if event["package"]==row["name"] and event["ecosystem"]==row["ecosystem"]:
                        fix_events.append({"id":a["id"],**event})
            highest=max((x["qualitative_severity"] for x in severities),key=lambda x:RANK[x])
            counts[row["upstream"]]+=len(severities)
            affected_packages.append({
                "upstream":row["upstream"],"name":row["name"],
                "version":row["version"],"purl":row["purl"],
                "component_precision":row["precision"],
                "advisory_matches":len(severities),
                "highest_explicit_severity":highest,
                "triage_lane":"REVIEW_"+highest if highest!="UNKNOWN" else "REVIEW_UNRATED",
                "related_advisories":severities,
                "recorded_fix_events":fix_events,
                "deployment_applicability":"UNKNOWN_CUSTOMER_RUNTIME",
                "fix_version_suitable_for_installed_product":"UNVERIFIED"})
        affected_packages.sort(key=lambda row:(-RANK[row["highest_explicit_severity"]],
                                                -row["advisory_matches"],
                                                row["upstream"],row["name"],row["version"]))
        receipt.update(
            state="PASS_PUBLIC_OSV_METADATA_TRIAGE_ONLY",
            source_advisory_total=sum(x["advisory_matches"] for x in affected_packages),
            affected_package_total=len(affected_packages),
            explicit_severity_distribution=dict(sorted(labels.items())),
            upstream_match_counts=dict(sorted(counts.items())),
            prioritization="EXPLICIT_RECORD_LABEL_THEN_MATCH_COUNT; UNRATED_IS_URGENT_MANUAL_REVIEW",
            cve_fix_applicability="HOLD_OWNER_RUNTIME_SCOPE",
            timestamp_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        report={"schema":receipt["schema"],"receipt_source_sha256":receipt["snapshot_sha256"],
                "observed_at_utc":receipt["timestamp_utc"],
                "advisory_metadata":[{k:v for k,v in info.items() if k!="affected"}
                                     for _,info in sorted(records.items())],
                "priority_queue":affected_packages,
                "scope":"RESEARCH_ONLY_NOT_INSTALLATION_OR_OFFICIAL_APPROVAL"}
        return receipt,report
    except (ValueError,TypeError,KeyError,OSError,urllib.error.URLError,
            TimeoutError,json.JSONDecodeError) as e:
        receipt["hold_reason"]=str(e)[:180]
        return receipt,None


def unique_pairs(pairs):
    ret={}
    for key,v in pairs:
        if key in ret:raise ValueError("DUPLICATE_INPUT_KEY")
        ret[key]=v
    return ret


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--snapshot",type=Path,required=True)
    p.add_argument("--summary",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--workers",type=int,default=8)
    args=p.parse_args()
    try:
        raw=args.snapshot.read_bytes()
        snapshot=json.loads(raw,object_pairs_hook=unique_pairs)
        summary=json.loads(args.summary.read_text(),object_pairs_hook=unique_pairs)
        receipt,report=audit(snapshot,summary,raw,workers=args.workers)
        if report is not None:
            args.output.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,
                                              separators=(",",":")),encoding="utf-8")
    except (OSError,TypeError,ValueError,UnicodeError) as e:
        receipt={"state":"HOLD_INPUT_OR_IO","type":type(e).__name__}
    print(json.dumps(receipt,ensure_ascii=False,sort_keys=True))
    return 0 if receipt["state"]=="PASS_PUBLIC_OSV_METADATA_TRIAGE_ONLY" else 2


if __name__=="__main__":
    raise SystemExit(main())
