#!/usr/bin/env python3
"""Real HTTP status build digest + independent byte-read + tamper detection.
Copied product/temporary state; never modifies protected original V5 or V6 candidate.
"""
from pathlib import Path
import hashlib, json, os, shutil, socket, subprocess, sys, tempfile, time, re
import requests
ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT/'PRODUCT'
checks=[]
def ck(name,p,details):
 checks.append({'name':name,'passed':bool(p),'observed':str(details)[:170]})
 print(('PASS' if p else 'FAIL'),name,str(details)[:70],flush=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory(prefix='ulmi_v6_sha_e2e_') as tmp:
 src=Path(tmp)/'PRODUCT';shutil.copytree(PRODUCT,src)
 state=Path(tmp)/'STATE'
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 env={**os.environ,'ENGURU_H1_STATE_HOME':str(state),'ENGURU_USTA_PORT':str(port)}
 process=subprocess.Popen([sys.executable,'-B',str(src/'server.py')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 url=f'http://127.0.0.1:{port}'
 try:
  for _ in range(70):
   if process.poll() is not None:raise RuntimeError('H1 exited')
   try:
    p=requests.get(url+'/api/status',timeout=.6)
    if p.status_code==200:break
   except requests.RequestException:time.sleep(.08)
  else:raise TimeoutError('H1 did not start')
  got=p.json();att=got['runtime_build'];reported=att['source_sha256']
  observed={name:sha((src/name).read_bytes()) for name in reported}
  aggregate=sha(json.dumps(observed,sort_keys=True,separators=(',',':')).encode())
  ck('01_REAL_HTTP_BUILD_STATUS',p.status_code==200 and got['version']=='ULMI-H1-V6-V22-BOUNDED-SECURE-CANDIDATE',got['version'])
  ck('02_SERVER_SHA_MATCHES_EXTERNAL_BYTES',reported==observed,len(reported))
  ck('03_AGGREGATE_SHA_MATCHES_EXTERNAL_BYTES',att['aggregate_sha256']==aggregate,aggregate)
  ck('04_SOURCE_ATTEST_NOT_SIGNED_PASS',att['verification_level']=='SELF_REPORTED_RUNNING_SOURCE_NOT_INDEPENDENT_DONECHECK',att['verification_level'])
  html=requests.get(url+'/uat-final',timeout=4);js=requests.get(url+'/uat_final.js',timeout=4)
  ck('05_REAL_UAT_PAGE_AND_SHA_CLIENT_CODE',html.status_code==200 and js.status_code==200 and 'Source-bound running H1 identity' in js.text and 'Browser reload unchanged exact H1 source SHA' in js.text,js.status_code)
  name='uat_final.js';initial=(src/name).read_bytes()
  (src/name).write_bytes(initial+b'\n/*attack changed source*/\n')
  change=requests.get(url+'/api/status',timeout=4).json()['runtime_build']
  ck('06_SOURCE_TAMPER_DETECTED',change['aggregate_sha256']!=aggregate and change['source_sha256'][name]!=observed[name],change['aggregate_sha256'])
  (src/name).write_bytes(initial)
  restore=requests.get(url+'/api/status',timeout=4).json()['runtime_build']
  ck('07_RESTORE_DETERMINISTIC_SHA',restore['aggregate_sha256']==aggregate,restore['aggregate_sha256'])
 finally:
  process.terminate();process.wait(timeout=5)
result={'schema':'enguru.ulmi.v6.running-code-build-provenance/v1','checks':checks,'passed':sum(x['passed'] for x in checks),'total':len(checks),'result':'PASS_SCOPED_REAL_HTTP' if all(x['passed'] for x in checks) else 'HOLD','independent_what':'SHA computed from separate test process and file bytes; NOT authorized independent reviewer','owner_safari_new_V6':'NOT_EXECUTED','owner_final':'NOT_ISSUED'}
(ROOT/'EVIDENCE/V6_BUILD_SOURCE_IDENTITY_HTTP_E2E.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('SUMMARY',result['passed'],'/',result['total'])
if not all(x['passed'] for x in checks):sys.exit(1)
