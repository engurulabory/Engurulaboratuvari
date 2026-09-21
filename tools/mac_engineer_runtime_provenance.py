#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineer™ v0.6 — installed runtime provenance discovery.

Non-destructive. It fingerprints the installed app/runtime and reports whether an
evidence-backed source/version binding already exists. It never manufactures one.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
from typing import Any


SHA40 = re.compile(r"\b[0-9a-f]{40}\b", re.IGNORECASE)
META_NAMES = {
    "manifest.json", "release.json", "build.json", "version.json",
    "provenance.json", "runtime-manifest.json", "runtime_manifest.json",
    "build-info.json", "build_info.json", "source.json",
}
TEXT_SUFFIXES = {".json", ".yaml", ".yml", ".toml", ".plist", ".txt", ".md", ".py", ".sh"}
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".cache"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(*args: str, cwd: Path | None = None) -> tuple[int, str, str]:
    p = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_record(path: Path, root: Path | None = None) -> dict[str, Any]:
    stat = path.stat()
    rec = {
        "path": str(path),
        "size": stat.st_size,
        "sha256": sha256_file(path),
    }
    if root is not None:
        try:
            rec["relative_path"] = str(path.relative_to(root))
        except ValueError:
            pass
    return rec


def git_truth(repo: Path) -> dict[str, Any]:
    values: dict[str, Any] = {"available": (repo / ".git").exists()}
    if not values["available"]:
        return values
    for key, cmd in {
        "head": ("git", "rev-parse", "HEAD"),
        "origin_main": ("git", "rev-parse", "origin/main"),
        "branch": ("git", "branch", "--show-current"),
        "status": ("git", "status", "--porcelain"),
        "origin": ("git", "remote", "get-url", "origin"),
    }.items():
        code, out, err = run(*cmd, cwd=repo)
        values[key] = out if code == 0 else None
        if code != 0:
            values[key + "_error"] = err
    values["clean"] = not bool(values.get("status"))
    values["exact_origin_main"] = bool(values.get("head")) and values.get("head") == values.get("origin_main")
    return values


def app_identity(app: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"path": str(app), "exists": app.exists()}
    if not app.exists():
        return result
    plist_path = app / "Contents" / "Info.plist"
    result["info_plist"] = str(plist_path)
    if plist_path.exists():
        with plist_path.open("rb") as fh:
            plist = plistlib.load(fh)
        result.update({
            "bundle_id": plist.get("CFBundleIdentifier", ""),
            "display_name": plist.get("CFBundleDisplayName") or plist.get("CFBundleName") or "",
            "bundle_version": plist.get("CFBundleVersion", ""),
            "short_version": plist.get("CFBundleShortVersionString", ""),
            "executable_name": plist.get("CFBundleExecutable", ""),
        })
        exe_name = str(result.get("executable_name", ""))
        if exe_name:
            exe = app / "Contents" / "MacOS" / exe_name
            result["executable"] = file_record(exe) if exe.exists() else {"path": str(exe), "exists": False}
    return result


def scan_runtime(root: Path, max_files: int = 400) -> dict[str, Any]:
    result: dict[str, Any] = {"path": str(root), "exists": root.exists(), "files": [], "metadata_candidates": []}
    if not root.exists():
        return result

    git = git_truth(root)
    if git.get("available"):
        result["git"] = git

    files: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    count = 0
    for current, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        current_path = Path(current)
        for name in names:
            path = current_path / name
            if path.is_symlink() or not path.is_file():
                continue
            if count >= max_files:
                result["truncated"] = True
                break
            if path.suffix.lower() in TEXT_SUFFIXES or name in META_NAMES:
                rec = file_record(path, root)
                files.append(rec)
                count += 1
                if name in META_NAMES or any(token in name.lower() for token in ("manifest", "release", "version", "build", "provenance", "source")):
                    try:
                        text = path.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        text = ""
                    metadata.append({
                        **rec,
                        "sha40_candidates": sorted(set(SHA40.findall(text)))[:20],
                        "preview": text[:1000],
                    })
        if result.get("truncated"):
            break
    result["files"] = files
    result["metadata_candidates"] = metadata
    return result


