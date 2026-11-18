from pathlib import Path
import tempfile,subprocess,os,time,socket,requests,re,json,shutil
ROOT=Path(__file__).resolve().parents[1]
def port():
 s=socket.socket();s.bind(('127.0.0.1',0));n=s.getsockname()[1];s.close();return n
with tempfile.TemporaryDirectory(prefix='ulmi_e06_red_') as home:
 p=port();url=f'http://127.0.0.1:{p}'
 candidate=Path(home)/'product'
 shutil.copytree(ROOT/'PRODUCT',candidate,ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copy2(ROOT/'ORIGINALS'/'server_before_E05_E06.py',candidate/'server.py')
 env={**os.environ,'ENGURU_H1_STATE_HOME':home,'ENGURU_USTA_PORT':str(p)}
 proc=subprocess.Popen([os.sys.executable,'-B',str(candidate/'server.py')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,env=env)
 try:
  for i in range(80):
   try: h=requests.get(url,timeout=1);break
   except requests.exceptions.RequestException:time.sleep(.1)
  else:raise AssertionError('baseline server not running')
  t=re.search('name="enguru-token" content="([a-f0-9]{48})"',h.text).group(1)
  headers={'X-Enguru-Token':t,'Origin':url,'Content-Type':'application/json'}
  plan=requests.post(url+'/api/scaffold',json={'kind':'python'},headers=headers,timeout=5).json()
  run=requests.post(url+'/api/execute',json={'task_id':plan['task_id']},headers=headers,timeout=7).json()
  assert run['status']=='PASS_SCOPED'
  path=Path(home)/'workspace'/run['receipt']['path']
  path.write_text('BOZULMUS_DOSYA_IZINSIZ_DEGISIM',encoding='utf8')
  verify=requests.get(url+'/api/verify?task_id='+plan['task_id'],timeout=5).json()
  exposed=requests.get(url+'/api/file?name='+path.name,timeout=5)
  assert verify['status']=='HOLD_INTEGRITY'
  # RED: pre-repair server returns mutated bytes to the UI while receipt is stale PASS.
  assert exposed.status_code==200 and 'BOZULMUS_DOSYA' in exposed.text
  print(json.dumps({'test':'E06_REAL_RED_READ_TAMPERED_FILE','baseline_sha':'efbfd4887deabe5e2652fb290821503d03c092465fde2669239e040928be2fe6','verified':'HOLD_INTEGRITY','unexpected_http':exposed.status_code,'confirmed_existing_bug':True,'scope':'DISPOSABLE_E04_BASELINE','result':'RED_REPRODUCED'},ensure_ascii=False))
 finally:proc.terminate();proc.wait(timeout=5)
