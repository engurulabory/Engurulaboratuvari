#!/usr/bin/env python3
"""Real disposable H1 HTTP / SQLite / file / subprocess, three distinct runs.
No synthetic PASS for browser, Qwen, official DoneCheck, owner.
"""
import requests, pathlib,sys,tempfile,subprocess,socket,os,time,re,hashlib,json,sqlite3,uuid
from contextlib import contextmanager
ROOT=pathlib.Path(__file__).resolve().parents[1]
P=ROOT/'PRODUCT'
E=ROOT/'EVIDENCE'
TESTS=[];RUNS=[]
def sha(data):return hashlib.sha256(data).hexdigest()
def check(name,truth,extra=None):
 passed=bool(truth); item={'name':name,'pass':passed,'detail':extra}; TESTS.append(item)
 print(('PASS' if passed else 'FAIL'),name, '' if extra is None else extra,flush=True)
 if not passed:raise AssertionError(name)
def alloc_port():
 with socket.socket() as s:
  s.bind(('127.0.0.1',0));return s.getsockname()[1]
class Engine:
 def __init__(self,home,label):
  self.home=pathlib.Path(home);self.label=label;self.p=alloc_port();self.base=f'http://127.0.0.1:{self.p}';self.proc=None
 def start(self):
  env={**os.environ,'ENGURU_H1_STATE_HOME':str(self.home),'ENGURU_USTA_PORT':str(self.p),'ENGURU_ULMI_CHAT_TEST_MODE':'1','ENGURU_ULMI_P1_ISOLATED':'TRUE'}
  (self.home/'.ulmi-disposable').write_text('ULMI-WORK-H1-P1-ISOLATED\n')
  self.proc=subprocess.Popen([sys.executable,'-B',str(P/'server.py')],env=env,stdout=(E/f'{self.label}_server.log').open('a'),stderr=subprocess.STDOUT)
  for i in range(150):
   if self.proc.poll() is not None:raise RuntimeError('Server stopped: '+(E/f'{self.label}_server.log').read_text()[-1300:])
   try:
    h=requests.get(self.base+'/',timeout=1);break
   except requests.RequestException:time.sleep(.08)
  else:raise RuntimeError('Server timeout')
  self.page=h;self.token=re.search(r'name="enguru-token" content="([a-f0-9]{48})"',h.text).group(1)
  self.headers={'X-Enguru-Token':self.token,'Origin':self.base,'Content-Type':'application/json'}
  return self
 def stop(self):
  if self.proc is not None:self.proc.terminate();self.proc.wait(timeout=6);self.proc=None
 def get(self,path,headers=None):return requests.get(self.base+path,headers=headers,timeout=8)
 def post(self,path,payload,headers=None):return requests.post(self.base+path,json=payload,headers=headers or self.headers,timeout=13)
 def file(self,p):return self.home/'workspace'/p

