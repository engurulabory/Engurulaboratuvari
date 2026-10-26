"""DÖM V1.0 internal evidence/three-phase/finish discipline, V1.4.1 compatible.

This is a local, fail-closed proof helper. Not an executor, issuer, DoneCheck,
owner authority, or independent external reviewer identity service.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat

SHA_CHARS = set('0123456789abcdef')
PHASES = ('REAL_TASK', 'ADVERSARIAL_RECOVERY', 'REPAIR_RETEST_PROOF')
KINDS = ('SOURCE', 'EXECUTION', 'WORKING_RESULT', 'INDEPENDENT_REVIEW', 'OWNER_ACCEPTANCE', 'DONECHECK')


def _digest(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= SHA_CHARS


def _bytes_pin(workspace: Path, relative: str, max_bytes: int = 2_000_000) -> tuple[str, int]:
    """Read only a regular, unlinked, sandbox-local file. Refuse path indirection."""
    root = Path(workspace).resolve(strict=True)
    if not root.is_dir() or not isinstance(relative, str):
        raise ValueError('UNSAFE_WORKSPACE_OR_PATH')
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or any(p in ('.', '..') for p in rel.parts):
        raise ValueError('UNSAFE_PATH')
    current = root
    for part in rel.parts[:-1]:
        current = current / part
        if current.is_symlink() or not current.is_dir():
            raise ValueError('UNSAFE_DIRECTORY_COMPONENT')
    path = root / rel
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size > max_bytes:
            raise ValueError('UNSAFE_SOURCE')
        bypath = os.stat(path, follow_symlinks=False)
        if (st.st_dev, st.st_ino) != (bypath.st_dev, bypath.st_ino):
            raise ValueError('FILE_CHANGED_DURING_OPEN')
        h = hashlib.sha256()
        chunks = []
        size = 0
        while True:
            chunk = os.read(fd, 64 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                raise ValueError('FILE_TOO_LARGE')
            h.update(chunk)
            chunks.append(chunk)
        return h.hexdigest(), size, b"".join(chunks)
    finally:
        os.close(fd)


def audit_evidence(workspace: Path, criteria: dict, bindings: list[dict], *, goal_id: str) -> dict:
    """Evidence ID count != unique bytes != independent provenance roots.

    criteria: {criterion_id: {kinds: [SOURCE, EXECUTION...], minRoots: integer}}
    Untrusted descriptions, labels and claims alone never count as proof.
    """
    if not isinstance(goal_id, str) or not goal_id.strip() or not isinstance(criteria, dict) or not criteria:
        raise ValueError('BAD_GOAL_OR_CRITERIA')
    if not isinstance(bindings, list):
        raise ValueError('BAD_BINDINGS')
    for key, contract in criteria.items():
        if (not isinstance(key, str) or not key.strip() or not isinstance(contract, dict) or
            not isinstance(contract.get('kinds'), list) or not contract['kinds'] or
            len(contract['kinds']) != len(set(contract['kinds'])) or
            any(kind not in KINDS for kind in contract['kinds']) or
            type(contract.get('minRoots')) is not int or contract['minRoots'] < 1):
            raise ValueError('BAD_REQUIREMENT')
    per_criterion = {key: [] for key in criteria}
    invalid = []
    ids = set()
    for number, evidence in enumerate(bindings):
        if not isinstance(evidence, dict):
            invalid.append({'index': number, 'reason': 'BAD_EVIDENCE'});continue
        ident = evidence.get('evidenceId')
        if not isinstance(ident, str) or not ident.strip() or ident in ids:
            invalid.append({'index': number, 'reason': 'DUPLICATE_OR_BAD_EVIDENCE_ID'});continue
        ids.add(ident)
        if (evidence.get('goalId') != goal_id or evidence.get('criterionId') not in criteria or
            evidence.get('kind') not in KINDS or not isinstance(evidence.get('provenanceRoot'), str) or
            not evidence['provenanceRoot'].strip() or not _digest(evidence.get('contentSha256'))):
            invalid.append({'index': number, 'reason': 'CLAIM_NOT_GROUNDED'});continue
        try:
            observed, length, _ = _bytes_pin(workspace, evidence.get('relativePath'))
        except (OSError, ValueError, TypeError):
            invalid.append({'index': number, 'reason': 'FILE_UNREADABLE_OR_UNSAFE'});continue
        if observed != evidence['contentSha256']:
            invalid.append({'index': number, 'reason': 'CONTENT_SHA_MISMATCH'});continue
        per_criterion[evidence['criterionId']].append({
            'id': ident, 'kind': evidence['kind'], 'root': evidence['provenanceRoot'],
            'digest': observed, 'length': length,
        })
    results = {}
    all_valid = [item for group in per_criterion.values() for item in group]
    for criterion, requirements in criteria.items():
        observed = per_criterion[criterion]
        roots = {x['root'] for x in observed}
        kinds = {x['kind'] for x in observed}
        missing_kinds = sorted(set(requirements['kinds']) - kinds)
        # Same bytes relabelled with fresh provenance ID is not independent.
        distinct_bytes = {x['digest'] for x in observed}
        independent_count = min(len(roots), len(distinct_bytes))
        passed = not missing_kinds and independent_count >= requirements['minRoots']
        results[criterion] = {'met': passed, 'bindings': len(observed),
            'uniqueContent': len(distinct_bytes), 'roots': len(roots),
            'independentSourceUpperBound': independent_count, 'missingKinds': missing_kinds,
            'missingRoots': max(0, requirements['minRoots'] - independent_count)}
    digests = {x['digest'] for x in all_valid}
    roots = {x['root'] for x in all_valid}
    duplicate_bindings = len(all_valid) - len(digests)
    # Reuse across criteria is tracked, not silently counted as independent.
    reused = {}
    for cid, group in per_criterion.items():
        for e in group:
            reused.setdefault(e['digest'], set()).add(cid)
    reused_across_criteria = sum(len(v) > 1 for v in reused.values())
    complete = all(r['met'] for r in results.values()) and not invalid
    return {'state': 'EVIDENCE_READY_FOR_EXTERNAL_REVIEW' if complete else 'EVIDENCE_HOLD',
        'goalId': goal_id, 'criteriaTotal': len(criteria), 'criteriaMet': sum(x['met'] for x in results.values()),
        'bindingsSubmitted': len(bindings), 'bindingsVerified': len(all_valid),
        'uniqueContentSources': len(digests), 'uniqueProvenanceRoots': len(roots),
        'duplicateContentBindings': duplicate_bindings, 'reusedContentAcrossCriteria': reused_across_criteria,
        'requirements': results, 'invalid': invalid, 'acceptedScore': None, 'officialPassIssued': False}


def assess_three_phase_runs(workspace: Path, events: list[dict], *, goal_id: str) -> dict:
    """Three DIFFERENT real observations, not three identical unit test repetitions."""
    if not isinstance(events, list) or len(events) != 3:
        return {'state': 'EXECUTION_HOLD', 'reason': 'THREE_DISTINCT_PHASES_REQUIRED'}
    seen = set()
    digests = []
    for expected_phase, event in zip(PHASES, events):
        if not isinstance(event, dict) or event.get('phase') != expected_phase or event.get('goalId') != goal_id:
            return {'state': 'EXECUTION_HOLD', 'reason': 'PHASE_OR_GOAL_MISMATCH'}
        uid = event.get('runId')
        if not isinstance(uid, str) or not uid.strip() or uid in seen:
            return {'state': 'EXECUTION_HOLD', 'reason': 'REPEATED_OR_MISSING_RUN_ID'}
        seen.add(uid)
        if event.get('processObserved') is not True or type(event.get('exitCode')) is not int:
            return {'state': 'EXECUTION_HOLD', 'reason': 'NO_OBSERVED_PROCESS'}
        try:
            observed, _, content = _bytes_pin(workspace, event.get('relativePath'))
        except (OSError, ValueError, TypeError):
            return {'state': 'EXECUTION_HOLD', 'reason': 'NO_PINNED_REAL_ARTIFACT'}
        if event.get('artifactSha256') != observed:
            return {'state': 'EXECUTION_HOLD', 'reason': 'RUN_ARTIFACT_MISMATCH'}
        try:
            observed_document = json.loads(content)
        except (ValueError, UnicodeDecodeError, TypeError):
            return {'state': 'EXECUTION_HOLD', 'reason': 'RUN_RECEIPT_NOT_READABLE'}
        if (not isinstance(observed_document, dict) or observed_document.get('phase') != expected_phase or
            observed_document.get('goalId') != goal_id or observed_document.get('runId') != uid):
            return {'state': 'EXECUTION_HOLD', 'reason': 'RUN_RECEIPT_IDENTITY_MISMATCH'}
        # Reject claims about exit/fault/outcome inconsistent with the actual
        # phase receipt. Self-reported process observations remain CANDIDATE.
        if (observed_document.get('processObserved') is not True or
            type(observed_document.get('exitCode')) is not int or
            observed_document['exitCode'] != event['exitCode']):
            return {'state': 'EXECUTION_HOLD', 'reason': 'RUN_RECEIPT_PROCESS_OR_EXIT_DRIFT'}
        phase_fields = ('taskOutcome',) if expected_phase == PHASES[0] else (
            ('faultInjected', 'faultObserved', 'faultKind', 'recoveryObserved')
            if expected_phase == PHASES[1] else ('taskOutcome', 'regressionClear'))
        if any(observed_document.get(field) != event.get(field) or
               type(observed_document.get(field)) is not type(event.get(field))
               for field in phase_fields):
            return {'state': 'EXECUTION_HOLD', 'reason': 'RUN_RECEIPT_OUTCOME_OR_FAULT_DRIFT'}
        digests.append(observed)
        if expected_phase == PHASES[0] and not isinstance(event.get('taskOutcome'), bool):
            return {'state': 'EXECUTION_HOLD', 'reason': 'BASELINE_TASK_UNMEASURED'}
        if expected_phase == PHASES[1] and (event.get('faultInjected') is not True or
            event.get('faultObserved') is not True or not isinstance(event.get('faultKind'), str) or
            not event['faultKind'] or event.get('recoveryObserved') is not True):
            return {'state': 'EXECUTION_HOLD', 'reason': 'NO_ADVERSARIAL_RECOVERY_PROOF'}
        if expected_phase == PHASES[2] and (event['exitCode'] != 0 or event.get('taskOutcome') is not True or
            event.get('regressionClear') is not True):
            return {'state': 'EXECUTION_HOLD', 'reason': 'RETEST_NOT_PROVEN'}
    return {'state': 'THREE_PHASE_LOCAL_PROOF_CANDIDATE', 'observedRuns': 3,
            'goalId': goal_id, 'phaseKinds': list(PHASES), 'uniqueRunIds': len(seen),
            'uniqueArtifactContent': len(set(digests)),
            'acceptedScore': None, 'officialPassIssued': False}


def finish_readiness(goal_id: str, evidence_audit: dict, three_phase: dict,
                     *, observed_working_result: bool, independent_review: dict | None,
                     owner_decision: dict | None, donecheck: dict | None,
                     existing_authority_verifier=None) -> dict:
    """Only checks a readiness boundary; cannot issue a DoneCheck or owner signature.

    Claimed records are not authoritative: existing authority must verify both
    documents via caller-provided bridge. Even verified records are OBSERVATIONS
    of an external mechanism, not newly created permissions.
    """
    missing = []
    if evidence_audit.get('state') != 'EVIDENCE_READY_FOR_EXTERNAL_REVIEW' or evidence_audit.get('goalId') != goal_id:
        missing.append('INDEPENDENT_SOURCE_EVIDENCE')
    if three_phase.get('state') != 'THREE_PHASE_LOCAL_PROOF_CANDIDATE' or three_phase.get('goalId') != goal_id:
        missing.append('REAL_THREE_PHASE_EXECUTION')
    if observed_working_result is not True:
        missing.append('WORKING_USER_RESULT')
    if not isinstance(independent_review, dict) or independent_review.get('goalId') != goal_id:
        missing.append('INDEPENDENT_REVIEW_RECORD')
    elif independent_review.get('reviewerId') == independent_review.get('executorId'):
        missing.append('REVIEWER_SEPARATION')
    if not isinstance(owner_decision, dict) or owner_decision.get('goalId') != goal_id:
        missing.append('OWNER_DECISION_RECORD')
    if not isinstance(donecheck, dict) or donecheck.get('goalId') != goal_id:
        missing.append('OFFICIAL_DONECHECK_RECORD')
    if missing:
        return {'state': 'FINISH_HOLD', 'missing': sorted(set(missing)),
            'acceptedScore': None, 'verifiedFinishIssued': False}
    if not callable(existing_authority_verifier):
        return {'state': 'FINISH_HOLD', 'missing': ['EXISTING_AUTHORITY_BRIDGE'],
                'acceptedScore': None, 'verifiedFinishIssued': False}
    # This callback MUST be linked to the existing external owner/DoneCheck
    # mechanism. This module does not fabricate or persist official results.
    try:
        accepted = existing_authority_verifier(goal_id, independent_review, owner_decision, donecheck)
    except Exception:
        accepted = False
    if accepted is not True:
        return {'state': 'FINISH_HOLD', 'missing': ['AUTHORIZED_ACCEPTANCE_UNVERIFIED'],
                'acceptedScore': None, 'verifiedFinishIssued': False}
    return {'state': 'EXTERNAL_BRIDGE_RESPONSE_CANDIDATE_NOT_ISSUED',
            'missing': [], 'acceptedScore': None, 'verifiedFinishIssued': False,
            'note': 'Callback response observed. Existing owner/DoneCheck system alone has official authority.'}
