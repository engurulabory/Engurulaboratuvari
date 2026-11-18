#!/usr/bin/env python3
"""ULMi-generated task-board: stand-alone Python + HTTP + SQLite application.

Runs 6 actual unittest checks by default. To serve: python taskboard_....py serve
All output remains in a disposable project folder. No third-party packages.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import sys
import tempfile
import threading
import unittest
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from urllib import request as urequest

HOST='127.0.0.1'
PORT=int(os.environ.get('ULMI_TASKBOARD_PORT','18991'))
DB=Path(os.environ.get('ULMI_TASKBOARD_DB',str(Path(__file__).with_suffix('.sqlite3')))).resolve()
TOKEN=secrets.token_hex(24)

HTML='''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="ulmi-token" content="__TOKEN__"><title>ULMi · Gerçek Görev Panosu</title>
<style>body{font:16px system-ui;background:#f4f4f0;color:#243c31;margin:0;padding:36px}main{max-width:830px;margin:auto;background:white;padding:32px;border-radius:20px;box-shadow:0 16px 40px #153c2211}h1{font-size:2rem}input,select,button{font:inherit;padding:12px;border-radius:10px;border:1px solid #a9b6ae}input{width:min(460px,95%)}button{background:#14533c;color:#fff;cursor:pointer}li{list-style:none;border:1px solid #ddd;padding:12px;border-radius:10px;margin:9px 0;display:flex;align-items:center;justify-content:space-between;gap:12px}li span{overflow-wrap:anywhere}li select{background:white}small{color:#566}ul{padding:0}</style></head><body><main><small>ENGÜRÜ · KANITLI MÜHENDİSLİK</small><h1>Görev Panosu</h1><p>Gerçek yerel HTTP · SQLite · yeniden açılabilir iş listesi</p><form id="new"><input id="title" required maxlength="160" placeholder="Yeni görevin adı" aria-label="Görev adı"><button type="submit">Görev ekle</button></form><p id="notice" role="status">Hazır.</p><ul id="tasks"></ul><small>Yalnız bu izole uygulamada çalışır. Resmî owner/DoneCheck kabulü ayrı.</small></main>
<script>
'use strict';const token=document.querySelector('meta[name="ulmi-token"]').content;const list=document.getElementById('tasks');const notice=document.getElementById('notice');
async function api(path,body){const o={headers:{'X-ULMI-Token':token}};if(body){o.method='POST';o.headers['Content-Type']='application/json';o.body=JSON.stringify(body);}const r=await fetch(path,o);const j=await r.json();if(!r.ok)throw Error(j.error||'HTTP '+r.status);return j;}
async function show(){const j=await api('/api/tasks');list.replaceChildren();for(const task of j.tasks){const li=document.createElement('li');const title=document.createElement('span');title.textContent=task.title;const choice=document.createElement('select');choice.setAttribute('aria-label',task.title+' durumu');for(const state of ['TODO','DOING','DONE']){const opt=document.createElement('option');opt.value=state;opt.textContent=state;choice.append(opt);}choice.value=task.state;choice.addEventListener('change',async()=>{try{await api('/api/update',{id:task.id,state:choice.value});await show();}catch(e){notice.textContent='HOLD '+e.message;}});li.append(title,choice);list.append(li);}notice.textContent=j.tasks.length+' görev SQLite üzerinden okundu.';}
document.getElementById('new').addEventListener('submit',async(e)=>{e.preventDefault();const title=document.getElementById('title');const value=title.value.trim();try{await api('/api/tasks',{title:value,request_id:crypto.randomUUID()});title.value='';await show();}catch(err){notice.textContent='HOLD '+err.message;}});show().catch(e=>notice.textContent='HOLD '+e.message);
</script></body></html>'''

def init(db_path=DB):
    db_path.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db_path) as db:
        db.execute('''CREATE TABLE IF NOT EXISTS jobs(
            id TEXT PRIMARY KEY, title TEXT NOT NULL, state TEXT NOT NULL,
            request_id TEXT UNIQUE NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        db.commit()

def list_jobs(db_path=DB):
    with sqlite3.connect(db_path) as db:
        return [dict(zip(['id','title','state'],r)) for r in db.execute('SELECT id,title,state FROM jobs ORDER BY rowid DESC LIMIT 100')]

def create(title,request_id,db_path=DB):
    if type(title) is not str or not 1 <= len(title.strip()) <= 160 or any(ord(c)<32 for c in title):
        raise ValueError('HOLD_TITLE')
    try:uuid.UUID(request_id)
    except (ValueError,TypeError,AttributeError):raise ValueError('HOLD_REQUEST_ID')
    with sqlite3.connect(db_path) as db:
        old=db.execute('SELECT id,title,state FROM jobs WHERE request_id=?',(request_id,)).fetchone()
        if old:
            if old[1]!=title.strip():raise ValueError('HOLD_REPLAY_PAYLOAD_DRIFT')
            return dict(zip(['id','title','state'],old))
        job={'id':str(uuid.uuid4()),'title':title.strip(),'state':'TODO'}
        db.execute('INSERT INTO jobs (id,title,state,request_id) VALUES (?,?,?,?)',(*job.values(),request_id))
        db.commit()
        return job

def update(job_id,state,db_path=DB):
    if state not in ('TODO','DOING','DONE'):raise ValueError('HOLD_STATE')
    try:uuid.UUID(job_id)
    except (ValueError,TypeError,AttributeError):raise ValueError('HOLD_JOB_ID')
    with sqlite3.connect(db_path) as db:
        result=db.execute('UPDATE jobs SET state=? WHERE id=?',(state,job_id))
        db.commit()
        if result.rowcount!=1:raise ValueError('HOLD_UNKNOWN_TASK')
    return {'id':job_id,'state':state}

class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    db_path=DB
    token=TOKEN
    def log_message(self,fmt,*args):pass
    def reply(self,code,obj):
        data=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def trusted(self):return self.headers.get('Host')==f'{HOST}:{self.server.server_port}'
    def do_GET(self):
        if not self.trusted():return self.reply(403,{'error':'HOLD_HOST'})
        path=urlparse(self.path).path
        if path=='/':
            content=HTML.replace('__TOKEN__',self.token)
            data=content.encode('utf-8')
            import re,base64
            inline=re.search(r'<script>(.*?)</script>',content,re.S).group(1)
            script_hash=base64.b64encode(hashlib.sha256(inline.encode()).digest()).decode()
            self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'sha256-"+script_hash+"'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        if path=='/api/tasks':return self.reply(200,{'tasks':list_jobs(self.db_path)})
        return self.reply(404,{'error':'HOLD_ROUTE'})
    def do_POST(self):
        if not self.trusted():return self.reply(403,{'error':'HOLD_HOST'})
        if self.headers.get('X-ULMI-Token')!=self.token:return self.reply(403,{'error':'HOLD_TOKEN'})
        if self.headers.get('Origin') not in (None,f'http://{HOST}:{self.server.server_port}'):
            return self.reply(403,{'error':'HOLD_ORIGIN'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size<2 or size>3000:raise ValueError('HOLD_BODY_SIZE')
            if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise ValueError('HOLD_CONTENT_TYPE')
            payload=json.loads(self.rfile.read(size))
            if type(payload) is not dict:raise ValueError('HOLD_JSON')
            path=urlparse(self.path).path
            if path=='/api/tasks':return self.reply(200,{'task':create(payload.get('title'),payload.get('request_id'),self.db_path)})
            if path=='/api/update':return self.reply(200,{'task':update(payload.get('id'),payload.get('state'),self.db_path)})
            return self.reply(404,{'error':'HOLD_ROUTE'})
        except (ValueError,TypeError,json.JSONDecodeError) as e:return self.reply(422,{'error':str(e)[:100]})

def serve():
    init()
    with ThreadingHTTPServer((HOST,PORT),Handler) as server:
        print(f'ULMI_TASKBOARD_READY=http://{HOST}:{PORT}',flush=True)
        server.serve_forever(poll_interval=.2)

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ulmi_board_test_')
        self.path=Path(self.tmp.name)/'tasks.sqlite3';init(self.path)
    def tearDown(self):self.tmp.cleanup()
    def test_01_create_read(self):
        x=create('Gerçek iş',str(uuid.uuid4()),self.path)
        self.assertEqual(list_jobs(self.path)[0]['id'],x['id'])
    def test_02_sqlite_reopen(self):
        x=create('Kalıcı görev',str(uuid.uuid4()),self.path)
        self.assertEqual(list_jobs(self.path)[0]['id'],x['id'])
        with sqlite3.connect(self.path) as db:self.assertEqual(db.execute('PRAGMA quick_check').fetchone()[0],'ok')
    def test_03_update(self):
        x=create('Onar',str(uuid.uuid4()),self.path)
        update(x['id'],'DONE',self.path)
        self.assertEqual(list_jobs(self.path)[0]['state'],'DONE')
    def test_04_no_duplicate_or_drift(self):
        k=str(uuid.uuid4());x=create('Tek kayıt',k,self.path)
        self.assertEqual(create('Tek kayıt',k,self.path)['id'],x['id'])
        self.assertEqual(len(list_jobs(self.path)),1)
        with self.assertRaisesRegex(ValueError,'HOLD_REPLAY_PAYLOAD_DRIFT'):create('Sahte kayıt',k,self.path)
    def test_05_bad_state_injection(self):
        x=create('Test',str(uuid.uuid4()),self.path)
        with self.assertRaises(ValueError):update(x['id'],'DONE;DROP TABLE jobs',self.path)
        with self.assertRaises(ValueError):create('script\nbody',str(uuid.uuid4()),self.path)
        self.assertEqual(len(list_jobs(self.path)),1)
    def test_06_real_http_api(self):
        class TestHandler(Handler):pass
        TestHandler.db_path=self.path
        with ThreadingHTTPServer((HOST,0),TestHandler) as server:
            t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
            host=f'http://{HOST}:{server.server_port}'
            try:
                response=urequest.urlopen(host+'/').read().decode()
                self.assertIn('Gerçek Görev Panosu',response)
                req=urequest.Request(host+'/api/tasks',data=json.dumps({'title':'HTTP görevi','request_id':str(uuid.uuid4())}).encode(),headers={'X-ULMI-Token':TOKEN,'Content-Type':'application/json'},method='POST')
                created=json.loads(urequest.urlopen(req).read())
                self.assertEqual(created['task']['state'],'TODO')
                records=json.loads(urequest.urlopen(host+'/api/tasks').read())
                self.assertEqual(len(records['tasks']),1)
            finally:server.shutdown();t.join(timeout=2)

if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1]=='serve':serve()
    else:unittest.main(verbosity=2)
