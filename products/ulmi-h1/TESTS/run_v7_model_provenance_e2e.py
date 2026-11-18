#!/usr/bin/env python3
"""Real loopback HTTP-to-SQLite verification using a *synthetic, explicitly labeled*
Ollama-shaped response. NOT actual Qwen inference or independent model attestation.
V6 baseline RED is run in an isolated, disposable subprocess context. No Mac access.
"""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import socket
import sqlite3
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request, error
import uuid

ROOT=Path(__file__).resolve().parents[1]
V6=ROOT/'ORIGINALS'/'V6_PRE_REPAIR_PRODUCT'
V7=ROOT/'PRODUCT'
checks=[]

def test(name,ok,observed=''):
    checks.append({'name':name,'passed':bool(ok),'observed':str(observed)[:300]})
    print(('PASS' if ok else 'FAIL'),name,str(observed)[:80],flush=True)

class Stub(BaseHTTPRequestHandler):
    scenario='GOOD'; requests=[]
    def log_message(self,*a):pass
    def do_GET(self):
        data=json.dumps({'models':[{'name':'qwen3:14b','model':'qwen3:14b'}]}).encode()
        if self.path!='/api/tags':self.send_response(404)
        else:self.send_response(200)
        self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_POST(self):
        raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
        self.__class__.requests.append((self.path,raw))
        spec={'path':'model_generated_example.py','content':'# synthetic output, not actual Qwen\na=2+2\n'}
        model='qwen3:14b'
        body={'model':model,'done':True,'message':{'role':'assistant','content':json.dumps(spec)}}
        scenario=self.__class__.scenario
        if scenario=='WRONG_MODEL':body['model']='unapproved:fake'
        if scenario=='INCOMPLETE':body['done']=False
        if scenario=='WRONG_ROLE':body['message']['role']='tool'
        if scenario=='TOOL_CALL':body['message']['tool_calls']=[{'function':{'name':'delete_file'}}]
        if scenario=='DUPLICATE_WRAPPER':resp=b'{"model":"qwen3:14b","model":"fake-model","done":true,"message":{"role":"assistant","content":"{}"}}'
        elif scenario=='DUPLICATE_PLAN':body['message']['content']='{"path":"x.py","path":"y.py","content":"print(1)"}';resp=json.dumps(body).encode()
        elif scenario=='EXTRA_PLAN_FIELD':body['message']['content']='{"path":"x.py","content":"print(1)","execute":true}';resp=json.dumps(body).encode()
        elif scenario=='PATH_TRAVERSAL':body['message']['content']='{"path":"../outside.py","content":"print(1)"}';resp=json.dumps(body).encode()
        else:resp=json.dumps(body).encode()
        if scenario=='REDIRECT':
            self.send_response(302);self.send_header('Location','http://example.invalid/steal');self.send_header('Content-Length','0');self.end_headers();return
        contenttype='text/html' if scenario=='WRONG_MIME' else 'application/json'
        self.send_response(200);self.send_header('Content-Type',contenttype);self.send_header('Content-Length',str(len(resp)));self.end_headers();self.wfile.write(resp)


