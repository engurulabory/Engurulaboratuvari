#!/usr/bin/env python3
"""Crash-durable, fail-closed publication primitive for Gate12 PRE-005.

The publisher is deliberately generic: it publishes caller-supplied bytes and
does not create reviewer decisions, Verified Finish receipts or canonical locks.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import uuid
from typing import Callable, Any


class PublicationHold(RuntimeError):
    """Publication or recovery evidence is incomplete or conflicting."""


FaultInjector = Callable[[str], None]


@dataclass(frozen=True)
class PublicationResult:
    state: str
    destination: str
    digest: str
    idempotent: bool


def sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .encode("utf-8")
        + b"\n"
    )


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(str(directory), flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_fsync(path: Path, payload: bytes) -> None:
    with path.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


class CrashDurablePublisher:
    """Publish one immutable byte payload with explicit recovery evidence."""

    MARKER_SUFFIX = ".enguru-publication.json"

    def __init__(self, fault_injector: FaultInjector | None = None) -> None:
        self._fault = fault_injector or (lambda _stage: None)

    @classmethod
    def marker_path(cls, destination: Path) -> Path:
        return destination.with_name(destination.name + cls.MARKER_SUFFIX)

    @classmethod
    def staging_paths(cls, destination: Path) -> list[Path]:
        return sorted(destination.parent.glob(f".{destination.name}.staging-*"))

    @classmethod
    def _read_marker(cls, marker: Path) -> dict[str, Any]:
        try:
            value = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PublicationHold("PUBLICATION_MARKER_CORRUPT") from exc
        if (
            not isinstance(value, dict)
            or set(value) != {"schema", "digest", "byteLength"}
            or value.get("schema") != "enguru.mac-engineer.publication/v1"
            or not isinstance(value.get("digest"), str)
            or not isinstance(value.get("byteLength"), int)
        ):
            raise PublicationHold("PUBLICATION_MARKER_INVALID")
        return value

    @classmethod
    def _existing_result(
        cls, destination: Path, payload: bytes
    ) -> PublicationResult | None:
        marker = cls.marker_path(destination)
        if not destination.exists() and not marker.exists():
            return None
        if not destination.is_file() or not marker.is_file():
            raise PublicationHold("PUBLICATION_AMBIGUOUS_RECOVERY_STATE")
        observed = destination.read_bytes()
        metadata = cls._read_marker(marker)
        digest = sha256_bytes(payload)
        if (
            observed != payload
            or metadata["digest"] != digest
            or metadata["byteLength"] != len(payload)
        ):
            raise PublicationHold("PUBLICATION_DESTINATION_CONFLICT")
        return PublicationResult("PASS", str(destination), digest, True)

    def publish_bytes(
        self,
        destination: Path,
        payload: bytes,
        *,
        allow_replace: bool = False,
    ) -> PublicationResult:
        destination = destination.resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        digest = sha256_bytes(payload)
        try:
            existing = self._existing_result(destination, payload)
        except PublicationHold as exc:
            if not allow_replace or str(exc) != "PUBLICATION_DESTINATION_CONFLICT":
                raise
            existing = None
        if existing is not None:
            return existing
        if self.staging_paths(destination):
            raise PublicationHold("PUBLICATION_INCOMPLETE_STAGING_PRESENT")
        if (destination.exists() or self.marker_path(destination).exists()) and not allow_replace:
            raise PublicationHold("PUBLICATION_DESTINATION_CONFLICT")

        staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4().hex}"
        staged_payload = staging / "payload"
        staged_marker = staging / "marker"
        marker = self.marker_path(destination)
        staging.mkdir()
        try:
            _write_fsync(staged_payload, payload)
            self._fault("after_staged_file_fsync")
            _fsync_directory(staging)
            self._fault("after_staging_directory_fsync")
            os.replace(staged_payload, destination)
            self._fault("after_rename_before_parent_directory_fsync")
            _fsync_directory(destination.parent)
            self._fault("after_parent_directory_fsync")
            marker_payload = canonical_json_bytes(
                {
                    "schema": "enguru.mac-engineer.publication/v1",
                    "digest": digest,
                    "byteLength": len(payload),
                }
            )
            _write_fsync(staged_marker, marker_payload)
            os.replace(staged_marker, marker)
            _fsync_directory(destination.parent)
            self._fault("before_readback")
            if destination.read_bytes() != payload:
                raise PublicationHold("PUBLICATION_READBACK_MISMATCH")
            metadata = self._read_marker(marker)
            if metadata["digest"] != digest or metadata["byteLength"] != len(payload):
                raise PublicationHold("PUBLICATION_MARKER_MISMATCH")
            staging.rmdir()
            _fsync_directory(destination.parent)
            return PublicationResult("PASS", str(destination), digest, False)
        except PublicationHold:
            raise
        except Exception as exc:
            raise PublicationHold(f"PUBLICATION_IO_FAILURE:{type(exc).__name__}") from exc

    def publish_json(
        self,
        destination: Path,
        value: Any,
        *,
        allow_replace: bool = False,
    ) -> PublicationResult:
        return self.publish_bytes(
            destination,
            canonical_json_bytes(value),
            allow_replace=allow_replace,
        )


__all__ = [
    "CrashDurablePublisher",
    "PublicationHold",
    "PublicationResult",
    "canonical_json_bytes",
    "sha256_bytes",
]
