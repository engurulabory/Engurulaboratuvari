"""Completion fallacy guard: local proof candidates; never issues authority."""
from __future__ import annotations
import json
from pathlib import Path
from proof_chain import _bytes_pin, _digest


def hold(*reasons, **details):
    return {'state': 'COMPLETION_HOLD', 'missing': sorted(set(reasons)),
            'acceptedScore': None, 'stagePassIssued': False,
            'verifiedFinishIssued': False, **details}


def audit_completion_claim(workspace: Path, contract, claim: dict | None,
                           independent_session_verifier=None) -> dict:
    """Every original criterion needs a pinned, different-session review.

    An external callback is a handoff boundary, not authentication by this code.
    Even a complete local review is a candidate rather than owner acceptance.
    """
    contract.validate()
    expected = set(contract.criteria)
    if not isinstance(claim, dict):
        return hold('FRESH_CROSS_SESSION_REVIEW_REQUIRED')
    missing = []
    if claim.get('goalId') != contract.goal_id or claim.get('stage') != contract.stage:
        missing.append('GOAL_OR_GATE_DRIFT')
    if claim.get('sourceSha256') != contract.source_pin:
        missing.append('SOURCE_PIN_DRIFT')
    # The source pin must match current bytes, not merely its echoed claim.
    try:
        live_source_sha, _, _ = _bytes_pin(workspace, claim.get('sourcePath'))
    except (OSError, ValueError, TypeError):
        missing.append('ORIGINAL_GOAL_SOURCE_UNREADABLE_OR_UNSAFE')
    else:
        if live_source_sha != contract.source_pin:
            missing.append('ORIGINAL_GOAL_SOURCE_CHANGED')
    producer, reviewer = claim.get('executorSessionId'), claim.get('reviewerSessionId')
    executor_id, reviewer_id = claim.get('executorId'), claim.get('reviewerId')
    if (not all(isinstance(x, str) and x.strip() for x in (producer, reviewer, executor_id, reviewer_id))
        or producer == reviewer or executor_id == reviewer_id):
        missing.append('INDEPENDENT_SESSION_IDENTITY_REQUIRED')
    covered = claim.get('claimedCriteria')
    if (not isinstance(covered, list) or not covered or
        not all(isinstance(x,str) for x in covered) or
        len(covered) != len(set(covered)) or set(covered) != expected):
        missing.append('ORIGINAL_CRITERIA_COVERAGE')
    opened = claim.get('openItems')
    if not isinstance(opened, list):
        missing.append('OPEN_ITEM_LEDGER_REQUIRED')
    elif opened:
        missing.append('OPEN_ITEMS_REMAIN')
    if claim.get('selfReportedScore') != 100:
        missing.append('SELF_SCORE_NOT_COMPLETE')
    if not _digest(claim.get('resultSha256')) or not _digest(claim.get('reviewSha256')):
        missing.append('RESULT_OR_REVIEW_PIN_REQUIRED')
    if not _digest(claim.get('checkpointSha256')) or not isinstance(claim.get('executionRunId'), str) or not claim['executionRunId'].strip():
        missing.append('LATEST_CHECKPOINT_ID_REQUIRED')
    if missing:
        return hold(*missing, originalCriteria=len(expected))
    try:
        observed, _, _ = _bytes_pin(workspace, claim.get('resultPath'))
        review_hash, _, review_bytes = _bytes_pin(workspace, claim.get('reviewPath'))
        checkpoint_hash, _, checkpoint_bytes = _bytes_pin(workspace, claim.get('checkpointPath'))
    except (OSError, ValueError, TypeError):
        return hold('OUTPUT_OR_REVIEW_UNREADABLE_OR_UNSAFE')
    if observed != claim['resultSha256'] or review_hash != claim['reviewSha256'] or checkpoint_hash != claim['checkpointSha256']:
        return hold('ACTUAL_ARTIFACT_SHA_MISMATCH')
    if len({observed, review_hash, checkpoint_hash}) != 3:
        return hold('REVIEW_OR_CHECKPOINT_DUPLICATE_BYTES')
    try:
        checkpoint = json.loads(checkpoint_bytes)
    except (ValueError, UnicodeError):
        return hold('CHECKPOINT_NOT_JSON')
    if (not isinstance(checkpoint, dict) or
        checkpoint.get('goalId') != contract.goal_id or
        checkpoint.get('stage') != contract.stage or
        checkpoint.get('executionRunId') != claim.get('executionRunId') or
        checkpoint.get('resultSha256') != observed):
        return hold('LATEST_CHECKPOINT_IDENTITY_DRIFT')
    try:
        review_doc = json.loads(review_bytes)
    except (ValueError, UnicodeError):
        return hold('REVIEW_NOT_JSON')
    if not isinstance(review_doc, dict) or any(review_doc.get(k) != claim.get(k) for k in
        ('goalId','stage','sourceSha256','executorSessionId','reviewerSessionId',
         'executorId','reviewerId','resultSha256','checkpointSha256','executionRunId')):
        return hold('INDEPENDENT_REVIEW_IDENTITY_DRIFT')
    outcomes = review_doc.get('criterionOutcomes')
    if (not isinstance(outcomes, dict) or set(outcomes) != expected or
        any(type(x) is not bool for x in outcomes.values())):
        return hold('REVIEW_CRITERIA_INCOMPLETE', originalCriteria=len(expected))
    if review_doc.get('unresolvedItems') != []:
        return hold('REVIEW_UNRESOLVED_ITEMS')
    regression = review_doc.get('regressionChecked')
    if (not isinstance(regression, list) or len(regression) != len(set(regression))
        or set(regression) != expected):
        return hold('REGRESSION_NOT_ALL_CRITERIA')
    negative = review_doc.get('negativeCasesCaught')
    if (not isinstance(negative, list) or not negative or
        not all(isinstance(x,str) and x.strip() for x in negative)):
        return hold('ADVERSARIAL_NEGATIVE_CONTROL_MISSING')
    failed = sorted(k for k,v in outcomes.items() if v is not True)
    if failed:
        return hold('CROSS_SESSION_REVIEW_FOUND_GAPS', failedCriteria=failed,
                    originalCriteria=len(expected))
    if not callable(independent_session_verifier):
        return hold('EXTERNAL_SESSION_VERIFIER_REQUIRED')
    try:
        checked = independent_session_verifier(contract, claim, review_doc)
    except Exception:
        checked = False
    if checked is not True:
        return hold('INDEPENDENT_SESSION_NOT_AUTHENTICATED')
    # Callback may be slow or mutating: re-pin source, output and peer proof
    # AFTER the external reviewer check. A stale review never becomes a candidate.
    try:
        live_sources = (
            _bytes_pin(workspace, claim.get('sourcePath'))[0],
            _bytes_pin(workspace, claim.get('resultPath'))[0],
            _bytes_pin(workspace, claim.get('reviewPath'))[0],
            _bytes_pin(workspace, claim.get('checkpointPath'))[0],
        )
    except (OSError, ValueError, TypeError):
        return hold('SOURCE_OR_RESULT_CHANGED_DURING_EXTERNAL_REVIEW')
    if live_sources != (contract.source_pin, observed, review_hash, checkpoint_hash):
        return hold('SOURCE_OR_RESULT_CHANGED_DURING_EXTERNAL_REVIEW')
    return {'state':'CROSS_SESSION_LOCAL_COMPLETENESS_CANDIDATE',
            'originalCriteria':len(expected), 'reviewedCriteria':len(outcomes),
            'negativeControls':len(negative), 'resultSha256':observed,
            'reviewSha256':review_hash,'acceptedScore':None,
            'stagePassIssued':False,'verifiedFinishIssued':False,
            'warning':'Local candidate only; existing external reviewer and owner DoneCheck still required.'}
