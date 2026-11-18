#!/usr/bin/env python3
"""Real localhost HTTP/SQLite W07/W08 on a disposable V7 code copy; NOT owner/DoneCheck."""
import argparse, hashlib, json, os, re, socket, sqlite3, subprocess, sys, tempfile, time, uuid
from pathlib import Path
from urllib import request, error

parser=argparse.ArgumentParser()
parser.add_argument('--product',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
product=Path(args.product).resolve()
checks=[];log=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(name,actual,expected=None):
 ok=bool(actual) if expected is None else actual==expected
 checks.append({'case':name,'passed':ok,'observed':str(actual)[:260],'expected':str(expected)[:260] if expected is not None else 'truthy'})
 print(('PASS' if ok else 'FAIL'),name,actual,flush=True)
 return ok

def free_port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]

def raw(port,head,body=b'',shutdown_write=False):
 with socket.create_connection(('127.0.0.1',port),timeout=4) as s:
  s.settimeout(4);s.sendall(('\r\n'.join(head)+'\r\n\r\n').encode()+body)
  if shutdown_write:s.shutdown(socket.SHUT_WR)
  out=b''
  while len(out)<8192:
   try:b=s.recv(4096)
   except socket.timeout:break
   if not b:break
   out+=b
  m=re.search(rb'HTTP/1\.1\s+(\d+)',out)
  return int(m.group(1)) if m else None,out[:1500].decode('utf8','replace')

def call(port,route,token=None,payload=None,method='GET',timeout=10):
 headers={}
 if token is not None:headers.update({'X-Enguru-Token':token,'Origin':f'http://127.0.0.1:{port}'})
 body=None
 if payload is not None:body=json.dumps(payload).encode();headers['Content-Type']='application/json'
 req=request.Request(f'http://127.0.0.1:{port}'+route,body,headers,method)
 try:
  with request.urlopen(req,timeout=timeout) as r:status=r.status;data=r.read()
 except error.HTTPError as e:status=e.code;data=e.read()
 try:parsed=json.loads(data)
 except (ValueError,UnicodeError):parsed={'_body':data.decode(errors='replace')[:600]}
 return status,parsed

