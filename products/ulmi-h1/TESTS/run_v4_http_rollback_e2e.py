#!/usr/bin/env python3
"""Genuine disposable localhost HTTP + SQLite + fault injection: no browser claim."""
from __future__ import annotations
import sys,os,pathlib,tempfile,threading,urllib.request,urllib.error,json,types,hashlib
from unittest.mock import patch
R=pathlib.Path(__file__).resolve().parents[1]/'PRODUCT'
sys.path.insert(0,str(R))
with tempfile.TemporaryDirectory(prefix='ulmi-h1-v4-http-') as home:
    os.environ['ENGURU_H1_STATE_HOME']=home
    import server
    app=server.make_server(port=0)
    th=threading.Thread(target=app.serve_forever,daemon=True); th.start()
    port=app.server_port
    origin=f'http://127.0.0.1:{port}'
    checks=[]
    def check(name,truth):
        assert truth,name
        checks.append(name);print('PASS',name,flush=True)
    def req(method,path,data=None,token=True,origin_good=True):
        header={'X-Enguru-Token':server.TOKEN} if token else {}
        if method=='POST':
            header['Content-Type']='application/json'
            if origin_good:header['Origin']=origin
        raw=None if data is None else json.dumps(data).encode()
        request=urllib.request.Request(origin+path,data=raw,headers=header,method=method)
        try:
            with urllib.request.urlopen(request,timeout=10) as r:return r.status, r.read(),dict(r.headers)
        except urllib.error.HTTPError as ex:return ex.code,ex.read(),dict(ex.headers)
    try:
        code,body,headers=req('GET','/')
        check('01_product_real_HTTP_200',code==200 and b'ULMi' in body)
        check('02_browser_token_embedded',server.TOKEN.encode() in body and headers.get('Content-Security-Policy') is not None)
        code,body,_=req('POST','/api/scaffold',{'kind':'python'})
        task=json.loads(body)
        check('03_real_HTTP_plan_READY',code==200 and task['status']=='READY')
        fn=task['path'];target=server.WORKSPACE/fn;tid=task['task_id']
        check('04_no_write_before_execute',not target.exists())
        failure=types.SimpleNamespace(returncode=1,stdout='',stderr='Ran 3 tests\nFAILED')
        with patch.object(server.subprocess,'run',return_value=failure):
            code,body,_=req('POST','/api/execute',{'task_id':tid})
        check('05_real_HTTP_failed_execution_rejected',code==422 and b'HOLD' in body)
        check('06_no_new_file_after_failure',not target.exists())
        code,body,_=req('GET','/api/task?task_id='+tid)
        record=json.loads(body)['task']
        check('07_real_HTTP_durable_HOLD',record['status']=='HOLD' and record['receipt'] is None)
        code,body,_=req('POST','/api/execute',{'task_id':tid})
        check('08_replay_fail_closed',code==422 and not target.exists())
        code,body,_=req('POST','/api/scaffold',{'kind':'python'})
        new=json.loads(body)
        good_id=new['task_id']
        code,body,_=req('POST','/api/execute',{'task_id':good_id})
        receipt=json.loads(body)
        check('09_real_3_tests_pass',code==200 and receipt['receipt']['functional_test']['status']=='PASS' and 'Ran 3 tests' in receipt['receipt']['functional_test']['output'])
        good_file=server.WORKSPACE/new['path']
        check('10_readback_SHA_identical',hashlib.sha256(good_file.read_bytes()).hexdigest()==receipt['receipt']['output_sha256'])
        code,body,_=req('GET','/api/verify?task_id='+good_id)
        check('11_HTTP_SHA_verification',json.loads(body)['status']=='PASS_SCOPED_READBACK')
        code,body,_=req('POST','/api/execute',{'task_id':good_id})
        check('12_duplicate_no_second_write',code==200 and json.loads(body)['already_executed'] is True)
        code,body,_=req('GET','/api/files')
        check('13_only_successful_file_listed',any(x['name']==new['path'] for x in json.loads(body)['files']) and all(x['name']!=fn for x in json.loads(body)['files']))
        code,body,_=req('POST','/api/scaffold',{'kind':'python'},token=False)
        check('14_wrong_token_no_plan',code==403)
        code,body,_=req('POST','/api/scaffold',{'kind':'python'},origin_good=False)
        check('15_missing_origin_denied_for_write',code==403)
        # Read-only SQLite integrity state, independent from HTTP.
        with server.db_conn() as db:
            check('16_SQLite_quick_check',db.execute('PRAGMA quick_check').fetchone()[0]=='ok')
            check('17_two_distinct_task_states',db.execute('SELECT status FROM tasks WHERE task_id=?',(tid,)).fetchone()[0]=='HOLD' and db.execute('SELECT status FROM tasks WHERE task_id=?',(good_id,)).fetchone()[0]=='PASS_SCOPED')
    finally:
        app.shutdown();app.server_close();th.join(timeout=5)
    print('V4_REAL_HTTP_ROLLBACK_TESTS',len(checks),'/',17,'BROWSER_NOT_TESTED',flush=True)
