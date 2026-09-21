#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineering™ v0.6 — canonical runtime/app provenance verifier.

Read-only. Verifies the installed/native runtime identity against the dedicated
product repository exact-main and the provenance receipt written by the
exact-SHA rebuild/install step.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import plistlib
import subprocess
from typing import Any


HOME = Path.home()
PRODUCT = HOME / "Enguru" / "Projects" / "enguru-mac-engineer"
RUNTIME_ROOT = HOME / "Enguru" / "Runtime" / "MacEngineer"
RUNTIME_APP = RUNTIME_ROOT / "App" / "ENGÜRÜ Mac Engineer.app"
INSTALLED_APP = HOME / "Applications" / "ENGÜRÜ Mac Engineer.app"
PROVENANCE = RUNTIME_ROOT / "state" / "source-provenance.json"
INSTALL_EVIDENCE = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.6"
    / "package6-exact-sha-rebuild-install.json"
)
OUTPUT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.6"
    / "package6-runtime-app-provenance-closure.json"
)

EXPECTED_REPO = "engurulabory/enguru-mac-engineer"
EXPECTED_BUNDLE_ID = "com.engurumaya.macengineer"
EXPECTED_VERSION = "0.6"


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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_truth(path: Path) -> dict[str, Any]:
    if not (path / ".git").exists():
        return {"available": False}
    out: dict[str, Any] = {"available": True}
    for key, cmd in {
        "head": ["git", "rev-parse", "HEAD"],
        "origin_main": ["git", "rev-parse", "origin/main"],
        "branch": ["git", "branch", "--show-current"],
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


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False, "path": str(path)}
    try:
        return {
            "exists": True,
            "path": str(path),
            "payload": json.loads(path.read_text(encoding="utf-8")),
        }
    except json.JSONDecodeError as exc:
        return {
            "exists": True,
            "path": str(path),
            "error": f"JSONDecodeError:{exc}",
        }


def app_identity(app: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"path": str(app), "exists": app.exists()}
    if not app.exists():
        return result

    plist_path = app / "Contents" / "Info.plist"
    result["info_plist"] = str(plist_path)
    if not plist_path.is_file():
        return result

    with plist_path.open("rb") as fh:
        plist = plistlib.load(fh)

    executable_name = str(plist.get("CFBundleExecutable", ""))
    result.update(
        {
            "bundle_id": str(plist.get("CFBundleIdentifier", "")),
            "short_version": str(plist.get("CFBundleShortVersionString", "")),
            "bundle_version": str(plist.get("CFBundleVersion", "")),
            "executable_name": executable_name,
        }
    )

    if executable_name:
        executable = app / "Contents" / "MacOS" / executable_name
        result["executable"] = {
            "path": str(executable),
            "exists": executable.is_file(),
        }
        if executable.is_file():
            result["executable"]["sha256"] = sha256_file(executable)

    return result


