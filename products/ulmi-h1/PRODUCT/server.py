#!/usr/bin/env python3
"""ENGÜRÜ Mühendis OSi™: çevrimdışı, dar yetkili yerel pilot.

Yalnızca 127.0.0.1 üzerinde HTTP; isteğe bağlı yerel Ollama.
Yetki: pilot çalışma alanında tek dosya oluşturma ve doğrulama.
Yapay zekâ hiçbir shell komutu çalıştıramaz.
"""
from __future__ import annotations

import ast
import base64
from contextlib import contextmanager
import hashlib
from html.parser import HTMLParser
from html import escape as html_escape
import json
import re
import os
from pathlib import Path
import secrets
import socket
import stat
import sqlite3
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request as urlrequest, error as urlerror
from urllib.parse import urlparse, parse_qs
import uuid
import capabilities
import worklist
import contract_bridge
import chat_bridge

BASE = Path(__file__).resolve().parent
# H1 state is isolated from the translocated app bundle and versioned source code.
STATE_ROOT = Path(os.environ.get('ENGURU_H1_STATE_HOME', str(BASE))).expanduser().resolve()
WORKSPACE = STATE_ROOT / 'workspace'
DATA = STATE_ROOT / 'data'
DB = DATA / 'tasks.sqlite3'
HOST = '127.0.0.1'
PORT = int(os.environ.get('ENGURU_USTA_PORT', '8899'))
MODEL = os.environ.get('ENGURU_USTA_MODEL', 'qwen3:14b')
OLLAMA_URL = 'http://127.0.0.1:11434/api/chat'
TOKEN = secrets.token_hex(24)
DB_LOCK = threading.RLock()
# W08: bound new READY plans in the owner-isolated SQLite ledger.
# This limit is a local safety quota, not a claim about official pilot acceptance.
MAX_PLANNED_TASKS = 1000
ALLOWED = {'.html', '.css', '.js', '.txt', '.md', '.json', '.py', '.csv'}
MAX_BYTES = 80000
VERSION = 'ULMI-H1-V7-QWEN-SOURCE-ROUTE-GUARD-CANDIDATE'
PRODUCT_ID = 'ENGURU_MUHENDIS_OSI'
MAP_INDEX = 'maps/map_index.json'

# Machine-verifiable runtime-to-artifact provenance, not a reviewer signature.
BUILD_FILES = ('server.py','uat_final.js','index.html','app.js','taskboard_template.py','chat_bridge.py','contract_bridge.py')

def runtime_build_identity() -> dict:
    sources={p:sha((BASE/p).read_bytes()) for p in BUILD_FILES}
    raw=json.dumps(sources,sort_keys=True,separators=(',',':')).encode('utf-8')
    return {'source_sha256':sources,'aggregate_sha256':sha(raw),
            'verification_level':'SELF_REPORTED_RUNNING_SOURCE_NOT_INDEPENDENT_DONECHECK'}


def iso_now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def prepare():
    if STATE_ROOT.is_symlink() or DATA.is_symlink() or WORKSPACE.is_symlink() or DB.is_symlink():
        raise RuntimeError('Veri veya çalışma alanı sembolik bağ olamaz.')
    STATE_ROOT.mkdir(exist_ok=True, mode=0o700)
    DATA.mkdir(exist_ok=True, mode=0o700)
    WORKSPACE.mkdir(exist_ok=True, mode=0o700)
    with db_conn() as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('''CREATE TABLE IF NOT EXISTS tasks (
          task_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          origin TEXT NOT NULL, user_prompt TEXT NOT NULL, path TEXT NOT NULL,
          content TEXT NOT NULL, plan_sha TEXT NOT NULL, status TEXT NOT NULL,
          receipt TEXT, error TEXT
        )''')
        db.execute("UPDATE tasks SET status='HOLD_INTERRUPTED', updated_at=? WHERE status='RUNNING'", (iso_now(),))
        worklist.init(db)
        db.execute('''CREATE TABLE IF NOT EXISTS desk_projects (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, goal TEXT NOT NULL,
          saved_at TEXT NOT NULL, sha256 TEXT NOT NULL
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS desk_chat (
          message_id TEXT PRIMARY KEY, project_id TEXT NOT NULL,
          project_sha256 TEXT NOT NULL, user_text TEXT NOT NULL,
          response_json TEXT NOT NULL, saved_at TEXT NOT NULL)''')
        # W06: provenance belongs to the same transaction as the READY plan.
        # This table is evidence of a local HTTP exchange, NEVER owner/model attestation.
        db.execute('''CREATE TABLE IF NOT EXISTS model_plan_receipts (
          task_id TEXT PRIMARY KEY, model TEXT NOT NULL,
          route_receipt TEXT NOT NULL, response_sha256 TEXT NOT NULL,
          FOREIGN KEY(task_id) REFERENCES tasks(task_id))''')
        db.execute('''CREATE TABLE IF NOT EXISTS desk_snapshots (
          id TEXT PRIMARY KEY, content TEXT NOT NULL, sha256 TEXT NOT NULL)''')
        db.commit()
    # Pilot örnek işler görünür; kaynak türü kesin olarak DEMO etiketlidir.
    # Saray yönetiminin gerçek listesi owner tarafından ayrı dosyayla yüklenir.
    worklist.seed_if_empty(sys.modules[__name__])


@contextmanager
def db_conn():
    db = sqlite3.connect(DB, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def validate_name(name: str) -> str:
    if not isinstance(name, str) or not (1 <= len(name) <= 90):
        raise ValueError('Dosya adı 1–90 karakter olmalı.')
    if name in ('.', '..') or '/' in name or '\\' in name or name.startswith('.'):
        raise ValueError('Yalnızca çalışma alanında, tek düzeyde dosya adı kullanılabilir.')
    if any(ord(c) < 32 or c in ':\\' for c in name) or Path(name).suffix.lower() not in ALLOWED:
        raise ValueError('Dosya adı veya uzantısı izinli değil.')
    if name.strip() != name:
        raise ValueError('Dosya adında başta/sonda boşluk olamaz.')
    return name


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = set()
    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)


def syntax_check(name: str, data: bytes) -> dict:
    ext = Path(name).suffix.lower()
    value = data.decode('utf-8')
    if not value.strip():
        raise ValueError('Boş çıktı kabul edilmedi.')
    if ext == '.json':
        json.loads(value)
        return {'status': 'PASS', 'method': 'JSON parse'}
    if ext == '.py':
        ast.parse(value)
        return {'status': 'PASS', 'method': 'Python AST/sözdizimi (çalıştırılmadı)'}
    if ext == '.html':
        p = Tags()
        p.feed(value)
        if not {'html','body'}.issubset(p.tags):
            raise ValueError('HTML için <html> ve <body> gerekir.')
        return {'status': 'PASS_SCOPED', 'method': 'HTMLParser + html/body (tarayıcı testi değil)'}
    return {'status': 'NOT_TESTED', 'method': 'Yalnızca doluluk / SHA / geri okuma; davranış veya sözdizimi testi yok'}


def store_plan(user_prompt: str, path: str, content: str, origin: str, model_receipt: dict | None = None) -> dict:
    validate_name(path)
    if not isinstance(content, str) or not content.strip():
        raise ValueError('Üretilecek içerik boş olamaz.')
    binary = content.encode('utf-8')
    if len(binary) > MAX_BYTES:
        raise ValueError('Tek dosya en fazla 80 KB olabilir.')
    # Syntax is checked before any file write. A failing plan is rejected.
    validation = syntax_check(path, binary)
    task_id = str(uuid.uuid4())
    plan_hash = sha(json.dumps({'path':path,'content':content}, ensure_ascii=False,sort_keys=True).encode('utf-8'))
    with DB_LOCK, db_conn() as db:
        # W08: no unbounded SQLite growth from repeated authorized plans.
        # The lock also serializes quota checks across concurrent requests.
        if db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0] >= MAX_PLANNED_TASKS:
            raise ValueError('HOLD_TASK_QUOTA')
        db.execute('''INSERT INTO tasks (task_id,created_at,updated_at,origin,user_prompt,path,content,plan_sha,status)
                   VALUES (?,?,?,?,?,?,?,?,?)''',
                   (task_id,iso_now(),iso_now(),origin,user_prompt,path,content,plan_hash,'READY'))
        if model_receipt is not None:
            if origin != 'LOCAL_OLLAMA' or model_receipt.get('provenance_level') != 'LOCAL_HTTP_SELF_REPORTED_NOT_INDEPENDENT_ATTESTATION':
                raise ValueError('HOLD_MODEL_PROVENANCE_SCOPE')
            db.execute('''INSERT INTO model_plan_receipts(task_id,model,route_receipt,response_sha256)
                          VALUES(?,?,?,?)''',
                       (task_id, model_receipt['model'], json.dumps(model_receipt,sort_keys=True,ensure_ascii=False),
                        model_receipt['response_sha256']))
        db.commit()
    result={'task_id':task_id,'path':path,'content':content,'plan_sha256':plan_hash,
            'syntax_check':validation,'status':'READY','origin':origin}
    if model_receipt is not None:result['model_route_receipt']=model_receipt
    return result


