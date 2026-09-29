#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mac_engineer_donecheck_v12_bridge as bridge
import mac_engineer_governed_finish_guard as finish_guard


PRODUCER_ID = "enguru.mac-engineer"


def now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(value, dict):
        raise ValueError(
            "JSON_OBJECT_REQUIRED"
        )

    return value


def build_donecheck_input(
    *,
    evidence_path: Path,
    execution_id: str,
    task_id: str,
    criterion_id: str,
    statement: str,
) -> dict[str, Any]:

    evidence = load(evidence_path)

    if evidence.get("state") != "PASS":
        raise ValueError(
            "SOURCE_EVIDENCE_PASS_REQUIRED"
        )

    observed_at = now()

    digest = (
        "sha256:"
        + sha256(evidence_path)
    )

    task = {
        "id": task_id,
        "title":
            "ENGÜRÜ Package 07 governed finish verification",
        "requestText":
            "Verify the supplied orchestration Evidence through pinned DoneCheck v1.2.",
        "status": "awaiting_review",
        "createdAt": observed_at,
    }

    criteria = [
        {
            "id": criterion_id,
            "taskId": task_id,
            "statement": statement,
            "verificationInstruction":
                "Consume trusted criterion-scoped Mac Engineer Evidence.",
            "kind": "objective",
            "required": True,
        }
    ]

    producer_evidence = [
        {
            "id":
                "evidence-" + criterion_id,
            "taskId":
                task_id,
            "criterionId":
                criterion_id,
            "kind":
                "test_report",
            "source":
                "system",
            "content":
                "[DONECHECK:PASS] "
                + statement
                + " Evidence state is PASS.",
            "collectedAt":
                observed_at,
            "provenance": {
                "schema":
                    "donecheck.evidence-provenance/v1",
                "producerKind":
                    "mac_engineer",
                "producerId":
                    PRODUCER_ID,
                "executionId":
                    execution_id,
                "artifactDigest":
                    digest,
                "observedAt":
                    observed_at,
                "verificationRef":
                    str(evidence_path),
            },
        }
    ]

    return {
        "task":
            task,
        "criteria":
            criteria,
        "aiOutput":
            "ENGÜRÜ Mac Engineer supplied fresh criterion-scoped Evidence.",
        "evidence":
            producer_evidence,
        "resultId":
            "verification-" + execution_id[:24],
        "verifiedAt":
            observed_at,
        "policy": {
            "requireEvidenceProvenance":
                True,
            "trustedProducerIds": [
                PRODUCER_ID
            ],
        },
    }


def verify_machine_finish(
    *,
    evidence_path: Path,
    execution_id: str,
    task_id: str,
    criterion_id: str,
    statement: str,
) -> dict[str, Any]:

    payload = build_donecheck_input(
        evidence_path=evidence_path,
        execution_id=execution_id,
        task_id=task_id,
        criterion_id=criterion_id,
        statement=statement,
    )

    result = (
        bridge.reproduce_verification_result(
            payload
        )
    )

    criteria = result.get(
        "criteria"
    ) or []

    criterion_pass = (
        len(criteria) == 1
        and criteria[0].get("outcome")
        == "pass"
    )

    aggregate = (
        result.get("aggregateOutcome")
        or result.get("outcome")
    )

    donecheck_pass = (
        criterion_pass
        and aggregate == "pass"
    )

    return {
        "STATE":
            "PASS"
            if donecheck_pass
            else "HOLD",

        "DONECHECK_STATE":
            "PASS"
            if donecheck_pass
            else "HOLD",

        "DONECHECK_VERSION":
            bridge.DONECHECK_VERSION,

        "DONECHECK_SHA":
            bridge.DONECHECK_SHA,

        "EXECUTION_ID":
            execution_id,

        "TASK_ID":
            task_id,

        "VERIFICATION_RESULT_ID":
            result.get("id")
            or result.get("resultId"),

        "RAW_RESULT":
            result,
    }


def evaluate_green_finish(
    machine: dict[str, Any],
) -> dict[str, Any]:

    return finish_guard.evaluate_finish(
        material_evidence_present=True,
        fresh_verification=True,
        cached_pass_used=False,
        donecheck_state=
            machine["DONECHECK_STATE"],
        ht_required=False,
        human_decision=None,
        execution_identity_bound=True,
        donecheck_identity_bound=True,
        supported_final_claim=True,
    )


def evaluate_ht_missing(
    machine: dict[str, Any],
) -> dict[str, Any]:

    return finish_guard.evaluate_finish(
        material_evidence_present=True,
        fresh_verification=True,
        cached_pass_used=False,
        donecheck_state=
            machine["DONECHECK_STATE"],
        ht_required=True,
        human_decision=None,
        execution_identity_bound=False,
        donecheck_identity_bound=False,
        supported_final_claim=True,
    )


