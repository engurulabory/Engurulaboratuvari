"""Real Chromium navigation attempt for final HTML, never claim UAT on policy denial."""
from pathlib import Path
import tempfile,os,sys,socket,subprocess,time,json,requests
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='ulmi_e08_browser_') as home:
 with socket.socket() as x:
  x.bind(('127.0.0.1',0));port=x.getsockname()[1]
 root=f'http://127.0.0.1:{port}/'
 env={**os.environ,'ENGURU_H1_STATE_HOME':home,'ENGURU_USTA_PORT':str(port)}
 p=subprocess.Popen([sys.executable,'-B',str(R/'PRODUCT/server.py')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 try:
  for _ in range(60):
   try:
    req=requests.get(root,timeout=1)
    break
   except requests.exceptions.RequestException:time.sleep(.1)
  else:raise AssertionError('H1 HTTP server not ready')
  record={'stage':'E08_UAT_FINAL','real_http_status':req.status_code,'chromium_attempted':True,'browser_page_loaded':False,'owner_uat':'NOT_EXECUTED','formal_acceptance':'HOLD'}
  try:
   with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    try:
     page=b.new_page();page.goto(root,timeout=6000);record['browser_page_loaded']=True
     record['title']=page.title()
     record['user_flow_observed']='NOT_EXECUTED'
    finally:b.close()
  except Exception as e:
   record['browser_error']=str(e)[:500]
   record['browser_gate']='HOLD_BROWSER_ENVIRONMENT_POLICY'
  (R/'EVIDENCE/E08_REAL_BROWSER_POLICY_AND_UAT_BOUNDARY.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
  print(json.dumps(record,ensure_ascii=False))
 finally:p.terminate();p.wait(timeout=6)