def render_project_taskboard(title: str, goal: str) -> str:
    """Only substitutions inside a SHA-pinned, reviewed program. No AI code execution."""
    if type(title) is not str or not 1 <= len(title) <= 90 or any(ord(x)<32 for x in title):
        raise ValueError('HOLD_PROJECT_BOARD_TITLE')
    if type(goal) is not str or not 5 <= len(goal) <= 4000 or any(ord(x)<32 and x not in '\r\n\t' for x in goal):
        raise ValueError('HOLD_PROJECT_BOARD_GOAL')
    if sha(TASKBOARD_FIXTURE.encode('utf-8')) != TASKBOARD_TEMPLATE_PIN:
        raise ValueError('HOLD_TEMPLATE_SHA')
    a='<h1>Görev Panosu</h1>'
    b='<p>Gerçek yerel HTTP · SQLite · yeniden açılabilir iş listesi</p>'
    if TASKBOARD_FIXTURE.count(a)!=1 or TASKBOARD_FIXTURE.count(b)!=1:
        raise ValueError('HOLD_TEMPLATE_MARKERS')
    # HTML escaping also prevents three-quote escape from the source's Python string.
    output=TASKBOARD_FIXTURE.replace(a,a+'<p><strong>Proje: '+html_escape(title,quote=True)+'</strong></p>')
    excerpt=' '.join(goal.split())[:180]
    output=output.replace(b,'<p>Hedef: '+html_escape(excerpt,quote=True)+'</p>'+b)
    ast.parse(output)
    if len(output.encode('utf-8'))>MAX_BYTES:raise ValueError('HOLD_PROJECT_BOARD_QUOTA')
    return output


def project_board_plan(payload: dict) -> dict:
    if type(payload) is not dict or set(payload)!={'project_id','project_sha256'}:
        raise ValueError('HOLD_PROJECT_BOARD_FIELDS')
    pid=payload['project_id']; digest=payload['project_sha256']
    try:
        if type(pid)!=str or str(uuid.UUID(pid))!=pid:raise ValueError()
    except (ValueError,TypeError,AttributeError):raise ValueError('HOLD_PROJECT_BOARD_ID')
    if type(digest)!=str or not re.fullmatch('[0-9a-f]{64}',digest):
        raise ValueError('HOLD_PROJECT_BOARD_SHA')
    with DB_LOCK,db_conn() as db:
        row=db.execute('SELECT id,title,goal,sha256 FROM desk_projects WHERE id=?',(pid,)).fetchone()
        if not row or row['sha256']!=digest or desk_project_sha(row['id'],row['title'],row['goal'])!=digest:
            raise ValueError('HOLD_PROJECT_BOARD_SCOPE_OR_SHA')
        title,goal=row['title'],row['goal']
    source=render_project_taskboard(title,goal)
    # This immutable task input can be re-derived from SQLite and compared before execute.
    stored=json.dumps({'project_id':pid,'project_sha256':digest},sort_keys=True,separators=(',',':'))
    result=store_plan(stored,'proje_gorev_panosu_'+uuid.uuid4().hex[:12]+'.py',source,
                      'SCOPED_TEMPLATE_PROJECT_BOARD')
    result['project_id']=pid;result['project_sha256']=digest
    result['template_sha256']=TASKBOARD_TEMPLATE_PIN
    result['scope']='VERIFIED_OWNER_CREATED_PROJECT_ROW_SHA_NOT_A_PRODUCT_OWNER_GRANT'
    return result


def verify_project_board_task(row: sqlite3.Row, data: bytes) -> bool:
    if row['origin'] != 'SCOPED_TEMPLATE_PROJECT_BOARD':return False
    try:
        query=json.loads(row['user_prompt'])
        if type(query) is not dict or set(query)!={'project_id','project_sha256'}:return False
        pid=query['project_id']; digest=query['project_sha256']
        with DB_LOCK,db_conn() as db:
            project=db.execute('SELECT id,title,goal,sha256 FROM desk_projects WHERE id=?',(pid,)).fetchone()
        if project is None or project['sha256']!=digest:return False
        if desk_project_sha(project['id'],project['title'],project['goal'])!=digest:return False
        return data==render_project_taskboard(project['title'],project['goal']).encode('utf-8')
    except (ValueError,TypeError,KeyError,json.JSONDecodeError):return False


def trusted_html_fixture_readback(task_id: str) -> bytes:
    """Serve only the exact trusted built-in HTML fixture for browser behavior test.

    Model/untrusted HTML can never be previewed as runnable same-origin HTML here.
    """
    task=get_task(task_id)
    if not task or task['origin'] != 'SCOPED_TEMPLATE_HTML' or task['status']!='PASS_SCOPED':
        raise ValueError('Yalnız önceden yürütülmüş güvenilir HTML örneği önizlenebilir.')
    file=WORKSPACE/validate_name(task['path'])
    if file.is_symlink() or not file.is_file():
        raise ValueError('Güvenilir HTML dosyası bulunamadı.')
    data=file.read_bytes()
    expected=HTML_FIXTURE.encode('utf-8')
    if data!=expected or sha(data)!=task['receipt']['output_sha256']:
        raise ValueError('Güvenilir HTML dosyasının kaynak/SHA eşliği bulunamadı.')
    return data


def make_demo_plan() -> dict:
    unique = uuid.uuid4().hex[:8]
    name = f'usta_ornek_{unique}.txt'
    body = 'ENGÜRÜ Mühendis OSi — yerel görev pilotu\nTarih: ' + iso_now() + '\nBu dosya yerel uygulama tarafından oluşturulmuştur.\n'
    return store_plan('Yerel örnek görev: gerçek dosya oluştur, doğrula, kayıt tut.',name,body,'DETERMINISTIC_DEMO')


def read_only_model_readiness() -> dict:
    """Read-only W01/W04/W06 preflight; does NOT invoke any model or grant authority."""
    # This is a local socket/catalog and trusted source-byte check, not an
    # independent attestation of model weights, producer identity, or quality.
    catalog='HOLD_LOCAL_MODEL_CATALOG_UNAVAILABLE'
    listed=False
    info='NO_INFERENCE'
    try:
        import urllib.request as _rq
        class NoRedirect(_rq.HTTPRedirectHandler):
            def redirect_request(self,*args,**kwargs):return None
        opener=_rq.build_opener(_rq.ProxyHandler({}),NoRedirect())
        # Production uses 11434; only isolated tests may override loopback.
        target=urlparse(OLLAMA_URL)
        if target.scheme!='http' or target.hostname!='127.0.0.1' or target.path!='/api/chat':
            raise ValueError('HOLD_MODEL_ROUTE_CONFIGURATION')
        req=_rq.Request(f'http://{target.netloc}/api/tags',method='GET',headers={'Accept':'application/json'})
        with opener.open(req,timeout=1.2) as resp:
            if resp.status!=200 or resp.headers.get_content_type()!='application/json':
                raise ValueError('HOLD_LOCAL_MODEL_CATALOG_HTTP')
            raw=resp.read(65537)
        if len(raw)>65536:raise ValueError('HOLD_LOCAL_MODEL_CATALOG_SIZE')
        obj=json.loads(raw,object_pairs_hook=contract_bridge._object_pairs,
                       parse_constant=contract_bridge._reject_constant)
        models=obj.get('models') if type(obj) is dict else None
        if type(models) is not list:raise ValueError('HOLD_LOCAL_MODEL_LIST')
        listed=any(type(m) is dict and (m.get('name')=='qwen3:14b' or m.get('model')=='qwen3:14b') for m in models)
        catalog='PASS_SCOPED_SELF_REPORTED_CATALOG' if listed else 'HOLD_QWEN3_14B_NOT_LISTED'
    except (Exception):
        catalog='HOLD_LOCAL_MODEL_CATALOG_UNAVAILABLE'
    bridge='HOLD_SHARED_AI_8787_NOT_REACHABLE'
    try:
        with socket.create_connection(('127.0.0.1',8787),timeout=.4):
            bridge='TCP_OPEN_NOT_PROVIDER_ATTESTATION'
    except OSError:pass
    context='HOLD_TRUSTED_CONTEXT_UNVERIFIED';refs=[]
    try:
        _graph,refs,_context,is_test=chat_bridge.approved_context()
        context='PASS_SCOPED_PINNED_SOURCE_BYTES_TEST_FIXTURE' if is_test else 'PASS_SCOPED_PINNED_SOURCE_BYTES_NOT_OWNER_GRANT'
    except (chat_bridge.Hold,contract_bridge.ContractHold,OSError,ValueError) as exc:
        context='HOLD_SOURCE_CONTEXT:'+str(exc)[:90]
    return {'schema':'enguru.ulmi.h1.v7.read-only-model-readiness/v1',
        'local_catalog':catalog,'qwen3_14b_listed':listed,
        'shared_ai_bridge':bridge,'eight_role_source_context':context,
        'loaded_roles':len(refs),'model_inference':'NOT_EXECUTED_BY_PREFLIGHT',
        'source_provenance':'LOCAL_SELF_REPORTED_OR_PINNED_READ_ONLY_NOT_INDEPENDENT_REVIEW',
        'independent_real_qwen_attestation':'NOT_EXECUTED',
        'producer_authority':'NOT_GRANTED_BY_PREFLIGHT',
        'owner_acceptance':'NOT_ISSUED','h2':'PARKED'}


