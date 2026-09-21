#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineer™ v0.6 — runtime delta authority review.

Read-only. Resolves source-vs-runtime authority for the currently observed Mac
Engineer deltas by combining:
- historical source comparison,
- current runtime test execution,
- Python compile verification,
- current field-runtime precedence for verified later evolution.

It does not copy files into Git and does not create a canonical source tree.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any


SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".cache"}
TEXT_SUFFIXES = {".py", ".html", ".json", ".yaml", ".yml", ".plist", ".sh", ".txt", ".md", ".swift"}
TARGET_NAMES = {
    "repair.py",
    "repo_manager.py",
    "app.py",
    "steward_handshake.py",
    "local_ci.py",
    "support_repair_loop.py",
    "governance.py",
    "index.html",
    "reliability.py",
    "field_reliability.py",
    "test_operating_character.py",
    "test_steel_operating_character.py",
    "test_reliability.py",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None, timeout: int = 180) -> dict[str, Any]:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        return {
            "command": cmd,
            "cwd": str(cwd) if cwd else "",
            "returncode": p.returncode,
            "stdout": p.stdout[-12000:],
            "stderr": p.stderr[-12000:],
            "pass": p.returncode == 0,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "cwd": str(cwd) if cwd else "",
            "returncode": 124,
            "stdout": (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-12000:] if isinstance(exc.stderr, str) else "",
            "pass": False,
            "reason": "TIMEOUT",
        }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not root.exists():
        return out
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        cur = Path(current)
        for name in files:
            p = cur / name
            if p.is_symlink() or not p.is_file():
                continue
            if p.suffix.lower() not in TEXT_SUFFIXES and name not in TARGET_NAMES:
                continue
            try:
                rel = str(p.relative_to(root))
            except ValueError:
                rel = name
            out.append({
                "path": str(p),
                "relative_path": rel,
                "name": name,
                "size": p.stat().st_size,
                "sha256": sha256(p),
            })
    return out


