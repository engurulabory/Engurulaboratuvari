#!/usr/bin/env python3
"""10,001 REAL localhost HTTP security refusals; disposable H1 state, 1 server."""
import concurrent.futures,hashlib,json,os,re,socket,subprocess,sys,tempfile,time
from pathlib import Path
import requests
R=Path(__file__).resolve().parents[1];PRODUCT=R/'PRODUCT';N=10001
with tempfile.TemporaryDirectory(prefix='ulmi_w07_10001_http_') as td:
 state=Path(td)/'STATE'
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 url=f'http://127.0.0.1:{port}'
 proc=subprocess.Popen([sys.executable,'-B',str(PRODUCT/'server.py')],env={**os.environ,'ENGURU_H1_STATE_HOME':str(state),'ENGURU_USTA_PORT':str(port)},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  for i in range(100):
   try:
    r=requests.get(url+'/uat-final',timeout=.5)
    if r.status_code==200:break
   except requests.RequestException:time.sleep(.04)
  else:raise RuntimeError('Cannot boot isolated H1')
  token=re.search(r'<meta name="enguru-token" content="([a-f0-9]{48})"',r.text).group(1)
  def attack(worker_index):
   session=requests.Session();failure=[];ok=0
   # six bounded worker connections; 10,001 actual HTTP POST calls total.
   for ix in range(worker_index,N,6):
    forged=ix%2==0
    headers={'Origin':url if forged else 'https://forged.invalid','X-Enguru-Token':'forged' if forged else token,'Content-Type':'application/json'}
    try:
     answer=session.post(url+'/api/execute',json={'task_id':'00000000-0000-0000-0000-000000000000'},headers=headers,timeout=4)
     if answer.status_code==403:ok+=1
     else:failure.append({'ix':ix,'code':answer.status_code})
    except Exception as e:failure.append({'ix':ix,'error':type(e).__name__})
   session.close();return ok,failure
  t=time.monotonic()
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
   batches=list(executor.map(attack,range(6)))
  elapsed=round(time.monotonic()-t,2)
  good=sum(n for n,e in batches);bad=[x for _,e in batches for x in e]
  with __import__('sqlite3').connect(state/'data/tasks.sqlite3') as db:
   count=db.execute('SELECT count(*) FROM tasks').fetchone()[0]
  files=list((state/'workspace').iterdir())
  result={'schema':'enguru.ulmi.h1.v22.w07.http-attacks-10001-v1','requests':N,'denied_403':good,'failures':bad[:40],'elapsed_seconds':elapsed,'sqlite_task_rows':count,'files_written':len(files),'real_HTTP':True,'authoritative_producer_grant':'NOT_TESTED','formal_verdict':'HOLD','technical_test':'PASS_SCOPED' if good==N and count==0 and not files else 'HOLD'}
  (R/'EVIDENCE/V22_W07_10001_REAL_HTTP_ATTACK_RECEIPT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  print('REAL_HTTP_ATTACKS',good,'/',N,'seconds',elapsed,'SQLite_tasks',count,'files',len(files),'verdict',result['technical_test'],flush=True)
  if result['technical_test']!='PASS_SCOPED':sys.exit(1)
 finally:
  proc.terminate();proc.wait(timeout=10)