# SIM1: real construction Python, HTML, AST repair, project, search
with tempfile.TemporaryDirectory(prefix='ulmi_final_sim1_') as d:
 e=Engine(d,'SIM1').start()
 try:
  check('S1_real_HTML_http',e.page.status_code==200 and 'ULMi' in e.page.text)
  check('S1_CSP_same_origin',"script-src 'self'" in e.page.headers.get('Content-Security-Policy',''))
  check('S1_static_assets',all(e.get('/'+p).status_code==200 for p in ('style.css','app.js')))
  check('S1_HTML_filter_and_repair_controls',all(c in e.page.text for c in ['id="task-search"','id="task-status-filter"','id="choice-repair"']))
  project=e.post('/api/desk/projects/save',{'title':'Pilot A İzole','goal':'Gerçek görev üretimi, SQLite ve Python testlerini kanıtla.'})
  check('S1_SQLite_project',project.status_code==200 and bool(project.json()['project']['sha256']))
  projects=e.get('/api/desk/projects',headers={'X-Enguru-Token':e.token})
  check('S1_SQLite_project_readback',any(p['id']==project.json()['project']['id'] for p in projects.json()['projects']))
  # Real trusted Python sample does 3 subprocess unittests after owner on-click action simulated by explicit authorized POST.
  p=e.post('/api/scaffold',{'kind':'python'}).json(); target=e.file(p['path'])
  check('S1_no_file_before_approval',p['status']=='READY' and not target.exists())
  result=e.post('/api/execute',{'task_id':p['task_id']}).json();receipt=result['receipt']
  check('S1_real_Python_subprocess_3_unittests',receipt['functional_test']['status']=='PASS' and 'Ran 3 tests' in receipt['functional_test']['output'])
  check('S1_Python_real_output_SHA',sha(target.read_bytes())==receipt['output_sha256']==receipt['readback_sha256'])
  check('S1_SQLite_receipt_task',e.get('/api/task?task_id='+p['task_id']).json()['task']['receipt']['output_sha256']==receipt['output_sha256'])
  check('S1_real_get_file',e.get('/api/file?name='+p['path']).json()['content']==target.read_text())
  # E05 filter feature: real SQLite SELECT with parameterized matching
  hp=e.post('/api/scaffold',{'kind':'html'}).json();hr=e.post('/api/execute',{'task_id':hp['task_id']}).json()['receipt']
  check('S1_real_HTML_fixture_SHA',e.file(hp['path']).is_file() and sha(e.file(hp['path']).read_bytes())==hr['output_sha256'])
  check('S1_trusted_HTML_preview',e.get('/api/trusted-html?task_id='+hp['task_id']).status_code==200)
  fl=e.get('/api/tasks?search=muhendis_python&status=PASS_SCOPED').json()['tasks']
  check('S1_E05_search_filter_real_rows',len(fl)==1 and fl[0]['task_id']==p['task_id'])
  check('S1_E05_filter_nonexistent',e.get('/api/tasks?search=no_such_file').json()['tasks']==[])
  check('S1_E05_injection_parameter_not_SQL',e.get('/api/tasks?search=%27%20OR%201%3D1').json()['tasks']==[])
  check('S1_E05_invalid_status_rejected',e.get('/api/tasks?status=PASS_SCOPED%27%20OR%201%3D1').status_code==400)
  check('S1_E05_unknown_query_field_rejected',e.get('/api/tasks?owner=grant').status_code==400)
  # E06: true static repair of user-supplied syntactically invalid Python; never executes it.
  original='def topla(a, b)\n    return a + b\n'
  try:compile(original,'user_source','exec');red=False
  except SyntaxError:red=True
  check('S1_E06_real_AST_red',red)
  rp=e.post('/api/capability/repair-plan',{'source':original})
  check('S1_E06_repair_plan_ready',rp.status_code==200 and rp.json()['status']=='READY')
  rtask=rp.json();check('S1_E06_repair_not_written_until_approval',not e.file(rtask['path']).exists())
  rr=e.post('/api/execute',{'task_id':rtask['task_id']}).json()['receipt']
  compile(e.file(rtask['path']).read_text(),'repaired','exec')
  check('S1_E06_real_AST_green',rr['functional_test']['status']=='PASS_SCOPED_STATIC' and rr['functional_test']['repair_proof']['green']=='AST_PARSE_PASS')
  check('S1_E06_untrusted_source_NOT_executed','çalıştırılmadı' in rr['functional_test']['method'])
  check('S1_E06_bad_repair_rejected',e.post('/api/capability/repair-plan',{'source':'import os\nos.system("echo unsafe")'}).status_code==422)
  check('S1_E05_filter_repair_task',len(e.get('/api/tasks?search=python_onarim&status=PASS_SCOPED').json()['tasks'])==1)
  # E06 file evidence anti-tampering, authentic regression on prior RED
  target.write_text('TAMPERED_OUTPUT',encoding='utf8')
  tampered=e.get('/api/file?name='+p['path']);check('S1_E06_green_file_tamper_rejected',tampered.status_code==400 and 'HOLD_OUTPUT_INTEGRITY' in tampered.text)
  repeat=e.post('/api/execute',{'task_id':p['task_id']}).json()
  check('S1_E06_green_duplicate_tampered_hold',repeat['status']=='HOLD_INTEGRITY' and repeat['receipt'] is None)
  check('S1_E06_new_repair_receipt_remains_valid',e.get('/api/verify?task_id='+rtask['task_id']).json()['match'])
  # persist selected ids for a real restart of the server
  live={'project':project.json()['project']['id'],'python':p['task_id'],'html':hp['task_id'],'repair':rtask['task_id'],'sha_html':hr['output_sha256']}
 finally:e.stop()
 e.start()
 try:
  check('S1_restart_reloads_SQLite_task',e.get('/api/task?task_id='+live['repair']).json()['task']['status']=='PASS_SCOPED')
  check('S1_restart_file_SHA_readback',e.get('/api/verify?task_id='+live['html']).json()['sha256']==live['sha_html'])
  check('S1_restart_project_persistence',any(x['id']==live['project'] for x in e.get('/api/desk/projects',headers={'X-Enguru-Token':e.token}).json()['projects']))
  task=e.post('/api/execute',{'task_id':live['html']}).json()
  check('S1_duplicate_no_second_write_after_restart',task.get('already_executed') is True)
  with sqlite3.connect('file:'+str(pathlib.Path(d)/'data'/'tasks.sqlite3')+'?mode=ro',uri=True) as db:
   db.execute('PRAGMA query_only=ON');check('S1_independent_SQLite_quick_check',db.execute('PRAGMA quick_check').fetchone()[0]=='ok')
  RUNS.append({'id':'SIM1','kind':'REAL_HTTP_SQLITE_RESTART_PYTHON_HTML_REPAIR','pass':True,'browser':'NOT_TESTED','qwen':'NOT_TESTED'})
 finally:e.stop()
