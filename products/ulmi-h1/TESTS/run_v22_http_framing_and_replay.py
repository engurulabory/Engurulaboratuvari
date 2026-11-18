#!/usr/bin/env python3
"""V22 W07 negative HTTP framing and durable replay tests on isolated H1 V5/V6.
This exercises real ThreadingHTTPServer bound to loopback and disposable SQLite.
"""
import argparse, hashlib, importlib, json, os, re, socket, sys, tempfile, threading, time
from pathlib import Path
from urllib.request import urlopen
import requests

parser=argparse.ArgumentParser();parser.add_argument('--product',required=True);parser.add_argument('--out',required=True);parser.add_argument('--stress',type=int,default=0)
args=parser.parse_args()
product=Path(args.product).resolve();out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
checks=[];errors=[]
def check(name,passed,detail):
    checks.append({'id':name,'passed':bool(passed),'detail':str(detail)[:260]})
    print(('PASS' if passed else 'FAIL'),name,str(detail)[:90],flush=True)
    if not passed: errors.append(name)

def raw_post(port,token,payload,header_lines):
    body=json.dumps(payload,separators=(',',':')).encode()
    headers=[f'POST /api/scaffold HTTP/1.1',f'Host: 127.0.0.1:{port}',f'Origin: http://127.0.0.1:{port}',f'X-Enguru-Token: {token}',f'Connection: close',*header_lines,'','']
    data='\r\n'.join(headers).encode('ascii')+body
    with socket.create_connection(('127.0.0.1',port),timeout=5) as s:
        s.settimeout(5);s.sendall(data);chunks=[]
        while True:
            try: x=s.recv(65536)
            except socket.timeout:break
            if not x:break
            chunks.append(x)
    raw=b''.join(chunks)
    match=re.match(rb'HTTP/1\.1\s+(\d+)',raw)
    return (int(match.group(1)) if match else None),raw[:1200].decode('utf8','replace')

with tempfile.TemporaryDirectory(prefix='ulmi_w07_disposable_') as tmp:
    os.environ['ENGURU_H1_STATE_HOME']=tmp
    sys.path.insert(0,str(product))
    import server as s
    srv=s.make_server(0);port=srv.server_port;url=f'http://127.0.0.1:{port}'
    thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
    try:
        page=requests.get(url+'/uat-final',timeout=5).text
        m=re.search(r'<meta name="enguru-token" content="([a-f0-9]+)"',page)
        assert m,'No token in served page';token=m.group(1)
        body=json.dumps({'kind':'python'},separators=(',',':')).encode();length=len(body)
        tests=[
            ('DUPLICATE_CONTENT_LENGTH', [f'Content-Length: {length}',f'Content-Length: {length}','Content-Type: application/json'],400),
            ('CONFLICTING_CONTENT_LENGTH', [f'Content-Length: {length}',f'Content-Length: {length+1}','Content-Type: application/json'],400),
            ('TRANSFER_ENCODING_AND_LENGTH',[f'Content-Length: {length}','Transfer-Encoding: chunked','Content-Type: application/json'],400),
            ('WRONG_CONTENT_TYPE',[f'Content-Length: {length}','Content-Type: text/plain'],415),
        ]
        for case,headers,expected in tests:
            count_before=len(s.list_tasks())
            code,resp=raw_post(port,token,{'kind':'python'},headers)
            count_after=len(s.list_tasks())
            check(case,code==expected and count_before==count_after,{'expected_status':expected,'observed_status':code,'new_plans':count_after-count_before,'raw_prefix':resp[:75]})
        good=requests.post(url+'/api/scaffold',json={'kind':'python'},headers={'X-Enguru-Token':token,'Origin':url},timeout=5)
        check('POSITIVE_PLAN_AFTER_FRAMING',good.status_code==200,good.status_code)
        if good.status_code==200:
            tid=good.json()['task_id']
            execute=requests.post(url+'/api/execute',json={'task_id':tid},headers={'X-Enguru-Token':token,'Origin':url},timeout=10)
            if execute.status_code==200:
                sha=execute.json().get('receipt',{}).get('output_sha256')
                check('POSITIVE_REAL_EXECUTE',execute.json().get('status')=='PASS_SCOPED',sha)
                # The replay attack is tested against the same task id, never creating a fresh plan.
                if args.stress:
                    t=time.monotonic();bad=0;different=0
                    for i in range(args.stress):
                        result=s.execute(tid)
                        if result.get('status')!='PASS_SCOPED' or not result.get('already_executed') or result.get('receipt',{}).get('output_sha256')!=sha:bad+=1
                    duration=round(time.monotonic()-t,2)
                    stored=s.get_task(tid)
                    check('CORE_REPLAY_STRESS_'+str(args.stress),bad==0 and stored['status']=='PASS_SCOPED',{'calls':args.stress,'errors':bad,'duration_seconds':duration,'source_sha':sha})
                    # After process-internal state re-init, same task cannot be run twice.
                    s.prepare();after=s.execute(tid)
                    check('RESTART_IDEMPOTENCY',after.get('already_executed') is True and after.get('receipt',{}).get('output_sha256')==sha,after.get('status'))
                else:
                    replay=requests.post(url+'/api/execute',json={'task_id':tid},headers={'X-Enguru-Token':token,'Origin':url},timeout=10).json()
                    check('VALID_HTTP_REPLAY_NO_SECOND_EFFECT',replay.get('already_executed') is True,replay)
            else:check('POSITIVE_REAL_EXECUTE',False,execute.status_code)
    finally:
        srv.shutdown();srv.server_close();thread.join(timeout=5)
receipt={'schema':'enguru.ulmi.h1.v22.w07.http-framing-replay/v1','product_code_sha256':hashlib.sha256((product/'server.py').read_bytes()).hexdigest(),'checks':checks,'passed':sum(x['passed'] for x in checks),'total':len(checks),'failed_ids':errors,'result':'PASS_SCOPED_REAL_HTTP' if not errors else 'RED_NEEDS_FIX','stress_calls':args.stress,'note':'Isolated local HTTP/SQLite security test, not owner Pilot A/B/C nor independent DoneCheck.'}
out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('SUMMARY',receipt['passed'],'/',receipt['total'],'result',receipt['result'],flush=True)
if errors:sys.exit(1)
