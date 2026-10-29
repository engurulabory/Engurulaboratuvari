"""ENGÜRÜ E00 Durumdan Vazife Kutusu: durable local research/test queue.

The box never edits code, grants authority, publishes, merges, signs or
declares Verified Finish. It stores observational events, groups ready tasks,
records evidence candidates, and archives only after external verification.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3

DOMAINS = (
    "GOAL", "SOURCE", "CODE", "TEST", "PERFORMANCE", "RECOVERY",
    "DATA", "INTEGRATION", "SECURITY", "USER_EXPERIENCE",
    "AESTHETIC", "DELIVERY"
)
KINDS = ("SUCCESS", "FAILURE", "REGRESSION", "INTERRUPTION",
         "DRIFT", "RISK", "FEEDBACK", "OPPORTUNITY")
OUTCOMES = ("POSITIVE", "NEGATIVE", "UNCERTAIN")
ACTIVE = ("NEW", "READY", "RESEARCH", "BATCHED", "HOLD", "CANDIDATE", "OWNER_REVIEW")
HEX = re.compile(r"^[a-f0-9]{64}$")
COMMIT = re.compile(r"^[a-f0-9]{40}$")
IDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,90}$")
FIELDS = frozenset(("eventId","goalId","sourceSha256","domain","kind",
                    "outcome","need","description","lesson"))
STATE_ORDER = ("NEW","RESEARCH","READY","BATCHED","HOLD",
               "CANDIDATE","OWNER_REVIEW","ARCHIVED")


def now():
    return datetime.now(timezone.utc).isoformat()


def identity(value):
    if not isinstance(value, str) or not IDENT.fullmatch(value):
        raise ValueError("INVALID_IDENTITY")
    return value


def source_hash(value):
    if not isinstance(value, str) or not HEX.fullmatch(value):
        raise ValueError("INVALID_SOURCE_SHA")
    return value


def text_value(value, max_len=500):
    if not isinstance(value,str) or not value.strip() or len(value)>max_len:
        raise ValueError("INVALID_TEXT")
    return value


def event_valid(e):
    if type(e) is not dict or set(e)!=FIELDS:
        raise ValueError("EVENT_SCHEMA_HOLD")
    identity(e["eventId"]); identity(e["goalId"]); source_hash(e["sourceSha256"])
    if not isinstance(e["domain"],str) or e["domain"] not in DOMAINS:
        raise ValueError("UNKNOWN_DOMAIN")
    if not isinstance(e["kind"],str) or e["kind"] not in KINDS:
        raise ValueError("UNKNOWN_KIND")
    if not isinstance(e["outcome"],str) or e["outcome"] not in OUTCOMES:
        raise ValueError("UNKNOWN_OUTCOME")
    text_value(e["need"],100); text_value(e["description"]); text_value(e["lesson"])
    return e


def case_fingerprint(e):
    selected=(e["goalId"],e["sourceSha256"],e["domain"],e["kind"],
              e["description"].strip().casefold())
    return hashlib.sha256(json.dumps(selected,ensure_ascii=False,
                                     separators=(",",":")).encode()).hexdigest()


class ExperienceBox:
    def __init__(self, db_path):
        self.path=Path(db_path)
        if self.path.is_symlink() or not self.path.parent.is_dir():
            raise ValueError("SAFE_EXISTING_PARENT_REQUIRED")
        self.db=sqlite3.connect(str(self.path),timeout=8,isolation_level=None)
        self.db.row_factory=sqlite3.Row
        self.db.execute("PRAGMA busy_timeout=8000")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS cases(
           event_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL,
           event_json TEXT NOT NULL, goal TEXT NOT NULL, source_sha TEXT NOT NULL,
           domain TEXT NOT NULL, kind TEXT NOT NULL, outcome TEXT NOT NULL,
           state TEXT NOT NULL, solution TEXT, solution_ref TEXT,
           batch_id TEXT, attempts INTEGER NOT NULL DEFAULT 0,
           test_sha TEXT, update_sha TEXT, created TEXT NOT NULL,
           updated TEXT NOT NULL);
        CREATE UNIQUE INDEX IF NOT EXISTS one_open_fingerprint
          ON cases(fingerprint) WHERE state != 'ARCHIVED';
        CREATE TABLE IF NOT EXISTS batches(
           id TEXT PRIMARY KEY, goal TEXT NOT NULL, source_sha TEXT NOT NULL,
           domain TEXT NOT NULL, state TEXT NOT NULL, attempts INTEGER NOT NULL,
           created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS journal(
           id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT,
           action TEXT NOT NULL, previous TEXT, current TEXT NOT NULL,
           note TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS diagnostics(
           id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL,
           cause TEXT NOT NULL, gap TEXT NOT NULL,
           requirement TEXT NOT NULL, correction TEXT NOT NULL,
           attempts_at_diagnosis INTEGER NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS attempts(
           id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL,
           batch_id TEXT NOT NULL, round INTEGER NOT NULL,
           verdict TEXT NOT NULL, reason TEXT NOT NULL,
           receipt_sha TEXT, created TEXT NOT NULL);
        """)
    @contextmanager
    def _transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        else:
            self.db.execute("COMMIT")
    def close(self):
        self.db.close()
    def _row(self,event_id):
        r=self.db.execute("SELECT * FROM cases WHERE event_id=?",(identity(event_id),)).fetchone()
        if r is None: raise ValueError("UNKNOWN_EVENT")
        return r
    def _log(self,eid,action,old,new,note):
        self.db.execute("INSERT INTO journal(event_id,action,previous,current,note,created) VALUES (?,?,?,?,?,?)",
                        (eid,action,old,new,text_value(note,600),now()))
    def _state(self,eid,expected,new,action,note):
        r=self._row(eid)
        if r["state"] not in expected: raise ValueError("ILLEGAL_STATE_TRANSITION")
        self.db.execute("UPDATE cases SET state=?,updated=? WHERE event_id=?",
                        (new,now(),eid))
        self._log(eid,action,r["state"],new,note)
    def put(self,event):
        e=event_valid(event)
        eid=e["eventId"]
        fp=case_fingerprint(e)
        canonical=json.dumps(e,sort_keys=True,ensure_ascii=False,separators=(",",":"))
        with self._transaction():
            old=self.db.execute("SELECT event_json FROM cases WHERE event_id=?",(eid,)).fetchone()
            if old:
                if old["event_json"]!=canonical: raise ValueError("IDENTITY_REUSE_WITH_DIFFERENT_EVENT")
                return {"state":"IDEMPOTENT_EXISTING","eventId":eid}
            seen=self.db.execute("SELECT event_id FROM cases WHERE fingerprint=? AND state!='ARCHIVED'",(fp,)).fetchone()
            if seen: return {"state":"DEDUPLICATED_OPEN","eventId":seen["event_id"]}
            self.db.execute(
              "INSERT INTO cases(event_id,fingerprint,event_json,goal,source_sha,domain,kind,outcome,state,created,updated) "
              "VALUES (?,?,?,?,?,?,?,?,'NEW',?,?)",
              (eid,fp,canonical,e["goalId"],e["sourceSha256"],e["domain"],
               e["kind"],e["outcome"],now(),now()))
            self._log(eid,"OBSERVED",None,"NEW","Unverified observation; no test PASS")
        return {"state":"NEW","eventId":eid}
    def triage(self,eid,*,solution=None,solution_ref=None):
        with self._transaction():
            r=self._row(eid)
            if r["state"] not in ("NEW","RESEARCH","HOLD"): raise ValueError("TRIAGE_NOT_ALLOWED")
            ready=solution is not None
            if ready:
                text_value(solution);text_value(solution_ref)
                new="READY"
                self.db.execute("UPDATE cases SET solution=?,solution_ref=? WHERE event_id=?",
                                (solution,solution_ref,eid))
            else:
                new="RESEARCH"
            self._state(eid,("NEW","RESEARCH","HOLD"),new,"TRIAGE",
                        "Candidate recipe recorded; requires real proof" if ready else "Solution research still required")
        return {"eventId":eid,"state":new,"solutionVerified":False}
    def diagnose(self,eid,*,cause,gap,requirement,correction):
        """Preserve WHY a failure occurred and WHAT will change before retest."""
        fields=[text_value(x) for x in (cause,gap,requirement,correction)]
        with self._transaction():
            r=self._row(eid)
            if r["state"] not in ("NEW","RESEARCH","HOLD"):
                raise ValueError("DIAGNOSIS_NOT_ALLOWED")
            self.db.execute(
                "INSERT INTO diagnostics(event_id,cause,gap,requirement,correction,attempts_at_diagnosis,created) "
                "VALUES (?,?,?,?,?,?,?)",(eid,*fields,r["attempts"],now()))
            self._log(eid,"FAILURE_DIAGNOSIS",r["state"],r["state"],
                      "Cause, gap, requirement and corrective action preserved")
        return {"eventId":eid,"state":r["state"],"diagnosisRecorded":True,
                "officialPassIssued":False}

    def make_batch(self,event_ids):
        if type(event_ids) not in (list,tuple) or not 1<=len(event_ids)<=12 or len(set(event_ids))!=len(event_ids):
            raise ValueError("INVALID_BATCH_SIZE_OR_DUPLICATES")
        with self._transaction():
            rows=[self._row(x) for x in event_ids]
            if any(r["state"]!="READY" for r in rows): raise ValueError("NOT_READY_FOR_BATCH")
            if len({(r["goal"],r["source_sha"],r["domain"]) for r in rows})!=1:
                raise ValueError("MIXED_GOAL_SOURCE_OR_DOMAIN")
            goal,source,domain=(rows[0][k] for k in ("goal","source_sha","domain"))
            signature="|".join(sorted(event_ids))+":"+now()
            bid="E00B-"+hashlib.sha256(signature.encode()).hexdigest()[:24]
            self.db.execute("INSERT INTO batches(id,goal,source_sha,domain,state,attempts,created) VALUES (?,?,?,?,?,?,?)",
                            (bid,goal,source,domain,"TESTING",0,now()))
            for eid in event_ids:
                self.db.execute("UPDATE cases SET batch_id=? WHERE event_id=?",(bid,eid))
                self._state(eid,("READY",),"BATCHED","BATCH","Scoped, source-pinned batch candidate")
        return {"batchId":bid,"state":"TESTING","events":len(event_ids),
                "officialPassIssued":False}
    def assess_batch(self,bid,worker,max_rounds=3):
        """Worker is existing authorized DÖM callback; the box itself has no executor."""
        if not callable(worker) or type(max_rounds) is not int or not 1<=max_rounds<=3:
            raise ValueError("UNAUTHORIZED_OR_UNBOUNDED_TEST")
        b=self.db.execute("SELECT * FROM batches WHERE id=?",(bid,)).fetchone()
        if not b or b["state"]!="TESTING": raise ValueError("BATCH_NOT_TESTABLE")
        rows=list(self.db.execute("SELECT * FROM cases WHERE batch_id=? ORDER BY event_id",(bid,)))
        if not rows or any(r["state"]!="BATCHED" for r in rows):
            raise ValueError("BATCH_SOURCE_STATE_CHANGED")
        remaining={r["event_id"]:r for r in rows}
        receipts={}
        records=[]
        counts={r["event_id"]:0 for r in rows}
        for i in range(1,max_rounds+1):
            for eid,r in list(remaining.items()):
                counts[eid]+=1
                try:
                    proof=worker(json.loads(r["event_json"]),r["solution"],i)
                    failure="EVIDENCE_INSUFFICIENT"
                except Exception as exc:
                    proof={}
                    failure="WORKER_ERROR_"+type(exc).__name__
                verified=(type(proof) is dict and
                    proof.get("state")=="E00_ISOLATED_TEST_CANDIDATE" and
                    proof.get("realTestObserved") is True and
                    proof.get("officialPassIssued") is False and
                    isinstance(proof.get("journalHeadSha256"),str) and
                    HEX.fullmatch(proof["journalHeadSha256"]))
                if verified:
                    receipts[eid]=proof["journalHeadSha256"]
                    del remaining[eid]
                elif type(proof) is dict and isinstance(proof.get("reason"),str):
                    failure=proof["reason"][:90] or failure
                records.append((eid,bid,i,"CANDIDATE" if verified else "HOLD",
                                "TECHNICAL_CANDIDATE" if verified else failure,
                                receipts.get(eid),now()))
            if not remaining: break
        with self._transaction():
            self.db.executemany(
               "INSERT INTO attempts(event_id,batch_id,round,verdict,reason,receipt_sha,created) "
               "VALUES (?,?,?,?,?,?,?)",records)
            previous=b["attempts"]
            self.db.execute("UPDATE batches SET state=?, attempts=? WHERE id=?",
                            ("CANDIDATE" if not remaining else "HOLD",previous+i,bid))
            for r in rows:
                eid=r["event_id"]
                target="CANDIDATE" if eid in receipts else "HOLD"
                self.db.execute("UPDATE cases SET attempts=attempts+?,test_sha=? WHERE event_id=?",
                                (counts[eid],receipts.get(eid),eid))
                self._state(eid,("BATCHED",),target,"TEST_RESULT",
                            "DÖM isolated test evidence candidate" if target=="CANDIDATE"
                            else "Unresolved failure preserved for diagnosis and next bounded cycle")
        return {"state":"ISOLATED_BATCH_CANDIDATE" if not remaining else "BATCH_HOLD",
                "batchId":bid,"rounds":i,"tested":len(rows),
                "candidate":len(receipts),"hold":len(remaining),
                "officialPassIssued":False,"productVerifiedFinish":"NOT_ISSUED"}
    def retry_batch(self,bid,corrections):
        """Resume an unresolved package with fresh corrective actions.

        At most three rounds per call. All old attempts stay in the durable
        ledger. Previously successful candidates are retested before promotion.
        """
        if type(corrections) is not dict:
            raise ValueError("CORRECTIONS_REQUIRED")
        with self._transaction():
            b=self.db.execute("SELECT * FROM batches WHERE id=?",(bid,)).fetchone()
            if not b or b["state"]!="HOLD":
                raise ValueError("ONLY_UNRESOLVED_BATCH_CAN_RETRY")
            rows=list(self.db.execute("SELECT * FROM cases WHERE batch_id=?",(bid,)))
            held={r["event_id"] for r in rows if r["state"]=="HOLD"}
            if not held or set(corrections)!=held or any(
                    r["state"] not in ("HOLD","CANDIDATE") for r in rows):
                raise ValueError("UNRESOLVED_CASES_MUST_BE_CORRECTED")
            for eid in sorted(held):
                fix=corrections[eid]
                if type(fix) is not dict or set(fix)!={"solution","solution_ref"}:
                    raise ValueError("CORRECTION_FORMAT")
                solution=text_value(fix["solution"])
                ref=text_value(fix["solution_ref"])
                old=self._row(eid)
                if solution==old["solution"] and ref==old["solution_ref"]:
                    raise ValueError("NO_CORRECTIVE_DIFFERENCE")
                diag=self.db.execute(
                    "SELECT * FROM diagnostics WHERE event_id=? ORDER BY id DESC LIMIT 1",
                    (eid,)).fetchone()
                if diag is None or diag["attempts_at_diagnosis"]!=old["attempts"]:
                    raise ValueError("FRESH_FAILURE_DIAGNOSIS_REQUIRED")
                self.db.execute(
                    "UPDATE cases SET solution=?, solution_ref=? WHERE event_id=?",
                    (solution,ref,eid))
            for r in rows:
                # Prior candidate receipt remains in attempts ledger; no stale
                # PASS can be reused in a new cycle without independent testing.
                self.db.execute(
                    "UPDATE cases SET test_sha=NULL WHERE event_id=?",(r["event_id"],))
                self._state(r["event_id"],("HOLD","CANDIDATE"),"BATCHED",
                            "RETRY_BATCH","Reopened with preserved history and fresh corrective change")
            self.db.execute("UPDATE batches SET state='TESTING' WHERE id=?",(bid,))
        return {"batchId":bid,"state":"TESTING","preservedAttempts":True,
                "retestAllCases":True,"officialPassIssued":False}

    def archive_authorized(self,bid,*,commit_sha,ci_url,owner_verifier,source_verifier):
        """Record externally verified owner-controlled update; never execute it."""
        if not isinstance(commit_sha,str) or not COMMIT.fullmatch(commit_sha):
            raise ValueError("GIT_COMMIT_SHA_REQUIRED")
        text_value(ci_url)
        if not callable(owner_verifier) or not callable(source_verifier):
            raise ValueError("AUTHORITY_VERIFIERS_REQUIRED")
        b=self.db.execute("SELECT * FROM batches WHERE id=?",(bid,)).fetchone()
        if not b or b["state"]!="CANDIDATE": raise ValueError("BATCH_NOT_ACCEPTED_FOR_ARCHIVE")
        context={"batchId":bid,"goalId":b["goal"],"sourceSha256":b["source_sha"],
                 "candidateCommitSha256":commit_sha,"ciUrl":ci_url}
        if owner_verifier(context) is not True or source_verifier(context) is not True:
            raise ValueError("OWNER_OR_SOURCE_VERIFICATION_HOLD")
        with self._transaction():
            rows=list(self.db.execute("SELECT * FROM cases WHERE batch_id=?",(bid,)))
            if any(r["state"]!="CANDIDATE" or not r["test_sha"] for r in rows):
                raise ValueError("MISSING_CASE_EVIDENCE")
            for r in rows:
                self.db.execute("UPDATE cases SET update_sha=? WHERE event_id=?",(commit_sha,r["event_id"]))
                self._state(r["event_id"],("CANDIDATE",),"ARCHIVED",
                            "OWNER_VERIFIED_ARCHIVE","External authority and source verifier attested")
            self.db.execute("UPDATE batches SET state='ARCHIVED' WHERE id=?",(bid,))
        return {"state":"ARCHIVED_INACTIVE_QUEUE","archived":len(rows),
                "proofRetained":True,"officialPassIssued":False}
    def summary(self):
        items={k:0 for k in STATE_ORDER}
        items.update({r["state"]:r["n"] for r in self.db.execute(
            "SELECT state,COUNT(*) n FROM cases GROUP BY state")})
        return {"categories":len(DOMAINS)*len(KINDS),"domains":len(DOMAINS),
                "kinds":len(KINDS),"states":items,
                "active":sum(items[k] for k in ACTIVE),
                "archived":items["ARCHIVED"],
                "journalRecords":self.db.execute("SELECT count(*) FROM journal").fetchone()[0],
                "failureDiagnoses":self.db.execute("SELECT count(*) FROM diagnostics").fetchone()[0],
                "attemptRecords":self.db.execute("SELECT count(*) FROM attempts").fetchone()[0],
                "officialVerifiedFinish":"NOT_ISSUED"}