def model_plan_receipt(task_id: str) -> dict:
    '''A previous real route receipt; no inference of actual Qwen identity.

    Caller must already be authenticated at the same-origin H1 HTTP layer.
    '''
    try:
        if type(task_id) is not str or str(uuid.UUID(task_id))!=task_id:
            raise ValueError('HOLD_MODEL_TASK_ID')
    except (ValueError,TypeError):
        raise ValueError('HOLD_MODEL_TASK_ID')
    with DB_LOCK,db_conn() as db:
        row=db.execute('''SELECT p.route_receipt,p.response_sha256,p.model,t.status,t.plan_sha
                          FROM model_plan_receipts p JOIN tasks t ON t.task_id=p.task_id
                          WHERE p.task_id=? AND t.origin='LOCAL_OLLAMA' ''',(task_id,)).fetchone()
    if row is None:raise ValueError('HOLD_MODEL_RECEIPT_NOT_FOUND')
    receipt=json.loads(row['route_receipt'])
    if receipt['model']!=row['model'] or receipt['response_sha256']!=row['response_sha256']:
        raise ValueError('HOLD_MODEL_RECEIPT_INTEGRITY')
    return {'task_id':task_id,'origin':'LOCAL_OLLAMA','route_receipt':receipt,
            'task_status':row['status'],'plan_sha256':row['plan_sha'],
            'independent_provider_attestation':'NOT_VERIFIED',
            'owner_execution_grant':'NOT_ISSUED'}


def _model_http_exchange(request_bytes: bytes) -> bytes:
    '''Bounded loopback only. No proxy, no redirects, no remote fallback.'''
    import urllib.request as _rq
    class _NeverRedirect(_rq.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):return None
    target=urlparse(OLLAMA_URL)
    if target.scheme!='http' or target.hostname!='127.0.0.1' or target.path!='/api/chat' or target.username or target.password or target.query or target.fragment:
        raise ValueError('HOLD_NON_LOOPBACK_PROVIDER_ROUTE')
    opener=_rq.build_opener(_rq.ProxyHandler({}),_NeverRedirect())
    req=_rq.Request(OLLAMA_URL,data=request_bytes,
                  headers={'Content-Type':'application/json','Accept':'application/json'},method='POST')
    try:
        with opener.open(req,timeout=120) as resp:
            if resp.status!=200:raise ValueError('HOLD_OLLAMA_HTTP_STATUS')
            if resp.headers.get_content_type()!='application/json':
                raise ValueError('HOLD_OLLAMA_CONTENT_TYPE')
            raw=resp.read(2_000_001)
            if len(raw)>2_000_000:raise ValueError('HOLD_OLLAMA_RESPONSE_SIZE')
            return raw
    except (urlerror.HTTPError,urlerror.URLError,TimeoutError,OSError) as exc:
        raise RuntimeError('HOLD_OLLAMA_LOOPBACK_UNAVAILABLE_OR_REDIRECT') from exc


def generate_local_plan(prompt: str) -> dict:
    '''W06: local Qwen path. A plan is only a proposal, not a model attestation.'''
    if not isinstance(prompt, str) or not 5 <= len(prompt.strip()) <= 1200:
        raise ValueError('Görev 5–1200 karakter arasında olmalı.')
    # Original H1 target specifically binds Qwen3 14B; an env override cannot
    # silently promote a different model into that acceptance ID.
    if MODEL != 'qwen3:14b':raise ValueError('HOLD_QWEN_MODEL_CONFIG')
    system = ("Sen ENGÜRÜ yerel yazılım dosyası taslaklayıcısısın. "
              "Yalnızca tek JSON nesnesi döndür: {\"path\":\"ornek.html\",\"content\":\"tam dosya metni\"}. "
              "Tam ve işlevsel tek bir dosya üret. path tek dosya adı olmalı (klasör yok). "
              "İzinli uzantılar: .html .css .js .txt .md .json .py .csv. "
              "HTML istenirse tam belge içinde html ve body kullan. "
              "Harici servis, API anahtarı, indirme veya üçüncü taraf bağımlılık kullanma. "
              "Bilinmeyen gerçekleri uydurma. Kullanıcının işini doğrudan karşıla.")
    payload=json.dumps({'model':MODEL,'stream':False,'format':'json','think':False,
                        'options':{'temperature':0.2,'num_predict':5000},
                        'messages':[{'role':'system','content':system},
                                    {'role':'user','content':prompt}]},ensure_ascii=False).encode('utf-8')
    raw=_model_http_exchange(payload)
    # Reject duplicate keys, NaN and non-object model wrappers; provider response
    # is untrusted even if the TCP port is loopback.
    try:
        obj=json.loads(raw,object_pairs_hook=contract_bridge._object_pairs,
                       parse_constant=contract_bridge._reject_constant)
    except (ValueError,UnicodeError) as exc:raise ValueError('HOLD_OLLAMA_RESPONSE_JSON') from exc
    if type(obj) is not dict or obj.get('model')!=MODEL:
        raise ValueError('HOLD_OLLAMA_REPORTED_MODEL')
    if obj.get('done') is not True:
        raise ValueError('HOLD_OLLAMA_INCOMPLETE_GENERATION')
    message=obj.get('message')
    if type(message) is not dict or message.get('role')!='assistant' or 'tool_calls' in message:
        raise ValueError('HOLD_OLLAMA_UNTRUSTED_MESSAGE')
    content=message.get('content')
    if type(content) is not str or not 1<=len(content)<=2_000_000:
        raise ValueError('HOLD_OLLAMA_EMPTY_OR_OVERSIZE_CONTENT')
    try:spec=json.loads(content,object_pairs_hook=contract_bridge._object_pairs,
                        parse_constant=contract_bridge._reject_constant)
    except (ValueError,UnicodeError) as exc:raise ValueError('HOLD_OLLAMA_GENERATED_JSON') from exc
    if type(spec) is not dict or set(spec)!={'path','content'}:
        raise ValueError('HOLD_OLLAMA_PLAN_FIELDS')
    route_receipt={'schema':'enguru.ulmi.local-plan-http-provenance/v1',
        'route':'DIRECT_LOCAL_OLLAMA_NOT_SHARED_AI','endpoint':urlparse(OLLAMA_URL).netloc+'/api/chat',
        'test_endpoint_override':OLLAMA_URL!='http://127.0.0.1:11434/api/chat',
        'model':MODEL,'self_reported_provider_model':obj['model'],
        'request_sha256':sha(payload),'response_sha256':sha(raw),
        'prompt_sha256':sha(prompt.encode('utf-8')),
        'runtime_build_sha256':runtime_build_identity()['aggregate_sha256'],
        'provenance_level':'LOCAL_HTTP_SELF_REPORTED_NOT_INDEPENDENT_ATTESTATION',
        'actual_qwen_inference_independently_verified':False,
        'owner_grant':'NOT_ISSUED','donecheck':'NOT_EXECUTED'}
    return store_plan(prompt,spec['path'],spec['content'],'LOCAL_OLLAMA',model_receipt=route_receipt)


# Hedef 1 kapsamı: iki güvenilir, kaynak kodu sabit şablon. Bu, genel AI kodunu
# komut olarak çalıştırma izni vermez.
HTML_FIXTURE = """<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><title>Mühendis · İşlevli Görev Kartı</title>
<style>body{font:18px system-ui;margin:3rem;max-width:42rem;color:#18322c}button{font:inherit;padding:.7rem;border:1px solid #769989;border-radius:8px;background:#e5f4ee}</style></head>
<body><main><h1>Yerel Görev Kartı</h1><p id="durum" role="status">Görev hazır</p>
<button id="tamamla" type="button">Görevi tamamla</button></main>
<script>document.getElementById('tamamla').addEventListener('click',()=>{document.getElementById('durum').textContent='Görev tamamlandı';});</script>
</body></html>
"""
PY_FIXTURE = """# Mühendis yerel hesaplama örneği: gerçek unittest ile sınanır.
import unittest

def hesapla(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError('Sayı gerekli')
    return a + b

class TestHesapla(unittest.TestCase):
    def test_olumlu(self): self.assertEqual(hesapla(2, 3), 5)
    def test_sifir(self): self.assertEqual(hesapla(0, -4), -4)
    def test_olumsuz(self):
        with self.assertRaises(TypeError): hesapla('a', 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
"""
# Reuse the existing plan/execute/SQLite engine: Pilot A's generated task-board
# is an immutable, reviewed fixture, not a second engineering executor.
TASKBOARD_TEMPLATE_PIN = '861638957813a0cf8de29b760558a8f12d4360464a4932c2637e340aa30e0deb'
TASKBOARD_FIXTURE = (BASE / 'taskboard_template.py').read_text('utf-8')
if sha(TASKBOARD_FIXTURE.encode('utf-8')) != TASKBOARD_TEMPLATE_PIN:
    raise RuntimeError('HOLD_TRUSTED_TASKBOARD_TEMPLATE_SOURCE_SHA')
TEMPLATES = {'html': ('html', HTML_FIXTURE), 'python': ('py', PY_FIXTURE),
             'taskboard': ('py', TASKBOARD_FIXTURE)}


def make_scaffold(kind: str) -> dict:
    if kind not in TEMPLATES:
        raise ValueError('Yalnızca html, python veya taskboard güvenilir üretimi kabul edilir.')
    ext, body = TEMPLATES[kind]
    name = f'muhendis_{kind}_{uuid.uuid4().hex[:10]}.{ext}'
    plan = store_plan(f'İzinli {kind} mühendislik örneğini üret ve doğrula.', name, body,
                      'SCOPED_TEMPLATE_' + kind.upper())
    plan['template_kind'] = kind
    plan['safety_note'] = 'Kod çalıştırma yalnızca sabit SHA eşleşmeli Python örneğine aittir.'
    return plan



