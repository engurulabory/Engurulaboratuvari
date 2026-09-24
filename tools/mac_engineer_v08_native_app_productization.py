#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineering™ v0.8 Gate 5 — Native App Productization + Provenance.

First real v0.8 product mutation. The tool is fail-closed and bounded to exactly
three product paths on one dedicated product branch. It does not push remotely.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import time
from typing import Any
from urllib.request import urlopen

HOME = Path.home()
CONTROL = Path(__file__).resolve().parents[1]
PRODUCT = HOME / "Enguru" / "Projects" / "enguru-mac-engineer"
SESSION = CONTROL / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
CONTRACT = CONTROL / "governance" / "mac-engineer" / "V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE_V1.md"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.8" / "native-app-productization"
RUNTIME_INSTALL = HOME / "Enguru" / "Runtime" / "MacEngineer" / "runtime"
STATE_RELEASE = HOME / "Enguru" / "Runtime" / "MacEngineer" / "state" / "release.json"
USER_APP = HOME / "Applications" / "ENGÜRÜ Mac Engineer.app"

PRODUCT_BASELINE = "5432b9b135499cea18273c0e003877b864af92c6"
PRODUCT_BRANCH = "feat/v08-native-productization-provenance"
PRODUCT_VERSION = "0.8"
DONECHECK_EXACT_MAIN = "8b90a8fc93453dd8a84994195d28d14b15e261cb"

AUTHORIZED_PATHS = (
    "execution_prep/native_app/Info.plist",
    "execution_prep/native_app/prepare_native_app.command",
    "runtime/tests/test_v08_native_productization.py",
)

