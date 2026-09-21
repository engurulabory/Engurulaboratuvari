#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineer™ v0.6 — local provenance reconciliation.

Read-only. Compares the currently running local runtime/app identity against the
known historical source package, baseline, build receipts and evidence without
inventing source-to-binary provenance.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
from typing import Any


TEXT_NAMES = {
    "app.py", "provider.py", "repo_manager.py", "backup_manager.py", "local_ci.py",
    "local_gitvault.py", "repair.py", "doctor.py", "requirements.txt", "index.html",
}
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


def file_rec(path: Path, root: Path | None = None) -> dict[str, Any]:
    rec = {"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)}
    if root is not None:
        try:
            rec["relative_path"] = str(path.relative_to(root))
        except ValueError:
            pass
    return rec


def collect_files(root: Path, max_files: int = 1200) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not root.exists():
        return out
    count = 0
    for current, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        cur = Path(current)
        for name in names:
            p = cur / name
            if not p.is_file() or p.is_symlink():
                continue
            if count >= max_files:
                return out
            if name in TEXT_NAMES or p.suffix.lower() in {".py", ".html", ".json", ".yaml", ".yml", ".plist", ".sh", ".md", ".txt"}:
                out.append(file_rec(p, root))
                count += 1
    return out


def index_by_tail(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    idx: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        rel = rec.get("relative_path") or Path(rec["path"]).name
        parts = Path(rel).parts
        keys = {Path(rel).name}
        if len(parts) >= 2:
            keys.add("/".join(parts[-2:]))
        if len(parts) >= 3:
            keys.add("/".join(parts[-3:]))
        for key in keys:
            idx.setdefault(key, []).append(rec)
    return idx


def compare_runtime_to_source(runtime_files: list[dict[str, Any]], source_files: list[dict[str, Any]]) -> dict[str, Any]:
    source_idx = index_by_tail(source_files)
    rows: list[dict[str, Any]] = []
    exact = 0
    unmatched = 0
    differing = 0
    for r in runtime_files:
        rel = r.get("relative_path") or Path(r["path"]).name
        parts = Path(rel).parts
        keys = []
        if len(parts) >= 3:
            keys.append("/".join(parts[-3:]))
        if len(parts) >= 2:
            keys.append("/".join(parts[-2:]))
        keys.append(Path(rel).name)

        candidates: list[dict[str, Any]] = []
        seen: set[str] = set()
        for key in keys:
            for c in source_idx.get(key, []):
                if c["path"] not in seen:
                    candidates.append(c)
                    seen.add(c["path"])

        matches = [c for c in candidates if c["sha256"] == r["sha256"]]
        if matches:
            exact += 1
            rows.append({
                "runtime": r,
                "state": "EXACT_MATCH",
                "source_matches": matches[:10],
            })
        elif candidates:
            differing += 1
            rows.append({
                "runtime": r,
                "state": "NAME_MATCH_HASH_DIFF",
                "source_candidates": candidates[:10],
            })
        else:
            unmatched += 1
            rows.append({"runtime": r, "state": "NO_SOURCE_CANDIDATE"})
    total = len(runtime_files)
    return {
        "total_runtime_files": total,
        "exact_matches": exact,
        "hash_differences": differing,
        "unmatched": unmatched,
        "exact_ratio": (exact / total) if total else 0.0,
        "rows": rows,
    }


def app_info(app: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"path": str(app), "exists": app.exists()}
    if not app.exists():
        return out
    plist = app / "Contents" / "Info.plist"
    if plist.exists():
        with plist.open("rb") as fh:
            data = plistlib.load(fh)
        out.update({
            "bundle_id": data.get("CFBundleIdentifier", ""),
            "short_version": data.get("CFBundleShortVersionString", ""),
            "bundle_version": data.get("CFBundleVersion", ""),
            "executable_name": data.get("CFBundleExecutable", ""),
        })
        exe = app / "Contents" / "MacOS" / str(out["executable_name"])
        if exe.exists():
            out["executable"] = file_rec(exe)
    return out


def find_named(root: Path, name: str, max_depth: int = 8) -> list[str]:
    found: list[str] = []
    if not root.exists():
        return found
    root_depth = len(root.parts)
    for current, dirs, files in os.walk(root):
        cur = Path(current)
        depth = len(cur.parts) - root_depth
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        if depth > max_depth:
            dirs[:] = []
            continue
        if name in dirs:
            found.append(str(cur / name))
        if name in files:
            found.append(str(cur / name))
    return found


def git_head(repo: Path) -> str:
    code, out, _ = run("git", "rev-parse", "HEAD", cwd=repo)
    return out if code == 0 else ""


def main() -> int:
    home = Path.home()
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
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
        "--app",
        type=Path,
        default=home / "Applications" / "ENGÜRÜ Mac Engineer.app",
    )
    parser.add_argument(
        "--evidence-root",
        type=Path,
        default=home / "Enguru" / "Evidence" / "MacEngineer",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=home / "Enguru" / "Evidence" / "MacEngineer" / "v0.6" / "package6-provenance-reconcile.json",
    )
    args = parser.parse_args()

    source_files = collect_files(args.source_root)
    runtime_files = collect_files(args.runtime_root)
    comparison = compare_runtime_to_source(runtime_files, source_files)

    build_receipts = find_named(args.evidence_root, "native_app_prepare_20260920T082338Z.txt")
    phase1_evidence = find_named(args.evidence_root, "phase1_donecheck_20260920T095119Z.json")
    baselines = find_named(args.source_root, "baseline_v0.4")

    issues: list[str] = []
    if not args.source_root.exists():
        issues.append("HISTORICAL_SOURCE_PACKAGE_NOT_FOUND")
    if not args.runtime_root.exists():
        issues.append("CURRENT_RUNTIME_NOT_FOUND")
    if not args.app.exists():
        issues.append("CURRENT_APP_NOT_FOUND")
    if not baselines:
        issues.append("BASELINE_V0_4_NOT_FOUND")
    if not build_receipts:
        issues.append("BUILD_RECEIPT_NOT_FOUND")
    if not phase1_evidence:
        issues.append("PHASE1_DONECHECK_EVIDENCE_NOT_FOUND")
    if comparison["total_runtime_files"] == 0:
        issues.append("NO_RUNTIME_FILES_SCANNED")
    if comparison["exact_matches"] == 0:
        issues.append("NO_RUNTIME_SOURCE_EXACT_MATCHES")

    payload = {
        "schema": "enguru.mac-engineer.provenance-reconcile/v0.1",
        "observed_at": now(),
        "canonical_github_head": git_head(args.repo),
        "historical_source_root": str(args.source_root),
        "historical_source_exists": args.source_root.exists(),
        "baseline_candidates": baselines,
        "build_receipts": build_receipts,
        "phase1_donecheck_evidence": phase1_evidence,
        "current_app": app_info(args.app),
        "current_runtime_root": str(args.runtime_root),
        "source_file_count": len(source_files),
        "runtime_file_count": len(runtime_files),
        "comparison": comparison,
        "issues": issues,
        "state": "PASS" if not issues else "HOLD",
        "truth_boundary": (
            "This reconciliation may establish historical source/build/runtime continuity. "
            "It does not make the historical local source package canonical GitHub source. "
            "GitHub canonicalization remains a separate governed step after source hygiene review."
        ),
        "next_action": (
            "Review reconciled source tree for canonical GitHub intake."
            if not issues else
            "Resolve only the reported historical-source/evidence gaps, then rerun."
        ),
    }

    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "state": payload["state"],
        "issues": issues,
        "evidence": str(args.evidence),
        "canonical_github_head": payload["canonical_github_head"],
        "historical_source_root": payload["historical_source_root"],
        "baseline_candidates": baselines,
        "build_receipts": build_receipts,
        "phase1_donecheck_evidence": phase1_evidence,
        "current_app": payload["current_app"],
        "current_runtime_root": payload["current_runtime_root"],
        "source_file_count": len(source_files),
        "runtime_file_count": len(runtime_files),
        "comparison_summary": {
            "total_runtime_files": comparison["total_runtime_files"],
            "exact_matches": comparison["exact_matches"],
            "hash_differences": comparison["hash_differences"],
            "unmatched": comparison["unmatched"],
            "exact_ratio": comparison["exact_ratio"],
        },
        "next_action": payload["next_action"],
    }, ensure_ascii=False, indent=2))
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
