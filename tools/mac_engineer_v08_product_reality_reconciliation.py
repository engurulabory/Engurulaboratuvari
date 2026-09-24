#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineering™ v0.8 Gate 2 — Product Reality Reconciliation.

Consumes the latest Gate 1 self-engineering baseline Evidence and turns measured
product truth into a bounded required-difference contract. Read-only with respect
to product source, runtime, installed app and canonical repositories.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

HOME = Path.home()
CONTROL = Path(__file__).resolve().parents[1]
SESSION = CONTROL / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
BASELINE_ROOT = (
    HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.8"
    / "self-engineering-baseline"
)
EVIDENCE_ROOT = (
    HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.8"
    / "product-reality-reconciliation"
)

DONECHECK_VERSION = "1.2.0"
DONECHECK_EXACT_MAIN = "8b90a8fc93453dd8a84994195d28d14b15e261cb"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{label}_REQUIRED:{path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"{label}_INVALID:{type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label}_OBJECT_REQUIRED")
    return value


def latest_baseline() -> Path:
    if not BASELINE_ROOT.is_dir():
        raise RuntimeError("V08_GATE1_EVIDENCE_ROOT_REQUIRED")
    candidates = sorted(
        BASELINE_ROOT.glob("*/evidence.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise RuntimeError("V08_GATE1_PASS_EVIDENCE_REQUIRED")
    return candidates[0]


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def fail(reason: str, details: dict[str, Any] | None = None) -> int:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_ROOT / f"{stamp()}-hold.json"
    payload = {
        "schema": "enguru.mac-engineer.v08-product-reality-reconciliation/v1",
        "observedAt": now(),
        "state": "HOLD",
        "gate": "V08-02",
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
    try:
        session = load_json(SESSION, "SESSION_STATE")
        if session.get("currentVersion") != "v0.8":
            raise RuntimeError("CURRENT_VERSION_V08_REQUIRED")
        if session.get("currentObjective") != "V08_SELF_ENGINEERING_PRODUCT_REALITY_RECONCILIATION":
            raise RuntimeError("V08_GATE2_OBJECTIVE_REQUIRED")

        v08 = session.get("currentV08") or {}
        gate1 = v08.get("gate1") or {}
        if gate1.get("state") != "PASS":
            raise RuntimeError("V08_GATE1_CANONICAL_PASS_REQUIRED")

        baseline_path = latest_baseline()
        baseline = load_json(baseline_path, "V08_GATE1_EVIDENCE")
        if baseline.get("state") != "PASS" or baseline.get("gate") != "V08-01":
            raise RuntimeError("V08_GATE1_EVIDENCE_PASS_REQUIRED")
        if baseline.get("mutation") is not False:
            raise RuntimeError("V08_GATE1_READ_ONLY_REQUIRED")
        if baseline.get("remotePush") is not False:
            raise RuntimeError("V08_GATE1_REMOTE_PUSH_FALSE_REQUIRED")
        if baseline.get("secondCanonicalTruth") is not False:
            raise RuntimeError("V08_GATE1_SECOND_CANONICAL_TRUTH_FALSE_REQUIRED")

        verification = baseline.get("verification") or {}
        for key in (
            "runtimeCompile",
            "runtimeRegression",
            "nativePrepSyntax",
            "nativeSwiftBuild",
            "productWorktreeAfterAudit",
        ):
            if verification.get(key) not in ("PASS", "CLEAN"):
                raise RuntimeError(f"V08_GATE1_{key.upper()}_PASS_REQUIRED")

        observations = baseline.get("observations") or {}
        bundle_source = (observations.get("sourceBundleVersion") or {}).get("short")
        bundle_installed = (observations.get("installedBundleVersion") or {}).get("short")
        native = observations.get("nativeShell") or {}
        ui = observations.get("ui") or {}
        runtime = observations.get("runtime") or {}

        required_measurements = {
            "sourceBundleVersion": bundle_source,
            "installedBundleVersion": bundle_installed,
            "swiftUI": native.get("swiftUI"),
            "webKit": native.get("webKit"),
            "wkWebView": native.get("wkWebView"),
            "sidebarPresent": ui.get("sidebarPresent"),
            "statusDrawerPresent": ui.get("statusDrawerPresent"),
            "newWorkSurfacePresent": ui.get("newWorkSurfacePresent"),
            "chatComposerPresent": ui.get("chatComposerPresent"),
            "sourceInstalledRuntimeParity": runtime.get("sourceInstalledParity"),
        }
        missing = [k for k, v in required_measurements.items() if v is None]
        if missing:
            raise RuntimeError("V08_GATE1_MEASUREMENTS_REQUIRED:" + ",".join(missing))

        donecheck = baseline.get("doneCheckAuthority") or {}
        if donecheck.get("version") != DONECHECK_VERSION:
            raise RuntimeError("DONECHECK_V1_2_VERSION_REQUIRED")
        if donecheck.get("exactMain") != DONECHECK_EXACT_MAIN:
            raise RuntimeError("DONECHECK_V1_2_EXACT_MAIN_REQUIRED")

        preserve = [
            "V07_VERIFIED_LOCKED_AUTHORITY_AND_RELIABILITY",
            "MAC_NATIVE_PRIMARY_ENGINEERING_AUTHORITY",
            "LOCAL_FIRST_RUNTIME",
            "SWIFTUI_NATIVE_SHELL",
            "WEBKIT_RUNTIME_SURFACE_UNTIL_EVIDENCE_JUSTIFIES_CHANGE",
            "EXISTING_RELIABILITY_RECOVERY_EVIDENCE_LAYERS",
            "DONECHECK_V1_2_MACHINE_VERIFICATION_AUTHORITY",
            "HUMAN_THRESHOLD_FINAL_AUTHORITY",
        ]

        required_difference: list[dict[str, Any]] = []

        if bundle_source != "0.8" or bundle_installed != "0.8":
            required_difference.append({
                "id": "VERSION_PROVENANCE_ALIGNMENT",
                "state": "PLANNED_GATE_5",
                "current": {
                    "sourceBundleVersion": bundle_source,
                    "installedBundleVersion": bundle_installed,
                },
                "target": "Version changes only after achieved product milestone Evidence.",
            })

        if ui.get("sidebarPresent") or ui.get("statusDrawerPresent"):
            required_difference.append({
                "id": "UX_SIMPLIFICATION_CONTRACT",
                "state": "REQUIRED_GATE_3",
                "current": {
                    "sidebarPresent": bool(ui.get("sidebarPresent")),
                    "statusDrawerPresent": bool(ui.get("statusDrawerPresent")),
                    "newWorkSurfacePresent": bool(ui.get("newWorkSurfacePresent")),
                    "chatComposerPresent": bool(ui.get("chatComposerPresent")),
                },
                "target": (
                    "Define a simpler desktop-first product surface from measured "
                    "user needs before implementation."
                ),
            })

        required_difference.append({
            "id": "FULL_PRODUCT_ENGINEERING_CHAIN_BINDING",
            "state": "REQUIRED_GATE_4",
            "target": (
                "Bind INTAKE→DISCOVER→ARCHITECT→DESIGN→BUILD→TEST→REPAIR→"
                "PACKAGE→DEPLOY→LIVE VERIFY→LIFECYCLE→EVIDENCE→DoneCheck™ v1.2."
            ),
        })

        if runtime.get("sourceInstalledParity") is not True:
            required_difference.insert(0, {
                "id": "SOURCE_INSTALLED_RUNTIME_PARITY",
                "state": "ATTENTION_REQUIRED_GATE_5",
                "current": "MISMATCH",
                "target": "One provenance-bound source/runtime/installed application chain.",
            })

        product_reality = {
            "productSource": baseline.get("product") or {},
            "bundle": {
                "source": bundle_source,
                "installed": bundle_installed,
            },
            "architecture": {
                "nativeShell": "SwiftUI",
                "runtimeSurface": "WKWebView/WebKit",
                "localRuntime": True,
                "nativeRewriteRequired": False,
                "rule": "Reuse current boundary unless Evidence demonstrates a required change.",
            },
            "ui": {
                "sidebarPresent": bool(ui.get("sidebarPresent")),
                "statusDrawerPresent": bool(ui.get("statusDrawerPresent")),
                "newWorkSurfacePresent": bool(ui.get("newWorkSurfacePresent")),
                "chatComposerPresent": bool(ui.get("chatComposerPresent")),
            },
            "runtime": {
                "sourceInstalledParity": bool(runtime.get("sourceInstalledParity")),
                "sourceAppSha256": runtime.get("sourceAppSha256"),
                "installedAppSha256": runtime.get("installedAppSha256"),
            },
        }

        run_dir = EVIDENCE_ROOT / stamp()
        run_dir.mkdir(parents=True, exist_ok=False)
        path = run_dir / "evidence.json"
        payload = {
            "schema": "enguru.mac-engineer.v08-product-reality-reconciliation/v1",
            "observedAt": now(),
            "state": "PASS",
            "gate": "V08-02",
            "claim": "Measured Gate 1 product truth was reconciled into one bounded v0.8 product-engineering contract.",
            "sourceEvidence": str(baseline_path),
            "sourceEvidenceDigest": digest(baseline_path),
            "productReality": product_reality,
            "preserve": preserve,
            "requiredDifference": required_difference,
            "unnecessaryNewCoreCount": 0,
            "productMutation": False,
            "remotePush": False,
            "secondCanonicalTruth": False,
            "doneCheckAuthority": {
                "product": "DoneCheck™ v1.2",
                "version": DONECHECK_VERSION,
                "exactMain": DONECHECK_EXACT_MAIN,
            },
            "nextAction": "V08_UX_AESTHETIC_PRODUCT_CONTRACT",
        }
        payload["evidencePath"] = str(path)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        print("STATE=PASS")
        print("V08_GATE_02=PASS")
        print("PRODUCT_REALITY_RECONCILED=PASS")
        print(f"SOURCE_BUNDLE_VERSION={bundle_source or 'UNKNOWN'}")
        print(f"INSTALLED_BUNDLE_VERSION={bundle_installed or 'UNKNOWN'}")
        print("NATIVE_SHELL=SWIFTUI")
        print("RUNTIME_SURFACE=WKWEBVIEW_WEBKIT")
        print(
            "SOURCE_INSTALLED_RUNTIME_PARITY="
            + ("PASS" if runtime.get("sourceInstalledParity") is True else "ATTENTION_REQUIRED")
        )
        print(f"REQUIRED_DIFFERENCE_COUNT={len(required_difference)}")
        print("UNNECESSARY_NEW_CORE_COUNT=0")
        print("DONECHECK_AUTHORITY=DoneCheck™_v1.2")
        print(f"EVIDENCE={path}")
        print("NEXT_ACTION=V08_UX_AESTHETIC_PRODUCT_CONTRACT")
        return 0

    except Exception as exc:
        return fail(f"{type(exc).__name__}:{exc}")


if __name__ == "__main__":
    raise SystemExit(main())
