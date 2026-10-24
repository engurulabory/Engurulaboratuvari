#!/usr/bin/env python3
"""ENGURU MK two-node isolated pilot. Stdlib only. No product writes or owner authority.

Public review-branch transport sends ONLY fixed no-secret diagnostic codes. All
ACKs mean transport delivery, never DoneCheck / Human Threshold acceptance.
"""
from __future__ import annotations
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import urllib.error

SCHEMA = 'enguru.mk.bridge-event/v1'
ACK_SCHEMA = 'enguru.mk.bridge-ack/v1'
TASK = 'ENGURU_MK_BRIDGE_PILOT_V1'
REPO = 'engurulabory/Engurulaboratuvari'
BRANCH = 'feat/enguru-mk-bridge-intelligence-v5-20261024'
ROOT = 'governance/enguru-suzgeci/learning/bridge/pilot'
NODES = ('MAC_OSI_MK', 'GITHUB_MK')
ALLOWED_CODES = frozenset(('PILOT_HELLO', 'GITHUB_RECEIVED', 'PILOT_RECOVERY', 'RUNTIME_DRIFT', 'PACKAGE_ABSENT', 'INTERACTIVE_TIMEOUT', 'NODE_TAP_MISMATCH'))
ALLOWED_TYPES = frozenset(('SUCCESS', 'ERROR', 'NEED', 'MISMATCH'))
HEX40 = re.compile(r'[a-f0-9]{40}\Z')
HEX64 = re.compile(r'[a-f0-9]{64}\Z')
EV_ID = re.compile(r'(?:MAC|GH)-[0-9]{8}\Z')
MAX_JSON = 4096

class Hold(Exception):
    pass

