import subprocess
import tempfile
from pathlib import Path
import unittest
from worktree_fixture import git, prepare_worktree


class WorktreeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root/'root'
        self.repo.mkdir()
        git(self.repo, 'init', '--initial-branch=fixture')
        git(self.repo, 'config', 'user.name', 'Fixture')
        git(self.repo, 'config', 'user.email', 'fixture@example.invalid')
        (self.repo/'source.txt').write_text('original')
        git(self.repo, 'add', 'source.txt')
        git(self.repo, 'commit', '-m', 'fixture source')
        self.sha = git(self.repo, 'rev-parse', 'HEAD')
        self.target = self.root/'worktree'
    def test_clean_exact_sha_creates_detached_worktree_preserves_root(self):
        self.assertEqual(prepare_worktree(self.repo,self.target,self.sha), self.sha)
        detached = subprocess.run(['git','-C',str(self.target),'symbolic-ref','-q','HEAD'],
                                  capture_output=True).returncode
        self.assertEqual(detached,1)
        (self.target/'source.txt').write_text('candidate')
        self.assertEqual((self.repo/'source.txt').read_text(),'original')
        self.assertEqual(git(self.repo,'status','--porcelain=v1'),'')
        self.assertEqual(git(self.repo,'rev-parse','HEAD'),self.sha)
    def test_wrong_sha_holds_without_worktree(self):
        with self.assertRaises(ValueError): prepare_worktree(self.repo,self.target,'0'*40)
        self.assertFalse(self.target.exists())
    def test_untracked_staged_deleted_modified_ignored_all_hold(self):
        cases = ['untracked','staged','deleted','modified','ignored']
        for case in cases:
            with self.subTest(case=case):
                if case=='untracked': (self.repo/'extra').write_text('x')
                if case=='staged':
                    (self.repo/'extra').write_text('x')
                    git(self.repo,'add','extra')
                if case=='deleted': (self.repo/'source.txt').unlink()
                if case=='modified': (self.repo/'source.txt').write_text('changed')
                if case=='ignored':
                    (self.repo/'.git/info/exclude').write_text('ignored\n')
                    (self.repo/'ignored').write_text('x')
                before = git(self.repo,'status','--porcelain=v1','--untracked-files=all','--ignored')
                with self.assertRaises(ValueError): prepare_worktree(self.repo,self.target,self.sha)
                self.assertEqual(git(self.repo,'status','--porcelain=v1','--untracked-files=all','--ignored'),before)
                self.assertFalse(self.target.exists())
                # Test fixture cleanup only; implementation never runs these commands.
                if (self.repo/'extra').exists():
                    if case=='staged': git(self.repo,'restore','--staged','extra')
                    (self.repo/'extra').unlink()
                (self.repo/'source.txt').write_text('original')
    def test_existing_target_symlink_and_bad_sha_rejected(self):
        self.target.mkdir()
        with self.assertRaises(ValueError): prepare_worktree(self.repo,self.target,self.sha)
        self.target.rmdir()
        self.target.symlink_to(self.repo)
        with self.assertRaises(ValueError): prepare_worktree(self.repo,self.target,self.sha)
        with self.assertRaises(ValueError): prepare_worktree(self.repo,self.target,'HEAD; command')