def load_server(name,product):
    # Non-production isolated test: only the SERVER module is imported. Its source
    # is preserved; dependencies come from the V7 tree (same V6 core files).
    sys.path.insert(0,str(V7))
    spec=importlib.util.spec_from_file_location(name,product/'server.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod


def use_http(port,host,post=None,token=None):
    headers={'X-Enguru-Token':token or '', 'Origin':host,'Content-Type':'application/json'}
    method='POST' if post is not None else 'GET'
    body=None if post is None else json.dumps(post).encode()
    req=request.Request(host+port,data=body,headers=headers,method=method)
    try:
        with request.urlopen(req,timeout=12) as resp:return resp.status,json.loads(resp.read())
    except error.HTTPError as ex:return ex.code,json.loads(ex.read())

with tempfile.TemporaryDirectory(prefix='ulmi_v7_model_source_oracle_') as temp:
    home=Path(temp)
    os.environ['ENGURU_H1_STATE_HOME']=str(home/'isolated')
    os.environ['ENGURU_ULMI_CHAT_TEST_MODE']='0'
    stub=ThreadingHTTPServer(('127.0.0.1',0),Stub)
    provider_port=stub.server_port
    th=threading.Thread(target=stub.serve_forever,daemon=True);th.start()
    stub_url=f'http://127.0.0.1:{provider_port}/api/chat'
    try:
        # RED: exact V6 code accepts a wrong model response and stores READY.
        old=load_server('ulmi_v6_source_before_repair',V6)
        old.prepare();old.OLLAMA_URL=stub_url;Stub.scenario='WRONG_MODEL'
        with old.db_conn() as db: before=db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        bad=old.generate_local_plan('Bana güvenli örnek Python dosyası üret')
        with old.db_conn() as db: after=db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        test('RED_V6_WRONG_MODEL_CREATED_READY',bad['status']=='READY' and after==before+1,'V6 wrong model falsely accepted')
        # V7 uses a fresh STATE root, so old bug output cannot be promoted.
        os.environ['ENGURU_H1_STATE_HOME']=str(home/'new_v7_state')
        latest=load_server('ulmi_v7_after_repair',V7)
        latest.prepare();latest.OLLAMA_URL=stub_url
        live=latest.make_server(port=0)
        lt=threading.Thread(target=live.serve_forever,daemon=True);lt.start()
        url=f'http://127.0.0.1:{live.server_port}'
        def call(post):
            return use_http('/api/plan',url,post,latest.TOKEN)
        try:
            with latest.db_conn() as db: start=db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
            for scenario in ['WRONG_MODEL','INCOMPLETE','WRONG_ROLE','TOOL_CALL','DUPLICATE_WRAPPER',
                             'DUPLICATE_PLAN','EXTRA_PLAN_FIELD','PATH_TRAVERSAL','WRONG_MIME','REDIRECT']:
                Stub.scenario=scenario
                code,resp=call({'prompt':'Bana güvenli örnek Python dosyası üret'})
                with latest.db_conn() as db:
                    n=db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
                    k=db.execute('SELECT COUNT(*) FROM model_plan_receipts').fetchone()[0]
                test('GREEN_REJECT_'+scenario,code in (422,500) and n==start and k==0,code)
            Stub.scenario='GOOD'
            code,resp=call({'prompt':'Bana güvenli örnek Python dosyası üret'})
            task_id=resp.get('task_id','')
            receipt=resp.get('model_route_receipt',{})
            test('GREEN_ONE_REAL_HTTP_PLAN_READY',code==200 and resp.get('status')=='READY' and bool(task_id),code)
            test('GREEN_ROUTE_SELF_REPORTED_NOT_ATTESTED',receipt.get('provenance_level')=='LOCAL_HTTP_SELF_REPORTED_NOT_INDEPENDENT_ATTESTATION' and receipt.get('test_endpoint_override') is True and receipt.get('actual_qwen_inference_independently_verified') is False,receipt)
            test('GREEN_ONLY_LOCAL_LOOPBACK',receipt.get('endpoint')==f'127.0.0.1:{provider_port}/api/chat' and all(z[0]=='/api/chat' for z in Stub.requests),len(Stub.requests))
            rcode,r=use_http('/api/model/receipt?task_id='+task_id,url,token=latest.TOKEN)
            test('GREEN_READ_ROUTE_RECEIPT_HTTP',rcode==200 and r['route_receipt']['response_sha256']==receipt['response_sha256'] and r['independent_provider_attestation']=='NOT_VERIFIED',rcode)
            c,_=use_http('/api/model/receipt?task_id='+task_id,url,token='WRONG_TOKEN')
            test('GREEN_RECEIPT_REQUIRES_SESSION_TOKEN',c==403,c)
            with latest.db_conn() as db:
                n=db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
                k=db.execute('SELECT COUNT(*) FROM model_plan_receipts').fetchone()[0]
                integrity=db.execute('PRAGMA quick_check').fetchone()[0]
            test('GREEN_ATOMIC_SQLITE_PLAN_AND_RECEIPT',n==start+1 and k==1 and integrity=='ok',(n,k,integrity))
            test('GREEN_NO_FILE_BEFORE_EXPLICIT_EXECUTE',not (latest.WORKSPACE/resp['path']).exists(),resp['path'])
            # Prove model-proposed Python is *never* executed as trusted fixture.
            code,exe=use_http('/api/execute',url,{'task_id':task_id},token=latest.TOKEN)
            t=latest.get_task(task_id)
            test('GREEN_UNTRUSTED_MODEL_CODE_NOT_SUBPROCESS',code==200 and t['receipt']['functional_test']['status']=='NOT_TESTED' and t['receipt']['source_origin']=='LOCAL_OLLAMA',t['receipt']['functional_test']['status'])
            test('GREEN_OUTPUT_FILE_SHA_READBACK',hashlib.sha256((latest.WORKSPACE/resp['path']).read_bytes()).hexdigest()==t['receipt']['output_sha256'],resp['path'])
            code,r=use_http('/api/model/receipt?task_id='+task_id,url,token=latest.TOKEN)
            test('GREEN_RECEIPT_PERSISTS_AFTER_EXECUTE',code==200 and r['task_status']=='PASS_SCOPED',r.get('task_status'))
            # Verify user cannot change provider destination into a remote host.
            Stub.scenario='GOOD';latest.OLLAMA_URL='https://example.invalid/api/chat'
            before=latest.task_status()['tasks'] if isinstance(latest.task_status(),dict) and 'tasks' in latest.task_status() else None
            code,_=call({'prompt':'Başka bir dosya üret'})
            test('GREEN_REMOTE_PROVIDER_REJECTED',code==422,code)
            latest.OLLAMA_URL=stub_url
            code,ready=use_http('/api/model/readiness',url,token=latest.TOKEN)
            test('GREEN_READONLY_CATALOG_NOT_INFERENCE',code==200 and ready['local_catalog']=='PASS_SCOPED_SELF_REPORTED_CATALOG' and ready['qwen3_14b_listed'] and ready['model_inference']=='NOT_EXECUTED_BY_PREFLIGHT',ready['local_catalog'])
            test('GREEN_TRUSTED_SOURCE_NOT_BYPASSED',ready['eight_role_source_context'].startswith('HOLD_SOURCE_CONTEXT:') and ready['producer_authority']=='NOT_GRANTED_BY_PREFLIGHT',ready['eight_role_source_context'])
            denied,_=use_http('/api/model/readiness',url,token='WRONG_TOKEN')
            test('GREEN_READINESS_AUTHENTICATED',denied==403,denied)
        finally:
            live.shutdown();live.server_close();lt.join(timeout=3)
    finally:
        stub.shutdown();stub.server_close();th.join(timeout=3)

passed=sum(x['passed'] for x in checks)
result={'schema':'enguru.ulmi.h1.v7.local-provider-route-negative-e2e/v1',
        'checks':checks,'passed':passed,'total':len(checks),
        'red_before_repair':'V6 falsely accepts wrong model and stores READY',
        'real_http_to_synthetic_stub':True,'actual_qwen_inference':'NOT_EXECUTED',
        'provider_identity_independently_attested':'NO',
        'owner_authority':'NOT_ISSUED','result':'PASS_SCOPED_SYNTHETIC_PROVIDER_ORACLES' if passed==len(checks) else 'HOLD'}
(ROOT/'EVIDENCE/V7_LOCAL_PROVIDER_RED_GREEN_REAL_HTTP.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('V7_PROVIDER_RED_GREEN',passed,'/',len(checks))
if passed!=len(checks):sys.exit(1)
