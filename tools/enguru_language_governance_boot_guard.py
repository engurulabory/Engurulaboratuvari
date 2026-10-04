#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

AUTHORITY_PATHS = [
    ROOT / "governance" / "ENGURU_LANGUAGE_GOVERNANCE_V1.md",
    ROOT / "governance" / "chatgpt"
    / "ENGURU_LANGUAGE_GOVERNANCE_CHATGPT_MASTER_INSTRUCTION_V1.md",
    ROOT / "governance" / "chatgpt"
    / "ENGURU_LANGUAGE_GOVERNANCE_CONTRACT_V1.json",
    ROOT / "governance" / "chatgpt"
    / "ENGURU_LANGUAGE_GOVERNANCE_AUTHORITY_PRECEDENCE_V1.json",
    ROOT / "governance" / "chatgpt"
    / "ENGURU_LANGUAGE_GOVERNANCE_TRANSFORMATION_CORPUS_V1.md",
    ROOT / "governance" / "chatgpt"
    / "ENGURU_LANGUAGE_GOVERNANCE_PRE_SEND_LINTER_CONTRACT_V1.md",
    ROOT / "governance" / "chatgpt"
    / "ENGURU_CHATGPT_CANONICAL_BOOT_V1.md",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate() -> dict:
    artifacts = []
    missing = []

    for path in AUTHORITY_PATHS:
        rel = path.relative_to(ROOT).as_posix()

        if not path.is_file():
            missing.append(rel)
            continue

        artifacts.append(
            {
                "path": rel,
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
        )

    if missing:
        return {
            "schema": "enguru.suzgeci.boot-guard/v1",
            "state": "HOLD",
            "authority_state": "INCOMPLETE",
            "missing": missing,
            "artifacts": artifacts,
        }

    try:
        contract = json.loads(
            (
                ROOT
                / "governance"
                / "chatgpt"
                / "ENGURU_LANGUAGE_GOVERNANCE_CONTRACT_V1.json"
            ).read_text(encoding="utf-8")
        )

        precedence = json.loads(
            (
                ROOT
                / "governance"
                / "chatgpt"
                / "ENGURU_LANGUAGE_GOVERNANCE_AUTHORITY_PRECEDENCE_V1.json"
            ).read_text(encoding="utf-8")
        )

    except Exception as exc:
        return {
            "schema": "enguru.suzgeci.boot-guard/v1",
            "state": "HOLD",
            "authority_state": "INVALID",
            "error": str(exc),
            "artifacts": artifacts,
        }

    if contract.get("executionStates") != [
        "PASS",
        "HOLD",
        "BLOCKED",
        "FAIL",
    ]:
        return {
            "schema": "enguru.suzgeci.boot-guard/v1",
            "state": "HOLD",
            "authority_state": "SEMANTIC_MISMATCH",
            "reason": "EXECUTION_STATE_CONTRACT_MISMATCH",
            "artifacts": artifacts,
        }

    if (
        contract.get("preferredVocabulary", {}).get("bozmadan")
        != "koruyarak"
    ):
        return {
            "schema": "enguru.suzgeci.boot-guard/v1",
            "state": "HOLD",
            "authority_state": "SEMANTIC_MISMATCH",
            "reason": "PRESERVATION_FIRST_VOCABULARY_MISMATCH",
            "artifacts": artifacts,
        }

    if len(precedence.get("layers", [])) != 10:
        return {
            "schema": "enguru.suzgeci.boot-guard/v1",
            "state": "HOLD",
            "authority_state": "SEMANTIC_MISMATCH",
            "reason": "AUTHORITY_PRECEDENCE_LAYER_MISMATCH",
            "artifacts": artifacts,
        }

    return {
        "schema": "enguru.suzgeci.boot-guard/v1",
        "state": "PASS",
        "authority_state": "PASS",
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }


def main() -> int:
    result = validate()

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0 if result["state"] == "PASS" else 20


if __name__ == "__main__":
    raise SystemExit(main())
