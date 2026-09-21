#!/usr/bin/env python3
"""Read-only filesystem topology audit for ENGÜRÜ Mac Engineer™."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
import unicodedata
from typing import Any

HOME = Path.home()
CANONICAL = {
    "control_plane": HOME / "Enguru" / "Projects" / "Engurulaboratuvari",
    "product_source": HOME / "Enguru" / "Projects" / "enguru-mac-engineer",
    "runtime": HOME / "Enguru" / "Runtime" / "MacEngineer",
    "installed_app": HOME / "Applications" / "ENGÜRÜ Mac Engineer.app",
    "evidence": HOME / "Enguru" / "Evidence" / "MacEngineer",
}
KNOWN_SECONDARY = {
    str(HOME / "Desktop" / "ENGURU_Mac_Engineer_Project_Handoff_v1"): "LEGACY_PROVENANCE_SOURCE",
    str(HOME / "Enguru" / "Backup" / "MacEngineer"): "BACKUP_ROOT",
    str(HOME / "Enguru" / "Runtime" / "MacEngineer" / "App" / "ENGÜRÜ Mac Engineer.app"): "RUNTIME_BUILD_ARTIFACT",
}
TOKENS = ("macengineer", "mac-engineer", "mac engineer", "engürü mac engineer", "enguru_mac_engineer")


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def app_info(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    plist = path / "Contents" / "Info.plist"
    if plist.exists():
        try:
            with plist.open("rb") as f:
                data = plistlib.load(f)
            out["bundle_id"] = data.get("CFBundleIdentifier", "")
            out["version"] = data.get("CFBundleShortVersionString", "")
            exe_name = data.get("CFBundleExecutable", "")
            out["executable_name"] = exe_name
            exe = path / "Contents" / "MacOS" / str(exe_name)
            if exe.is_file():
                out["executable_sha256"] = sha256_file(exe)
        except Exception as exc:
            out["plist_error"] = type(exc).__name__
    return out


def git_info(path: Path) -> dict[str, Any]:
    if not (path / ".git").exists():
        return {}
    def run(*cmd: str) -> str:
        p = subprocess.run(cmd, cwd=path, text=True, capture_output=True, check=False)
        return p.stdout.strip() if p.returncode == 0 else ""
    return {
        "head": run("git", "rev-parse", "HEAD"),
        "branch": run("git", "branch", "--show-current"),
        "origin": run("git", "remote", "get-url", "origin"),
        "status": run("git", "status", "--porcelain"),
    }


def is_related(path: Path) -> bool:
    name = path.name.lower()
    return (
        any(token in name for token in TOKENS)
        or path.name.startswith(".enguru-mac-engineer.bootstrap-")
    )


def is_mac_engineer_app(path: Path) -> bool:
    if not path.name.endswith(".app"):
        return False
    info = app_info(path)
    return info.get("bundle_id") == "com.engurumaya.macengineer"


def within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def normalized_text(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def canonical_process_command(command: str) -> bool:
    normalized = normalized_text(command)
    return any(
        normalized_text(str(CANONICAL[key])) in normalized
        for key in ("installed_app", "runtime")
    )


def classify(path: Path) -> tuple[str, str]:
    rp = str(path.resolve()) if path.exists() else str(path)
    for role, cp in CANONICAL.items():
        try:
            if path.resolve() == cp.resolve():
                return "CANONICAL", role
        except Exception:
            pass

    for known, label in KNOWN_SECONDARY.items():
        kp = Path(known)
        try:
            if path.resolve() == kp.resolve() or within(path, kp):
                return "KNOWN_SECONDARY", label
        except Exception:
            pass

    for role in ("control_plane", "product_source", "runtime", "evidence"):
        cp = CANONICAL[role]
        try:
            if within(path, cp):
                return "CANONICAL_CHILD", role
        except Exception:
            pass

    if path.name.startswith(".enguru-mac-engineer.bootstrap-"):
        return "STALE_TEMP", "bootstrap_staging"

    if path.is_symlink():
        try:
            target = path.resolve()
            if target == CANONICAL["installed_app"].resolve():
                return "KNOWN_SECONDARY", "SYMLINK_ALIAS_TO_CANONICAL_APP"
        except Exception:
            pass

    return "UNKNOWN", "requires_review"


def scan() -> list[dict[str, Any]]:
    roots = [
        HOME / "Enguru",
        HOME / "Applications",
        HOME / "Desktop",
        HOME / "Library" / "LaunchAgents",
    ]
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()

    for root in roots:
        if not root.exists():
            continue
        for current, dirs, files in os.walk(root):
            cur = Path(current)
            depth = len(cur.relative_to(root).parts)
            if depth > 8:
                dirs[:] = []
                continue

            for name in list(dirs):
                p = cur / name
                app_match = name.endswith(".app") and is_mac_engineer_app(p)
                if is_related(p) or app_match:
                    key = str(p.absolute())
                    if key not in seen:
                        state, reason = classify(p)
                        item: dict[str, Any] = {
                            "path": str(p),
                            "kind": "directory",
                            "classification": state,
                            "reason": reason,
                            "is_symlink": p.is_symlink(),
                        }
                        if name.endswith(".app"):
                            item["kind"] = "app"
                            item.update(app_info(p))
                            dirs.remove(name)
                        item["git"] = git_info(p)
                        findings.append(item)
                        seen.add(key)

            for name in files:
                p = cur / name
                if is_related(p):
                    key = str(p.absolute())
                    if key not in seen:
                        state, reason = classify(p)
                        findings.append({
                            "path": str(p),
                            "kind": "symlink" if p.is_symlink() else "file",
                            "classification": state,
                            "reason": reason,
                            "is_symlink": p.is_symlink(),
                            "symlink_target": str(p.resolve()) if p.is_symlink() else "",
                        })
                        seen.add(key)

    # Always record canonical roots even if their names do not match token scan.
    for role, p in CANONICAL.items():
        key = str(p.absolute())
        if key not in seen:
            findings.append({
                "path": str(p),
                "kind": "canonical_root",
                "classification": "CANONICAL" if p.exists() else "MISSING_CANONICAL",
                "reason": role,
                "exists": p.exists(),
                "git": git_info(p) if p.exists() else {},
            })
            seen.add(key)

    return sorted(findings, key=lambda x: x["path"])


def processes() -> list[dict[str, Any]]:
    p = subprocess.run(["ps", "-axo", "pid=,command="], text=True, capture_output=True, check=False)
    out: list[dict[str, Any]] = []
    if p.returncode != 0:
        return out
    for line in p.stdout.splitlines():
        low = line.lower()
        if "engurumacengineer" in low or "/enguru/runtime/macengineer/" in low:
            pid, _, command = line.strip().partition(" ")
            classification = (
                "CANONICAL_PROCESS"
                if canonical_process_command(command)
                else "UNKNOWN_PROCESS_PATH"
            )
            out.append({"pid": pid, "command": command, "classification": classification})
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidence",
        type=Path,
        default=HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6" / "package6-layout-audit.json",
    )
    args = parser.parse_args()

    findings = scan()
    proc = processes()
    unknown = [x for x in findings if x["classification"] == "UNKNOWN"]
    stale_temp = [x for x in findings if x["classification"] == "STALE_TEMP"]
    missing = [x for x in findings if x["classification"] == "MISSING_CANONICAL"]
    unknown_proc = [
        x
        for x in proc
        if x["classification"] != "CANONICAL_PROCESS"
    ]

    issues: list[str] = []
    if unknown:
        issues.append("UNKNOWN_MAC_ENGINEER_STRUCTURES")
    if stale_temp:
        issues.append("STALE_BOOTSTRAP_TEMP_STRUCTURES")
    if missing:
        issues.append("CANONICAL_PATH_MISSING")
    if unknown_proc:
        issues.append("UNKNOWN_ACTIVE_PROCESS_PATH")

    payload = {
        "schema": "enguru.mac-engineer.layout-audit/v1",
        "observed_at": now(),
        "state": "PASS" if not issues else "HOLD",
        "issues": issues,
        "canonical_paths": {k: str(v) for k, v in CANONICAL.items()},
        "findings": findings,
        "processes": proc,
        "summary": {
            "total_findings": len(findings),
            "canonical": sum(
                x["classification"] in {"CANONICAL", "CANONICAL_CHILD"}
                for x in findings
            ),
            "canonical_roots": sum(
                x["classification"] == "CANONICAL"
                for x in findings
            ),
            "canonical_children": sum(
                x["classification"] == "CANONICAL_CHILD"
                for x in findings
            ),
            "known_secondary": sum(
                x["classification"] == "KNOWN_SECONDARY"
                for x in findings
            ),
            "unknown": len(unknown),
            "stale_temp": len(stale_temp),
            "missing_canonical": len(missing),
            "unknown_processes": len(unknown_proc),
        },
        "cleanup_candidates": [x["path"] for x in stale_temp + unknown],
        "truth_boundary": (
            "Read-only inventory. PASS means no unknown/stale Mac Engineer structures were observed in bounded roots. "
            "Canonical descendants of control-plane/product-source/runtime/evidence roots are classified explicitly. "
            "Known backup, provenance and runtime-build artifacts are reported but do not count as drift. "
            "No path is deleted or moved by this audit."
        ),
        "next_action": (
            "Review only cleanup_candidates before any deletion."
            if issues else
            "Layout is clean enough to proceed to dedicated GitHub product-source publication."
        ),
    }
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": payload["state"],
        "issues": issues,
        "evidence": str(args.evidence),
        "summary": payload["summary"],
        "cleanup_candidates": payload["cleanup_candidates"],
        "findings": findings,
        "processes": proc,
        "next_action": payload["next_action"],
    }, ensure_ascii=False, indent=2))
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
