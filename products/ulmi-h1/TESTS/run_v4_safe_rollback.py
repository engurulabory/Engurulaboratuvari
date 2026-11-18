#!/usr/bin/env python3
from __future__ import annotations
import importlib,sys,os,pathlib,tempfile,unittest,uuid,types,hashlib
from unittest.mock import patch
P=pathlib.Path(__file__).resolve().parents[1]/'PRODUCT'
sys.path.insert(0,str(P))
_tmp=tempfile.TemporaryDirectory(prefix='ulmi-v4-safe-rollback-')
os.environ['ENGURU_H1_STATE_HOME']=_tmp.name
import server
server.prepare()

class RollbackFaultSuite(unittest.TestCase):
    def setUp(self):
        self.name='failure_'+uuid.uuid4().hex+'.py'
        self.plan=server.store_plan('Synthetic injected trusted test failure',self.name,server.PY_FIXTURE,'SCOPED_TEMPLATE_PYTHON')
        self.target=server.WORKSPACE/self.name
    def fake_failed_test(self):
        return types.SimpleNamespace(returncode=1,stdout='',stderr='Ran 3 tests in 0.003s\\nFAILED')
    def test_01_failure_does_not_leave_unauthorized_file(self):
        with patch.object(server.subprocess,'run',return_value=self.fake_failed_test()):
            with self.assertRaisesRegex(RuntimeError,'fonksiyonel testten geçemedi'):
                server.execute(self.plan['task_id'])
        self.assertFalse(self.target.exists(),'RED: test failure left a real filesystem side effect')
        task=server.get_task(self.plan['task_id'])
        self.assertEqual(task['status'],'HOLD')
        self.assertNotEqual(task.get('receipt'),{'readback':'PASS'})
    def test_02_hijacked_file_preserved_for_manual_reconciliation(self):
        def adversarial_test(*a,**kw):
            self.target.write_text('OTHER_OWNER_CONTENT',encoding='utf-8')
            return self.fake_failed_test()
        with patch.object(server.subprocess,'run',side_effect=adversarial_test):
            with self.assertRaises(RuntimeError):server.execute(self.plan['task_id'])
        self.assertEqual(self.target.read_text(),'OTHER_OWNER_CONTENT')
        task=server.get_task(self.plan['task_id'])
        self.assertEqual(task['status'],'HOLD')
        self.assertIn('HOLD_ROLLBACK_RECONCILE',task['error'])
    def test_03_failed_task_cannot_reexecute_itself(self):
        with patch.object(server.subprocess,'run',return_value=self.fake_failed_test()):
            with self.assertRaises(RuntimeError):server.execute(self.plan['task_id'])
        with self.assertRaises(ValueError):server.execute(self.plan['task_id'])
        self.assertFalse(self.target.exists())
    def test_04_success_keeps_file_and_verifies_sha(self):
        result=server.execute(self.plan['task_id'])
        self.assertEqual(result['status'],'PASS_SCOPED')
        self.assertTrue(self.target.is_file())
        self.assertEqual(hashlib.sha256(self.target.read_bytes()).hexdigest(),result['receipt']['output_sha256'])
        self.assertEqual(server.verify_written_task(self.plan['task_id'])['status'],'PASS_SCOPED_READBACK')
    def test_05_preexisting_file_never_deleted_or_overwritten(self):
        self.target.write_text('KEEP_ME',encoding='utf-8')
        with self.assertRaises(FileExistsError):server.execute(self.plan['task_id'])
        self.assertEqual(self.target.read_text(),'KEEP_ME')
        self.assertEqual(server.get_task(self.plan['task_id'])['status'],'HOLD')
    def test_06_rollback_is_not_owner_or_donecheck_grant(self):
        self.assertEqual(server.TASKBOARD_TEMPLATE_PIN,server.sha(server.TASKBOARD_FIXTURE.encode('utf-8')))
        self.assertNotIn('owner_final',server.execute.__doc__ or '')

if __name__=='__main__':
    unittest.main(verbosity=2)
