#!/usr/bin/env python3
"""ULMi H1 portable evidence runner when GitHub Actions is unavailable.

Operates on an isolated SHA-verified source release, uses Python stdlib for
orchestration, invokes existing local regression tests, and records honest
provenance. Does not contact GitHub, bypass account controls, or issue an
independent/owner/GitHub-CI PASS.
"""
from __future__ import annotations

import argparse
import warnings
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_release  # noqa: E402 -- preinstalled source-only reproducible packager

EMIR_ID = 'KAPTAN-ULMI-H1-BIRLESIK-01-TECH-01-11-20261118'
BASELINE_COMMIT = '047848f37c89f4a6a0f62ac59ec194594d48d417'
TESTS = (
    ('contract_sha_and_ids', ('tools/verify_contracts.py',)),
    ('source_archive_adversarial', ('tools/test_release_integrity.py',)),
    ('real_project_chat_http_sqlite', ('TESTS/test_r2_project_chat_real_http.py',)),
    ('project_bound_http_e2e', ('TESTS/run_project_bound_e2e.py',)),
    ('generated_application_http_e2e', ('TESTS/run_generated_taskboard_e2e.py',)),
    ('integrated_http_sqlite_e2e', ('TESTS/run_final_e2e.py',)),
    ('safe_rollback', ('TESTS/run_v4_safe_rollback.py',)),
    ('synthetic_shared_ai_boundary', ('TESTS/run_v7_shared_ai_source_boundary.py',)),
    ('w07_w08_real_http_restart', (
        'TESTS/run_v7_w07_w08_real_http_and_restart.py',
        '--product', 'PRODUCT', '--output', '{OUT}/w07_w08_actual.json',
    )),
    ('original_12_job_reconciliation', ('TESTS/reconcile_v22_12_original_tasks.py',)),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_unzip(blob: bytes, target: Path) -> None:
    """Fail closed for ZIP traversal, duplicates, non-regular and symlink members."""
    with zipfile.ZipFile(__import__('io').BytesIO(blob)) as archive:
        members = archive.infolist()
        names = [m.filename for m in members]
        if len(names) != len(set(names)) or archive.testzip() is not None:
            raise ValueError('HOLD_PORTABLE_ZIP_DUPLICATE_OR_CRC')
        for member in members:
            name = member.filename
            rel = PurePosixPath(name)
            if (rel.is_absolute() or '\\' in name or
                    not name.startswith('ULMI_H1/') or
                    '..' in rel.parts or not rel.parts[-1]):
                raise ValueError('HOLD_PORTABLE_ZIP_PATH:' + name)
            mode = member.external_attr >> 16
            file_type = mode & 0o170000
            if file_type not in (0, 0o100000) or name.endswith('/'):
                raise ValueError('HOLD_PORTABLE_ZIP_NONREGULAR:' + name)
            if (target / name).resolve().is_relative_to(target.resolve()) is False:
                raise ValueError('HOLD_PORTABLE_ZIP_PATH_ESCAPE:' + name)
        for member in members:
            destination = target / member.filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.read(member))


def runner_selftest():
    import io
    tests = []

    def z(data, attrs=None):
        b = io.BytesIO()
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='Duplicate name:.*', category=UserWarning)
            with zipfile.ZipFile(b, 'w') as archive:
                for name, contents in data:
                    info = zipfile.ZipInfo(name)
                    info.external_attr = (attrs.get(name, 0o100644) if attrs else 0o100644) << 16
                    archive.writestr(info, contents)
        return b.getvalue()

    with tempfile.TemporaryDirectory(prefix='ulmi-ci-guard-') as d:
        root = Path(d)
        safe_unzip(z([('ULMI_H1/hello.txt', b'ok')]), root)
        tests.append(('regular_archive', (root/'ULMI_H1'/'hello.txt').read_bytes() == b'ok'))
        for label, rows, attrs in (
            ('path_traversal', [('ULMI_H1/../../outside.txt', b'bad')], None),
            ('duplicate_path', [('ULMI_H1/d.txt', b'1'), ('ULMI_H1/d.txt', b'2')], None),
            ('symlink', [('ULMI_H1/link', b'dest')], {'ULMI_H1/link': 0o120777}),
        ):
            try:
                safe_unzip(z(rows, attrs), root)
                tests.append((label, False))
            except ValueError:
                tests.append((label, True))
    return tests


