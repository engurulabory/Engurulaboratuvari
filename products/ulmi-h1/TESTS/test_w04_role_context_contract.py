#!/usr/bin/env python3
"""W04 H1 real source-context function exercised with SYNTHETIC TEST fixtures.
Never interprets synthetic fixtures as owner-approved canonical source content.
"""
import hashlib, json, os, sys, tempfile
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'PRODUCT'))
import chat_bridge, contract_bridge
REAL_CONTRACT=ROOT/'RESEARCH_ARCHIVE/canonical_sources/03_ORNEK_MIMARI_KABUL_SOZLESMESI_A.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

class Fixture:
 def __init__(self, tmp):
  self.path=Path(tmp).resolve()
  self.sources=self.path/'trusted-source'
  self.sources.mkdir()
  self.contract=self.path/'pilot.json'
  self.contract.write_bytes(REAL_CONTRACT.read_bytes())
  assert sha(self.contract.read_bytes())==contract_bridge.CONTRACT_PIN
  (self.path/'.ulmi-disposable').write_text('ULMI-WORK-H1-P1-ISOLATED\n')
  self.role_map={'AGENTS':'agents.txt','EVRENSEL_V3':'v3.txt','ZULFIKAR':'zulfikar.txt',
    'SUZGEC':'suzgec.txt','POZITIF_DIL':'suzgec.txt',
    'DONECHECK':'donecheck.txt','HUMAN_THRESHOLD':'donecheck.txt','PILOT_A':'pilot_a.txt'}
  for x in sorted(set(self.role_map.values())):
   (self.sources/x).write_text('TEST SOURCE '+x+'\n',encoding='utf-8')
  os.environ.update({'ENGURU_H1_STATE_HOME':str(self.path), 'ENGURU_ULMI_CHAT_TEST_MODE':'1',
    'ENGURU_ULMI_P1_ISOLATED':'TRUE',
    'ENGURU_ULMI_CHAT_CONTRACT_FILE':str(self.contract),
    'ENGURU_ULMI_TRUSTED_BASELINE_ROOT':str(self.path),
    'ENGURU_ULMI_CHAT_CONTEXT_ROOT':str(self.sources)})
  self.versions={r:'synthetic-test-v1' for r in self.role_map}
  self.rewrite()
 def rewrite(self):
  manifest={'schema':'enguru.ulmi.chat-source-bundle/v2','source_class':'SYNTHETIC_TEST_FIXTURE',
   'sources':[{'role':r,'path':f,'version':self.versions[r],
               'sha256':sha((self.sources/f).read_bytes())} for r,f in self.role_map.items()]}
  raw=json.dumps(manifest,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
  (self.sources/'manifest.json').write_bytes(raw)
  os.environ['ENGURU_ULMI_CHAT_CONTEXT_MANIFEST_SHA256']=sha(raw)
 def run(self):
  try:
   with patch.object(contract_bridge,'preview',return_value={'gates':{'owner_execution':'HOLD_NO_GRANT'},'contract_sha256':contract_bridge.CONTRACT_PIN}):
    _,refs,full,is_test=chat_bridge.approved_context()
    return 'ACCEPTED',len(full.encode()),refs
  except chat_bridge.Hold as e:return e.reason,0,[]

if __name__=='__main__':
 with tempfile.TemporaryDirectory(prefix='ulmi_v71_w04_context_') as d:
  f=Fixture(d)
  good=f.run();print('CONTROL_GOOD',good[0],good[1]);assert good[0]=='ACCEPTED'
  f.versions['POZITIF_DIL']='contradicting-shared-document-version'
  f.rewrite();bad=f.run()
  print('CONTROL_SHARED_DOC_VERSION_CONFLICT',bad[0],bad[1])
  if '--expect-red' in sys.argv:
   # The historical V7 source erroneously accepted this deliberately wrong input.
   assert bad[0]=='ACCEPTED','V7 source no longer reproduces old RED'
   print('RED_REPRODUCED=TRUE: inconsistent version was accepted')
   sys.exit(0)
  assert bad[0]=='HOLD_CONTEXT_SHARED_VERSION',bad
  f.versions['POZITIF_DIL']='synthetic-test-v1';f.rewrite()
  f.versions['HUMAN_THRESHOLD']='contradicting-donecheck-version';f.rewrite()
  assert f.run()[0]=='HOLD_CONTEXT_SHARED_VERSION'
  f.versions['HUMAN_THRESHOLD']='synthetic-test-v1';f.rewrite()
  # The exact assembled context is bounded to 32768 UTF-8 bytes.
  last_good=None; first_bad=None
  for count in range(31500,32900):
   (f.sources/'agents.txt').write_bytes(b'A'*count)
   f.rewrite();state,n,_=f.run()
   if state=='ACCEPTED':last_good=(count,n)
   elif state=='HOLD_CONTEXT_TOTAL_SIZE':
    first_bad=(count,n)
    if last_good:break
   else:raise AssertionError('Unexpected result '+state)
  print('BOUNDARY_GOOD',last_good,'BOUNDARY_REJECTED',first_bad)
  assert last_good and first_bad and last_good[1]==chat_bridge.MAX_CONTEXT
  assert first_bad[0]==last_good[0]+1
  # Source byte tampering must refuse despite unchanged signed manifest.
  (f.sources/'agents.txt').write_bytes(b'changed source')
  assert f.run()[0]=='HOLD_CONTEXT_SOURCE_SHA'
  print('W04_SYNTHETIC_ROLE_AND_32768_BYTE_TESTS=PASS')
