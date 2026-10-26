import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/enguru_osi_twin_probe_v1.py'
spec = importlib.util.spec_from_file_location('twin', SCRIPT)
twin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(twin)

class TestTwin(unittest.TestCase):
    def test_missing_repo_hold(self):
        with tempfile.TemporaryDirectory() as td:
            row = twin.git_observation(Path(td)/'missing', 'a'*40)
            self.assertEqual(row['state'], 'HOLD_LOCAL_CHECKOUT_PATH')

    def test_symlink_source_hold(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root/'legit').write_text('text')
            (root/'link').symlink_to(root/'legit')
            self.assertEqual(twin.source_observation(root, ('link',))['link']['state'], 'HOLD_EXACT_SOURCE_READ')

    def test_source_sha(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'test.txt').write_bytes(b'abc')
            value=twin.source_observation(root, ('test.txt',))['test.txt']
            self.assertEqual(value['sha256'], twin.digest(b'abc'))
            self.assertEqual(value['bytes'],3)

    def test_directory_not_running_proof(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(twin.directory_state(Path(td)), 'DIRECTORY_OBSERVED_ONLY')

    def test_receipt_original_and_copy_equal(self):
        with tempfile.TemporaryDirectory() as td:
            home=Path(td); (home/'Desktop').mkdir()
            receipt={'schema': twin.SCHEMA, 'verifiedFinish':'HOLD'}
            original, copied, pin=twin.save(home, receipt)
            self.assertEqual(Path(original).read_bytes(),Path(copied).read_bytes())
            self.assertEqual(twin.digest(Path(original).read_bytes()),pin)

    def test_main_refuses_non_mac(self):
        with patch.object(twin.platform,'system',return_value='Linux'):
            exit_code=twin.main(['--run','--expected-control','a'*40,'--expected-product','b'*40])
            self.assertEqual(exit_code,2)

    def test_missing_app_hold(self):
        self.assertEqual(twin.app_state(Path('/nonexistent_enguru_app_test'))['applicationRunning'],'NOT_MEASURED')

    def test_observation_never_claims_field_finish(self):
        with tempfile.TemporaryDirectory() as td:
            receipt=twin.observe(Path(td),'a'*40,'b'*40)
            self.assertEqual(receipt['verifiedFinish'],'HOLD')
            self.assertEqual(receipt['appLaunches'],0)
            self.assertEqual(receipt['networkRequests'],0)
            self.assertEqual(receipt['canonicalWrites'],0)
            self.assertEqual(receipt['twoViewSnapshotParity'],'HOLD_NOT_MEASURED')

if __name__=='__main__': unittest.main()