def canon(obj):
    return (json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def strict_pairs(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise Hold('HOLD_DUPLICATE_JSON_KEY')
        d[k]=v
    return d

def parse(raw):
    if len(raw)>MAX_JSON: raise Hold('HOLD_JSON_SIZE')
    try:
        obj=json.loads(raw, object_pairs_hook=strict_pairs)
    except (UnicodeError, ValueError, TypeError) as exc:
        raise Hold('HOLD_JSON_PARSE') from exc
    if not isinstance(obj, dict): raise Hold('HOLD_JSON_OBJECT')
    return obj

def timestamp(s):
    try:
        d=datetime.fromisoformat(s.replace('Z','+00:00'))
        if d.utcoffset() is None: raise ValueError('timezone')
        return d
    except (ValueError,AttributeError,TypeError) as exc:
        raise Hold('HOLD_TIME_FORMAT') from exc

def validate_event(ev):
    fields={'schema','eventId','taskId','blockId','producer','sequence','type','code','sourceCommit','evidenceSha256','observedAt','visibility'}
    if not isinstance(ev,dict) or set(ev)!=fields: raise Hold('HOLD_EVENT_FIELDS')
    if ev['schema']!=SCHEMA or ev['taskId']!=TASK: raise Hold('HOLD_EVENT_SCOPE')
    if ev['producer'] not in NODES: raise Hold('HOLD_PRODUCER')
    if not isinstance(ev['eventId'],str) or not EV_ID.fullmatch(ev['eventId']): raise Hold('HOLD_EVENT_ID')
    expected_prefix = 'MAC-' if ev['producer']=='MAC_OSI_MK' else 'GH-'
    if not ev['eventId'].startswith(expected_prefix): raise Hold('HOLD_EVENT_OWNER')
    if type(ev['sequence']) is not int or ev['sequence']<1 or ev['sequence']>99999999 or int(ev['eventId'].split('-')[1])!=ev['sequence']:raise Hold('HOLD_SEQUENCE')
    if not isinstance(ev['blockId'],str) or not re.fullmatch(r'OSIBLOCK-[0-9]{8}-[A-Z0-9]{3,16}',ev['blockId']):raise Hold('HOLD_BLOCK_ID')
    if ev['type'] not in ALLOWED_TYPES or ev['code'] not in ALLOWED_CODES:raise Hold('HOLD_CODE')
    if not isinstance(ev['sourceCommit'],str) or not HEX40.fullmatch(ev['sourceCommit']): raise Hold('HOLD_COMMIT')
    if not isinstance(ev['evidenceSha256'],str) or not HEX64.fullmatch(ev['evidenceSha256']):raise Hold('HOLD_EVIDENCE_HASH')
    if ev['visibility']!='PUBLIC_SANITIZED': raise Hold('HOLD_VISIBILITY')
    timestamp(ev['observedAt'])
    raw=canon(ev)
    if len(raw)>MAX_JSON: raise Hold('HOLD_EVENT_SIZE')
    return sha(raw)

def make_event(producer, seq, commit, code='PILOT_HELLO', block='OSIBLOCK-20261024-PILOT', observed=None):
    ev={'schema':SCHEMA,'eventId':('MAC-' if producer=='MAC_OSI_MK' else 'GH-')+f'{seq:08d}',
        'taskId':TASK,'blockId':block,'producer':producer,'sequence':seq,'type':'SUCCESS',
        'code':code,'sourceCommit':commit,'evidenceSha256':sha(b'ENGURU_PUBLIC_PILOT_ONLY_V1'),
        'observedAt':observed or datetime.now(timezone.utc).isoformat(),'visibility':'PUBLIC_SANITIZED'}
    validate_event(ev)
    return ev

def make_ack(ev):
    digest=validate_event(ev)
    return {'schema':ACK_SCHEMA,'eventId':ev['eventId'],'receiver':('GITHUB_MK' if ev['producer']=='MAC_OSI_MK' else 'MAC_OSI_MK'),
            'eventSha256':digest,'delivery':'RECEIVED_ONLY','officialAcceptance':'HOLD'}

def validate_ack(ack,ev,expected_receiver):
    fields={'schema','eventId','receiver','eventSha256','delivery','officialAcceptance'}
    if not isinstance(ack,dict) or set(ack)!=fields:raise Hold('HOLD_ACK_FIELDS')
    if ack['schema']!=ACK_SCHEMA or ack['eventId']!=ev['eventId'] or ack['receiver']!=expected_receiver:raise Hold('HOLD_ACK_ACTOR')
    if ack['eventSha256']!=validate_event(ev) or ack['delivery']!='RECEIVED_ONLY' or ack['officialAcceptance']!='HOLD':raise Hold('HOLD_ACK_INTEGRITY')
    return True

class LocalLedger:
    def __init__(self, path):
        path=Path(path)
        if path.is_symlink():raise Hold('HOLD_LEDGER_SYMLINK')
        if not path.parent.is_dir() or path.parent.is_symlink():raise Hold('HOLD_LEDGER_PARENT')
        self.path=path
        self.db=sqlite3.connect(str(path), timeout=15)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA busy_timeout=15000')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS outgoing(event_id TEXT PRIMARY KEY,seq INTEGER UNIQUE NOT NULL,raw BLOB NOT NULL,digest TEXT NOT NULL,acked INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS incoming(event_id TEXT PRIMARY KEY,seq INTEGER UNIQUE NOT NULL,raw BLOB NOT NULL,digest TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY,value TEXT NOT NULL);
        ''')
    def close(self): self.db.close()
    def enqueue(self,ev):
        digest=validate_event(ev)
        if ev['producer']!='MAC_OSI_MK':raise Hold('HOLD_NOT_MAC_EVENT')
        with self.db:
            old=self.db.execute('SELECT digest FROM outgoing WHERE event_id=?',(ev['eventId'],)).fetchone()
            if old:
                if old[0]!=digest:raise Hold('HOLD_EVENT_ID_CONFLICT')
                return 'IDEMPOTENT'
            last=self.db.execute('SELECT coalesce(max(seq),0) FROM outgoing').fetchone()[0]
            if ev['sequence']!=last+1:raise Hold('HOLD_OUTBOX_SEQUENCE')
            self.db.execute('INSERT INTO outgoing(event_id,seq,raw,digest) VALUES(?,?,?,?)',(ev['eventId'],ev['sequence'],canon(ev),digest))
        return 'QUEUED'
    def queued(self):
        return [(x[0],parse(x[1])) for x in self.db.execute('SELECT event_id,raw FROM outgoing WHERE acked=0 ORDER BY seq')]
    def ack_outgoing(self,ack):
        row=self.db.execute('SELECT raw FROM outgoing WHERE event_id=?',(ack.get('eventId'),)).fetchone()
        if not row:raise Hold('HOLD_ACK_UNKNOWN_EVENT')
        validate_ack(ack,parse(row[0]),'GITHUB_MK')
        with self.db:self.db.execute('UPDATE outgoing SET acked=1 WHERE event_id=?',(ack['eventId'],))
    def receive(self,ev):
        digest=validate_event(ev)
        if ev['producer']!='GITHUB_MK':raise Hold('HOLD_NOT_GITHUB_EVENT')
        with self.db:
            old=self.db.execute('SELECT digest FROM incoming WHERE event_id=?',(ev['eventId'],)).fetchone()
            if old:
                if old[0]!=digest:raise Hold('HOLD_INBOX_CONFLICT')
                return make_ack(ev)
            current=self.db.execute('SELECT coalesce(max(seq),0) FROM incoming').fetchone()[0]
            if ev['sequence']!=current+1:raise Hold('HOLD_INBOX_GAP')
            self.db.execute('INSERT INTO incoming(event_id,seq,raw,digest) VALUES(?,?,?,?)',(ev['eventId'],ev['sequence'],canon(ev),digest))
        return make_ack(ev)
    def last_remote(self):
        r=self.db.execute("SELECT value FROM meta WHERE k='remote_head'").fetchone()
        return r[0] if r else None
    def set_remote(self, sha_commit):
        if not HEX40.fullmatch(sha_commit):raise Hold('HOLD_REMOTE_SHA')
        with self.db:self.db.execute("INSERT INTO meta(k,value) VALUES('remote_head',?) ON CONFLICT(k) DO UPDATE SET value=excluded.value",(sha_commit,))
    def counts(self):
        return {'outbox':self.db.execute('SELECT count(*) FROM outgoing').fetchone()[0],
                'pending':self.db.execute('SELECT count(*) FROM outgoing WHERE acked=0').fetchone()[0],
                'inbox':self.db.execute('SELECT count(*) FROM incoming').fetchone()[0],
                'officialAcceptance':'HOLD','codeExecution':0}
    def backup(self,dest):
        p=Path(dest)
        if p.exists() or p.is_symlink():raise Hold('HOLD_BACKUP_EXISTS')
        # Exclusive reservation protects previously recorded AudiV13 snapshots.
        flags=os.O_CREAT|os.O_EXCL|os.O_WRONLY|getattr(os,'O_NOFOLLOW',0)
        try:
            fd=os.open(str(p),flags,0o600)
        except FileExistsError as exc:
            raise Hold('HOLD_BACKUP_EXISTS') from exc
        os.close(fd)
        target=None
        try:
            target=sqlite3.connect(str(p))
            self.db.backup(target)
            result=target.execute('PRAGMA quick_check').fetchone()
            if not result or result[0]!='ok':raise Hold('HOLD_BACKUP_QUICK_CHECK')
        finally:
            if target is not None:target.close()
        return sha(p.read_bytes())

class GitHubAPI:
    def __init__(self,token,repo=REPO,branch=BRANCH, opener=None):
        if repo!=REPO or branch!=BRANCH:raise Hold('HOLD_GITHUB_SCOPE')
        if not token:raise Hold('HOLD_TOKEN_REQUIRED')
        self.token=token;self.repo=repo;self.branch=branch;self.opener=opener or urllib.request.urlopen
    def request(self,endpoint, method='GET', payload=None):
        url='https://api.github.com/repos/'+self.repo+'/'+endpoint
        body=canon(payload) if payload is not None else None
        req=urllib.request.Request(url, data=body, method=method, headers={
            'Authorization':'Bearer '+self.token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',
            'User-Agent':'enguru-mk-bridge-v1','Content-Type':'application/json'})
        try:
            with self.opener(req,timeout=25) as response: raw=response.read(2_000_001)
            if len(raw)>2_000_000:raise Hold('HOLD_GITHUB_RESPONSE_SIZE')
            
            try:
                return json.loads(raw,object_pairs_hook=strict_pairs)
            except (ValueError,UnicodeError,TypeError) as exc:
                raise Hold('HOLD_GITHUB_JSON_PARSE') from exc
        except urllib.error.HTTPError as exc:
            if exc.code==404:return None
            if exc.code in (409,412,422):raise Hold('HOLD_GITHUB_CONFLICT') from exc
            raise Hold('HOLD_GITHUB_HTTP_'+str(exc.code)) from exc
        except (urllib.error.URLError,OSError) as exc:raise Hold('HOLD_NETWORK') from exc
    def branch_head(self):
        data=self.request('branches/'+urllib.parse.quote(self.branch,safe=''))
        head=(data or {}).get('commit',{}).get('sha')
        if not isinstance(head,str) or not HEX40.fullmatch(head):raise Hold('HOLD_REMOTE_BRANCH')
        return head
    def ensure_forward(self,old,new):
        if old==new or old is None:return
        j=self.request('compare/'+old+'...'+new)
        if not j or j.get('status') not in ('ahead','identical') or j.get('behind_by',0)!=0:raise Hold('HOLD_REMOTE_REWIND')
    def content(self,path,ref):
        if not (path.startswith(ROOT+'/') and '..' not in PurePosixPath(path).parts):raise Hold('HOLD_PATH_SCOPE')
        url='contents/'+urllib.parse.quote(path,safe='/')+'?ref='+urllib.parse.quote(ref,safe='')
        x=self.request(url)
        if x is None:return None
        if not isinstance(x,dict) or x.get('encoding')!='base64':raise Hold('HOLD_GITHUB_CONTENTS')
        try:return base64.b64decode(x['content'],validate=False)
        except (ValueError,KeyError) as exc:raise Hold('HOLD_BASE64') from exc
    def listing(self,path,ref):
        if not path.startswith(ROOT+'/'):raise Hold('HOLD_PATH_SCOPE')
        v=self.request('contents/'+urllib.parse.quote(path,safe='/')+'?ref='+urllib.parse.quote(ref,safe=''))
        if v is None:return []
        if not isinstance(v,list) or len(v)>200:raise Hold('HOLD_LISTING_SHAPE')
        out=[]
        for x in v:
            if not isinstance(x,dict) or x.get('type')!='file' or not re.fullmatch(r'(?:MAC|GH)-[0-9]{8}\.json',x.get('name','')):raise Hold('HOLD_UNEXPECTED_REMOTE_FILE')
            out.append(x['name'])
        return sorted(out)
    def put_once(self,path,content):
        if not path.startswith(ROOT+'/'):raise Hold('HOLD_PATH_SCOPE')
        if len(content)>MAX_JSON:raise Hold('HOLD_UPLOAD_SIZE')
        existed=self.content(path,self.branch)
        if existed is not None:
            if existed!=content:raise Hold('HOLD_REMOTE_CONTENT_CONFLICT')
            return 'IDEMPOTENT'
        payload={'message':'docs(mk): append sanitized bridge pilot record','branch':self.branch,
                 'content':base64.b64encode(content).decode('ascii')}
        result=self.request('contents/'+urllib.parse.quote(path,safe='/'),method='PUT',payload=payload)
        if not result or 'commit' not in result:raise Hold('HOLD_PUBLISH_ACK')
        return 'PUBLISHED'

def sync_local(ledger,api):
    h=api.branch_head();api.ensure_forward(ledger.last_remote(),h)
    # Delivery is at-least-once; remote file conflict is a fail-closed duplicate guard.
    sent=0
    for event_id,ev in ledger.queued():
        api.put_once(ROOT+'/streams/mac/'+event_id+'.json',canon(ev));sent+=1
    h=api.branch_head();api.ensure_forward(ledger.last_remote(),h)
    acks=0;incoming=0
    for filename in api.listing(ROOT+'/acks/mac',h):
        raw=api.content(ROOT+'/acks/mac/'+filename,h)
        ack=parse(raw)
        try:ledger.ack_outgoing(ack);acks+=1
        except Hold as err:
            if str(err)=='HOLD_ACK_UNKNOWN_EVENT':raise Hold('HOLD_FOREIGN_ACK') from err
            raise
    for filename in api.listing(ROOT+'/streams/github',h):
        ev=parse(api.content(ROOT+'/streams/github/'+filename,h))
        if filename!=ev['eventId']+'.json':raise Hold('HOLD_EVENT_PATH_MISMATCH')
        ack=ledger.receive(ev);incoming+=1
        api.put_once(ROOT+'/acks/github/'+filename,canon(ack))
    newhead=api.branch_head();api.ensure_forward(h,newhead)
    ledger.set_remote(newhead)
    return {'state':'PASS_TRANSPORT_SYNC_ONLY','sentAttempts':sent,'ackObserved':acks,'githubEventsObserved':incoming,
            'ledger':ledger.counts(),'remoteHead':newhead,'officialAcceptance':'HOLD'}

def github_worker(root,owner,actor):
    if not owner or actor!=owner or actor.lower().endswith('[bot]'):raise Hold('HOLD_ACTOR_AUTH')
    root=Path(root); folder=root/ROOT
    mac=folder/'streams/mac'; acks=folder/'acks/mac'; gh=folder/'streams/github'
    for d in (mac,acks,gh):
        if d.is_symlink():raise Hold('HOLD_LINKED_DIR')
        d.mkdir(parents=True,exist_ok=True)
    names=sorted(mac.glob('MAC-*.json'))
    if len(names)>100:raise Hold('HOLD_BATCH_LIMIT')
    generated=0
    for index,p in enumerate(names,1):
        if p.is_symlink() or not p.is_file() or p.stat().st_size>MAX_JSON:raise Hold('HOLD_SOURCE_FILE')
        ev=parse(p.read_bytes())
        if p.name!=ev['eventId']+'.json' or ev['producer']!='MAC_OSI_MK' or ev['sequence']!=index:raise Hold('HOLD_STREAM_ORDER')
        validate_event(ev)
        ack=canon(make_ack(ev)); out=acks/p.name
        if out.is_symlink():raise Hold('HOLD_ACK_SYMLINK')
        if out.exists():
            if out.read_bytes()!=ack:raise Hold('HOLD_ACK_MUTATION')
        else:
            out.write_bytes(ack);generated+=1
        # Reverse channel: one deterministic GH event for each accepted Mac test event.
        reply=make_event('GITHUB_MK',index,ev['sourceCommit'],code='GITHUB_RECEIVED',block=ev['blockId'],observed=ev['observedAt'])
        target=gh/('GH-'+f'{index:08d}'+'.json');data=canon(reply)
        if target.is_symlink():raise Hold('HOLD_REPLY_SYMLINK')
        if target.exists():
            if target.read_bytes()!=data:raise Hold('HOLD_REPLY_MUTATION')
        else:target.write_bytes(data);generated+=1
    return {'state':'PASS_GITHUB_PILOT_ONLY','receivedMacEvents':len(names),'writtenArtifacts':generated,'officialAcceptance':'HOLD'}

def safe_root(root):
    root=Path(root).expanduser()
    if root.is_symlink():raise Hold('HOLD_ROOT_SYMLINK')
    # Explicitly restrict the pilot to Mac Engineer state under the user's HOME.
    required=Path.home()/'Enguru/Runtime/MacEngineer/state/mk-bridge'
    if root.resolve(strict=False)!=required.resolve(strict=False):raise Hold('HOLD_ROOT_SCOPE')
    for ancestor in (root.parent,root.parent.parent,root.parent.parent.parent):
        if ancestor.is_symlink():raise Hold('HOLD_PARENT_SYMLINK')
    return root

def cli(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--bootstrap',action='store_true')
    parser.add_argument('--queue-demo',action='store_true')
    parser.add_argument('--inspect',action='store_true')
    parser.add_argument('--backup',action='store_true')
    parser.add_argument('--output',default='')
    parser.add_argument('--sync',action='store_true')
    parser.add_argument('--github-worker',action='store_true')
    parser.add_argument('--root',default=str(Path.home()/'Enguru/Runtime/MacEngineer/state/mk-bridge'))
    parser.add_argument('--repo-root',default='.')
    parser.add_argument('--base-commit',default='')
    parser.add_argument('--owner',default='')
    parser.add_argument('--actor',default='')
    a=parser.parse_args(argv)
    if sum(bool(getattr(a,k)) for k in ('self_test','preflight','bootstrap','queue_demo','inspect','backup','sync','github_worker'))!=1:
        raise Hold('HOLD_ONE_ACTION_REQUIRED')
    if a.self_test:
        import unittest
        start=Path(__file__).resolve().parents[1]/'tests'
        suite=unittest.defaultTestLoader.discover(str(start),pattern='test_enguru_mk_bridge_v1.py')
        result=unittest.TextTestRunner(verbosity=1).run(suite)
        if not result.wasSuccessful():raise Hold('HOLD_SELF_TEST')
        print('STATE=PASS_BRIDGE_ISOLATED_TESTS_ONLY')
        return
    if a.github_worker:
        print(json.dumps(github_worker(a.repo_root,a.owner,a.actor),sort_keys=True));return
    if a.preflight:
        import platform
        if sys.version_info<(3,12):raise Hold('HOLD_PYTHON_VERSION')
        if sqlite3.sqlite_version_info<(3,35):raise Hold('HOLD_SQLITE_VERSION')
        print(json.dumps({'state':'PASS_LOCAL_RUNTIME_PREFLIGHT_ONLY','python':platform.python_version(),
          'sqlite':sqlite3.sqlite_version,'networkRequiredForSync':True,'productWrites':0,'officialAcceptance':'HOLD'},sort_keys=True));return
    root=safe_root(a.root)
    if a.bootstrap:
        if root.exists():
            if root.is_symlink() or not root.is_dir():raise Hold('HOLD_ROOT_STATE')
        else:root.mkdir(parents=True,mode=0o700)
        if root.stat().st_mode & 0o077:os.chmod(root,0o700)
        ledger=LocalLedger(root/'bridge.sqlite');print(json.dumps({'state':'PASS_LOCAL_BOOTSTRAP_ONLY','path':str(root),'ledger':ledger.counts()}));ledger.close();return
    if not (root/'bridge.sqlite').is_file():raise Hold('HOLD_BOOTSTRAP_REQUIRED')
    ledger=LocalLedger(root/'bridge.sqlite')
    try:
        if a.inspect:
            print(json.dumps({'state':'PASS_LOCAL_INSPECTION','ledger':ledger.counts(),'remoteHead':ledger.last_remote()}));return
        if a.backup:
            dest=Path(a.output).expanduser()
            archive=Path.home()/'Desktop/AudiV13'
            if not a.output or dest.parent.resolve(strict=False)!=archive.resolve(strict=False) or dest.suffix!='.sqlite':
                raise Hold('HOLD_BACKUP_ARCHIVE_SCOPE')
            if not archive.is_dir() or archive.is_symlink():raise Hold('HOLD_ARCHIVE_DIRECTORY')
            digest=ledger.backup(dest)
            print(json.dumps({'state':'PASS_SQLITE_SNAPSHOT_ONLY','backup':str(dest),'sha256':digest,'officialAcceptance':'HOLD'},sort_keys=True));return
        if a.queue_demo:
            if not HEX40.fullmatch(a.base_commit):raise Hold('HOLD_SOURCE_COMMIT_REQUIRED')
            seq=ledger.db.execute('SELECT coalesce(max(seq),0)+1 FROM outgoing').fetchone()[0]
            print(json.dumps({'state':ledger.enqueue(make_event('MAC_OSI_MK',seq,a.base_commit)), 'queued':seq,'officialAcceptance':'HOLD'}));return
        if a.sync:
            token=os.environ.get('ENGURU_MK_GITHUB_TOKEN','')
            print(json.dumps(sync_local(ledger,GitHubAPI(token)),sort_keys=True));return
    finally:ledger.close()

def main():
    try:cli()
    except Hold as exc:
        print('STATE=HOLD_GUVENLI_DUR; REASON='+str(exc))
        sys.exit(50)

if __name__=='__main__':main()
