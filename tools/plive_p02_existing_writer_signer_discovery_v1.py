#!/usr/bin/env python3
"""Bounded Mac OSi read-only source discovery for existing P02 producer and G3 signer.

Reports candidates and SHA only; no authority or API inference. Never executes
found code, Keychain tools, signing binaries, or canonical commands.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

WRITER = re.compile(rb"P02\.S01\.01|PLIVE_P02|plive.p02|canonical.*(?:writer|update|commit)|(?:writer|commit).*canonical", re.I)
SIGNER = re.compile(rb"SecKeyCreateRandomKey|codesign\s|swiftc\s|provisioning|SecAccessControlCreateWithFlags", re.I)
SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__", ".build", "dist", "build"}
ALLOWED = {".py", ".swift", ".sh", ".command", ".md", ".json", ".plist", ".yml", ".yaml"}
MAX_BYTES = 512_000
MAX_FILES = 15_000
MAX_RESULTS = 150

def inspect(root: Path) -> dict:
    result = {"schema":"enguru.osi.p02.auth-source-discovery/v1",
              "state":"HOLD_NOT_SCANNED", "nativeAuthority":"HOLD",
              "canonicalWrites":0,"keychainOperations":0,"signingOperations":0,
              "writerAuthority":"HOLD_NOT_PROVEN","signerAuthority":"HOLD_NOT_PROVEN",
              "candidates":[], "scanned":0, "skipped":0}
    if not root.is_dir() or root.is_symlink():
        result["state"]="HOLD_INVALID_ROOT"; return result
    root = root.resolve()
    stop = False
    for base, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink())
        for name in sorted(names):
            p=Path(base)/name
            if p.suffix.lower() not in ALLOWED:
                continue
            if result["scanned"] >= MAX_FILES:
                stop=True;break
            try:
                if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_BYTES:
                    result["skipped"]+=1;continue
                data=p.read_bytes()
            except OSError:
                result["skipped"]+=1;continue
            result["scanned"]+=1
            tags=[]
            if WRITER.search(data): tags.append("P02_WRITER_SOURCE_CANDIDATE")
            if SIGNER.search(data): tags.append("SIGNER_BUILD_SOURCE_CANDIDATE")
            if tags:
                result["candidates"].append({"path":str(p.relative_to(root)),
                                              "sha256":hashlib.sha256(data).hexdigest(),
                                              "bytes":len(data),"tags":tags})
                if len(result["candidates"])>=MAX_RESULTS:
                    stop=True;break
        if stop:break
    result["truncated"]=stop
    result["state"]="PASS_BOUNDED_SOURCE_CANDIDATES_ONLY__AUTHORITY_HOLD"
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path.home()/"Enguru/Projects/Engurulaboratuvari")
    ap.add_argument("--archive",type=Path,default=Path.home()/"Desktop/AudiV13")
    args=ap.parse_args()
    result=inspect(args.root)
    if not args.archive.is_dir() or args.archive.is_symlink():
        print("STATE=HOLD_ARCHIVE");return 50
    data=(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode()
    dest=args.archive/"ENGURU_P02_REAL_WRITER_SIGNER_SOURCE_DISCOVERY_V1.json"
    try:
        with dest.open("xb") as out: out.write(data)
    except FileExistsError:
        print("STATE=HOLD_EXISTING_OUTPUT_NO_OVERWRITE");return 50
    print("STATE="+result["state"])
    print("SCANNED="+str(result["scanned"]))
    print("CANDIDATES="+str(len(result["candidates"])))
    print("TRUNCATED="+str(result.get("truncated",False)))
    print("REPORT="+str(dest))
    print("REPORT_SHA256="+hashlib.sha256(data).hexdigest())
    print("NATIVE_AUTHORITY=HOLD P02=0/12_HOLD VERIFIED_FINISH=HOLD")
    return 0 if result["state"].startswith("PASS_BOUNDED") else 50

if __name__=="__main__":
    raise SystemExit(main())
