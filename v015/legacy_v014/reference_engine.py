"""Reviewer-authored V014 fixture implementation. No app integration or tool dispatcher.

Trust boundary: accepted receipt hashes are supplied by a separate trusted harness,
never by model JSON. This prototype does not authenticate production receipts.
"""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat


def unique_jobs(jobs):
    seen, result = set(), []
    for job in jobs:
        if job not in seen:
            seen.add(job)
            result.append(job)
    return result


def remaining(done):
    if type(done) is not int or not 0 <= done <= 100:
        raise ValueError('INTEGER_0_TO_100_REQUIRED')
    return 100 - done


def progress(weights, verified_blocks):
    if (not weights or any(not isinstance(k, str) or not k for k in weights)
            or any(type(v) is not int or v <= 0 for v in weights.values())
            or sum(weights.values()) != 10000):
        raise ValueError('INVALID_FIXED_WEIGHTS')
    blocks = list(verified_blocks)
    if any(not isinstance(b, str) or b not in weights for b in blocks):
        raise ValueError('UNKNOWN_VERIFIED_BLOCK')
    if len(set(blocks)) != len(blocks):
        raise ValueError('DUPLICATE_RECEIPT_BLOCK')
    done = sum(weights[b] for b in blocks)
    return done / 100, (10000 - done) / 100


def validate_dag(ids, dependencies):
    if set(dependencies) != set(ids):
        raise ValueError('DEPENDENCY_KEYS')
    visiting, visited = set(), set()
    def visit(job):
        if job in visiting:
            raise ValueError('CYCLE')
        if job in visited:
            return
        visiting.add(job)
        for dep in dependencies[job]:
            if dep not in ids:
                raise ValueError('UNKNOWN_DEPENDENCY')
            visit(dep)
        visiting.remove(job)
        visited.add(job)
    for job in ids:
        visit(job)


def manager_plan(weights, dependencies, accepted_blocks, attempts):
    validate_dag(weights, dependencies)
    completed, left = progress(weights, accepted_blocks)
    done = set(accepted_blocks)
    if type(attempts) is not int or not 0 <= attempts <= 3:
        raise ValueError('REPAIR_BUDGET')
    active = next((b for b in weights if b not in done
                   and set(dependencies[b]) <= done), None)
    return dict(completed_percent=completed, remaining_percent=left,
                active_block=active, attempts_used=attempts, attempts_left=3-attempts)


def repair_decision(history):
    if len(history) > 3:
        raise ValueError('REPAIR_BUDGET')
    if len(history) == 3:
        return 'HOLD_BUDGET'
    if len(history) >= 2 and history[-1] == history[-2]:
        return 'HOLD_NEW_DIAGNOSIS_REQUIRED'
    return 'REVIEW_NEXT_ATTEMPT'


def task_contract(source_sha=None):
    # A draft is useful even when source acquisition is still blocked.
    return {'task_id': 'unique_jobs', 'plan': 'v1', 'state': 'HOLD',
            'SOURCE_SHA': source_sha or 'HOLD_SOURCE_REQUIRED',
            'scope': '/tmp/enguru_exam_fixture',
            'acceptance': ['first-seen order preserved', 'duplicate IDs removed'],
            'tests': ['empty', 'repeated', 'single', 'order'],
            'human_threshold': ['install', 'delete', 'merge', 'publish'],
            'ran_tests': False, 'next_action': 'pin source and review contract'}


class Conflict(ValueError):
    pass


