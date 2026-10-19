"""Read-only OSi delivery dry run against an independently verified GitHub inventory.

Does not fetch, copy, modify or execute candidate files. Never implies native acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

def assess(osi_root, inventory_path):
    result={"state":"HOLD_GUVENLI_DUR","verifiedFinish":"HOLD","nativeAuthority":"HOLD","writes":0,"items":[],"blockers":[]}
    try:
        root=Path(osi_root).resolve(strict=True)
        obj=json.loads(Path(inventory_path).read_text(encoding="utf-8"))
        if obj.get("schema")!="enguru.suzgec.v24.github-delivery-inventory/v1" or obj.get("state")!="PASS_BOUNDED_GITHUB_SOURCE_INVENTORY_ONLY":
            raise ValueError("UNVERIFIED_INVENTORY")
        files=obj.get("files")
        if not isinstance(files,dict) or not files: raise ValueError("EMPTY_FILES")
        for name, expected in sorted(files.items()):
            if not isinstance(name,str) or not isinstance(expected,str) or len(expected)!=64 or any(c not in "0123456789abcdef" for c in expected):
                raise ValueError("INVALID_ENTRY")
            pos=PurePosixPath(name)
            if pos.is_absolute() or ".." in pos.parts or pos.as_posix()!=name or name.startswith("./"):
                raise ValueError("UNSAFE_PATH")
            path=root.joinpath(*pos.parts)
            if any(p.is_symlink() for p in [path,*list(path.parents)[:len(pos.parts)]]):
                status="HOLD_SYMLINK"
            elif not path.exists():
                status="MISSING_NEEDS_EXPLICIT_DELIVERY"
            elif not path.is_file() or not path.resolve().is_relative_to(root):
                status="HOLD_UNSAFE_TARGET"
            else:
                status="MATCH" if hashlib.sha256(path.read_bytes()).hexdigest()==expected else "HOLD_EXISTING_SOURCE_DIFFERS"
            result["items"].append({"path":name,"status":status})
        result["blockers"]=[i for i in result["items"] if i["status"]!="MATCH"]
        result["state"]="PASS_READ_ONLY_IDENTICAL_SOURCES_ONLY" if not result["blockers"] else "HOLD_GUVENLI_DUR"
    except (OSError,ValueError,TypeError,AttributeError) as e:
        result["blockers"].append({"reason":str(e)})
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--osi-root",required=True)
    p.add_argument("--inventory",required=True)
    a=p.parse_args()
    res=assess(a.osi_root,a.inventory)
    print(json.dumps(res,ensure_ascii=False,sort_keys=True))
    return 0 if res["state"]=="PASS_READ_ONLY_IDENTICAL_SOURCES_ONLY" else 50
if __name__=="__main__":
    raise SystemExit(main())