def process_matches() -> list[dict[str, str]]:
    code, out, err = run("ps", "-axo", "pid=,command=")
    if code != 0:
        return [{"error": err or "ps_failed"}]
    found: list[dict[str, str]] = []
    for line in out.splitlines():
        lowered = line.lower()
        if "engurumacengineer" in lowered or "/enguru/runtime/macengineer/" in lowered:
            pid, _, command = line.strip().partition(" ")
            found.append({"pid": pid.strip(), "command": command.strip()[:1000]})
    return found


def find_existing_binding(app_info: dict[str, Any], runtime_info: dict[str, Any], canonical: dict[str, Any]) -> dict[str, Any]:
    expected_sha = str(canonical.get("head") or "")
    findings: list[dict[str, Any]] = []

    if runtime_info.get("git", {}).get("head"):
        head = runtime_info["git"]["head"]
        findings.append({
            "type": "runtime_git_head",
            "value": head,
            "matches_canonical": head == expected_sha,
        })

    for meta in runtime_info.get("metadata_candidates", []):
        for sha in meta.get("sha40_candidates", []):
            findings.append({
                "type": "metadata_sha",
                "path": meta.get("path"),
                "value": sha,
                "matches_canonical": sha == expected_sha,
            })

    matched = [x for x in findings if x.get("matches_canonical") is True]
    return {
        "canonical_head": expected_sha,
        "signals": findings,
        "matched_signals": matched,
        "bound": bool(matched),
    }


def main() -> int:
    home = Path.home()
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--app", type=Path, default=home / "Applications" / "ENGÜRÜ Mac Engineer.app")
    parser.add_argument("--runtime-root", type=Path, default=home / "Enguru" / "Runtime" / "MacEngineer")
    parser.add_argument(
        "--evidence",
        type=Path,
        default=home / "Enguru" / "Evidence" / "MacEngineer" / "v0.6" / "package6-runtime-provenance.json",
    )
    args = parser.parse_args()

    canonical = git_truth(args.repo)
    app = app_identity(args.app)
    runtime = scan_runtime(args.runtime_root)
    binding = find_existing_binding(app, runtime, canonical)

    issues: list[str] = []
    if not canonical.get("exact_origin_main") or not canonical.get("clean"):
        issues.append("CANONICAL_EXACT_MAIN_REQUIRED")
    if not app.get("exists"):
        issues.append("MAC_ENGINEER_APP_NOT_FOUND")
    if app.get("bundle_id") != "com.engurumaya.macengineer":
        issues.append("UNEXPECTED_MAC_ENGINEER_BUNDLE_ID")
    if not runtime.get("exists"):
        issues.append("MAC_ENGINEER_RUNTIME_ROOT_NOT_FOUND")
    if not binding.get("bound"):
        issues.append("RUNTIME_PROVENANCE_UNBOUND")

    payload = {
        "schema": "enguru.mac-engineer.runtime-provenance/v0.1",
        "observed_at": now(),
        "canonical_checkout": canonical,
        "app": app,
        "runtime": runtime,
        "processes": process_matches(),
        "binding": binding,
        "issues": issues,
        "state": "PASS" if not issues else "HOLD",
        "truth_boundary": (
            "PASS requires an existing evidence-backed source/version signal matching the canonical GitHub HEAD. "
            "This tool fingerprints and discovers; it does not create provenance or infer source identity from names."
        ),
        "next_action": (
            "Proceed to Package 6 real-task commissioning."
            if not issues
            else "Reconcile only the reported provenance gap before real-task commissioning."
        ),
    }

    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": payload["state"],
        "issues": issues,
        "evidence": str(args.evidence),
        "canonical_head": canonical.get("head"),
        "app": {
            "path": app.get("path"),
            "bundle_id": app.get("bundle_id"),
            "short_version": app.get("short_version"),
            "bundle_version": app.get("bundle_version"),
            "executable": app.get("executable"),
        },
        "runtime_path": runtime.get("path"),
        "runtime_git": runtime.get("git"),
        "metadata_candidates": runtime.get("metadata_candidates"),
        "binding": binding,
        "processes": payload["processes"],
        "next_action": payload["next_action"],
    }, ensure_ascii=False, indent=2))
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
