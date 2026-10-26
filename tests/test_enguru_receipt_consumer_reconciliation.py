"""Receipt publication faults through the real helper and consumer entrypoints."""
import contextlib
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
from tools import enguru_evidence_receipt_io as receipts
from tools import enguru_p06_runtime_task_adapter as native
from tools import enguru_steward_operator as steward
from tools import enguru_p06_pilot_handler_adapter as legacy


class ReceiptReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'Enguru/Evidence/MacEngineer'
        self.root.mkdir(parents=True)
        self.dest = self.root/'P06/receipt.json'

    def test_nonfinite_rejected_before_publication(self):
        for v in (float('nan'), float('inf'), -float('inf')):
            with self.assertRaises(ValueError):
                receipts.write_new_json(self.dest, {'value':v}, evidence_root=self.root)
            self.assertFalse(self.dest.exists())

    def test_publication_fault_reconciles_exact_bytes(self):
        real_fsync, real_link = os.fsync, os.link
        linked = [False]
        failed = [False]
        def link(*a, **kw):
            result=real_link(*a, **kw);linked[0]=True;return result
        def fsync(fd):
            if linked[0] and not failed[0] and stat.S_ISDIR(os.fstat(fd).st_mode):
                failed[0]=True;raise OSError('injected after publication')
            return real_fsync(fd)
        with patch.object(receipts.os,'link',side_effect=link), patch.object(receipts.os,'fsync',side_effect=fsync):
            receipts.write_or_reconcile_json(self.dest, {'state':'HOLD'}, evidence_root=self.root)
        self.assertTrue(failed[0]);self.assertEqual(json.loads(self.dest.read_text()),{'state':'HOLD'})
        before=self.dest.read_bytes()
        receipts.write_or_reconcile_json(self.dest, {'state':'HOLD'}, evidence_root=self.root)
        self.assertEqual(before,self.dest.read_bytes())

    def test_different_existing_receipt_never_replaced(self):
        self.dest.parent.mkdir();self.dest.write_text('old bytes')
        with self.assertRaises(OSError):
            receipts.write_or_reconcile_json(self.dest, {'state':'PASS'}, evidence_root=self.root)
        self.assertEqual(self.dest.read_text(),'old bytes')

    def test_symlink_receipt_never_reconciled(self):
        self.dest.parent.mkdir();outside=Path(self.tmp.name)/'sentinel.json';outside.write_text('{}')
        self.dest.symlink_to(outside)
        with self.assertRaises(OSError):
            receipts.write_or_reconcile_json(self.dest, {}, evidence_root=self.root)
        self.assertEqual(outside.read_text(),'{}')

    def test_persistent_durability_failure_stays_hold(self):
        receipts.write_new_json(self.dest, {'state':'HOLD'}, evidence_root=self.root)
        with patch.object(receipts.os,'fsync',side_effect=OSError('persistent')):
            with self.assertRaises(OSError):
                receipts.write_or_reconcile_json(self.dest, {'state':'HOLD'}, evidence_root=self.root)

    def test_native_replay_does_not_execute_again(self):
        task=Path(self.tmp.name)/'task.json';task.write_text('{"WORK_ID":"bounded-test"}')
        with patch.object(Path,'home',return_value=Path(self.tmp.name)), patch.object(native,'githead',return_value='a'*40), patch.object(native,'execute',return_value={'STATE':'PASS','SOURCE_HEAD':'a'*40,'canonicalPilotAccepted':False}) as execute, contextlib.redirect_stdout(io.StringIO()) as log:
            self.assertEqual(native.main([str(task),str(self.dest)]),0)
            before=self.dest.read_bytes()
            self.assertEqual(native.main([str(task),str(self.dest)]),0)
            self.assertEqual(execute.call_count,1)
        self.assertEqual(self.dest.read_bytes(),before)
        self.assertIn('REVALIDATED_NO_NEW_TASK_EXECUTION',log.getvalue())

    def test_native_changed_task_stays_hold_without_execution(self):
        task=Path(self.tmp.name)/'task.json';task.write_text('{"WORK_ID":"first"}')
        with patch.object(Path,'home',return_value=Path(self.tmp.name)), patch.object(native,'githead',return_value='a'*40), patch.object(native,'execute',return_value={'STATE':'PASS','SOURCE_HEAD':'a'*40,'canonicalPilotAccepted':False}) as execute, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(native.main([str(task),str(self.dest)]),0)
            before=self.dest.read_bytes();task.write_text('{"WORK_ID":"changed"}')
            self.assertEqual(native.main([str(task),str(self.dest)]),2)
            self.assertEqual(execute.call_count,1)
            self.assertEqual(before,self.dest.read_bytes())

    def test_steward_and_legacy_use_reconciling_writer(self):
        self.assertIs(steward.write_new_json,receipts.write_or_reconcile_json)
        self.assertIs(legacy.write_new_json,receipts.write_or_reconcile_json)
        with patch.object(Path,'home',return_value=Path(self.tmp.name)):
            steward.atomic_json(self.dest,{'state':'HOLD'})
            steward.atomic_json(self.dest,{'state':'HOLD'})

if __name__=='__main__':unittest.main()
