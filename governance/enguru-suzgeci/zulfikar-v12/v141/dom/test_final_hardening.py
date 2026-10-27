"""Independent adversarial hardening of the pre-GitHub local scope only."""
import hashlib
import json
import os
from pathlib import Path
import time
import subprocess
import sys
import tempfile
import unittest

from engine import Contract, GATES, LocalJournal, execute


def start_competing_writer(folder):
    ready=Path(folder)/'lock-ready'
    release=Path(folder)/'lock-release'
    helper="""import sys,time,pathlib
sys.path.insert(0,sys.argv[1])
from engine import LocalJournal
j=LocalJournal(pathlib.Path(sys.argv[2]))
ready=pathlib.Path(sys.argv[3])
release=pathlib.Path(sys.argv[4])
with j.writer():
    ready.write_text('LOCK_HELD')
    while not release.exists():
        time.sleep(0.02)
"""
    p=subprocess.Popen([sys.executable,'-B','-c',helper,str(Path(__file__).parent),str(folder),str(ready),str(release)],
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    deadline=time.monotonic()+7
    while not ready.exists() and p.poll() is None and time.monotonic()<deadline:
        time.sleep(0.02)
    if not ready.exists() or ready.read_text()!='LOCK_HELD':
        p.terminate();p.wait(timeout=5)
        raise RuntimeError('LOCK_HELPER_NOT_READY')
    return p,release


class HardenedLoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/'goal.txt'
        self.source.write_text('LOCKED_GOAL',encoding='utf8')
        self.work=self.root/'artifact.json'
        self.work.write_text('{"A":false}',encoding='utf8')
        self.goal=Contract('GOAL-01','Hedef kaybı olmadan işi bitir','T01',('A',),hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.state={'location':str(self.work),'checks':{'A':False}}
        self.journal=LocalJournal(self.root)
        self.calls=[]

    def simulator(self,s,c):
        self.calls.append('SIMULATION')
        return {'valid':True}

    def evaluate(self,s,c):
        self.calls.append('ASSESS')
        content=json.loads(Path(s['location']).read_text())
        return {'A':content['A'] is True and s['checks']['A'] is True}

    def repair(self,s,gaps,c):
        self.calls.append('REPAIR')
        s['checks']['A']=True
        self.work.write_text(json.dumps(s['checks']),encoding='utf8')
        return s

    def real_test(self,s,c):
        self.calls.append('OS_TEST')
        proc=subprocess.run([sys.executable,'-B','-c',
           'import hashlib,sys,pathlib;print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())',
           str(self.work)],capture_output=True,text=True,check=False,timeout=8)
        return {'processObserved':True,'exitCode':proc.returncode,'scope':'LOCAL_DISPOSABLE_PROOF','artifactSha256':proc.stdout.strip(),'artifactPath':str(self.work)}

    def verify(self,s,c,run):
        self.calls.append('INDEPENDENT_TEST_MECHANISM')
        return run['artifactSha256']==hashlib.sha256(self.work.read_bytes()).hexdigest() and json.loads(self.work.read_text())==s['checks']

    def drive(self,**kwargs):
        defaults=dict(contract=self.goal,start_state=self.state,journal=self.journal,
                      simulator=self.simulator,evaluator=self.evaluate,repairer=self.repair,
                      real_tester=self.real_test,independent_verifier=self.verify,
                      source_probe=lambda c:True,max_rounds=2,source_file=self.source)
        defaults.update(kwargs)
        return execute(**defaults)

    def test_39_predecessor_gate_missing_blocks_A01(self):
        self.goal=Contract(self.goal.goal_id,self.goal.goal_text,'A01',self.goal.criteria,self.goal.source_pin)
        r=self.drive()
        self.assertEqual(r['reason'],'PREVIOUS_GATE_AUTHORIZED_ACCEPTANCE_REQUIRED')
        self.assertEqual(self.calls,[])

    def test_40_predecessor_wrong_stage_blocks(self):
        self.goal=Contract(self.goal.goal_id,self.goal.goal_text,'A01',self.goal.criteria,self.goal.source_pin)
        r=self.drive(predecessor_receipt={'stage':'T01','goalId':'GOAL-01','acceptedScore':100,'authorizedScope':True},predecessor_verifier=lambda *_:True)
        self.assertEqual(r['reason'],'PREVIOUS_GATE_AUTHORIZED_ACCEPTANCE_REQUIRED')

    def test_41_predecessor_wrong_goal_blocks(self):
        self.goal=Contract(self.goal.goal_id,self.goal.goal_text,'T02',self.goal.criteria,self.goal.source_pin)
        r=self.drive(predecessor_receipt={'stage':'T01','goalId':'EVIL','acceptedScore':100,'authorizedScope':True},predecessor_verifier=lambda *_:True)
        self.assertEqual(r['reason'],'PREVIOUS_GATE_AUTHORIZED_ACCEPTANCE_REQUIRED')

    def test_42_predecessor_self_claim_without_verifier_blocks(self):
        self.goal=Contract(self.goal.goal_id,self.goal.goal_text,'T02',self.goal.criteria,self.goal.source_pin)
        r=self.drive(predecessor_receipt={'stage':'T01','goalId':'GOAL-01','acceptedScore':100,'authorizedScope':True})
        self.assertEqual(r['reason'],'PREVIOUS_GATE_AUTHORIZED_ACCEPTANCE_REQUIRED')

    def test_43_predecessor_verifier_refuses(self):
        self.goal=Contract(self.goal.goal_id,self.goal.goal_text,'T02',self.goal.criteria,self.goal.source_pin)
        r=self.drive(predecessor_receipt={'stage':'T01','goalId':'GOAL-01','acceptedScore':100,'authorizedScope':True},predecessor_verifier=lambda *_:False)
        self.assertEqual(r['reason'],'PREVIOUS_GATE_AUTHORIZED_ACCEPTANCE_REQUIRED')

    def test_44_mock_external_verifier_still_not_official_pass(self):
        self.goal=Contract(self.goal.goal_id,self.goal.goal_text,'T02',self.goal.criteria,self.goal.source_pin)
        r=self.drive(predecessor_receipt={'stage':'T01','goalId':'GOAL-01','acceptedScore':100,'authorizedScope':True},predecessor_verifier=lambda *_:True)
        self.assertEqual(r['state'],'STAGE_100_CANDIDATE_EXTERNAL_REVIEW_REQUIRED')
        self.assertIsNone(r['acceptedScore'])
        self.assertFalse(r['stagePassIssued'])

    def test_45_forged_source_probe_cannot_bypass_real_bytes(self):
        self.source.write_text('SOURCE_TAMPER')
        r=self.drive(source_probe=lambda _: True)
        self.assertEqual(r['reason'],'ACTUAL_SOURCE_DIGEST_MISMATCH')

    def test_46_missing_source_path_blocks(self):
        self.assertEqual(self.drive(source_file=None)['reason'],'SOURCE_FILE_REQUIRED')

    def test_47_symlinked_source_file_fails_closed(self):
        link=self.root/'fake.txt';link.symlink_to(self.source)
        self.assertTrue(self.drive(source_file=link)['reason'].startswith('SAFE_FAILURE_'))

    def test_48_hardlinked_source_file_fails_closed(self):
        link=self.root/'hard.txt';os.link(self.source,link)
        self.assertTrue(self.drive(source_file=link)['reason'].startswith('SAFE_FAILURE_'))

    def test_49_journal_symlink_fails(self):
        target=self.root/'real';target.write_text('')
        self.journal.path.symlink_to(target)
        with self.assertRaises((OSError,ValueError)):LocalJournal(self.root)

    def test_50_journal_hardlink_fails(self):
        target=self.root/'real';target.write_text('')
        os.link(target,self.journal.path)
        with self.assertRaises(ValueError):LocalJournal(self.root)

    def test_51_incomplete_journal_line_fails(self):
        self.journal.path.write_bytes(b'{"partial":true}')
        with self.assertRaises(ValueError):LocalJournal(self.root)

    def test_52_noncanonical_journal_line_fails(self):
        self.journal.path.write_bytes(b'{}\n')
        with self.assertRaises(ValueError):LocalJournal(self.root)

    def test_53_lockfile_symlink_fails(self):
        target=self.root/'not_safe';target.write_text('')
        self.journal.lock_path.symlink_to(target)
        r=self.drive()
        self.assertTrue(r['reason'].startswith('SAFE_FAILURE_'))

    def test_54_writer_competing_process_rejected(self):
        proc,release=start_competing_writer(self.root)
        try:
            r=self.drive()
            self.assertEqual(r['reason'],'SAFE_FAILURE_ValueError')
            self.assertEqual(self.calls,[])
        finally:
            release.write_text('RELEASE')
            proc.wait(timeout=7)
        self.assertEqual(proc.returncode,0)

    def test_55_real_process_test_and_pinned_checkpoint(self):
        r=self.drive()
        self.assertEqual(r['state'],'STAGE_100_CANDIDATE_EXTERNAL_REVIEW_REQUIRED')
        self.assertEqual(self.calls[:7],['SIMULATION','ASSESS','REPAIR','OS_TEST','INDEPENDENT_TEST_MECHANISM','SIMULATION','ASSESS'])
        self.assertEqual(len(self.journal.events),1)
        self.assertEqual(self.journal.events[0]['payload']['externalAuthority'],False)

    def test_56_local_journal_cannot_issue_owner_pass(self):
        r=self.drive()
        self.assertIsNone(r['acceptedScore'])
        self.assertEqual(r['productVerifiedFinish'],'NOT_ISSUED')

    def test_58_every_successor_gate_rejects_missing_predecessor(self):
        for stage in GATES[1:]:
            with self.subTest(stage=stage):
                self.goal=Contract('GOAL-01','Hedef kaybı olmadan işi bitir',stage,('A',),hashlib.sha256(self.source.read_bytes()).hexdigest())
                self.calls.clear()
                r=self.drive()
                self.assertEqual(r['reason'],'PREVIOUS_GATE_AUTHORIZED_ACCEPTANCE_REQUIRED')
                self.assertEqual(self.calls,[])

    def test_59_after_competitor_releases_lock_runner_can_recover(self):
        proc,release=start_competing_writer(self.root)
        try:
            self.assertEqual(self.drive()['reason'],'SAFE_FAILURE_ValueError')
        finally:
            release.write_text('RELEASE')
            proc.wait(timeout=7)
        self.assertEqual(proc.returncode,0)
        r=self.drive()
        self.assertEqual(r['state'],'STAGE_100_CANDIDATE_EXTERNAL_REVIEW_REQUIRED')

    def test_57_all_eight_gates_unchanged(self):
        self.assertEqual(GATES,('T01','T02','A01','A02','A03','A04','A05','A06'))

if __name__=='__main__':unittest.main(verbosity=2)
