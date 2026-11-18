#!/usr/bin/env python3
"""Real H1 HTTP/files/SQLite UAT support test. NOT a browser or independent DoneCheck."""
import hashlib, json, os, re, socket, subprocess, sys, tempfile, time
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT/'PRODUCT'
checks=[]; paths=[]
def ck(name,ok):
 checks.append({'name':name,'passed':bool(ok)})
 print(('PASS ' if ok else 'FAIL ')+name,flush=True)
 if not ok:raise AssertionError(name)
def sha(data):return hashlib.sha256(data).hexdigest()
def freeport():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def boot(port,state):
 env={**os.environ,'ENGURU_H1_STATE_HOME':str(state),'ENGURU_USTA_PORT':str(port)}
 p=subprocess.Popen([sys.executable,'-B',str(PRODUCT/'server.py')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 base=f'http://127.0.0.1:{port}'
 for _ in range(100):
  if p.poll() is not None:raise RuntimeError('server exit '+str(p.returncode)+': '+str(p.stderr.read()[:450]))
  try:
   r=requests.get(base+'/uat-final',timeout=.6)
   if r.status_code==200:return p,base,r
  except requests.RequestException:time.sleep(.05)
 raise TimeoutError('server did not answer')
def stop(p):
 if p.poll() is None:p.terminate();p.wait(timeout=5)
with tempfile.TemporaryDirectory(prefix='ulmi-v5-sandbox-') as temp:
 state=Path(temp)/'STATE';port=freeport();proc,base,page=boot(port,state)
 try:
  match=re.search(r'<meta name="enguru-token" content="([0-9a-f]{48})"',page.text)
  ck('01_live_H1_real_uat_HTTP',page.status_code==200 and '/uat_final.js' in page.text)
  ck('02_session_token_injected',bool(match) and '__ENGURU_CSRF__' not in page.text)
  tok=match.group(1)
  ck('03_CSP_no_inline_JS',"script-src 'self'" in page.headers.get('Content-Security-Policy','') and "frame-ancestors 'none'" in page.headers.get('Content-Security-Policy',''))
  js=requests.get(base+'/uat_final.js',timeout=3)
  ck('04_JS_served_with_correct_mime',js.status_code==200 and 'javascript' in js.headers.get('Content-Type',''))
  ck('05_JS_syntax_node',subprocess.run(['node','--check',str(PRODUCT/'uat_final.js')],capture_output=True).returncode==0)
  ck('06_UI_links_final_UAT', '/uat-final' in requests.get(base,timeout=3).text)
  ck('07_no_unauthorized_work_before_click',not any((state/'workspace').iterdir()))
  wrong=requests.post(base+'/api/scaffold',json={'kind':'python'},headers={'X-Enguru-Token':'BAD','Origin':base},timeout=3)
  ck('08_bad_token_denied',wrong.status_code==403)
  good={'Origin':base,'X-Enguru-Token':tok,'Content-Type':'application/json'}
  missing=requests.post(base+'/api/scaffold',json={'kind':'python'},headers={'X-Enguru-Token':tok},timeout=3)
  ck('09_missing_origin_denied',missing.status_code==403)
  ck('10_no_write_after_bad_requests',not any((state/'workspace').iterdir()))
  badpath=requests.get(base+'/api/file?name=..%2Fescape.py',timeout=3)
  ck('11_path_traversal_denied',badpath.status_code==400)
  rows=[]
  for kind in ('python','html'):
   plan=requests.post(base+'/api/scaffold',json={'kind':kind},headers=good,timeout=4)
   ck('12_'+kind+'_plan_READY',plan.status_code==200 and plan.json().get('status')=='READY')
   task=plan.json();filename=state/'workspace'/task['path']
   ck('13_'+kind+'_no_write_before_approval',not filename.exists())
   executed=requests.post(base+'/api/execute',json={'task_id':task['task_id']},headers=good,timeout=20)
   ck('14_'+kind+'_execute_real_file',executed.status_code==200 and executed.json().get('status')=='PASS_SCOPED')
   got=requests.get(base+'/api/task?task_id='+task['task_id'],timeout=3).json()['task']
   verified=requests.get(base+'/api/verify?task_id='+task['task_id'],timeout=3).json()
   ck('15_'+kind+'_SHA_SQLite_readback',filename.is_file() and verified['match'] and sha(filename.read_bytes())==got['receipt']['output_sha256'])
   if kind=='python':ck('16_python_three_real_unittests','Ran 3 tests' in got['receipt']['functional_test']['output'])
   else:
    fixture=requests.get(base+'/api/trusted-html?task_id='+task['task_id'],timeout=3)
    ck('16_trusted_HTML_preview_and_csp',fixture.status_code==200 and "script-src 'sha256-" in fixture.headers['Content-Security-Policy'])
    ck('17_browser_behavior_still_not_self_attested',got['receipt']['functional_test']['status']=='NOT_TESTED_BROWSER')
   rows.append({'task_id':task['task_id'],'path':task['path'],'sha':sha(filename.read_bytes())})
  saved=requests.post(base+'/api/desk/projects/save',json={'title':'Gerçek UAT Test Projesi','goal':'Yerel HTML HTTP ve SQLite görev panosu, izole kapsamda çalıştırılacak.'},headers=good,timeout=5)
  ck('18_real_SQLite_project',saved.status_code==200 and bool(saved.json().get('project')))
  project=saved.json()['project']
  listed=requests.get(base+'/api/desk/projects',headers=good,timeout=3)
  ck('19_real_SQLite_project_readback',listed.status_code==200 and any(p['id']==project['id'] for p in listed.json()['projects']))
  plan=requests.post(base+'/api/desk/project-board/plan',json={'project_id':project['id'],'project_sha256':project['sha256']},headers=good,timeout=4)
  ck('20_provenance_SHA_pinned_board_PLAN',plan.status_code==200 and plan.json().get('status')=='READY')
  task=plan.json()
  result=requests.post(base+'/api/execute',json={'task_id':task['task_id']},headers=good,timeout=20)
  ck('21_board_real_subprocess_six_tests',result.status_code==200 and 'Ran 6 tests' in result.json()['receipt']['functional_test']['output'])
  rows.append({'task_id':task['task_id'],'path':task['path'],'sha':result.json()['receipt']['output_sha256']})
  ck('22_three_files_exist',len(list((state/'workspace').iterdir()))==3)
  repeated=requests.post(base+'/api/execute',json={'task_id':task['task_id']},headers=good,timeout=3)
  ck('23_repeat_has_no_new_write',repeated.status_code==200 and repeated.json().get('already_executed') is True and len(list((state/'workspace').iterdir()))==3)
  stop(proc);proc,base,page=boot(port,state)
  ck('24_restart_returns_HTML_200',page.status_code==200)
  for item in rows:
   file=state/'workspace'/item['path'];verify=requests.get(base+'/api/verify?task_id='+item['task_id'],timeout=3)
   ck('25_restart_'+item['path'][:10]+'_SHA',verify.status_code==200 and verify.json().get('match') is True and sha(file.read_bytes())==item['sha'])
  ck('26_three_SQLite_rows_after_restart',len(requests.get(base+'/api/tasks',timeout=3).json()['tasks'])==3)
  ck('27_author_browser_UAT_not_forged','NOT_TESTED_BROWSER' in (ROOT/'README_FINAL.md').read_text())
 finally:stop(proc)
proof={'schema':'enguru.ulmi.h1.v5.uatharness-http-readiness-v1','checks':checks,'passed':sum(x['passed'] for x in checks),'total':len(checks),'real_browser':'NOT_EXECUTED_ADMIN_POLICY','independent_donecheck':'NOT_PERFORMED','owner_final':'NOT_ISSUED','state_isolated':True,'product_source_unchanged':True}
(ROOT/'EVIDENCE/V5_REAL_HTTP_UAT_READINESS_RECEIPT.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
print('V5_UAT_HTTP_READINESS_CHECKS',proof['passed'],'/',proof['total'],flush=True)
