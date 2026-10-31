"""Integrated candidate. Supported positive task: fixed unique_jobs repair only.

Other natural language tasks HOLD, with no arbitrary code execution fallback.
Local caller grants cover this private fixture capability, not system installs.
"""
from dataclasses import asdict
import fcntl
import json
import os
from .contracts import Plan, Rejected, digest, encoded, progress
from .storage import Ledger, read_private, write_new
from .security import Authority, tool_proposal
from .broker import Broker, Verifier, fixture_pin


def recognize(text):
    if not isinstance(text,str) or not 1<=len(text)<=4000:raise Rejected('COMMAND_TEXT')
    # The only supported task. Hostile or unrelated text cannot broaden scope.
    folded=text.casefold()
    if any(s in folded for s in ('../','/users/','/etc/','sudo ','ignore previous','önceki talimat','prompt injection','curl ','rm -','http://','https://')):
        raise Rejected('UNTRUSTED_INSTRUCTION')
    if 'unique_jobs' not in folded or not any(x in folded for x in ('sıra','order')):
        raise Rejected('HOLD_UNSUPPORTED_TASK')
    return 'unique_jobs_repair'


class Kernel:
    def __init__(self,profile,roles):
        self.ledger=Ledger(profile);self.root=self.ledger.root;self.roles=roles
        self.authority=Authority(self.root)
        self.broker=Broker(self.root,self.authority);self.verifier=Verifier(self.root,self.authority)

    def plan(self,cid):
        return Plan(cid,'v015.1',fixture_pin(),digest(str(self.root)),
                    (('B1',10000,()),)).validate()

    def execute(self,cid,text,grant=None):
        recognize(text);p=self.plan(cid)
        self.ledger.submit(cid,{'text':text,'task_kind':'unique_jobs_repair'},asdict(p))
        old=self.ledger.db.execute('SELECT state FROM jobs WHERE command=?',(cid,)).fetchone()[0]
        if old=='DONE':return self.snapshot(cid)
        lockpath=self.root/'worker.lock'
        if not lockpath.exists():
            try:write_new(lockpath,b'')
            except FileExistsError:pass
        read_private(lockpath)
        fd=os.open(lockpath,os.O_RDWR|os.O_NOFOLLOW)
        try:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise Rejected('ACTIVE_WORKER')
            if old!='READY':raise Rejected('HOLD_RECONCILE_BEFORE_RETRY')
            # Only this local owner bridge mints private-pilot grants. No model field enters it.
            g=grant if grant is not None else self.authority.issue_local_pilot(p,self.root)
            nonce=self.authority.validate(g,p,self.root)
            if not self.ledger.claim(cid,nonce):raise Rejected('QUEUE_OR_PAUSED')
            try:
                mgr=self.roles.propose('manager',text,p)
                if mgr!={'operation':'plan_unique_jobs_repair','plan_sha256':p.sha}:raise Rejected('MANAGER_SCHEMA')
                self.ledger.event(cid,'MANAGER_PROPOSAL',{'proposal':mgr,'provider':self.roles.kind})
                exe=self.roles.propose('executor',text,p);tool_proposal(exe,p)
                self.ledger.event(cid,'EXECUTOR_PROPOSAL',{'proposal':exe,'provider':self.roles.kind})
                # Recheck expiry/identity immediately before actual side effects.
                self.authority.validate(g,p,self.root)
                paused=self.ledger.db.execute("SELECT value FROM control WHERE key='paused'").fetchone()
                if paused and paused[0]=='1':raise Rejected('PAUSED_AT_SAFE_BOUNDARY')
                receipt=self.broker.execute(p,cid)
                verified=self.verifier.verify(receipt,p,cid)
                with self.ledger.transaction():
                    row=self.ledger.db.execute('SELECT state,plan FROM jobs WHERE command=?',(cid,)).fetchone()
                    if row['state']!='RUNNING' or row['plan']!=encoded(asdict(p)).decode():raise Rejected('STALE_PLAN')
                    self.ledger.db.execute('INSERT INTO proofs VALUES(?,?,?)',(cid,'B1',encoded(verified).decode()))
                    self.ledger.db.execute("UPDATE jobs SET state='DONE',effect='APPLIED_VERIFIED' WHERE command=?",(cid,))
                    self.ledger.event(cid,'VERIFIED',{'receipt_sha256':digest(receipt),'output_sha256':verified['output_sha256']})
                return self.snapshot(cid)
            except BaseException as e:
                self.ledger.hold(cid,type(e).__name__+': '+str(e)[:200]);raise
        finally:os.close(fd)

    def snapshot(self,cid=None):
        self.ledger.audit_chain()
        if cid is None:
            row=self.ledger.db.execute('SELECT * FROM jobs ORDER BY seq DESC LIMIT 1').fetchone()
        else:row=self.ledger.db.execute('SELECT * FROM jobs WHERE command=?',(cid,)).fetchone()
        if row is None:return {'state':'IDLE','completion_percent':0,'remaining_percent':100,
                 'donecheck':'HOLD','message':'Bir görev yazın. Desteklenen pilot: unique_jobs sıra koruma onarımı.'}
        p=self.plan(row['command'])
        if encoded(asdict(p)).decode()!=row['plan']:raise Rejected('PLAN_SOURCE_DRIFT')
        proofs=list(self.ledger.db.execute('SELECT block,receipt FROM proofs WHERE command=?',(row['command'],)))
        # Re-verify persisted artifact/test evidence, never trust stored DONE alone.
        valid=[]
        for block,v in proofs:
            saved=json.loads(v);path=self.root/'jobs'/digest(row['command'])/'operation.json'
            rec=json.loads(read_private(path))
            fresh=self.verifier.verify(rec,p,row['command'],rerun=False)
            if saved['receipt_sha256']!=fresh['receipt_sha256']:raise Rejected('PROOF_DRIFT')
            valid.append(block)
        metrics=progress(p,valid)
        if row['state']=='DONE' and metrics['done_weight']!=10000:raise Rejected('EVIDENCE_REQUIRED_FOR_DONE')
        last=self.ledger.db.execute('SELECT seq,kind,data FROM events WHERE command=? ORDER BY seq DESC LIMIT 1',(row['command'],)).fetchone()
        return dict(schema='enguru.readonly.projection/v015.1',task_id=row['command'],plan_sha256=p.sha,
           source_sha256=p.source,state=row['state'],effect=row['effect'],**metrics,
           active_block=None if row['state']=='DONE' else 'B1',
           last_event_seq=last['seq'],last_verified_event=last['kind'],
           donecheck='PASS_SCOPED_PILOT' if metrics['done_weight']==10000 else 'HOLD',
           product_verified_finish='HOLD',mac_field='NOT_TESTED',
           evidence=str(self.root/'jobs'/digest(row['command'])/'operation.json'),
           queue=[dict(x) for x in self.ledger.db.execute('SELECT command,state FROM jobs ORDER BY seq')])

    def recover(self):
        path=self.root/'worker.lock'
        if not path.exists():
            try:write_new(path,b'')
            except FileExistsError:pass
        read_private(path);fd=os.open(path,os.O_RDWR|os.O_NOFOLLOW)
        try:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise Rejected('LIVE_WORKER_RECOVERY_REJECTED')
            return self.ledger.recover()
        finally:os.close(fd)

    def close(self):self.ledger.close()