PREPARE_V08 = r'''#!/bin/zsh
set -euo pipefail

ROOT="$HOME/Enguru"
ME="$ROOT/Runtime/MacEngineer"
APP_ROOT="$ME/App"
APP="$APP_ROOT/ENGÜRÜ Mac Engineer.app"
CONTENTS="$APP/Contents"
MACOS="$CONTENTS/MacOS"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
PRODUCT_ROOT="$(cd "$SRC_DIR/../.." && pwd)"
RUNTIME_SRC="$(cd "$SRC_DIR/../../runtime" && pwd)"
EVIDENCE="$ROOT/Evidence/MacEngineer"
TS="$(date -u +%Y%m%dT%H%M%SZ)"

print "STATE — ENGÜRÜ Mac Engineer™ native app v0.8 productization"
[[ "$(uname -s)" == "Darwin" ]] || { print "BLOCKED — this commissioning step requires macOS"; exit 2; }
command -v python3 >/dev/null || { print "BLOCKED — python3 not found"; exit 3; }
command -v git >/dev/null || { print "BLOCKED — git not found"; exit 4; }
command -v swiftc >/dev/null || { print "HOLD — swiftc not found"; exit 5; }
command -v codesign >/dev/null || { print "HOLD — codesign not found"; exit 6; }
command -v rsync >/dev/null || { print "HOLD — rsync not found"; exit 7; }

SOURCE_REPOSITORY="engurulabory/enguru-mac-engineer"
SOURCE_BRANCH="$(git -C "$PRODUCT_ROOT" branch --show-current)"
SOURCE_COMMIT="$(git -C "$PRODUCT_ROOT" rev-parse HEAD)"
SOURCE_DIRTY="$(git -C "$PRODUCT_ROOT" status --porcelain)"
BUNDLE_VERSION="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$SRC_DIR/Info.plist")"

[[ "$SOURCE_BRANCH" == "feat/v08-native-productization-provenance" ]] || {
  print "HOLD — source branch identity mismatch"
  exit 8
}
[[ -z "$SOURCE_DIRTY" ]] || {
  print "HOLD — source worktree must be clean before package provenance"
  exit 9
}
[[ "$BUNDLE_VERSION" == "0.8" ]] || {
  print "HOLD — bundle version must be 0.8"
  exit 10
}

mkdir -p \
  "$ROOT/Projects" "$ROOT/Cores" "$ROOT/Evidence" "$ROOT/Archive" \
  "$ROOT/GitVault" "$ME/state" "$ME/tasks" "$ME/checkpoints" \
  "$ME/logs" "$ME/config" "$APP_ROOT" "$ROOT/Backup" "$EVIDENCE"

BACKUP_ROOT="$ROOT/Backup/MacEngineer"
mkdir -p "$BACKUP_ROOT"

BUILD_DIR="$(mktemp -d "$APP_ROOT/.macengineer-build.XXXXXX")"
STAGED_APP="$BUILD_DIR/ENGÜRÜ Mac Engineer.app"
STAGED_CONTENTS="$STAGED_APP/Contents"
STAGED_MACOS="$STAGED_CONTENTS/MacOS"
STAGED_RESOURCES="$STAGED_CONTENTS/Resources"
RUNTIME_STAGE="$(mktemp -d "$ME/.runtime-stage.XXXXXX")"

cleanup_stage() {
  [[ -d "$BUILD_DIR" ]] && rm -rf "$BUILD_DIR"
  [[ -d "$RUNTIME_STAGE" ]] && rm -rf "$RUNTIME_STAGE"
}
trap cleanup_stage EXIT INT TERM HUP

mkdir -p "$STAGED_MACOS" "$STAGED_RESOURCES"
cp "$SRC_DIR/Info.plist" "$STAGED_CONTENTS/Info.plist"
cp "$SRC_DIR/Resources/ENGURU_Mac_Engineer.icns" "$STAGED_RESOURCES/ENGURU_Mac_Engineer.icns"

swiftc -parse-as-library "$SRC_DIR/EnguruMacEngineerApp.swift" \
  -o "$STAGED_MACOS/EnguruMacEngineer" \
  -framework SwiftUI -framework WebKit -framework AppKit
chmod +x "$STAGED_MACOS/EnguruMacEngineer"

python3 - "$STAGED_RESOURCES/release.json" \
  "$SOURCE_REPOSITORY" "$SOURCE_BRANCH" "$SOURCE_COMMIT" \
  "$BUNDLE_VERSION" "$RUNTIME_SRC" <<'PY'
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

out = Path(sys.argv[1])
repository, branch, commit, version = sys.argv[2:6]
runtime = Path(sys.argv[6])

h = hashlib.sha256()
count = 0
for path in sorted(p for p in runtime.rglob("*") if p.is_file()):
    if "__pycache__" in path.parts or path.suffix == ".pyc":
        continue
    rel = path.relative_to(runtime).as_posix()
    h.update(rel.encode("utf-8"))
    h.update(b"\0")
    h.update(path.read_bytes())
    h.update(b"\0")
    count += 1

payload = {
    "schema": "enguru.mac-engineer.native-release/v0.8",
    "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "product": "ENGÜRÜ Mac Engineer™",
    "sourceRepository": repository,
    "sourceBranch": branch,
    "sourceCommit": commit,
    "bundleVersion": version,
    "runtimeDigest": "sha256:" + h.hexdigest(),
    "runtimeFileCount": count,
    "authority": "ENGÜRÜ Mac-Native Engineering Authority™",
}
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

codesign --force --deep --sign - "$STAGED_APP"
codesign --verify --deep --strict "$STAGED_APP"

rsync -a --delete \
  --exclude='__pycache__/' --exclude='*.pyc' \
  "$RUNTIME_SRC/" "$RUNTIME_STAGE/"

RUNTIME_PREVIOUS=""
OLD_APP=""
BACKUP_APP="none"

if [[ -d "$ME/runtime" ]]; then
  RUNTIME_PREVIOUS="$ME/.runtime-previous.${TS}"
  mv "$ME/runtime" "$RUNTIME_PREVIOUS"
fi

if [[ -e "$APP" ]]; then
  BACKUP_APP="$BACKUP_ROOT/ENGÜRÜ Mac Engineer_${TS}.app"
  ditto "$APP" "$BACKUP_APP"
  OLD_APP="$APP_ROOT/.ENGÜRÜ Mac Engineer.previous.${TS}.app"
  mv "$APP" "$OLD_APP"
fi

activate_failed=0
mv "$RUNTIME_STAGE" "$ME/runtime" || activate_failed=1
if [[ "$activate_failed" -eq 0 ]]; then
  mv "$STAGED_APP" "$APP" || activate_failed=1
fi

if [[ "$activate_failed" -ne 0 ]]; then
  [[ -d "$ME/runtime" ]] && rm -rf "$ME/runtime"
  [[ -n "$RUNTIME_PREVIOUS" && -d "$RUNTIME_PREVIOUS" ]] && mv "$RUNTIME_PREVIOUS" "$ME/runtime"
  [[ -e "$APP" ]] && rm -rf "$APP"
  [[ -n "$OLD_APP" && -e "$OLD_APP" ]] && mv "$OLD_APP" "$APP"
  print "BLOCKED — staged activation failed; previous runtime/app restored"
  exit 11
fi

[[ -n "$RUNTIME_PREVIOUS" && -d "$RUNTIME_PREVIOUS" ]] && rm -rf "$RUNTIME_PREVIOUS"
[[ -n "$OLD_APP" && -e "$OLD_APP" ]] && rm -rf "$OLD_APP"

rm -rf "$BUILD_DIR"
trap - EXIT INT TERM HUP

USER_APPS="$HOME/Applications"
USER_APP="$USER_APPS/ENGÜRÜ Mac Engineer.app"
USER_STAGE="$USER_APPS/.ENGÜRÜ Mac Engineer.installing.${TS}.app"
USER_PREV="$USER_APPS/.ENGÜRÜ Mac Engineer.previous.${TS}.app"

mkdir -p "$USER_APPS"
[[ -e "$USER_STAGE" ]] && rm -rf "$USER_STAGE"
ditto "$APP" "$USER_STAGE"

if [[ -L "$USER_APP" ]]; then
  rm "$USER_APP"
elif [[ -e "$USER_APP" ]]; then
  mv "$USER_APP" "$USER_PREV"
fi

if mv "$USER_STAGE" "$USER_APP"; then
  [[ -e "$USER_PREV" ]] && rm -rf "$USER_PREV"
else
  [[ -e "$USER_APP" ]] && rm -rf "$USER_APP"
  [[ -e "$USER_PREV" ]] && mv "$USER_PREV" "$USER_APP"
  print "BLOCKED — user app installation failed; previous app restored"
  exit 12
fi

touch "$USER_APP"
codesign --verify --deep --strict "$USER_APP"

mkdir -p "$ME/state"
cp "$USER_APP/Contents/Resources/release.json" "$ME/state/release.json"

PARITY="$(
  rsync -nrc --delete \
    --exclude='__pycache__/' --exclude='*.pyc' \
    "$RUNTIME_SRC/" "$ME/runtime/"
)"
[[ -z "$PARITY" ]] || {
  print "HOLD — installed runtime parity mismatch"
  print "$PARITY"
  exit 13
}

INSTALLED_VERSION="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$USER_APP/Contents/Info.plist")"
[[ "$INSTALLED_VERSION" == "$BUNDLE_VERSION" ]] || {
  print "HOLD — installed bundle version mismatch"
  exit 14
}

INSTALLED_COMMIT="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["sourceCommit"])' "$USER_APP/Contents/Resources/release.json")"
[[ "$INSTALLED_COMMIT" == "$SOURCE_COMMIT" ]] || {
  print "HOLD — installed release source commit mismatch"
  exit 15
}

PYVER="$(python3 --version 2>&1)"
GITVER="$(git --version 2>&1)"
SWIFTVER="$(swiftc --version | head -n 1)"
RECEIPT="$EVIDENCE/native_app_prepare_${TS}.txt"

cat > "$RECEIPT" <<EOT
STATE
root=$ROOT
runtime=$ME/runtime
app=$APP
user_app=$USER_APP
runtime_action=source-bound runtime sync
install_strategy=staged atomic replace
previous_app_backup=$BACKUP_APP

SOURCE
repository=$SOURCE_REPOSITORY
branch=$SOURCE_BRANCH
commit=$SOURCE_COMMIT
bundle_version=$BUNDLE_VERSION

EVIDENCE
python=$PYVER
git=$GITVER
swift=$SWIFTVER
codesign=PASS
runtime_parity=PASS
release_manifest=$USER_APP/Contents/Resources/release.json
runtime_release_manifest=$ME/state/release.json

CLAIM
Native v0.8 candidate bundle and installed runtime are provenance-bound to one exact local product commit.

NEXT ACTION
Fresh-launch the installed app and verify runtime readiness from the installed runtime.

VERDICT
HOLD — package/install/provenance PASS; fresh launch readiness still required.
EOT

print "STATE=PASS"
print "NATIVE_PACKAGE_INSTALL=PASS"
print "SOURCE_COMMIT=$SOURCE_COMMIT"
print "BUNDLE_VERSION=$BUNDLE_VERSION"
print "RUNTIME_PARITY=PASS"
print "CODESIGN=PASS"
print "RELEASE_MANIFEST=$USER_APP/Contents/Resources/release.json"
print "EVIDENCE=$RECEIPT"
'''

