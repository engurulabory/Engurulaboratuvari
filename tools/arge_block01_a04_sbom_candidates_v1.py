#!/usr/bin/env python3
"""A04 source-bound *candidate* CycloneDX: locked versions vs unresolved ranges.

Never asserts a deployed product, a complete SBOM, or vulnerability clearance.
The original seven source pins are checked against actual upstream bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
import urllib.parse
from pathlib import Path

from tools.arge_block01_a04_dependency_seeds_v1 import (
    ORIGINAL, blob_sha1, entries, fetch_remote,
)

LOCKED = frozenset({"Meilisearch", "Medusa", "Saleor"})
GO = frozenset({"Temporal", "OpenFGA"})
RANGE = frozenset({"Supabase", "LangGraph"})
VERSION = re.compile(r"^\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?$")
GO_VERSION = re.compile(r"^v\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?(?:-\d{14}-[a-f0-9]+)?$")
YARN_HEADER = re.compile(r'^"(.+)":\s*$')
YARN_RES = re.compile(r'^  resolution:\s*"?(.+?)"?\s*$')
YARN_VER = re.compile(r'^  version:\s*"?(.+?)"?\s*$')


def _component(ecosystem, name, version, parent, relation):
    if not isinstance(name, str) or not name.strip() or not isinstance(version, str):
        raise ValueError("INVALID_PACKAGE_NAME_VERSION")
    # Coordinates are URL encoded, keeping slashes used by Go module and
    # scoped npm names while avoiding corruption of special chars in PURLs.
    purl_type = {"cargo": "cargo", "pypi": "pypi", "npm": "npm", "golang": "golang"}[ecosystem]
    normalized = urllib.parse.quote(name, safe="/")
    component_purl = f"pkg:{purl_type}/{normalized}@{urllib.parse.quote(version,safe='.+-')}"
    return {"type": "library", "name": name, "version": version,
            "purl": component_purl, "bom-ref": component_purl,
            "properties": [
                {"name": "enguru:a04:source", "value": parent},
                {"name": "enguru:a04:precision", "value": relation},
            ]}


def parse_locked(tech, body):
    text = body.decode("utf-8")
    result = []
    if tech in ("Meilisearch", "Saleor"):
        doc = tomllib.loads(text)
        ecosystem = "cargo" if tech == "Meilisearch" else "pypi"
        for item in doc.get("package", []):
            name,version = item.get("name"),item.get("version")
            if not name or not version or not VERSION.fullmatch(version):
                raise ValueError("MALFORMED_LOCK_PACKAGE")
            source = item.get("source")
            if tech=="Meilisearch" and not source:
                # Local workspace modules lack an externally resolved version.
                continue
            if tech=="Saleor" and not (isinstance(source,dict) and source.get("registry")):
                continue
            result.append(_component(ecosystem,name,version,tech,"LOCKFILE_EXACT_CANDIDATE"))
    elif tech=="Medusa":
        # Yarn Berry v6: root-level mapping keys and 'resolution' entries.
        # Skip workspace/patch/virtual/non-npm protocols; no guessed versions.
        current = {}
        for line in text.splitlines()+[""]:
            if line and not line[0].isspace() and line.rstrip().endswith(":"):
                if current.get("resolution"):
                    resolution=current["resolution"]
                    m=re.fullmatch(r"(.+)@npm:([^#\s]+)",resolution)
                    version=current.get("version")
                    if m and version and VERSION.fullmatch(version) and m.group(2)==version:
                        result.append(_component("npm",m.group(1),version,tech,
                                                 "LOCKFILE_EXACT_CANDIDATE"))
                current={}
            if line.startswith("  resolution:"):
                m=YARN_RES.match(line)
                if m:
                    current["resolution"]=m.group(1).strip('"')
            elif line.startswith("  version:"):
                m=YARN_VER.match(line)
                if m:
                    current["version"]=m.group(1).strip('"')
        if current.get("resolution"):
            m=re.fullmatch(r"(.+)@npm:([^#\\s]+)",current["resolution"])
            version=current.get("version")
            if m and version and VERSION.fullmatch(version) and m.group(2)==version:
                result.append(_component("npm",m.group(1),version,tech,
                                         "LOCKFILE_EXACT_CANDIDATE"))
    else:
        raise ValueError("UNSUPPORTED_LOCK_ECOSYSTEM")
    if not result:
        raise ValueError("EMPTY_OR_UNSUPPORTED_LOCK_SOURCE")
    return result


def parse_declared(tech, body):
    text=body.decode("utf-8")
    result=[]
    if tech in GO:
        # Only require (...) and 'require module version'; replace/exclude
        # directives and build tags are NOT modeled as resolved binaries.
        block=False
        for line in text.splitlines():
            line=line.split("//",1)[0].strip()
            if line=="require (":
                block=True
                continue
            if block and line==")":
                block=False
                continue
            if block or line.startswith("require "):
                if line.startswith("require "):
                    line=line[len("require "):]
                parts=line.split()
                if len(parts)>=2 and GO_VERSION.fullmatch(parts[1]):
                    result.append(_component("golang",parts[0],parts[1],tech,
                                             "DIRECT_GO_MOD_DECLARATION_NOT_BUILD_GRAPH"))
    elif tech=="Supabase":
        root=json.loads(text)
        for group in ("dependencies","devDependencies","optionalDependencies"):
            for name,spec in root.get(group,{}).items():
                if isinstance(spec,str) and spec:
                    result.append({"name":name,"constraint":spec,"source":tech,
                                   "precision":"UNRESOLVED_ROOT_PACKAGE_RANGE"})
    elif tech=="LangGraph":
        root=tomllib.loads(text)
        from_array=root.get("project",{}).get("dependencies",[])
        for spec in from_array:
            if isinstance(spec,str) and spec.strip():
                result.append({"requirement":spec,"source":tech,
                               "precision":"UNRESOLVED_PYPROJECT_SPECIFIER"})
    else:
        raise ValueError("UNSUPPORTED_MANIFEST")
    if not result:
        raise ValueError("EMPTY_DECLARED_SOURCE")
    return result


def assemble(manifest,upstream,fetch=fetch_remote,timeout=15.0):
    receipt={"schema":"enguru.hym2.a04.source-scoped-cdx-candidates/v1",
             "state":"HOLD", "source_count_expected":7,"source_count_verified":0,
             "locked_versions_technologies":sorted(LOCKED),
             "declared_module_technologies":sorted(GO),
             "unresolved_range_technologies":sorted(RANGE),
             "source_summary":[],"unresolved_declarations":[],
             "complete_sbom":"HOLD","customer_installation_sbom":"HOLD",
             "cve_advisory_review":"HOLD", "legal_license_clearance":"HOLD",
             "a04_official":"HOLD","verified_finish":"HOLD"}
    try:
        seed_entries=entries(manifest,upstream)
    except (ValueError,KeyError,TypeError) as err:
        receipt["reason"]="MANIFEST_HOLD_"+str(err)
        return receipt, None
    components=[]
    for tech,repo,commit,path,expected,coverage in seed_entries:
        row={"technology":tech,"commit":commit,"file":path,
             "file_git_blob_sha1_expected":expected,"state":"HOLD"}
        uri=f"https://raw.githubusercontent.com/{repo}/{commit}/{urllib.parse.quote(path)}"
        try:
            body,final=fetch(uri,timeout)
            if urllib.parse.urlparse(final).hostname!="raw.githubusercontent.com":
                raise ValueError("UNTRUSTED_REDIRECT")
            if not isinstance(body,bytes) or not body:
                raise ValueError("NO_BINARY_SOURCE")
            actual=blob_sha1(body)
            row["file_git_blob_sha1_observed"]=actual
            row["file_sha256"]=hashlib.sha256(body).hexdigest()
            if actual != expected:
                raise ValueError("SOURCE_BLOB_MISMATCH")
            parsed = parse_locked(tech,body) if tech in LOCKED else parse_declared(tech,body)
            if tech in RANGE:
                receipt["unresolved_declarations"].extend(parsed)
            else:
                components.extend(parsed)
            row["source_entries"]=len(parsed)
            row["precision"]=coverage
            row["state"]="PASS_SOURCE_PARSED"
            receipt["source_count_verified"]+=1
        except (OSError,ValueError,KeyError,TypeError,UnicodeError,tomllib.TOMLDecodeError) as exc:
            row["error_type"]=type(exc).__name__
            row["error_reason"]=str(exc)[:80]
        receipt["source_summary"].append(row)
    if receipt["source_count_verified"]!=7:
        return receipt,None
    components={x["bom-ref"]:x for x in components}.values()
    bom={"bomFormat":"CycloneDX","specVersion":"1.5","version":1,
         "metadata":{"properties":[
             {"name":"enguru:a04:scope","value":"RESEARCH_SOURCE_CANDIDATE_NOT_DEPLOYED_OR_COMPLETE"},
             {"name":"enguru:a04:source_pin_count","value":"7"},
             {"name":"enguru:a04:unresolved_root_package_ranges","value":str(len(receipt["unresolved_declarations"]))},
             {"name":"enguru:a04:advisory_scan","value":"NOT_EXECUTED"},
         ]},
         "components":sorted(components,key=lambda x:x["bom-ref"])}
    receipt["candidate_components_with_version"]=len(bom["components"])
    receipt["state"]="PASS_SOURCE_SCOPED_COMPONENT_CANDIDATES_ONLY"
    receipt["candidate_sbom_sha256"]=hashlib.sha256(
        json.dumps(bom,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return receipt,bom


def _unique(pairs):
    obj={}
    for k,v in pairs:
        if k in obj:
            raise ValueError("DUPLICATE_JSON_KEY")
        obj[k]=v
    return obj


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--upstream",type=Path,required=True)
    parser.add_argument("--output-cdx",type=Path,required=True)
    args=parser.parse_args()
    try:
        m=json.loads(args.manifest.read_text(encoding="utf-8"),object_pairs_hook=_unique)
        u=json.loads(args.upstream.read_text(encoding="utf-8"),object_pairs_hook=_unique)
        receipt,bom=assemble(m,u)
        if bom is not None:
            args.output_cdx.write_text(json.dumps(bom,ensure_ascii=False,sort_keys=True,separators=(",",":")),
                                       encoding="utf-8")
    except (OSError,ValueError,TypeError,UnicodeError) as err:
        receipt={"state":"HOLD_INPUT_OR_WRITE","error_type":type(err).__name__}
    print(json.dumps(receipt,ensure_ascii=False,sort_keys=True))
    return 0 if receipt["state"]=="PASS_SOURCE_SCOPED_COMPONENT_CANDIDATES_ONLY" else 2


if __name__=="__main__":
    sys.exit(main())
