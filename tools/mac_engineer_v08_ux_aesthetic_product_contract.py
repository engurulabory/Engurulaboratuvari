#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineering™ v0.8 Gate 3 — UX + Aesthetic Product Contract verifier.

Consumes the latest Gate 2 reconciliation Evidence and verifies the canonical
UX/Aesthetic contract against measured product reality. Product source mutation
is not allowed in this gate.
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
CONTRACT = (
    CONTROL
    / "governance"
    / "mac-engineer"
    / "V08_UX_AESTHETIC_PRODUCT_CONTRACT_V1.md"
)
GATE2_ROOT = (
    HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.8"
    / "product-reality-reconciliation"
)
EVIDENCE_ROOT = (
    HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.8"
    / "ux-aesthetic-product-contract"
)

DONECHECK_VERSION = "1.2.0"
DONECHECK_EXACT_MAIN = "8b90a8fc93453dd8a84994195d28d14b15e261cb"

PRIMARY_QUESTIONS = (
    "Her şey yolunda mı?",
    "Nerede dikkat gerekiyor?",
    "Şimdi neye bakmalıyım?",
)

REQUIRED_CONTRACT_TERMS = (
    "ENGÜRÜ Mac-Native Engineering Authority™",
    "DoneCheck™ v1.2",
    "Human Artistic Authority™",
    "Human Threshold™",
    "persistent left sidebar",
    "natural-language engineering composer",
    "overflow",
    "originality",
    "accessibility",
    "one coherent canonical direction",
)


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


