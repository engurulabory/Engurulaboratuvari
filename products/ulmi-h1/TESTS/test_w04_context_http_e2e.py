#!/usr/bin/env python3
"""Actual H1 HTTP /api/desk/chat against a SYNTHETIC context/provider.
Confirms W04 source validation reaches the HTTP gate without grant or execution.
"""
import http.client, json, os, sys, tempfile,threading, uuid
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'PRODUCT'))
sys.path.insert(0,str(ROOT/'TESTS'))
from test_w04_role_context_contract import Fixture
import chat_bridge,contract_bridge,server as ulmi

class FakeSharedAI(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  self.rfile.read(int(self.headers['Content-Length']))
  raw=json.dumps({'state':'PASS','output':'SENTETIK UYGULAMA YETKISI OLMAYAN TEST YANITI',
    'route_evidence':{'provider':'synthetic_test','model':'NO_REAL_MODEL',
     'estimated_cost':0,'fallback_path':['synthetic_test:PASS']}}).encode()
  self.send_response(200);self.send_header('Content-Type','application/json')
  self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)

checks=[]
def ck(name,yes,observed):
 checks.append({'id':name,'status':'PASS' if yes else 'FAIL','observed':str(observed)[:400]})
 print(('PASS' if yes else 'FAIL'),name,observed,flush=True)
 if not yes:raise AssertionError(name)

with tempfile.TemporaryDirectory(prefix='ulmi_v71_w04_real_http_') as d:
 f=Fixture(d)
 # server imports are already loaded from actual V7.1 PRODUCT. It must have the disposable state root.
 ulmi.STATE_ROOT=f.path;ulmi.DATA=f.path/'data';ulmi.WORKSPACE=f.path/'workspace';ulmi.DB=ulmi.DATA/'tasks.sqlite3'
 fake=ThreadingHTTPServer(('127.0.0.1',0),FakeSharedAI)
 os.environ['ENGURU_ULMI_SHARED_AI_TEST_PORT']=str(fake.server_port)
 ft=threading.Thread(target=fake.serve_forever,daemon=True);ft.start()
 srv=ulmi.make_server(0);t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
 try:
  def call(origin=True,project=contract_bridge.CONTRACT_ID):
   port=srv.server_port
   dct={'project_id':project,'contract_revision':1,'contract_sha256':contract_bridge.CONTRACT_PIN,
         'message_id':str(uuid.uuid4()),'text':'Türkçe mühendislik görevi', 'requested_action':'ADVISE_ONLY'}
   c=http.client.HTTPConnection('127.0.0.1',port,timeout=5)
   h={'Content-Type':'application/json','X-Enguru-Token':ulmi.TOKEN,
      'Origin':f'http://127.0.0.1:{port}' if origin else 'http://evil.invalid'}
   c.request('POST','/api/desk/chat',body=json.dumps(dct).encode(),headers=h)
   res=c.getresponse();body=json.loads(res.read());c.close();return res.status,body
  with patch.object(contract_bridge,'preview',return_value={'gates':{'owner_execution':'HOLD_NO_GRANT'},'contract_sha256':contract_bridge.CONTRACT_PIN}):
   f.versions['POZITIF_DIL']='INCONSISTENT-CANONICAL-REV';f.rewrite()
   status,resp=call();ck('CONFLICTING_ROLE_VERSION_HTTP_422',status==422 and resp.get('reason')=='HOLD_CONTEXT_SHARED_VERSION',(status,resp))
   f.versions['POZITIF_DIL']='synthetic-test-v1';f.rewrite()
   # Tamper source file while retaining its owner-pinned fixture manifest.
   (f.sources/'agents.txt').write_bytes(b'CHANGED_AFTER_MANIFEST_SHA')
   status,resp=call();ck('TAMPERED_SOURCE_HTTP_422',status==422 and resp.get('reason')=='HOLD_CONTEXT_SOURCE_SHA',(status,resp))
   f.rewrite()
   status,resp=call(origin=False);ck('CROSS_ORIGIN_DENIED_HTTP_403',status==403,status)
   status,resp=call(project='other-product');ck('WRONG_PROJECT_ID_HTTP_422',status==422 and resp.get('reason')=='HOLD_PROJECT_ID',(status,resp))
   status,resp=call();ck('SYNTHETIC_SOURCE_ONLY_ADVICE_HTTP_200',status==200 and resp.get('state')=='ADVICE_PROPOSAL_TEST_FIXTURE',(status,resp.get('state')))
   ck('NO_EXECUTION_OR_DONECHECK',resp.get('execution_state')=='NOT_EXECUTED' and resp.get('donecheck_state')=='NOT_EXECUTED',str({k:resp.get(k) for k in ('execution_state','donecheck_state')}))
   import sqlite3
   with sqlite3.connect(ulmi.DB) as db:n=db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
   ck('NO_WRITTEN_ENGINEERING_TASKS',n==0,n)
 finally:
  srv.shutdown();srv.server_close();t.join(timeout=3);fake.shutdown();fake.server_close();ft.join(timeout=3)
report={'schema':'enguru.ulmi.h1.w04.v71.real-http-synthetic-source-contract/v1','checks':checks,
 'passed':len(checks),'total':len(checks),'source':'V7.1 actual H1 /api/desk/chat via 127.0.0.1',
 'synthetic_context':True,'synthetic_provider':True,'real_qwen':'NOT_EXECUTED',
 'independent_owner_approval':'NOT_ISSUED','formal_original_W04':'HOLD'}
(ROOT/'EVIDENCE/V71_W04_REAL_HTTP_NEGATIVE.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