# SIM2: deliberate adversarial behavior, actual local network only
with tempfile.TemporaryDirectory(prefix='ulmi_final_sim2_') as d:
 e=Engine(d,'SIM2').start()
 try:
  check('S2_denies_missing_token',e.post('/api/scaffold',{'kind':'python'},headers={'Origin':e.base,'Content-Type':'application/json'}).status_code==403)
  check('S2_denies_cross_origin',e.post('/api/scaffold',{'kind':'python'},headers={**e.headers,'Origin':'https://fake-owner.invalid'}).status_code==403)
  check('S2_denies_wrong_host',e.get('/',headers={'Host':'fake-owner.invalid'}).status_code==403)
  check('S2_rejects_undefined_capability',e.post('/api/scaffold',{'kind':'unbounded_shell'}).status_code==422)
  check('S2_rejects_path_traversal',e.get('/api/file?name=..%2Foutside.py').status_code==400)
  check('S2_rejects_unknown_task',e.post('/api/execute',{'task_id':str(uuid.uuid4())}).status_code==422)
  check('S2_rejects_missing_colon_unrepairable',e.post('/api/capability/repair-plan',{'source':'def f(x)\n return +++'}).status_code==422)
  check('S2_denies_long_search',e.get('/api/tasks?search='+'a'*100).status_code==400)
  check('S2_rejects_bad_filter_multiplicity',e.get('/api/tasks?status=READY&status=PASS_SCOPED').status_code==400)
  check('S2_empty_workspace_unmutated',not any((pathlib.Path(d)/'workspace').iterdir()))
  RUNS.append({'id':'SIM2','kind':'REAL_HTTP_ADVERSARIAL_DENY','pass':True,'unauthorized_writes':0})
 finally:e.stop()
# SIM3: native SQLite project snapshot and native restore only in marked disposable test scope
with tempfile.TemporaryDirectory(prefix='ulmi_final_sim3_') as d:
 e=Engine(d,'SIM3').start()
 try:
  p1=e.post('/api/desk/projects/save',{'title':'Kök proje','goal':'İzole kurtarma, kaynak bütünlüğü ve regresyonu ölç.'}).json()['project']
  snap=e.post('/api/desk/snapshot',{});check('S3_disposable_native_snapshot',snap.status_code==200 and 'sha256' in snap.json(),snap.text[:200])
  p2=e.post('/api/desk/projects/save',{'title':'Geçici proje','goal':'Bu proje native restore sonrası bulunmamalıdır.'}).json()['project']
  check('S3_before_restore_two_projects',len(e.get('/api/desk/projects',headers={'X-Enguru-Token':e.token}).json()['projects'])==2)
  restore=e.post('/api/desk/restore',{'snapshot_id':snap.json()['snapshot_id'],'expected_sha256':snap.json()['sha256']})
  check('S3_actual_native_SQLite_restore',restore.status_code==200 and restore.json()['state']=='PASS_SCOPED_NATIVE_RESTORE',restore.text[:200])
  projects=e.get('/api/desk/projects',headers={'X-Enguru-Token':e.token}).json()['projects']
  check('S3_rollback_exact_project_state',len(projects)==1 and projects[0]['id']==p1['id'])
  check('S3_replay_ledger_boundary_not_reset',restore.json()['replay_ledger']=='PRESERVED_NOT_RESTORED')
  with sqlite3.connect('file:'+str(pathlib.Path(d)/'data'/'tasks.sqlite3')+'?mode=ro',uri=True) as db:
   db.execute('PRAGMA query_only=ON');check('S3_SQLite_integrity_after_restore',db.execute('PRAGMA quick_check').fetchone()[0]=='ok')
  RUNS.append({'id':'SIM3','kind':'REAL_HTTP_NATIVE_ROLLBACK_SQLITE','pass':True,'scope':'DISPOSABLE_DESK_ONLY'})
 finally:e.stop()
artifact={'schema':'enguru.ulmi.h1.final.real_e2e_3runs.v1','passed':sum(t['pass'] for t in TESTS),'total':len(TESTS),'tests':TESTS,'runs':RUNS,'real_browser':'NOT_TESTED_ADMIN_BLOCK','real_qwen':'NOT_TESTED_PROVIDER','pilot_A_formal':'0/8','pilot_B_formal':'0/8','pilot_C_formal':'0/8','donecheck_official':'NOT_TESTED','owner_acceptance':'NOT_TESTED','product':'TECHNICALLY_RUNNING_HTML_HTTP_SQLITE_SCOPED'}
(E/'E05_E06_E07_REAL_E2E_TEST_RECEIPT.json').write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n')
print('FINAL_REAL_CHECKS',artifact['passed'],'/',artifact['total'],'RUNS',len(RUNS),flush=True)