def restricted_python_syntax_repair(source: str) -> tuple[str,dict]:
    """One bounded missing-colon repair. Red AST -> green AST, never execute user code.

    This is an explicit scoped capability; semantic bugs and general repairs remain HOLD.
    """
    if type(source) is not str or not 5 <= len(source) <= 4000 or '\x00' in source:
        raise ValueError('HOLD_REPAIR_INPUT')
    try:
        ast.parse(source)
    except SyntaxError as err:
        red={'type':type(err).__name__,'line':err.lineno,'message':err.msg}
        if not isinstance(err.lineno,int): raise ValueError('HOLD_REPAIR_LOCATION')
        lines=source.splitlines(keepends=True); i=err.lineno-1
        if i < 0 or i >= len(lines): raise ValueError('HOLD_REPAIR_LOCATION')
        raw=lines[i]; ending='\n' if raw.endswith('\n') else ''
        core=raw[:-1] if ending else raw
        # A single missing colon on a def/if/class/for/while header; reject other edits.
        if not re.match(r'^\s*(?:def|if|for|while|class)\s+[^#]+$',core) or core.rstrip().endswith(':'):
            raise ValueError('HOLD_UNSUPPORTED_REPAIR')
        fixed=core.rstrip()+':'+ending
        lines[i]=fixed
        updated=''.join(lines)
        try: ast.parse(updated)
        except SyntaxError:raise ValueError('HOLD_UNSUPPORTED_REPAIR')
        return updated,{'red':red,'green':'AST_PARSE_PASS','changed_line':i+1,'change':'ADD_MISSING_COLON'}
    raise ValueError('HOLD_SOURCE_ALREADY_PARSES')


def plan_repair(source: str) -> dict:
    repaired,proof=restricted_python_syntax_repair(source)
    task=store_plan(source,f'python_onarim_{uuid.uuid4().hex[:12]}.py',repaired,'SCOPED_PYTHON_REPAIR_V1')
    task['repair_proof']=proof
    task['safety_note']='Sözdizimi onarımıdır; güvenilmeyen Python kodu çalıştırılmaz.'
    return task


def plan_capability(capability_id: str, source: str) -> dict:
    if capability_id != capabilities.CAPABILITY['id']:
        raise ValueError('Kayıtlı yetenek kimliği bulunamadı.')
    if not capabilities.enabled():
        raise ValueError('Python teşhis yeteneği bu sürümde kapalı.')
    # This trusted module produces a single Markdown report; never executes user code.
    content = capabilities.render(source)
    filename = f'python_teshis_{uuid.uuid4().hex[:12]}.md'
    plan = store_plan(source, filename, content, 'CAPABILITY_PY_DIAGNOSTIC_V1')
    plan['capability'] = capabilities.registry()[0]
    return plan

def atomic_read_workspace_file(name: str, expected_inode: tuple[int, int] | None = None) -> bytes:
    """Read one regular file by its pinned fd, never a re-opened checked path.

    O_NONBLOCK ensures that an attacker-controlled FIFO fails immediately rather
    than hanging a verification/rollback request. Parent and leaf disallow links.
    An expected inode additionally binds first-run readback to its O_EXCL create.
    """
    name = validate_name(name)
    for flag in ('O_DIRECTORY', 'O_NOFOLLOW', 'O_NONBLOCK'):
        if not hasattr(os, flag):
            raise ValueError('HOLD_ATOMIC_READ_UNSUPPORTED')
    folder_fd = None
    leaf_fd = None
    try:
        folder_fd = os.open(WORKSPACE, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        leaf_fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=folder_fd)
        st = os.fstat(leaf_fd)
        if not stat.S_ISREG(st.st_mode) or st.st_size > MAX_BYTES:
            raise ValueError('HOLD_OUTPUT_NOT_REGULAR_OR_TOO_LARGE')
        if expected_inode is not None and (st.st_dev, st.st_ino) != expected_inode:
            raise ValueError('HOLD_OUTPUT_INODE_CHANGED')
        with os.fdopen(leaf_fd, 'rb') as stream:
            leaf_fd = None
            content = stream.read(MAX_BYTES + 1)
            if len(content) > MAX_BYTES:
                raise ValueError('HOLD_OUTPUT_TOO_LARGE')
            return content
    except OSError as exc:
        raise ValueError('HOLD_OUTPUT_NOT_REGULAR_OR_UNREADABLE') from exc
    finally:
        if leaf_fd is not None:
            os.close(leaf_fd)
        if folder_fd is not None:
            os.close(folder_fd)


def verify_written_task(task_id: str) -> dict:
    row = get_task(task_id)
    if not row or row['status'] != 'PASS_SCOPED':
        return {'task_id':task_id,'status':'HOLD','reason':'Önce başarılı gerçek icra makbuzu gerekir.'}
    name = validate_name(row['path'])
    try:
        actual = sha(atomic_read_workspace_file(name))
    except (ValueError, OSError) as exc:
        return {'task_id':task_id,'status':'HOLD_INTEGRITY','reason':str(exc)[:160]}
    expected = row['receipt']['output_sha256']
    return {'task_id':task_id,'status':'PASS_SCOPED_READBACK' if actual==expected else 'HOLD_INTEGRITY',
            'match':actual==expected,'sha256':actual,'expected_sha256':expected,
            'verifier':'SAME_PROCESS_READBACK_NOT_INDEPENDENT_DONECHECK'}


def prepare_safe_resume(task_id: str) -> dict:
    """Sadece kesin biçimde dosya üretmemiş, kesilmiş işi owner tıklamasıyla READY yap.

    Belirsiz dosya etkisi varsa ikinci yazma yok; uzlaştırma gerekir.
    """
    with DB_LOCK, db_conn() as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT task_id,status,path FROM tasks WHERE task_id=?',(task_id,)).fetchone()
        if row is None or row['status']!='HOLD_INTERRUPTED':
            db.rollback()
            raise ValueError('Yalnız kesilmiş ve uzlaştırılabilir görev devam ettirilebilir.')
        target=WORKSPACE/validate_name(row['path'])
        if target.exists() or target.is_symlink():
            db.execute('UPDATE tasks SET status=?,updated_at=?,error=? WHERE task_id=?',
                       ('HOLD_RECONCILE',iso_now(),'Dosya/bağ bulundu: otomatik ikinci işlem yok.',task_id))
            db.commit()
            return {'task_id':task_id,'status':'HOLD_RECONCILE','next_action':'Kaynak/çıktı bağı elle uzlaştırılmalı.'}
        db.execute('UPDATE tasks SET status=?,updated_at=?,error=NULL WHERE task_id=?',('READY',iso_now(),task_id))
        db.commit()
    return {'task_id':task_id,'status':'READY','next_action':'Owner aynı görev kimliğiyle yeniden onaylayabilir.'}


def task_status():
    with DB_LOCK, db_conn() as db:
        rows = db.execute('SELECT status, COUNT(*) AS n FROM tasks GROUP BY status').fetchall()
    return {'product_id':PRODUCT_ID,'goal_1':'ACTIVE_HTML_PRODUCT_HOLD','goal_2':'PARKED_MAC',
            'four_h_formal_pass':0,'four_h_total':56,'counts':{r['status']:r['n'] for r in rows},
            'maps_design':'PASS_SCOPED_DESIGN_ONLY',
            'runtime':'H1_ISOLATED_LOCAL_PILOT_NOT_MAC_ENGINEER'}


def get_task(task_id: str) -> dict | None:
    with DB_LOCK, db_conn() as db:
        row = db.execute('SELECT * FROM tasks WHERE task_id=?',(task_id,)).fetchone()
    if row is None:
        return None
    task = dict(row)
    task['receipt'] = json.loads(task['receipt']) if task['receipt'] else None
    # Reading task details from localhost is allowed; keep prompt/content out of ordinary list.
    return task


def list_tasks(search: str = '', status: str = '') -> list:
    # E05: real feature addition. SQL params keep special characters literal and prevent injection.
    if type(search) is not str or len(search) > 90 or any(ord(ch) < 32 for ch in search):
        raise ValueError('HOLD_SEARCH_INPUT')
    allowed_status = ('','READY','RUNNING','PASS_SCOPED','HOLD','HOLD_INTERRUPTED','HOLD_RECONCILE')
    if type(status) is not str or status not in allowed_status:
        raise ValueError('HOLD_STATUS_FILTER')
    terms=[]; params=[]
    if search.strip():
        terms.append('(instr(lower(path),lower(?)) > 0 OR instr(lower(origin),lower(?)) > 0 OR instr(task_id,?) > 0)')
        params.extend([search.strip()]*3)
    if status:
        terms.append('status=?');params.append(status)
    where=' WHERE '+' AND '.join(terms) if terms else ''
    sql='SELECT task_id,created_at,origin,path,status,error,receipt FROM tasks'+where+' ORDER BY created_at DESC, rowid DESC LIMIT 60'
    with DB_LOCK, db_conn() as db:
        rows=db.execute(sql,params).fetchall()
    items=[]
    for r in rows:
        receipt=json.loads(r['receipt']) if r['receipt'] else None
        integrity='NOT_APPLICABLE'
        if r['status']=='PASS_SCOPED':
            file=WORKSPACE/validate_name(r['path'])
            if not receipt or file.is_symlink() or not file.is_file() or file.stat().st_size > MAX_BYTES:
                integrity='HOLD_INTEGRITY'
            else:
                integrity='PASS_SCOPED_READBACK' if sha(file.read_bytes())==receipt.get('output_sha256') else 'HOLD_INTEGRITY'
        items.append({'task_id':r['task_id'],'created_at':r['created_at'],'origin':r['origin'],
               'path':r['path'],'status':r['status'],'integrity':integrity,'error':r['error'], 'receipt':receipt})
    return items


