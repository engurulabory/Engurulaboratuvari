#!/usr/bin/env python3
"""ENGURU V6.9 V3 source-bound CI preflight. Safe HOLD until all 10 source modules are committed."""
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[4]
MANIFEST=pathlib.Path(__file__).with_name("source_manifest.json")
def main():
    entries=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if len(entries)!=10:
        print("HOLD_MANIFEST_COUNT");return 1
    bad=[]
    for entry in entries:
        path=(ROOT/entry["path"]).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            bad.append((entry["id"],"MISSING_OR_OUTSIDE"));continue
        observed=hashlib.sha256(path.read_bytes()).hexdigest()
        if observed!=entry["source_sha256"]:bad.append((entry["id"],"SHA_DRIFT"))
    if bad:
        for n,why in bad:print("HOLD_SOURCE",n,why)
        print("V3_CI=HOLD_EXACT_SOURCE");return 1
    print("V3_SOURCE_PINS=10/10_PASS");return 0
if __name__=="__main__":sys.exit(main())
