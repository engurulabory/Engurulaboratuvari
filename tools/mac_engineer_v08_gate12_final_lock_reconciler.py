#!/usr/bin/env python3
"""Reconcile the immutable Gate 12 final receipt into the canonical v0.8 lock.

This module is intentionally two-phase:
1. prepare_final_lock_reconciliation() verifies the already-published final
   acceptance receipt and writes one bounded canonical repository difference.
   It returns HOLD until that difference is committed/pushed and re-accepted.
2. verify_final_lock_readback() runs only from the committed final state and
   fails closed unless branch parity, local-candidate acceptance and the final
   receipt binding all still match. Only this phase may return PASS.

No remote push or merge is performed here.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
GOV = ROOT / "governance" / "mac-engineer"

SESSION_PATH = GOV / "SESSION_STATE_V1.json"
ROADMAP_PATH = GOV / "PRODUCT_ROADMAP_V1.json"
REGISTRY_PATH = GOV / "OPERATOR_ACTION_REGISTRY_V1.json"
CANDIDATE_PATH = GOV / "V08_GATE12_FINAL_ACCEPTANCE_RECEIPT_V1.json"
STATUS_PATH = GOV / "CURRENT_STATUS.md"
WORKING_PATH = GOV / "ACTIVE_WORKING_PATH.md"
WORKLIST_PATH = ROOT / "WORKLIST.md"

ACCEPTANCE_STATE = (
    HOME / "Enguru" / "Runtime" / "MacEngineer" / "state"
    / "local-accepted-control-plane-candidate.json"
)
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.8" / "gate12-final"

GATE12 = "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"
EXIT = "PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED"
AWAIT = "AWAIT_NEXT_OBJECTIVE"
EXPECTED_BRANCH = "feat/mac-engineer-v08-product-engineering-operator"
EXPECTED_PRODUCT_PUBLICATION = "LOCAL_VERIFIED_NOT_REMOTE_EXACT_MAIN_NOT_REMOTE_PARITY"
FINAL_RECEIPT_NAME = "final-acceptance-receipt.json"
FINAL_LOCK_RECEIPT_NAME = "canonical-lock-final.json"

EXPECTED_MUTATION_PATHS = {
    "WORKLIST.md",
    "governance/mac-engineer/ACTIVE_WORKING_PATH.md",
    "governance/mac-engineer/CURRENT_STATUS.md",
    "governance/mac-engineer/OPERATOR_ACTION_REGISTRY_V1.json",
    "governance/mac-engineer/PRODUCT_ROADMAP_V1.json",
    "governance/mac-engineer/SESSION_STATE_V1.json",
    "governance/mac-engineer/V08_GATE12_FINAL_ACCEPTANCE_RECEIPT_V1.json",
}


class FinalLockHold(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FinalLockHold(f"JSON_READ_FAILED:{path}:{exc}") from exc
    if not isinstance(value, dict):
        raise FinalLockHold(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _run(*args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def _git(*args: str, timeout: int = 120) -> str:
    result = _run("git", *args, timeout=timeout)
    if result.returncode != 0:
        raise FinalLockHold(
            "GIT_FAILED:" + " ".join(args) + ":" + (result.stderr or result.stdout)[-2000:]
        )
    return result.stdout.strip()


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp = Path(raw)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    _atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def _publication(path: Path, expected_digest: str | None = None) -> dict[str, Any]:
    if not path.resolve().is_relative_to(EVIDENCE_ROOT.resolve()):
        raise FinalLockHold("FINAL_RECEIPT_OUTSIDE_GATE12_EVIDENCE_ROOT")
    marker = path.with_name(path.name + ".enguru-publication.json")
    if not path.is_file() or not marker.is_file():
        raise FinalLockHold("FINAL_RECEIPT_OR_PUBLICATION_MISSING")
    payload = _load(path)
    metadata = _load(marker)
    observed = _digest(path)
    if (
        metadata.get("schema") != "enguru.mac-engineer.publication/v1"
        or metadata.get("digest") != observed
        or metadata.get("byteLength") != len(path.read_bytes())
        or (expected_digest is not None and observed != expected_digest)
    ):
        raise FinalLockHold("FINAL_RECEIPT_PUBLICATION_MISMATCH")
    payload["_observedDigest"] = observed
    return payload


def _v08_version(roadmap: dict[str, Any]) -> dict[str, Any]:
    for item in roadmap.get("versions") or []:
        if isinstance(item, dict) and item.get("version") == "v0.8":
            return item
    raise FinalLockHold("ROADMAP_V08_REQUIRED")


def _preflight() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], Path]:
    session = _load(SESSION_PATH)
    roadmap = _load(ROADMAP_PATH)
    registry = _load(REGISTRY_PATH)
    candidate = _load(CANDIDATE_PATH)

    branch = _git("branch", "--show-current")
    head = _git("rev-parse", "HEAD")
    status = _git("status", "--porcelain")
    if branch != EXPECTED_BRANCH:
        raise FinalLockHold("EXPECTED_CONTROL_BRANCH_REQUIRED")
    if status:
        raise FinalLockHold("CONTROL_PLANE_CLEAN_REQUIRED")

    v08 = session.get("currentV08") or {}
    gate = v08.get("gate12") or {}
    closure = v08.get("closureContract") or {}
    current = roadmap.get("current") or {}
    version = _v08_version(roadmap)
    finish = version.get("verifiedFinishContract") or {}
    action = (registry.get("actions") or {}).get(GATE12) or {}

    if (
        session.get("currentVersion") != "v0.8"
        or session.get("currentObjective") != GATE12
        or v08.get("state") != "ACTIVE"
        or gate.get("state") != "LOCK_EVIDENCE_RECONCILED_PENDING_FINAL_RECEIPT"
        or gate.get("canonicalLockCreated") is not False
        or gate.get("machineResult") != "PASS_11_OF_11"
        or gate.get("humanDecision") != "ACCEPT"
        or closure.get("passedGates") != list(range(1, 12))
        or closure.get("activeGate") != 12
        or closure.get("remainingGates") != [12]
        or current.get("activeObjective") != GATE12
        or current.get("activeGate") != 12
        or current.get("remaining") != [GATE12]
        or version.get("state") != "ACTIVE"
        or finish.get("state") != "LOCK_EVIDENCE_RECONCILED_PENDING_FINAL_RECEIPT"
        or finish.get("passed") != list(range(1, 12))
        or finish.get("remaining") != [12]
        or action.get("finalAcceptanceReceipt") is not False
        or action.get("canonicalLock") is not False
    ):
        raise FinalLockHold("FINAL_LOCK_PRECONDITION_MISMATCH")

    lock_path = Path(str(gate.get("lockEvidence") or ""))
    if not lock_path.is_file():
        raise FinalLockHold("LOCK_EVIDENCE_REQUIRED")
    receipt_path = lock_path.parent / FINAL_RECEIPT_NAME
    receipt = _publication(receipt_path)

    if (
        receipt.get("schema") != "enguru.mac-engineer.v08-gate12-final-acceptance-receipt/v1"
        or receipt.get("state") != "FINAL_ACCEPTANCE_PASS_PENDING_CANONICAL_LOCK"
        or receipt.get("claim") != "GATE12_FINAL_ACCEPTANCE_VERIFIED"
        or receipt.get("canonicalLockCreated") is not False
        or receipt.get("machineResult") != "PASS_11_OF_11"
        or receipt.get("humanDecision") != "ACCEPT"
        or receipt.get("externalA09State") != "HOLD"
        or receipt.get("productPublicationState") != EXPECTED_PRODUCT_PUBLICATION
        or not isinstance(receipt.get("controlHead"), str)
        or _git("merge-base", receipt["controlHead"], head) != receipt["controlHead"]
        or receipt.get("fieldReceipt") != gate.get("fieldAcceptanceReceipt")
        or receipt.get("fieldReceiptDigest") != gate.get("fieldAcceptanceReceiptDigest")
        or receipt.get("lockEvidence") != gate.get("lockEvidence")
        or receipt.get("lockEvidenceDigest") != gate.get("lockEvidenceDigest")
        or receipt.get("terminalCandidateId") != gate.get("terminalCandidateId")
        or receipt.get("finalAcceptanceCandidate") != str(CANDIDATE_PATH)
        or receipt.get("finalAcceptanceCandidateDigest") != _digest(CANDIDATE_PATH)
    ):
        raise FinalLockHold("FINAL_RECEIPT_BINDING_MISMATCH")

    product = v08.get("currentProductSource") or {}
    if (
        receipt.get("productHead") != product.get("localVerifiedHead")
        or product.get("publicationState") != EXPECTED_PRODUCT_PUBLICATION
    ):
        raise FinalLockHold("FINAL_RECEIPT_PRODUCT_BINDING_MISMATCH")

    if (
        candidate.get("schema") != "enguru.mac-engineer.v08-gate12-final-acceptance/v1"
        or candidate.get("state") != "CANDIDATE_PENDING_FRESH_REMOTE_READBACK"
        or candidate.get("objective") != GATE12
        or candidate.get("exit") != EXIT
        or candidate.get("postCommitVerificationRequired") is not True
        or candidate.get("fieldReceiptDigest") != gate.get("fieldAcceptanceReceiptDigest")
        or candidate.get("lockEvidenceDigest") != gate.get("lockEvidenceDigest")
        or candidate.get("humanDecision") != "ACCEPT"
        or (candidate.get("doneCheck") or {}).get("criteria") != "PASS_11_OF_11"
    ):
        raise FinalLockHold("FINAL_ACCEPTANCE_CANDIDATE_MISMATCH")

    return session, roadmap, registry, candidate, receipt_path


def _replace_gate12_worklist(text: str, *, receipt_path: Path, digest: str) -> str:
    marker = "<!-- ENGURU_GATE12_PREEXECUTION_CURRENT_AUTHORITY_V1 -->"
    if marker not in text:
        raise FinalLockHold("WORKLIST_GATE12_MARKER_REQUIRED")
    prefix = text.split(marker, 1)[0]
    block = f"""{marker}

