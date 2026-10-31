import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import mac_toolchain as m


class Toolchain(unittest.TestCase):
    def setup_fixture(self,d):
        root=Path(d);compiler=root/'swiftc';compiler.write_text('compiler fixture')
        sdk=root/'SDK';sdk.mkdir()
        return root,compiler,sdk
    def test_sdk_target_and_language_passed_to_probe(self):
        with tempfile.TemporaryDirectory() as d:
            root,compiler,sdk=self.setup_fixture(d);calls=[]
            def run(args,**kw):
                calls.append(args)
                output=str(compiler) if '--find' in args else str(sdk) if '--show-sdk-path' in args else 'SDK/Swift fixture'
                return subprocess.CompletedProcess(args,0,output,'')
            with patch.object(m.subprocess,'run',side_effect=run):c,flags=m.prepare(root)
            self.assertEqual(c,str(compiler))
            self.assertEqual(flags,['-sdk',str(sdk),'-target','arm64-apple-macosx13.0','-swift-version','5'])
            self.assertEqual(calls[-1],[c,*flags,'-typecheck',str(root/'MAC_TOOLCHAIN_PROBE.swift')])
            self.assertEqual(json.loads((root/'MAC_TOOLCHAIN.json').read_text())['state'],'PASS_SCOPED_IMPORT_TYPECHECK')
    def test_missing_sdk_records_hold_without_download(self):
        with tempfile.TemporaryDirectory() as d:
            root,compiler,sdk=self.setup_fixture(d)
            def run(args,**kw):
                output=str(compiler) if '--find' in args else '/nonexistent/sdk' if '--show-sdk-path' in args else 'fixture'
                return subprocess.CompletedProcess(args,0,output,'')
            with patch.object(m.subprocess,'run',side_effect=run),self.assertRaises(RuntimeError):m.prepare(root)
            record=json.loads((root/'MAC_TOOLCHAIN.json').read_text())
            self.assertEqual(record['state'],'HOLD')
            self.assertFalse(any('--install' in x['argv'] for x in record['commands']))
    def test_probe_failure_remains_hold_with_full_diagnostics(self):
        with tempfile.TemporaryDirectory() as d:
            root,compiler,sdk=self.setup_fixture(d)
            def run(args,**kw):
                output=str(compiler) if '--find' in args else str(sdk) if '--show-sdk-path' in args else 'fixture'
                return subprocess.CompletedProcess(args,1 if '-typecheck' in args else 0,output,'stdlib error' if '-typecheck' in args else '')
            with patch.object(m.subprocess,'run',side_effect=run),self.assertRaises(RuntimeError):m.prepare(root)
            record=json.loads((root/'MAC_TOOLCHAIN.json').read_text())
            self.assertEqual(record['state'],'HOLD');self.assertEqual(record['commands'][-1]['stderr'],'stdlib error')
    def test_probe_timeout_does_not_claim_pass(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(m.subprocess,'run',side_effect=subprocess.TimeoutExpired('xcrun',20)),self.assertRaises(subprocess.TimeoutExpired):m.prepare(Path(d))
            self.assertEqual(json.loads((Path(d)/'MAC_TOOLCHAIN.json').read_text())['state'],'HOLD')
