#!/usr/bin/env python3
"""Read-only Gate 12 pre-execution canonical reconciliation guard."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT.parent / "enguru-mac-engineer"

SESSION = ROOT / "governance/mac-engineer/SESSION_STATE_V1.json"
ROADMAP = ROOT / "governance/mac-engineer/PRODUCT_ROADMAP_V1.json"
STATUS = ROOT / "governance/mac-engineer/CURRENT_STATUS.md"
WORKING_PATH = ROOT / "governance/mac-engineer/ACTIVE_WORKING_PATH.md"
WORKLIST = ROOT / "WORKLIST.md"
ACCEPTANCE = (
    ROOT
    / "governance/mac-engineer/V08_PRODUCT_ENGINEERING_OPERATOR_ACCEPTANCE_MATRIX_V1.md"
)

G12 = "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"
G12_EXIT = "PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED"
PRODUCT_BRANCH = "feat/v08-native-productization-provenance"
PRODUCT_HEAD = "0ca33cc7b70fee915d02de72946bbd4bb0e40065"
PRODUCT_BASE = "5432b9b135499cea18273c0e003877b864af92c6"
PRODUCT_PUBLICATION_STATE = (
    "LOCAL_VERIFIED_NOT_REMOTE_EXACT_MAIN_NOT_REMOTE_PARITY"
)
GATE11_EVIDENCE = (
    "/Users/abdal/Enguru/Evidence/MacEngineer/v0.8/"
    "gate11-p12-closure/20260927T223539Z/p12-final-acceptance.json"
)
HISTORICAL_GATE_EVIDENCE = {
    "gate6": {
        "container": "gate6",
        "state": "PASS",
        "field": "evidence",
        "identity": (
            "/Users/abdal/Enguru/Evidence/MacEngineer/v0.8/"
            "gate6-functional-seal/20260924T174037Z/evidence.json"
        ),
    },
    "gate7": {
        "container": "gate7",
        "state": "PASS",
        "field": "evidence",
        "identity": (
            "/Users/abdal/Enguru/Evidence/MacEngineer/v0.8/"
            "gate7-final/20260924T182614Z/evidence.json"
        ),
    },
    "gate8": {
        "container": "gate8Closure",
        "state": "VERIFIED_PASS",
        "field": "evidence",
        "identity": (
            "/Users/abdal/Enguru/Evidence/MacEngineer/v0.8/"
            "gate8-native-layout-verified-finish/20260925T121312Z/"
            "gate8-evidence.json"
        ),
    },
    "gate9": {
        "container": "gate9Closure",
        "state": "VERIFIED_LOCKED",
        "field": "evidence",
        "identity": (
            "/Users/abdal/Enguru/Evidence/MacEngineer/v0.8/"
            "gate9-donecheck-final/20260925T153632Z/"
            "gate9-technical-acceptance.json"
        ),
    },
    "gate10": {
        "container": "gate10Closure",
        "state": "VERIFIED_LOCKED",
        "field": "evidence",
        "identity": (
            "/Users/abdal/Enguru/Evidence/MacEngineer/v0.8/"
            "gate10-final-canonical-reconciliation/20260926T191843Z/"
            "evidence.json"
        ),
    },
}

CURRENT_OBJECTIVE_MARKER = f"CURRENT_OBJECTIVE={G12}"
CURRENT_GATE_MARKER = "CURRENT_GATE=12"
GATE12_EXECUTION_MARKER = "GATE12_EXECUTION_STARTED=0"
CURRENT_FINAL_TARGET_MARKER = "CURRENT_PROGRAM_FINAL_TARGET=v1.3_USABLE_VERIFIED_PRODUCT"

ACCEPTANCE_SEMANTICS = (
    "DoneCheck™ v1.2 exact-main authority consumes criterion-scoped Evidence from Gates 1–11",
    "machine result is PASS",
    "external/deferred evidence remains accurately classified",
    "Human Threshold™ explicitly accepts",
    "canonical state/worklist/roadmap reconcile",
    "v0.8 is locked only after the final acceptance receipt",
    G12_EXIT,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_value(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def expected_product_source() -> dict[str, Any]:
    return {
        "repository": "engurulabory/enguru-mac-engineer",
        "branch": PRODUCT_BRANCH,
        "localVerifiedHead": PRODUCT_HEAD,
        "baseOriginMain": PRODUCT_BASE,
        "worktree": "CLEAN",
        "remoteExactMain": False,
        "remoteParity": False,
        "publicationState": PRODUCT_PUBLICATION_STATE,
        "verificationEvidence": (
            "/Users/abdal/Enguru/Evidence/MacEngineer/v0.8/"
            "gate11-p11-independent-verification/20260927T204728Z/"
            "p11-final-acceptance.json"
        ),
    }


def worklist_current_objective_projections(worklist: str) -> dict[str, list[str]]:
    return {
        "activeObjective": re.findall(
            r"^\*\*Active objective:\*\* `([^`]+)`$",
            worklist,
            flags=re.MULTILINE,
        ),
        "currentSingleObjective": re.findall(
            r"^\*\*Current single objective:\*\* \*\*([^*]+)\*\*\.$",
            worklist,
            flags=re.MULTILINE,
        ),
        "currentObjectiveMarker": re.findall(
            r"^`CURRENT_OBJECTIVE=([^`]+)`$",
            worklist,
            flags=re.MULTILINE,
        ),
    }


def historical_gate_evidence_preserved(
    v08: dict[str, Any],
    gate: str,
) -> bool:
    expected = HISTORICAL_GATE_EVIDENCE[gate]
    record = v08.get(expected["container"]) or {}
    return (
        record.get("state") == expected["state"]
        and record.get(expected["field"]) == expected["identity"]
    )


def evaluate(
    session: dict[str, Any],
    roadmap: dict[str, Any],
    status: str,
    working_path: str,
    worklist: str,
    acceptance: str,
    product_truth: dict[str, Any],
) -> dict[str, Any]:
    v08 = session.get("currentV08") or {}
    closure = v08.get("closureContract") or {}
    gate11 = v08.get("gate11") or {}
    gate12 = v08.get("gate12") or {}
    current = roadmap.get("current") or {}
    versions = {
        item.get("version"): item
        for item in roadmap.get("versions") or []
        if isinstance(item, dict)
    }
    version_v08 = versions.get("v0.8") or {}
    version_v08_finish = version_v08.get("verifiedFinishContract") or {}
    gate11_method = version_v08.get("gate11CommissioningMethod") or {}
    expected_source = expected_product_source()
    worklist_objectives = worklist_current_objective_projections(worklist)
    gate11_closure = v08.get("gate11Closure") or {}

    checks = {
        "SESSION_OBJECTIVE_GATE12": session.get("currentObjective") == G12,
        "SESSION_NEXT_ACTION_GATE12": session.get("nextAction") == G12,
        "SESSION_GATES_1_11_PASSED": closure.get("passedGates") == list(range(1, 12)),
        "SESSION_ONLY_GATE12_ACTIVE": (
            closure.get("activeGate") == 12
            and closure.get("remainingGates") == [12]
        ),
        "SESSION_GATE11_VERIFIED_LOCKED": (
            gate11.get("state") == "VERIFIED_LOCKED"
            and gate11.get("closureEvidence") == GATE11_EVIDENCE
            and gate11_closure.get("state") == "VERIFIED_LOCKED"
            and gate11_closure.get("evidence") == GATE11_EVIDENCE
        ),
        "SESSION_GATE12_ACTIVE_NOT_STARTED": (
            gate12.get("state") == "ACTIVE"
            and gate12.get("executionStarted") is False
            and gate12.get("exit") == G12_EXIT
        ),
        "SESSION_PRESEND_OBJECTIVE_GATE12": (
            (session.get("preSendFilter") or {}).get("activeObjectivePreserved") == G12
        ),
        "ROADMAP_OBJECTIVE_GATE12": (
            current.get("activeObjective") == G12
            and current.get("nextAction") == G12
        ),
        "ROADMAP_GATES_1_11_PASSED": all(
            f"V08_GATE_{gate:02d}_" in "\n".join(current.get("completed") or [])
            for gate in range(1, 12)
        ),
        "ROADMAP_ONLY_GATE12_ACTIVE": (
            current.get("activeGate") == 12
            and current.get("remaining") == [G12]
        ),
        "ROADMAP_V08_FINISH_CONTRACT_GATE12": (
            version_v08.get("nextAction") == G12
            and version_v08_finish.get("passed") == list(range(1, 12))
            and version_v08_finish.get("active") == 12
            and version_v08_finish.get("remaining") == [12]
        ),
        "ROADMAP_GATE11_METHOD_HISTORY_PRESERVED": (
            gate11_method.get("state") == "PREPARED_QUEUED"
            and gate11_method.get("executionActive") is False
        ),
        "CURRENT_OBJECTIVE_TEXT_SURFACES_AGREE": all(
            CURRENT_OBJECTIVE_MARKER in text
            and CURRENT_GATE_MARKER in text
            and GATE12_EXECUTION_MARKER in text
            for text in (status, working_path)
        ),
        "WORKLIST_EXACT_CURRENT_OBJECTIVE": all(
            values == [G12]
            for values in worklist_objectives.values()
        ),
        "SESSION_GATE6_HISTORICAL_EVIDENCE_PRESERVED": (
            historical_gate_evidence_preserved(v08, "gate6")
        ),
        "SESSION_GATE7_HISTORICAL_EVIDENCE_PRESERVED": (
            historical_gate_evidence_preserved(v08, "gate7")
        ),
        "SESSION_GATE8_HISTORICAL_EVIDENCE_PRESERVED": (
            historical_gate_evidence_preserved(v08, "gate8")
        ),
        "SESSION_GATE9_HISTORICAL_EVIDENCE_PRESERVED": (
            historical_gate_evidence_preserved(v08, "gate9")
        ),
        "SESSION_GATE10_HISTORICAL_EVIDENCE_PRESERVED": (
            historical_gate_evidence_preserved(v08, "gate10")
        ),
        "SESSION_GATE11_HISTORICAL_EVIDENCE_PRESERVED": (
            gate11.get("state") == "VERIFIED_LOCKED"
            and gate11.get("closureEvidence") == GATE11_EVIDENCE
            and gate11_closure.get("state") == "VERIFIED_LOCKED"
            and gate11_closure.get("evidence") == GATE11_EVIDENCE
        ),
        "SESSION_PRODUCT_SOURCE_CURRENT": (
            v08.get("currentProductSource") == expected_source
        ),
        "ROADMAP_PRODUCT_SOURCE_CURRENT": (
            current.get("productSource") == expected_source
            and current.get("productSourceSha") == PRODUCT_HEAD
        ),
        "PRODUCT_REPOSITORY_UNCHANGED": product_truth == {
            "branch": PRODUCT_BRANCH,
            "head": PRODUCT_HEAD,
            "originMain": PRODUCT_BASE,
            "mergeBase": PRODUCT_BASE,
            "clean": True,
        },
        "SESSION_FINAL_TARGET_V13": (
            session.get("finalTarget") == "v1.3_USABLE_VERIFIED_PRODUCT"
        ),
        "ROADMAP_FINAL_TARGET_V13": (
            (roadmap.get("finalTarget") or {}).get("version") == "v1.3"
            and (roadmap.get("finalTarget") or {}).get("title")
            == "Usable Verified Product"
        ),
        "CURRENT_FINAL_TARGET_TEXT_SURFACES_AGREE": all(
            CURRENT_FINAL_TARGET_MARKER in text
            for text in (status, working_path, worklist, acceptance)
        ),
        "V12_VERSION_PATH_MILESTONE_PRESERVED": (
            (versions.get("v1.2") or {}).get("state") == "PLANNED_MILESTONE"
            and (versions.get("v1.2") or {}).get("name")
            == "Local Mac Astra Verified Final"
        ),
        "V07_HISTORICAL_LOCK_PRESERVED": (
            (versions.get("v0.7") or {}).get("state") == "VERIFIED_LOCKED"
            and (session.get("currentV07") or {}).get("state") == "VERIFIED_LOCKED"
        ),
        "GATE12_ACCEPTANCE_SEMANTICS_PRESERVED": all(
            item in acceptance for item in ACCEPTANCE_SEMANTICS
        ),
        "NO_NEW_CORE": (
            (v08.get("gate11Closure") or {}).get("newCore") is False
            and "New core:\n\n**false**" in acceptance
        ),
        "NO_GATE12_PASS_OR_LOCK": (
            session.get("currentVersion") == "v0.8"
            and v08.get("state") == "ACTIVE"
            and gate12.get("state") == "ACTIVE"
            and "finalAcceptanceReceipt" not in gate12
            and "humanDecision" not in gate12
        ),
    }

    failed = [name for name, passed in checks.items() if not passed]
    return {
        "schema": "enguru.mac-engineer.v08-gate12-preexecution-reconciliation/v1",
        "state": "PASS" if not failed else "HOLD",
        "activeObjective": G12,
        "gate12ExecutionStarted": 0,
        "productSourceMutationCount": 0 if product_truth.get("clean") else 1,
        "newCore": False,
        "checks": checks,
        "failed": failed,
        "nextAction": (
            "ZEKU_SECOND_LOOK_BEFORE_BOUNDED_RECONCILIATION_COMMIT"
            if not failed
            else "RECONCILE_GATE12_PREEXECUTION_CURRENT_PROJECTIONS"
        ),
    }


def current_product_truth() -> dict[str, Any]:
    return {
        "branch": git_value(PRODUCT, "branch", "--show-current"),
        "head": git_value(PRODUCT, "rev-parse", "HEAD"),
        "originMain": git_value(PRODUCT, "rev-parse", "origin/main"),
        "mergeBase": git_value(PRODUCT, "merge-base", "HEAD", "origin/main"),
        "clean": git_value(PRODUCT, "status", "--porcelain") == "",
    }


def main() -> int:
    result = evaluate(
        load_json(SESSION),
        load_json(ROADMAP),
        STATUS.read_text(encoding="utf-8"),
        WORKING_PATH.read_text(encoding="utf-8"),
        WORKLIST.read_text(encoding="utf-8"),
        ACCEPTANCE.read_text(encoding="utf-8"),
        current_product_truth(),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["state"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