class Queue:
    """SQLite fixture; no external effects. Claim and completion are separate.

    All connections, including competing workers, must use this schema/API.
    accepted_receipts is a set of hashes from the trusted harness, not model input.
    """
    def __init__(self, path=':memory:', *, accepted_receipts=None):
        self.db = sqlite3.connect(path, timeout=5, isolation_level=None)
        self.accepted = frozenset(accepted_receipts or ())
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS jobs(
              seq INTEGER PRIMARY KEY, command_id TEXT NOT NULL UNIQUE,
              payload TEXT NOT NULL, task TEXT NOT NULL, plan TEXT NOT NULL,
              source TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'READY',
              network INTEGER NOT NULL, permitted INTEGER NOT NULL, deps TEXT NOT NULL);
            CREATE UNIQUE INDEX IF NOT EXISTS one_active ON jobs((1))
              WHERE state='CLAIMED';
        ''')

    def submit(self, command_id, payload, *, task='T1', plan='v1', source='S1',
               deps=(), network=False, permitted=True, state='READY'):
        if not isinstance(command_id, str) or not command_id:
            raise ValueError('COMMAND_ID')
        if (state not in {'READY', 'HOLD', 'WAIT_NETWORK'}
                or type(network) is not bool or type(permitted) is not bool
                or any(not isinstance(x, str) or not x for x in (task, plan, source))
                or any(not isinstance(x, str) or not x for x in deps)):
            raise ValueError('INVALID_JOB_CONTRACT')
        # Same command binds not just payload but its execution contract.
        values = (json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False),
                  task, plan, source, state, int(network), int(permitted),
                  json.dumps(list(deps)))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row = self.db.execute('SELECT seq,payload,task,plan,source,network,permitted,deps '
                                  'FROM jobs WHERE command_id=?', (command_id,)).fetchone()
            if row:
                original = (values[0], values[1], values[2], values[3],
                            values[5], values[6], values[7])
                if row[1:] != original:
                    raise Conflict('COMMAND_ID_CONTRACT_CONFLICT')
                job = row[0]
            else:
                job = self.db.execute('INSERT INTO jobs(command_id,payload,task,plan,source,'
                                      'state,network,permitted,deps) VALUES(?,?,?,?,?,?,?,?,?)',
                                      (command_id, *values)).lastrowid
            self.db.execute('COMMIT')
            return job
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def claim(self, *, online):
        if type(online) is not bool:
            raise ValueError('NETWORK_FACT')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            selected = None
            if not self.db.execute("SELECT 1 FROM jobs WHERE state='CLAIMED'").fetchone():
                done = {r[0] for r in self.db.execute("SELECT command_id FROM jobs WHERE state='DONE'")}
                for seq, cid, network, permitted, deps in self.db.execute(
                    "SELECT seq,command_id,network,permitted,deps FROM jobs "
                    "WHERE state IN ('READY','WAIT_NETWORK') ORDER BY seq"):
                    if permitted and (online or not network) and set(json.loads(deps)) <= done:
                        self.db.execute("UPDATE jobs SET state='CLAIMED' WHERE seq=?", (seq,))
                        selected = cid
                        break
            self.db.execute('COMMIT')
            return selected
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def complete(self, cid, receipt):
        """Only an externally accepted full receipt hash, exact binding, exit0 can close."""
        self.db.execute('BEGIN IMMEDIATE')
        try:
            job = self.db.execute('SELECT task,plan,source,state FROM jobs WHERE command_id=?',
                                  (cid,)).fetchone()
            if not job or job[3] != 'CLAIMED' or not isinstance(receipt, dict):
                raise ValueError('NO_CLAIM_OR_RECEIPT')
            digest = hashlib.sha256(json.dumps(receipt, sort_keys=True,
                ensure_ascii=False, allow_nan=False).encode()).hexdigest()
            if (digest not in self.accepted
                    or tuple(receipt.get(k) for k in ('task', 'plan', 'source')) != job[:3]
                    or receipt.get('command_id') != cid
                    or type(receipt.get('exit_code')) is not int or receipt['exit_code'] != 0):
                raise ValueError('INDEPENDENT_RECEIPT_REQUIRED')
            self.db.execute("UPDATE jobs SET state='DONE' WHERE command_id=?", (cid,))
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def close(self):
        self.db.close()


def recovery(checkpoint, current, effect):
    if checkpoint != current:
        return 'HOLD_SOURCE_PLAN_TASK_DRIFT'
    if effect == 'UNKNOWN':
        return 'HOLD_READ_ONLY_RECONCILE'
    if effect == 'APPLIED_VERIFIED':
        return 'RESTORE_VERIFIED_RECEIPT_NO_REPLAY'
    if effect == 'NOT_APPLIED_VERIFIED':
        return 'REVIEW_SAME_COMMAND_ID_AND_AUTHORITY'
    return 'HOLD_INVALID_EFFECT'


MANIFEST_FILES = ('output.txt', 'test-receipt.json')


def file_hashes(root):
    # Trusted test-root path; reject symlink components and final children.
    root = Path(root).absolute()
    if '..' in root.parts or any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError('UNSAFE_MANIFEST_ROOT')
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        result = {}
        for name in MANIFEST_FILES:
            f = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            with os.fdopen(f, 'rb') as stream:
                st = os.fstat(stream.fileno())
                if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                    raise ValueError('UNSAFE_MANIFEST_MEMBER')
                b = stream.read(3_000_001)
                if len(b) > 3_000_000:
                    raise ValueError('FILE_SIZE_LIMIT')
                result[name] = hashlib.sha256(b).hexdigest()
        return result
    finally:
        os.close(fd)


def verify_manifest(root, manifest):
    if not isinstance(manifest, dict) or set(manifest) != set(MANIFEST_FILES):
        raise ValueError('EXACT_MANIFEST_REQUIRED')
    if file_hashes(root) != manifest:
        raise ValueError('HASH_MISMATCH')
    return 'INTEGRITY_ONLY_NOT_TEST_SUCCESS'
