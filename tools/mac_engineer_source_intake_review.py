#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineer™ v0.6 — source hygiene + canonical intake review.

Read-only. Reviews the historical local handoff source against the current runtime,
identifies secret/binary/cache risks, and produces an evidence-backed intake manifest.
It never copies files into Git or chooses an authoritative side for divergent files.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any


SOURCE_SUFFIXES = {
    ".py", ".swift", ".html", ".css", ".js", ".mjs", ".json",
    ".yaml", ".yml", ".toml", ".plist", ".sh", ".command", ".md", ".txt",
}
RUNTIME_SOURCE_NAMES = {
    "app.py", "provider.py", "repo_manager.py", "backup_manager.py",
    "local_ci.py", "local_gitvault.py", "repair.py", "doctor.py",
    "requirements.txt", "index.html",
}
SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules", ".cache",
    "DerivedData", "build", "dist",
}
PROHIBITED_SUFFIXES = {
    ".zip", ".tar", ".gz", ".tgz", ".7z", ".dmg", ".pkg", ".iso",
    ".pyc", ".pyo", ".o", ".a", ".so", ".dylib",
}
SECRET_FILENAME_TOKENS = (
    ".env", "credentials", "credential", "secret", "token", "apikey",
    "api_key", "private_key", "id_rsa",
)
SECRET_PATTERNS = [
    ("OPENAI_STYLE_KEY", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b")),
    ("AWS_ACCESS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("PRIVATE_KEY_BLOCK", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("GENERIC_SECRET_ASSIGNMENT", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*[\"']?[A-Za-z0-9_\-./+=]{12,}"
    )),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rec(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "relative_path": str(path.relative_to(root)),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def looks_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return True
    if b"\x00" in chunk:
        return True
    if not chunk:
        return False
    textish = sum(1 for b in chunk if b in b"\n\r\t\f\b" or 32 <= b <= 126 or b >= 128)
    return (textish / len(chunk)) < 0.85


def scan_tree(root: Path) -> dict[str, Any]:
    safe: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    secret_findings: list[dict[str, Any]] = []
    swift_sources: list[dict[str, Any]] = []
    app_bundles: list[str] = []

    if not root.exists():
        return {
            "exists": False,
            "safe": safe,
            "excluded": excluded,
            "secret_findings": secret_findings,
            "swift_sources": swift_sources,
            "app_bundles": app_bundles,
        }

    for current, dirs, files in os.walk(root):
        cur = Path(current)
        for d in list(dirs):
            if d in SKIP_DIRS or d.startswith("."):
                dirs.remove(d)
                continue
            if d.endswith(".app"):
                app_bundles.append(str(cur / d))
                dirs.remove(d)

        for name in files:
            path = cur / name
            if path.is_symlink() or not path.is_file():
                continue
            lower = name.lower()
            suffix = path.suffix.lower()

            if lower in {".ds_store"}:
                excluded.append({"path": str(path), "reason": "OS_METADATA"})
                continue
            if suffix in PROHIBITED_SUFFIXES:
                excluded.append({"path": str(path), "reason": "BINARY_OR_ARCHIVE"})
                continue
            if any(token in lower for token in SECRET_FILENAME_TOKENS):
                secret_findings.append({"path": str(path), "rule": "SENSITIVE_FILENAME"})
            if suffix not in SOURCE_SUFFIXES:
                excluded.append({"path": str(path), "reason": "UNRECOGNIZED_SUFFIX"})
                continue
            if looks_binary(path):
                excluded.append({"path": str(path), "reason": "BINARY_CONTENT"})
                continue

            record = rec(path, root)
            safe.append(record)
            if suffix == ".swift":
                swift_sources.append(record)

            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for rule, pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    secret_findings.append({"path": str(path), "rule": rule})

    return {
        "exists": True,
        "safe": safe,
        "excluded": excluded,
        "secret_findings": sorted(
            {json.dumps(x, sort_keys=True) for x in secret_findings}
        ),
        "swift_sources": swift_sources,
        "app_bundles": app_bundles,
    }


def normalize_secret_findings(items: list[str]) -> list[dict[str, Any]]:
    return [json.loads(x) for x in items]


def runtime_files(root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not root.exists():
        return out
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        cur = Path(current)
        for name in files:
            path = cur / name
            if not path.is_file() or path.is_symlink():
                continue
            if name in RUNTIME_SOURCE_NAMES or path.suffix.lower() in {".py", ".html", ".json", ".yaml", ".yml", ".plist", ".sh"}:
                if looks_binary(path):
                    continue
                out.append(rec(path, root))
    return out


def source_index(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    idx: dict[str, list[dict[str, Any]]] = {}
    for item in records:
        rel = Path(item["relative_path"])
        keys = {rel.name}
        if len(rel.parts) >= 2:
            keys.add("/".join(rel.parts[-2:]))
        if len(rel.parts) >= 3:
            keys.add("/".join(rel.parts[-3:]))
        for key in keys:
            idx.setdefault(key, []).append(item)
    return idx


def compare_runtime(runtime: list[dict[str, Any]], source: list[dict[str, Any]]) -> dict[str, Any]:
    idx = source_index(source)
    exact: list[dict[str, Any]] = []
    divergent: list[dict[str, Any]] = []
    runtime_only: list[dict[str, Any]] = []

    for item in runtime:
        rel = Path(item["relative_path"])
        keys: list[str] = []
        if len(rel.parts) >= 3:
            keys.append("/".join(rel.parts[-3:]))
        if len(rel.parts) >= 2:
            keys.append("/".join(rel.parts[-2:]))
        keys.append(rel.name)

        candidates: list[dict[str, Any]] = []
        seen: set[str] = set()
        for key in keys:
            for candidate in idx.get(key, []):
                if candidate["path"] not in seen:
                    candidates.append(candidate)
                    seen.add(candidate["path"])

        same = [x for x in candidates if x["sha256"] == item["sha256"]]
        if same:
            exact.append({"runtime": item, "source_matches": same[:10]})
        elif candidates:
            divergent.append({"runtime": item, "source_candidates": candidates[:10]})
        else:
            runtime_only.append({"runtime": item})

    return {
        "exact": exact,
        "divergent": divergent,
        "runtime_only": runtime_only,
        "counts": {
            "runtime_total": len(runtime),
            "exact": len(exact),
            "divergent": len(divergent),
            "runtime_only": len(runtime_only),
        },
    }


def main() -> int:
    home = Path.home()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-root",
        type=Path,
        default=home / "Desktop" / "ENGURU_Mac_Engineer_Project_Handoff_v1",
    )
    parser.add_argument(
        "--runtime-root",
        type=Path,
        default=home / "Enguru" / "Runtime" / "MacEngineer" / "runtime",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=home / "Enguru" / "Evidence" / "MacEngineer" / "v0.6" / "package6-source-intake-review.json",
    )
    args = parser.parse_args()

    source = scan_tree(args.source_root)
    source["secret_findings"] = normalize_secret_findings(source["secret_findings"])
    runtime = runtime_files(args.runtime_root)
    comparison = compare_runtime(runtime, source["safe"])

    issues: list[str] = []
    if not source["exists"]:
        issues.append("HISTORICAL_SOURCE_PACKAGE_NOT_FOUND")
    if source["secret_findings"]:
        issues.append("SECRET_OR_SENSITIVE_MATERIAL_REVIEW_REQUIRED")
    if not source["swift_sources"]:
        issues.append("NATIVE_SWIFT_SOURCE_NOT_FOUND")
    if not source["safe"]:
        issues.append("NO_SAFE_SOURCE_FILES")
    if comparison["counts"]["divergent"] or comparison["counts"]["runtime_only"]:
        issues.append("RUNTIME_DELTA_AUTHORITY_REVIEW_REQUIRED")

    payload = {
        "schema": "enguru.mac-engineer.source-intake-review/v0.1",
        "observed_at": now(),
        "source_root": str(args.source_root),
        "runtime_root": str(args.runtime_root),
        "source": {
            "safe_file_count": len(source["safe"]),
            "safe_files": source["safe"],
            "swift_sources": source["swift_sources"],
            "excluded": source["excluded"],
            "app_bundles": source["app_bundles"],
            "secret_findings": source["secret_findings"],
        },
        "runtime_comparison": comparison,
        "issues": issues,
        "state": "PASS" if not issues else "HOLD",
        "truth_boundary": (
            "This review identifies files eligible for canonical intake and unresolved runtime deltas. "
            "It does not copy files, expose secret values, or choose source-vs-runtime authority."
        ),
        "next_action": (
            "Canonicalize the reviewed source set in GitHub with an explicit provenance manifest."
            if not issues
            else "Resolve only the reported sensitive-material or runtime-delta authority questions before canonical intake."
        ),
    }

    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "state": payload["state"],
        "issues": issues,
        "evidence": str(args.evidence),
        "source_root": payload["source_root"],
        "safe_file_count": payload["source"]["safe_file_count"],
        "swift_source_count": len(payload["source"]["swift_sources"]),
        "excluded_count": len(payload["source"]["excluded"]),
        "app_bundle_count": len(payload["source"]["app_bundles"]),
        "secret_findings": payload["source"]["secret_findings"],
        "runtime_comparison": comparison["counts"],
        "divergent_runtime_files": [
            x["runtime"]["relative_path"] for x in comparison["divergent"]
        ],
        "runtime_only_files": [
            x["runtime"]["relative_path"] for x in comparison["runtime_only"]
        ],
        "next_action": payload["next_action"],
    }, ensure_ascii=False, indent=2))
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
