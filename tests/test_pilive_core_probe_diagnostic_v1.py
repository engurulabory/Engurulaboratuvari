import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from tools import pilive_core_adapter_probe_v1 as p

class ProbeDiagnosticTests(unittest.TestCase):
    def diagnostic(self,reason):
        pins=[{'path':k,'sha256':v,'match':True} for k,v in p.safe.CORE_PINS.items()]
        data={'registry':{'projects':{'private-project':{'projectId':'PRIVATE_ID'}}},'facts':{'p02':{}}}
        proc=SimpleNamespace(returncode=0,stdout=json.dumps(data))
        with patch.object(p.safe,'core_pin_check',return_value=pins),patch.object(p,'head',return_value='a'*40),patch.object(p.subprocess,'run',return_value=proc),patch.object(p.adapter,'build',side_effect=p.adapter.Hold(reason)):
            return p.native_read(Path('/test-owned-home'),Path('/test-owned-temp'))
    def test_exact_hold_reason_retained_without_acceptance(self):
        r=self.diagnostic('HOLD_PROJECT_ID')
        self.assertEqual(r['state'],'HOLD_ADAPTER_VALIDATION');self.assertEqual(r['reason'],'HOLD_PROJECT_ID')
        self.assertEqual(r['verifiedFinish'],'HOLD');self.assertIn('coreFacts',r)
        self.assertEqual(r['before'],r['after'])
    def test_arbitrary_exception_text_not_exported_as_reason(self):
        r=self.diagnostic('private path /Users/example')
        self.assertEqual(r['reason'],'HOLD_UNCLASSIFIED_VALIDATION')
    def test_pin_drift_still_prevents_execution(self):
        with patch.object(p.safe,'core_pin_check',return_value=[{'match':False}]),patch.object(p.subprocess,'run') as run:
            r=p.native_read(Path('/test-owned-home'),Path('/test-owned-temp'))
        run.assert_not_called();self.assertFalse(r['executed'])

if __name__=='__main__':unittest.main()
