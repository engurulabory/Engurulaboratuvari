import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

class Packaging(unittest.TestCase):
    def test_evidence_allowlist_never_exports_key_or_database(self):
        path=Path(__file__).resolve().parents[1]/'tools/mac_evidence.py'
        spec=importlib.util.spec_from_file_location('mac_evidence',path)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'profile/jobs/a').mkdir(parents=True)
            (root/'profile/authority.key').write_text('SECRET')
            (root/'profile/tasks.sqlite').write_text('PRIVATE')
            (root/'MAC_INSTALL_RECEIPT.json').write_text('{"compile":"HOLD"}')
            (root/'profile/jobs/a/operation.json').write_text('{}')
            with patch.object(m,'ROOT',root):p=m.collect()
            with zipfile.ZipFile(p) as z:
                self.assertEqual(set(z.namelist()),{'MAC_INSTALL_RECEIPT.json','profile/jobs/a/operation.json','EVIDENCE_MANIFEST.json'})
                self.assertIsNone(z.testzip())
                self.assertFalse(json.loads(z.read('EVIDENCE_MANIFEST.json'))['private_key_included'])
    def test_native_source_uses_readonly_projection_and_existing_python(self):
        text=(Path(__file__).resolve().parents[1]/'native/Ulak.swift').read_text()
        self.assertNotIn('sqlite3',text);self.assertNotIn('/bin/sh',text)
        self.assertIn('idleSystemSleepDisabled',text)
        self.assertIn('accessibilityReduceMotion',text)
        # Static source check only; not SwiftUI compilation.