### v0.8 Gate 11 — FINAL VERIFIED CLOSURE

- [x] **Gate 11 — Consolidated Real-Mac Product Engineering Commissioning — VERIFIED / LOCKED**
- Exit: `V08_CONSOLIDATED_MAC_COMMISSIONING_PASS`
- DoneCheck™ v1.2: **PASS**
- Evidence: `/Users/abdal/Enguru/Evidence/MacEngineer/v0.8/gate11-p12-closure/20260927T223539Z/p12-final-acceptance.json`

### v0.8 Gate 12 — FINAL CANONICAL LOCK RECONCILED

- [x] **Gate 12 — DoneCheck™ v1.2 + Human Threshold™ + Version Lock — VERIFIED / LOCKED**
- Canonical identifier: `{GATE12}`
- Exit: `{EXIT}`
- DoneCheck™ v1.2: **11/11 PASS**
- Human Threshold™: **ACCEPT**
- Final acceptance receipt: `{receipt_path}`
- Final acceptance receipt digest: `{digest}`
- External A09: **HOLD / EXTERNAL**.
- Product remote publication: **DEFERRED**; local verified publication classification is preserved.
- Canonical lock repository difference requires mandatory commit/push + fresh local-candidate acceptance + post-commit operator readback before operator PASS.
- Current program final target: **v1.3 — Usable Verified Product**.

