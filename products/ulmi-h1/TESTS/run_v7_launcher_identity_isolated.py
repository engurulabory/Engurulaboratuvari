#!/usr/bin/env python3
"""Portable launcher logic in a disposable Linux shell with stubbed macOS 'open'.
Not a real owner macOS field test. No install or writes outside disposable root.
"""
from pathlib import Path
import tempfile,shutil,os,subprocess,socket,sys,time,json,urllib.request
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def ck(name,ok,detail=''):
 checks.append({'id':name,'passed':bool(ok),'detail':str(detail)[:150]});print(('PASS' if ok else 'FAIL'),name,detail,flush=True)
with tempfile.TemporaryDirectory(prefix='ulmi_v7_launcher_disposable_') as td:
 r=Path(td)/'H1';r.mkdir();shutil.copytree(ROOT/'PRODUCT',r/'PRODUCT')
 shutil.copy2(ROOT/'START_ULMI_H1.command',r/'START_ULMI_H1.command')
 fake=Path(td)/'bin';fake.mkdir()
 opened=Path(td)/'opened.txt'
 (fake/'open').write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "'+str(opened)+'"\n')
 (fake/'open').chmod(0o755)
 env={**os.environ,'PATH':str(fake)+':'+os.environ.get('PATH','')}
 # Scenario 1: an older/unrelated service already owns the port.
 with socket.socket() as occupied:
  occupied.bind(('127.0.0.1',0));occupied.listen(2);port=occupied.getsockname()[1]
  p=subprocess.run(['/bin/bash',str(r/'START_ULMI_H1.command')],env={**env,'ENGURU_USTA_PORT':str(port)},capture_output=True,text=True,timeout=8)
  ck('OLD_SERVICE_PORT_BLOCKED',p.returncode==1 and 'HOLD_PORT_OCCUPIED' in p.stdout,p.returncode)
  ck('OLD_SERVICE_BROWSER_NOT_OPENED',not opened.exists(),opened.exists())
 # Scenario 2: the genuine new V7 service is started in isolated copied source.
 with socket.socket() as sample:
  sample.bind(('127.0.0.1',0));port=sample.getsockname()[1]
 p=subprocess.Popen(['/bin/bash',str(r/'START_ULMI_H1.command')],env={**env,'ENGURU_USTA_PORT':str(port)},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 try:
  url=f'http://127.0.0.1:{port}/'
  for _ in range(50):
   if opened.exists():break
   if p.poll() is not None:break
   time.sleep(.2)
  ck('REAL_V7_PROCESS_STILL_RUNNING',p.poll() is None,p.poll())
  ck('V7_BROWSER_ONLY_AFTER_IDENTITY_MATCH',opened.exists() and url in opened.read_text() if opened.exists() else False,opened.read_text() if opened.exists() else 'NO_OPEN')
  with urllib.request.urlopen(url+'api/status',timeout=4) as response:
   status=json.loads(response.read())
  ck('V7_STATUS_EXACT_BUILD',status['version']=='ULMI-H1-V7-QWEN-SOURCE-ROUTE-GUARD-CANDIDATE',status['version'])
  ck('V7_RUNS_IN_COPIED_SOURCE_NOT_OWNER_MAC',str(r) not in str(ROOT) and (r/'STATE/data/tasks.sqlite3').exists(),str(r))
 finally:
  p.terminate()
  try:p.wait(timeout=6)
  except subprocess.TimeoutExpired:p.kill();p.wait(timeout=3)
result={'schema':'enguru.ulmi.h1.v7.launcher-identity-disposable/v1','checks':checks,'passed':sum(x['passed'] for x in checks),'total':len(checks),'real_mac_safari':'NOT_EXECUTED','simulated_mac_open':'SHELL_STUB_ONLY','state_scope':'DISPOSABLE_TEMP','result':'PASS_SCOPED' if all(x['passed'] for x in checks) else 'HOLD'}
(ROOT/'EVIDENCE/V7_LAUNCHER_IDENTITY_DISPOSABLE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('V7_LAUNCHER',result['passed'],'/',result['total'])
if result['passed']!=result['total']:sys.exit(1)
