import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from tools.pilive_live_reader_v1 import packet
from tools.pilive_native_app_handoff_v1 import reader_resources,validate_frame,run_command,NativeCommandHold
from unittest.mock import patch
from types import SimpleNamespace
from tools.pilive_reader_entry_v1 import validate
from test_pilive_screen_wire_v1 import native_model

class LiveReaderTests(unittest.TestCase):
    def observation(self):return {'state':'PASS_NATIVE_PORTFOLIO_CAPTURE_ONLY','snapshot':native_model()}
    def frame(self):
        o=self.observation();s=o['snapshot'];return {'schema':'enguru.pilive.visible-frame/v1','windowVisible':True,'readerPacketBase64':base64.b64encode(json.dumps(packet(o)).encode()).decode(),'projectionDigest':s['projectionDigest'],'sourceRevision':s['sourceRevision'],'projectIds':[r['projectId'] for r in s['projects']],'qualifiedCounters':14,'sourceReadAt':s['sourceReadAt'],'adapterBuiltAt':s['adapterBuiltAt'],'uiRenderedAt':'2026-10-26T06:04:00Z','humanAcceptance':'NOT_ASSESSED','verifiedFinish':'HOLD'}
    def test_native_packet_wire_exact_and_trusted_identity(self):
        p=packet(self.observation());raw=base64.b64decode(p['wire']);self.assertEqual(hashlib.sha256(raw).hexdigest(),p['identity']['wireSha256']);self.assertEqual(json.loads(raw)['snapshot']['projects'][10]['done'],0)
    def test_failed_core_or_changed_digest_rejected(self):
        for o in ({'state':'HOLD_CORE_PIN_DRIFT'},self.observation()):
            if 'snapshot' in o:o['snapshot']['projectionDigest']='0'*64
            with self.assertRaises(ValueError):packet(o)
    def test_visible_frame_is_not_human_acceptance(self):
        v=validate_frame(self.frame(),'a'*64);self.assertEqual(v['state'],'PASS_SOURCE_TO_VISIBLE_FRAME_ONLY');self.assertEqual(v['productAcceptance'],'HOLD')
    def test_frame_identity_counter_time_and_authority_attacks_rejected(self):
        for field,value in [('projectionDigest','0'*64),('projectIds',[]),('qualifiedCounters',15),('windowVisible',False),('uiRenderedAt','2000-01-01T00:00:00Z'),('humanAcceptance','ACCEPTED'),('verifiedFinish','VERIFIED')]:
            f=self.frame();f[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_frame(f,'a'*64)
    def test_packaged_reader_resources_pin_every_executed_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve()/'reader'
            pin=reader_resources(Path(__file__).resolve().parents[1],root)
            self.assertEqual(len(validate(root,pin)),6)
            (root/'launch_reader.py').write_text('changed')
            with self.assertRaises(ValueError):validate(root,pin)
    def test_native_command_failure_keeps_private_diagnostic(self):
        failed=SimpleNamespace(returncode=2,stdout='',stderr='specific native compiler diagnostic')
        with patch('tools.pilive_native_app_handoff_v1.subprocess.run',return_value=failed):
            with self.assertRaises(NativeCommandHold) as caught:run_command(['/usr/bin/xcrun','swift','test'])
        self.assertIn('specific native',caught.exception.diagnostic['outputTail'])
        self.assertEqual(caught.exception.diagnostic['visibility'],'PRIVATE_RECEIPT_ONLY')
    def test_reader_manifest_tamper_and_symlink_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();(root/'data.py').write_text('safe')
            raw=json.dumps({'data.py':hashlib.sha256(b'safe').hexdigest()}).encode();(root/'READER_MANIFEST.json').write_bytes(raw);pin=hashlib.sha256(raw).hexdigest()
            validate(root,pin);(root/'data.py').write_text('changed')
            with self.assertRaises(ValueError):validate(root,pin)
            (root/'data.py').unlink();(root/'actual').write_text('safe');(root/'data.py').symlink_to(root/'actual')
            with self.assertRaises(OSError):validate(root,pin)
