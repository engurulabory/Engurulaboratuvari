import copy
import hashlib
import json
from pathlib import Path
import unittest
from tools import pilive_core_snapshot_adapter_v1 as adapter
from tools.pilive_screen_wire_v1 import export_wire

def native_model():
    d=json.loads((Path(__file__).parent/'fixtures/pilive_native_portfolio_review_v1.json').read_text())
    return adapter.build_portfolio(d['registry'],d['facts'],**d['identity'])

class ScreenWireTests(unittest.TestCase):
    def test_lossless_native_portfolio_and_digest(self):
        s=native_model();wire=json.loads(export_wire(s))
        self.assertEqual(wire['snapshot'],s)
        self.assertEqual(hashlib.sha256(wire['canonicalProjection'].encode()).hexdigest(),s['projectionDigest'])
    def test_changed_counter_or_identity_cannot_use_old_digest(self):
        for field,value in [('done',True),('projectId','UNKNOWN')]:
            s=copy.deepcopy(native_model());s['projects'][0][field]=value
            with self.assertRaises(adapter.Hold):export_wire(s)
    def test_repeat_export_is_deterministic_and_preserves_hold(self):
        s=native_model();self.assertEqual(export_wire(s),export_wire(s))
        row=next(r for r in json.loads(export_wire(s))['snapshot']['projects'] if r['key']=='visual-cockpit-premium-v1')
        self.assertIsNone(row['percent']);self.assertEqual(row['officialAcceptance'],'HOLD')
