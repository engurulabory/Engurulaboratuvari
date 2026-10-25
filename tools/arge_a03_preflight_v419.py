"""A03 review-only preflight: structural checks with external authority explicitly HOLD.

GitHub/OSi DoneCheck authority, reviewer identity and cryptographic proof must be
verified by the existing canonical verifier, never by this helper's self-assertions.
"""
from __future__ import annotations
import re
from typing import Mapping, Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
PINNED_GITHUB = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/"
    r"(?:blob/[0-9a-f]{40}/[^#?\s]+|commit/[0-9a-f]{40})"
    r"#sha256=[0-9a-f]{64}$"
)
PINNED_LOCAL = re.compile(r"^file:///(?:[^#?\s]+/)??[^#?\s]+#sha256=[0-9a-f]{64}$")
GATES = (
    "trust_anchor_verified", "task_grant_verified",
    "reviewer_independent_verified", "source_pinned_verified",
    "donecheck_authorized_verified",
)


def _plausible_pinned_reference(value: Any) -> bool:
    """Only validate a content-addressed reference *format*, never its truth."""
    return isinstance(value, str) and bool(
        PINNED_GITHUB.fullmatch(value) or PINNED_LOCAL.fullmatch(value)
    )


def assess_a03(record: Mapping[str, Any]) -> dict[str, Any]:
    """Fail closed on untrusted evidence; this helper cannot grant acceptance.

    Even a fully formed self-reported record requires actual independent issuer,
    signer, reviewer, source and evidence verification by existing authorities.
    """
    blockers: list[str] = []
    if not isinstance(record, Mapping):
        record = {}
        blockers.append("INVALID_RECORD")

    if record.get("task_id") != "A03":
        blockers.append("TASK_SCOPE")
    if not isinstance(record.get("source_commit"), str) or not SHA1.fullmatch(record["source_commit"]):
        blockers.append("SOURCE_COMMIT_FORMAT")
    if not isinstance(record.get("artifact_sha256"), str) or not SHA256.fullmatch(record["artifact_sha256"]):
        blockers.append("ARTIFACT_DIGEST_FORMAT")

    producer = record.get("producer_id")
    reviewer = record.get("reviewer_id")
    if not isinstance(producer, str) or not producer.strip():
        blockers.append("PRODUCER_ID_MISSING")
    if not isinstance(reviewer, str) or not reviewer.strip():
        blockers.append("REVIEWER_ID_MISSING")
    if isinstance(producer, str) and isinstance(reviewer, str) and producer.strip() and reviewer.strip() and producer.strip() == reviewer.strip():
        blockers.append("REVIEWER_NOT_INDEPENDENT")

    for gate in GATES:
        if record.get(gate) is not True:
            blockers.append(gate.upper())
        if not _plausible_pinned_reference(record.get(gate + "_evidence_ref")):
            blockers.append(gate.upper() + "_EVIDENCE_REF_INVALID")

    # A self-declared boolean, 40-hex SHA or URL is never proof of real authority.
    format_ok = not blockers
    return {
        "state": "HOLD",
        "structural_preflight": "PASS_FORMAT_ONLY" if format_ok else "HOLD_INVALID_INPUT",
        "blockers": blockers + ["EXTERNAL_AUTHORITY_VERIFICATION_REQUIRED"],
        "official_acceptance": False,
        "verified_finish": False,
    }