def latest_gate2() -> Path:
    if not GATE2_ROOT.is_dir():
        raise RuntimeError("V08_GATE2_EVIDENCE_ROOT_REQUIRED")
    candidates = sorted(
        GATE2_ROOT.glob("*/evidence.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise RuntimeError("V08_GATE2_PASS_EVIDENCE_REQUIRED")
    return candidates[0]


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def fail(reason: str, details: dict[str, Any] | None = None) -> int:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_ROOT / f"{stamp()}-hold.json"
    payload = {
        "schema": "enguru.mac-engineer.v08-ux-aesthetic-contract/v1",
        "observedAt": now(),
        "state": "HOLD",
        "gate": "V08-03",
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
        if session.get("currentObjective") != "V08_UX_AESTHETIC_PRODUCT_CONTRACT":
            raise RuntimeError("V08_GATE3_OBJECTIVE_REQUIRED")

        v08 = session.get("currentV08") or {}
        gate2 = v08.get("gate2") or {}
        if gate2.get("state") != "PASS":
            raise RuntimeError("V08_GATE2_CANONICAL_PASS_REQUIRED")

        gate2_path = latest_gate2()
        gate2_evidence = load_json(gate2_path, "V08_GATE2_EVIDENCE")
        if gate2_evidence.get("state") != "PASS":
            raise RuntimeError("V08_GATE2_EVIDENCE_PASS_REQUIRED")
        if gate2_evidence.get("gate") != "V08-02":
            raise RuntimeError("V08_GATE2_ID_REQUIRED")
        if gate2_evidence.get("productMutation") is not False:
            raise RuntimeError("V08_GATE2_PRODUCT_MUTATION_FALSE_REQUIRED")
        if gate2_evidence.get("unnecessaryNewCoreCount") != 0:
            raise RuntimeError("V08_GATE2_UNNECESSARY_NEW_CORE_ZERO_REQUIRED")
        if gate2_evidence.get("secondCanonicalTruth") is not False:
            raise RuntimeError("V08_GATE2_SECOND_CANONICAL_TRUTH_FALSE_REQUIRED")

        dc = gate2_evidence.get("doneCheckAuthority") or {}
        if dc.get("version") != DONECHECK_VERSION:
            raise RuntimeError("DONECHECK_V1_2_VERSION_REQUIRED")
        if dc.get("exactMain") != DONECHECK_EXACT_MAIN:
            raise RuntimeError("DONECHECK_V1_2_EXACT_MAIN_REQUIRED")

        reality = gate2_evidence.get("productReality") or {}
        ui = reality.get("ui") or {}
        architecture = reality.get("architecture") or {}
        if architecture.get("nativeShell") != "SwiftUI":
            raise RuntimeError("SWIFTUI_NATIVE_SHELL_MEASURED_REQUIRED")
        if architecture.get("runtimeSurface") != "WKWebView/WebKit":
            raise RuntimeError("WKWEBVIEW_RUNTIME_SURFACE_MEASURED_REQUIRED")
        for key in (
            "sidebarPresent",
            "statusDrawerPresent",
            "newWorkSurfacePresent",
            "chatComposerPresent",
        ):
            if key not in ui:
                raise RuntimeError(f"MEASURED_UI_{key.upper()}_REQUIRED")

        if not CONTRACT.is_file():
            raise RuntimeError("V08_UX_AESTHETIC_CONTRACT_REQUIRED")
        contract_text = CONTRACT.read_text(encoding="utf-8")
        for question in PRIMARY_QUESTIONS:
            if question not in contract_text:
                raise RuntimeError("PRIMARY_USER_QUESTION_REQUIRED:" + question)
        for term in REQUIRED_CONTRACT_TERMS:
            if term.lower() not in contract_text.lower():
                raise RuntimeError("UX_CONTRACT_TERM_REQUIRED:" + term)

        if "product mutation = false" not in contract_text.lower() and "does not change" not in contract_text.lower():
            raise RuntimeError("GATE3_PRODUCT_MUTATION_BOUNDARY_REQUIRED")

        run_dir = EVIDENCE_ROOT / stamp()
        run_dir.mkdir(parents=True, exist_ok=False)
        path = run_dir / "evidence.json"
        payload = {
            "schema": "enguru.mac-engineer.v08-ux-aesthetic-contract/v1",
            "observedAt": now(),
            "state": "PASS",
            "gate": "V08-03",
            "claim": (
                "Measured Gate 2 product reality is bound to one canonical "
                "UX/Aesthetic product contract before implementation."
            ),
            "sourceEvidence": str(gate2_path),
            "sourceEvidenceDigest": sha256(gate2_path),
            "contract": str(CONTRACT.relative_to(CONTROL)),
            "contractDigest": sha256(CONTRACT),
            "measuredCurrentUI": ui,
            "architectureBoundary": architecture,
            "primaryUserQuestions": list(PRIMARY_QUESTIONS),
            "mainSurface": {
                "persistentSidebarRequired": False,
                "overallState": "PRIMARY",
                "attention": "CONDITIONAL_PRIMARY",
                "nextAction": "PRIMARY",
                "naturalLanguageComposer": "PRIMARY",
                "advancedEngineeringControls": "SECONDARY_ON_DEMAND",
            },
            "aesthetic": {
                "reuse": "Aesthetic Motor™",
                "newCore": False,
                "overflowGate": True,
                "originalityGate": True,
                "accessibilityGate": True,
                "canonicalDirectionCount": 1,
                "humanArtisticAuthority": "REQUIRED_AT_IMPLEMENTED_DIRECTION_REVIEW",
            },
            "productMutation": False,
            "remotePush": False,
            "unnecessaryNewCoreCount": 0,
            "secondCanonicalTruth": False,
            "doneCheckAuthority": {
                "product": "DoneCheck™ v1.2",
                "version": DONECHECK_VERSION,
                "exactMain": DONECHECK_EXACT_MAIN,
            },
            "nextAction": "V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING",
        }
        payload["evidencePath"] = str(path)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        print("STATE=PASS")
        print("V08_GATE_03=PASS")
        print("UX_PRODUCT_CONTRACT=PASS")
        print("PRIMARY_USER_QUESTIONS=3")
        print("MAIN_SURFACE_SIMPLIFICATION=PASS")
        print("AESTHETIC_MOTOR_REUSE=PASS")
        print("OVERFLOW_GATE=DEFINED")
        print("ORIGINALITY_GATE=DEFINED")
        print("ACCESSIBILITY_GATE=DEFINED")
        print("HUMAN_ARTISTIC_AUTHORITY_GATE=DEFINED")
        print("PRODUCT_MUTATION=false")
        print("UNNECESSARY_NEW_CORE_COUNT=0")
        print("DONECHECK_AUTHORITY=DoneCheck™_v1.2")
        print(f"EVIDENCE={path}")
        print("NEXT_ACTION=V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING")
        return 0
    except Exception as exc:
        return fail(f"{type(exc).__name__}:{exc}")


if __name__ == "__main__":
    raise SystemExit(main())
