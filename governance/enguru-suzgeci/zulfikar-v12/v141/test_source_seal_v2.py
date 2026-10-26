"""Adversarial acceptance tests for current-source source seal (no real owner assertion)."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from verify_github_source_seal_v2 import verify, PREFIX

HERE=Path(__file__).resolve().parent
seal=json.loads((HERE/'GITHUB_SOURCE_SHA_SEAL_V2.json').read_text())
root=HERE.parents[3]
original={r['path']:(root/r['path']).read_bytes() for r in seal['stageFiles']}
tracked=set(original)

class SealV2Tests(unittest.TestCase):
    def test_exact_bytes(self):
        self.assertEqual(verify(seal,lambda p:original[p],tracked)['files'],len(original))
    def test_duplicate_path_rejected(self):
        x=copy.deepcopy(seal);x['stageFiles'][-1]['path']=x['stageFiles'][0]['path']
        with self.assertRaises(ValueError):verify(x,lambda p:original[p],tracked)
    def test_file_byte_tampering_rejected(self):
        source=PREFIX+'dom/engine.py'
        with self.assertRaisesRegex(ValueError,'SEAL_SOURCE_DRIFT_HOLD'):
            verify(seal,lambda p:original[p]+b'bad' if p==source else original[p],tracked)
    def test_fake_approval_rejected(self):
        x=copy.deepcopy(seal);x['productVerifiedFinish']='PASS'
        with self.assertRaisesRegex(ValueError,'SEAL_AUTHORITY_HOLD'):
            verify(x,lambda p:original[p],tracked)
    def test_missing_new_test_rejected(self):
        x=copy.deepcopy(seal);x['stageFiles']=[r for r in x['stageFiles'] if r['path']!=PREFIX+'dom/test_completion_guard.py'];x['expectedSourceFiles']-=1
        with self.assertRaises(ValueError):verify(x,lambda p:original[p],tracked)
    def test_unsealed_new_operational_file_rejected(self):
        with self.assertRaisesRegex(ValueError,'SEAL_NEW_UNCOVERED_OPERATIONAL_SOURCE_HOLD'):
            verify(seal,lambda p:original[p],tracked|{PREFIX+'dom/new_controller.py'})
    def test_invalid_path_rejected(self):
        x=copy.deepcopy(seal);x['stageFiles'][0]['path']=PREFIX+'../secrets'
        with self.assertRaises(ValueError):verify(x,lambda p:original[p],tracked)
    def test_wrong_test_scope_rejected(self):
        x=copy.deepcopy(seal);x['expectedExecutedTests']=177
        with self.assertRaisesRegex(ValueError,'SEAL_TEST_SCOPE_HOLD'):
            verify(x,lambda p:original[p],tracked)

if __name__=='__main__': unittest.main()