PRODUCT_TEST = r'''from __future__ import annotations

from pathlib import Path
import plistlib
import unittest


ROOT = Path(__file__).resolve().parents[2]
INFO = ROOT / "execution_prep" / "native_app" / "Info.plist"
PREP = ROOT / "execution_prep" / "native_app" / "prepare_native_app.command"


class V08NativeProductizationTests(unittest.TestCase):
    def test_bundle_version_is_v08_candidate(self) -> None:
        with INFO.open("rb") as handle:
            payload = plistlib.load(handle)
        self.assertEqual(payload["CFBundleShortVersionString"], "0.8")
        self.assertEqual(payload["CFBundleVersion"], "0.8")

    def test_prepare_is_source_bound_and_provenance_bound(self) -> None:
        text = PREP.read_text(encoding="utf-8")
        for expected in (
            'SOURCE_REPOSITORY="engurulabory/enguru-mac-engineer"',
            'SOURCE_COMMIT="$(git -C "$PRODUCT_ROOT" rev-parse HEAD)"',
            'release.json',
            'runtimeDigest',
            'rsync -a --delete',
            'RUNTIME_PARITY=PASS',
            'codesign --verify --deep --strict',
        ):
            self.assertIn(expected, text)

    def test_gate5_does_not_encode_remote_push(self) -> None:
        text = PREP.read_text(encoding="utf-8")
        self.assertNotIn("git push", text)


if __name__ == "__main__":
    unittest.main()
'''


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run(
    args: list[str],
    *,
    cwd: Path = PRODUCT,
    timeout: int = 1800,
    env: dict[str, str] | None = None,
    allow: tuple[int, ...] = (0,),
) -> dict[str, Any]:
    p = subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
        env=env,
    )
    result = {
        "args": args,
        "code": p.returncode,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }
    if p.returncode not in allow:
        raise RuntimeError(
            "COMMAND_FAILED:"
            + " ".join(args)
            + ":"
            + (p.stderr or p.stdout)[-1800:]
        )
    return result


