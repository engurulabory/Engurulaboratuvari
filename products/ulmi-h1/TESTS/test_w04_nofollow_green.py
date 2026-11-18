#!/usr/bin/env python3
"""W04 nofollow source read: real Python file IO in disposable directory."""
import json,os,sys,tempfile
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'PRODUCT'))
import chat_bridge
checks=[]
def ck(name,actual,expected):
 ok=actual==expected;checks.append({'id':name,'status':'PASS' if ok else 'FAIL','actual':repr(actual),'expected':repr(expected)});print(checks[-1]);assert ok
with tempfile.TemporaryDirectory(prefix='enguru-w04-nofollow-green-') as d:
 base=Path(d);trusted=base/'trusted';trusted.mkdir();source=trusted/'role.txt';source.write_bytes(b'authorized source')
 outside=base/'NOT_A_SOURCE';outside.write_bytes(b'FAKE_OUTSIDE')
 ck('REGULAR_SOURCE_READ',chat_bridge.read_regular(trusted,'role.txt'),b'authorized source')
 source.unlink();source.symlink_to(outside)
 try:chat_bridge.read_regular(trusted,'role.txt');ret='ACCEPTED'
 except chat_bridge.Hold as e:ret=e.reason
 ck('LEAF_SYMLINK_DENIED',ret,'HOLD_SOURCE_UNREADABLE')
 source.unlink();source.write_bytes(b'authorized source')
 outside_dir=base/'outside_dir';outside_dir.mkdir();(outside_dir/'secret').write_bytes(b'FAKE_OUTSIDE')
 (trusted/'sub').symlink_to(outside_dir)
 try:chat_bridge.read_regular(trusted,'sub/secret');ret='ACCEPTED'
 except chat_bridge.Hold as e:ret=e.reason
 ck('INTERMEDIATE_SYMLINK_DENIED',ret,'HOLD_SOURCE_UNREADABLE')
 for bad in ['../NOT_A_SOURCE','/etc/passwd','sub/../role.txt','C:\\file']:
  try:chat_bridge.read_regular(trusted,bad);ret='ACCEPTED'
  except chat_bridge.Hold as e:ret=e.reason
  ck('BAD_PATH_'+bad,ret,'HOLD_SOURCE_PATH')
 realopen=os.open;trigger=[False]
 def race(path,*args,**kwargs):
  if path=='role.txt' and 'dir_fd' in kwargs and not trigger[0]:
   trigger[0]=True;source.unlink();source.symlink_to(outside)
  return realopen(path,*args,**kwargs)
 with patch.object(os,'open',race):
  try:chat_bridge.read_regular(trusted,'role.txt');ret='ACCEPTED'
  except chat_bridge.Hold as e:ret=e.reason
 ck('REAL_LAST_MOMENT_SYMLINK_SWAP_DENIED',ret,'HOLD_SOURCE_UNREADABLE')
 ck('RACE_ACTUALLY_TRIGGERED',trigger[0],True)
report={'schema':'enguru.ulmi.w04.real-nofollow-directory-io-green/v1','checks':checks,'passed':sum(x['status']=='PASS' for x in checks),'total':len(checks),'scope':'DISPOSABLE_LOCAL_FILESYSTEM_NOT_CANONICAL_OWNER_SOURCE','real_qwen':'NOT_TESTED','original_task_full':'HOLD'}
(root/'EVIDENCE/W04_V71_NOFOLLOW_GREEN.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
