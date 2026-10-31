import dataclasses
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from enguru_core.contracts import Plan,Rejected,strict_json,progress,remaining,repair_gate,encoded,digest
from enguru_core.storage import Ledger,write_new,read_private
from enguru_core.kernel import Kernel,recognize
from enguru_core.broker import fixture_pin,RELEASE
from enguru_core.security import tool_proposal
from enguru_core.roles import local_http


class FixtureRoles:
    kind='TEST_STUB_NOT_LLM'
    def propose(self,role,text,plan):
        return {'operation':'plan_unique_jobs_repair' if role=='manager' else 'apply_reviewed_unique_jobs_patch',
                'plan_sha256':plan.sha}


class Setup(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'profile'
        self.k=Kernel(self.root,FixtureRoles());self.addCleanup(self.k.close)
        self.p=self.k.plan('task-A')


class Positive(Setup):
    def test_natural_command_to_real_red_green_independent_test_and_projection(self):
        result=self.k.execute('task-A','unique_jobs fonksiyonunu sıra koruyacak biçimde düzelt')
        self.assertEqual(result['state'],'DONE');self.assertEqual(result['completion_percent'],100)
        self.assertEqual(result['donecheck'],'PASS_SCOPED_PILOT');self.assertEqual(result['product_verified_finish'],'HOLD')
        receipt=json.loads(Path(result['evidence']).read_text())['operation']
        self.assertNotEqual(receipt['red']['exit_code'],0);self.assertEqual(receipt['green']['exit_code'],0)
        self.assertIn('Ran 4 tests',receipt['green']['stderr'])
        self.assertEqual(self.k.ledger.db.execute('SELECT count(*) FROM proofs').fetchone()[0],1)
    def test_same_command_stable_no_reexecution(self):
        a=self.k.execute('task-A','unique_jobs sıra onarımı')
        before=Path(a['evidence']).read_bytes()
        b=self.k.execute('task-A','unique_jobs sıra onarımı')
        self.assertEqual(a,b);self.assertEqual(Path(a['evidence']).read_bytes(),before)
    def test_pause_resume_controls_queue_without_replay(self):
        self.k.ledger.control(True)
        with self.assertRaises(Rejected):self.k.execute('task-A','unique_jobs sıra onarımı')
        self.assertEqual(self.k.ledger.db.execute('SELECT state FROM jobs').fetchone()[0],'READY')
        self.k.ledger.control(False)
        self.assertEqual(self.k.execute('task-A','unique_jobs sıra onarımı')['state'],'DONE')
    def test_readonly_snapshot_does_not_run_tools(self):
        from unittest.mock import patch
        self.k.execute('task-A','unique_jobs sıra onarımı')
        with patch('enguru_core.broker.run_tests',side_effect=AssertionError('no tool in readonly projection')):
            self.assertEqual(self.k.snapshot()['completion_percent'],100)


class Adversarial(Setup):
    def test_wrong_source_sha_rejected(self):
        p=dataclasses.replace(self.p,source='0'*64)
        with self.assertRaisesRegex(Rejected,'SOURCE_SHA'):self.k.broker.execute(p,'task-A')
        self.assertFalse((self.root/'jobs'/digest('task-A')).exists())
    def test_wrong_expired_and_forged_authority(self):
        a=self.k.authority
        expired=a.issue_local_pilot(self.p,self.root,now=1)
        with self.assertRaisesRegex(Rejected,'EXPIRED'):a.validate(expired,self.p,self.root,now=9999)
        g=a.issue_local_pilot(self.p,self.root)
        for field,val in [('task','other'),('source','x'),('scope','other'),('action','shell'),('resource','/etc')]:
            q=json.loads(json.dumps(g));q['grant'][field]=val;q['signature']=a.sign(q['grant'])
            with self.subTest(field=field),self.assertRaisesRegex(Rejected,'BINDING'):a.validate(q,self.p,self.root)
        g['signature']='0'*64
        with self.assertRaisesRegex(Rejected,'SIGNATURE'):a.validate(g,self.p,self.root)
    def test_conflicting_repeat_preserves_original(self):
        plan=dataclasses.asdict(self.p);self.k.ledger.submit('A',{'n':1},plan)
        with self.assertRaisesRegex(Rejected,'CONFLICT'):self.k.ledger.submit('A',{'n':2},plan)
        self.assertEqual(json.loads(self.k.ledger.db.execute('SELECT payload FROM jobs').fetchone()[0]),{'n':1})
    def test_unknown_external_effect_does_not_replay(self):
        self.k.ledger.submit('task-A',{'text':'unique_jobs sıra onarımı','task_kind':'unique_jobs_repair'},dataclasses.asdict(self.p))
        self.k.ledger.claim('task-A','nonce')
        self.assertEqual(self.k.recover(),1)
        with self.assertRaisesRegex(Rejected,'RECONCILE'):self.k.execute('task-A','unique_jobs sıra onarımı')
        row=self.k.ledger.db.execute('SELECT state,effect FROM jobs').fetchone()
        self.assertEqual(tuple(row),('HOLD','UNKNOWN'))
    def test_double_active_claim_real_two_connections(self):
        self.k.ledger.submit('A',{},{});self.k.ledger.submit('B',{},{});barrier=threading.Barrier(2)
        results=[];errors=[]
        def worker(cid):
            try:
                l=Ledger(self.root)
                try:barrier.wait(timeout=5);results.append(l.claim(cid,cid))
                finally:l.close()
            except Exception as e:errors.append(str(e))
        ts=[threading.Thread(target=worker,args=(cid,)) for cid in ['A','B']]
        for t in ts:t.start()
        for t in ts:t.join(10)
        self.assertFalse(any(t.is_alive() for t in ts));self.assertEqual(errors,[])
        self.assertEqual(sum(results),1)
        self.assertEqual(self.k.ledger.db.execute("SELECT count(*) FROM jobs WHERE state='RUNNING'").fetchone()[0],1)
    def test_weights_types_unknown_and_wrong_percentage(self):
        for blocks in [(('A',10100,()),),(('A',True,()),),(('A',10000,('A',)),)]:
            with self.subTest(blocks=blocks),self.assertRaises(Rejected):dataclasses.replace(self.p,blocks=blocks).validate()
        with self.assertRaises(Rejected):progress(self.p,['B5'])
        with self.assertRaises(Rejected):progress(self.p,['B1','B1'])
        for value in [True,-1,101,15.0]:
            with self.subTest(value=value),self.assertRaises(Rejected):remaining(value)
        for n in range(101):self.assertEqual(remaining(n),100-n)
        self.assertEqual(progress(self.p,[])['completion_percent'],0)
    def test_fake_success_receipt_rejected(self):
        with self.assertRaises(Rejected):self.k.verifier.verify({'operation':{'green':{'exit_code':0}},'signature':'PASS'},self.p,'A')
    def test_model_raw_shell_and_path_injection_rejected(self):
        for text in ['unique_jobs sıra ../outside','unique_jobs sıra sudo rm -rf /','unique_jobs sıra prompt injection','normal unrelated task']:
            with self.subTest(text=text),self.assertRaises(Rejected):recognize(text)
        for candidate in [{'operation':'shell','plan_sha256':self.p.sha},
                          {'operation':'apply_reviewed_unique_jobs_patch','plan_sha256':'x'},
                          {'operation':'apply_reviewed_unique_jobs_patch','plan_sha256':self.p.sha,'code':'arbitrary'}]:
            with self.assertRaises(Rejected):tool_proposal(candidate,self.p)
    def test_symlink_and_hardlink_rejected(self):
        p=self.root/'link';p.symlink_to(self.root/'authority.key')
        with self.assertRaises(OSError):read_private(p)
        p.unlink();os.link(self.root/'authority.key',p)
        with self.assertRaises(Rejected):read_private(p)
    def test_evidence_free_done_rejected(self):
        self.k.ledger.submit('task-A',{},dataclasses.asdict(self.p))
        self.k.ledger.db.execute("UPDATE jobs SET state='DONE' WHERE command='task-A'")
        with self.assertRaisesRegex(Rejected,'EVIDENCE_REQUIRED'):self.k.snapshot()
    def test_source_tamper_after_done_rejected(self):
        r=self.k.execute('task-A','unique_jobs sıra onarımı')
        (Path(r['evidence']).parent/'unique_jobs.py').write_text('tampered')
        with self.assertRaisesRegex(Rejected,'OUTPUT_DRIFT'):self.k.snapshot()
    def test_event_tampering_update_and_delete_denied(self):
        self.k.ledger.submit('A',{}, {})
        for sql in ['UPDATE events SET hash="x"','DELETE FROM events']:
            with self.assertRaises(sqlite3.IntegrityError):self.k.ledger.db.execute(sql)
        self.assertEqual(len(self.k.ledger.audit_chain()),64)
    def test_repair_budget_and_duplicate_json_and_endpoint(self):
        for h in [[1,2,3],[1,1]]:
            with self.assertRaises(Rejected):repair_gate(h)
        for raw in ['{"state":1,"state":2}','NaN']:
            with self.assertRaises(Rejected):strict_json(raw)
        for path in ['/api/pull','http://outside','/api/tags']:
            with self.assertRaises(Rejected):local_http(path,{'x':1})
    def test_actual_kill_and_restart_no_replay(self):
        script='''import sys,time\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\nfrom enguru_core.storage import Ledger\nl=Ledger(Path(sys.argv[2]));l.submit('crash',{},{});l.claim('crash','n');print('CLAIMED',flush=True);time.sleep(60)'''
        p=subprocess.Popen([sys.executable,'-I','-c',script,str(RELEASE),str(self.root/'crash')],stdout=subprocess.PIPE,text=True)
        try:
            self.assertEqual(p.stdout.readline().strip(),'CLAIMED')
            p.kill();p.wait(timeout=5)
            self.assertEqual(p.returncode,-signal.SIGKILL)
            l=Ledger(self.root/'crash')
            try:
                self.assertEqual(l.recover(),1)
                self.assertFalse(l.claim('crash','new'))
                self.assertEqual(l.db.execute('SELECT effect FROM jobs').fetchone()[0],'UNKNOWN')
            finally:l.close()
        finally:
            if p.poll() is None:p.kill();p.wait()
            p.stdout.close()