**NEXT ACTION — commit/push this bounded reconciliation, run fresh local candidate acceptance, then `enguru-mac continue` for final post-commit readback.**
"""
    return prefix + block.rstrip() + "\n"


def _replace_status(text: str, *, receipt_path: Path, digest: str) -> str:
    start = text.find("## Gate 12 lock evidence reconciliation")
    boundary = text.find("## PROGRAMMER AGENT AUTHORING DISCIPLINE")
    if start < 0 or boundary < 0 or boundary <= start:
        raise FinalLockHold("CURRENT_STATUS_GATE12_BOUNDARY_REQUIRED")
    top = f"""## Gate 12 final canonical lock reconciliation

**STATE — FINAL LOCK RECONCILED / POST-COMMIT READBACK REQUIRED.**

DoneCheck™ v1.2 remains **PASS 11/11** and Human Threshold™ remains **ACCEPT**.
The immutable final acceptance receipt is now reconciled into the canonical
v0.8 closure candidate.

**FINAL RECEIPT —** `{receipt_path}`;
digest `{digest}`.

External A09 remains **HOLD / EXTERNAL**. Product publication remains
`{EXPECTED_PRODUCT_PUBLICATION}`. No product mutation, remote product push,
new core or second canonical truth is introduced by this reconciliation.

