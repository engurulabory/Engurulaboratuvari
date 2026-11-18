#!/usr/bin/env python3
"""Real H1 executor -> generated app -> HTTP/SQLite/restart; no browser/owner fiction."""
import os,sys,subprocess,tempfile,requests,socket,time,re,json,sqlite3,hashlib,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'PRODUCT';E=ROOT/'EVIDENCE'
results=[]
def sha(x):return hashlib.sha256(x).hexdigest()
def ck(k,passed):
 results.append({'id':k,'passed':bool(passed)});print(('PASS' if passed else 'FAIL'),k,flush=True)
 if not passed:raise AssertionError(k)
def port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def start(args,env,base,label):
 p=subprocess.Popen(args,env=env,stdout=(E/(label+'.log')).open('a'),stderr=subprocess.STDOUT)
 for i in range(90):
  if p.poll() is not None:raise RuntimeError(label+' exited '+str(p.returncode))
  try:
   r=requests.get(base+'/',timeout=.5)
   if r.status_code==200:return p,r
  except requests.RequestException:time.sleep(.1)
 raise RuntimeError(label+' timeout')
def stop(p):
 if p.poll() is None:p.terminate();p.wait(timeout=8)
with tempfile.TemporaryDirectory(prefix='ULMI_9_EMIR_V2_ISOLATED_') as t:
 d=Path(t);hport=port();hurl=f'http://127.0.0.1:{hport}'
 env={**os.environ,'ENGURU_H1_STATE_HOME':str(d/'h1'),'ENGURU_USTA_PORT':str(hport)}
 hp,page=start([sys.executable,'-B',str(P/'server.py')],env,hurl,'V2_H1_REAL_SERVER')
 try:
  token=re.search('name="enguru-token" content="([0-9a-f]{48})"',page.text).group(1)
  auth={'X-Enguru-Token':token,'Origin':hurl,'Content-Type':'application/json'}
  def hpost(path,payload,heads=None):return requests.post(hurl+path,json=payload,headers=heads or auth,timeout=30)
  ck('01_V22_and_ABC_contracts_preserved',all((ROOT/'ORIGINALS'/s).is_file() for s in ('V22_IMMUTABLE_SOURCE.json','PILOT_ABC_IMMUTABLE_SOURCE.json')))
  ck('02_live_H1_HTML',page.status_code==200 and 'ULMi' in page.text)
  ck('03_H1_CSP',"script-src 'self'" in page.headers.get('Content-Security-Policy',''))
  ck('04_new_taskboard_ui_card', 'id="choice-taskboard"' in page.text)
  ck('05_new_taskboard_JS',"taskboard:" in requests.get(hurl+'/app.js').text)
  ck('06_before_plan_no_workspace_files',not any((d/'h1/workspace').iterdir()))
  plan_result=hpost('/api/scaffold',{'kind':'taskboard'});ck('07_plan_HTTP',plan_result.status_code==200)
  plan=plan_result.json();path=d/'h1/workspace'/plan['path']
  ck('08_plan_ready_and_unwritten',plan['status']=='READY' and not path.exists())
  ck('09_plan_registered_SQLite',any(x['task_id']==plan['task_id'] and x['status']=='READY' for x in requests.get(hurl+'/api/tasks').json()['tasks']))
  run=hpost('/api/execute',{'task_id':plan['task_id']});ck('10_real_H1_execute',run.status_code==200)
  rec=run.json()['receipt']
  ck('11_six_real_subprocess_unittests',rec['functional_test']['status']=='PASS' and 'Ran 6 tests' in rec['functional_test']['output'])
  ck('12_real_generated_Python_file',path.is_file() and path.stat().st_size>5000)
  ck('13_generated_SHA_readback',sha(path.read_bytes())==rec['output_sha256']==rec['readback_sha256'])
  ck('14_reviewed_fixture_byte_match',path.read_bytes()==(P/'taskboard_template.py').read_bytes())
  ck('15_real_task_receipt_in_SQLite',requests.get(hurl+'/api/task?task_id='+plan['task_id']).json()['task']['receipt']['output_sha256']==sha(path.read_bytes()))
  ck('16_real_H1_verify_SHA',requests.get(hurl+'/api/verify?task_id='+plan['task_id']).json()['match'])
  ck('17_duplicate_no_second_effect',hpost('/api/execute',{'task_id':plan['task_id']}).json().get('already_executed') is True)
  ck('18_cross_origin_denied',hpost('/api/scaffold',{'kind':'taskboard'},{**auth,'Origin':'https://forged.invalid'}).status_code==403)
  ck('19_fake_token_denied',hpost('/api/scaffold',{'kind':'taskboard'},{**auth,'X-Enguru-Token':'forged'}).status_code==403)
  ck('20_other_engine_denied',hpost('/api/scaffold',{'kind':'shell'}).status_code==422)
  ck('21_escape_path_denied',requests.get(hurl+'/api/file?name=..%2Fsecret.py').status_code==400)
  bport=port();burl=f'http://127.0.0.1:{bport}';db=d/'generated_board/data.sqlite3'
  benv={**os.environ,'ULMI_TASKBOARD_PORT':str(bport),'ULMI_TASKBOARD_DB':str(db)}
  bp,bpage=start([sys.executable,'-I','-B',str(path),'serve'],benv,burl,'V2_GENERATED_TASKBOARD')
  try:
   ck('22_generated_app_real_HTML',bpage.status_code==200 and 'Görev Panosu' in bpage.text)
   ck('23_generated_app_CSP_JS',"script-src 'sha256-" in bpage.headers.get('Content-Security-Policy',''))
   btoken=re.search('name="ulmi-token" content="([0-9a-f]{48})"',bpage.text).group(1)
   bheaders={'X-ULMI-Token':btoken,'Origin':burl,'Content-Type':'application/json'}
   request_id=str(uuid.uuid4())
   payload={'title':'Pilot A gerçek görev','request_id':request_id}
   created=requests.post(burl+'/api/tasks',json=payload,headers=bheaders).json()['task'];job=created['id']
   ck('24_generated_app_real_create',created['state']=='TODO')
   ck('25_generated_app_real_readback',requests.get(burl+'/api/tasks').json()['tasks'][0]['id']==job)
   ck('26_generated_app_SQLite_file',db.is_file() and db.stat().st_size>0)
   duplicate=requests.post(burl+'/api/tasks',json=payload,headers=bheaders).json()['task']
   ck('27_generated_app_replay_safe',duplicate['id']==job and len(requests.get(burl+'/api/tasks').json()['tasks'])==1)
   ck('28_generated_app_reject_drift',requests.post(burl+'/api/tasks',json={'title':'Other','request_id':request_id},headers=bheaders).status_code==422)
   updated=requests.post(burl+'/api/update',json={'id':job,'state':'DONE'},headers=bheaders)
   ck('29_generated_app_update',updated.status_code==200 and requests.get(burl+'/api/tasks').json()['tasks'][0]['state']=='DONE')
   ck('30_generated_app_deny_token',requests.post(burl+'/api/tasks',json=payload,headers={'Content-Type':'application/json'}).status_code==403)
   ck('31_generated_app_deny_SQL_injection',requests.post(burl+'/api/update',json={'id':job,'state':'DROP TABLE'},headers=bheaders).status_code==422)
   with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) as con:
    con.execute('PRAGMA query_only=ON');ck('32_generated_SQLite_integrity',con.execute('PRAGMA quick_check').fetchone()[0]=='ok')
  finally:stop(bp)
  bp,again=start([sys.executable,'-I','-B',str(path),'serve'],benv,burl,'V2_GENERATED_BOARD_RESTART')
  try:
   jobs=requests.get(burl+'/api/tasks').json()['tasks']
   ck('33_generated_app_restart_id',len(jobs)==1 and jobs[0]['id']==job)
   ck('34_generated_app_restart_state',jobs[0]['state']=='DONE')
  finally:stop(bp)
  stop(hp);hp,page=start([sys.executable,'-B',str(P/'server.py')],env,hurl,'V2_H1_RESTART')
  ck('35_H1_restart_SHA',requests.get(hurl+'/api/verify?task_id='+plan['task_id']).json()['match'])
  ck('36_H1_restart_SQLite',requests.get(hurl+'/api/task?task_id='+plan['task_id']).json()['task']['status']=='PASS_SCOPED')
  with sqlite3.connect('file:'+str(d/'h1/data/tasks.sqlite3')+'?mode=ro',uri=True) as con:
   con.execute('PRAGMA query_only=ON');ck('37_H1_SQLite_quick_check',con.execute('PRAGMA quick_check').fetchone()[0]=='ok')
  path.write_bytes(path.read_bytes()+b'\n# Unauthorized tamper\n')
  ck('38_E06_tamper_detected',requests.get(hurl+'/api/verify?task_id='+plan['task_id']).json()['match'] is False)
  ck('39_E06_tamper_not_served',requests.get(hurl+'/api/file?name='+plan['path']).status_code==400)
  newtoken=re.search('name="enguru-token" content="([0-9a-f]{48})"',page.text).group(1)
  bad=requests.post(hurl+'/api/execute',json={'task_id':plan['task_id']},headers={**auth,'X-Enguru-Token':newtoken}).json()
  ck('40_E06_no_stale_PASS_receipt',bad['status']=='HOLD_INTEGRITY' and bad['receipt'] is None)
  ck('41_E06_no_second_write',len(list((d/'h1/workspace').iterdir()))==1)
  other=requests.post(hurl+'/api/scaffold',json={'kind':'taskboard'},headers={**auth,'X-Enguru-Token':newtoken}).json()
  with sqlite3.connect(d/'h1/data/tasks.sqlite3') as conn:
   conn.execute('UPDATE tasks SET content=? WHERE task_id=?',('# forged trusted template\n',other['task_id']))
   conn.commit()
  checkdrift=requests.post(hurl+'/api/execute',json={'task_id':other['task_id']},headers={**auth,'X-Enguru-Token':newtoken})
  ck('42_E02_template_SHA_drift_denied',checkdrift.status_code==422 and 'HOLD_SCOPED_TEMPLATE_SOURCE_MISMATCH' in checkdrift.text)
  ck('43_E02_drift_no_new_file',not (d/'h1/workspace'/other['path']).exists())
  ck('44_E02_drift_task_status_HOLD',requests.get(hurl+'/api/task?task_id='+other['task_id']).json()['task']['status']=='HOLD')
 finally:stop(hp)
artifact={'schema':'enguru.ulmi.h1.nine.emir.v2.actual_generated_e2e','passed':len(results),'total':len(results),'controls':results,'browser':'HOLD_ADMIN_POLICY','real_qwen':'NOT_EXECUTED','formal_ABC':'HOLD','independent_donecheck':'NOT_EXECUTED','owner_final':'NOT_EXECUTED','verified_finish':'HOLD'}
(E/'E04_E09_TASKBOARD_REAL_E2E_RECEIPT.json').write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n')
print('REAL_GENERATED_APP_TESTS',artifact['passed'],'/',artifact['total'],flush=True)
