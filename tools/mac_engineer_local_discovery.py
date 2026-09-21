#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineer™ v0.6 — Package 6 local discovery / commissioning preflight.

This tool is intentionally non-destructive. It discovers current Mac-local truth,
records evidence, and refuses to manufacture a commissioning PASS.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import plistlib
import subprocess
import sys
from typing import Any
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "Library", ".Trash",
    ".cache", ".npm", ".pnpm-store", "__pycache__", "DerivedData",
}
NAME_MARKERS = ("enguru", "engürü", "mac engineer", "mac-engineer", "osi")
PROCESS_MARKERS = ("enguru", "mac engineer", "mac-engineer", "shared_ai", "ollama", "osi")


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


def http_json(url: str, timeout: float = 2.0) -> dict[str, Any]:
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=timeout) as res:
            body = res.read().decode("utf-8", "replace")
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = {"raw": body[:500]}
            return {"reachable": True, "status": res.status, "payload": payload}
    except HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        return {"reachable": True, "status": exc.code, "error": body[:500]}
    except (URLError, TimeoutError, OSError) as exc:
        return {"reachable": False, "error": type(exc).__name__ + ":" + str(exc)[:240]}


def path_depth(path: Path, root: Path) -> int:
    try:
        return len(path.relative_to(root).parts)
    except ValueError:
        return 999


def discover_git_repositories(root: Path, max_depth: int = 5) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not root.exists():
        return results
    for current, dirs, _files in os.walk(root):
        current_path = Path(current)
        depth = path_depth(current_path, root)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        if depth >= max_depth:
            dirs[:] = []
        git_dir = current_path / ".git"
        if git_dir.exists():
            code, remote, _ = run("git", "remote", "get-url", "origin", cwd=current_path)
            code2, head, _ = run("git", "rev-parse", "HEAD", cwd=current_path)
            code3, branch, _ = run("git", "branch", "--show-current", cwd=current_path)
            results.append({
                "path": str(current_path),
                "origin": remote if code == 0 else "",
                "head": head if code2 == 0 else "",
                "branch": branch if code3 == 0 else "",
            })
            dirs[:] = []
    return results


def discover_apps(roots: list[Path], max_depth: int = 4) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for current, dirs, _files in os.walk(root):
            current_path = Path(current)
            depth = path_depth(current_path, root)
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            if depth >= max_depth:
                dirs[:] = []
            for name in list(dirs):
                if not name.endswith(".app"):
                    continue
                app = current_path / name
                label = name[:-4].lower()
                info: dict[str, Any] = {"path": str(app), "name": name}
                plist_path = app / "Contents" / "Info.plist"
                if plist_path.exists():
                    try:
                        with plist_path.open("rb") as fh:
                            plist = plistlib.load(fh)
                        info["bundle_id"] = plist.get("CFBundleIdentifier", "")
                        info["display_name"] = plist.get("CFBundleDisplayName") or plist.get("CFBundleName") or ""
                        info["executable"] = plist.get("CFBundleExecutable", "")
                        label += " " + str(info["bundle_id"]).lower() + " " + str(info["display_name"]).lower()
                    except Exception as exc:  # evidence only
                        info["plist_error"] = type(exc).__name__
                key = str(app.resolve())
                if key not in seen and any(marker in label for marker in NAME_MARKERS):
                    found.append(info)
                    seen.add(key)
                dirs.remove(name)
    return found


def discover_processes() -> list[dict[str, Any]]:
    code, out, err = run("ps", "-axo", "pid=,command=")
    if code != 0:
        return [{"error": err or "ps_failed"}]
    found: list[dict[str, Any]] = []
    for line in out.splitlines():
        lowered = line.lower()
        if any(marker in lowered for marker in PROCESS_MARKERS):
            pid, _, command = line.strip().partition(" ")
            found.append({"pid": pid.strip(), "command": command.strip()[:500]})
    return found


