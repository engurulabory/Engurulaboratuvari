"""ENGURU isolated GitHub-only OSi handoff artifact builder.

Prepares signed-by-hash *candidate* source package and a reproducible SHA256
receipt. Never executes on Mac, never publishes/installs into a user device.
"""
import hashlib
import io
import json
import os
import re
import subprocess
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCES=(
    "AGENTS.md",
    "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md",
    "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json",
    "capabilities/enguru-harvest-v1/goal.json",
    "capabilities/enguru-harvest-v1/ZULFIKAR_V131_100_GATE_CONTRACT.json",
    "capabilities/enguru-harvest-v1/UPSTREAM_GITHUB_PINS_30.json",
    "capabilities/enguru-harvest-v1/READINESS_AUDIT_V2.json",
    "capabilities/enguru-harvest-v1/OSI_HANDOFF_PREPARATION.md",
    "capabilities/enguru-harvest-v1/KALAN_ISLER_VE_OSI_ONCESI_PUANLAMA.md",
)
V3="governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md"
V3_PIN="11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc"
MAX_PACKAGE_BYTES=2_000_000

def _sha(raw):
    return hashlib.sha256(raw).hexdigest()

def _head_bytes(path):
    return subprocess.run(["git","-C",str(ROOT),"show","HEAD:"+path],
                          check=True,capture_output=True).stdout

def build():
    head=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
    if re.fullmatch("[0-9a-f]{40}",head) is None:
        raise ValueError("GIT_HEAD_REQUIRED")
    entries={}
    total=0
    for name in SOURCES:
        p=ROOT/name
        if (p.is_symlink() or not p.is_file() or p.resolve().is_relative_to(ROOT.resolve()) is False or
                name.startswith("/") or ".." in Path(name).parts):
            raise ValueError("UNSAFE_SOURCE_PATH")
        data=p.read_bytes()
        if data!=_head_bytes(name):
            raise ValueError("GIT_HEAD_BYTE_MISMATCH")
        total+=len(data)
        if total>MAX_PACKAGE_BYTES:
            raise ValueError("SOURCE_BUDGET_EXCEEDED")
        entries[name]={"sha256":_sha(data),"size":len(data)}
    if entries[V3]["sha256"]!=V3_PIN:
        raise ValueError("CANONICAL_V3_SHA")
    manifest={
        "schema":"enguru.harvest.github-to-osi-packet/v1",
        "source_repository":"engurulabory/Engurulaboratuvari",
        "github_head":head,
        "official_github_verified_finish":"HOLD",
        "mac_field_acceptance":"HOLD",
        "owner_field_authority":"HOLD",
        "package_execution_allowed":False,
        "mac_transfer_executed":False,
        "osi_execution_count":0,
        "required_first_field_action":"AUTHORIZED_READ_ONLY_MAC_INVENTORY",
        "sources":entries
    }
    manifest_data=(json.dumps(manifest,sort_keys=True,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    memory=io.BytesIO()
    with zipfile.ZipFile(memory,"w",compression=zipfile.ZIP_STORED) as archive:
        for name in SOURCES:
            payload=(ROOT/name).read_bytes()
            item=zipfile.ZipInfo(name,(2026,10,26,0,0,0))
            item.compress_type=zipfile.ZIP_STORED
            item.external_attr=0o100644<<16
            archive.writestr(item,payload)
        entry=zipfile.ZipInfo("HANDOFF_MANIFEST.json",(2026,10,26,0,0,0))
        entry.compress_type=zipfile.ZIP_STORED
        entry.external_attr=0o100644<<16
        archive.writestr(entry,manifest_data)
    data=memory.getvalue()
    if len(data)>MAX_PACKAGE_BYTES:
        raise ValueError("PACKAGE_SIZE")
    check=inspect(data)
    if check["state"]!="PASS_GITHUB_PACKAGE_INTEGRITY_ONLY":
        raise ValueError("INTERNAL_SELF_TEST")
    out=ROOT/"capabilities/enguru-harvest-v1"
    zip_path=out/("ENGURU_OSI_HAZIRLIK_"+head[:12]+".zip")
    zip_path.write_bytes(data)
    receipt={"schema":"enguru.harvest.github-package-receipt/v1",
             "github_head":head,"package_filename":zip_path.name,
             "zip_sha256":_sha(data),"manifest_sha256":_sha(manifest_data),
             "file_count":len(SOURCES),"self_test":check["state"],
             "github_runner_only":True,"mac_transfer_executed":False,
             "osi_execution_count":0,"authorized_field_action":"HOLD",
             "official_verified_finish":"HOLD"}
    (out/"osi-github-handoff-receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return receipt

def inspect(data):
    if not isinstance(data,bytes) or len(data)>MAX_PACKAGE_BYTES:
        return {"state":"HOLD_PACKAGE_BYTES"}
    try:
        with zipfile.ZipFile(io.BytesIO(data),"r") as archive:
            names=archive.namelist()
            if sorted(names)!=sorted([*SOURCES,"HANDOFF_MANIFEST.json"]) or len(set(names))!=len(names):
                return {"state":"HOLD_PATHS"}
            manifest=json.loads(archive.read("HANDOFF_MANIFEST.json"))
            if (manifest.get("schema")!="enguru.harvest.github-to-osi-packet/v1" or
                    manifest.get("official_github_verified_finish")!="HOLD" or
                    manifest.get("mac_field_acceptance")!="HOLD" or
                    manifest.get("owner_field_authority")!="HOLD" or
                    manifest.get("package_execution_allowed") is not False or
                    manifest.get("mac_transfer_executed") is not False or
                    type(manifest.get("osi_execution_count")) is not int or manifest["osi_execution_count"]!=0):
                return {"state":"HOLD_AUTHORITY"}
            entries=manifest.get("sources")
            if not isinstance(entries,dict) or set(entries)!=set(SOURCES):
                return {"state":"HOLD_SOURCE_LIST"}
            for name in SOURCES:
                info=archive.getinfo(name)
                if (name.startswith("/") or ".." in Path(name).parts or
                    (info.external_attr >> 16) & 0o170000 != 0o100000):
                    return {"state":"HOLD_ZIP_PATH"}
                content=archive.read(name)
                if _sha(content)!=entries[name].get("sha256") or len(content)!=entries[name].get("size"):
                    return {"state":"HOLD_SOURCE_DIGEST"}
            if entries[V3]["sha256"]!=V3_PIN:
                return {"state":"HOLD_V3_DIGEST"}
            return {"state":"PASS_GITHUB_PACKAGE_INTEGRITY_ONLY","files":len(SOURCES)}
    except (ValueError,KeyError,TypeError,zipfile.BadZipFile,json.JSONDecodeError):
        return {"state":"HOLD_PACKAGE_PARSE"}

if __name__=="__main__":
    print(json.dumps(build(),ensure_ascii=False,sort_keys=True,indent=2))
