#!/usr/bin/env python3
"""Shared AI route/isolation and source authority, SYNTHETIC HTTP only.
No real Qwen request. Deliberately keeps W01/W04/W05/W06/W09 canonical HOLD.
"""
import hashlib,json,os,sys,tempfile,threading,uuid
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'PRODUCT'))
import chat_bridge,contract_bridge
checks=[]
def ck(name,ok,observed=''):
 checks.append({'id':name,'passed':bool(ok),'observed':str(observed)[:250]})
 print(('PASS' if ok else 'FAIL'),name,str(observed)[:70],flush=True)

class SimulatedSharedAI(BaseHTTPRequestHandler):
 scenario='GOOD';requests=[]
 def log_message(self,*a):pass
 def do_POST(self):
  raw=self.rfile.read(int(self.headers['Content-Length']));self.__class__.requests.append((self.path,raw))
  route={'provider':'synthetic_test','model':'NO_REAL_MODEL','estimated_cost':0.0,'fallback_path':['synthetic_test:PASS']}
  body={'state':'PASS','output':'Bu metin sentetik test cevabıdır; gerçek model değildir.','route_evidence':route}
  v=self.__class__.scenario
  if v=='WRONG_PROVIDER':route['provider']='remote'
  if v=='WRONG_MODEL':route['model']='qwen3:14b'
  if v=='PAID':route['estimated_cost']=1.0
  if v=='REMOTE_FALLBACK':route['fallback_path']=['remote:PASS']
  if v=='WRONG_STATE':body['state']='HOLD'
  if v=='EMPTY':body['output']=' '
  if v=='OVERSIZE':body['output']='A'*11000
  if v=='MISSING_ROUTE':del body['route_evidence']
  if v=='DUPLICATE_JSON':resp=b'{"state":"PASS","state":"HOLD","output":"OK","route_evidence":{}}'
  elif v=='INVALID_JSON':resp=b'{not-json'
  else:resp=json.dumps(body).encode()
  if v=='HTTP_ERROR':self.send_response(503)
  elif v=='REDIRECT':self.send_response(302);self.send_header('Location','http://example.invalid/steal')
  else:self.send_response(200)
  self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(resp)));self.end_headers()
  try:self.wfile.write(resp)
  except BrokenPipeError:pass

with tempfile.TemporaryDirectory(prefix='ulmi_v7_sharedai_isolation_') as t:
 root=Path(t).resolve();(root/'.ulmi-disposable').write_text('ULMI-WORK-H1-P1-ISOLATED\n')
 os.environ.update({'ENGURU_H1_STATE_HOME':str(root),'ENGURU_ULMI_CHAT_TEST_MODE':'1','ENGURU_ULMI_P1_ISOLATED':'TRUE'})
 mock=ThreadingHTTPServer(('127.0.0.1',0),SimulatedSharedAI)
 os.environ['ENGURU_ULMI_SHARED_AI_TEST_PORT']=str(mock.server_port)
 worker=threading.Thread(target=mock.serve_forever,daemon=True);worker.start()
 try:
  for v in ['GOOD','WRONG_PROVIDER','WRONG_MODEL','PAID','REMOTE_FALLBACK',
            'WRONG_STATE','EMPTY','OVERSIZE','MISSING_ROUTE','DUPLICATE_JSON',
            'INVALID_JSON','HTTP_ERROR','REDIRECT']:
   SimulatedSharedAI.scenario=v
   try:
    output,route=chat_bridge.shared_ai_request('Test mühendislik önerisi',[],'SYNTHETIC_SAMPLE')
    accepted=True
   except chat_bridge.Hold as e:accepted=False;output=e.reason
   ck('SHARED_AI_'+v,accepted if v=='GOOD' else not accepted,output)
  ck('STRICT_SYNTHETIC_ISOLATION_ROUTE',all(path=='/v1/enguru/respond' for path,raw in SimulatedSharedAI.requests),len(SimulatedSharedAI.requests))
  last=json.loads(SimulatedSharedAI.requests[0][1])
  ck('NO_TOOLS_AND_ZERO_PAID_ROUTE',last['tool_plan']==[] and last['requested_tool'] is None and last['cost_ceiling']==0, last['task_type'])
  ck('DIRECT_OLLAMA_VS_SHARED_AI_SEPARATION',chat_bridge.shared_ai_request.__code__.co_consts.__contains__('http://127.0.0.1:') and 'local_runtime' in chat_bridge.shared_ai_request.__code__.co_consts.__str__(), 'self-reported route not independent')
  # Non-real source context must remain a HOLD without separately pinned owner source bundles.
  for e in ('ENGURU_ULMI_CHAT_CONTRACT_FILE','ENGURU_ULMI_TRUSTED_BASELINE_ROOT',
            'ENGURU_ULMI_CHAT_CONTEXT_ROOT','ENGURU_ULMI_CHAT_CONTEXT_MANIFEST_SHA256'):
   os.environ.pop(e,None)
  try:chat_bridge.approved_context();fail=False
  except chat_bridge.Hold as e:fail=e.reason=='HOLD_TRUSTED_CONTEXT_NOT_CONFIGURED'
  ck('W01_W04_TRUSTED_CONTEXT_FAIL_CLOSED',fail,'HOLD_TRUSTED_CONTEXT_NOT_CONFIGURED')
  ck('SOURCE_ROLE_ORACLES_RETAINED',len(chat_bridge.REQUIRED_ROLES)==8 and len(set(chat_bridge.CANONICAL_PINS.values()))==6,len(chat_bridge.REQUIRED_ROLES))
 finally:
  mock.shutdown();mock.server_close();worker.join(timeout=3)
result={'schema':'enguru.ulmi.h1.v7.shared-ai-source-boundary-tests/v1',
 'passed':sum(x['passed'] for x in checks),'total':len(checks),'checks':checks,
 'network':'ACTUAL_LOOPBACK_HTTP_TO_SYNTHETIC_PROVIDER',
 'genuine_qwen':'NOT_EXECUTED','canonical_owner_source_bundle':'HOLD_NOT_CONFIGURED',
 'independent_producer_identity':'HOLD_NOT_ATTESTED','pilot_BC_owner_grant':'NOT_ISSUED',
 'authority':'NOT_GRANTED','verdict':'PASS_SCOPED_SYNTHETIC_NEGATIVE_ONLY' if all(x['passed'] for x in checks) else 'HOLD'}
(ROOT/'EVIDENCE/V7_SHARED_AI_SOURCE_BOUNDARY_TESTS.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('V7_SHARED_AI',result['passed'],'/',result['total'])
if result['passed']!=result['total']:sys.exit(1)