def execute(task_id: str) -> dict:
    # Only the user approval request triggers execution. Existing files are never overwritten.
    with DB_LOCK, db_conn() as db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT * FROM tasks WHERE task_id=?',(task_id,)).fetchone()
        if row is None:
            raise ValueError('Görev bulunamadı.')
        if row['status'] == 'PASS_SCOPED':
            db.rollback()
            # Prevent a stale PASS if the previously produced file was altered.
            # Reuse the existing readback verifier; no second execution or write.
            integrity = verify_written_task(task_id)
            if integrity.get('status') != 'PASS_SCOPED_READBACK':
                return {'status':'HOLD_INTEGRITY','task_id':task_id,
                        'already_executed':True,'receipt':None,
                        'reason':'Önceki dosyanın SHA geri okuması doğrulanmadı; ikinci yazım yapılmadı.'}
            return {'status':'PASS_SCOPED','task_id':task_id,'already_executed':True,'receipt':json.loads(row['receipt'])}
        if row['status'] != 'READY':
            db.rollback()
            raise ValueError('Görev READY değil; tekrar otomatik yazma engellendi.')
        db.execute('UPDATE tasks SET status=?,updated_at=? WHERE task_id=?',('RUNNING',iso_now(),task_id))
        db.commit()
    name=row['path']
    path=WORKSPACE / validate_name(name)
    data=row['content'].encode('utf-8')
    # Only files created by this exact invocation may be rolled back.
    created_identity=None
    try:
        syntax=syntax_check(name,data)
        expected=sha(data)
        trusted_py = row['origin']=='SCOPED_TEMPLATE_PYTHON' and data==PY_FIXTURE.encode('utf-8')
        trusted_html = row['origin']=='SCOPED_TEMPLATE_HTML' and data==HTML_FIXTURE.encode('utf-8')
        trusted_taskboard = row['origin']=='SCOPED_TEMPLATE_TASKBOARD' and data==TASKBOARD_FIXTURE.encode('utf-8')
        trusted_project_board = verify_project_board_task(row,data)
        # Truth Boundary: a corrupted, formerly trusted template MUST NOT be written
        # as an untested generic artifact. Refuse before any filesystem effect.
        if row['origin'].startswith('SCOPED_TEMPLATE_') and not (trusted_py or trusted_html or trusted_taskboard or trusted_project_board):
            raise RuntimeError('HOLD_SCOPED_TEMPLATE_SOURCE_MISMATCH')
        flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
        if hasattr(os,'O_NOFOLLOW'):
            flags |= os.O_NOFOLLOW
        fd=os.open(path, flags, 0o600)
        opened_stat=os.fstat(fd)
        created_identity=(opened_stat.st_dev,opened_stat.st_ino)
        with os.fdopen(fd,'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        # Read-back is the real I/O acceptance check.
        actual_data=atomic_read_workspace_file(name, expected_inode=created_identity)
        actual=sha(actual_data)
        if expected != actual:
            raise RuntimeError('Geri okuma SHA eşliği sağlanmadı.')
        functional={'status':'NOT_TESTED','method':'Yalnız bilinen, tam SHA eşleşmeli fixture kodu çalıştırılır.'}
        if trusted_py:
            # Güvenilir sabit şablon, serbest model kodu değil. Gerçek subprocess testidir.
            done=subprocess.run([sys.executable,'-I','-B',str(path)], cwd=str(WORKSPACE),
                                capture_output=True,text=True,timeout=8,check=False)
            functional={'status':'PASS' if done.returncode==0 and 'Ran 3 tests' in done.stderr and 'OK' in done.stderr else 'HOLD',
                        'method':'trusted Python unittest subprocess, 3 gerçek test',
                        'exit_code':done.returncode,'output':(done.stdout+done.stderr)[-1100:]}
            if functional['status']!='PASS':
                raise RuntimeError('Güvenilir Python örneği fonksiyonel testten geçemedi.')
        elif trusted_taskboard or trusted_project_board:
            # This generates a genuine runnable task-board API/HTML/SQLite app.
            # Its own 6 tests use disposable databases and real local HTTP.
            done=subprocess.run([sys.executable,'-I','-B',str(path)], cwd=str(WORKSPACE),
                                capture_output=True,text=True,timeout=15,check=False)
            passed=done.returncode==0 and 'Ran 6 tests' in done.stderr and 'OK' in done.stderr
            functional={'status':'PASS' if passed else 'HOLD',
                        'method':'Generated HTTP+HTML+SQLite task-board, 6 real subprocess unittest',
                        'exit_code':done.returncode,'source_sha256':sha(data),
                        'verified_template_sha256':TASKBOARD_TEMPLATE_PIN,
                        'output':(done.stdout+done.stderr)[-1600:]}
            if not passed:
                raise RuntimeError('Üretilen görev panosunun altı gerçek testi başarısız.')
        elif trusted_html:
            functional={'status':'NOT_TESTED_BROWSER','method':'HTML yapısı kontrol edildi; gerçek buton testi ayrı tarayıcıda gerekir.'}
        elif row['origin']=='SCOPED_PYTHON_REPAIR_V1':
            # Trust-boundary: deterministically recompute edit from immutable stored input.
            repaired,proof=restricted_python_syntax_repair(row['user_prompt'])
            if data != repaired.encode('utf-8'):
                raise RuntimeError('HOLD_REPAIR_SOURCE_DRIFT')
            functional={'status':'PASS_SCOPED_STATIC','method':'Gerçek Python AST RED→GREEN; onarılan kullanıcı kodu çalıştırılmadı',
                        'repair_proof':proof,'before_sha256':sha(row['user_prompt'].encode('utf-8')),
                        'after_sha256':sha(data)}
        elif row['origin']=='CAPABILITY_PY_DIAGNOSTIC_V1':
            # Recalculate the module's output from immutable task input before receipt.
            if not capabilities.enabled() or data != capabilities.render(row['user_prompt']).encode('utf-8'):
                raise RuntimeError('Modül kapalı veya kaynak/çıktı eşliği bozuldu.')
            result=capabilities.diagnostic(row['user_prompt'])
            functional={'status':'PASS', 'method':'Yerleşik Python AST statik teşhisi; kaynak KOD ÇALIŞTIRILMADI',
                        'capability_id':'PY_DIAGNOSTIC_V1','capability_version':'1.0.0',
                        'module_source_sha256':capabilities.module_sha256(),
                        'source_sha256':result['source_sha256'],'diagnostic':result['syntax'],
                        'line':result['line']}
        receipt={'task_id':task_id,'timestamp':iso_now(),'path':name,
                 'bound_project':json.loads(row['user_prompt']) if trusted_project_board else None,
                 'job_id':task_id,'product_id':PRODUCT_ID,'runtime_build_sha256':runtime_build_identity()['aggregate_sha256'],'source_origin':row['origin'],
                 'map_ids':['H01','H03','H05','H06','H08'],
                 'acceptance_id':'H1_PILOT_E2E_SCOPED','contract_sha256':row['plan_sha'],
                 'functional_test':functional,'bytes':len(actual_data),'output_sha256':actual,'readback_sha256':expected,
                 'readback':'PASS','syntax':syntax,'environment':'H1_ISOLATED_HTML_PILOT_NOT_MAC_FIELD',
                 'claim':'Gerçek dosya, SHA ve kapsamlı test kanıtı. Ürün/4H/Safari/Mac nihai kabulü değildir.'}
        with DB_LOCK, db_conn() as db:
            db.execute('UPDATE tasks SET status=?,updated_at=?,receipt=?,error=NULL WHERE task_id=?',
                       ('PASS_SCOPED',iso_now(),json.dumps(receipt,ensure_ascii=False),task_id))
            db.commit()
        return {'status':'PASS_SCOPED','task_id':task_id,'receipt':receipt}
    except Exception as e:
        # True rollback: a failed functional test must not leave the just-created
        # artifact in the workspace. Never remove pre-existing or changed bytes.
        # The O_EXCL-created device/inode and exact written prefix are required.
        reconcile=False
        if created_identity is not None:
            try:
                st=os.stat(path,follow_symlinks=False)
                if not stat.S_ISREG(st.st_mode) or (st.st_dev,st.st_ino)!=created_identity:
                    reconcile=True
                elif st.st_size>len(data):
                    reconcile=True
                else:
                    current=atomic_read_workspace_file(name, expected_inode=created_identity)
                    if current != data[:len(current)]:
                        reconcile=True
                    else:
                        # Same freshly created inode, same content or an exact
                        # incomplete prefix; no other owned file is removed.
                        os.unlink(path)
                        if path.exists() or path.is_symlink():
                            reconcile=True
            except (OSError, ValueError):
                reconcile=True
        error=('HOLD_ROLLBACK_RECONCILE: ' if reconcile else '')+str(e)
        with DB_LOCK, db_conn() as db:
            db.execute('UPDATE tasks SET status=?,updated_at=?,error=? WHERE task_id=?',
                       ('HOLD',iso_now(),error[:300],task_id))
            db.commit()
        raise


def safe_read_file(name: str) -> str:
    """Read exactly one receipt-backed regular inode under the isolated workspace.

    W08: use directory-relative O_NOFOLLOW/O_NONBLOCK so changing a checked
    pathname into a symlink or FIFO cannot redirect or block readback.
    """
    name = validate_name(name)
    if not all(hasattr(os, x) for x in ('O_NOFOLLOW', 'O_DIRECTORY', 'O_NONBLOCK')):
        raise ValueError('HOLD_ATOMIC_READ_UNSUPPORTED')
    workspace_fd = None
    file_fd = None
    try:
        workspace_fd = os.open(WORKSPACE, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        file_fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=workspace_fd)
        with os.fdopen(file_fd, 'rb') as stream:
            file_fd = None
            st = os.fstat(stream.fileno())
            if not stat.S_ISREG(st.st_mode) or st.st_size > MAX_BYTES:
                raise ValueError('HOLD_OUTPUT_NOT_REGULAR_OR_TOO_LARGE')
            actual = stream.read(MAX_BYTES + 1)
            if len(actual) > MAX_BYTES:
                raise ValueError('HOLD_OUTPUT_TOO_LARGE')
    except OSError as exc:
        raise ValueError('HOLD_OUTPUT_NOT_REGULAR_OR_UNREADABLE') from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        if workspace_fd is not None:
            os.close(workspace_fd)
    with DB_LOCK, db_conn() as db:
        row = db.execute("SELECT receipt FROM tasks WHERE path=? AND status='PASS_SCOPED' ORDER BY rowid DESC LIMIT 1", (name,)).fetchone()
    if not row or not row['receipt']:
        raise ValueError('HOLD_UNRECEIPTED_FILE')
    receipt = json.loads(row['receipt'])
    if sha(actual) != receipt.get('output_sha256') or receipt.get('output_sha256') != receipt.get('readback_sha256'):
        raise ValueError('HOLD_OUTPUT_INTEGRITY')
    return actual.decode('utf-8')


def list_files():
    results=[]
    for f in sorted(WORKSPACE.iterdir()):
        if f.is_file() and not f.is_symlink() and f.suffix.lower() in ALLOWED and f.stat().st_size <= MAX_BYTES:
            results.append({'name':f.name,'bytes':f.stat().st_size})
    return results[:200]


# V11 / Job05: H1-only project scope; does not grant execution.
def desk_project_sha(pid,title,goal):
    raw=json.dumps({'id':pid,'title':title,'goal':goal},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    return sha(raw)

def desk_projects():
    with DB_LOCK, db_conn() as db:
        rows=db.execute('SELECT id,title,goal,saved_at,sha256 FROM desk_projects ORDER BY rowid DESC LIMIT 50').fetchall()
    return {'source':'H1_SQLITE','projects':[dict(x) for x in rows]}

def desk_save(payload):
    if set(payload) not in ({'title','goal'},{'title','goal','id','expected_sha256'}):
        raise ValueError('HOLD_PROJECT_FIELDS')
    title=payload['title']; goal=payload['goal']
    if not isinstance(title,str) or not 1<=len(title.strip())<=90 or title!=title.strip() or '\x00' in title: raise ValueError('HOLD_PROJECT_TITLE')
    if not isinstance(goal,str) or not 5<=len(goal.strip())<=4000 or goal!=goal.strip() or '\x00' in goal: raise ValueError('HOLD_PROJECT_GOAL')
    is_edit='id' in payload
    if is_edit:
        pid=payload['id']; expected=payload['expected_sha256']
        try:
            if str(uuid.UUID(pid))!=pid: raise ValueError()
        except (ValueError,TypeError,AttributeError): raise ValueError('HOLD_PROJECT_ID')
        if type(expected)!=str or not re.fullmatch('[0-9a-f]{64}',expected):raise ValueError('HOLD_PROJECT_SHA')
    else:pid=str(uuid.uuid4());expected=None
    now=iso_now();digest_value=desk_project_sha(pid,title,goal)
    with DB_LOCK,db_conn() as db:
        if is_edit:
            row=db.execute('SELECT sha256 FROM desk_projects WHERE id=?',(pid,)).fetchone()
            if not row or row['sha256']!=expected:raise ValueError('HOLD_PROJECT_CAS')
            db.execute('UPDATE desk_projects SET title=?,goal=?,saved_at=?,sha256=? WHERE id=? AND sha256=?',
                       (title,goal,now,digest_value,pid,expected))
        else:
            if db.execute('SELECT COUNT(*) FROM desk_projects').fetchone()[0]>=50:raise ValueError('HOLD_PROJECT_QUOTA')
            db.execute('INSERT INTO desk_projects(id,title,goal,saved_at,sha256) VALUES(?,?,?,?,?)',
                       (pid,title,goal,now,digest_value))
    return {'source':'H1_SQLITE','project':{'id':pid,'title':title,'goal':goal,'saved_at':now,'sha256':digest_value},
            'execution_state':'NOT_EXECUTED','donecheck_state':'NOT_EXECUTED'}

def desk_project_chat(payload):
    # Serialize project edits, conversation completion and native restore.
    # The upstream call is bounded; a project cannot change beneath its answer.
    with DB_LOCK:
        return _desk_project_chat(payload)

def _desk_project_chat(payload):
    required={'project_id','project_sha256','message_id','text','requested_action'}
    if set(payload)!=required or payload.get('requested_action')!='ADVISE_ONLY':raise chat_bridge.Hold('HOLD_ADVICE_ONLY_FIELDS')
    pid=payload['project_id']; psha=payload['project_sha256']; msg=payload['text']
    try:
        if type(pid)!=str or str(uuid.UUID(pid))!=pid:raise ValueError()
    except (ValueError,TypeError,AttributeError):raise chat_bridge.Hold('HOLD_PROJECT_ID')
    if type(psha)!=str or not re.fullmatch('[0-9a-f]{64}',psha):raise chat_bridge.Hold('HOLD_PROJECT_SHA')
    if type(msg)!=str or not 1<=len(msg.strip())<=2000 or '\x00' in msg:raise chat_bridge.Hold('HOLD_MESSAGE_TEXT')
    with DB_LOCK,db_conn() as db:
        row=db.execute('SELECT id,title,goal,sha256 FROM desk_projects WHERE id=?',(pid,)).fetchone()
    if row is None or row['sha256']!=psha or desk_project_sha(row['id'],row['title'],row['goal'])!=psha:
        raise chat_bridge.Hold('HOLD_PROJECT_SCOPE_OR_SHA')
    # Full project text stays in the DB. Advice includes an explicitly labelled excerpt
    # to honour the existing canonical chat-bridge message budget.
    excerpt=row['goal'][:1150]
    context=('H1 kayitli proje (SALT-OKUNUR, icra yetkisi yok):\n'
             +'Proje kimligi: '+pid+'\nProje adi: '+row['title']+'\n'
             +'Hedefin ilk 1150 karakteri: '+excerpt+'\n'
             +'Kullanici sorusu: '+msg.strip())
    if len(context)>chat_bridge.MAX_MESSAGE:raise chat_bridge.Hold('HOLD_MESSAGE_BUDGET')
    with db_conn() as db:
        if db.execute('SELECT COUNT(*) FROM desk_chat').fetchone()[0]>=1000:
            raise chat_bridge.Hold('HOLD_CHAT_QUOTA')
    resp=chat_bridge.respond({'project_id':contract_bridge.CONTRACT_ID,
         'contract_revision':1,'contract_sha256':contract_bridge.CONTRACT_PIN,
         'message_id':payload['message_id'],'text':context,'requested_action':'ADVISE_ONLY'})
    # Do not claim the model provider identity was independently attested.
    result={**resp,'project_id':pid,'project_sha256':psha,
         'context_goal_truncated':len(row['goal'])>1150,
         'project_scope':'H1_SQLITE_ROW_SHA_VERIFIED_READ_ONLY',
         'provider_verification':'ROUTE_SELF_REPORTED_NOT_INDEPENDENTLY_ATTESTED'}
    with db_conn() as db:
        db.execute('INSERT INTO desk_chat VALUES(?,?,?,?,?,?)',
          (payload['message_id'],pid,psha,msg,json.dumps(result,ensure_ascii=False,sort_keys=True),iso_now()))
    return result

def desk_history(pid):
    with DB_LOCK,db_conn() as db:
        rows=db.execute('SELECT message_id,project_sha256,user_text,response_json,saved_at FROM desk_chat WHERE project_id=? ORDER BY rowid', (pid,)).fetchall()
    return {'source':'H1_SQLITE','project_id':pid,'messages':[
      {**{k:r[k] for k in ('message_id','project_sha256','user_text','saved_at')},'response':json.loads(r['response_json'])} for r in rows]}

def _desk_state(db):
    return {'projects':[list(r) for r in db.execute('SELECT id,title,goal,saved_at,sha256 FROM desk_projects ORDER BY id')],
      'messages':[list(r) for r in db.execute('SELECT message_id,project_id,project_sha256,user_text,response_json,saved_at FROM desk_chat ORDER BY message_id')]}

def _desk_state_bytes(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')

def _restore_scope():
    if not chat_bridge.isolated_test():raise ValueError('HOLD_DISPOSABLE_ONLY')

def desk_snapshot(payload):
    _restore_scope()
    if payload!={}:raise ValueError('HOLD_SNAPSHOT_FIELDS')
    with DB_LOCK,db_conn() as db:
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('HOLD_DB_INTEGRITY')
        if db.execute('SELECT COUNT(*) FROM desk_snapshots').fetchone()[0]>=10:raise ValueError('HOLD_SNAPSHOT_QUOTA')
        raw=_desk_state_bytes(_desk_state(db)); sid=str(uuid.uuid4()); digest=sha(raw)
        db.execute('INSERT INTO desk_snapshots VALUES(?,?,?)',(sid,raw.decode('utf-8'),digest))
    return {'snapshot_id':sid,'sha256':digest,'scope':'DISPOSABLE_DESK_TABLES_ONLY_REPLAY_LEDGER_PRESERVED'}

def desk_restore(payload):
    _restore_scope()
    if set(payload)!={'snapshot_id','expected_sha256'}:raise ValueError('HOLD_RESTORE_FIELDS')
    with DB_LOCK,db_conn() as db:
        row=db.execute('SELECT content,sha256 FROM desk_snapshots WHERE id=?',(payload['snapshot_id'],)).fetchone()
        if not row or row['sha256']!=payload['expected_sha256'] or sha(row['content'].encode('utf-8'))!=row['sha256']:
            raise ValueError('HOLD_SNAPSHOT_SHA')
        state=json.loads(row['content']); db.execute('DELETE FROM desk_chat');db.execute('DELETE FROM desk_projects')
        db.executemany('INSERT INTO desk_projects VALUES(?,?,?,?,?)',state['projects'])
        db.executemany('INSERT INTO desk_chat VALUES(?,?,?,?,?,?)',state['messages'])
        after=sha(_desk_state_bytes(_desk_state(db)))
        if after!=row['sha256'] or db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('HOLD_RESTORE_READBACK')
    return {'state':'PASS_SCOPED_NATIVE_RESTORE','sha256':after,'replay_ledger':'PRESERVED_NOT_RESTORED','execution_state':'NOT_EXECUTED','donecheck_state':'NOT_EXECUTED'}

class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def setup(self):
        super().setup()
        self.connection.settimeout(2)
    def log_message(self, fmt, *args):
        print('[local]', fmt % args,flush=True)

    def json_response(self, code, obj, *, close=False):
        # HTTP/1.1: when rejecting a POST before consuming its request body,
        # the same socket must not parse leftover bytes as the next HTTP verb.
        # Close only that rejected connection; valid requests keep keep-alive.
        if close:
            self.close_connection = True
        body=json.dumps(obj,ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        if close:
            self.send_header('Connection','close')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def static_response(self, filename):
        typ={'index.html':'text/html','browser_kabul.html':'text/html','uat_final.html':'text/html','uat_final.js':'text/javascript','uat_final.css':'text/css','app.js':'text/javascript','v05_browser.js':'text/javascript','worklist_ui.js':'text/javascript','style.css':'text/css','v05_browser.css':'text/css'}[filename]
        body=(BASE / filename).read_bytes()
        if filename in ('index.html','browser_kabul.html','uat_final.html'):
            body=body.replace(b'__ENGURU_CSRF__',TOKEN.encode('ascii'))
        atelier = filename=='index.html' and b'id="atelier-chat"' in body
        self.send_response(200)
        self.send_header('Content-Type',typ+'; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        if atelier:
            # Browser executes only the two exact inline scripts SHA-pinned to rendered HTML.
            inline=re.findall(rb'<script>(.*?)</script>',body,re.S)
            assert len(inline)==2
            hashes=' '.join("'sha256-"+base64.b64encode(hashlib.sha256(raw).digest()).decode('ascii')+"'" for raw in inline)
            csp="default-src 'none'; script-src "+hashes+"; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        else:
            csp="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        self.send_header('Content-Security-Policy',csp)
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def permitted_host(self):
        # W07: HTTP/1.1 ambiguous Host is denied, even if the first value is valid.
        hosts=self.headers.get_all('Host',[])
        return len(hosts)==1 and hosts[0] == f'{HOST}:{self.server.server_port}'

    def unambiguous_auth_headers(self):
        # Duplicate Origin/token can make distinct parsers reach different
        # authorization conclusions. Never take merely the first value.
        return all(len(self.headers.get_all(name,[]))<=1
                   for name in ('Origin','X-Enguru-Token'))

    def do_GET(self):
        if not self.permitted_host():
            return self.json_response(403,{'error':'HTTP Host reddedildi.'},close=True)
        if not self.unambiguous_auth_headers():
            return self.json_response(400,{'error':'HOLD_DUPLICATE_AUTH_HEADERS'},close=True)
        try:
            parsed=urlparse(self.path)
            if parsed.path=='/uat-final':
                return self.static_response('uat_final.html')
            if parsed.path in ('/','/index.html'):
                return self.static_response('index.html')
            if parsed.path in ('/style.css','/app.js','/browser_kabul.html','/v05_browser.js','/v05_browser.css','/worklist_ui.js','/uat_final.html','/uat_final.js','/uat_final.css'):
                return self.static_response(parsed.path[1:])
            if parsed.path=='/api/trusted-html':
                task_id=parse_qs(parsed.query).get('task_id',[''])[0]
                try: uuid.UUID(task_id)
                except (ValueError,AttributeError):return self.json_response(400,{'error':'Geçersiz görev kimliği.'})
                try: body=trusted_html_fixture_readback(task_id)
                except ValueError as e:return self.json_response(422,{'error':str(e)})
                js=HTML_FIXTURE.split('<script>',1)[1].split('</script>',1)[0]
                script_hash=base64.b64encode(hashlib.sha256(js.encode('utf-8')).digest()).decode('ascii')
                self.send_response(200)
                self.send_header('Content-Type','text/html; charset=utf-8')
                self.send_header('Cache-Control','no-store')
                self.send_header('X-Content-Type-Options','nosniff')
                self.send_header('X-Frame-Options','SAMEORIGIN')
                self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'sha256-"+script_hash+"'; style-src 'unsafe-inline'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
                self.send_header('Content-Length',str(len(body)))
                self.end_headers();self.wfile.write(body)
                return
            if parsed.path=='/api/status':
                try:
                    with socket.create_connection(('127.0.0.1',11434),timeout=.4):
                        ollama_port='OPEN_MODEL_NOT_VERIFIED'
                except OSError:
                    ollama_port='CLOSED'
                return self.json_response(200,{'app':'ENGÜRÜ Mühendis OSi™ · Hedef 1 İzole HTML Prototip','version':VERSION,
                    'network':'LOOPBACK_ONLY','extensions':len([c for c in capabilities.registry() if c['enabled']]),'ollama_port':ollama_port,
                    'ai':'Ollama 127.0.0.1:11434 (isteğe bağlı)',
                    'workspace':'workspace/','runtime_build':runtime_build_identity(), 'instance_id':hashlib.sha256(str(BASE.resolve()).encode('utf-8')).hexdigest()[:20], 'worklist_capability':'HFS_OWNER_IMPORT_LOCAL_DEMO_SEPARATED','model':MODEL,'allowed_extensions':sorted(ALLOWED)})
            if parsed.path=='/api/model/readiness':
                if self.headers.get('X-Enguru-Token','')!=TOKEN:
                    return self.json_response(403,{'state':'HOLD','reason':'HOLD_TOKEN'},close=True)
                return self.json_response(200,read_only_model_readiness())
            if parsed.path=='/api/model/receipt':
                if self.headers.get('X-Enguru-Token','')!=TOKEN:
                    return self.json_response(403,{'state':'HOLD','reason':'HOLD_TOKEN'},close=True)
                tid=parse_qs(parsed.query).get('task_id',[''])[0]
                return self.json_response(200,model_plan_receipt(tid))
            if parsed.path=='/api/desk/projects':
                if self.headers.get('X-Enguru-Token','')!=TOKEN:
                    return self.json_response(403,{'error':'HOLD_TOKEN'})
                return self.json_response(200,desk_projects())
            if parsed.path=='/api/desk/history':
                if self.headers.get('X-Enguru-Token','')!=TOKEN:
                    return self.json_response(403,{'error':'HOLD_TOKEN'})
                return self.json_response(200,desk_history(parse_qs(parsed.query).get('project_id',[''])[0]))
            if parsed.path=='/api/worklist':
                return self.json_response(200,worklist.list_catalog(sys.modules[__name__]))
            if parsed.path=='/api/dashboard':
                return self.json_response(200,task_status())
            if parsed.path=='/api/capabilities':
                return self.json_response(200,{'capabilities':capabilities.registry(),'core':'SINGLE_EXECUTOR_SQLITE'})
            if parsed.path=='/api/maps':
                return self.json_response(200,json.loads((BASE / MAP_INDEX).read_text('utf-8')))
            if parsed.path=='/api/task':
                task_id=parse_qs(parsed.query).get('task_id',[''])[0]
                try:uuid.UUID(task_id)
                except (ValueError,AttributeError):return self.json_response(400,{'error':'Geçersiz görev kimliği.'})
                task=get_task(task_id)
                return self.json_response(200,{'task':task}) if task else self.json_response(404,{'error':'Görev bulunamadı.'})
            if parsed.path=='/api/verify':
                task_id=parse_qs(parsed.query).get('task_id',[''])[0]
                try:uuid.UUID(task_id)
                except (ValueError,AttributeError):return self.json_response(400,{'error':'Geçersiz görev kimliği.'})
                return self.json_response(200,verify_written_task(task_id))
            if parsed.path=='/api/tasks':
                query=parse_qs(parsed.query,keep_blank_values=True)
                if any(k not in ('search','status') or len(v)!=1 for k,v in query.items()):
                    return self.json_response(400,{'error':'HOLD_TASK_FILTER_FIELDS'})
                return self.json_response(200,{'tasks':list_tasks(query.get('search',[''])[0],query.get('status',[''])[0])})
            if parsed.path=='/api/files':
                return self.json_response(200,{'files':list_files()})
            if parsed.path=='/api/file':
                name=parse_qs(parsed.query).get('name',[''])[0]
                return self.json_response(200,{'name':name,'content':safe_read_file(name)})
            return self.json_response(404,{'error':'Sayfa/rota bulunamadı.'})
        except Exception as e:
            return self.json_response(400,{'error':str(e)[:250]})

    def do_POST(self):
        if not self.permitted_host():
            return self.json_response(403,{'error':'HTTP Host reddedildi.'},close=True)
        if not self.unambiguous_auth_headers():
            return self.json_response(400,{'error':'HOLD_DUPLICATE_AUTH_HEADERS'},close=True)
        # Do not accept cross-origin form submissions or unauthenticated local POST.
        if self.headers.get('X-Enguru-Token','') != TOKEN:
            return self.json_response(403,{'error':'Yerel oturum onay anahtarı eksik.'},close=True)
        origin=self.headers.get('Origin')
        # Every write path must originate from the same browser origin.  A
        # session token alone (e.g. copied from GET /) is not a run grant.
        if origin != f'http://{HOST}:{self.server.server_port}':
            return self.json_response(403,{'error':'HOLD_ORIGIN_REQUIRED: Farklı veya eksik Origin.'},close=True)
        try:
            route=urlparse(self.path).path
            # V22-W07 RED->GREEN: enforce unambiguous request framing and JSON
            # media type across ALL write endpoints, not only /api/desk/.
            # Reject before reading an untrusted body or creating any SQLite row.
            sizes=self.headers.get_all('Content-Length',[])
            types=self.headers.get_all('Content-Type',[])
            if (len(sizes)!=1 or not sizes[0].isascii() or not sizes[0].isdecimal()
                or self.headers.get_all('Transfer-Encoding',[])):
                return self.json_response(400,{'state':'HOLD','reason':'HOLD_BODY_FRAMING'},close=True)
            if len(types)!=1 or types[0].split(';',1)[0].strip().lower()!='application/json':
                return self.json_response(415,{'state':'HOLD','reason':'HOLD_CONTENT_TYPE'},close=True)
            if route.startswith('/api/desk/'):
                sizes=self.headers.get_all('Content-Length',[])
                if self.headers.get_all('Transfer-Encoding',[]) or len(sizes)!=1 or not sizes[0].isascii() or not sizes[0].isdecimal():
                    return self.json_response(400,{'state':'HOLD','reason':'HOLD_BODY_FRAMING'},close=True)
                if origin != f'http://{HOST}:{self.server.server_port}':
                    return self.json_response(403,{'state':'HOLD','reason':'HOLD_ORIGIN_REQUIRED'},close=True)
                if self.headers.get('Content-Type','').split(';',1)[0].strip()!='application/json':
                    return self.json_response(415,{'state':'HOLD','reason':'HOLD_CONTENT_TYPE'},close=True)
            n=int(self.headers.get('Content-Length','0'))
            limit=80000 if route=='/api/worklist/import' else (chat_bridge.MAX_BODY if route in ('/api/desk/chat','/api/desk/project-chat') else 16000)
            if n<2 or n>limit:
                return self.json_response(413,{'error':'İstek boyutu uygun değil.'},close=True)
            body=self.rfile.read(n)
            if len(body)!=n:
                return self.json_response(400,{'state':'HOLD','reason':'HOLD_INCOMPLETE_BODY'},close=True)
            if route.startswith('/api/desk/'):
                payload=json.loads(body,
                                   object_pairs_hook=contract_bridge._object_pairs,
                                   parse_constant=contract_bridge._reject_constant)
            else:
                # W07: duplicate keys and non-JSON NaN/Infinity are ambiguous
                # across parsers; reject before any effect on the task ledger.
                payload=json.loads(body,
                                   object_pairs_hook=contract_bridge._object_pairs,
                                   parse_constant=contract_bridge._reject_constant)
            if not isinstance(payload,dict):
                return self.json_response(400,{'error':'JSON nesnesi gerekli.'})
            if route=='/api/desk/snapshot':
                return self.json_response(200,desk_snapshot(payload))
            if route=='/api/desk/restore':
                return self.json_response(200,desk_restore(payload))
            if route=='/api/desk/project-board/plan':
                return self.json_response(200,project_board_plan(payload))
            if route=='/api/desk/projects/save':
                if origin != f'http://{HOST}:{self.server.server_port}':
                    return self.json_response(403,{'error':'HOLD_ORIGIN_REQUIRED'},close=True)
                return self.json_response(200,desk_save(payload))
            if route=='/api/desk/project-chat':
                if origin != f'http://{HOST}:{self.server.server_port}':
                    return self.json_response(403,{'state':'HOLD','reason':'HOLD_ORIGIN_REQUIRED'},close=True)
                if self.headers.get('Content-Type','').split(';',1)[0].strip()!='application/json':
                    return self.json_response(415,{'state':'HOLD','reason':'HOLD_CONTENT_TYPE'},close=True)
                try:
                    return self.json_response(200,desk_project_chat(payload))
                except chat_bridge.Hold as exc:
                    return self.json_response(422,{'state':'HOLD','reason':exc.reason,
                        'execution_state':'NOT_EXECUTED','donecheck_state':'NOT_EXECUTED'})
            # Chat route: strict origin; existing session token already checked above.
            # No model output may reach execute(), SQLite, shell, or owner grant.
            if route in ('/api/desk/chat','/api/desk/project-chat'):
                if origin != f'http://{HOST}:{self.server.server_port}':
                    return self.json_response(403,{'state':'HOLD_AUTHORITY','reason':'HOLD_ORIGIN_REQUIRED'},close=True)
                if self.headers.get('Content-Type','').split(';',1)[0].strip()!='application/json':
                    return self.json_response(415,{'state':'HOLD_AUTHORITY','reason':'HOLD_CONTENT_TYPE'},close=True)
                if len(self.headers.get_all('Content-Length',[]))!=1 or self.headers.get_all('Transfer-Encoding',[]):
                    return self.json_response(400,{'state':'HOLD_AUTHORITY','reason':'HOLD_BODY_FRAMING'},close=True)
                if n>chat_bridge.MAX_BODY:
                    return self.json_response(413,{'state':'HOLD_AUTHORITY','reason':'HOLD_BODY_OVERSIZE'},close=True)
                try:
                    reply=chat_bridge.respond(payload)
                    return self.json_response(200,reply)
                except chat_bridge.Hold as exc:
                    return self.json_response(422,{'state':'HOLD','reason':exc.reason,
                        'execution_state':'NOT_EXECUTED','donecheck_state':'NOT_EXECUTED'})
            # Sözleşmeden İcraya Köprü V1: review-only; no plan, task, SQLite or execute calls.
            # Trusted baseline root is server-side local configuration, never HTTP-supplied.
            if route=='/api/contract/preview':
                return self.json_response(200,contract_bridge.preview_base64(
                    payload.get('contract_b64'), os.environ.get('ENGURU_ULMI_TRUSTED_BASELINE_ROOT')))
            if route=='/api/worklist/import':
                return self.json_response(200,worklist.import_catalog(payload.get('catalog'),sys.modules[__name__]))
            if route=='/api/worklist/plan':
                return self.json_response(200,worklist.plan_selected(payload.get('work_id'),sys.modules[__name__]))
            if route=='/api/worklist/browser-accept':
                return self.json_response(200,worklist.accept_html_browser(payload.get('work_id'),payload.get('task_id'),payload.get('observed'),sys.modules[__name__]))
            if route=='/api/capability/plan':
                return self.json_response(200,plan_capability(payload.get('id',''),payload.get('source','')))
            if route=='/api/capability/repair-plan':
                return self.json_response(200,plan_repair(payload.get('source','')))
            if route=='/api/scaffold':
                return self.json_response(200,make_scaffold(payload.get('kind','')))
            if route=='/api/demo':
                return self.json_response(200,make_demo_plan())
            if route=='/api/plan':
                return self.json_response(200,generate_local_plan(payload.get('prompt','')))
            if route=='/api/resume':
                return self.json_response(200,prepare_safe_resume(payload.get('task_id','')))
            if route=='/api/execute':
                return self.json_response(200,execute(payload.get('task_id','')))
            return self.json_response(404,{'error':'Rota bulunamadı.'})
        except (TimeoutError,socket.timeout):
            return self.json_response(408,{'state':'HOLD','reason':'HOLD_BODY_TIMEOUT'},close=True)
        except (ValueError,RuntimeError,json.JSONDecodeError) as e:
            return self.json_response(422,{'error':str(e)[:350],'status':'HOLD'})
        except Exception as e:
            return self.json_response(500,{'error':type(e).__name__+': '+str(e)[:240],'status':'HOLD'})


def make_server(port=PORT):
    prepare()
    return ThreadingHTTPServer((HOST,port),Handler)


def main():
    if sys.version_info < (3,10):
        sys.exit('Python 3.10+ gerekiyor.')
    try:
        app=make_server()
    except OSError as exc:
        sys.exit(f'Port {PORT} kullanımda: {exc}. ENGURU_USTA_PORT ile başka bir port seçilebilir.')
    print(f'ENGURU_MUHENDIS_H1_READY=http://{HOST}:{PORT}\nMODEL={MODEL}\nCTRL+C ile durdur.\n',flush=True)
    try:
        app.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        app.server_close()

if __name__=='__main__':
    main()
