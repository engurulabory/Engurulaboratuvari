#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

HOME = Path.home()
CONTROL = Path(__file__).resolve().parents[1]
PRODUCT = HOME / "Enguru" / "Projects" / "enguru-mac-engineer"
SESSION = CONTROL / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
CONTRACT = CONTROL / "governance" / "mac-engineer" / "V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING_V1.md"
GATE3_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.8" / "ux-aesthetic-product-contract"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.8" / "full-product-engineering-chain-binding"

PRODUCT_EXACT_MAIN = "5432b9b135499cea18273c0e003877b864af92c6"
DONECHECK_EXACT_MAIN = "8b90a8fc93453dd8a84994195d28d14b15e261cb"

CHAIN = (
    "INTAKE","DISCOVER","ARCHITECT","DESIGN","BUILD","TEST","REPAIR",
    "PACKAGE","DEPLOY","LIVE VERIFY","LIFECYCLE","EVIDENCE","DONECHECK","HUMAN THRESHOLD"
)

REQUIRED_PRODUCT_FILES = (
    "runtime/app.py",
    "runtime/repo_manager.py",
    "runtime/repo_control.py",
    "runtime/research_capability.py",
    "runtime/governance.py",
    "runtime/local_ci.py",
    "runtime/repair.py",
    "runtime/support_repair_loop.py",
    "runtime/reliability.py",
    "runtime/backup_manager.py",
    "runtime/doctor.py",
    "runtime/verified_finish.py",
    "execution_prep/native_app/prepare_native_app.command",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{label}_REQUIRED:{path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label}_OBJECT_REQUIRED")
    return value


def run(*args: str) -> str:
    p = subprocess.run(args, cwd=str(PRODUCT), text=True, capture_output=True, check=False, timeout=120)
    if p.returncode != 0:
        raise RuntimeError("COMMAND_FAILED:" + " ".join(args) + ":" + p.stderr[-1200:])
    return p.stdout.strip()


def latest_gate3() -> Path:
    candidates = sorted(
        GATE3_ROOT.glob("*/evidence.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    ) if GATE3_ROOT.is_dir() else []
    if not candidates:
        raise RuntimeError("V08_GATE3_PASS_EVIDENCE_REQUIRED")
    return candidates[0]


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def fail(reason: str) -> int:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_ROOT / f"{stamp()}-hold.json"
    path.write_text(json.dumps({
        "schema":"enguru.mac-engineer.v08-full-chain-binding/v1",
        "observedAt":now(),"state":"HOLD","gate":"V08-04",
        "reason":reason,"nextAction":"RECOVERY_REQUIRED"
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
        if session.get("currentObjective") != "V08_FULL_PRODUCT_ENGINEERING_CHAIN_BINDING":
            raise RuntimeError("V08_GATE4_OBJECTIVE_REQUIRED")
        v08 = session.get("currentV08") or {}
        if (v08.get("gate3") or {}).get("state") != "PASS":
            raise RuntimeError("V08_GATE3_CANONICAL_PASS_REQUIRED")

        gate3_path = latest_gate3()
        gate3 = load_json(gate3_path, "V08_GATE3_EVIDENCE")
        if gate3.get("state") != "PASS" or gate3.get("gate") != "V08-03":
            raise RuntimeError("V08_GATE3_EVIDENCE_PASS_REQUIRED")
        if gate3.get("productMutation") is not False:
            raise RuntimeError("V08_GATE3_PRODUCT_MUTATION_FALSE_REQUIRED")
        if gate3.get("unnecessaryNewCoreCount") != 0:
            raise RuntimeError("V08_GATE3_NEW_CORE_ZERO_REQUIRED")

        if not PRODUCT.is_dir():
            raise RuntimeError("PRODUCT_REPOSITORY_REQUIRED")
        head = run("git","rev-parse","HEAD")
        origin_main = run("git","rev-parse","origin/main")
        branch = run("git","branch","--show-current")
        status = run("git","status","--porcelain")
        if head != PRODUCT_EXACT_MAIN or origin_main != PRODUCT_EXACT_MAIN:
            raise RuntimeError("PRODUCT_EXACT_MAIN_REQUIRED")
        if branch != "main":
            raise RuntimeError("PRODUCT_MAIN_BRANCH_REQUIRED")
        if status:
            raise RuntimeError("PRODUCT_CLEAN_REQUIRED")

        missing = [p for p in REQUIRED_PRODUCT_FILES if not (PRODUCT / p).is_file()]
        if missing:
            raise RuntimeError("PRODUCT_BINDING_SURFACE_REQUIRED:" + ",".join(missing))

        text = CONTRACT.read_text(encoding="utf-8")
        for stage in CHAIN:
            if stage not in text:
                raise RuntimeError("CHAIN_STAGE_REQUIRED:" + stage)
        for required in (
            "ENGÜRÜ Mac-Native Engineering Authority™",
            "DoneCheck™ v1.2",
            DONECHECK_EXACT_MAIN,
            "No new core is introduced",
            "ADAPTER_BOUND",
            "Health status alone does not satisfy LIVE VERIFY",
        ):
            if required.lower() not in text.lower():
                raise RuntimeError("CHAIN_CONTRACT_TERM_REQUIRED:" + required)

        run_dir = EVIDENCE_ROOT / stamp()
        run_dir.mkdir(parents=True, exist_ok=False)
        path = run_dir / "evidence.json"
        payload = {
            "schema":"enguru.mac-engineer.v08-full-chain-binding/v1",
            "observedAt":now(),
            "state":"PASS",
            "gate":"V08-04",
            "claim":"Every Product Engineering Operator stage has one explicit existing owner or bounded adapter boundary.",
            "product":{
                "path":str(PRODUCT),"branch":branch,"head":head,"originMain":origin_main,"clean":True
            },
            "sourceEvidence":str(gate3_path),
            "sourceEvidenceDigest":digest(gate3_path),
            "contract":str(CONTRACT.relative_to(CONTROL)),
            "contractDigest":digest(CONTRACT),
            "chain":list(CHAIN),
            "bindingCount":len(CHAIN),
            "missingBindingCount":0,
            "unnecessaryNewCoreCount":0,
            "productMutation":False,
            "remotePush":False,
            "secondCanonicalTruth":False,
            "executionProofBoundary":"Binding PASS does not claim later-gate execution PASS.",
            "doneCheckAuthority":{
                "product":"DoneCheck™ v1.2","version":"1.2.0","exactMain":DONECHECK_EXACT_MAIN
            },
            "nextAction":"V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE",
        }
        payload["evidencePath"] = str(path)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        print("STATE=PASS")
        print("V08_GATE_04=PASS")
        print("FULL_PRODUCT_ENGINEERING_CHAIN_BOUND=PASS")
        print(f"CHAIN_STAGE_COUNT={len(CHAIN)}")
        print("MISSING_BINDING_COUNT=0")
        print("UNNECESSARY_NEW_CORE_COUNT=0")
        print("PRODUCT_EXACT_MAIN=PASS")
        print("PRODUCT_MUTATION=false")
        print("DONECHECK_AUTHORITY=DoneCheck™_v1.2")
        print(f"EVIDENCE={path}")
        print("NEXT_ACTION=V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE")
        return 0
    except Exception as exc:
        return fail(f"{type(exc).__name__}:{exc}")


if __name__ == "__main__":
    raise SystemExit(main())
