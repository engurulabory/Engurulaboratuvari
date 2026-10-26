import tempfile,unittest
from pathlib import Path
from tools.enguru_pre_execution_simulation import predict,reconcile
class PredictionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'script.py'
    def test_valid_syntax_forecast_only(self):
        self.path.write_text('x = 1\n')
        p=predict(self.path,'python',0,'PASS')
        self.assertEqual(p['state'],'READY_FOR_FIELD')
        self.assertFalse(p['realExecutionPerformed'])
    def test_invalid_syntax_holds(self):
        self.path.write_text('def broken(:\n')
        self.assertEqual(predict(self.path,'python',0,'PASS')['state'],'HOLD')
    def test_matching_observation(self):
        self.path.write_text('print(1)\n')
        p=predict(self.path,'python',0,'PASS')
        self.assertEqual(reconcile(p,'STATE=PASS\n',0)['state'],'MATCH')
    def test_missing_observed_state_mismatch(self):
        self.path.write_text('print(1)\n')
        p=predict(self.path,'python',0,'PASS')
        self.assertEqual(reconcile(p,'ok\n',0)['state'],'MISMATCH')
    def test_wrong_rc_mismatch(self):
        self.path.write_text('print(1)\n')
        p=predict(self.path,'python',0,'PASS')
        self.assertEqual(reconcile(p,'STATE=PASS\n',2)['state'],'MISMATCH')
