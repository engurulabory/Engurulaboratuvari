#!/usr/bin/env python3
"""ENGURU MK 5-minute GitHub polling: deterministic observer, not an AI or owner signer.

Writes candidates only to a dedicated review branch working tree. All API payloads are
untrusted. Mac OSi/chat messages enter only if explicitly relayed by an allowed GitHub user.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enguru_muhendislik_kasi as muscle

SCHEMA = 'enguru.mk.watch-checkpoint/v1'
TARGETS = [('engurulabory/Engurulaboratuvari', 203, 'MGMT'),
           ('engurulabory/Engurulaboratuvari', 206, 'LEARN'),
           ('engurulabory/enguru-mac-engineer', 14, 'OSIBRIDGE')]
TAGS = {'<!-- ENGURU_OSI_BLOCK_V1 -->': 'NEW_REQUIREMENT',
        '<!-- ENGURU_OSI_RESPONSE_V1 -->': 'UNEXPECTED'}
CODE_FENCE = re.compile(r'^\s*```enguru-mk-event\s*\n(\{.*\})\s*\n```\s*$', re.S)
MAX_COMMENTS = 500


def canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def fingerprint(obj):
    return hashlib.sha256(canon(obj)).hexdigest()


def key(repo, number):
    return repo.replace('/', '__') + '__' + str(number)


def url_for(repo, number):
    return f'https://github.com/{repo}/pull/{number}'


def http_get(uri, token):
    if not uri.startswith('https://api.github.com/repos/') or not token:
        raise ValueError('HOLD_API_BOUNDARY_OR_TOKEN')
    request = urllib.request.Request(uri, headers={
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'enguru-mk-observer-v1',
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = response.read(1_000_001)
        if len(payload) > 1_000_000:
            raise ValueError('HOLD_API_PAYLOAD_LIMIT')
    return json.loads(payload, object_pairs_hook=muscle.strict_object)


def github_fetcher(token, cross_repo_token=None):
    def fetch(endpoint):
        private_repo = endpoint.startswith('engurulabory/enguru-mac-engineer/')
        selected = (cross_repo_token or token) if private_repo else token
        return http_get('https://api.github.com/repos/' + endpoint, selected)
    return fetch


def comments(fetch, repo, number):
    result = []
    # First 5 pages; if limit reached, fail closed to prevent silent dropped comments.
    for page in range(1, 6):
        part = fetch(f'{repo}/issues/{number}/comments?per_page=100&page={page}')
        if not isinstance(part, list):
            raise ValueError('HOLD_COMMENT_RESPONSE')
        result.extend(part)
        if len(part) < 100:
            return sorted(result, key=lambda x: x['id'])
    if len(result) == MAX_COMMENTS:
        raise ValueError('HOLD_COMMENT_PAGINATION_LIMIT')
    return sorted(result, key=lambda x: x['id'])


def snapshot(fetch, repo, number, kind):
    pr = fetch(f'{repo}/pulls/{number}')
    if not isinstance(pr, dict) or not isinstance(pr.get('head'), dict):
        raise ValueError('HOLD_PR_PAYLOAD')
    if not re.fullmatch('[0-9a-f]{40}', str(pr['head'].get('sha', ''))):
        raise ValueError('HOLD_HEAD_SHA')
    result = {'repo': repo, 'pr': number, 'state': pr['state'],
              'merged': bool(pr.get('merged', False)), 'draft': bool(pr.get('draft', False))}
    if kind != 'LEARN':  # Our own review branch changes each time it learns: no feedback loop.
        result['head'] = pr['head']['sha']
        runs = fetch(f'{repo}/actions/runs?head_sha={result["head"]}&per_page=25')
        entries = runs.get('workflow_runs', [])
        if not isinstance(entries, list):
            raise ValueError('HOLD_RUN_PAYLOAD')
        result['ci'] = sorted([{'id': int(run['id']), 'name': str(run.get('name', ''))[:120],
                                'conclusion': run.get('conclusion'), 'status': run.get('status')}
                               for run in entries if run.get('head_sha') == result['head']],
                              key=lambda x: x['id'])
    return result


def event_for_comment(c, repo, number, owner):
    """Conservative parsing: user-owned, explicit tags only, never raw or implicit chat sync."""
    user = c.get('user') or {}
    if not owner or user.get('login') != owner or user.get('type') == 'Bot':
        return None
    body = c.get('body')
    if not isinstance(body, str) or len(body.encode('utf-8')) > 24000:
        return None
    fence = CODE_FENCE.fullmatch(body)
    if fence:
        raw = fence.group(1).encode('utf-8')
        try:
            return muscle.parse_event(raw)
        except muscle.IntakeHold:
            return None
    for tag, kind in TAGS.items():
        if body.startswith(tag + '\n'):
            observed = body[len(tag):].strip()
            if not (2 <= len(observed) <= 3500):
                return None
            if muscle.SECRET_RE.search(observed):
                return None
            created = c.get('created_at', '')
            try:
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    return None
            except (ValueError, TypeError):
                return None
            comment_id = int(c['id'])
            obj = {
                'schema': muscle.SCHEMA, 'eventId': f'MK-EVT-OSI-{number}-{comment_id}',
                'taskId': muscle.TASK_ID, 'observedAt': created,
                'type': kind, 'evidenceLevel': 'A',
                'sourceUri': c.get('html_url') or url_for(repo, number),
                'sourceSha256': hashlib.sha256(body.encode('utf-8')).hexdigest(),
                'expected': 'OSi blok/yanıt zincirinde doğrulanabilir ve yetkili kaynak',
                'observed': observed, 'causeStatus': 'UNKNOWN',
                'fixProposal': 'OSi kaynak kanıtı ve görev kapsamı bağımsız incelensin',
                'testState': 'NOT_EXECUTED',
            }
            return muscle.parse_event(canon(obj))
    return None


def delta_event(current, former, k, observed_at):
    repo, number, tag = k
    content = {'old': former, 'new': current}
    return {
        'schema': muscle.SCHEMA,
        'eventId': 'MK-EVT-GH-' + tag + '-' + fingerprint(content)[:16].upper(),
        'taskId': muscle.TASK_ID, 'observedAt': observed_at,
        'type': 'IMPROVEMENT' if current.get('merged') and not former.get('merged') else 'MISMATCH',
        'evidenceLevel': 'A', 'sourceUri': url_for(repo, number),
        'sourceSha256': fingerprint(current),
        'expected': f'Önceki GitHub durum SHA-256 {fingerprint(former)}',
        'observed': f'Yeni GitHub durum SHA-256 {fingerprint(current)}; PR #{number}; state={current["state"]}; merged={current["merged"]}',
        'causeStatus': 'UNKNOWN',
        'fixProposal': 'Güncel commit/workflow run kanıtını bağımsız doğrula ve gereken kontrol farkını değerlendir',
        'testState': 'NOT_EXECUTED',
    }


def evaluate(fetch, original, checkpoint, owner, now):
    if not original.startswith('# ENGÜRÜ OSi × ChatGPT — Mühendislik Kası™'):
        raise ValueError('HOLD_CANONICAL_RECORD')
    if checkpoint is not None and checkpoint.get('schema') != SCHEMA:
        raise ValueError('HOLD_CHECKPOINT_SCHEMA')
    previous = (checkpoint or {}).get('targets', {})
    next_targets, events = {}, []
    inaccessible = []
    for repo, number, tag in TARGETS:
        k = key(repo, number)
        try:
            state = snapshot(fetch, repo, number, tag)
            all_comments = comments(fetch, repo, number)
        except urllib.error.HTTPError as ex:
            if tag == 'OSIBRIDGE' and ex.code in (401, 403, 404):
                inaccessible.append('PR14_PRIVATE_REPO_ACCESS_HOLD')
                if k in previous:
                    next_targets[k] = previous[k]  # preserve cursor and last known truth
                continue
            raise
        prev = previous.get(k)
        last_id = max((int(c['id']) for c in all_comments), default=0)
        next_targets[k] = {'snapshot': state, 'commentMaxId': last_id}
        if prev is None:  # Bootstrap only; do not pretend historical messages just arrived.
            continue
        earlier = prev['snapshot']
        if state != earlier:
            events.append(delta_event(state, earlier, (repo, number, tag), now))
        cursor = int(prev['commentMaxId'])
        if last_id < cursor:
            raise ValueError('HOLD_COMMENT_CURSOR_REGRESSION')
        for c in all_comments:
            if int(c['id']) > cursor:
                e = event_for_comment(c, repo, number, owner)
                if e is not None:
                    events.append(e)
    next_checkpoint = {'schema': SCHEMA, 'targets': next_targets, 'accessHolds': inaccessible}
    record, outcomes = original, []
    for event in events:
        try:
            record, receipt = muscle.process(record, canon(event))
            outcomes.append({'eventId': event['eventId'], 'state': receipt['state']})
        except muscle.IntakeHold as err:
            outcomes.append({'eventId': event['eventId'], 'state': str(err)})
            # Invalid event should not block safe metadata checkpoint; its GitHub source remains available.
    return record, next_checkpoint, outcomes


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', required=True, type=Path)
    parser.add_argument('--checkpoint', required=True, type=Path)
    parser.add_argument('--at', default=None)
    a = parser.parse_args(argv)
    token = os.environ.get('GITHUB_TOKEN', '')
    if not token:
        raise ValueError('HOLD_GITHUB_TOKEN')
    if a.record.is_symlink() or not a.record.is_file() or a.checkpoint.is_symlink():
        raise ValueError('HOLD_PATH')
    original = a.record.read_text(encoding='utf-8')
    ck = json.loads(a.checkpoint.read_text(encoding='utf-8')) if a.checkpoint.exists() else None
    now = a.at or datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    updated, checkpoint, outcomes = evaluate(github_fetcher(token, os.environ.get('ENGURU_MK_CROSS_REPO_TOKEN')), original, ck,
        os.environ.get('ENGURU_MK_OWNER_LOGIN', ''), now)
    # Git workflow checkout isolates review branch. Only specified review-only files are written.
    if updated != original:
        a.record.write_text(updated, encoding='utf-8')
    content = canon(checkpoint) + b'\n'
    if not a.checkpoint.exists() or a.checkpoint.read_bytes() != content:
        a.checkpoint.parent.mkdir(parents=True, exist_ok=True)
        a.checkpoint.write_bytes(content)
    print(json.dumps({'state':'PASS_OBSERVATION_ONLY', 'eventsReviewed':len(outcomes),
        'candidateAdded':sum(x['state']=='NEW_REVIEW_CANDIDATE' for x in outcomes),
        'officialAcceptance':'UNCHANGED_HOLD', 'macLocalFilesAccessed':0,
        'accessHolds':checkpoint.get('accessHolds', [])},sort_keys=True))

if __name__ == '__main__':
    try:
        run()
    except (muscle.IntakeHold, ValueError, KeyError, OSError, urllib.error.URLError) as ex:
        print('STATE=HOLD_GUVENLI_DUR; reason=' + type(ex).__name__)
        sys.exit(2)