def main() -> int:
    issues: list[str] = []

    product = git_truth(PRODUCT)
    provenance_record = load_json(PROVENANCE)
    install_record = load_json(INSTALL_EVIDENCE)
    installed = app_identity(INSTALLED_APP)
    runtime_app = app_identity(RUNTIME_APP)

    if not product.get("available"):
        issues.append("PRODUCT_SOURCE_GIT_REQUIRED")
    else:
        if product.get("branch") != "main":
            issues.append("PRODUCT_SOURCE_MAIN_REQUIRED")
        if product.get("clean") is not True:
            issues.append("PRODUCT_SOURCE_CLEAN_REQUIRED")
        if product.get("exact_origin_main") is not True:
            issues.append("PRODUCT_SOURCE_EXACT_MAIN_REQUIRED")
        if EXPECTED_REPO not in str(product.get("origin") or ""):
            issues.append("PRODUCT_SOURCE_ORIGIN_MISMATCH")

    if not provenance_record.get("exists"):
        issues.append("SOURCE_PROVENANCE_RECEIPT_REQUIRED")
    elif provenance_record.get("error"):
        issues.append("SOURCE_PROVENANCE_RECEIPT_INVALID")

    if not install_record.get("exists"):
        issues.append("EXACT_SHA_INSTALL_EVIDENCE_REQUIRED")
    elif install_record.get("error"):
        issues.append("EXACT_SHA_INSTALL_EVIDENCE_INVALID")
    elif install_record.get("payload", {}).get("state") != "PASS":
        issues.append("EXACT_SHA_INSTALL_PASS_REQUIRED")

    for label, app in (
        ("INSTALLED", installed),
        ("RUNTIME_BUILD", runtime_app),
    ):
        if not app.get("exists"):
            issues.append(f"{label}_APP_REQUIRED")
            continue
        if app.get("bundle_id") != EXPECTED_BUNDLE_ID:
            issues.append(f"{label}_BUNDLE_ID_MISMATCH")
        if app.get("short_version") != EXPECTED_VERSION:
            issues.append(f"{label}_VERSION_V06_REQUIRED")
        if app.get("bundle_version") != EXPECTED_VERSION:
            issues.append(f"{label}_BUILD_VERSION_V06_REQUIRED")
        if not app.get("executable", {}).get("exists"):
            issues.append(f"{label}_EXECUTABLE_REQUIRED")

    product_sha = str(product.get("head") or "")
    provenance = provenance_record.get("payload", {})
    install = install_record.get("payload", {})
    installed_sha = str(installed.get("executable", {}).get("sha256") or "")
    runtime_sha = str(runtime_app.get("executable", {}).get("sha256") or "")

    if provenance_record.get("exists") and not provenance_record.get("error"):
        if provenance.get("product_repository") != EXPECTED_REPO:
            issues.append("PROVENANCE_PRODUCT_REPOSITORY_MISMATCH")
        if provenance.get("product_source_sha") != product_sha:
            issues.append("PROVENANCE_PRODUCT_SHA_MISMATCH")
        if provenance.get("version") != EXPECTED_VERSION:
            issues.append("PROVENANCE_VERSION_MISMATCH")
        if provenance.get("build_version") != EXPECTED_VERSION:
            issues.append("PROVENANCE_BUILD_VERSION_MISMATCH")
        if provenance.get("runtime_source_parity") != "27/27_EXACT_AT_PREFLIGHT":
            issues.append("PROVENANCE_RUNTIME_PARITY_MISMATCH")
        if provenance.get("native_executable_sha256") != installed_sha:
            issues.append("PROVENANCE_NATIVE_HASH_MISMATCH")

    if install_record.get("exists") and not install_record.get("error"):
        if install.get("product_source_sha") != product_sha:
            issues.append("INSTALL_EVIDENCE_PRODUCT_SHA_MISMATCH")
        if install.get("version") != EXPECTED_VERSION:
            issues.append("INSTALL_EVIDENCE_VERSION_MISMATCH")
        if install.get("runtime_source_parity") != "27/27_EXACT":
            issues.append("INSTALL_EVIDENCE_RUNTIME_PARITY_MISMATCH")
        if install.get("installed_app", {}).get("executable_sha256") != installed_sha:
            issues.append("INSTALL_EVIDENCE_INSTALLED_HASH_MISMATCH")
        if install.get("runtime_build_app", {}).get("executable_sha256") != runtime_sha:
            issues.append("INSTALL_EVIDENCE_RUNTIME_HASH_MISMATCH")
        if install.get("live_status", {}).get("pass") is not True:
            issues.append("INSTALL_EVIDENCE_LIVE_STATUS_PASS_REQUIRED")
        if install.get("process_verification", {}).get("pass") is not True:
            issues.append("INSTALL_EVIDENCE_PROCESS_VERIFICATION_PASS_REQUIRED")

    if installed_sha and runtime_sha and installed_sha != runtime_sha:
        issues.append("INSTALLED_RUNTIME_NATIVE_HASH_MISMATCH")

    binding = {
        "product_source_sha": product_sha,
        "provenance_source_sha": provenance.get("product_source_sha"),
        "install_evidence_source_sha": install.get("product_source_sha"),
        "installed_executable_sha256": installed_sha,
        "runtime_build_executable_sha256": runtime_sha,
        "provenance_executable_sha256": provenance.get("native_executable_sha256"),
        "all_source_sha_equal": bool(
            product_sha
            and product_sha == provenance.get("product_source_sha")
            and product_sha == install.get("product_source_sha")
        ),
        "all_native_hash_equal": bool(
            installed_sha
            and installed_sha == runtime_sha
            and installed_sha == provenance.get("native_executable_sha256")
            and installed_sha
            == install.get("installed_app", {}).get("executable_sha256")
            and installed_sha
            == install.get("runtime_build_app", {}).get("executable_sha256")
        ),
    }

    if not binding["all_source_sha_equal"]:
        issues.append("SOURCE_SHA_BINDING_REQUIRED")
    if not binding["all_native_hash_equal"]:
        issues.append("NATIVE_BINARY_HASH_BINDING_REQUIRED")

    payload = {
        "schema": "enguru.mac-engineering.runtime-app-provenance-closure/v1",
        "observed_at": now(),
        "state": "PASS" if not issues else "HOLD",
        "issues": sorted(set(issues)),
        "product": product,
        "installed_app": installed,
        "runtime_build_app": runtime_app,
        "source_provenance": provenance_record,
        "install_evidence": {
            "exists": install_record.get("exists"),
            "path": install_record.get("path"),
            "state": install.get("state"),
            "product_source_sha": install.get("product_source_sha"),
            "version": install.get("version"),
            "runtime_source_parity": install.get("runtime_source_parity"),
            "live_status_pass": install.get("live_status", {}).get("pass"),
            "process_verification_pass": install.get(
                "process_verification", {}
            ).get("pass"),
        },
        "binding": binding,
        "truth_boundary": (
            "PASS proves source SHA, product exact-main, installed app v0.6, "
            "runtime build app v0.6, native executable hashes, install Evidence "
            "and local provenance receipt all agree. It does not prove the next "
            "real engineering task, restart/resume, or final DoneCheck."
        ),
        "next_action": (
            "Reconcile archive treatment for historical handoff, backup and runtime-build artifacts."
            if not issues
            else "Resolve only the reported provenance mismatch, then rerun."
        ),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "state": payload["state"],
                "issues": payload["issues"],
                "product_source_sha": product_sha,
                "installed_app": {
                    "version": installed.get("short_version"),
                    "build_version": installed.get("bundle_version"),
                    "executable_sha256": installed_sha,
                },
                "runtime_build_app": {
                    "version": runtime_app.get("short_version"),
                    "build_version": runtime_app.get("bundle_version"),
                    "executable_sha256": runtime_sha,
                },
                "binding": binding,
                "evidence": str(OUTPUT),
                "next_action": payload["next_action"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
