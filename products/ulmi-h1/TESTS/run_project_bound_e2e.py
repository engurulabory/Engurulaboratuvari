#!/usr/bin/env python3
"""User project -> pinned code generation -> real subprocess tests -> generated app HTTP -> restart.

Truth boundary: HTTP real, browser UAT NOT_TESTED, Qwen NOT_EXECUTED,
independent owner DoneCheck NOT_EXECUTED. Uses isolated temporary SQLite/workspace only.
"""
import hashlib,json,os,re,socket,sqlite3,subprocess,sys,tempfile,time,uuid
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT/'PRODUCT'
EVIDENCE=ROOT/'EVIDENCE'
EVIDENCE.mkdir(parents=True,exist_ok=True)
checks=[]
def ck(name,truth):
 checks.append({'id':name,'pass':bool(truth)})
 print(('PASS' if truth else 'FAIL'),name,flush=True)
 if not truth:raise AssertionError(name)
def sha(x):return hashlib.sha256(x).hexdigest()
def port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def start(command, env, base,log):
 handle=(EVIDENCE/log).open('a')
 process=subprocess.Popen(command,env=env,stdout=handle,stderr=subprocess.STDOUT)
 for _ in range(100):
  if process.poll() is not None:raise RuntimeError('exit '+str(process.returncode)+' '+log)
  try:
   r=requests.get(base,timeout=.5)
   if r.status_code==200:return process,r
  except requests.RequestException:time.sleep(.1)
 raise TimeoutError(log)
def stop(p):
 if p.poll() is None:p.terminate();p.wait(timeout=10)
