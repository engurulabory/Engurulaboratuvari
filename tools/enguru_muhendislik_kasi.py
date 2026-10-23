#!/usr/bin/env python3
"""ENGURU OSi learning sidecar: untrusted evidence -> reviewable, deterministic delta.

An advisory reader/writer for a dedicated draft branch. It never signs, authorizes,
merges, changes canonical product files, or executes event-supplied instructions.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys

SCHEMA = "enguru.mk.evidence-event/v1"
MARKER = "ENGURU_MK_EVENT_V1"
MAX_EVENT_BYTES = 24000
ALLOWED_TYPES = frozenset({"UNEXPECTED", "ERROR", "MISMATCH", "REGRESSION", "IMPROVEMENT", "NEW_REQUIREMENT", "SUCCESS"})
ALLOWED_LEVELS = frozenset({"A", "B", "C", "D"})
ALLOWED_CAUSES = frozenset({"HYPOTHESIS", "CONFIRMED", "UNKNOWN"})
ALLOWED_TEST_STATES = frozenset({"NOT_EXECUTED", "PASS", "HOLD", "FAIL"})
FIELDS = frozenset({"schema", "eventId", "taskId", "observedAt", "type", "evidenceLevel", "sourceUri", "sourceSha256", "sourcePath", "expected", "observed", "causeStatus", "fixProposal", "testState", "examinedCount", "impact", "suggestedCheck", "correlationId"})
REQUIRED = frozenset({"schema", "eventId", "taskId", "observedAt", "type", "evidenceLevel", "sourceUri", "sourceSha256", "expected", "observed", "causeStatus", "fixProposal", "testState"})
TASK_ID = "ENGURU_MANAGEMENT_V69_PR_203"
ID_RE = re.compile(r"MK-EVT-[A-Z0-9][A-Z0-9_-]{4,70}\Z")
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
MARK_RE = re.compile(r"<!-- ENGURU_MK_EVENT_V1:([A-Za-z0-9_\-=]+):([0-9a-f]{64}) -->")
# Additional risky strings are rejected before any persistence, even in quotations.
SECRET_RE = re.compile(r"-----BEGIN (?:OPENSSH |RSA |EC |ENCRYPTED )?PRIVATE KEY-----|(?i:password|private_key|access[_-]?token|secret[_-]?key)\s*[:=]\s*\S+|\bgh[pousr]_[A-Za-z0-9]{25,}\b", re.MULTILINE)


class IntakeHold(ValueError):
    pass


def strict_object(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise IntakeHold("HOLD_DUPLICATE_JSON_KEY")
        out[k] = v
    return out


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def parse_event(raw: bytes) -> dict:
    if len(raw) > MAX_EVENT_BYTES:
        raise IntakeHold("HOLD_EVENT_SIZE")
    try:
        event = json.loads(raw, object_pairs_hook=strict_object)
    except IntakeHold:
        raise
    except (ValueError, UnicodeDecodeError) as ex:
        raise IntakeHold("HOLD_EVENT_JSON") from ex
    if not isinstance(event, dict) or set(event) - FIELDS or not REQUIRED.issubset(event):
        raise IntakeHold("HOLD_EVENT_SCHEMA_FIELDS")
    if event["schema"] != SCHEMA or not isinstance(event["eventId"], str) or not ID_RE.fullmatch(event["eventId"]):
        raise IntakeHold("HOLD_EVENT_ID_SCHEMA")
    if event["taskId"] != TASK_ID:
        raise IntakeHold("HOLD_TASK_SCOPE")
    for k in ("expected", "observed", "fixProposal", "sourceUri", "impact", "suggestedCheck"):
        if k in event and (not isinstance(event[k], str) or len(event[k]) > 4000):
            raise IntakeHold("HOLD_TEXT_FIELD_" + k)
    for k in ("expected", "observed", "fixProposal", "sourceUri"):
        if not event[k].strip():
            raise IntakeHold("HOLD_EMPTY_FIELD_" + k)
    if not isinstance(event["sourceSha256"], str) or not HASH_RE.fullmatch(event["sourceSha256"]):
        raise IntakeHold("HOLD_EVIDENCE_SHA_FORMAT")
    if not isinstance(event["observedAt"], str):
        raise IntakeHold("HOLD_TIME_FORMAT")
    try:
        dt = datetime.fromisoformat(event["observedAt"].replace("Z", "+00:00"))
        if dt.tzinfo is None:
            raise ValueError("naive")
    except ValueError as ex:
        raise IntakeHold("HOLD_TIME_FORMAT") from ex
    if event["type"] not in ALLOWED_TYPES or event["evidenceLevel"] not in ALLOWED_LEVELS or event["causeStatus"] not in ALLOWED_CAUSES or event["testState"] not in ALLOWED_TEST_STATES:
        raise IntakeHold("HOLD_EVENT_ENUM")
    if "examinedCount" in event and (type(event["examinedCount"]) is not int or event["examinedCount"] < 0):
        raise IntakeHold("HOLD_COVERAGE_TYPE")
    if "sourcePath" in event and (not isinstance(event["sourcePath"], str) or len(event["sourcePath"]) > 1000):
        raise IntakeHold("HOLD_SOURCE_PATH")
    if 'correlationId' in event and (not isinstance(event['correlationId'], str) or not re.fullmatch(r'[A-Z0-9][A-Z0-9_-]{5,70}', event['correlationId'])):
        raise IntakeHold('HOLD_CORRELATION_ID')
    if SECRET_RE.search(canonical(event).decode("utf-8")):
        raise IntakeHold("HOLD_POTENTIAL_SECRET")
    return event


def inspect_evidence(event: dict) -> str:
    """Actual byte hash proof is local-only. A supplied SHA is a claim until checked."""
    sp = event.get("sourcePath")
    if not sp:
        return "UNVERIFIED_EVIDENCE_POINTER"
    p = Path(sp)
    try:
        if not p.is_file() or p.is_symlink() or p.stat().st_size > 5_000_000:
            return "HOLD_EVIDENCE_FILE"
        actual = sha(p.read_bytes())
    except OSError:
        return "HOLD_EVIDENCE_FILE"
    if actual != event["sourceSha256"]:
        return "HOLD_EVIDENCE_SHA_MISMATCH"
    return "PASS_BYTE_SHA_ONLY"


def classify(event: dict, evidence_state: str) -> dict:
    issues = []
    if event.get("examinedCount") == 0:
        issues.append("ZERO_COVERAGE_IS_NOT_ABSENCE_PROOF")
    if event["causeStatus"] == "CONFIRMED" and evidence_state != "PASS_BYTE_SHA_ONLY":
        issues.append("CAUSE_CLAIM_REQUIRES_INDEPENDENT_CONFIRMATION")
    if event["evidenceLevel"] in {"B", "C", "D"} and evidence_state != "PASS_BYTE_SHA_ONLY":
        issues.append("EVIDENCE_LEVEL_CLAIM_NOT_INDEPENDENTLY_AUTHENTICATED")
    if event.get('correlationId') and event['type'] == 'UNEXPECTED':
        issues.append('OSI_RESPONSE_CORRELATION_REVIEW_REQUIRED')
    # Even a local hash match proves bytes only, not independent verifier or owner signature.
    if event["evidenceLevel"] == "D":
        issues.append("OWNER_ATTESTATION_REQUIRES_EXTERNAL_CANONICAL_VERIFIER")
    if event["type"] in {"ERROR", "MISMATCH", "REGRESSION", "NEW_REQUIREMENT"}:
        issues.append("GENERATE_NEGATIVE_REGRESSION_CANDIDATE")
    return {"evidenceState": evidence_state, "advisoryState": "REVIEW_REQUIRED", "issues": sorted(set(issues)), "officialAcceptance": "UNCHANGED_HOLD", "productGatesModified": 0}


def markers(record: str) -> dict:
    found = {}
    for m in MARK_RE.finditer(record):
        try:
            decoded = base64.urlsafe_b64decode(m.group(1).encode())
            if sha(decoded) != m.group(2):
                raise IntakeHold("HOLD_EXISTING_RECORD_MARKER_HASH")
            obj = json.loads(decoded, object_pairs_hook=strict_object)
            if not isinstance(obj, dict) or not isinstance(obj.get("eventId"), str):
                raise IntakeHold("HOLD_EXISTING_RECORD_MARKER_SCHEMA")
            if obj["eventId"] in found and found[obj["eventId"]] != m.group(2):
                raise IntakeHold("HOLD_EXISTING_DUPLICATE_ID_CONFLICT")
            found[obj["eventId"]] = m.group(2)
        except (ValueError, UnicodeError) as ex:
            raise IntakeHold("HOLD_EXISTING_RECORD_MARKER_DECODE") from ex
    return found


def add_event(record: str, event: dict, classification: dict):
    if not record.startswith("# ENGÜRÜ OSi × ChatGPT — Mühendislik Kası™"):
        raise IntakeHold("HOLD_RECORD_AUTHORITY")
    cb = canonical(event)
    digest = sha(cb)
    previous = markers(record)
    if event["eventId"] in previous:
        if previous[event["eventId"]] != digest:
            raise IntakeHold("HOLD_EVENT_ID_CONTENT_CONFLICT")
        return record, "IDEMPOTENT_SAME_EVENT"
    code = base64.urlsafe_b64encode(cb).decode("ascii")
    # Presentation escapes do not affect canonical marker stored for replay.
    def text(s):
        return html.escape(s, quote=False).replace("\r", " ").replace("\n", " / ").replace("|", "&#124;")
    appended = (
        f"\n### Otomatik öğrenme adayı — {event['eventId']}\n"
        f"<!-- {MARKER}:{code}:{digest} -->\n"
        f"- **Tür:** `{event['type']}` · **Seviye iddiası:** `{event['evidenceLevel']}` · **Kanıt kontrolü:** `{classification['evidenceState']}`.\n"
        f"- **Gözlem:** {text(event['observed'])}\n"
        f"- **Beklenti:** {text(event['expected'])}\n"
        f"- **Önerilen fark:** {text(event['fixProposal'])}\n"
        f"- **Kaynak:** {text(event['sourceUri'])} · SHA-256 `{event['sourceSha256']}`.\n"
        f"- **OSi eşleşme kimliği:** `{event.get('correlationId', 'UNSPECIFIED')}`.\n"
        f"- **Karar:** `REVIEW_REQUIRED`; ürün kabul sayacı değişimi `0`; kontroller: {', '.join(classification['issues']) or 'SOURCE_REVIEW'}.\n"
    )
    return record.rstrip("\n") + "\n" + appended, "NEW_REVIEW_CANDIDATE"


def process(record: str, event_bytes: bytes) -> tuple[str, dict]:
    event = parse_event(event_bytes)
    status = inspect_evidence(event)
    if status.startswith("HOLD_"):
        raise IntakeHold(status)
    cls = classify(event, status)
    updated, state = add_event(record, event, cls)
    return updated, {"state": state, "eventId": event["eventId"], "candidateDigest": sha(canonical(event)), **cls}


def run(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--record", type=Path, required=True)
    p.add_argument("--event", type=Path)
    p.add_argument("--github-event", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    ns = p.parse_args(argv)
    if (ns.event is None) == (ns.github_event is None):
        raise IntakeHold("HOLD_REQUIRE_EXACTLY_ONE_INPUT")
    if not ns.record.is_file() or ns.record.is_symlink() or ns.record.stat().st_size > 2_000_000:
        raise IntakeHold("HOLD_ORIGINAL_RECORD")
    record_raw = ns.record.read_bytes()
    record = record_raw.decode("utf-8")
    if ns.github_event:
        if ns.github_event.is_symlink() or not ns.github_event.is_file() or ns.github_event.stat().st_size > 300_000:
            raise IntakeHold("HOLD_GITHUB_EVENT_FILE")
        envelope = json.loads(ns.github_event.read_bytes(), object_pairs_hook=strict_object)
        issue = envelope.get("issue") or {}
        sender = envelope.get("sender") or {}
        comment = envelope.get("comment") or {}
        authorized = os.environ.get("ENGURU_MK_OWNER_LOGIN", "")
        if not authorized or sender.get("login") != authorized:
            raise IntakeHold("HOLD_OWNER_ACTOR_NOT_AUTHENTICATED")
        if issue.get("number") not in (203, 206) or not issue.get("pull_request"):
            raise IntakeHold("HOLD_EVENT_ISSUE_SCOPE")
        text = comment.get("body", "")
        m = re.fullmatch(r"\s*```enguru-mk-event\s*\n(\{.*\})\s*\n```\s*", text, flags=re.S)
        if not m:
            raise IntakeHold("HOLD_EVENT_COMMENT_FORMAT")
        event_bytes = m.group(1).encode("utf-8")
    else:
        if ns.event.is_symlink() or not ns.event.is_file():
            raise IntakeHold("HOLD_EVENT_FILE")
        event_bytes = ns.event.read_bytes()
    updated, receipt = process(record, event_bytes)
    if ns.output.resolve() == ns.record.resolve():
        raise IntakeHold("HOLD_ORIGINAL_RECORD_PROTECTED")
    if ns.output.is_symlink() or ns.receipt.is_symlink():
        raise IntakeHold("HOLD_OUTPUT_SYMLINK")
    ns.output.parent.mkdir(parents=True, exist_ok=True)
    ns.receipt.parent.mkdir(parents=True, exist_ok=True)
    ns.output.write_text(updated, encoding="utf-8")
    receipt.update({"originalRecordSha256": sha(record_raw), "candidateRecordSha256": sha(updated.encode("utf-8"))})
    ns.receipt.write_bytes(canonical(receipt) + b"\n")
    print("STATE=" + receipt["state"])
    print("EVIDENCE_STATE=" + receipt["evidenceState"])
    print("OFFICIAL_ACCEPTANCE=" + receipt["officialAcceptance"])
    print("CANDIDATE_SHA256=" + receipt["candidateRecordSha256"])


if __name__ == "__main__":
    try:
        run()
    except IntakeHold as ex:
        print("STATE=" + str(ex))
        sys.exit(2)