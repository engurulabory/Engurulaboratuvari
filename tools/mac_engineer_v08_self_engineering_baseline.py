#!/usr/bin/env python3
"""v0.8 Gate 1 — ENGÜRÜ Mac Engineer™ self-engineering baseline audit.

Read-only with respect to canonical source and installed product. The audit
measures the current product truth before v0.8 product engineering begins.
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
from typing import Any


HOME = Path.home()
CONTROL = Path(__file__).resolve().parents[1]
SESSION = CONTROL / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
PRODUCT = HOME / "Enguru" / "Projects" / "enguru-mac-engineer"
INSTALLED_APP = HOME / "Applications" / "ENGÜRÜ Mac Engineer.app"
INSTALLED_RUNTIME = HOME / "Enguru" / "Runtime" / "MacEngineer" / "runtime"
EVIDENCE_ROOT = (
    HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.8"
    / "self-engineering-baseline"
)

DONECHECK_VERSION = "1.2.0"
DONECHECK_EXACT_MAIN = "8b90a8fc93453dd8a84994195d28d14b15e261cb"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 7200,
) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        return {
            "code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"code": 124, "stdout": "", "stderr": "TIMEOUT"}


def git_value(*args: str) -> str:
    result = run(["git", *args], cwd=PRODUCT, timeout=180)
    return result["stdout"].strip() if result["code"] == 0 else ""


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def plist_version(path: Path) -> dict[str, str | None]:
    if not path.is_file():
        return {"short": None, "build": None}
    with path.open("rb") as handle:
        payload = plistlib.load(handle)
    return {
        "short": str(payload.get("CFBundleShortVersionString") or "") or None,
        "build": str(payload.get("CFBundleVersion") or "") or None,
    }


def fail(reason: str, details: dict[str, Any] | None = None) -> int:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_ROOT / f"{stamp()}-hold.json"
    payload = {
        "schema": "enguru.mac-engineer.v08-self-engineering-baseline/v1",
        "observedAt": now(),
        "state": "HOLD",
        "gate": "V08-01",
        "reason": reason,
        "details": details or {},
        "nextAction": "RECOVERY_REQUIRED",
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("STATE=HOLD")
    print(f"HOLD={reason}")
    print(f"EVIDENCE={path}")
    print("NEXT_ACTION=RECOVERY_REQUIRED")
    return 2


def main() -> int:
    if not SESSION.is_file():
        return fail("SESSION_STATE_REQUIRED")
    session = json.loads(SESSION.read_text(encoding="utf-8"))
    v08 = session.get("currentV08") or {}
    expected_product_sha = str(v08.get("productExactMain") or "")

    if str(session.get("currentVersion") or "") != "v0.8":
        return fail("CURRENT_VERSION_V08_REQUIRED")
    if v08.get("state") != "ACTIVE":
        return fail("V08_ACTIVE_STATE_REQUIRED")
    if not expected_product_sha:
        return fail("V08_PRODUCT_EXACT_MAIN_REQUIRED")
    if not (PRODUCT / ".git").exists():
        return fail("PRODUCT_CHECKOUT_REQUIRED", {"path": str(PRODUCT)})

    fetch = run(["git", "fetch", "origin", "main", "--prune"], cwd=PRODUCT, timeout=300)
    if fetch["code"] != 0:
        return fail(
            "PRODUCT_REMOTE_REFRESH_REQUIRED",
            {"stderr": fetch["stderr"][-2000:]},
        )

    product_truth = {
        "branch": git_value("branch", "--show-current"),
        "head": git_value("rev-parse", "HEAD"),
        "originMain": git_value("rev-parse", "origin/main"),
        "status": git_value("status", "--porcelain"),
    }
    product_truth["clean"] = product_truth["status"] == ""

    if product_truth["branch"] != "main":
        return fail("PRODUCT_MAIN_REQUIRED", product_truth)
    if product_truth["head"] != expected_product_sha:
        return fail(
            "PRODUCT_EXACT_MAIN_REQUIRED",
            {"expected": expected_product_sha, **product_truth},
        )
    if product_truth["originMain"] != expected_product_sha:
        return fail(
            "PRODUCT_ORIGIN_MAIN_PARITY_REQUIRED",
            {"expected": expected_product_sha, **product_truth},
        )
    if not product_truth["clean"]:
        return fail("PRODUCT_WORKTREE_CLEAN_REQUIRED", product_truth)

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(PRODUCT / "runtime")

    compile_result = run(
        ["python3", "-B", "-m", "compileall", "-q", "runtime"],
        cwd=PRODUCT,
        env=env,
    )
    if compile_result["code"] != 0:
        return fail(
            "PRODUCT_RUNTIME_COMPILE_FAILED",
            {"stderr": compile_result["stderr"][-3000:]},
        )

    tests = run(
        ["python3", "-B", "-m", "unittest", "discover", "-s", "runtime/tests", "-v"],
        cwd=PRODUCT,
        env=env,
    )
    if tests["code"] != 0:
        return fail(
            "PRODUCT_RUNTIME_REGRESSION_FAILED",
            {
                "stdout": tests["stdout"][-5000:],
                "stderr": tests["stderr"][-5000:],
            },
        )

    syntax = run(
        ["zsh", "-n", "execution_prep/native_app/prepare_native_app.command"],
        cwd=PRODUCT,
    )
    if syntax["code"] != 0:
        return fail(
            "NATIVE_PREP_SYNTAX_FAILED",
            {"stderr": syntax["stderr"][-3000:]},
        )

    swiftc = shutil.which("swiftc")
    if not swiftc:
        return fail("SWIFTC_REQUIRED")

    with tempfile.TemporaryDirectory(prefix="enguru-v08-baseline-") as tmp:
        out = Path(tmp) / "EnguruMacEngineer"
        swift = run(
            [
                swiftc,
                "-parse-as-library",
                "execution_prep/native_app/EnguruMacEngineerApp.swift",
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
            timeout=1800,
        )
        if swift["code"] != 0 or not out.is_file():
            return fail(
                "NATIVE_SWIFT_BUILD_FAILED",
                {
                    "stdout": swift["stdout"][-3000:],
                    "stderr": swift["stderr"][-5000:],
                },
            )

    source_plist = PRODUCT / "execution_prep" / "native_app" / "Info.plist"
    installed_plist = INSTALLED_APP / "Contents" / "Info.plist"
    source_version = plist_version(source_plist)
    installed_version = plist_version(installed_plist)

    ui_path = PRODUCT / "runtime" / "static" / "index.html"
    swift_path = PRODUCT / "execution_prep" / "native_app" / "EnguruMacEngineerApp.swift"
    ui_text = ui_path.read_text(encoding="utf-8")
    swift_text = swift_path.read_text(encoding="utf-8")

    source_runtime_app = PRODUCT / "runtime" / "app.py"
    installed_runtime_app = INSTALLED_RUNTIME / "app.py"

    observations = {
        "sourceBundleVersion": source_version,
        "installedBundleExists": INSTALLED_APP.is_dir(),
        "installedBundleVersion": installed_version,
        "nativeShell": {
            "swiftUI": "import SwiftUI" in swift_text,
            "webKit": "import WebKit" in swift_text,
            "wkWebView": "WKWebView" in swift_text,
        },
        "ui": {
            "sidebarPresent": 'class="sidebar"' in ui_text,
            "statusDrawerPresent": 'class="drawer"' in ui_text,
            "newWorkSurfacePresent": "Yeni Üretim" in ui_text,
            "chatComposerPresent": "Mac Engineer’a yaz" in ui_text,
        },
        "runtime": {
            "sourceAppSha256": sha256(source_runtime_app),
            "installedAppSha256": sha256(installed_runtime_app),
            "sourceInstalledParity": (
                sha256(source_runtime_app) is not None
                and sha256(source_runtime_app) == sha256(installed_runtime_app)
            ),
        },
    }

    attention: list[str] = []
    if source_version.get("short") == "0.6":
        attention.append("SOURCE_BUNDLE_VERSION_0_6")
    if installed_version.get("short") == "0.6":
        attention.append("INSTALLED_BUNDLE_VERSION_0_6")
    if observations["ui"]["sidebarPresent"]:
        attention.append("CURRENT_UI_SIDEBAR_PRESENT")
    if observations["ui"]["statusDrawerPresent"]:
        attention.append("CURRENT_UI_STATUS_DRAWER_PRESENT")
    if not observations["runtime"]["sourceInstalledParity"]:
        attention.append("SOURCE_INSTALLED_RUNTIME_PARITY_REVIEW")
    attention.append("V08_FULL_PRODUCT_ENGINEERING_CHAIN_PENDING")

    post_status = git_value("status", "--porcelain")
    post_head = git_value("rev-parse", "HEAD")
    if post_status:
        return fail("AUDIT_CHANGED_PRODUCT_WORKTREE", {"status": post_status})
    if post_head != expected_product_sha:
        return fail(
            "PRODUCT_HEAD_CHANGED_DURING_AUDIT",
            {"before": expected_product_sha, "after": post_head},
        )

    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_ROOT / stamp() / "evidence.json"
    path.parent.mkdir(parents=True, exist_ok=False)
    payload = {
        "schema": "enguru.mac-engineer.v08-self-engineering-baseline/v1",
        "observedAt": now(),
        "state": "PASS",
        "gate": "V08-01",
        "claim": (
            "Current ENGÜRÜ Mac Engineer product reality was measured on the "
            "verified product exact-main source before v0.8 product mutation."
        ),
        "product": {
            **product_truth,
            "expectedExactMain": expected_product_sha,
        },
        "verification": {
            "runtimeCompile": "PASS",
            "runtimeRegression": "PASS",
            "nativePrepSyntax": "PASS",
            "nativeSwiftBuild": "PASS",
            "productWorktreeAfterAudit": "CLEAN",
        },
        "observations": observations,
        "attentionRequired": attention,
        "doneCheckAuthority": {
            "product": "DoneCheck™ v1.2",
            "version": DONECHECK_VERSION,
            "exactMain": DONECHECK_EXACT_MAIN,
            "appliedAtFinalGate": True,
        },
        "mutation": False,
        "remotePush": False,
        "secondCanonicalTruth": False,
        "nextAction": "V08_SELF_ENGINEERING_PRODUCT_REALITY_RECONCILIATION",
    }
    payload["evidencePath"] = str(path)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("STATE=PASS")
    print("V08_GATE_01=PASS")
    print(f"PRODUCT_EXACT_MAIN={expected_product_sha}")
    print("PRODUCT_RUNTIME_COMPILE=PASS")
    print("PRODUCT_RUNTIME_REGRESSION=PASS")
    print("NATIVE_PREP_SYNTAX=PASS")
    print("NATIVE_SWIFT_BUILD=PASS")
    print(f"SOURCE_BUNDLE_VERSION={source_version.get('short') or 'UNKNOWN'}")
    print(f"INSTALLED_BUNDLE_VERSION={installed_version.get('short') or 'UNKNOWN'}")
    print(
        "SOURCE_INSTALLED_RUNTIME_PARITY="
        + ("PASS" if observations["runtime"]["sourceInstalledParity"] else "ATTENTION_REQUIRED")
    )
    print(
        "ATTENTION_REQUIRED="
        + (";".join(attention) if attention else "NONE")
    )
    print("DONECHECK_AUTHORITY=DoneCheck™_v1.2")
    print(f"EVIDENCE={path}")
    print("NEXT_ACTION=V08_SELF_ENGINEERING_PRODUCT_REALITY_RECONCILIATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