def token(html):return re.search('name="enguru-token" content="([0-9a-f]{48})"',html).group(1)
with tempfile.TemporaryDirectory(prefix='ULMI_V3_PROJECT_BOUND_ISOLATED_') as temporary:
 tmp=Path(temporary);p1=port();hurl=f'http://127.0.0.1:{p1}'
 env={**os.environ,'ENGURU_H1_STATE_HOME':str(tmp/'H1'),'ENGURU_USTA_PORT':str(p1)}
 process,page=start([sys.executable,'-B',str(PRODUCT/'server.py')],env,hurl,'V3_H1_SERVER.log')
 try:
  tkn=token(page.text)
  hdr={'Content-Type':'application/json','Origin':hurl,'X-Enguru-Token':tkn}
  def post(route,payload,headers=None):return requests.post(hurl+route,json=payload,headers=headers or hdr,timeout=30)
  ck('01_actual_H1_HTTP',page.status_code==200)
  ck('02_project_card_and_JS_present','id="choice-projectboard"' in page.text and 'projectboard:' in requests.get(hurl+'/app.js').text)
  ck('03_browser_script_valid',subprocess.run(['node','--check',str(PRODUCT/'app.js')],capture_output=True).returncode==0)
  ck('04_template_pinned',sha((PRODUCT/'taskboard_template.py').read_bytes())=='861638957813a0cf8de29b760558a8f12d4360464a4932c2637e340aa30e0deb')
  ck('05_original_V22_ABC_unchanged',sha((ROOT/'ORIGINALS/V22_IMMUTABLE_SOURCE.json').read_bytes())=='069c03b0f299e76ef46e26a25eb4284474ae5219353185a88386ee5df9f39304' and sha((ROOT/'ORIGINALS/PILOT_ABC_IMMUTABLE_SOURCE.json').read_bytes())=='5beb10d407dc550d7f979062fef6bdcfd451791103d5b02fc1c2d05a1786d79b')
  title="Pilot A <img src=x onerror=alert(1)> ' Projem"
  goal="Müşteri kayıtları ve takip görevleri için izole bir pano. <script>alert(1)</script> İzinli bir prototip."
  saved=post('/api/desk/projects/save',{'title':title,'goal':goal})
  ck('06_real_project_SQLite',saved.status_code==200 and saved.json()['project']['title']==title)
  project=saved.json()['project'];ident={'project_id':project['id'],'project_sha256':project['sha256']}
  ck('07_project_readback',any(p['id']==project['id'] for p in requests.get(hurl+'/api/desk/projects',headers=hdr).json()['projects']))
  ck('08_denied_wrong_SHA',post('/api/desk/project-board/plan',{**ident,'project_sha256':'0'*64}).status_code==422)
  ck('09_denied_forged_ID',post('/api/desk/project-board/plan',{**ident,'project_id':str(uuid.uuid4())}).status_code==422)
  ck('10_denied_missing_Origin',post('/api/desk/project-board/plan',ident,{k:v for k,v in hdr.items() if k!='Origin'}).status_code==403)
  ck('11_denied_token',post('/api/desk/project-board/plan',ident,{**hdr,'X-Enguru-Token':'forged'}).status_code==403)
  baddup='{"project_id":"'+project['id']+'","project_id":"'+project['id']+'","project_sha256":"'+project['sha256']+'"}'
  ck('12_denied_duplicate_JSON_keys',requests.post(hurl+'/api/desk/project-board/plan',data=baddup.encode(),headers=hdr).status_code==422)
  plan_r=post('/api/desk/project-board/plan',ident)
  ck('13_project_plan_HTTP',plan_r.status_code==200)
  plan=plan_r.json();output=tmp/'H1/workspace'/plan['path'];obj=plan['content']
  ck('14_plan_READY_no_write',plan['status']=='READY' and not output.exists())
  ck('15_bound_project_SHA_receipt',plan['project_sha256']==project['sha256'] and plan['template_sha256']==sha((PRODUCT/'taskboard_template.py').read_bytes()))
  ck('16_escaped_XSS_title','&lt;img src=x onerror=alert(1)&gt;' in obj and '<img src=x onerror=alert(1)>' not in obj)
  ck('17_escaped_XSS_goal','&lt;script&gt;alert(1)&lt;/script&gt;' in obj and '<script>alert(1)</script>' not in obj)
  ck('18_source_SHA_plan_integrity',plan['plan_sha256'] and 'Proje:' in obj and 'Hedef:' in obj)
  changed=post('/api/desk/projects/save',{'id':project['id'],'expected_sha256':project['sha256'],'title':'Güncellenmiş Proje','goal':'Yeni hedef ve tam SHA değişimi.'})
  ck('19_project_CAS_change',changed.status_code==200 and changed.json()['project']['sha256']!=project['sha256'])
  stale=post('/api/execute',{'task_id':plan['task_id']})
  ck('20_stale_plan_denied_before_write',stale.status_code==422 and not output.exists())
  ck('21_stale_task_HOLD',requests.get(hurl+'/api/task?task_id='+plan['task_id']).json()['task']['status']=='HOLD')
  new=changed.json()['project'];newident={'project_id':new['id'],'project_sha256':new['sha256']}
  plan2=post('/api/desk/project-board/plan',newident).json()
  ck('22_fresh_project_plan_READY',plan2['status']=='READY' and plan2['project_id']==new['id'])
  with sqlite3.connect(tmp/'H1/data/tasks.sqlite3') as db:
   db.execute('UPDATE tasks SET content=? WHERE task_id=?',('import os\nprint("owned")',plan2['task_id']));db.commit()
  invalid=post('/api/execute',{'task_id':plan2['task_id']});output2=tmp/'H1/workspace'/plan2['path']
  ck('23_payload_tamper_denied',invalid.status_code==422 and 'HOLD_SCOPED_TEMPLATE_SOURCE_MISMATCH' in invalid.text)
  ck('24_payload_tamper_no_file',not output2.exists())
  plan3=post('/api/desk/project-board/plan',newident).json()
  ck('25_fresh_reviewed_plan',plan3['status']=='READY' and not (tmp/'H1/workspace'/plan3['path']).exists())
  executed=post('/api/execute',{'task_id':plan3['task_id']})
  ck('26_real_write_subprocess_HTTP',executed.status_code==200 and executed.json()['status']=='PASS_SCOPED')
  rec=executed.json()['receipt'];out=tmp/'H1/workspace'/plan3['path']
  ck('27_generated_real_source',out.is_file() and out.stat().st_size>5000)
  ck('28_generated_source_SHA_readback',sha(out.read_bytes())==rec['output_sha256']==rec['readback_sha256'])
  ck('29_six_true_generated_unit_tests',rec['functional_test']['status']=='PASS' and 'Ran 6 tests' in rec['functional_test']['output'] and rec['functional_test']['exit_code']==0)
  ck('30_bound_project_in_receipt',rec['bound_project']==newident)
  ck('31_H1_SQLite_receipt',requests.get(hurl+'/api/task?task_id='+plan3['task_id']).json()['task']['receipt']['output_sha256']==sha(out.read_bytes()))
  ck('32_no_duplicate_write',post('/api/execute',{'task_id':plan3['task_id']}).json()['already_executed'] is True)
  ck('33_verify_endpoint',requests.get(hurl+'/api/verify?task_id='+plan3['task_id']).json()['match'] is True)
  bport=port();burl=f'http://127.0.0.1:{bport}';bdb=tmp/'BOARD/data.sqlite3'
  benv={**os.environ,'ULMI_TASKBOARD_PORT':str(bport),'ULMI_TASKBOARD_DB':str(bdb)}
  bp,board=start([sys.executable,'-I','-B',str(out),'serve'],benv,burl,'V3_BOARD_SERVER.log')
  try:
   ck('34_generated_app_real_HTML_HTTP',board.status_code==200 and 'Güncellenmiş Proje' in board.text)
   ck('35_generated_app_CSP',"script-src 'sha256-" in board.headers.get('Content-Security-Policy',''))
   btkn=re.search('name="ulmi-token" content="([0-9a-f]{48})"',board.text).group(1)
   bheaders={'Content-Type':'application/json','Origin':burl,'X-ULMI-Token':btkn}
   rid=str(uuid.uuid4())
   item=requests.post(burl+'/api/tasks',json={'title':'Gerçek iş','request_id':rid},headers=bheaders).json()['task']
   ck('36_generated_app_real_task',item['state']=='TODO')
   dup=requests.post(burl+'/api/tasks',json={'title':'Gerçek iş','request_id':rid},headers=bheaders).json()['task']
   ck('37_generated_replay_idempotent',dup['id']==item['id'] and len(requests.get(burl+'/api/tasks').json()['tasks'])==1)
   ck('38_generated_wrong_token_denied',requests.post(burl+'/api/tasks',json={'title':'Yasak','request_id':str(uuid.uuid4())},headers={**bheaders,'X-ULMI-Token':'forged'}).status_code==403)
   ck('39_generated_update',requests.post(burl+'/api/update',json={'id':item['id'],'state':'DONE'},headers=bheaders).status_code==200)
   ck('40_generated_db_committed',bdb.is_file() and sqlite3.connect(bdb).execute('PRAGMA quick_check').fetchone()[0]=='ok')
  finally:stop(bp)
  bp,board=start([sys.executable,'-I','-B',str(out),'serve'],benv,burl,'V3_BOARD_RESTART.log')
  try:
   rows=requests.get(burl+'/api/tasks').json()['tasks']
   ck('41_generated_app_restart_SQLite',len(rows)==1 and rows[0]['id']==item['id'] and rows[0]['state']=='DONE')
  finally:stop(bp)
  stop(process);process,page=start([sys.executable,'-B',str(PRODUCT/'server.py')],env,hurl,'V3_H1_RESTART.log')
  ck('42_H1_restart_SHA',requests.get(hurl+'/api/verify?task_id='+plan3['task_id']).json()['match'] is True)
  ck('43_H1_restart_project',requests.get(hurl+'/api/desk/projects',headers={'X-Enguru-Token':token(page.text)}).json()['projects'][0]['sha256']==new['sha256'])
  with sqlite3.connect(tmp/'H1/data/tasks.sqlite3') as db:ck('44_H1_restart_SQLite_integrity',db.execute('PRAGMA quick_check').fetchone()[0]=='ok')
  # Same generated code cannot silently become a different source after receipt.
  out.write_bytes(out.read_bytes()+b'\n# modified without owner\n')
  ck('45_generated_file_tamper_detected',requests.get(hurl+'/api/verify?task_id='+plan3['task_id']).json()['status']=='HOLD_INTEGRITY')
  ck('46_modified_file_not_served',requests.get(hurl+'/api/file?name='+plan3['path']).status_code==400)
  new_token=token(page.text)
  response=requests.post(hurl+'/api/execute',json={'task_id':plan3['task_id']},headers={**hdr,'X-Enguru-Token':new_token}).json()
  ck('47_stale_receipt_denied',response['status']=='HOLD_INTEGRITY' and response['receipt'] is None)
  ck('48_no_second_write_after_tamper',len(list((tmp/'H1/workspace').glob('*.py')))==1)
 finally:stop(process)
 # Use an isolated copy for deliberate source tamper; preserve real product.
 evil=tmp/'SOURCE_TAMPER';evil.mkdir();
 import shutil
 for f in ('server.py','taskboard_template.py','capabilities.py','worklist.py','contract_bridge.py','chat_bridge.py'):
  shutil.copy2(PRODUCT/f,evil/f)
 (evil/'taskboard_template.py').write_bytes((evil/'taskboard_template.py').read_bytes()+b'\n# drift\n')
 result=subprocess.run([sys.executable,'-B',str(evil/'server.py')],env={**os.environ,'ENGURU_H1_STATE_HOME':str(tmp/'EVIL')},capture_output=True,text=True,timeout=8)
 ck('49_runtime_template_SHA_tamper_fail_closed',result.returncode!=0 and 'HOLD_TRUSTED_TASKBOARD_TEMPLATE_SOURCE_SHA' in result.stderr)
 artifact={'schema':'enguru.ulmi.h1.v3.real-project-board/actual-e2e','result':'PASS_SCOPED' if all(x['pass'] for x in checks) else 'HOLD', 'passed':sum(x['pass'] for x in checks),'total':len(checks),'checks':checks, 'original_v22_formal':'0/12','h1_browser_uat':'HOLD_BROWSER_POLICY','owner_acceptance':'NOT_EXECUTED','independent_reviewer':'NOT_EXECUTED','H2':'PARKED','new_paid_api':False}
 (EVIDENCE/'V3_PROJECT_BOUND_E2E_RECEIPT.json').write_text(json.dumps(artifact,indent=2,ensure_ascii=False)+'\n')
 print('PROJECT_BOUND_TESTS',artifact['passed'],'/',artifact['total'])
