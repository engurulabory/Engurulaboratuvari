"""Private isolated profile; SQLite WAL transactional queue and event chain."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3
import stat
import time
from .contracts import Rejected, digest, encoded


def private_root(path):
    p=Path(path).absolute()
    if '..' in p.parts or any(x.is_symlink() for x in (p,*p.parents)):
        raise Rejected('SYMLINK_OR_TRAVERSAL')
    if not p.exists(): p.mkdir(mode=0o700,parents=True)
    st=p.stat()
    if not stat.S_ISDIR(st.st_mode) or st.st_uid!=os.getuid() or st.st_mode&0o022:
        raise Rejected('PRIVATE_ROOT_REQUIRED')
    return p


def read_private(path, limit=3000000):
    p=Path(path)
    if any(x.is_symlink() for x in p.parents):raise Rejected('SYMLINK_PARENT')
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as f:
        s=os.fstat(f.fileno())
        if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_nlink!=1 or s.st_mode&0o022:
            raise Rejected('PRIVATE_REGULAR_FILE')
        b=f.read(limit+1)
        if len(b)>limit:raise Rejected('FILE_SIZE')
        return b


def write_new(path, data):
    p=Path(path)
    if any(x.is_symlink() for x in p.parents):raise Rejected('SYMLINK_PARENT')
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())


class Ledger:
    def __init__(self, root):
        self.root=private_root(root);p=self.root/'tasks.sqlite'
        if not p.exists():write_new(p,b'')
        read_private(p)
        for name in ('tasks.sqlite-wal','tasks.sqlite-shm'):
            if os.path.lexists(self.root/name):read_private(self.root/name)
        self.db=sqlite3.connect(p,timeout=10,isolation_level=None)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS jobs(seq INTEGER PRIMARY KEY, command TEXT UNIQUE NOT NULL,
            payload TEXT NOT NULL,plan TEXT NOT NULL,state TEXT NOT NULL, effect TEXT NOT NULL DEFAULT 'NONE');
          CREATE UNIQUE INDEX IF NOT EXISTS one_active ON jobs((1)) WHERE state='RUNNING';
          CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY,command TEXT NOT NULL,
            kind TEXT NOT NULL,data TEXT NOT NULL,previous TEXT NOT NULL,hash TEXT NOT NULL);
          CREATE TRIGGER IF NOT EXISTS immutable_event_update BEFORE UPDATE ON events
            BEGIN SELECT RAISE(ABORT,'APPEND_ONLY');END;
          CREATE TRIGGER IF NOT EXISTS immutable_event_delete BEFORE DELETE ON events
            BEGIN SELECT RAISE(ABORT,'APPEND_ONLY');END;
          CREATE TABLE IF NOT EXISTS proofs(command TEXT,block TEXT,receipt TEXT NOT NULL,
            PRIMARY KEY(command,block));
          CREATE TABLE IF NOT EXISTS nonces(nonce TEXT PRIMARY KEY);
          CREATE TABLE IF NOT EXISTS control(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        ''')

    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:yield;self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise

    def event(self, cid, kind, data):
        last=self.db.execute('SELECT hash FROM events ORDER BY seq DESC LIMIT 1').fetchone()
        prev=last[0] if last else '0'*64
        payload=encoded(data).decode();h=digest([cid,kind,payload,prev])
        self.db.execute('INSERT INTO events(command,kind,data,previous,hash) VALUES(?,?,?,?,?)',
                        (cid,kind,payload,prev,h))

    def audit_chain(self):
        prev='0'*64
        for row in self.db.execute('SELECT * FROM events ORDER BY seq'):
            if row['previous']!=prev or row['hash']!=digest([row['command'],row['kind'],row['data'],prev]):
                raise Rejected('EVENT_CHAIN')
            prev=row['hash']
        return prev

    def submit(self,cid,payload,plan):
        if not isinstance(cid,str) or not cid or len(cid)>128:raise Rejected('COMMAND_ID')
        p=encoded(payload).decode();sealed=encoded(plan).decode()
        with self.transaction():
            old=self.db.execute('SELECT * FROM jobs WHERE command=?',(cid,)).fetchone()
            if old:
                if (old['payload'],old['plan'])!=(p,sealed):raise Rejected('IDEMPOTENCY_CONFLICT')
                return dict(old)
            self.db.execute('INSERT INTO jobs(command,payload,plan,state) VALUES(?,?,?,?)',(cid,p,sealed,'READY'))
            self.event(cid,'SUBMITTED',{'plan':digest(plan)})
        return dict(self.db.execute('SELECT * FROM jobs WHERE command=?',(cid,)).fetchone())

    def claim(self,cid,nonce):
        with self.transaction():
            if self.db.execute("SELECT 1 FROM jobs WHERE state='RUNNING'").fetchone():return False
            row=self.db.execute("SELECT command FROM jobs WHERE state='READY' ORDER BY seq LIMIT 1").fetchone()
            if not row or row[0]!=cid:return False
            paused=self.db.execute("SELECT value FROM control WHERE key='paused'").fetchone()
            if paused and paused[0]=='1':return False
            if self.db.execute('SELECT 1 FROM nonces WHERE nonce=?',(nonce,)).fetchone():raise Rejected('NONCE_REPLAY')
            self.db.execute('INSERT INTO nonces VALUES(?)',(nonce,))
            self.db.execute("UPDATE jobs SET state='RUNNING',effect='UNKNOWN' WHERE command=?",(cid,))
            self.event(cid,'CLAIMED',{'nonce':nonce})
        return True

    def hold(self,cid,reason):
        with self.transaction():
            self.db.execute("UPDATE jobs SET state='HOLD' WHERE command=? AND state!='DONE'",(cid,))
            self.event(cid,'HOLD',{'reason':reason})

    def recover(self):
        # Explicit recovery only; another live worker must hold profile flock.
        with self.transaction():
            rows=self.db.execute("SELECT command FROM jobs WHERE state='RUNNING'").fetchall()
            for row in rows:
                self.db.execute("UPDATE jobs SET state='HOLD',effect='UNKNOWN' WHERE command=?",(row[0],))
                self.event(row[0],'RECOVERING',{'reason':'READ_ONLY_RECONCILE_REQUIRED_NO_REPLAY'})
        return len(rows)

    def control(self,pause):
        with self.transaction():
            self.db.execute("INSERT INTO control VALUES('paused',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",('1' if pause else '0',))

    def close(self):self.db.close()