**NEXT ACTION —** Commit and push only the bounded Gate 12 reconciliation,
fresh-accept that exact working-branch HEAD, then run `enguru-mac continue`
for mandatory post-commit readback. Operator PASS is forbidden before that
readback.

**Updated:** 2026-09-29
**Program target:** ENGÜRÜ Mac Engineering™ v1.3 — Usable Verified Product
**Current version:** v0.8 — PRODUCT ENGINEERING OPERATOR / FINAL LOCK CANDIDATE
**Current objective:** {GATE12}
**Canonical objective id:** `V08_PRODUCT_ENGINEERING_OPERATOR`

`CURRENT_OBJECTIVE={GATE12}`

`CURRENT_GATE=NONE`

`GATE12_EXECUTION_STARTED=1`

`V08_CANONICAL_LOCK_CANDIDATE=1`

`CURRENT_PROGRAM_FINAL_TARGET=v1.3_USABLE_VERIFIED_PRODUCT`

## CURRENT ENGINEERING TRUTH

ENGÜRÜ Mac Engineering™ v0.7 remains **LONG-RUN RELIABILITY VERIFIED / LOCKED**.
v0.8 Gates 1–12 are reconciled as the final lock candidate. The final
acceptance receipt digest is bound above; mandatory post-commit readback is
the only remaining acceptance action before operator PASS.

Current product source remains the clean local verified branch
`feat/v08-native-productization-provenance` at
`0ca33cc7b70fee915d02de72946bbd4bb0e40065`, based on `origin/main`
`5432b9b135499cea18273c0e003877b864af92c6`. It is not remote exact-main
and not remote parity; publication remains a separate authority surface.

"""
    return text[:start] + top + text[boundary:]


def _replace_working_path(text: str, *, receipt_path: Path, digest: str) -> str:
    start = text.find("## CURRENT GATE 12 AUTHORITY")
    boundary = text.find("Bu dosya ENGÜRÜ Mac Engineer™")
    if start < 0 or boundary < 0 or boundary <= start:
        raise FinalLockHold("ACTIVE_WORKING_PATH_GATE12_BOUNDARY_REQUIRED")
    block = f"""## CURRENT GATE 12 AUTHORITY

`CURRENT_OBJECTIVE={GATE12}`

`CURRENT_GATE=NONE`

`GATE12_EXECUTION_STARTED=1`

`CURRENT_PROGRAM_FINAL_TARGET=v1.3_USABLE_VERIFIED_PRODUCT`

Gate 11 remains **VERIFIED / LOCKED**. Gate 12 is reconciled as the final
canonical lock candidate from immutable final acceptance receipt
`{receipt_path}` with digest `{digest}`.

The only remaining v0.8 acceptance action is mandatory post-commit readback:
exact working-branch parity → fresh local-candidate acceptance → operator
readback. External A09 remains HOLD and product publication remains local
verified / remote-deferred.

