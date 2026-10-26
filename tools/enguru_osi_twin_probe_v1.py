#!/usr/bin/env python3
"""ENGURU OSi V1: user-triggered, read-only Mac twin fact collection.

No GitHub access or operations against live applications. Only two unique
receipt files are created: Desktop/AudiV13/original and Desktop/copy.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import plistlib
import re
import stat
import subprocess
import uuid

SCHEMA = "enguru.osi.birlesik-mimari-live-readback/v1"
PATHS = {
    "control": "Enguru/Projects/Engurulaboratuvari",
    "macEngineerProduct": "Enguru/Projects/enguru-mac-engineer",
}
SOURCE_ALLOWLIST = {
    "control": (
        "AGENTS.md",
        "governance/mac-engineer/OPERATING_MODEL_V1.md",
        "governance/mac-engineer/PRODUCT_OPERATOR_V12_PILOT_FABRIC_CONTRACT_V1.json",
        "governance/plive/ENGURU_PILIVE_URUN_HEDEFI_V4.md",
    ),
    "macEngineerProduct": (
        "runtime/cockpit_store.py",
        "runtime/static/index.html",
    ),
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
EXEC_NAME = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def open_dir(path: Path) -> int:
    """Open every existing directory component without following symlinks."""
    p = path.absolute()
    fd = os.open(p.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in p.parts[1:]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


def safe_bytes(root: Path, relative: str, limit=4 * 1024 * 1024) -> bytes:
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or '..' in rel.parts:
        raise ValueError("PATH_SCOPE")
    fd = open_dir(root)
    try:
        for segment in rel.parts[:-1]:
            nxt = os.open(segment, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        child = os.open(rel.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        with os.fdopen(child, "rb") as f:
            before = os.fstat(f.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
                raise ValueError("HOLD_FILE_TYPE_OR_SIZE")
            data = f.read(limit + 1)
            after = os.fstat(f.fileno())
            if len(data) > limit or (before.st_ino, before.st_mtime_ns, before.st_size) != (after.st_ino, after.st_mtime_ns, after.st_size):
                raise ValueError("HOLD_FILE_DRIFT")
            return data
    finally:
        os.close(fd)


def git_observation(root: Path, expected: str) -> dict:
    try:
        fd = open_dir(root)
        os.close(fd)
    except (OSError, ValueError):
        return {"state": "HOLD_LOCAL_CHECKOUT_PATH", "expectedGitHubMain": expected}
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    def command(*parts):
        p = subprocess.run(["git", "-C", str(root), *parts], capture_output=True,
                           timeout=12, env=env, check=False)
        if p.returncode or len(p.stdout) > 150000:
            raise ValueError("GIT_READ_FAILED")
        return p.stdout.decode("utf-8", errors="replace").strip()
    try:
        head = command("rev-parse", "HEAD")
        status = command("status", "--porcelain=v1", "-uno")
        branch_result = subprocess.run(["git", "-C", str(root), "symbolic-ref", "--quiet", "--short", "HEAD"],
                                       capture_output=True, timeout=12, env=env, check=False)
        branch = branch_result.stdout.decode(errors="replace").strip() if branch_result.returncode == 0 else "DETACHED"
        remote_result = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "refs/remotes/origin/main"],
                                       capture_output=True, timeout=12, env=env, check=False)
        remote = remote_result.stdout.decode(errors="replace").strip() if remote_result.returncode == 0 else None
        if not HEX40.fullmatch(head):
            raise ValueError("GIT_HEAD_SHAPE")
        return {"state": "HEAD_MATCH_GITHUB_OBSERVATION" if head == expected else "HOLD_HEAD_DIFFERENCE",
                "head": head, "branch": branch[:120], "originMainLocal": remote if remote and HEX40.fullmatch(remote) else None,
                "dirtyTrackedEntryCount": len(status.splitlines()) if status else 0,
                "dirtyTracked": bool(status), "expectedGitHubMain": expected,
                "remoteFetchPerformed": False, "localSourceModified": False}
    except (OSError, ValueError, subprocess.SubprocessError):
        return {"state": "HOLD_GIT_READ", "expectedGitHubMain": expected}


def source_observation(root: Path, allowlist: tuple[str, ...]) -> dict:
    rows = {}
    for relative in allowlist:
        try:
            content = safe_bytes(root, relative)
            rows[relative] = {"state": "LOCAL_SHA_OBSERVED", "sha256": digest(content), "bytes": len(content)}
        except (OSError, ValueError):
            rows[relative] = {"state": "HOLD_EXACT_SOURCE_READ"}
    return rows


def directory_state(p: Path) -> str:
    try:
        fd = open_dir(p)
        os.close(fd)
        return "DIRECTORY_OBSERVED_ONLY"
    except (OSError, ValueError):
        return "HOLD_DIRECTORY_READ"


def app_state(path: Path) -> dict:
    try:
        info = plistlib.loads(safe_bytes(path, "Contents/Info.plist", 1024 * 1024))
        exe = info.get("CFBundleExecutable")
        if not isinstance(exe, str) or not EXEC_NAME.fullmatch(exe):
            raise ValueError("EXECUTABLE_NAME")
        binary = safe_bytes(path, "Contents/MacOS/" + exe, 160 * 1024 * 1024)
        return {"state": "INSTALLED_BINARY_READ_ONLY", "bundleId": info.get("CFBundleIdentifier"),
                "bundleVersion": info.get("CFBundleVersion"), "binarySha256": digest(binary),
                "binaryBytes": len(binary), "applicationRunning": "NOT_MEASURED",
                "sourceToBinaryBuildBinding": "HOLD_BUILD_MANIFEST_REQUIRED"}
    except (OSError, ValueError, TypeError, plistlib.InvalidFileException):
        return {"state": "HOLD_INSTALLED_APP_READ", "applicationRunning": "NOT_MEASURED",
                "sourceToBinaryBuildBinding": "HOLD_BUILD_MANIFEST_REQUIRED"}


def observe(home: Path, expected_control: str, expected_product: str) -> dict:
    expected = {"control": expected_control, "macEngineerProduct": expected_product}
    repos = {}
    for name, suffix in PATHS.items():
        root = home / suffix
        repos[name] = {"checkout": git_observation(root, expected[name]),
                       "allowlistedSources": source_observation(root, SOURCE_ALLOWLIST[name])}
    return {
        "schema": SCHEMA, "observedAtUtc": datetime.now(timezone.utc).isoformat(),
        "environment": "REAL_MAC_READ_ONLY_INVOCATION", "platform": platform.system(),
        "repositories": repos,
        "runtime": {"macEngineer": directory_state(home / "Enguru/Runtime/MacEngineer"),
                    "evidence": directory_state(home / "Enguru/Evidence/MacEngineer")},
        "installedApps": {
            "macEngineer": app_state(home / "Enguru/Runtime/MacEngineer/App/ENGÜRÜ Mac Engineer.app"),
            "historicalPiLiveV31": app_state(Path("/Applications/ENGURU-PLive-V31.app"))},
        "liveZEKuPilot": "HOLD_NOT_MEASURED", "liveCockpitModal": "HOLD_NOT_MEASURED",
        "pilive15ProjectFacts": "HOLD_USE_PRODUCT_SPECIFIC_NATIVE_RECEIPT",
        "twoViewSnapshotParity": "HOLD_NOT_MEASURED", "realApplicationTaskRun": "NOT_EXECUTED",
        "canonicalWrites": 0, "nativeMuscleWrites": 0, "installedAppWrites": 0,
        "networkRequests": 0, "sqliteConnections": 0, "keychainReads": 0, "appLaunches": 0,
        "gitWrites": 0, "verifiedFinish": "HOLD",
        "atomicity": "PER_FILE_FSTAT_ONLY; MULTI_SOURCE_CAPTURE_NOT_ATOMIC",
        "state": "OSI_SOURCE_INVENTORY_REQUIRES_GITHUB_RECONCILIATION",
    }


def save(home: Path, receipt: dict) -> tuple[str, str, str]:
    raw = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    desktop = home / "Desktop"
    fd = open_dir(desktop)
    arch_fd = None
    try:
        try:
            os.mkdir("AudiV13", mode=0o700, dir_fd=fd)
        except FileExistsError:
            pass
        arch_fd = os.open("AudiV13", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
        name = "ENGURU_OSI_BIRLESIK_V1_TWIN_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid.uuid4().hex[:12] + ".json"
        def write(folder):
            child = os.open(name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600, dir_fd=folder)
            with os.fdopen(child, "wb") as out:
                out.write(raw)
                out.flush()
                os.fsync(out.fileno())
            child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=folder)
            with os.fdopen(child, "rb") as check:
                assert check.read() == raw, "RECEIPT_READBACK_HOLD"
        write(arch_fd)
        write(fd)
        return str(desktop / "AudiV13" / name), str(desktop / name), digest(raw)
    finally:
        if arch_fd is not None:
            os.close(arch_fd)
        os.close(fd)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--run", action="store_true")
    p.add_argument("--expected-control", required=True)
    p.add_argument("--expected-product", required=True)
    args = p.parse_args(argv)
    if not args.run or platform.system() != "Darwin":
        print("STATE=HOLD_REAL_MAC_AND_EXPLICIT_RUN_REQUIRED")
        return 2
    if not all(HEX40.fullmatch(v) for v in (args.expected_control, args.expected_product)):
        print("STATE=HOLD_SHA_ARGUMENT")
        return 2
    home = Path.home()
    result = observe(home, args.expected_control, args.expected_product)
    try:
        original, copy, sha = save(home, result)
    except (OSError, ValueError, AssertionError) as exc:
        print("STATE=HOLD_RECEIPT_WRITE; REASON=" + type(exc).__name__)
        return 2
    print("STATE=" + result["state"])
    print("ORIGINAL=" + original)
    print("DESKTOP_COPY=" + copy)
    print("RECEIPT_SHA256=" + sha)
    print("COPY_SHA256_MATCH=PASS")
    print("CANONICAL_WRITES=0; APP_LAUNCHES=0; GIT_WRITES=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
