#!/usr/bin/env python3
"""Unified real regression receipt. Tests use explicit stubs, never a cloud model."""
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools'))
from validate import validate

class EvidenceResult(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.passed=[]
    def addSuccess(self,test):super().addSuccess(test);self.passed.append(test.id())

def run():
    pins=validate()
    # Mac /var is a system symlink: tests use a private, non-symlink temp root.
    temp=ROOT/'test-temporary'
    temp.mkdir(mode=0o700,exist_ok=True)
    if temp.is_symlink():raise RuntimeError('TEMP_ROOT_SYMLINK')
    tempfile.tempdir=str(temp)
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=EvidenceResult).run(suite)
    evidence=ROOT/'evidence';evidence.mkdir(exist_ok=True)
    log=stream.getvalue();(evidence/'V015_TEST_LOG.txt').write_text(log)
    manifest=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
    record=dict(schema='enguru.v015.real-tests/v1',timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        host=platform.system(),machine=platform.machine(),scope='CLOSED_FIXTURE_BROKER_REAL_CODE_HTTP_STUB_NOT_QWEN',
        tests=result.testsRun,passed_ids=result.passed,failures=len(result.failures),errors=len(result.errors),
        success=result.wasSuccessful(),source_manifest_sha256=hashlib.sha256((ROOT/'SOURCE_MANIFEST.json').read_bytes()).hexdigest(),
        source_files=manifest['files'],canonical=pins,
        test_log_sha256=hashlib.sha256(log.encode()).hexdigest(),
        live_model_calls=0,swiftui_compile='NOT_TESTED',mac_app_field='NOT_TESTED',verified_finish='HOLD')
    (evidence/'V015_TEST_RECEIPT.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(log);print('V015_REAL_REGRESSION=%d_TEST_METHODS'%result.testsRun)
    return result.wasSuccessful()

if __name__=='__main__':sys.exit(0 if run() else 1)