def verify_existing_signed_ht_bundle(
    candidate_dir: Path,
) -> dict[str, Any]:

    try:
        import mac_engineer_v08_gate12_reviewer_authority as reviewer
    except ModuleNotFoundError:
        from tools import mac_engineer_v08_gate12_reviewer_authority as reviewer

    review_path = (
        candidate_dir
        / "human-review.json"
    )

    attestation_path = (
        candidate_dir
        / "human-review-attestation.json"
    )

    receipt_path = (
        candidate_dir
        / "verified-finish-receipt.json"
    )

    audit_path = (
        candidate_dir
        / "audit-ledger.jsonl"
    )

    envelope_path = (
        candidate_dir
        / "human-threshold-envelope.json"
    )

    bundle_path = (
        candidate_dir
        / "candidate-bundle.json"
    )

    required = [
        review_path,
        attestation_path,
        receipt_path,
        audit_path,
        envelope_path,
        bundle_path,
    ]

    missing = [
        str(p)
        for p in required
        if not p.is_file()
    ]

    if missing:
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "SIGNED_HT_ARTIFACT_MISSING",
            "MISSING": missing,
        }

    authority_path = (
        reviewer.EXPECTED_AUTHORITY_ARTIFACT
    )

    authority = reviewer.load_authority(
        authority_path
    )

    attestation = load(
        attestation_path
    )

    observed_at = str(
        attestation.get("signedAt") or ""
    )

    authority_result = (
        reviewer.verify_authority(
            authority,
            observed_at=observed_at,
            production_use=False,
        )
    )

    if (
        authority_result.get("state")
        != "PASS"
    ):
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "REVIEWER_AUTHORITY_HOLD",
            "AUTHORITY_RESULT":
                authority_result,
        }

    review_result = (
        bridge.verify_human_review_and_verified_finish(
            review_path=review_path,
            attestation_path=attestation_path,
            receipt_path=receipt_path,
            audit_path=audit_path,
            authority=authority,
        )
    )

    if (
        review_result.get("state")
        != "PASS"
    ):
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "SIGNED_HUMAN_REVIEW_OR_VERIFIED_FINISH_HOLD",
            "REVIEW_RESULT":
                review_result,
        }

    bundle = load(bundle_path)
    envelope = load(envelope_path)
    receipt = load(receipt_path)
    review = load(review_path)

    receipt_digest = (
        "sha256:"
        + sha256(receipt_path)
    )

    if (
        receipt_digest
        != bundle["chain"][
            "verifiedFinishReceiptDigest"
        ]
    ):
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "VERIFIED_FINISH_DIGEST_MISMATCH",
        }

    if (
        review_result.get("auditHead")
        != bundle["chain"]["auditHead"]
    ):
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "AUDIT_HEAD_BINDING_MISMATCH",
        }

    payload = envelope.get(
        "payload"
    ) or {}

    if payload.get("decision") != "ACCEPT":
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "SIGNED_ACCEPT_REQUIRED",
        }

    expected = {
        "controlHead":
            bundle["control"]["head"],

        "productHead":
            bundle["product"]["head"],

        "doneCheckVersion":
            bundle["doneCheck"]["version"],

        "doneCheckSha":
            bundle["doneCheck"]["exactSha"],

        **bundle["chain"],

        "targetVersion":
            bundle["target"]["targetVersion"],

        "intendedExit":
            bundle["target"]["intendedExit"],
    }

    threshold = (
        reviewer.verify_threshold_envelope_json(
            authority_path.read_text(
                encoding="utf-8"
            ),
            envelope_path.read_text(
                encoding="utf-8"
            ),
            expected=expected,
            observed_at=str(
                payload.get("decidedAt")
                or observed_at
            ),
            production_use=False,
        )
    )

    if (
        threshold.get("state")
        != "PASS"
    ):
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "SIGNED_THRESHOLD_VERIFY_HOLD",
            "THRESHOLD_RESULT":
                threshold,
        }

    if (
        threshold.get("decisionId")
        != payload.get("decisionId")
    ):
        return {
            "STATE": "HOLD",
            "HOLD_REASON":
                "DECISION_ID_MISMATCH",
        }

    return {
        "STATE": "PASS",

        "DECISION": "ACCEPT",

        "TASK_ID":
            review["taskId"],

        "VERIFICATION_RESULT_ID":
            review["verificationResultId"],

        "REVIEWER_ID":
            review["reviewerId"],

        "FINISH_ID":
            receipt["finishId"],

        "AUDIT_HEAD":
            review_result["auditHead"],

        "DECISION_ID":
            threshold["decisionId"],

        "TERMINAL_CANDIDATE_ID":
            bundle["terminalCandidateId"],

        "DONECHECK_VERSION":
            bundle["doneCheck"]["version"],

        "DONECHECK_SHA":
            bundle["doneCheck"]["exactSha"],

        "SIGNED_REVIEW_VALID":
            True,

        "VERIFIED_FINISH_VALID":
            True,

        "SIGNED_THRESHOLD_VALID":
            True,
    }


def evaluate_signed_ht_finish(
    *,
    signed_ht: dict[str, Any],
    expected_task_id: str,
    expected_verification_result_id: str,
) -> dict[str, Any]:

    signed_pass = (
        signed_ht.get("STATE")
        == "PASS"
    )

    task_bound = (
        signed_pass
        and signed_ht.get("TASK_ID")
        == expected_task_id
    )

    result_bound = (
        signed_pass
        and signed_ht.get(
            "VERIFICATION_RESULT_ID"
        )
        == expected_verification_result_id
    )

    return finish_guard.evaluate_finish(
        material_evidence_present=True,
        fresh_verification=True,
        cached_pass_used=False,
        donecheck_state=
            "PASS"
            if signed_pass
            else "HOLD",
        ht_required=True,
        human_decision=
            signed_ht.get("DECISION"),
        execution_identity_bound=
            task_bound,
        donecheck_identity_bound=
            result_bound,
        supported_final_claim=True,
    )
