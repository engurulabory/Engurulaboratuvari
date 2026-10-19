"""ENGURU v2.4 Terminal Twin parity: bounded read-only source and tool fingerprint.

OSi snapshots stay local until the owner reviews/redacts them. No issuer,
grant, writer, keychain contents, environment values or user paths are exported.
"""
import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

SCHEMA="enguru.suzgec.v24.terminal-twin-fingerprint/v1"
REQUIRED=("tools/enguru_suzgec_v24_source_preflight.py",
          "tools/enguru_suzgec_v24_presend_source_binding.py",
          "tools/enguru_suzgec_v24_github_test_terminal.py")
HEX64=re.compile(r"^[0-9a-f]{64}$")

def fingerprint(root, paths=REQUIRED):
    root=Path(root).resolve(strict=True)
    if not paths or len(set(paths))!=len(paths):
        raise ValueError("INVALID_SOURCE_SCOPE")
    sources={}
    for name in paths:
        if not isinstance(name,str):
            raise ValueError("INVALID_SOURCE_PATH")
        part=PurePosixPath(name)
        if part.is_absolute() or ".." in part.parts or part.as_posix()!=name or name.startswith("./"):
            raise ValueError("UNSAFE_SOURCE_PATH")
        path=root.joinpath(*part.parts)
        if path.is_symlink() or not path.resolve(strict=True).is_relative_to(root) or not path.is_file():
            raise ValueError("UNSAFE_SOURCE")
        sources[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    return {"schema":SCHEMA,"host":"OSi_OR_GITHUB_UNATTESTED","os":platform.system(),
            "architecture":platform.machine(),"python_major_minor":".".join(map(str,sys.version_info[:2])),
            "source_sha256":sources,"verifiedFinish":"HOLD"}

def compare(osi, github):
    problems=[]
    for label,item in (("OSi",osi),("GITHUB",github)):
        if not isinstance(item,dict) or item.get("schema")!=SCHEMA:
            problems.append(label+"_INVALID_SCHEMA")
            continue
        src=item.get("source_sha256")
        if not isinstance(src,dict) or not src or not all(isinstance(k,str) and isinstance(v,str) and HEX64.fullmatch(v) for k,v in src.items()):
            problems.append(label+"_INVALID_SOURCE_SCOPE")
        if item.get("verifiedFinish")!="HOLD":
            problems.append(label+"_FALSE_AUTHORITY")
    if not problems:
        for key in ("os","architecture","python_major_minor"):
            if osi.get(key)!=github.get(key):
                problems.append("ENVIRONMENT_DIFFERENCE_"+key)
        if osi["source_sha256"]!=github["source_sha256"]:
            problems.append("SOURCE_PARITY_DIFFERENCE")
    return {"state":"PASS_BOUNDED_FINGERPRINT_PARITY_ONLY" if not problems else "HOLD_GUVENLI_DUR",
            "reasons":problems,"realOSiSourceAttestation":"HOLD_NOT_ATTESTED",
            "executionBehaviorParity":"HOLD_NOT_TESTED","nativeAuthority":"HOLD",
            "verifiedFinish":"HOLD"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True)
    ap.add_argument("--out")
    ap.add_argument("--compare-osi")
    args=ap.parse_args()
    try:
        candidate=fingerprint(args.root)
        result=compare(json.loads(Path(args.compare_osi).read_text(encoding="utf-8")),candidate) if args.compare_osi else candidate
        if args.out:
            Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True),encoding="utf-8")
        print(json.dumps(result,sort_keys=True))
        return 0 if result.get("state")=="PASS_BOUNDED_FINGERPRINT_PARITY_ONLY" or not args.compare_osi else 50
    except (OSError,ValueError,TypeError,KeyError) as e:
        print(json.dumps({"state":"HOLD_GUVENLI_DUR","reason":type(e).__name__,"verifiedFinish":"HOLD"}))
        return 50

if __name__=="__main__":
    raise SystemExit(main())