def git_truth(repo: Path) -> dict[str, Any]:
    if not (repo / ".git").exists():
        return {"available": False, "reason": "not_git_checkout"}
    commands = {
        "head": ("git", "rev-parse", "HEAD"),
        "branch": ("git", "branch", "--show-current"),
        "origin": ("git", "remote", "get-url", "origin"),
        "origin_main": ("git", "rev-parse", "origin/main"),
        "status": ("git", "status", "--porcelain"),
    }
    values: dict[str, Any] = {"available": True}
    for key, cmd in commands.items():
        code, out, err = run(*cmd, cwd=repo)
        values[key] = out if code == 0 else None
        if code != 0:
            values[key + "_error"] = err
    if values.get("head") and values.get("origin_main"):
        values["exact_origin_main"] = values["head"] == values["origin_main"]
    values["clean"] = not bool(values.get("status"))
    return values


@dataclass(frozen=True)
class DiscoveryVerdict:
    state: str
    reason: str
    evidence_path: str
    next_action: str


def assess_discovery(payload: dict[str, Any]) -> tuple[str, str]:
    if payload.get("platform") != "Darwin":
        return "BLOCKED", "MACOS_REQUIRED"
    git = payload.get("canonical_checkout", {})
    if not git.get("available"):
        return "HOLD", "CANONICAL_CHECKOUT_NOT_CONFIRMED"
    if not git.get("exact_origin_main"):
        return "HOLD", "EXACT_MAIN_SYNC_REQUIRED"
    if not git.get("clean"):
        return "HOLD", "DIRTY_WORKTREE_RECONCILIATION_REQUIRED"

    shared = payload.get("services", {}).get("shared_ai", {})
    ollama = payload.get("services", {}).get("ollama", {})
    runtime_signals = (
        bool(payload.get("candidate_apps"))
        or bool(payload.get("candidate_processes"))
        or shared.get("reachable") is True
    )
    if not runtime_signals:
        return "HOLD", "MAC_ENGINEER_RUNTIME_PATH_DISCOVERY_REQUIRED"
    if not ollama.get("reachable"):
        return "HOLD", "OLLAMA_LOCAL_RUNTIME_NOT_REACHABLE"
    return "HOLD", "DISCOVERY_COMPLETE_REAL_TASK_COMMISSIONING_REQUIRED"


def build_payload(repo: Path, scan_root: Path) -> dict[str, Any]:
    home = Path.home()
    return {
        "schema": "enguru.mac-engineer.local-discovery/v0.1",
        "observed_at": now(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "canonical_checkout_path": str(repo.resolve()),
        "canonical_checkout": git_truth(repo),
        "scan_root": str(scan_root),
        "repositories": discover_git_repositories(scan_root),
        "candidate_apps": discover_apps([scan_root, home / "Applications", Path("/Applications")]),
        "candidate_processes": discover_processes(),
        "services": {
            "shared_ai": http_json("http://127.0.0.1:8787/health"),
            "ollama": http_json("http://127.0.0.1:11434/api/tags"),
        },
        "truth_boundary": (
            "Discovery evidence identifies local candidates and service state only. "
            "It does not prove a real Mac engineering task, restart/resume, recovery, "
            "or product-level v0.6 Verified Final."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Canonical Engurulaboratuvari checkout.",
    )
    parser.add_argument(
        "--scan-root",
        type=Path,
        default=Path.home() / "Enguru",
        help="Primary local Enguru workspace to inspect non-destructively.",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=Path.home() / "Enguru" / "Evidence" / "MacEngineer" / "v0.6",
    )
    args = parser.parse_args()

    payload = build_payload(args.repo, args.scan_root)
    state, reason = assess_discovery(payload)
    payload["state"] = state
    payload["reason"] = reason
    payload["next_action"] = (
        "Use discovered canonical runtime/app path to run Package 6 real-task commissioning."
        if state == "HOLD"
        else "Resolve the blocking platform/repository condition."
    )

    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    path = args.evidence_dir / "package6-local-discovery.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "state": state,
        "reason": reason,
        "evidence": str(path),
        "canonical_checkout": payload["canonical_checkout"],
        "candidate_apps": payload["candidate_apps"],
        "candidate_processes": payload["candidate_processes"],
        "services": payload["services"],
        "next_action": payload["next_action"],
    }, ensure_ascii=False, indent=2))
    return 3 if state == "BLOCKED" else (2 if state == "HOLD" else 0)


if __name__ == "__main__":
    raise SystemExit(main())
