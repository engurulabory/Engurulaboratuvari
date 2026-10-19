"""Süzgeç v2.4: source-to-prediction preflight guard; no native authority granted."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

REQUIRED = ("goal_scope_id", "source_files", "prediction_source_sha256")

def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def assess(root, manifest):
    """Pure read-only preflight. PASS never means native acceptance or Verified Finish."""
    result = {"state": "HOLD_GUVENLI_DUR", "verifiedFinish": "HOLD", "reasons": []}
    try:
        root = Path(root).resolve(strict=True)
        m = json.loads(Path(manifest).read_text(encoding="utf-8"))
        if not isinstance(m, dict) or any(k not in m for k in REQUIRED):
            raise ValueError("MANIFEST_CONTRACT")
        if not isinstance(m["goal_scope_id"], str) or not m["goal_scope_id"].strip():
            raise ValueError("GOAL_SCOPE_MISSING")
        files = m["source_files"]
        if not isinstance(files, dict) or not files:
            raise ValueError("SOURCE_LIST_MISSING")
        verified = {}
        for name, pin in files.items():
            if not isinstance(name, str) or not isinstance(pin, str):
                raise ValueError("SOURCE_ENTRY_INVALID")
            p = PurePosixPath(name)
            if p.is_absolute() or ".." in p.parts or p.as_posix() != name or name.startswith("./"):
                raise ValueError("UNSAFE_SOURCE_PATH")
            candidate = root.joinpath(*p.parts)
            if any(x.is_symlink() for x in (candidate, *list(candidate.parents)[:len(p.parts)])):
                raise ValueError("SYMLINK_SOURCE")
            resolved = candidate.resolve(strict=True)
            if not resolved.is_relative_to(root) or not resolved.is_file():
                raise ValueError("OUT_OF_SCOPE_SOURCE")
            actual = _digest(resolved)
            if len(pin) != 64 or pin.lower() != actual:
                raise ValueError("SOURCE_SHA_DRIFT")
            verified[name] = actual
        encoded = json.dumps(verified, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        source_set_sha = hashlib.sha256(encoded).hexdigest()
        if m["prediction_source_sha256"] != source_set_sha:
            raise ValueError("PREDICTION_SOURCE_STALE")
        result.update(state="PASS_SOURCE_PREFLIGHT_ONLY", source_set_sha256=source_set_sha, file_count=len(verified))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        result["reasons"].append(str(exc) if isinstance(exc, ValueError) else type(exc).__name__)
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--manifest", required=True)
    a = p.parse_args()
    r = assess(a.root, a.manifest)
    print(json.dumps(r, sort_keys=True, ensure_ascii=False))
    return 0 if r["state"] == "PASS_SOURCE_PREFLIGHT_ONLY" else 50

if __name__ == "__main__":
    raise SystemExit(main())
