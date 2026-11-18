#!/usr/bin/env python3
"""W08 actual isolated file-reader race test; run --attack-red on unpatched source or --green on patched."""
import argparse, hashlib, json, os, pathlib, sqlite3, subprocess, sys, tempfile
P=argparse.ArgumentParser();P.add_argument('--product',required=True);P.add_argument('--mode',choices=['red','green'],required=True);a=P.parse_args()

child=r'''
import sys,os,pathlib,json,hashlib,tempfile
from pathlib import Path
root=Path(sys.argv[1]);product=Path(sys.argv[2]);mode=sys.argv[3]
os.environ['ENGURU_H1_STATE_HOME']=str(root)
sys.path.insert(0,str(product))
import server
server.prepare()
target=server.WORKSPACE/'w08_verified.txt';payload=b'Yalniz kilitli izinli gorev'
target.write_bytes(payload)
receipt={'output_sha256':hashlib.sha256(payload).hexdigest(),'readback_sha256':hashlib.sha256(payload).hexdigest()}
with server.db_conn() as db:
 db.execute('INSERT INTO tasks(task_id,created_at,updated_at,origin,user_prompt,path,content,plan_sha,status,receipt) VALUES(?,?,?,?,?,?,?,?,?,?)',('W08-test','now','now','TEST','TEST',target.name,payload.decode(),'test','PASS_SCOPED',json.dumps(receipt)))

if mode=='red':
 orig=Path.open; changed=[False]
 def swapped(self,*args,**kwargs):
  if self==target and not changed[0]:
   changed[0]=True
   # File type & size were already checked, now swap right before the re-open.
   self.unlink(); os.mkfifo(self)
  return orig(self,*args,**kwargs)
 Path.open=swapped
 print('SWAP_ACTIVATED',flush=True)
 try:server.safe_read_file(target.name)
 except Exception as e:print(type(e).__name__,str(e),flush=True)
 print('READ_RETURNED',flush=True)
else:
 # A FIFO already present in the workspace may never block the read API.
 target.unlink();os.mkfifo(target)
 print('FIFO_REPLACED',flush=True)
 try:server.safe_read_file(target.name)
 except Exception as e:
  print('SAFE_HOLD',type(e).__name__,str(e),flush=True)
 else:raise RuntimeError('UNSAFE_READ_RETURNED')
 target.unlink()
 outside=root/'outside-secret.txt';outside.write_text('DO_NOT_READ')
 target.symlink_to(outside)
 try:server.safe_read_file(target.name)
 except ValueError as exc:print('SYMLINK_DENIED',str(exc),flush=True)
 else:raise RuntimeError('UNSAFE_SYMLINK_ACCEPTED')
 target.unlink();target.write_bytes(payload)
 if server.safe_read_file(target.name)!=payload.decode():raise RuntimeError('SAFE_VALID_READ_FAILED')
 print('NORMAL_RECEIPT_READ=PASS',flush=True)
 target.write_bytes(b'tampered')
 try:server.safe_read_file(target.name)
 except ValueError as exc:
  if 'HOLD_OUTPUT_INTEGRITY' not in str(exc):raise
  print('SHA_TAMPER_DENIED=PASS',flush=True)
 else:raise RuntimeError('UNSAFE_SHA_ACCEPTED')
'''
with tempfile.TemporaryDirectory(prefix='ulmi-w08-fifo-race-') as temp:
 try:
  run=subprocess.run([sys.executable,'-B','-c',child,temp,a.product,a.mode],capture_output=True,text=True,timeout=2)
  print('EXIT',run.returncode,'OUT',run.stdout.strip(),'ERR',run.stderr[-300:])
  if a.mode=='red':
   assert 'SWAP_ACTIVATED' in run.stdout and 'READ_RETURNED' not in run.stdout,run.stdout
   raise AssertionError('RED was not reproduced')
  assert run.returncode==0 and all(x in run.stdout for x in ('SAFE_HOLD','SYMLINK_DENIED','NORMAL_RECEIPT_READ=PASS','SHA_TAMPER_DENIED=PASS')) and 'UNSAFE_READ_RETURNED' not in run.stdout
  print('W08_FIFO_NONBLOCK_GREEN=PASS')
 except subprocess.TimeoutExpired as exc:
  if a.mode=='red' and b'SWAP_ACTIVATED' in (exc.stdout or b''):
   print('W08_FIFO_REAL_BLOCK_RED=CONFIRMED timeout=2s')
  else: raise
