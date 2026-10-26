"""ENGÜRÜ byte-level evidence checking; never grants independent authority.

Untrusted manifest and receipt assertions are constrained to EVIDENCE_CANDIDATE.
This is not signature verification, DoneCheck or Human Threshold approval.
"""
import hashlib
import json
import re
from pathlib import Path

KINDS=("source","test","real_task","review")
HEX64=re.compile(r"^[0-9a-f]{64}$")

def _hold(reason):
    return {"state":"HOLD","reason":reason}

def validate(manifest, assets):
    if not isinstance(manifest, dict) or not isinstance(assets, dict):
        return _hold("BAD_INPUT")
    used=set()
    source_pin=None
    for kind in KINDS:
        desc=manifest.get(kind)
        if not isinstance(desc,dict):
            return _hold("MISSING_"+kind.upper())
        path=desc.get("path")
        pin=desc.get("sha256")
        if not isinstance(path,str) or not path or path in used or not isinstance(assets.get(path),bytes):
            return _hold("MISSING_OR_DUPLICATE_BYTES_"+kind.upper())
        if not isinstance(pin,str) or HEX64.fullmatch(pin) is None:
            return _hold("INVALID_PIN_"+kind.upper())
        data=assets[path]
        if hashlib.sha256(data).hexdigest()!=pin:
            return _hold("HASH_MISMATCH_"+kind.upper())
        used.add(path)
        if kind=="source":
            source_pin=pin
            continue
        try:
            receipt=json.loads(data)
        except (ValueError, UnicodeDecodeError):
            return _hold("INVALID_RECEIPT_"+kind.upper())
        if (not isinstance(receipt,dict) or receipt.get("stage")!=kind or
            receipt.get("result")!="PASS" or receipt.get("source_sha256")!=source_pin):
            return _hold("RECEIPT_CONTENT_"+kind.upper())
    return {"state":"EVIDENCE_CANDIDATE","reason":"BYTE_PINS_MATCH; RECEIPT_AUTHORITY_UNVERIFIED"}

def safe_local_assets(directory, manifest):
    """Bounded read of regular, single-component filenames; no symlinks."""
    root=Path(directory).resolve()
    if not isinstance(manifest,dict):
        return {}
    assets={}
    for desc in manifest.values():
        if not isinstance(desc,dict):
            continue
        name=desc.get("path")
        if not isinstance(name,str) or not name or Path(name).name!=name or name in (".",".."):
            continue
        p=root/name
        if p.is_symlink() or not p.is_file() or p.resolve().parent!=root or p.stat().st_size>2_000_000:
            continue
        assets[name]=p.read_bytes()
    return assets
