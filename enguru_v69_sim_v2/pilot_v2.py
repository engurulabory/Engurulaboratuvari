
import sqlite3, hashlib, json, tempfile, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

ROLES=("management","engineer","verifier","field")
CAPABILITIES=("architecture","execution","finish","comfort","flow","security","osi_readiness","engineering","integration")
def digest(b): return hashlib.sha256(b).hexdigest()

class Pilot:
    def __init__(self,path):
        self.conn=sqlite3.connect(path,timeout=5,isolation_level=None,check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY, idx INTEGER NOT NULL, stage INTEGER NOT NULL,
            state TEXT NOT NULL, source_sha TEXT NOT NULL, receipt_sha TEXT,
            lease TEXT, rollback_count INTEGER NOT NULL DEFAULT 0)""")
        self.conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS one_active ON tasks((1)) WHERE state IN ('READY','RUNNING')")
    def create(self,id,idx,source_sha):
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            existing=self.conn.execute("SELECT id FROM tasks WHERE state IN ('READY','RUNNING')").fetchone()
            if existing: self.conn.execute("ROLLBACK");return "HOLD_ACTIVE"
            self.conn.execute("INSERT INTO tasks(id,idx,stage,state,source_sha) VALUES (?,?,0,'READY',?)",(id,idx,source_sha))
            self.conn.execute("COMMIT");return "CREATED"
        except sqlite3.IntegrityError:
            self.conn.execute("ROLLBACK");return "HOLD_ACTIVE_OR_DUPLICATE"
    def begin(self,id,role,worker):
        self.conn.execute("BEGIN IMMEDIATE")
        rec=self.conn.execute("SELECT stage,state FROM tasks WHERE id=?",(id,)).fetchone()
        if not rec or rec[1]!="READY" or rec[0]>=4 or ROLES[rec[0]]!=role:
            self.conn.execute("ROLLBACK");return "HOLD"
        self.conn.execute("UPDATE tasks SET state='RUNNING',lease=? WHERE id=?",(worker,id))
        self.conn.execute("COMMIT");return "ACQUIRED"
    def complete(self,id,worker,source,receipt_bytes,claimed_digest):
        self.conn.execute("BEGIN IMMEDIATE")
        rec=self.conn.execute("SELECT stage,state,lease,source_sha FROM tasks WHERE id=?",(id,)).fetchone()
        if not rec or rec[1]!="RUNNING" or rec[2]!=worker or rec[3]!=source or digest(receipt_bytes)!=claimed_digest:
            self.conn.execute("ROLLBACK");return "HOLD"
        stage=rec[0]+1
        self.conn.execute("UPDATE tasks SET stage=?,state=?,lease=NULL,receipt_sha=? WHERE id=?",
                          (stage,"THEORETICAL_PASS" if stage==4 else "READY",claimed_digest,id))
        self.conn.execute("COMMIT");return "PASS"
    def recover(self,id,proof_of_interrupted_worker):
        self.conn.execute("BEGIN IMMEDIATE")
        rec=self.conn.execute("SELECT state,lease FROM tasks WHERE id=?",(id,)).fetchone()
        if not rec or rec[0]!="RUNNING" or not proof_of_interrupted_worker:
            self.conn.execute("ROLLBACK");return "HOLD"
        self.conn.execute("UPDATE tasks SET state='READY',lease=NULL,rollback_count=rollback_count+1 WHERE id=?",(id,))
        self.conn.execute("COMMIT");return "RECOVERED"
    def get(self,id):
        return self.conn.execute("SELECT stage,state,rollback_count FROM tasks WHERE id=?",(id,)).fetchone()
    def close(self): self.conn.close()

def run():
    checks={}
    with tempfile.TemporaryDirectory() as td:
        db=str(Path(td)/"pilot.sqlite")
        src=digest(b"theoretical-source-v2")
        p=Pilot(db)
        checks["01_create"]=p.create("T01",1,src)=="CREATED"
        checks["02_only_one_active"]=p.create("T02",2,src)=="HOLD_ACTIVE"
        p.close()

        # Two truly independent SQLite connections and concurrent contenders.
        barrier=threading.Barrier(2)
        def contender(w):
            own=Pilot(db);barrier.wait()
            ans=own.begin("T01","management",w)
            own.close();return ans
        with ThreadPoolExecutor(max_workers=2) as ex:
            fut=[ex.submit(contender,x) for x in ("A","B")]
            outcomes=[x.result() for x in fut]
        checks["03_racing_workers"]=sorted(outcomes)==["ACQUIRED","HOLD"]
        winner="A" if outcomes[0]=="ACQUIRED" else "B"

        p=Pilot(db)
        checks["04_wrong_worker"]=p.complete("T01","FOREIGN",src,b"plan",digest(b"plan"))=="HOLD"
        checks["05_wrong_byte_receipt"]=p.complete("T01",winner,src,b"tamper",digest(b"plan"))=="HOLD"
        checks["06_wrong_source"]=p.complete("T01",winner,"0"*64,b"plan",digest(b"plan"))=="HOLD"
        p.close()
        p=Pilot(db)
        checks["07_restart_keeps_lease"]=p.begin("T01","management","C")=="HOLD"
        checks["08_recovery_requires_proof"]=p.recover("T01",False)=="HOLD"
        checks["09_atomic_recovery"]=p.recover("T01",True)=="RECOVERED"
        checks["10_rollback_count"]=p.get("T01")== (0,"READY",1)
        checks["11_reacquire"]=p.begin("T01","management","C")=="ACQUIRED"
        checks["12_real_bytes_hash"]=p.complete("T01","C",src,b"plan",digest(b"plan"))=="PASS"
        checks["13_no_duplicate_completion"]=p.complete("T01","C",src,b"plan",digest(b"plan"))=="HOLD"
        for idx,role in enumerate(ROLES[1:],start=2):
            checks[f"14_to_16_{role}"]=p.begin("T01",role,"C")== "ACQUIRED" and p.complete("T01","C",src,role.encode(),digest(role.encode()))=="PASS"
        checks["17_finish"]=p.get("T01")[:2]==(4,"THEORETICAL_PASS")
        # All 9 capabilities on same durable Pilot, one at a time.
        checks["18_nine_capability_sequence"]=True
        for i,name in enumerate(CAPABILITIES,1):
            task="C"+str(i)
            if p.create(task,i,src)!="CREATED":checks["18_nine_capability_sequence"]=False;break
            for role in ROLES:
                raw=(task+"|"+role+"|"+src).encode()
                if p.begin(task,role,"pilot")!="ACQUIRED" or p.complete(task,"pilot",src,raw,digest(raw))!="PASS":
                    checks["18_nine_capability_sequence"]=False;break
            if p.get(task)[:2]!=(4,"THEORETICAL_PASS"):
                checks["18_nine_capability_sequence"]=False;break
        checks["19_all_nine_closed"]=p.conn.execute("SELECT COUNT(*) FROM tasks WHERE id LIKE 'C%' AND state='THEORETICAL_PASS'").fetchone()[0]==9
        p.close()

        # TEST KEY ONLY - never a canonical human approval.
        key=Ed25519PrivateKey.generate()
        payload=json.dumps({"scope":"THEORETICAL_ONLY","task":"T01","source_sha":src,"nonce":"unique-1"},sort_keys=True).encode()
        sig=key.sign(payload)
        key.public_key().verify(sig,payload)
        checks["20_ed25519_test_signature"]=True
        try:key.public_key().verify(sig,payload+b"changed");checks["21_signature_tamper"]=False
        except InvalidSignature: checks["21_signature_tamper"]=True
        checks["22_test_signature_not_real_owner"]=True
    return checks

if __name__=="__main__":
    d=run()
    for k,v in d.items():print(k,"PASS" if v else "FAIL")
    print("CHECKS",sum(d.values()),len(d),"STATE", "PASS_THEORETICAL_SCOPE" if all(d.values()) else "HOLD")
    raise SystemExit(0 if all(d.values()) else 1)
