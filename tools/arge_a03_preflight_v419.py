"""A03 preflight evidence gate. Review-only; never issues authorization or receipts."""
from __future__ import annotations
import re
from typing import Mapping, Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
GATES = ("trust_anchor_verified", "task_grant_verified", "reviewer_independent_verified", "source_pinned_verified", "donecheck_authorized_verified")

def assess_a03(record: Mapping[str, Any]) -> dict[str, Any]:
    """A recorded boolean is never sufficient proof of a real grant.

    This gate checks that every assertion has an independent evidence reference.
    Upstream authorized verifier must have checked the referenced sources.
    """
    blockers = []
    if record.get("task_id") != "A03":
        blockers.append("TASK_SCOPE")
    if not SHA1.fullmatch(str(record.get("source_commit", ""))):
        blockers.append("SOURCE_COMMIT_FORMAT")
    if not SHA256.fullmatch(str(record.get("artifact_sha256", ""))):
        blockers.append("ARTIFACT_DIGEST_FORMAT")
    for gate in GATES:
        value = record.get(gate)
        reference = record.get(gate + "_evidence_ref")
        if value is not True or not isinstance(reference, str) or not reference.strip():
            blockers.append(gate.upper())
    if record.get("reviewer_id") and record.get("producer_id") and record["reviewer_id"] == record["producer_id"]:
        blockers.append("REVIEWER_NOT_INDEPENDENT")
    # Conservative advisory only; task grant and signature must be checked externally.
    return {"state": "EVIDENCE_REFERENCES_READY_FOR_INDEPENDENT_VERIFICATION" if not blockers else "HOLD",
            "blockers": blockers, "official_acceptance": False, "verified_finish": False}
