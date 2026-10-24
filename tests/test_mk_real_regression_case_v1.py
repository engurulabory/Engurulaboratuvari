"""Independent reproducible regression of historic silent V4 CLI dispatch.

Uses exact entrypoint bytes extracted from two archived, SHA-pinned ZIPapp versions.
All execution is inside a temporary synthetic ZIP with a stubbed handler.
No Mac, GitHub, external network, or product writes are performed.
"""
from __future__ import annotations
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'governance/enguru-suzgeci/learning/bridge/evidence'
PINS={
 'v4':('v4_dispatch_legacy_entrypoint.txt','ac9c058ad8b0e05c5702da61b6462b1353adee1b284656675f0699bd87476d98'),
 'v41':('v4_dispatch_repaired_entrypoint.txt','d23588e0996d1e20ce1a17974d1c3fd4d1cd4b39333371f36de7cd456b19f0da'),
}
CODE='''import runpy,sys,types
path=sys.argv[1]
sys.argv=[path,'--activate']
handler=types.ModuleType('tools.enguru_mk_autopilot_v4')
def main():print('SENTINEL_DISPATCH_CALLED=1')
handler.main=main
sys.modules['tools.enguru_mk_autopilot_v4']=handler
runpy.run_path(path,run_name='__main__')
'''

def read_source(version):
 name,pin=PINS[version]
 raw=(FIX/name).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=pin:raise AssertionError('SOURCE_PIN_MISMATCH')
 return raw

def files_from_ast(raw):
 tree=ast.parse(raw.decode('utf8'))
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FILES' for t in node.targets):
   names=ast.literal_eval(node.value)
   if not isinstance(names,tuple) or '__main__.py' not in names or len(names)!=len(set(names)):
    raise AssertionError('UNEXPECTED_MANIFEST')
   return names
 raise AssertionError('FILES_MISSING')

def test_zip(version):
 raw=read_source(version)
 names=files_from_ast(raw)
 payload={n:(raw if n=='__main__.py' else b'') for n in names}
 # The production verifier checks that archive paths, raw file digests and manifest agree.
 manifest={name:hashlib.sha256(body).hexdigest() for name,body in payload.items()}
 with tempfile.TemporaryDirectory(prefix='enguru-mk-dispatch-') as td:
  target=Path(td)/'pilot.zip'
  with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_STORED) as z:
   for key in sorted(payload):z.writestr(key,payload[key])
   z.writestr('MANIFEST.json',json.dumps(manifest))
  env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','HOME':td}
  proc=subprocess.run([sys.executable,'-B','-c',CODE,str(target)],text=True,capture_output=True,cwd=td,env=env,timeout=20)
  return {'version':version,'exitCode':proc.returncode,'manifestPass':'PACKAGE_MANIFEST=PASS_SHA256' in proc.stdout,
          'dispatchCalled':'SENTINEL_DISPATCH_CALLED=1' in proc.stdout,
          'stdout':proc.stdout.strip(),'stderr':proc.stderr.strip()}

def evidence():
 before=test_zip('v4');after=test_zip('v41')
 if before['exitCode']!=0 or after['exitCode']!=0 or not before['manifestPass'] or not after['manifestPass']:
  raise AssertionError('TEST_HARNESS_FAIL')
 if before['dispatchCalled'] or not after['dispatchCalled']:
  raise AssertionError('REGRESSION_NOT_REPRODUCED')
 return {'schema':'enguru.mk.dispatch-regression-evidence/v1','caseId':'CASE-V4SILENTCLI20261024',
  'oldEntryPointSha256':PINS['v4'][1],'fixedEntryPointSha256':PINS['v41'][1],
  'oldArchiveSha256':'ee2f36a6d2b7032d180ab641d06c69b4202173685f567ea3be1cffd0c4a9edd0',
  'fixedArchiveSha256':'af033fbb7a5768b870f9c76aded36d5161026fd194d54503fdffa2da27e4bb4e',
  'beforeDispatchSuccess':int(before['dispatchCalled']),
  'afterDispatchSuccess':int(after['dispatchCalled']),
  'verifiedBy':'CI_REPRODUCIBLE_REGRESSION',
  'trustStatus':'SOURCE_LEVEL_REGRESSION_ONLY',
  'learningPromotion':'HOLD_CANONICAL_VERIFIER',
  'officialAcceptance':'HOLD',
  'productWrites':0}

class TestDispatchRegression(unittest.TestCase):
 def test_manifest_both_versions(self):
  for version in PINS:
   with self.subTest(version=version):self.assertTrue(test_zip(version)['manifestPass'])
 def test_historic_silent_command_reproduces(self):
  r=test_zip('v4');self.assertEqual(r['exitCode'],0);self.assertFalse(r['dispatchCalled'])
 def test_fixed_dispatch_really_runs(self):
  r=test_zip('v41');self.assertEqual(r['exitCode'],0);self.assertTrue(r['dispatchCalled'])
 def test_before_after_bounded_improvement(self):
  e=evidence();self.assertEqual((e['beforeDispatchSuccess'],e['afterDispatchSuccess']),(0,1))
 def test_fixture_content_hash_pins(self):
  self.assertNotEqual(hashlib.sha256(read_source('v4')).digest(),hashlib.sha256(read_source('v41')).digest())
 def test_case_has_no_unearned_authority(self):
  e=evidence();self.assertEqual(e['officialAcceptance'],'HOLD');self.assertEqual(e['learningPromotion'],'HOLD_CANONICAL_VERIFIER')
 def test_no_product_mutation(self):
  self.assertEqual(evidence()['productWrites'],0)
 def test_deterministic_result(self):
  self.assertEqual(evidence(),evidence())
 def test_zip_paths_unique_and_static(self):
  for k in PINS:
   names=files_from_ast(read_source(k));self.assertEqual(len(set(names)),len(names))
   self.assertTrue(all(not x.startswith('/') and '..' not in x.split('/') for x in names))
 def test_no_token_or_private_log_in_evidence(self):
  e=evidence();self.assertNotIn('token',json.dumps(e).lower());self.assertNotIn('/Users/',json.dumps(e))
 def test_negative_control_bogus_pin(self):
  raw=read_source('v4');self.assertNotEqual(hashlib.sha256(raw+b'changed').hexdigest(),PINS['v4'][1])
 def test_no_learning_stats_from_one_case(self):
  e=evidence();self.assertEqual(e['learningPromotion'],'HOLD_CANONICAL_VERIFIER')

if __name__=='__main__':
 if sys.argv[1:]==['--evidence']:print(json.dumps(evidence(),sort_keys=True,separators=(',',':')))
 else:unittest.main()