def git(*args: str) -> str:
    return run(["git", *args], timeout=180)["stdout"]


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{label}_REQUIRED:{path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label}_OBJECT_REQUIRED")
    return value


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def runtime_digest(root: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    count = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        rel = path.relative_to(root).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
        count += 1
    return "sha256:" + h.hexdigest(), count


def runtime_parity(source: Path, installed: Path) -> dict[str, Any]:
    source_files = {
        p.relative_to(source).as_posix(): file_sha256(p)
        for p in source.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }
    installed_files = {
        p.relative_to(installed).as_posix(): file_sha256(p)
        for p in installed.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }
    changed = sorted(
        path for path in source_files.keys() & installed_files.keys()
        if source_files[path] != installed_files[path]
    )
    missing = sorted(source_files.keys() - installed_files.keys())
    extra = sorted(installed_files.keys() - source_files.keys())
    return {
        "state": "PASS" if not changed and not missing and not extra else "HOLD",
        "changed": changed,
        "missing": missing,
        "extra": extra,
        "sourceFileCount": len(source_files),
        "installedFileCount": len(installed_files),
    }


def plist_version(path: Path) -> str:
    with path.open("rb") as handle:
        return str(plistlib.load(handle)["CFBundleShortVersionString"])


def latest_gate4_evidence() -> Path | None:
    root = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.8" / "full-product-engineering-chain-binding"
    if not root.is_dir():
        return None
    items = sorted(root.glob("*/evidence.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return items[0] if items else None


def write_hold(run_dir: Path, reason: str, details: dict[str, Any] | None = None) -> int:
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "evidence.json"
    payload = {
        "schema": "enguru.mac-engineer.v08-native-productization/v1",
        "observedAt": utc_now(),
        "state": "HOLD",
        "gate": "V08-05",
        "reason": reason,
        "details": details or {},
        "remotePush": False,
        "nextAction": "RECOVERY_REQUIRED",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("STATE=HOLD")
    print(f"HOLD={reason}")
    print(f"EVIDENCE={path}")
    print("NEXT_ACTION=RECOVERY_REQUIRED")
    return 2


def ensure_preconditions() -> dict[str, Any]:
    session = load_json(SESSION, "SESSION_STATE")
    if session.get("currentVersion") != "v0.8":
        raise RuntimeError("CURRENT_VERSION_V08_REQUIRED")
    if session.get("currentObjective") != "V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE":
        raise RuntimeError("V08_GATE5_OBJECTIVE_REQUIRED")
    v08 = session.get("currentV08") or {}
    if (v08.get("gate4") or {}).get("state") != "PASS":
        raise RuntimeError("V08_GATE4_CANONICAL_PASS_REQUIRED")
    dc = v08.get("doneCheckAuthority") or {}
    if dc.get("exactMain") != DONECHECK_EXACT_MAIN:
        raise RuntimeError("DONECHECK_V1_2_EXACT_MAIN_REQUIRED")
    if not CONTRACT.is_file():
        raise RuntimeError("V08_GATE5_CONTRACT_REQUIRED")
    if not PRODUCT.is_dir() or not (PRODUCT / ".git").exists():
        raise RuntimeError("PRODUCT_REPOSITORY_REQUIRED")
    return session


def prepare_product_branch() -> dict[str, Any]:
    run(["git", "fetch", "origin", "main", PRODUCT_BRANCH], timeout=300)

    origin_main = git("rev-parse", "origin/main")
    origin_branch = git("rev-parse", f"origin/{PRODUCT_BRANCH}")
    if origin_main != PRODUCT_BASELINE:
        raise RuntimeError("PRODUCT_ORIGIN_MAIN_BASELINE_DRIFT")
    if origin_branch != PRODUCT_BASELINE:
        raise RuntimeError("PRODUCT_REMOTE_WORKING_BRANCH_BASELINE_DRIFT")

    current = git("branch", "--show-current")
    status = git("status", "--porcelain")
    if status:
        raise RuntimeError("PRODUCT_WORKTREE_CLEAN_REQUIRED")

    if current == "main":
        head = git("rev-parse", "HEAD")
        if head != PRODUCT_BASELINE:
            raise RuntimeError("PRODUCT_MAIN_EXACT_BASELINE_REQUIRED")
        run(["git", "switch", "-c", PRODUCT_BRANCH, "--track", f"origin/{PRODUCT_BRANCH}"], timeout=120)
    elif current != PRODUCT_BRANCH:
        raise RuntimeError("PRODUCT_WORKING_BRANCH_REQUIRED")

    head = git("rev-parse", "HEAD")
    base = git("merge-base", PRODUCT_BASELINE, "HEAD")
    if base != PRODUCT_BASELINE:
        raise RuntimeError("PRODUCT_BRANCH_BASELINE_ANCESTRY_REQUIRED")

    return {
        "branch": PRODUCT_BRANCH,
        "headBefore": head,
        "originMain": origin_main,
        "originWorkingBranch": origin_branch,
    }


def backup_authorized_paths(run_dir: Path) -> dict[str, str]:
    backup = run_dir / "source-backup"
    backup.mkdir(parents=True, exist_ok=True)
    refs: dict[str, str] = {}
    for rel in AUTHORIZED_PATHS:
        src = PRODUCT / rel
        if src.exists():
            dst = backup / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            refs[rel] = str(dst)
    return refs


def apply_mutation() -> None:
    info = PRODUCT / AUTHORIZED_PATHS[0]
    with info.open("rb") as handle:
        plist = plistlib.load(handle)
    plist["CFBundleShortVersionString"] = PRODUCT_VERSION
    plist["CFBundleVersion"] = PRODUCT_VERSION
    with info.open("wb") as handle:
        plistlib.dump(plist, handle, sort_keys=False)

    prepare = PRODUCT / AUTHORIZED_PATHS[1]
    prepare.write_text(PREPARE_V08, encoding="utf-8")
    prepare.chmod(0o755)

    test = PRODUCT / AUTHORIZED_PATHS[2]
    test.parent.mkdir(parents=True, exist_ok=True)
    test.write_text(PRODUCT_TEST, encoding="utf-8")


def verify_mutation_scope_against_worktree() -> list[str]:
    paths = sorted(
        path
        for path in set(
            git("diff", "--name-only").splitlines()
            + git("ls-files", "--others", "--exclude-standard").splitlines()
        )
        if path
    )
    if paths != sorted(AUTHORIZED_PATHS):
        raise RuntimeError("PRODUCT_MUTATION_SCOPE_MISMATCH:" + ",".join(paths))
    return paths


def run_product_regression(run_dir: Path) -> dict[str, Any]:
    logs = run_dir / "logs"
    logs.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["PYTHONPATH"] = str(PRODUCT / "runtime")
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    checks: list[dict[str, Any]] = []

    def checked(name: str, args: list[str], timeout: int = 1800) -> None:
        result = run(args, timeout=timeout, env=env)
        log = logs / f"{name}.log"
        log.write_text(
            (result["stdout"] + "\n" + result["stderr"]).strip() + "\n",
            encoding="utf-8",
        )
        checks.append({
            "name": name,
            "state": "PASS",
            "log": str(log),
            "sha256": file_sha256(log),
        })

    checked(
        "targeted-v08-native-productization",
        [
            "python3", "-B", "-m", "unittest", "discover",
            "-s", "runtime/tests",
            "-p", "test_v08_native_productization.py",
            "-v",
        ],
    )
    checked(
        "full-runtime-regression",
        ["python3", "-B", "-m", "unittest", "discover", "-s", "runtime/tests", "-v"],
        timeout=2400,
    )
    checked(
        "native-prep-syntax",
        ["zsh", "-n", "execution_prep/native_app/prepare_native_app.command"],
        timeout=120,
    )

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "EnguruMacEngineer"
        checked(
            "native-swift-build",
            [
                "xcrun", "swiftc", "-parse-as-library",
                "execution_prep/native_app/EnguruMacEngineerApp.swift",
                "-o", str(out),
                "-framework", "SwiftUI",
                "-framework", "WebKit",
                "-framework", "AppKit",
            ],
            timeout=900,
        )

    checked("diff-check", ["git", "diff", "--check"], timeout=120)
    return {"state": "PASS", "checks": checks}


def commit_product_change() -> dict[str, Any]:
    run(["git", "add", *AUTHORIZED_PATHS], timeout=120)
    staged = sorted(path for path in git("diff", "--cached", "--name-only").splitlines() if path)
    if staged != sorted(AUTHORIZED_PATHS):
        raise RuntimeError("PRODUCT_STAGED_SCOPE_MISMATCH:" + ",".join(staged))

    run([
        "git", "commit", "-m",
        "Mac Engineer v0.8: native app productization and provenance",
    ], timeout=300)

    if git("status", "--porcelain"):
        raise RuntimeError("PRODUCT_POST_COMMIT_CLEAN_REQUIRED")

    head = git("rev-parse", "HEAD")
    changed = sorted(path for path in git("diff", "--name-only", f"{PRODUCT_BASELINE}...{head}").splitlines() if path)
    if changed != sorted(AUTHORIZED_PATHS):
        raise RuntimeError("PRODUCT_COMMIT_SCOPE_MISMATCH:" + ",".join(changed))

    ahead = git("rev-list", "--count", f"origin/{PRODUCT_BRANCH}..HEAD")
    if ahead != "1":
        raise RuntimeError("PRODUCT_LOCAL_COMMIT_AHEAD_ONE_REQUIRED")

    return {
        "head": head,
        "changedPaths": changed,
        "aheadRemoteWorkingBranch": int(ahead),
    }


def existing_commit_state() -> dict[str, Any] | None:
    head = git("rev-parse", "HEAD")
    if head == PRODUCT_BASELINE:
        return None

    changed = sorted(path for path in git("diff", "--name-only", f"{PRODUCT_BASELINE}...{head}").splitlines() if path)
    if changed != sorted(AUTHORIZED_PATHS):
        raise RuntimeError("EXISTING_PRODUCT_COMMIT_SCOPE_MISMATCH:" + ",".join(changed))
    if plist_version(PRODUCT / AUTHORIZED_PATHS[0]) != PRODUCT_VERSION:
        raise RuntimeError("EXISTING_PRODUCT_VERSION_V08_REQUIRED")
    if git("status", "--porcelain"):
        raise RuntimeError("EXISTING_PRODUCT_WORKTREE_CLEAN_REQUIRED")
    ahead = git("rev-list", "--count", f"origin/{PRODUCT_BRANCH}..HEAD")
    if ahead != "1":
        raise RuntimeError("EXISTING_PRODUCT_LOCAL_AHEAD_ONE_REQUIRED")
    return {"head": head, "changedPaths": changed, "aheadRemoteWorkingBranch": 1}


def stop_old_runtime() -> None:
    run(["pkill", "-x", "EnguruMacEngineer"], timeout=30, allow=(0, 1))
    pattern = str(HOME / "Enguru" / "Runtime" / "MacEngineer" / "runtime" / "app.py")
    run(["pkill", "-f", pattern], timeout=30, allow=(0, 1))
    time.sleep(0.5)


def package_install() -> dict[str, Any]:
    stop_old_runtime()
    result = run(
        ["zsh", "execution_prep/native_app/prepare_native_app.command"],
        timeout=1800,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return {
        "state": "PASS",
        "stdoutTail": result["stdout"][-5000:],
        "stderrTail": result["stderr"][-3000:],
    }


def fresh_launch_ready(timeout_seconds: int = 30) -> dict[str, Any]:
    run(["open", str(USER_APP)], cwd=HOME, timeout=30)
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            with urlopen("http://127.0.0.1:8765/api/status", timeout=1.5) as response:
                payload = json.loads(response.read().decode("utf-8"))
                status_code = response.status
            if (
                status_code == 200
                and payload.get("service") == "ENGÜRÜ Mac Engineer™"
                and payload.get("state") == "RUNNING"
                and payload.get("governance") == "ACTIVE"
            ):
                return {"state": "PASS", "payload": payload}
            last_error = "STATUS_PAYLOAD_NOT_READY"
        except Exception as exc:
            last_error = f"{type(exc).__name__}:{exc}"
        time.sleep(0.5)
    raise RuntimeError("FRESH_APP_RUNTIME_READINESS_FAILED:" + last_error)


def verify_installed(product_head: str) -> dict[str, Any]:
    if not USER_APP.is_dir():
        raise RuntimeError("INSTALLED_USER_APP_REQUIRED")

    installed_info = USER_APP / "Contents" / "Info.plist"
    installed_release = USER_APP / "Contents" / "Resources" / "release.json"
    if plist_version(installed_info) != PRODUCT_VERSION:
        raise RuntimeError("INSTALLED_BUNDLE_VERSION_V08_REQUIRED")
    release = load_json(installed_release, "INSTALLED_RELEASE_MANIFEST")
    if release.get("sourceCommit") != product_head:
        raise RuntimeError("INSTALLED_RELEASE_SOURCE_COMMIT_MISMATCH")
    if release.get("sourceBranch") != PRODUCT_BRANCH:
        raise RuntimeError("INSTALLED_RELEASE_SOURCE_BRANCH_MISMATCH")
    if release.get("bundleVersion") != PRODUCT_VERSION:
        raise RuntimeError("INSTALLED_RELEASE_BUNDLE_VERSION_MISMATCH")
    state_release = load_json(STATE_RELEASE, "RUNTIME_RELEASE_MANIFEST")
    if state_release != release:
        raise RuntimeError("RUNTIME_RELEASE_MANIFEST_PARITY_REQUIRED")

    source_runtime = PRODUCT / "runtime"
    parity = runtime_parity(source_runtime, RUNTIME_INSTALL)
    if parity["state"] != "PASS":
        raise RuntimeError("SOURCE_INSTALLED_RUNTIME_PARITY_REQUIRED")

    source_digest, count = runtime_digest(source_runtime)
    if release.get("runtimeDigest") != source_digest:
        raise RuntimeError("RELEASE_RUNTIME_DIGEST_MISMATCH")
    if release.get("runtimeFileCount") != count:
        raise RuntimeError("RELEASE_RUNTIME_FILE_COUNT_MISMATCH")

    codesign = run(
        ["codesign", "--verify", "--deep", "--strict", str(USER_APP)],
        cwd=HOME,
        timeout=120,
    )
    return {
        "state": "PASS",
        "bundleVersion": PRODUCT_VERSION,
        "release": release,
        "runtimeParity": parity,
        "codesign": "PASS",
        "codesignOutput": codesign["stderr"] or codesign["stdout"],
    }


def main() -> int:
    run_dir = EVIDENCE_ROOT / stamp()
    try:
        ensure_preconditions()
        run_dir.mkdir(parents=True, exist_ok=False)

        gate4 = latest_gate4_evidence()
        branch_state = prepare_product_branch()
        backups = backup_authorized_paths(run_dir)

        existing = existing_commit_state()
        regression: dict[str, Any]
        if existing is None:
            apply_mutation()
            scope = verify_mutation_scope_against_worktree()
            regression = run_product_regression(run_dir)
            commit = commit_product_change()
            commit["mutationScopeBeforeCommit"] = scope
        else:
            regression = run_product_regression(run_dir)
            commit = existing
            commit["mutationScopeBeforeCommit"] = list(AUTHORIZED_PATHS)

        product_head = commit["head"]

        if git("rev-parse", f"origin/{PRODUCT_BRANCH}") != PRODUCT_BASELINE:
            raise RuntimeError("REMOTE_WORKING_BRANCH_MUST_REMAIN_BASELINE")
        if git("status", "--porcelain"):
            raise RuntimeError("PRODUCT_CLEAN_BEFORE_PACKAGE_REQUIRED")

        package = package_install()
        installed = verify_installed(product_head)
        readiness = fresh_launch_ready()
        installed_after_launch = verify_installed(product_head)

        path = run_dir / "evidence.json"
        payload = {
            "schema": "enguru.mac-engineer.v08-native-productization/v1",
            "observedAt": utc_now(),
            "state": "PASS",
            "gate": "V08-05",
            "claim": (
                "The v0.8 native candidate package, installed runtime and installed app "
                "are provenance-bound to one bounded local product commit."
            ),
            "sourceGate4Evidence": str(gate4) if gate4 else None,
            "contract": str(CONTRACT.relative_to(CONTROL)),
            "product": {
                "repository": "engurulabory/enguru-mac-engineer",
                "path": str(PRODUCT),
                "baselineExactMain": PRODUCT_BASELINE,
                "workingBranch": PRODUCT_BRANCH,
                "localCommit": product_head,
                "remoteWorkingBranchHead": PRODUCT_BASELINE,
                "remotePush": False,
                "changedPaths": commit["changedPaths"],
                "aheadRemoteWorkingBranch": commit["aheadRemoteWorkingBranch"],
            },
            "branchPreparation": branch_state,
            "sourceBackups": backups,
            "regression": regression,
            "packageInstall": package,
            "freshLaunchReadiness": readiness,
            "installedVerification": installed_after_launch,
            "sourceBundleVersion": plist_version(PRODUCT / AUTHORIZED_PATHS[0]),
            "installedBundleVersion": installed_after_launch["bundleVersion"],
            "runtimeParity": installed_after_launch["runtimeParity"],
            "releaseManifest": installed_after_launch["release"],
            "codesign": installed_after_launch["codesign"],
            "authorizedMutationPaths": list(AUTHORIZED_PATHS),
            "mutationPathCount": len(AUTHORIZED_PATHS),
            "unnecessaryNewCoreCount": 0,
            "secondCanonicalTruth": False,
            "doneCheckAuthority": {
                "product": "DoneCheck™ v1.2",
                "version": "1.2.0",
                "exactMain": DONECHECK_EXACT_MAIN,
            },
            "nextAction": "V08_EXISTING_PRODUCT_CHANGE_SCENARIO",
        }
        payload["evidencePath"] = str(path)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        print("STATE=PASS")
        print("V08_GATE_05=PASS")
        print("NATIVE_APP_PRODUCTIZATION=PASS")
        print(f"PRODUCT_BRANCH={PRODUCT_BRANCH}")
        print(f"PRODUCT_LOCAL_COMMIT={product_head}")
        print("PRODUCT_REMOTE_PUSH=false")
        print("PRODUCT_MUTATION_PATHS=3")
        print("SOURCE_BUNDLE_VERSION=0.8")
        print("INSTALLED_BUNDLE_VERSION=0.8")
        print("SOURCE_INSTALLED_RUNTIME_PARITY=PASS")
        print("RELEASE_PROVENANCE=PASS")
        print("CODESIGN=PASS")
        print("FRESH_APP_RUNTIME_READINESS=PASS")
        print("DONECHECK_AUTHORITY=DoneCheck™_v1.2")
        print(f"EVIDENCE={path}")
        print("NEXT_ACTION=V08_EXISTING_PRODUCT_CHANGE_SCENARIO")
        return 0
    except Exception as exc:
        return write_hold(
            run_dir,
            f"{type(exc).__name__}:{exc}",
            {
                "productBranch": PRODUCT_BRANCH,
                "productBaseline": PRODUCT_BASELINE,
                "authorizedPaths": list(AUTHORIZED_PATHS),
            },
        )


if __name__ == "__main__":
    raise SystemExit(main())
