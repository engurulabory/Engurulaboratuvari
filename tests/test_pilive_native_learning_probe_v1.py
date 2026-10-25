import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from tools import pilive_native_learning_probe_v1 as p

class NativeProbeBoundaryTests(unittest.TestCase):
    def test_regular_file_and_symlink_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'ok').write_bytes(b'x');(root/'link').symlink_to(root/'ok')
            self.assertEqual(p.read_file(root,'ok'),b'x')
            with self.assertRaises(OSError):p.read_file(root,'link')
            with self.assertRaises(ValueError):p.read_file(root,'../outside')
    def test_fifo_and_size_are_bounded(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);os.mkfifo(root/'fifo');(root/'large').write_bytes(b'xx')
            with self.assertRaises(ValueError):p.read_file(root,'fifo')
            with self.assertRaises(ValueError):p.read_file(root,'large',1)
    def test_original_copy_byte_pin(self):
        with tempfile.TemporaryDirectory() as d,patch.dict(p.RECEIPT_PINS,{'unit.json':p.digest(b'{}')},clear=True):
            root=Path(d)/'Desktop';(root/'AudiV13').mkdir(parents=True)
            (root/'AudiV13/unit.json').write_bytes(b'{}');(root/'unit.json').write_bytes(b'{}')
            self.assertEqual(p.receipt_pairs(d)[0]['state'],'PASS_ORIGINAL_COPY_PIN')
            (root/'unit.json').write_bytes(b'{ }')
            self.assertEqual(p.receipt_pairs(d)[0]['state'],'HOLD_RECEIPT_COPY')
    def test_native_inventory_does_not_execute_source(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'Enguru/Projects/Engurulaboratuvari/tools';root.mkdir(parents=True)
            (root/'enguru_muhendislik_kasi.py').write_text("raise RuntimeError('source must stay unexecuted')\nTASK_ID='LOCAL_SCOPE'\n")
            rows=p.native_muscle_inventory(d);observed=[r for r in rows if r['state']=='OBSERVED']
            self.assertEqual(len(observed),1);self.assertEqual(observed[0]['declaredScopes']['TASK_ID'],'LOCAL_SCOPE')
            self.assertTrue(any(r['state']=='MISSING_IN_EXACT_SCOPE' for r in rows))
    def test_non_mac_gate_precedes_archive_read(self):
        with patch.object(p.platform,'system',return_value='Linux'):
            with self.assertRaisesRegex(ValueError,'HOLD_MAC_REQUIRED'):p.run_package('/absent.zip')
    def test_package_payload_hash_before_execution(self):
        with tempfile.TemporaryDirectory() as d:
            zpath=Path(d)/'unit.pyz'
            with zipfile.ZipFile(zpath,'w') as z:
                z.writestr('MANIFEST.json',json.dumps({'files':{'tools/unit.py':'a'*64},'sourceCommit':'a'*40}))
                z.writestr('payload/tools/unit.py',b'raise RuntimeError()')
            with self.assertRaisesRegex(ValueError,'PACKAGE_SOURCE_SHA'):
                p.run_package(zpath,home=d,allow_non_mac=True,execute_core=False)

if __name__=='__main__':unittest.main()
