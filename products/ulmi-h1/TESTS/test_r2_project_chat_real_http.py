#!/usr/bin/env python3
"""Actual H1 HTTP→project SHA→synthetic advice→SQLite readback, isolated fixture only.

This checks new UI's existing backend route, not real Qwen or real browser UAT.
"""
import http.client,json,os,sys,tempfile,threading,uuid
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'PRODUCT'));sys.path.insert(0,str(ROOT/'TESTS'))
from test_w04_role_context_contract import Fixture
import server,chat_bridge,contract_bridge

class SyntheticProvider(BaseHTTPRequestHandler):
 def log_message(self,*args): pass
 def do_POST(self):
  n=int(self.headers['Content-Length']); self.rfile.read(n)
  raw=json.dumps({'state':'PASS','output':'ÖNERİ: Projenin gerçek hedefini kaynaklarla inceleyin. <script>alert(1)</script>',
   'route_evidence':{'provider':'synthetic_test','model':'NO_REAL_MODEL',
    'estimated_cost':0,'fallback_path':['synthetic_test:PASS']}}).encode('utf-8')
  self.send_response(200);self.send_header('Content-Type','application/json')
  self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)

def run():
 with tempfile.TemporaryDirectory(prefix='ulmi_r2_chat_real_http_') as d:
  fixture=Fixture(d)
  server.STATE_ROOT=fixture.path; server.DATA=fixture.path/'data';server.WORKSPACE=fixture.path/'workspace';server.DB=server.DATA/'tasks.sqlite3'
  fake=ThreadingHTTPServer(('127.0.0.1',0),SyntheticProvider)
  os.environ['ENGURU_ULMI_SHARED_AI_TEST_PORT']=str(fake.server_port)
  provider_thread=threading.Thread(target=fake.serve_forever,daemon=True);provider_thread.start()
  app=server.make_server(0);app_thread=threading.Thread(target=app.serve_forever,daemon=True);app_thread.start()
  checks=[]
  def ck(name,yes):
   print(('PASS ' if yes else 'FAIL ')+name,flush=True)
   checks.append((name,bool(yes)))
   assert yes,name
  def get(path):
   c=http.client.HTTPConnection('127.0.0.1',app.server_port,timeout=7)
   c.request('GET',path,headers={'X-Enguru-Token':server.TOKEN})
   r=c.getresponse();raw=r.read();code=r.status;headers=dict(r.getheaders());c.close()
   return code,raw,headers
  def post(path,payload,origin=None):
   c=http.client.HTTPConnection('127.0.0.1',app.server_port,timeout=7)
   headers={'Content-Type':'application/json','X-Enguru-Token':server.TOKEN,
    'Origin':origin or f'http://127.0.0.1:{app.server_port}'}
   c.request('POST',path,body=json.dumps(payload,ensure_ascii=False).encode('utf-8'),headers=headers)
   r=c.getresponse();raw=r.read();code=r.status;c.close()
   return code,json.loads(raw)
  try:
   page_code,page_raw,headers=get('/')
   page=page_raw.decode('utf-8')
   ck('REAL_HTTP_HTML_CHAT_PANEL',page_code==200 and 'id="h1-chat"' in page and 'id="chat-send"' in page)
   ck('REAL_HTTP_CSP_NO_INLINE', "script-src 'self'" in headers.get('Content-Security-Policy',''))
   js_code,js_raw,_=get('/app.js')
   ck('ACTUAL_JS_ROUTE_BOUND_AND_TEXTCONTENT',js_code==200 and b'/api/desk/project-chat' in js_raw and b'textContent' in js_raw)
   p1_code,p1=post('/api/desk/projects/save',{'title':'Deneme A','goal':'Gerçek kaynaklardan etik mühendislik önerisi üret.'})
   p2_code,p2=post('/api/desk/projects/save',{'title':'Deneme B','goal':'Başka bir proje ile izolasyon sınaması.'})
   ck('PROJECT_ROWS_WRITTEN',p1_code==200 and p2_code==200 and p1['project']['sha256']!=p2['project']['sha256'])
   project=p1['project'];msg_id=str(uuid.uuid4());payload={'project_id':project['id'],'project_sha256':project['sha256'],
    'message_id':msg_id,'text':'Bu projenin test kapsamını öner.', 'requested_action':'ADVISE_ONLY'}
   code,wrong=post('/api/desk/project-chat',{**payload,'project_sha256':'0'*64})
   ck('WRONG_PROJECT_SHA_HOLD',code==422 and wrong.get('reason')=='HOLD_PROJECT_SCOPE_OR_SHA')
   code,cross=post('/api/desk/project-chat',payload,origin='http://evil.example')
   ck('CROSS_ORIGIN_HOLD',code==403)
   with patch.object(contract_bridge,'preview',return_value={'gates':{'owner_execution':'HOLD_NO_GRANT'},'contract_sha256':contract_bridge.CONTRACT_PIN}):
    code,answer=post('/api/desk/project-chat',payload)
    ck('REAL_HTTP_SYNTHETIC_ADVICE',code==200 and answer['state']=='ADVICE_PROPOSAL_TEST_FIXTURE' and answer['execution_state']=='NOT_EXECUTED')
    code,replay=post('/api/desk/project-chat',payload)
    ck('DURABLE_IDEMPOTENCY_REJECTS_REPEAT',code==422 and replay['reason'].startswith('HOLD_'))
   code,h1,_=get('/api/desk/history?project_id='+project['id'])
   code2,h2,_=get('/api/desk/history?project_id='+p2['project']['id'])
   a=json.loads(h1);b=json.loads(h2)
   ck('SQLITE_HISTORY_SAME_PROJECT',code==200 and len(a['messages'])==1 and a['messages'][0]['message_id']==msg_id)
   ck('OTHER_PROJECT_HAS_NO_HISTORY',code2==200 and len(b['messages'])==0)
   ck('SYNTHETIC_HTML_INERT_STRING_ONLY', '<script>alert(1)</script>' in a['messages'][0]['response']['model_output'])
   ck('NO_FAKE_DONECHECK_OR_OWNER',a['messages'][0]['response']['donecheck_state']=='NOT_EXECUTED' and a['messages'][0]['response']['authority']=='OWNER_GRANT_NOT_PRESENT')
   with server.db_conn() as conn:
    ck('NO_ENGINEERING_EXECUTION',conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]==0)
   return {'schema':'enguru.ulmi.h1.r2.project-chat-http-test/v1','tests':len(checks),
    'passed':sum(v for _,v in checks),'checks':[{'name':n,'pass':v} for n,v in checks],
    'real_http':True,'synthetic_ai':True,'real_qwen':'NOT_EXECUTED','browser_uat':'NOT_EXECUTED','owner_grant':'NOT_ISSUED'}
  finally:
   app.shutdown();app.server_close();app_thread.join(timeout=3)
   fake.shutdown();fake.server_close();provider_thread.join(timeout=3)

if __name__=='__main__':
 print(json.dumps(run(),ensure_ascii=False,sort_keys=True),flush=True)