"""
    return text[:start] + block + text[boundary:]


def prepare_final_lock_reconciliation() -> dict[str, Any]:
    session, roadmap, registry, candidate, receipt_path = _preflight()
    receipt = _publication(receipt_path)
    digest = str(receipt.pop("_observedDigest"))

    v08 = session["currentV08"]
    gate = v08["gate12"]
    closure = v08["closureContract"]
    policy = v08.get("controlPlaneLocalContinuity") or {}

    v08["state"] = "VERIFIED_LOCKED"
    v08["nextAction"] = AWAIT
    v08["localContinuityNextAction"] = AWAIT
    v08["localContinuityState"] = "VERIFIED_LOCKED"
    policy["state"] = "VERIFIED_LOCAL_AUTHORITY_PENDING_EXTERNAL_RECONCILIATION"
    policy["currentTechnicalTarget"] = GATE12
    policy["nextAfterPass"] = AWAIT

    closure["passedGates"] = list(range(1, 13))
    closure["activeGate"] = None
    closure["remainingGates"] = []

    gate.update({
        "state": "VERIFIED_LOCKED",
        "canonicalLockCreated": True,
        "finalAcceptanceReceipt": str(receipt_path),
        "finalAcceptanceReceiptDigest": digest,
        "finalAcceptanceControlHead": receipt["controlHead"],
        "finalLockReadback": "PENDING_POST_COMMIT",
        "nextAction": AWAIT,
        "observedAt": _now(),
    })

    current = roadmap["current"]
    completed = list(current.get("completed") or [])
    for item in (
        "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK_PASS",
        EXIT,
    ):
        if item not in completed:
            completed.append(item)
    current.update({
        "state": "V08_PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED",
        "completed": completed,
        "remaining": [],
        "activeGate": None,
        "nextAction": AWAIT,
    })
    gate_current = current.get("gate12FieldAcceptance") or {}
    gate_current.update({
        "state": "VERIFIED_LOCKED",
        "canonicalLockCreated": True,
        "finalAcceptanceReceipt": str(receipt_path),
        "finalAcceptanceReceiptDigest": digest,
    })
    current["gate12FieldAcceptance"] = gate_current

    version = _v08_version(roadmap)
    version["state"] = "VERIFIED_LOCKED"
    version["nextAction"] = AWAIT
    finish = version.get("verifiedFinishContract") or {}
    finish.update({
        "state": "VERIFIED_LOCKED",
        "passed": list(range(1, 13)),
        "active": None,
        "remaining": [],
        "canonicalLockCreated": True,
        "finalAcceptanceReceipt": str(receipt_path),
        "finalAcceptanceReceiptDigest": digest,
        "postCommitReadback": "REQUIRED",
    })
    version["verifiedFinishContract"] = finish

    action = registry["actions"][GATE12]
    action.update({
        "handler": "V08_GATE12_FINAL_LOCK_READBACK",
        "finalAcceptanceReceipt": True,
        "canonicalLock": True,
        "finalAcceptanceReceiptCandidate": False,
        "finalAcceptanceReceiptDigest": digest,
        "postCommitReadbackRequired": True,
    })

    candidate.update({
        "state": "VERIFIED_LOCKED",
        "finalAcceptanceReceipt": str(receipt_path),
        "finalAcceptanceReceiptDigest": digest,
        "canonicalLockCreated": True,
        "postCommitVerificationRequired": True,
        "postCommitVerificationState": "PENDING",
    })

    originals = {
        SESSION_PATH: SESSION_PATH.read_text(encoding="utf-8"),
        ROADMAP_PATH: ROADMAP_PATH.read_text(encoding="utf-8"),
        REGISTRY_PATH: REGISTRY_PATH.read_text(encoding="utf-8"),
        CANDIDATE_PATH: CANDIDATE_PATH.read_text(encoding="utf-8"),
        STATUS_PATH: STATUS_PATH.read_text(encoding="utf-8"),
        WORKING_PATH: WORKING_PATH.read_text(encoding="utf-8"),
        WORKLIST_PATH: WORKLIST_PATH.read_text(encoding="utf-8"),
    }

    try:
        _atomic_json(SESSION_PATH, session)
        _atomic_json(ROADMAP_PATH, roadmap)
        _atomic_json(REGISTRY_PATH, registry)
        _atomic_json(CANDIDATE_PATH, candidate)
        _atomic_text(STATUS_PATH, _replace_status(originals[STATUS_PATH], receipt_path=receipt_path, digest=digest))
        _atomic_text(WORKING_PATH, _replace_working_path(originals[WORKING_PATH], receipt_path=receipt_path, digest=digest))
        _atomic_text(WORKLIST_PATH, _replace_gate12_worklist(originals[WORKLIST_PATH], receipt_path=receipt_path, digest=digest))

        changed = [
            line
            for line in _git("status", "--porcelain").splitlines()
            if line
        ]
        changed_paths = {
            line[3:] if len(line) >= 4 else line
            for line in changed
        }
        if changed_paths != EXPECTED_MUTATION_PATHS:
            raise FinalLockHold(
                "FINAL_LOCK_MUTATION_SCOPE_MISMATCH:" + ",".join(sorted(changed_paths))
            )
        diff_check = _run("git", "diff", "--check")
        if diff_check.returncode != 0:
            raise FinalLockHold("FINAL_LOCK_DIFF_CHECK_FAILED:" + diff_check.stderr[-2000:])
    except Exception:
        for path, value in originals.items():
            _atomic_text(path, value)
        raise

    return {
        "state": "HOLD",
        "reason": "GATE12_FINAL_LOCK_RECONCILIATION_COMMIT_REQUIRED",
        "finalAcceptanceReceipt": str(receipt_path),
        "finalAcceptanceReceiptDigest": digest,
        "canonicalLockCreated": True,
        "expectedMutationPaths": sorted(EXPECTED_MUTATION_PATHS),
        "nextAction": "COMMIT_PUSH_ACCEPT_AND_FRESH_READBACK",
    }


def verify_final_lock_readback() -> dict[str, Any]:
    session = _load(SESSION_PATH)
    roadmap = _load(ROADMAP_PATH)
    registry = _load(REGISTRY_PATH)
    candidate = _load(CANDIDATE_PATH)

    v08 = session.get("currentV08") or {}
    gate = v08.get("gate12") or {}
    closure = v08.get("closureContract") or {}
    current = roadmap.get("current") or {}
    version = _v08_version(roadmap)
    finish = version.get("verifiedFinishContract") or {}
    action = (registry.get("actions") or {}).get(GATE12) or {}

    receipt_path = Path(str(gate.get("finalAcceptanceReceipt") or ""))
    digest = str(gate.get("finalAcceptanceReceiptDigest") or "")
    receipt = _publication(receipt_path, digest)
    receipt.pop("_observedDigest", None)

    fetch = _run("git", "fetch", "--prune", "origin", timeout=300)
    if fetch.returncode != 0:
        raise FinalLockHold("FINAL_LOCK_REMOTE_REFRESH_REQUIRED:" + fetch.stderr[-2000:])

    branch = _git("branch", "--show-current")
    head = _git("rev-parse", "HEAD")
    origin_branch = _git("rev-parse", f"origin/{EXPECTED_BRANCH}")
    status = _git("status", "--porcelain")

    if (
        branch != EXPECTED_BRANCH
        or status
        or head != origin_branch
        or _git("merge-base", receipt["controlHead"], head) != receipt["controlHead"]
    ):
        raise FinalLockHold("FINAL_LOCK_POSTCOMMIT_GIT_READBACK_MISMATCH")

    acceptance = _load(ACCEPTANCE_STATE)
    acceptance_checks = acceptance.get("acceptance") or {}
    if (
        acceptance.get("state") != "PASS"
        or acceptance.get("branch") != EXPECTED_BRANCH
        or acceptance.get("head") != head
        or acceptance.get("clean") is not True
        or acceptance_checks.get("targetedTests") != "PASS"
        or acceptance_checks.get("fullRegression") != "PASS"
        or acceptance_checks.get("diffCheck") != "PASS"
        or acceptance_checks.get("remoteBranchParity") != "PASS"
        or acceptance_checks.get("canonicalContext") != "PASS"
        or acceptance_checks.get("sessionStart") != "PASS"
    ):
        raise FinalLockHold("FINAL_LOCK_LOCAL_ACCEPTANCE_REQUIRED")

    if (
        session.get("currentVersion") != "v0.8"
        or session.get("currentObjective") != GATE12
        or v08.get("state") != "VERIFIED_LOCKED"
        or gate.get("state") != "VERIFIED_LOCKED"
        or gate.get("canonicalLockCreated") is not True
        or gate.get("machineResult") != "PASS_11_OF_11"
        or gate.get("humanDecision") != "ACCEPT"
        or closure.get("passedGates") != list(range(1, 13))
        or closure.get("activeGate") is not None
        or closure.get("remainingGates") != []
        or current.get("state") != "V08_PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED"
        or current.get("activeGate") is not None
        or current.get("remaining") != []
        or version.get("state") != "VERIFIED_LOCKED"
        or finish.get("state") != "VERIFIED_LOCKED"
        or finish.get("passed") != list(range(1, 13))
        or finish.get("remaining") != []
        or action.get("finalAcceptanceReceipt") is not True
        or action.get("canonicalLock") is not True
        or candidate.get("state") != "VERIFIED_LOCKED"
        or candidate.get("canonicalLockCreated") is not True
        or candidate.get("finalAcceptanceReceiptDigest") != digest
        or receipt.get("machineResult") != "PASS_11_OF_11"
        or receipt.get("humanDecision") != "ACCEPT"
        or receipt.get("externalA09State") != "HOLD"
        or receipt.get("productPublicationState") != EXPECTED_PRODUCT_PUBLICATION
    ):
        raise FinalLockHold("FINAL_LOCK_CANONICAL_READBACK_MISMATCH")

    final_path = receipt_path.parent / FINAL_LOCK_RECEIPT_NAME
    final_payload = {
        "schema": "enguru.mac-engineer.v08-gate12-canonical-lock/v1",
        "state": "VERIFIED_LOCKED",
        "claim": EXIT,
        "observedAt": _now(),
        "controlHead": head,
        "sourceFinalAcceptanceControlHead": receipt["controlHead"],
        "productHead": receipt["productHead"],
        "finalAcceptanceReceipt": str(receipt_path),
        "finalAcceptanceReceiptDigest": digest,
        "machineResult": "PASS_11_OF_11",
        "humanDecision": "ACCEPT",
        "externalA09State": "HOLD",
        "productPublicationState": EXPECTED_PRODUCT_PUBLICATION,
        "canonicalLockCreated": True,
        "remoteWorkingBranchParity": True,
        "fullRegression": "PASS",
        "doneCheck": "PASS",
        "nextAction": AWAIT,
    }

    # Crash-durable enough for this final readback: write temp + fsync + replace,
    # and bind a publication sidecar exactly as the earlier Gate 12 publisher does.
    _atomic_json(final_path, final_payload)
    final_digest = _digest(final_path)
    marker = final_path.with_name(final_path.name + ".enguru-publication.json")
    _atomic_json(marker, {
        "schema": "enguru.mac-engineer.publication/v1",
        "digest": final_digest,
        "byteLength": len(final_path.read_bytes()),
    })

    return {
        "state": "PASS",
        "claim": EXIT,
        "canonicalLockCreated": True,
        "controlHead": head,
        "finalAcceptanceReceipt": str(receipt_path),
        "finalAcceptanceReceiptDigest": digest,
        "finalLockEvidence": str(final_path),
        "finalLockEvidenceDigest": final_digest,
        "externalA09State": "HOLD",
        "productPublicationState": EXPECTED_PRODUCT_PUBLICATION,
        "nextAction": AWAIT,
    }


if __name__ == "__main__":
    try:
        session = _load(SESSION_PATH)
        gate = ((session.get("currentV08") or {}).get("gate12") or {})
        if gate.get("state") == "VERIFIED_LOCKED" and gate.get("canonicalLockCreated") is True:
            result = verify_final_lock_readback()
        else:
            result = prepare_final_lock_reconciliation()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result.get("state") == "PASS" else 2)
    except (FinalLockHold, OSError, ValueError, KeyError, RuntimeError) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)