def source_index(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    idx: dict[str, list[dict[str, Any]]] = {}
    for r in records:
        rel = Path(r["relative_path"])
        keys = {rel.name}
        if len(rel.parts) >= 2:
            keys.add("/".join(rel.parts[-2:]))
        if len(rel.parts) >= 3:
            keys.add("/".join(rel.parts[-3:]))
        for key in keys:
            idx.setdefault(key, []).append(r)
    return idx


def candidate_matches(runtime_item: dict[str, Any], idx: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rel = Path(runtime_item["relative_path"])
    keys: list[str] = []
    if len(rel.parts) >= 3:
        keys.append("/".join(rel.parts[-3:]))
    if len(rel.parts) >= 2:
        keys.append("/".join(rel.parts[-2:]))
    keys.append(rel.name)
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for key in keys:
        for r in idx.get(key, []):
            if r["path"] not in seen:
                out.append(r)
                seen.add(r["path"])
    return out


def diff_summary(a: Path, b: Path) -> dict[str, Any]:
    result = run(["diff", "-u", str(a), str(b)], timeout=20)
    text = (result.get("stdout") or "") + (result.get("stderr") or "")
    add = 0
    delete = 0
    for line in text.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            add += 1
        elif line.startswith("-"):
            delete += 1
    return {
        "returncode": result["returncode"],
        "additions": add,
        "deletions": delete,
        "preview": text[:4000],
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
        default=home / "Enguru" / "Evidence" / "MacEngineer" / "v0.6" / "package6-delta-authority-review.json",
    )
    args = parser.parse_args()

    source = collect(args.source_root)
    runtime = collect(args.runtime_root)
    idx = source_index(source)

    py_env = dict(os.environ)
    existing = py_env.get("PYTHONPATH", "")
    py_env["PYTHONPATH"] = str(args.runtime_root) + (os.pathsep + existing if existing else "")

    compile_result = run(
        ["python3", "-m", "compileall", "-q", str(args.runtime_root)],
        cwd=args.runtime_root,
        env=py_env,
        timeout=120,
    )

    tests_dir = args.runtime_root / "tests"
    if tests_dir.exists():
        test_result = run(
            ["python3", "-m", "unittest", "discover", "-s", str(tests_dir), "-v"],
            cwd=args.runtime_root,
            env=py_env,
            timeout=240,
        )
    else:
        test_result = {
            "command": [],
            "cwd": str(args.runtime_root),
            "returncode": 2,
            "stdout": "",
            "stderr": "runtime tests directory missing",
            "pass": False,
            "reason": "RUNTIME_TESTS_MISSING",
        }

    rows: list[dict[str, Any]] = []
    exact_count = 0
    divergent_count = 0
    runtime_only_count = 0

    for item in runtime:
        if item["name"] not in TARGET_NAMES and not item["relative_path"].startswith("tests/"):
            continue

        candidates = candidate_matches(item, idx)
        exact = [c for c in candidates if c["sha256"] == item["sha256"]]
        if exact:
            exact_count += 1
            rows.append({
                "runtime": item,
                "classification": "EXACT",
                "authority": "SHARED_IDENTICAL",
                "source_matches": exact[:10],
                "evidence": ["hash_equal"],
            })
            continue

        if candidates:
            divergent_count += 1
            details = []
            for c in candidates[:10]:
                try:
                    ds = diff_summary(Path(c["path"]), Path(item["path"]))
                except OSError as exc:
                    ds = {"error": type(exc).__name__}
                details.append({"source": c, "diff": ds})

            authority = "RUNTIME_FIELD_CANDIDATE" if compile_result["pass"] and test_result["pass"] else "HOLD"
            rows.append({
                "runtime": item,
                "classification": "DIVERGENT",
                "authority": authority,
                "source_candidates": details,
                "basis": [
                    "current installed runtime is the observed active field state",
                    "historical handoff is baseline source, not current field truth",
                    f"runtime_compile_pass={compile_result['pass']}",
                    f"runtime_tests_pass={test_result['pass']}",
                ],
            })
        else:
            runtime_only_count += 1
            authority = "RUNTIME_FIELD_CANDIDATE" if compile_result["pass"] and test_result["pass"] else "HOLD"
            rows.append({
                "runtime": item,
                "classification": "RUNTIME_ONLY",
                "authority": authority,
                "basis": [
                    "file exists only in current active runtime",
                    f"runtime_compile_pass={compile_result['pass']}",
                    f"runtime_tests_pass={test_result['pass']}",
                ],
            })

    review_targets = [r for r in rows if r["classification"] in {"DIVERGENT", "RUNTIME_ONLY"}]
    unresolved = [r for r in review_targets if r["authority"] == "HOLD"]

    issues: list[str] = []
    if not compile_result["pass"]:
        issues.append("CURRENT_RUNTIME_COMPILE_FAIL")
    if not test_result["pass"]:
        issues.append("CURRENT_RUNTIME_TESTS_FAIL")
    if not review_targets:
        issues.append("NO_RUNTIME_DELTAS_FOUND")
    if unresolved:
        issues.append("DELTA_AUTHORITY_UNRESOLVED")

    proposed_runtime_authority = [
        r["runtime"]["relative_path"]
        for r in review_targets
        if r["authority"] == "RUNTIME_FIELD_CANDIDATE"
    ]

    payload = {
        "schema": "enguru.mac-engineer.delta-authority-review/v0.1",
        "observed_at": now(),
        "source_root": str(args.source_root),
        "runtime_root": str(args.runtime_root),
        "compile_result": compile_result,
        "test_result": test_result,
        "counts": {
            "exact": exact_count,
            "divergent": divergent_count,
            "runtime_only": runtime_only_count,
            "review_targets": len(review_targets),
            "runtime_authority_candidates": len(proposed_runtime_authority),
        },
        "rows": rows,
        "proposed_authority": {
            "historical_source_role": "BASELINE_AND_NATIVE_SOURCE",
            "current_runtime_role": "FIELD_TRUTH_FOR_VERIFIED_DELTAS",
            "runtime_authority_candidate_files": proposed_runtime_authority,
            "rule": (
                "For files that differ from or postdate the historical baseline, the currently active field runtime "
                "may become authoritative only when its current runtime compile and runtime test suite both PASS. "
                "Canonical GitHub intake remains a separate step."
            ),
        },
        "issues": issues,
        "state": "PASS" if not issues else "HOLD",
        "truth_boundary": (
            "PASS means technical authority review supports the current runtime as the candidate source for verified deltas. "
            "It does not itself copy or canonicalize local source in GitHub."
        ),
        "next_action": (
            "Prepare canonical source intake using historical safe/native source plus verified current-runtime delta overrides."
            if not issues else
            "Repair only the reported runtime compile/test or authority gap and rerun."
        ),
    }

    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "state": payload["state"],
        "issues": issues,
        "evidence": str(args.evidence),
        "compile_pass": compile_result["pass"],
        "tests_pass": test_result["pass"],
        "test_returncode": test_result["returncode"],
        "counts": payload["counts"],
        "runtime_authority_candidate_files": proposed_runtime_authority,
        "next_action": payload["next_action"],
    }, ensure_ascii=False, indent=2))
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
