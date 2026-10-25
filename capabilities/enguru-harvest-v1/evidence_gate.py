"""Independent byte-level evidence validation; no dynamic execution."""
import hashlib
import json
from pathlib import Path

def validate(manifest, assets):
    if not isinstance(manifest, dict) or not isinstance(assets, dict):
        return {"state":"HOLD","reason":"BAD_INPUT"}
    required=("source","test","real_task","review")
    for kind in required:
        desc=manifest.get(kind)
        if not isinstance(desc,dict):
            return {"state":"HOLD","reason":"MISSING_"+kind.upper()}
        path=desc.get("path")
        pin=desc.get("sha256")
        if not isinstance(path,str) or path not in assets or not isinstance(assets[path],bytes):
            return {"state":"HOLD","reason":"MISSING_BYTES_"+kind.upper()}
        if not isinstance(pin,str) or len(pin)!=64:
            return {"state":"HOLD","reason":"INVALID_PIN_"+kind.upper()}
        if hashlib.sha256(assets[path]).hexdigest()!=pin:
            return {"state":"HOLD","reason":"HASH_MISMATCH_"+kind.upper()}
        if kind!="source":
            try:
                receipt=json.loads(assets[path])
            except (ValueError, UnicodeDecodeError):
                return {"state":"HOLD","reason":"INVALID_RECEIPT_"+kind.upper()}
            if not isinstance(receipt,dict) or receipt.get("result")!="PASS" or receipt.get("source_sha256")!=manifest["source"].get("sha256"):
                return {"state":"HOLD","reason":"RECEIPT_CONTENT_"+kind.upper()}
    return {"state":"EVIDENCE_CANDIDATE","reason":"BYTES_MATCH; AUTHORITY_AND_INDEPENDENCE_UNVERIFIED"}

def safe_local_assets(directory, manifest):
    """Read only simple relative paths from a fixed root; symlinks are rejected."""
    root=Path(directory).resolve()
    assets={}
    for desc in manifest.values():
        if not isinstance(desc,dict):
            continue
        name=desc.get("path")
        if not isinstance(name,str) or Path(name).is_absolute() or ".." in Path(name).parts:
            continue
        p=root/name
        if p.is_symlink() or not p.is_file() or p.resolve().parent!=root:
            continue
        assets[name]=p.read_bytes()
    return assets
