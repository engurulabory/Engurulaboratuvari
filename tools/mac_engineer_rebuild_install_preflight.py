#!/usr/bin/env python3
"""Read-only exact-SHA rebuild/install preflight for ENGÜRÜ Mac Engineer™."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
from datetime import datetime, timezone
from typing import Any


HOME = Path.home()
PRODUCT = HOME / "Enguru" / "Projects" / "enguru-mac-engineer"
RUNTIME = HOME / "Enguru" / "Runtime" / "MacEngineer"
INSTALLED_APP = HOME / "Applications" / "ENGÜRÜ Mac Engineer.app"
NATIVE = PRODUCT / "execution_prep" / "native_app"
INFO_PLIST = NATIVE / "Info.plist"
PREP = NATIVE / "prepare_native_app.command"
SWIFT = NATIVE / "EnguruMacEngineerApp.swift"
PRODUCT_RUNTIME = PRODUCT / "runtime"
CURRENT_RUNTIME = RUNTIME / "runtime"
EVIDENCE = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6" / "package6-rebuild-install-preflight.json"
TARGET_VERSION = "0.6"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def git_state(path: Path) -> dict[str, Any]:
    if not (path / ".git").exists():
        return {"available": False}
    out: dict[str, Any] = {"available": True}
    for key, cmd in {
        "head": ["git", "rev-parse", "HEAD"],
        "branch": ["git", "branch", "--show-current"],
        "origin_main": ["git", "rev-parse", "origin/main"],
        "status": ["git", "status", "--porcelain"],
        "origin": ["git", "remote", "get-url", "origin"],
    }.items():
        rc, stdout, stderr = run(cmd, cwd=path)
        out[key] = stdout if rc == 0 else None
        if rc != 0:
            out[f"{key}_error"] = stderr
    out["clean"] = out.get("status") == ""
    out["exact_origin_main"] = bool(
        out.get("head")
        and out.get("origin_main")
        and out["head"] == out["origin_main"]
    )
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def plist_info(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    try:
        with path.open("rb") as f:
            data = plistlib.load(f)
        return {
            "exists": True,
            "bundle_id": data.get("CFBundleIdentifier"),
            "short_version": data.get("CFBundleShortVersionString"),
            "bundle_version": data.get("CFBundleVersion"),
            "executable": data.get("CFBundleExecutable"),
        }
    except Exception as exc:
        return {"exists": True, "error": type(exc).__name__}


def installed_app_info() -> dict[str, Any]:
    plist = INSTALLED_APP / "Contents" / "Info.plist"
    info = plist_info(plist)
    exe_name = info.get("executable")
    if exe_name:
        exe = INSTALLED_APP / "Contents" / "MacOS" / str(exe_name)
        info["executable_path"] = str(exe)
        if exe.is_file():
            info["executable_sha256"] = sha256_file(exe)
    return info


def source_runtime_parity() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    if not PRODUCT_RUNTIME.is_dir() or not CURRENT_RUNTIME.is_dir():
        return {
            "available": False,
            "product_runtime_exists": PRODUCT_RUNTIME.is_dir(),
            "current_runtime_exists": CURRENT_RUNTIME.is_dir(),
            "rows": rows,
        }

    product_files = {
        str(p.relative_to(PRODUCT_RUNTIME)): p
        for p in PRODUCT_RUNTIME.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    current_files = {
        str(p.relative_to(CURRENT_RUNTIME)): p
        for p in CURRENT_RUNTIME.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }

    all_names = sorted(set(product_files) | set(current_files))
    exact = 0
    changed = 0
    missing_current = 0
    current_only = 0
    for name in all_names:
        src = product_files.get(name)
        cur = current_files.get(name)
        if src is None:
            current_only += 1
            rows.append({"path": name, "state": "CURRENT_ONLY"})
            continue
        if cur is None:
            missing_current += 1
            rows.append({"path": name, "state": "MISSING_CURRENT"})
            continue
        s_hash = sha256_file(src)
        c_hash = sha256_file(cur)
        state = "EXACT" if s_hash == c_hash else "CHANGED"
        if state == "EXACT":
            exact += 1
        else:
            changed += 1
        rows.append({
            "path": name,
            "state": state,
            "product_sha256": s_hash,
            "current_sha256": c_hash,
        })

    return {
        "available": True,
        "product_files": len(product_files),
        "current_files": len(current_files),
        "exact": exact,
        "changed": changed,
        "missing_current": missing_current,
        "current_only": current_only,
        "rows": rows,
    }


def main() -> int:
    issues: list[str] = []
    product_git = git_state(PRODUCT)
    source_info = plist_info(INFO_PLIST)
    installed_info = installed_app_info()

    if not product_git.get("available"):
        issues.append("PRODUCT_SOURCE_GIT_REQUIRED")
    else:
        if product_git.get("branch") != "main":
            issues.append("PRODUCT_SOURCE_MAIN_REQUIRED")
        if product_git.get("clean") is not True:
            issues.append("PRODUCT_SOURCE_CLEAN_REQUIRED")
        if product_git.get("exact_origin_main") is not True:
            issues.append("PRODUCT_SOURCE_EXACT_MAIN_REQUIRED")

    required = {
        "Info.plist": INFO_PLIST,
        "prepare_native_app.command": PREP,
        "EnguruMacEngineerApp.swift": SWIFT,
        "runtime": PRODUCT_RUNTIME,
    }
    missing = [name for name, path in required.items() if not path.exists()]
    if missing:
        issues.append("PRODUCT_BUILD_INPUT_MISSING:" + ",".join(missing))

    prep_contract: dict[str, Any] = {"exists": PREP.exists()}
    if PREP.exists():
        text = PREP.read_text(encoding="utf-8")
        prep_contract["canonical_runtime_mapping"] = "$SRC_DIR/../../runtime" in text
        prep_contract["historical_runtime_mapping_present"] = "baseline_v0.4/runtime" in text
        prep_contract["executable"] = os.access(PREP, os.X_OK)
        if not prep_contract["canonical_runtime_mapping"]:
            issues.append("BUILD_SCRIPT_CANONICAL_RUNTIME_MAPPING_REQUIRED")
        if prep_contract["historical_runtime_mapping_present"]:
            issues.append("BUILD_SCRIPT_HISTORICAL_RUNTIME_MAPPING_PRESENT")

    if source_info.get("bundle_id") != "com.engurumaya.macengineer":
        issues.append("SOURCE_BUNDLE_ID_MISMATCH")
    if str(source_info.get("short_version") or "") != TARGET_VERSION:
        issues.append("PRODUCT_VERSION_ALIGNMENT_REQUIRED")
    if str(source_info.get("bundle_version") or "") != TARGET_VERSION:
        issues.append("PRODUCT_BUILD_VERSION_ALIGNMENT_REQUIRED")

    parity = source_runtime_parity()

    payload = {
        "schema": "enguru.mac-engineer.rebuild-install-preflight/v1",
        "observed_at": now(),
        "state": "PASS" if not issues else "HOLD",
        "issues": issues,
        "target_version": TARGET_VERSION,
        "product_git": product_git,
        "source_app": source_info,
        "installed_app": installed_info,
        "build_contract": prep_contract,
        "runtime_source_parity": parity,
        "source_files": {
            "swift_sha256": sha256_file(SWIFT) if SWIFT.is_file() else None,
            "info_plist_sha256": sha256_file(INFO_PLIST) if INFO_PLIST.is_file() else None,
            "prepare_script_sha256": sha256_file(PREP) if PREP.is_file() else None,
        },
        "truth_boundary": (
            "Read-only preflight. It does not rebuild, stop processes, replace runtime, install an app, "
            "move backups, or change product source."
        ),
        "next_action": (
            "Rebuild/install from this exact product-source SHA."
            if not issues
            else "Apply only the reported source/build alignment difference through the product repository, then rerun preflight."
        ),
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence": str(EVIDENCE)}, ensure_ascii=False, indent=2))
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
