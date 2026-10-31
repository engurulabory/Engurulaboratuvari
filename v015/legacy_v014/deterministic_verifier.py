"""Fail-closed review boundary, NOT a production policy engine or text executor.

Unrestricted model prose can never authorize an action, even with a safe label.
Typed policy facts below must originate outside the model in a trusted adapter.
There is deliberately no shell, eval, exec, subprocess or tool-dispatch path.
"""
import json
import re
from collections import Counter

FIELDS = {'state', 'answer', 'reason', 'evidence_needed', 'next_action', 'ran_tests'}
STATES = {'PLAN', 'HOLD', 'BLOCKED', 'WAIT_NETWORK', 'NEEDS_APPROVAL', 'NOT_TESTED'}


def parse_response(raw, done_reason):
    if done_reason != 'stop':
        raise ValueError('INCOMPLETE_GENERATION')
    if not isinstance(raw, str) or len(raw.encode()) > 100_000:
        raise ValueError('RESPONSE_SIZE_OR_TYPE')
    def unique_keys(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError('DUPLICATE_JSON_KEY')
            obj[key] = value
        return obj
    def invalid_constant(value):
        raise ValueError('NONFINITE_JSON')
    try:
        obj = json.loads(raw, object_pairs_hook=unique_keys, parse_constant=invalid_constant)
    except (TypeError, RecursionError, json.JSONDecodeError) as e:
        raise ValueError('INVALID_JSON') from e
    if (not isinstance(obj, dict) or set(obj) != FIELDS
            or not isinstance(obj['state'], str) or obj['state'] not in STATES
            or obj['ran_tests'] is not False
            or any(not isinstance(obj[k], str) or not obj[k].strip()
                   for k in FIELDS - {'state', 'ran_tests'})):
        raise ValueError('SCHEMA_OR_FALSE_EXECUTION_CLAIM')
    return obj


def review_model(raw, done_reason):
    try:
        obj = parse_response(raw, done_reason)
    except ValueError as e:
        return dict(state='HOLD', gate=str(e), execution_authorized=False,
                    professional_acceptance='HOLD')
    return dict(state='HOLD', proposed_state=obj['state'], gate='CONTENT_REVIEW_REQUIRED',
                execution_authorized=False, professional_acceptance='HOLD')


def repetition_metrics(raw):
    # Diagnostic only, never reject code merely for repeated syntactic lines.
    try:
        obj = json.loads(raw)
        text = obj.get('answer', raw) if isinstance(obj, dict) else raw
    except ValueError:
        text = raw.replace('\\n', '\n')  # incomplete JSON: diagnostic display only
    if not isinstance(text, str):
        text = raw
    lines = [re.sub(r'^#\s*\d+[.)]\s*', '# ', line.strip())
             for line in text.splitlines() if len(line.strip()) >= 25]
    counts = Counter(lines)
    return dict(long_lines=len(lines), max_repeated_line=max(counts.values(), default=0))


def policy(facts):
    """Deny unknown/incomplete facts. 'REVIEW_ONLY' never invokes any tool.

    Trusted-input prototype: callers must not construct facts from model claims.
    Owner grants also cannot authorize prompt injection, root escape or replay.
    """
    required = {'action', 'source_match', 'scope_match', 'symlink_escape',
                'untrusted_instruction', 'effect', 'grant_valid', 'test_exit'}
    if not isinstance(facts, dict) or set(facts) != required:
        return 'BLOCKED_INVALID_FACTS'
    bools = ('source_match', 'scope_match', 'symlink_escape', 'untrusted_instruction', 'grant_valid')
    if any(type(facts[k]) is not bool for k in bools):
        return 'BLOCKED_INVALID_FACTS'
    if not isinstance(facts['action'], str) or not isinstance(facts['effect'], str):
        return 'BLOCKED_INVALID_FACTS'
    if not facts['scope_match'] or facts['symlink_escape'] or facts['untrusted_instruction']:
        return 'BLOCKED_AUTHORITY_BOUNDARY'
    if facts['action'] not in {'READ', 'TEST_FIXTURE', 'REPLAY', 'INSTALL', 'MERGE', 'PUBLISH', 'DELETE'}:
        return 'BLOCKED_UNKNOWN_ACTION'
    if not facts['source_match']:
        return 'HOLD_SOURCE_DRIFT'
    if facts['effect'] not in {'UNKNOWN', 'NOT_APPLIED_VERIFIED', 'APPLIED_VERIFIED'}:
        return 'BLOCKED_INVALID_EFFECT'
    if facts['action'] == 'REPLAY':
        if facts['effect'] == 'UNKNOWN':
            return 'HOLD_RECONCILE_FIRST'
        if facts['effect'] == 'APPLIED_VERIFIED':
            return 'BLOCKED_DUPLICATE_EFFECT'
    if facts['action'] in {'INSTALL', 'MERGE', 'PUBLISH', 'DELETE', 'REPLAY'} and not facts['grant_valid']:
        return 'NEEDS_APPROVAL'
    if facts['action'] == 'TEST_FIXTURE' and (type(facts['test_exit']) is not int or facts['test_exit'] != 0):
        return 'HOLD_TEST_FAILED_OR_NOT_RUN'
    return 'REVIEW_ONLY_NO_EXECUTION'
