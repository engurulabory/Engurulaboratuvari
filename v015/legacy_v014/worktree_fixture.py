"""Trusted reviewer implementation of E-P05; disposable fixtures only.

No merge, push, clean, reset or delete operation. On uncertainty, no worktree.
Caller must hold exclusive control of the fixture repo during preflight/create;
this is not a race-proof adapter for a shared production repository.
"""
import re
import subprocess
from pathlib import Path


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True).stdout.strip()


def prepare_worktree(repo, target, expected_sha):
    repo, target = Path(repo).absolute(), Path(target).absolute()
    if not isinstance(expected_sha, str) or not re.fullmatch('[0-9a-f]{40}', expected_sha):
        raise ValueError('EXACT_COMMIT_SHA_REQUIRED')
    if any(p.is_symlink() for p in (repo, *repo.parents, target, *target.parents)):
        raise ValueError('SYMLINK_REJECTED')
    if target.exists() or not target.parent.is_dir():
        raise ValueError('WORKTREE_EXISTS_OR_PARENT_MISSING')
    if repo == target or repo in target.parents:
        raise ValueError('SEPARATE_WORKTREE_REQUIRED')
    if Path(git(repo, 'rev-parse', '--show-toplevel')).resolve() != repo.resolve():
        raise ValueError('EXACT_REPOSITORY_ROOT_REQUIRED')
    if git(repo, 'rev-parse', 'HEAD') != expected_sha:
        raise ValueError('HEAD_DRIFT')
    if git(repo, 'status', '--porcelain=v1', '--untracked-files=all', '--ignored'):
        raise ValueError('DIRTY_OR_IGNORED_ROOT_HOLD')
    git(repo, 'worktree', 'add', '--detach', str(target), expected_sha)
    if git(target, 'rev-parse', 'HEAD') != expected_sha or git(repo, 'rev-parse', 'HEAD') != expected_sha:
        raise ValueError('POST_CREATE_HEAD_DRIFT_HOLD')
    return expected_sha