def local_git_binding(root: Path, expected_commit: str) -> str:
    """Bind source to HEAD only inside a clean, real git checkout."""
    for candidate in (root, *root.parents):
        if not (candidate / '.git').exists():
            continue
        try:
            head = subprocess.run(['git', '-C', str(candidate), 'rev-parse', 'HEAD'],
                                  capture_output=True, text=True, timeout=8, check=True).stdout.strip()
            rel = root.relative_to(candidate).as_posix()
            dirty = subprocess.run(['git', '-C', str(candidate), 'status', '--porcelain',
                                    '--untracked-files=all', '--', rel], capture_output=True,
                                   text=True, timeout=8, check=True).stdout
            if head == expected_commit and not dirty.strip():
                return 'EXACT_LOCAL_GIT_HEAD_AND_CLEAN_PRODUCT_TREE'
            return 'HOLD_LOCAL_GIT_COMMIT_OR_WORKTREE_DRIFT'
        except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return 'HOLD_LOCAL_GIT_IDENTITY_ERROR'
    return 'REFERENCE_ONLY_NEEDS_REMOTE_EXACT_BLOB_COMPARISON'


def execute(output: Path, seconds: int, commit: str, *, browser: bool = False):
    output.mkdir(parents=True, exist_ok=True)
    git_binding = local_git_binding(ROOT, commit)
    guard = runner_selftest()
    if not all(ok for _, ok in guard):
        raise RuntimeError('HOLD_PORTABLE_RUNNER_SELFTEST')

    source1, records1, manifest = build_release.make(ROOT)
    source2, records2, _ = build_release.make(ROOT)
    if source1 != source2 or len(records1) != len(records2):
        raise RuntimeError('HOLD_NONDETERMINISTIC_SOURCE_RELEASE')
    validated = build_release.verify(source1)
    package_path = output / 'ULMI_H1_PORTABLE_TECHNICAL_CANDIDATE.zip'
    package_path.write_bytes(source1)
    results = []
    with tempfile.TemporaryDirectory(prefix='ulmi-ci-isolated-') as temp:
        safe_unzip(source1, Path(temp))
        isolated = Path(temp) / 'ULMI_H1'
        evidence = output / 'test_logs'
        evidence.mkdir(exist_ok=True)
        for i, (identity, argv) in enumerate(TESTS, start=1):
            real_argv = [segment.replace('{OUT}', str(output)) for segment in argv]
            cmd = [sys.executable, '-B', *real_argv]
            start = time.monotonic()
            try:
                p = subprocess.run(cmd, cwd=isolated, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                                   stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True,
                                   timeout=seconds, errors='replace')
                code, log = p.returncode, p.stdout
            except subprocess.TimeoutExpired as exc:
                code = 124
                chunk = exc.stdout or b''
                log = (chunk.decode('utf-8', 'replace') if isinstance(chunk, bytes) else chunk) + '\nHOLD_TEST_TIMEOUT'
            data = log.encode('utf-8')
            path = evidence / f'{i:02d}_{identity}.log'
            path.write_bytes(data)
            results.append({'id': identity, 'exit_code': code,
                            'state': 'PASS_SCOPED_LOCAL' if code == 0 else 'HOLD',
                            'elapsed_seconds': round(time.monotonic()-start, 3),
                            'log_sha256': sha256(data), 'log_file': str(path.relative_to(output))})
            print(('PASS' if code == 0 else 'HOLD'), identity, 'exit', code, flush=True)
        browser_state = 'NOT_TESTED'
        if browser:
            if not (isolated / 'tools' / 'browser_h1_e2e.py').exists():
                browser_state = 'HOLD_BROWSER_SCRIPT_ABSENT'
            else:
                cmd = [sys.executable, '-B', 'tools/browser_h1_e2e.py']
                start = time.monotonic()
                try:
                    b = subprocess.run(cmd, cwd=isolated, stdin=subprocess.DEVNULL, capture_output=True,
                                       text=True, timeout=seconds, errors='replace')
                    code, log = b.returncode, b.stdout + '\n'+b.stderr
                except subprocess.TimeoutExpired as exc:
                    code, log = 124, 'HOLD_BROWSER_TIMEOUT'
                data = log.encode('utf-8')
                (evidence / 'browser.log').write_bytes(data)
                browser_state = 'PASS_SCOPED_BROWSER' if code == 0 else 'HOLD_BROWSER_ENVIRONMENT_OR_TEST'
                results.append({'id':'real_browser_e2e','exit_code':code,'state':browser_state,
                                'elapsed_seconds':round(time.monotonic()-start,3),
                                'log_sha256':sha256(data),'log_file':'test_logs/browser.log'})

    passed = sum(row['exit_code'] == 0 for row in results)
    result = {
        'schema': 'enguru.ulmi-h1.portable-ci-receipt/v1',
        'emir_id': EMIR_ID,
        'execution_mode': 'PORTABLE_ISOLATED_NO_GITHUB_ACTIONS',
        'github_repository': 'engurulabory/Engurulaboratuvari',
        'github_commit_reference': commit,
        'github_commit_binding': git_binding,
        'github_actions_acceptance': 'HOLD_PLATFORM_RUNNER_UNAVAILABLE',
        'github_actions_bypass_method': 'ALTERNATE_INDEPENDENT_RUNNER_NOT_PLATFORM_OVERRIDE',
        'no_additional_paid_service_started_by_runner': True,
        'billing_or_entitlement_changed': False,
        'finance_cost_verification': 'NOT_TESTED_OUTSIDE_RUNNER_SCOPE',
        'original_v22_formal_acceptance': '0/12 HOLD',
        'original_jobs_01_11_technical_closeout': 'HOLD',
        'owner_acceptance': 'NOT_TESTED',
        'independent_donecheck': 'NOT_TESTED',
        'h2_mac_osi': 'PARKED',
        'real_qwen': 'NOT_TESTED',
        'browser': browser_state,
        'source_zip_sha256': sha256(source1),
        'source_file_count': len(records1),
        'release_manifest_sha256': sha256(manifest),
        'release_manifest_members': len(validated['files']),
        'runner_selftests': [{'id': name, 'pass': result} for name, result in guard],
        'python': platform.python_version(),
        'platform': platform.platform(),
        'passed': passed,
        'total': len(results),
        'suites': results,
        'result': 'PASS_SCOPED_LOCAL_EXTERNAL_CI' if passed == len(results) else 'HOLD',
    }
    target = output / 'ULMI_H1_PORTABLE_CI_RECEIPT.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print('PORTABLE_CI', result['result'], f'{passed}/{len(results)}', flush=True)
    print('RECEIPT', target, flush=True)
    print('ZIP_SHA256', result['source_zip_sha256'], flush=True)
    return 0 if passed == len(results) else 1


def main():
    p = argparse.ArgumentParser(description='ULMi H1 portable zero-new-paid-service regression runner')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--timeout', type=int, default=100)
    p.add_argument('--git-commit-reference', default=BASELINE_COMMIT)
    p.add_argument('--browser', action='store_true', help='Only on a permitted real browser runtime')
    args = p.parse_args()
    if args.timeout < 5 or args.timeout > 900:
        p.error('--timeout must be 5..900 seconds')
    if not re.fullmatch('[0-9a-f]{40}', args.git_commit_reference):
        p.error('reference must be a full git commit SHA')
    return execute(args.output, args.timeout, args.git_commit_reference, browser=args.browser)


if __name__ == '__main__':
    raise SystemExit(main())
