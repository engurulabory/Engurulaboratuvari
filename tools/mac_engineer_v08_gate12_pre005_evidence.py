#!/usr/bin/env python3
"""Prepare criterion-scoped Gate 12 inputs from verified Gates 1–11 field files."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any
from uuid import uuid4

try:
    from mac_engineer_donecheck_v12_bridge import reproduce_verification_result
    from mac_engineer_v08_gate12_pre005_candidate import file_digest
except ModuleNotFoundError:
    from tools.mac_engineer_donecheck_v12_bridge import reproduce_verification_result
    from tools.mac_engineer_v08_gate12_pre005_candidate import file_digest

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "governance/mac-engineer/SESSION_STATE_V1.json"
EVIDENCE_ROOT = Path.home() / "Enguru/Evidence/MacEngineer/v0.8/gate12-pre005"


class EvidenceHold(RuntimeError):
    """A source Gate or its field Evidence cannot support machine verification."""


def _source(gates: dict[str, Any], number: int) -> tuple[str, Path]:
    key = f"gate{number}Closure" if number in (8, 9, 10) else f"gate{number}"
    gate = gates.get(key)
    if not isinstance(gate, dict) or gate.get("state") not in ({"PASS"} if number <= 7 else {"VERIFIED_PASS", "VERIFIED_LOCKED"}):
        raise EvidenceHold(f"GATE{number}_STRUCTURED_STATE_NOT_VERIFIED")
    if number in (2, 3, 4):
        root = Path(gate["evidenceRoot"]).expanduser().resolve()
        paths = list(root.rglob("evidence.json")) if root.is_dir() else []
        if len(paths) != 1:
            raise EvidenceHold(f"GATE{number}_SOURCE_AMBIGUOUS_OR_MISSING")
        path = paths[0]
    else:
        raw = gate.get("evidence") or gate.get("closureEvidence")
        if not isinstance(raw, str) or not raw:
            raise EvidenceHold(f"GATE{number}_SOURCE_MISSING")
        path = Path(raw).expanduser().resolve()
    if not path.is_file():
        raise EvidenceHold(f"GATE{number}_SOURCE_MISSING")
    try:
        source = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        raise EvidenceHold(f"GATE{number}_SOURCE_INVALID") from exc
    if not isinstance(source, dict) or source.get("state") != "PASS":
        raise EvidenceHold(f"GATE{number}_SOURCE_NOT_PASS")
    if number <= 7 and source.get("gate") != f"V08-{number:02d}":
        raise EvidenceHold(f"GATE{number}_SOURCE_GATE_MISMATCH")
    if number in (8, 9, 10) and source.get("gate") != number:
        raise EvidenceHold(f"GATE{number}_SOURCE_GATE_MISMATCH")
    if number == 11 and source.get("gate11State") != "VERIFIED_LOCKED":
        raise EvidenceHold("GATE11_SOURCE_CLOSURE_MISMATCH")
    return key, path


def source_records(session: dict[str, Any]) -> list[dict[str, str]]:
    gates = (session.get("currentV08") or {})
    if (gates.get("gate12") or {}).get("executionStarted") is not False:
        raise EvidenceHold("GATE12_EXECUTION_STATE_CONFLICT")
    records = []
    for number in range(1, 12):
        key, path = _source(gates, number)
        records.append({"gate": f"gate{number}", "stateKey": key, "path": str(path), "digest": file_digest(path)})
    return records


def verify_source_lineage(manifest: dict[str, Any], session: dict[str, Any]) -> None:
    expected = source_records(session)
    files = manifest.get("evidenceFiles")
    if not isinstance(files, list) or len(files) != 11:
        raise EvidenceHold("GATE_SOURCE_LINEAGE_INCOMPLETE")
    for number, item in enumerate(files, 1):
        if not isinstance(item, dict) or {
            "gate": item.get("sourceGate"), "stateKey": item.get("sourceStateKey"),
            "path": item.get("sourcePath"), "digest": item.get("sourceDigest"),
        } != expected[number - 1]:
            raise EvidenceHold(f"GATE{number}_SOURCE_LINEAGE_MISMATCH")


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def prepare(*, session_path: Path = SESSION, output_root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    session = json.loads(session_path.read_text(encoding="utf-8"))
    records = source_records(session)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    task_id = "v08-gate12"
    output_root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".gate12-pre005-", dir=output_root))
    final = output_root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:12])
    try:
        criteria, evidence, files = [], [], []
        for number, source in enumerate(records, 1):
            gate = source["gate"]
            evidence_id = f"evidence-{gate}"
            content = f"[DONECHECK:PASS] {gate} VERIFIED source={source['path']} digest={source['digest']}\n"
            log = stage / f"{gate}.log"
            log.write_text(content, encoding="utf-8")
            log_digest = file_digest(log)
            criteria.append({"id": gate, "taskId": task_id, "statement": f"{gate} verified field closure", "verificationInstruction": "Verify exact governed Gate source and digest", "kind": "objective", "required": True})
            evidence.append({"id": evidence_id, "taskId": task_id, "criterionId": gate, "kind": "test_report", "source": "system", "content": content, "collectedAt": now, "provenance": {"schema": "donecheck.evidence-provenance/v1", "producerKind": "mac_engineer", "producerId": "enguru.mac-engineer", "executionId": f"gate12-{now}-{gate}", "artifactDigest": log_digest, "observedAt": now, "verificationRef": source["digest"]}})
            files.append({"evidenceId": evidence_id, "path": str(final / log.name), "digest": log_digest, "sourceGate": gate, "sourceStateKey": source["stateKey"], "sourcePath": source["path"], "sourceDigest": source["digest"]})
        verification_input = {"task": {"id": task_id, "title": "v0.8 Gate 12", "requestText": "Verify Gates 1–11 from exact field Evidence", "status": "awaiting_review", "createdAt": now}, "criteria": criteria, "aiOutput": "Gates 1–11 field sources reconciled", "evidence": evidence, "resultId": f"v08-gate12-{now}", "verifiedAt": now, "policy": {"requireEvidenceProvenance": True, "trustedProducerIds": ["enguru.mac-engineer"]}}
        manifest = {"verificationInput": verification_input, "evidenceFiles": files}
        verify_source_lineage(manifest, session)
        result = reproduce_verification_result(verification_input)
        if result.get("outcome") != "pass" or len(result.get("criteria", [])) != 11:
            raise EvidenceHold("DONECHECK_GATE12_MACHINE_NOT_PASS")
        _write(stage / "evidence-manifest.json", manifest)
        _write(stage / "verification-result.json", result)
        os.replace(stage, final)
        return {"state": "PASS", "sourceCount": 11, "machineOutcome": result["outcome"], "evidenceManifest": str(final / "evidence-manifest.json"), "verificationResult": str(final / "verification-result.json")}
    finally:
        if stage.exists():
            shutil.rmtree(stage)


if __name__ == "__main__":
    try:
        print(json.dumps(prepare(), ensure_ascii=False))
    except (EvidenceHold, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)
