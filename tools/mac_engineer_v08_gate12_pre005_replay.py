#!/usr/bin/env python3
"""Persistent replay adapter for the existing Gate12 replay semantics."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any

try:
    from tools.mac_engineer_v08_gate12_pre005_publisher import (
        CrashDurablePublisher,
        PublicationHold,
    )
except ImportError:  # pragma: no cover
    from mac_engineer_v08_gate12_pre005_publisher import (
        CrashDurablePublisher,
        PublicationHold,
    )


SCHEMA = "enguru.mac-engineer.v08-gate12-replay/v1"
RECORD_KEYS = {
    "decisionId",
    "terminalCandidateId",
    "payloadDigest",
    "envelopeDigest",
    "decision",
}
ROOT_KEYS = {"schema", "records"}
SHA256 = re.compile(r"^sha256:[a-f0-9]{64}$")
DECISION_ID = re.compile(r"^g12-ht-sha256:[a-f0-9]{64}$")
CANDIDATE_ID = re.compile(r"^g12-candidate-sha256:[a-f0-9]{64}$")


class ReplayStoreHold(RuntimeError):
    """The durable replay state is corrupt, conflicting or ambiguous."""


def _strict_load(text: str) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ReplayStoreHold(f"REPLAY_DUPLICATE_JSON_KEY:{key}")
            result[key] = value
        return result

    try:
        return json.loads(text, object_pairs_hook=pairs)
    except ReplayStoreHold:
        raise
    except (OSError, json.JSONDecodeError) as exc:
        raise ReplayStoreHold("REPLAY_REGISTRY_CORRUPT") from exc


def _validate_record(value: Any) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != RECORD_KEYS:
        raise ReplayStoreHold("REPLAY_RECORD_INVALID")
    if not isinstance(value["decisionId"], str) or not DECISION_ID.fullmatch(value["decisionId"]):
        raise ReplayStoreHold("REPLAY_DECISION_ID_INVALID")
    if not isinstance(value["terminalCandidateId"], str) or not CANDIDATE_ID.fullmatch(value["terminalCandidateId"]):
        raise ReplayStoreHold("REPLAY_TERMINAL_CANDIDATE_ID_INVALID")
    for key in ("payloadDigest", "envelopeDigest"):
        if not isinstance(value[key], str) or not SHA256.fullmatch(value[key]):
            raise ReplayStoreHold(f"REPLAY_{key.upper()}_INVALID")
    if value["decision"] not in {"ACCEPT", "HOLD"}:
        raise ReplayStoreHold("REPLAY_DECISION_INVALID")
    return {key: value[key] for key in RECORD_KEYS}


class PersistentReplayAuthority:
    """File-backed implementation of DurableReplayAuthority.

    Reads happen from disk on every lookup; production callers cannot silently
    fall back to an in-memory registry after restart.
    """

    durable = True

    def __init__(
        self,
        path: Path,
        *,
        publisher: CrashDurablePublisher | None = None,
    ) -> None:
        self.path = path.resolve()
        self.publisher = publisher or CrashDurablePublisher()

    def _load(self) -> list[dict[str, str]]:
        staging = CrashDurablePublisher.staging_paths(self.path)
        if not self.path.exists():
            if staging:
                raise ReplayStoreHold("REPLAY_INCOMPLETE_STAGING_PRESENT")
            return []
        try:
            root = _strict_load(self.path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise ReplayStoreHold("REPLAY_REGISTRY_UNREADABLE") from exc
        if not isinstance(root, dict) or set(root) != ROOT_KEYS or root.get("schema") != SCHEMA:
            raise ReplayStoreHold("REPLAY_REGISTRY_ROOT_INVALID")
        records = root.get("records")
        if not isinstance(records, list):
            raise ReplayStoreHold("REPLAY_RECORDS_LIST_REQUIRED")
        validated = [_validate_record(item) for item in records]
        by_decision: dict[str, dict[str, str]] = {}
        by_candidate: dict[str, dict[str, str]] = {}
        for record in validated:
            prior_decision = by_decision.get(record["decisionId"])
            prior_candidate = by_candidate.get(record["terminalCandidateId"])
            if prior_decision is not None and prior_decision != record:
                raise ReplayStoreHold("REPLAY_DUPLICATE_DECISION_CONFLICT")
            if prior_decision is not None:
                raise ReplayStoreHold("REPLAY_DUPLICATE_DECISION_RECORD")
            if prior_candidate is not None and prior_candidate != record:
                raise ReplayStoreHold("REPLAY_DUPLICATE_CANDIDATE_CONFLICT")
            by_decision[record["decisionId"]] = record
            by_candidate[record["terminalCandidateId"]] = record
        return validated

    def get_decision(self, decision_id: str) -> dict[str, str] | None:
        return next((r for r in self._load() if r["decisionId"] == decision_id), None)

    def get_terminal_candidate(self, terminal_candidate_id: str) -> dict[str, str] | None:
        return next(
            (r for r in self._load() if r["terminalCandidateId"] == terminal_candidate_id),
            None,
        )

    def remember(self, record: dict[str, str]) -> str:
        candidate = _validate_record(record)
        records = self._load()
        for prior in records:
            if prior["decisionId"] == candidate["decisionId"]:
                if prior == candidate:
                    return "IDEMPOTENT"
                raise ReplayStoreHold("REPLAY_ID_CONTENT_CONFLICT")
            if prior["terminalCandidateId"] == candidate["terminalCandidateId"]:
                if prior == candidate:
                    return "IDEMPOTENT"
                if prior["decision"] == "ACCEPT":
                    raise ReplayStoreHold("TERMINAL_CANDIDATE_ALREADY_ACCEPTED")
                raise ReplayStoreHold("REPLAY_CANDIDATE_CONTENT_CONFLICT")
        root = {"schema": SCHEMA, "records": [*records, deepcopy(candidate)]}
        try:
            self.publisher.publish_json(self.path, root, allow_replace=bool(records))
        except PublicationHold as exc:
            raise ReplayStoreHold(str(exc)) from exc
        return "NEW"


__all__ = ["PersistentReplayAuthority", "ReplayStoreHold", "SCHEMA"]
