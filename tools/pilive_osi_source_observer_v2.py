#!/usr/bin/env python3
"""Bounded source observation. Stdout only; no app launch or native-code execution.

The seven named source files are exported for review. Other candidates receive
names/hashes only. This is an inventory, never a Progress Core verification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
from datetime import datetime, timezone

PINS = {
    "governance/plive-p01-authorized-field/P01_ACCEPTANCE_FINAL_BINDING_V1.json": "e8847241b32960950a381bd179f56a7bbca8902a490ea226f72f3fe5a1c98510",
    "governance/plive-p01-authorized-field/STATE_V1.json": "68bc45cc41ed365d50b2e1b0476ecaaabfd0ccdfd21af54868276709cb877608",
    "governance/plive-p02-user-screen/PLIVE_P02_WORK_CONTRACT_V1.json": "1dc9b0bae00a13672a142fb91f6b1fe603f151bcebaa64482e297029deda7512",
    "governance/plive-p02-user-screen/STATE_V1.json": "ad29d034c8a97be75d69d972fca1c6e7ee207e7f7f1339e79b74e1ce6c40f432",
    "governance/plive-p02-user-screen/WORKLIST_V1.json": "4021dc7486363bc7baf503860969ea23324eabcbd4e3551930a20d79784532d2",
    "governance/progress-core/ENGURU_PROGRESS_CORE_PROJECT_REGISTRY_V1.json": "515748a88acffdd60be6afd4c837a2581a48a3bbeccd74c4a413ae3f986c4a80",
    "tools/enguru_progress.py": "f3e2610c6e325f6fd620baa84ec412437a015109dde88ac38cab7f08b2a365b4",
}
BASELINE_HEAD = "269854b8a42a27e9419eae65a3c9e349bdcc7300"
LIMIT = 2 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bounded_read(root, relative):
    """Open each component relative to an fd; reject symlinks, FIFOs and escapes."""
    parts = Path(relative).parts
    if not parts or Path(relative).is_absolute() or any(p in ("..", ".") for p in parts):
        raise ValueError("HOLD_PATH_SCOPE")
    # root itself and each of its ancestors must be real directories.
    absolute = Path(root).absolute()
    fd = os.open(absolute.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in absolute.parts[1:] + parts[:-1]:
            new = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = new
        child = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            info = os.fstat(child)
            if not stat.S_ISREG(info.st_mode) or info.st_size > LIMIT:
                raise ValueError("HOLD_FILE_TYPE_OR_SIZE")
            chunks, count = [], 0
            while True:
                block = os.read(child, min(65536, LIMIT + 1 - count))
                if not block:
                    break
                chunks.append(block)
                count += len(block)
                if count > LIMIT:
                    raise ValueError("HOLD_FILE_SIZE")
            return b"".join(chunks)
        finally:
            os.close(child)
    finally:
        os.close(fd)


def git(root, *args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    return subprocess.check_output(["git", "--no-optional-locks", "-c", "core.fsmonitor=false",
                                   "-c", "core.untrackedCache=false", "-C", str(root), *args],
                                   env=env, stderr=subprocess.PIPE, timeout=15)


def facts(root):
    return {"head": git(root, "rev-parse", "HEAD").decode().strip(),
            "branch": git(root, "branch", "--show-current").decode().strip(),
            "statusPorcelainZ": git(root, "status", "--porcelain=v1", "-z", "--untracked-files=no").decode()}


def observe(root):
    root = Path(root).absolute()
    before = facts(root)
    sources, errors = {}, []
    for name, expected in PINS.items():
        try:
            raw = bounded_read(root, name)
            sources[name] = {"sha256": sha(raw), "historicalPinMatch": sha(raw) == expected,
                             "contentUtf8": raw.decode("utf-8"), "bytes": len(raw)}
        except (OSError, ValueError, UnicodeError) as exc:
            errors.append({"path": name, "reason": type(exc).__name__})
    candidates = []
    names = git(root, "ls-files", "-z").decode().split("\0")[:-1]
    for name in sorted(names):
        if ("plive" in name.lower() or "pilive" in name.lower() or
                "progress" in name.lower()) and Path(name).suffix.lower() in {
                    ".swift", ".py", ".json", ".md", ".sh", ".plist"}:
            if len(candidates) == 500:
                errors.append({"reason": "CANDIDATE_LIMIT"})
                break
            try:
                raw = bounded_read(root, name)
                candidates.append({"path": name, "sha256": sha(raw), "bytes": len(raw)})
            except (OSError, ValueError) as exc:
                errors.append({"path": name, "reason": type(exc).__name__})
    after = facts(root)
    stable = before == after
    for name, record in sources.items():
        try:
            stable = sha(bounded_read(root, name)) == record["sha256"] and stable
        except (OSError, ValueError):
            stable = False
    matched = len(sources) == len(PINS) and all(r["historicalPinMatch"] for r in sources.values())
    return {"schema": "enguru.pilive.source-observation/v2",
            "observedAtUtc": datetime.now(timezone.utc).isoformat(),
            "scope": "SEVEN_SOURCE_CONTENTS_AND_TRACKED_CANDIDATE_DIGESTS",
            "platform": platform.system(), "root": str(root), "before": before, "after": after,
            "sources": sources, "candidates": candidates, "errors": errors,
            "stableBracket": stable, "historicalPinsMatch": matched,
            "historicalHeadMatch": before["head"] == BASELINE_HEAD,
            "state": "PASS_SOURCE_CAPTURE_ONLY" if stable and matched and not errors else "HOLD_SOURCE_REQUALIFICATION",
            "atomicity": "BEFORE_AFTER_BRACKET_ONLY; ABA_REQUIRES_NATIVE_REVISION_PROTOCOL",
            "nativeProgressVerification": "NOT_EXECUTED",
            "swiftBuildSourceBinding": "HOLD_REVIEW_CANDIDATES",
            "appLaunches": 0, "canonicalWrites": 0, "keychainReads": 0, "networkRequests": 0,
            "P01": "PRESERVED_REVERIFY_REQUIRED", "P02": "OFFICIAL_AUTHORITY_UNCHANGED",
            "verifiedFinish": "HOLD"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path.home()/"Enguru/Projects/Engurulaboratuvari")
    args = p.parse_args()
    if platform.system() != "Darwin":
        print(json.dumps({"state": "HOLD_MAC_REQUIRED", "canonicalWrites": 0}))
        return 2
    try:
        result = observe(args.root)
    except (OSError, ValueError, subprocess.SubprocessError, UnicodeError) as exc:
        print(json.dumps({"state": "HOLD_SOURCE_CAPTURE", "reason": type(exc).__name__, "canonicalWrites": 0}))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["state"] == "PASS_SOURCE_CAPTURE_ONLY" else 2


if __name__ == "__main__":
    sys.exit(main())