def start(port,state):
 env={**os.environ,'ENGURU_H1_STATE_HOME':str(state),'ENGURU_USTA_PORT':str(port),'PYTHONDONTWRITEBYTECODE':'1'}
 p=subprocess.Popen([sys.executable,'-B',str(product/'server.py')],env=env,cwd=str(product),stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 for _ in range(90):
  if p.poll() is not None:raise RuntimeError('server exited '+str(p.returncode)+' '+p.stderr.read().decode()[-2000:])
  try:
   status,_=call(port,'/api/status',timeout=.4)
   if status==200:return p
  except (OSError,TimeoutError):time.sleep(.07)
  time.sleep(.03)
 p.kill();raise RuntimeError('server unavailable')
def stop(p):
 if p.poll() is None:p.terminate()
 try:p.wait(timeout=4)
 except subprocess.TimeoutExpired:p.kill();p.wait(timeout=4)

def get_token(port):
 with request.urlopen(f'http://127.0.0.1:{port}/uat-final',timeout=5) as r:b=r.read()
 m=re.search(rb'<meta name="enguru-token" content="([a-f0-9]{48})"',b)
 if not m:raise RuntimeError('Missing token')
 return m.group(1).decode()

def head(port,token,*extra):
 return ['POST /api/scaffold HTTP/1.1',f'Host: 127.0.0.1:{port}',f'Origin: http://127.0.0.1:{port}',f'X-Enguru-Token: {token}',f'Content-Type: application/json',*extra,'Connection: close']

try:
 with tempfile.TemporaryDirectory(prefix='enguru-ulmi-w07w08-real-http-') as d:
  state=Path(d);port=free_port();p=start(port,state)
  try:
   token=get_token(port);body=b'{"kind":"python"}';n=len(body)
   cases=[('DUPLICATE_ORIGIN',[f'Origin: https://evil.example']),('DUPLICATE_TOKEN',['X-Enguru-Token: attacker']),('DUPLICATE_HOST',['Host: attacker.example'])]
   for name,extra in cases:
    status,rawdata=raw(port,head(port,token,f'Content-Length: {n}',*extra),body)
    with sqlite3.connect(state/'data/tasks.sqlite3') as db:count=db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
    check('W07_'+name+'_REJECT_NO_WRITE',status in (400,403) and count==0)
   for name,body2 in [('DUPLICATE_JSON',b'{"kind":"python","kind":"html"}'),('NONFINITE_JSON',b'{"kind":NaN}')]:
    status,rawdata=raw(port,head(port,token,f'Content-Length: {len(body2)}'),body2)
    with sqlite3.connect(state/'data/tasks.sqlite3') as db:count=db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
    check('W07_'+name+'_REJECT_NO_WRITE',status in (400,422) and count==0)
   status,_=raw(port,head(port,token,'Content-Length: 16001'),b'')
   check('W08_OVERSIZE_BODY_413',status,413)
   status,_=raw(port,head(port,token,f'Content-Length: {n+30}'),body,shutdown_write=True)
   check('W08_SHORT_BODY_400',status,400)
   status,result=call(port,'/api/scaffold',token,{'kind':'python'},'POST')
   check('W07_VALID_PLAN_READY',status==200 and result.get('status')=='READY')
   tid=result['task_id']
   status,executed=call(port,'/api/execute',token,{'task_id':tid},'POST',timeout=20)
   check('W08_VALID_PY_EXECUTE',status==200 and executed.get('status')=='PASS_SCOPED')
   filename=executed['receipt']['path'];digest=executed['receipt']['output_sha256']
   check('W08_FILE_SHA_AFTER_EXECUTE',sha(state/'workspace'/filename),digest)
   status,replayed=call(port,'/api/execute',token,{'task_id':tid},'POST')
   check('W07_REPEAT_EXECUTE_IDEMPOTENT',status==200 and replayed.get('already_executed') and replayed.get('receipt',{}).get('output_sha256')==digest)
   status,unrun=call(port,'/api/scaffold',token,{'kind':'html'},'POST')
   check('W08_PLAN_FOR_RESTART',status==200 and unrun.get('status')=='READY')
   interrupted_id=unrun['task_id']
  finally:stop(p)
  # Real OS process restart on the same DB: fault injection of a crashed RUNNING task.
  with sqlite3.connect(state/'data/tasks.sqlite3') as db:
   db.execute('UPDATE tasks SET status=? WHERE task_id=?',('RUNNING',interrupted_id))
   db.commit()
  p=start(port,state)
  try:
   token2=get_token(port)
   check('W07_RESTART_ROTATES_SESSION_TOKEN',token!=token2)
   status,_=call(port,'/api/scaffold',token,{'kind':'python'},'POST')
   check('W07_OLD_TOKEN_AFTER_RESTART_DENIED',status,403)
   status,replay2=call(port,'/api/execute',token2,{'task_id':tid},'POST')
   check('W07_DURABLE_REPLAY_AFTER_PROCESS_RESTART',status==200 and replay2.get('already_executed') and replay2.get('receipt',{}).get('output_sha256')==digest)
   status,task=call(port,'/api/task?task_id='+interrupted_id)
   check('W08_INTERRUPTED_RUN_HOLD',status==200 and task['task']['status']=='HOLD_INTERRUPTED')
   status,_=call(port,'/api/execute',token2,{'task_id':interrupted_id},'POST')
   check('W08_INTERRUPTED_AUTO_REEXECUTE_DENIED',status==422)
   status,resume=call(port,'/api/resume',token2,{'task_id':interrupted_id},'POST')
   check('W08_OWNER_EXPLICIT_RESUME_ONLY',status==200 and resume.get('status')=='READY')
   status,committed=call(port,'/api/execute',token2,{'task_id':interrupted_id},'POST')
   check('W08_RESUMED_SAFELY_REAL_FILE',status==200 and committed.get('status')=='PASS_SCOPED')
   check('W08_EXISTING_FILE_PRESERVED',sha(state/'workspace'/filename),digest)
   # Fast quota boundary setup is explicitly isolated SQLite fault injection.
   with sqlite3.connect(state/'data/tasks.sqlite3') as db:
    ct=db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
    if ct>1000:raise RuntimeError('unexpected task count')
    for i in range(1000-ct):
     x=str(uuid.uuid4());now='2026-11-18T00:00:00+00:00'
     db.execute('INSERT INTO tasks(task_id,created_at,updated_at,origin,user_prompt,path,content,plan_sha,status) VALUES (?,?,?,?,?,?,?,?,?)',
       (x,now,now,'ISOLATED_QUOTA_FIXTURE','test','fixture_'+x+'.txt','a','0'*64,'HOLD'))
    db.commit()
    check('W08_QUOTA_FIXTURE_EXACTLY_1000',db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0],1000)
   status,limit=call(port,'/api/scaffold',token2,{'kind':'python'},'POST')
   with sqlite3.connect(state/'data/tasks.sqlite3') as db:
    count=db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
   check('W08_QUOTA_LIMIT_DENY_ZERO_NEW_RECORDS',status==422 and count==1000 and 'HOLD_TASK_QUOTA' in str(limit))
   check('W08_EXISTING_RECEIPT_SURVIVES_QUOTA',sha(state/'workspace'/filename),digest)
  finally:stop(p)
except Exception as exc:
 print('UNHANDLED',repr(exc),flush=True)
 checks.append({'case':'UNHANDLED_EXCEPTION','passed':False,'observed':repr(exc),'expected':'NONE'})
receipt={'schema':'enguru.ulmi.v22.w07-w08.real-isolated-http-and-process-restart/v1',
 'scope':'REAL_LOOPBACK_HTTP_SQLITE_DISPOSABLE_NOT_MAC_NOT_INDEPENDENT',
 'source_server_sha256':sha(product/'server.py'),
 'source_chat_bridge_sha256':sha(product/'chat_bridge.py'),
 'passed':sum(1 for c in checks if c['passed']),'total':len(checks),'checks':checks,
 'result':'PASS_SCOPED' if all(c['passed'] for c in checks) else 'HOLD',
 'owner_final':'NOT_ISSUED','independent_donecheck':'NOT_EXECUTED','canonical_cas':'NOT_PERFORMED'}
Path(args.output).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print('SUMMARY',receipt['passed'],'/',receipt['total'],receipt['result'],flush=True)
sys.exit(0 if receipt['result']=='PASS_SCOPED' else 1)
