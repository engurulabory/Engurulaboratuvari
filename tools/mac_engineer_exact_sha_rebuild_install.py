#!/usr/bin/env python3
"""Exact-SHA native rebuild/install with backup, rollback and live provenance."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import signal
import subprocess
import tempfile
import time
import unicodedata
from datetime import datetime, timezone
from typing import Any


HOME = Path.home()
PRODUCT = HOME / "Enguru" / "Projects" / "enguru-mac-engineer"
RUNTIME_ROOT = HOME / "Enguru" / "Runtime" / "MacEngineer"
RUNTIME_APP = RUNTIME_ROOT / "App" / "ENGÜRÜ Mac Engineer.app"
INSTALLED_APP = HOME / "Applications" / "ENGÜRÜ Mac Engineer.app"
PRODUCT_RUNTIME = PRODUCT / "runtime"
RUNTIME_SOURCE = RUNTIME_ROOT / "runtime"
RUNTIME_PY = RUNTIME_SOURCE / "app.py"
STATE_DIR = RUNTIME_ROOT / "state"
PROVENANCE = STATE_DIR / "source-provenance.json"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
CI_EVIDENCE = EVIDENCE_ROOT / "package6-product-ci-exact-main.json"
PREFLIGHT_EVIDENCE = EVIDENCE_ROOT / "package6-rebuild-install-preflight.json"
OUTPUT = EVIDENCE_ROOT / "package6-exact-sha-rebuild-install.json"
BACKUP_ROOT = HOME / "Enguru" / "Backup" / "MacEngineer"

INFO = PRODUCT / "execution_prep" / "native_app" / "Info.plist"
SWIFT = PRODUCT / "execution_prep" / "native_app" / "EnguruMacEngineerApp.swift"
TARGET_VERSION = "0.6"
STATUS_URL = "http://127.0.0.1:8765/api/status"


class InstallError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 300,
) -> dict[str, Any]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    return {
        "cmd": cmd,
        "returncode": p.returncode,
        "pass": p.returncode == 0,
        "stdout": p.stdout[-12000:],
        "stderr": p.stderr[-12000:],
    }


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise InstallError(f"EVIDENCE_REQUIRED:{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InstallError(f"EVIDENCE_INVALID_JSON:{path}") from exc


def git_value(*args: str) -> str:
    r = run(["git", *args], cwd=PRODUCT)
    if not r["pass"]:
        raise InstallError(
            f"GIT_FAILED:{' '.join(args)}:{r['stderr']}"
        )
    return str(r["stdout"]).strip()


def canonical_runtime_relpaths() -> list[Path]:
    result = run(
        ["git", "ls-files", "runtime"],
        cwd=PRODUCT,
    )
    if not result["pass"]:
        raise InstallError(
            f"RUNTIME_SOURCE_LIST_FAILED:{result['stderr']}"
        )

    relpaths: list[Path] = []

    for raw in str(result["stdout"]).splitlines():
        raw = raw.strip()
        if not raw:
            continue

        path = Path(raw)

        try:
            rel = path.relative_to("runtime")
        except ValueError:
            continue

        source = PRODUCT_RUNTIME / rel

        if source.is_file():
            relpaths.append(rel)

    relpaths = sorted(set(relpaths))

    if not relpaths:
        raise InstallError(
            "CANONICAL_RUNTIME_SOURCE_SET_REQUIRED"
        )

    return relpaths


def runtime_source_parity() -> dict[str, Any]:
    canonical = canonical_runtime_relpaths()
    canonical_set = set(canonical)

    current: list[Path] = []

    if RUNTIME_SOURCE.is_dir():
        current = sorted(
            path.relative_to(RUNTIME_SOURCE)
            for path in RUNTIME_SOURCE.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
        )

    current_set = set(current)

    missing = sorted(canonical_set - current_set)
    current_only = sorted(current_set - canonical_set)

    changed: list[Path] = []
    exact = 0

    for rel in canonical:
        source = PRODUCT_RUNTIME / rel
        target = RUNTIME_SOURCE / rel

        if not target.is_file():
            continue

        if sha256_file(source) == sha256_file(target):
            exact += 1
        else:
            changed.append(rel)

    return {
        "product_files": len(canonical),
        "current_files": len(current),
        "exact": exact,
        "changed": len(changed),
        "missing_current": len(missing),
        "current_only": len(current_only),
        "changed_paths": [str(path) for path in changed],
        "missing_paths": [str(path) for path in missing],
        "current_only_paths": [
            str(path) for path in current_only
        ],
    }


def exact_runtime_parity(
    parity: dict[str, Any],
) -> bool:
    count = parity.get("product_files")

    return bool(
        isinstance(count, int)
        and count > 0
        and parity.get("current_files") == count
        and parity.get("exact") == count
        and parity.get("changed") == 0
        and parity.get("missing_current") == 0
        and parity.get("current_only") == 0
    )


def sync_runtime_source() -> dict[str, Any]:
    canonical = canonical_runtime_relpaths()

    if RUNTIME_SOURCE.exists():
        shutil.rmtree(RUNTIME_SOURCE)

    RUNTIME_SOURCE.mkdir(
        parents=True,
        exist_ok=True,
    )

    for rel in canonical:
        source = PRODUCT_RUNTIME / rel
        target = RUNTIME_SOURCE / rel

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            source,
            target,
        )

    parity = runtime_source_parity()

    if not exact_runtime_parity(parity):
        raise InstallError(
            "RUNTIME_SOURCE_EXACT_PARITY_REQUIRED"
        )

    return parity


def plist_info(app_or_plist: Path) -> dict[str, Any]:
    plist = (
        app_or_plist / "Contents" / "Info.plist"
        if app_or_plist.suffix == ".app"
        else app_or_plist
    )
    if not plist.is_file():
        return {"exists": False}
    with plist.open("rb") as f:
        data = plistlib.load(f)
    return {
        "exists": True,
        "bundle_id": data.get("CFBundleIdentifier"),
        "short_version": str(
            data.get("CFBundleShortVersionString", "")
        ),
        "bundle_version": str(data.get("CFBundleVersion", "")),
        "executable": str(data.get("CFBundleExecutable", "")),
    }


def app_executable(app: Path) -> Path:
    info = plist_info(app)
    name = info.get("executable")
    if not name:
        raise InstallError(f"APP_EXECUTABLE_NAME_REQUIRED:{app}")
    return app / "Contents" / "MacOS" / str(name)


def normalized_text(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def command_contains_path(command: str, path: Path) -> bool:
    return normalized_text(str(path)) in normalized_text(command)


def process_rows() -> list[dict[str, str]]:
    r = run(["ps", "-axo", "pid=,command="])
    if not r["pass"]:
        return []
    rows: list[dict[str, str]] = []
    for line in str(r["stdout"]).splitlines():
        command = line.strip()
        if (
            command_contains_path(command, INSTALLED_APP)
            or command_contains_path(command, RUNTIME_PY)
        ):
            pid, _, tail = command.partition(" ")
            rows.append({"pid": pid, "command": tail})
    return rows


def process_presence(
    rows: list[dict[str, str]],
) -> tuple[bool, bool]:
    app_process = any(
        command_contains_path(row["command"], INSTALLED_APP)
        for row in rows
    )
    runtime_process = any(
        command_contains_path(row["command"], RUNTIME_PY)
        for row in rows
    )
    return app_process, runtime_process


def wait_for_processes(
    timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last_rows: list[dict[str, str]] = []
    while time.time() < deadline:
        last_rows = process_rows()
        app_process, runtime_process = process_presence(last_rows)
        if app_process and runtime_process:
            return {
                "pass": True,
                "app_process": True,
                "runtime_process": True,
                "rows": last_rows,
            }
        time.sleep(0.25)

    app_process, runtime_process = process_presence(last_rows)
    return {
        "pass": False,
        "app_process": app_process,
        "runtime_process": runtime_process,
        "rows": last_rows,
    }


def stop_existing_processes() -> list[dict[str, str]]:
    rows = process_rows()
    for row in rows:
        try:
            os.kill(int(row["pid"]), signal.SIGTERM)
        except (ProcessLookupError, ValueError):
            pass
    deadline = time.time() + 8
    while time.time() < deadline:
        if not process_rows():
            return rows
        time.sleep(0.25)
    for row in process_rows():
        try:
            os.kill(int(row["pid"]), signal.SIGKILL)
        except (ProcessLookupError, ValueError):
            pass
    time.sleep(0.5)
    if process_rows():
        raise InstallError("EXISTING_PROCESS_STOP_FAILED")
    return rows


def copy_bundle(source: Path, target: Path) -> None:
    if target.exists() or target.is_symlink():
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    result = run(["ditto", str(source), str(target)])
    if not result["pass"]:
        raise InstallError(
            f"BUNDLE_COPY_FAILED:{source}->{target}:{result['stderr']}"
        )


def backup_path(source: Path, target: Path) -> bool:
    if not source.exists():
        return False
    copy_bundle(source, target)
    return True


def build_stage(root: Path) -> dict[str, Any]:
    app = root / "ENGÜRÜ Mac Engineer.app"
    contents = app / "Contents"
    macos = contents / "MacOS"
    macos.mkdir(parents=True, exist_ok=True)
    shutil.copy2(INFO, contents / "Info.plist")
    binary = macos / "EnguruMacEngineer"
    result = run(
        [
            "xcrun",
            "swiftc",
            "-parse-as-library",
            str(SWIFT),
            "-o",
            str(binary),
            "-framework",
            "SwiftUI",
            "-framework",
            "WebKit",
            "-framework",
            "AppKit",
        ],
        cwd=PRODUCT,
    )
    if not result["pass"]:
        raise InstallError(
            f"NATIVE_BUILD_FAILED:{result['stderr']}"
        )
    binary.chmod(binary.stat().st_mode | 0o111)

    info = plist_info(app)
    if info.get("bundle_id") != "com.engurumaya.macengineer":
        raise InstallError("STAGED_BUNDLE_ID_MISMATCH")
    if info.get("short_version") != TARGET_VERSION:
        raise InstallError("STAGED_VERSION_MISMATCH")
    if info.get("bundle_version") != TARGET_VERSION:
        raise InstallError("STAGED_BUILD_VERSION_MISMATCH")

    return {
        "app": app,
        "info": info,
        "binary": str(binary),
        "binary_sha256": sha256_file(binary),
        "build": result,
    }


def live_status() -> dict[str, Any]:
    last: dict[str, Any] = {}
    for _ in range(40):
        result = run(
            [
                "curl",
                "--fail",
                "--silent",
                "--show-error",
                "--max-time",
                "2",
                STATUS_URL,
            ],
            timeout=5,
        )
        last = result
        if result["pass"]:
            text = str(result["stdout"])
            parsed: Any = text
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                pass
            return {
                "pass": True,
                "url": STATUS_URL,
                "response": parsed,
            }
        time.sleep(0.5)
    return {
        "pass": False,
        "url": STATUS_URL,
        "last": last,
    }


def write_provenance(
    *,
    source_sha: str,
    app_sha: str,
    installed_info: dict[str, Any],
) -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    parity = runtime_source_parity()

    if not exact_runtime_parity(parity):
        raise InstallError(
            "PROVENANCE_RUNTIME_SOURCE_PARITY_REQUIRED"
        )

    parity_count = parity["product_files"]

    payload = {
        "schema": "enguru.mac-engineer.runtime-provenance/v1",
        "installed_at": now(),
        "product_repository": "engurulabory/enguru-mac-engineer",
        "product_source_sha": source_sha,
        "runtime_source_parity": (
            f"{parity_count}/{parity_count}_EXACT_AT_INSTALL"
        ),
        "runtime_source_parity_detail": parity,
        "installed_app": str(INSTALLED_APP),
        "runtime_build_app": str(RUNTIME_APP),
        "bundle_id": installed_info.get("bundle_id"),
        "version": installed_info.get("short_version"),
        "build_version": installed_info.get("bundle_version"),
        "native_executable_sha256": app_sha,
    }
    PROVENANCE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return payload


def restore_backup(
    backup_dir: Path,
    *,
    had_installed: bool,
    had_runtime_app: bool,
    provenance_backup: Path | None,
) -> dict[str, Any]:
    stopped = []
    try:
        stopped = stop_existing_processes()
    except InstallError:
        pass

    restored: list[str] = []

    runtime_source_backup = (
        backup_dir / "runtime_source_before"
    )

    if runtime_source_backup.exists():
        if RUNTIME_SOURCE.exists():
            shutil.rmtree(RUNTIME_SOURCE)

        copy_bundle(
            runtime_source_backup,
            RUNTIME_SOURCE,
        )
        restored.append(str(RUNTIME_SOURCE))

    elif RUNTIME_SOURCE.exists():
        shutil.rmtree(RUNTIME_SOURCE)

    installed_backup = backup_dir / "installed_app_before.app"
    runtime_backup = backup_dir / "runtime_app_before.app"

    if had_installed and installed_backup.exists():
        copy_bundle(installed_backup, INSTALLED_APP)
        restored.append(str(INSTALLED_APP))
    elif INSTALLED_APP.exists():
        shutil.rmtree(INSTALLED_APP)

    if had_runtime_app and runtime_backup.exists():
        copy_bundle(runtime_backup, RUNTIME_APP)
        restored.append(str(RUNTIME_APP))
    elif RUNTIME_APP.exists():
        shutil.rmtree(RUNTIME_APP)

    if provenance_backup and provenance_backup.exists():
        PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(provenance_backup, PROVENANCE)
        restored.append(str(PROVENANCE))
    elif PROVENANCE.exists():
        PROVENANCE.unlink()

    relaunch = None
    if had_installed and INSTALLED_APP.exists():
        relaunch = run(["open", str(INSTALLED_APP)], timeout=20)

    return {
        "stopped": stopped,
        "restored": restored,
        "relaunch": relaunch,
    }


def main() -> int:
    backup_dir = BACKUP_ROOT / f"v06_exact_sha_install_{stamp()}"
    mutation_started = False
    had_installed = INSTALLED_APP.exists()
    had_runtime_app = RUNTIME_APP.exists()
    provenance_backup: Path | None = None

    try:
        ci = load_json(CI_EVIDENCE)
        preflight = load_json(PREFLIGHT_EVIDENCE)
        if ci.get("state") != "PASS":
            raise InstallError("EXACT_MAIN_PRODUCT_CI_PASS_REQUIRED")
        if preflight.get("state") != "PASS":
            raise InstallError("REBUILD_PREFLIGHT_PASS_REQUIRED")

        source_sha = git_value("rev-parse", "HEAD")
        origin_main = git_value("rev-parse", "origin/main")
        branch = git_value("branch", "--show-current")
        status = git_value("status", "--porcelain")

        if branch != "main":
            raise InstallError("PRODUCT_MAIN_REQUIRED")
        if status:
            raise InstallError("PRODUCT_SOURCE_CLEAN_REQUIRED")
        if source_sha != origin_main:
            raise InstallError("PRODUCT_SOURCE_EXACT_MAIN_REQUIRED")
        if source_sha != str(ci.get("local_head", "")):
            raise InstallError("CI_EVIDENCE_SOURCE_SHA_MISMATCH")
        if source_sha != str(
            preflight.get("product_git", {}).get("head", "")
        ):
            raise InstallError("PREFLIGHT_SOURCE_SHA_MISMATCH")
        if preflight.get("target_version") != TARGET_VERSION:
            raise InstallError("PREFLIGHT_TARGET_VERSION_MISMATCH")
        parity = preflight.get("runtime_source_parity", {})
        canonical_runtime_count = len(
            canonical_runtime_relpaths()
        )

        if (
            parity.get("product_files")
            != canonical_runtime_count
        ):
            raise InstallError(
                "PREFLIGHT_RUNTIME_SOURCE_SET_MISMATCH"
            )

        if parity.get("current_only") != 0:
            raise InstallError(
                "RUNTIME_CURRENT_ONLY_SOURCE_REVIEW_REQUIRED"
            )

        before = {
            "installed_app": plist_info(INSTALLED_APP),
            "runtime_app": plist_info(RUNTIME_APP),
            "processes": process_rows(),
        }

        with tempfile.TemporaryDirectory() as td:
            stage = build_stage(Path(td))
            stage_app = Path(stage["app"])

            backup_dir.mkdir(parents=True, exist_ok=False)
            if had_installed:
                backup_path(
                    INSTALLED_APP,
                    backup_dir / "installed_app_before.app",
                )
            if had_runtime_app:
                backup_path(
                    RUNTIME_APP,
                    backup_dir / "runtime_app_before.app",
                )

            if RUNTIME_SOURCE.exists():
                backup_path(
                    RUNTIME_SOURCE,
                    backup_dir / "runtime_source_before",
                )

            if PROVENANCE.exists():
                provenance_backup = (
                    backup_dir / "source-provenance-before.json"
                )
                shutil.copy2(PROVENANCE, provenance_backup)

            stopped = stop_existing_processes()
            mutation_started = True

            runtime_parity = sync_runtime_source()
            runtime_count = runtime_parity["product_files"]

            copy_bundle(stage_app, RUNTIME_APP)
            copy_bundle(stage_app, INSTALLED_APP)

            installed_info = plist_info(INSTALLED_APP)
            runtime_info = plist_info(RUNTIME_APP)
            installed_exe = app_executable(INSTALLED_APP)
            runtime_exe = app_executable(RUNTIME_APP)
            installed_sha = sha256_file(installed_exe)
            runtime_sha = sha256_file(runtime_exe)

            if installed_info.get("short_version") != TARGET_VERSION:
                raise InstallError("INSTALLED_APP_VERSION_NOT_V06")
            if runtime_info.get("short_version") != TARGET_VERSION:
                raise InstallError("RUNTIME_APP_VERSION_NOT_V06")
            if installed_sha != stage["binary_sha256"]:
                raise InstallError("INSTALLED_APP_BINARY_SHA_MISMATCH")
            if runtime_sha != stage["binary_sha256"]:
                raise InstallError("RUNTIME_APP_BINARY_SHA_MISMATCH")

            provenance = write_provenance(
                source_sha=source_sha,
                app_sha=installed_sha,
                installed_info=installed_info,
            )

            launch = run(["open", str(INSTALLED_APP)], timeout=20)
            if not launch["pass"]:
                raise InstallError(
                    f"INSTALLED_APP_LAUNCH_FAILED:{launch['stderr']}"
                )

            status_result = live_status()
            if not status_result["pass"]:
                raise InstallError("LIVE_API_STATUS_REQUIRED")

            process_check = wait_for_processes()
            processes_after = process_check["rows"]
            if not process_check["app_process"]:
                raise InstallError("INSTALLED_APP_PROCESS_REQUIRED")
            if not process_check["runtime_process"]:
                raise InstallError("RUNTIME_PROCESS_REQUIRED")

            payload = {
                "schema": (
                    "enguru.mac-engineer."
                    "exact-sha-rebuild-install/v1"
                ),
                "observed_at": now(),
                "state": "PASS",
                "issues": [],
                "product_source_sha": source_sha,
                "version": TARGET_VERSION,
                "runtime_source_parity": (
                    f"{runtime_count}/{runtime_count}_EXACT"
                ),
                "runtime_source_parity_detail": runtime_parity,
                "backup_dir": str(backup_dir),
                "before": before,
                "build": {
                    "binary_sha256": stage["binary_sha256"],
                    "swift": stage["build"],
                },
                "stopped_processes": stopped,
                "installed_app": {
                    **installed_info,
                    "path": str(INSTALLED_APP),
                    "executable_sha256": installed_sha,
                },
                "runtime_build_app": {
                    **runtime_info,
                    "path": str(RUNTIME_APP),
                    "executable_sha256": runtime_sha,
                },
                "provenance": provenance,
                "live_status": status_result,
                "process_verification": process_check,
                "processes_after": processes_after,
                "rollback": {
                    "prepared": True,
                    "used": False,
                },
                "truth_boundary": (
                    "This proves exact-SHA native build/install, matching v0.6 "
                    f"app bundles, synchronized {runtime_count}/{runtime_count} "
                    "runtime source parity, live "
                    "/api/status and canonical app/runtime processes. It does "
                    "not yet prove a real engineering task, restart/resume or "
                    "recovery field behavior."
                ),
                "next_action": (
                    "Record runtime/app provenance canonically, decide archive "
                    "treatment for historical/backup artifacts, then execute "
                    "one real Mac engineering task."
                ),
            }
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.write_text(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            print(
                json.dumps(
                    {**payload, "evidence": str(OUTPUT)},
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0

    except (
        InstallError,
        OSError,
        plistlib.InvalidFileException,
        subprocess.TimeoutExpired,
    ) as exc:
        rollback: dict[str, Any] = {
            "prepared": backup_dir.exists(),
            "used": False,
        }
        if mutation_started and backup_dir.exists():
            try:
                rollback = {
                    "prepared": True,
                    "used": True,
                    "result": restore_backup(
                        backup_dir,
                        had_installed=had_installed,
                        had_runtime_app=had_runtime_app,
                        provenance_backup=provenance_backup,
                    ),
                }
            except Exception as rollback_exc:
                rollback = {
                    "prepared": True,
                    "used": True,
                    "error": type(rollback_exc).__name__,
                }

        payload = {
            "schema": (
                "enguru.mac-engineer."
                "exact-sha-rebuild-install/v1"
            ),
            "observed_at": now(),
            "state": "HOLD",
            "issues": [str(exc)],
            "backup_dir": (
                str(backup_dir)
                if backup_dir.exists()
                else None
            ),
            "rollback": rollback,
            "truth_boundary": (
                "Fail-closed. If execution mutation began, rollback was "
                "attempted from the timestamped pre-install backup."
            ),
        }
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {**payload, "evidence": str(OUTPUT)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
