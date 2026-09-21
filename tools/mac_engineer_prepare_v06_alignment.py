#!/usr/bin/env python3
"""Prepare the minimal v0.6 product-source alignment on Mac, fail-closed and local-only."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from typing import Any


HOME = Path.home()
PRODUCT = HOME / "Enguru" / "Projects" / "enguru-mac-engineer"
RUNTIME = HOME / "Enguru" / "Runtime" / "MacEngineer"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
PREFLIGHT = EVIDENCE_ROOT / "package6-rebuild-install-preflight.json"
OUTPUT = EVIDENCE_ROOT / "package6-product-v06-alignment-prepared.json"

INFO = PRODUCT / "execution_prep" / "native_app" / "Info.plist"
SWIFT = PRODUCT / "execution_prep" / "native_app" / "EnguruMacEngineerApp.swift"
PREP = PRODUCT / "execution_prep" / "native_app" / "prepare_native_app.command"
PRODUCT_RUNTIME = PRODUCT / "runtime"
RUNTIME_RUNTIME = RUNTIME / "runtime"
RUNTIME_ASSET = RUNTIME_RUNTIME / "static" / "engineer-emblem.png"
PRODUCT_ASSET = PRODUCT_RUNTIME / "static" / "engineer-emblem.png"

TARGET_VERSION = "0.6"
BRANCH = "feature/v06-version-branding-alignment"


class AlignmentError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 300,
) -> dict[str, Any]:
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
        "cmd": cmd,
        "returncode": p.returncode,
        "pass": p.returncode == 0,
        "stdout": p.stdout[-12000:],
        "stderr": p.stderr[-12000:],
    }


def git(*args: str) -> str:
    result = run(["git", *args], cwd=PRODUCT)
    if not result["pass"]:
        raise AlignmentError(
            f"GIT_FAILED:{' '.join(args)}:{result['stderr']}"
        )
    return str(result["stdout"]).strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AlignmentError(f"EVIDENCE_REQUIRED:{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AlignmentError(
            f"EVIDENCE_INVALID_JSON:{path}:{exc}"
        ) from exc


def inspect_product() -> dict[str, Any]:
    if not (PRODUCT / ".git").exists():
        raise AlignmentError("PRODUCT_SOURCE_GIT_REQUIRED")

    branch = git("branch", "--show-current")
    head = git("rev-parse", "HEAD")
    origin_main = git("rev-parse", "origin/main")
    status = git("status", "--porcelain")

    return {
        "branch": branch,
        "head": head,
        "origin_main": origin_main,
        "clean": status == "",
        "status": status,
    }


def verify_inputs(preflight: dict[str, Any], product: dict[str, Any]) -> None:
    if preflight.get("state") != "HOLD":
        raise AlignmentError("PREFLIGHT_HOLD_REQUIRED")

    issue_names = set(str(x) for x in preflight.get("issues", []))
    required = {
        "PRODUCT_VERSION_ALIGNMENT_REQUIRED",
        "PRODUCT_BUILD_VERSION_ALIGNMENT_REQUIRED",
    }
    if not required.issubset(issue_names):
        raise AlignmentError(
            "EXPECTED_VERSION_ALIGNMENT_ISSUES_REQUIRED"
        )

    current_only = [
        row.get("path")
        for row in preflight.get(
            "runtime_source_parity", {}
        ).get("rows", [])
        if row.get("state") == "CURRENT_ONLY"
    ]
    if current_only != ["static/engineer-emblem.png"]:
        raise AlignmentError(
            "CURRENT_ONLY_SET_REQUIRES_REVIEW:"
            + ",".join(str(x) for x in current_only)
        )

    if not product["clean"]:
        raise AlignmentError("PRODUCT_SOURCE_CLEAN_REQUIRED")

    if product["branch"] == "main":
        if product["head"] != product["origin_main"]:
            raise AlignmentError(
                "PRODUCT_SOURCE_EXACT_ORIGIN_MAIN_REQUIRED"
            )
    elif product["branch"] != BRANCH:
        raise AlignmentError(
            f"PRODUCT_BRANCH_UNEXPECTED:{product['branch']}"
        )


def align_info_plist() -> tuple[str, str]:
    if not INFO.is_file():
        raise AlignmentError("INFO_PLIST_REQUIRED")
    with INFO.open("rb") as f:
        data = plistlib.load(f)

    old_short = str(data.get("CFBundleShortVersionString", ""))
    old_build = str(data.get("CFBundleVersion", ""))

    data["CFBundleShortVersionString"] = TARGET_VERSION
    data["CFBundleVersion"] = TARGET_VERSION

    with INFO.open("wb") as f:
        plistlib.dump(data, f, fmt=plistlib.FMT_XML, sort_keys=False)

    return old_short, old_build


def copy_branding_asset() -> dict[str, Any]:
    if not RUNTIME_ASSET.is_file():
        raise AlignmentError(
            f"RUNTIME_BRANDING_ASSET_REQUIRED:{RUNTIME_ASSET}"
        )
    PRODUCT_ASSET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RUNTIME_ASSET, PRODUCT_ASSET)
    return {
        "source": str(RUNTIME_ASSET),
        "target": str(PRODUCT_ASSET),
        "sha256": sha256_file(PRODUCT_ASSET),
    }


def verify_product_tree() -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONPATH"] = (
        str(PRODUCT_RUNTIME)
        if not env.get("PYTHONPATH")
        else os.pathsep.join(
            [str(PRODUCT_RUNTIME), env["PYTHONPATH"]]
        )
    )

    compile_result = run(
        ["python3", "-m", "compileall", "-q", "runtime"],
        cwd=PRODUCT,
        env=env,
    )
    tests_result = run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "runtime/tests",
            "-v",
        ],
        cwd=PRODUCT,
        env=env,
    )
    zsh_result = run(
        ["zsh", "-n", str(PREP)],
        cwd=PRODUCT,
    )

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "EnguruMacEngineer"
        swift_result = run(
            [
                "xcrun",
                "swiftc",
                "-parse-as-library",
                str(SWIFT),
                "-o",
                str(out),
                "-framework",
                "SwiftUI",
                "-framework",
                "WebKit",
                "-framework",
                "AppKit",
            ],
            cwd=PRODUCT,
        )
        swift_result["artifact_exists"] = out.exists()
        swift_result["artifact_executable"] = (
            out.exists() and os.access(out, os.X_OK)
        )
        if (
            swift_result["pass"]
            and not swift_result["artifact_executable"]
        ):
            swift_result["pass"] = False
            swift_result["reason"] = (
                "NATIVE_BUILD_ARTIFACT_NOT_EXECUTABLE"
            )

    passed = all(
        item["pass"]
        for item in (
            compile_result,
            tests_result,
            zsh_result,
            swift_result,
        )
    )
    return {
        "pass": passed,
        "runtime_compile": compile_result,
        "runtime_tests": tests_result,
        "native_zsh_syntax": zsh_result,
        "native_swift_build": swift_result,
    }


def main() -> int:
    try:
        preflight = load_json(PREFLIGHT)
        product = inspect_product()
        verify_inputs(preflight, product)

        if product["branch"] == "main":
            git("switch", "-c", BRANCH)

        old_short, old_build = align_info_plist()
        asset = copy_branding_asset()
        verification = verify_product_tree()
        if not verification["pass"]:
            raise AlignmentError(
                "PRODUCT_ALIGNMENT_VERIFICATION_FAILED"
            )

        git("add", "execution_prep/native_app/Info.plist")
        git("add", "runtime/static/engineer-emblem.png")

        staged = git("diff", "--cached", "--name-only").splitlines()
        expected_staged = {
            "execution_prep/native_app/Info.plist",
            "runtime/static/engineer-emblem.png",
        }
        if set(staged) != expected_staged:
            raise AlignmentError(
                "STAGED_CHANGE_SET_MISMATCH:"
                + ",".join(staged)
            )

        status_before_commit = git("status", "--porcelain")
        git(
            "commit",
            "-m",
            "feat: align ENGÜRÜ Mac Engineer product source to v0.6",
        )
        commit = git("rev-parse", "HEAD")
        status_after = git("status", "--porcelain")
        if status_after:
            raise AlignmentError(
                "PRODUCT_SOURCE_NOT_CLEAN_AFTER_COMMIT"
            )

        payload = {
            "schema": (
                "enguru.mac-engineer."
                "product-v06-alignment-prepared/v1"
            ),
            "observed_at": now(),
            "state": "PASS",
            "issues": [],
            "branch": BRANCH,
            "base_main": product["origin_main"],
            "commit": commit,
            "version": {
                "old_short_version": old_short,
                "old_bundle_version": old_build,
                "new_short_version": TARGET_VERSION,
                "new_bundle_version": TARGET_VERSION,
            },
            "branding_asset": asset,
            "staged_files": sorted(expected_staged),
            "status_before_commit": status_before_commit,
            "verification": verification,
            "truth_boundary": (
                "Local product branch prepared and committed. "
                "No push, PR, merge, runtime replacement or app installation "
                "was performed."
            ),
            "next_action": (
                "Push this verified product branch and open a PR. "
                "Require product CI PASS before merge."
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
    except AlignmentError as exc:
        payload = {
            "schema": (
                "enguru.mac-engineer."
                "product-v06-alignment-prepared/v1"
            ),
            "observed_at": now(),
            "state": "HOLD",
            "issues": [str(exc)],
            "truth_boundary": (
                "Fail-closed. No remote publication, merge, runtime "
                "replacement or app installation was performed."
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
