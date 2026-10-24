"""ENGURU MK V5 bounded, symmetric, deterministic peer diagnosis and learning.

This is an advisory layer, NOT a model that autonomously invents root causes.
Knowledge updates require a caller-provided, independently authenticated verifier.
"""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3
from tools import enguru_mk_bridge_v1 as bridge

SCHEMA='enguru.mk.peer-diagnosis/v5'
OUTCOME_SCHEMA='enguru.mk.peer-outcome/v5'
ACTIONS={'INSPECT_LOCAL_LEDGER','INSPECT_SOURCE_PIN','INSPECT_RUNTIME','INSPECT_PACKAGE','INSPECT_TIMEOUT','INSPECT_TEST_CONTRACT'}
LEVELS={'OBSERVED','HYPOTHESIS'}
HEX=re.compile(r'[a-f0-9]{64}\Z')
# All code-to-response suggestions are pre-approved, sanitized, and reversible.
# First candidate is the baseline; updates require verified historical outcomes.
CATALOG={
 'PILOT_HELLO':('SUCCESS','OBSERVED','Receipt is present','ACK_GAP',('ACK_RECONCILE','LEDGER_AUDIT'),'INSPECT_LOCAL_LEDGER'),
 'GITHUB_RECEIVED':('SUCCESS','OBSERVED','Remote receipt is present','RETURN_ACK_GAP',('LEDGER_AUDIT','ACK_RECONCILE'),'INSPECT_LOCAL_LEDGER'),
 'PILOT_RECOVERY':('WARNING','HYPOTHESIS','Transport recovery is reported','REPLAY_OR_CURSOR',('CURSOR_AUDIT','ACK_RECONCILE'),'INSPECT_LOCAL_LEDGER'),
 'RUNTIME_DRIFT':('MISMATCH','HYPOTHESIS','Runtime difference is reported','RUNTIME_PIN',('RUNTIME_AUDIT','TEST_COMPATIBILITY'),'INSPECT_RUNTIME'),
 'PACKAGE_ABSENT':('MISSING','HYPOTHESIS','Expected package is absent','PACKAGE_PIN',('PACKAGE_SHA_AUDIT','SOURCE_AUDIT'),'INSPECT_PACKAGE'),
 'INTERACTIVE_TIMEOUT':('ERROR','HYPOTHESIS','Interactive operation timed out','OWNER_BOUNDARY',('TIMEOUT_REVIEW','AUDIT_RETRY'),'INSPECT_TIMEOUT'),
 'NODE_TAP_MISMATCH':('INCORRECT','HYPOTHESIS','Node format mismatch is reported','CONTRACT_DRIFT',('FORMAT_REGRESSION','SOURCE_AUDIT'),'INSPECT_TEST_CONTRACT'),
}
EVIDENCE_ONLY={'event_sha256','source_commit','trace_code'}
CHOICE_COST={'ACK_RECONCILE':1,'LEDGER_AUDIT':1,'CURSOR_AUDIT':2,'RUNTIME_AUDIT':2,'TEST_COMPATIBILITY':3,'PACKAGE_SHA_AUDIT':1,'SOURCE_AUDIT':2,'TIMEOUT_REVIEW':2,'AUDIT_RETRY':3,'FORMAT_REGRESSION':2}
EXPECTED_EVENT={'schema','eventId','taskId','blockId','producer','sequence','type','code','sourceCommit','evidenceSha256','observedAt','visibility'}
class Hold(Exception):pass

def canon(obj):return (json.dumps(obj,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def digest(obj):return hashlib.sha256(canon(obj)).hexdigest()
def parse(raw):
    if not isinstance(raw,(str,bytes)) or len(raw)>8192:raise Hold('HOLD_DIAG_SIZE')
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise Hold('HOLD_DUPLICATE_KEY')
            d[k]=v
        return d
    try:obj=json.loads(raw,object_pairs_hook=unique)
    except (ValueError,TypeError,UnicodeError) as e:raise Hold('HOLD_DIAG_JSON') from e
    if not isinstance(obj,dict):raise Hold('HOLD_DIAG_OBJECT')
    return obj

def validate_event(event):
    try:bridge.validate_event(event)
    except bridge.Hold as e:raise Hold('HOLD_SOURCE_'+str(e)) from e
    if set(event)!=EXPECTED_EVENT or event['code'] not in CATALOG:raise Hold('HOLD_CASE_CODE')
    return digest(event)

def assess(event,history=None):
    report=_compute_case(event,history)
    if len(canon(report))>8192:raise Hold('HOLD_REPORT_SIZE')
    return report

def validate_report(report,event,history=None):
    if not isinstance(report,dict) or report!=_compute_case(event,history):
        raise Hold('HOLD_REPORT_TAMPER')
    if len(canon(report))>8192:raise Hold('HOLD_REPORT_SIZE')
    return digest(report)

def _compute_case(event,history=None):
    # Implementation identical to generator, omitting terminal validation.
    event_sha=validate_event(event)
    code=event['code'];category,level,obs,hypothesis,choices,step=CATALOG[code]
    stats=history or {}
    if not isinstance(stats,dict) or set(stats)-set(CHOICE_COST):raise Hold('HOLD_LEARNING_STATS')
    alts=[]
    for choice in choices:
        n=stats.get(choice,(0,0))
        if not isinstance(n,(tuple,list)) or len(n)!=2 or any(type(x)!=int or x<0 or x>100000 for x in n) or n[1]>n[0]:raise Hold('HOLD_LEARNING_COUNTS')
        total,success=n
        confidence=0 if total<3 else ((success+1)*100)//(total+2)-50
        alts.append({'solutionCode':choice,'score':80-CHOICE_COST[choice]*4+confidence,'verifiedCases':total,
                     'evidenceNeeded':'INDEPENDENT_OUTCOME_PROOF','action':'REVIEW_OR_READONLY','reversible':True})
    alts.sort(key=lambda a:(-a['score'],a['solutionCode']))
    return {'schema':SCHEMA,'reportId':'DIA-'+event['eventId'],'eventId':event['eventId'],'eventSha256':event_sha,
      'producer':event['producer'],'recipient':'GITHUB_MK' if event['producer']=='MAC_OSI_MK' else 'MAC_OSI_MK',
      'taskId':event['taskId'],'blockId':event['blockId'],'visibility':'PUBLIC_SANITIZED',
      'category':category,'findingCode':'REPORTED_'+code,'observationCode':code,
      'needs':['EVIDENCE_CORRELATION','POST_ACTION_VERIFICATION'] if level=='HYPOTHESIS' else ['TRANSPORT_RECONCILIATION'],
      'requirements':['SOURCE_SHA_ANCHOR','INDEPENDENT_VERIFIER','OWNER_REVIEW_FOR_CHANGES'],
      'hypothesisCode':hypothesis,'claimLevel':level,'rootCause':'UNCONFIRMED',
      'alternatives':alts,'suggestedSolutionCode':alts[0]['solutionCode'],'alignedNextStep':step,
      'nextStepPolicy':'READONLY_OR_OWNER_REVIEW','authority':'SUGGESTION_ONLY','productWrites':0,'officialAcceptance':'HOLD'}


def learning_db(db):
    db.execute('''CREATE TABLE IF NOT EXISTS mk_v5_assessments(
      report_id TEXT PRIMARY KEY,event_sha TEXT NOT NULL,report_sha TEXT NOT NULL,
      report BLOB NOT NULL,next_step TEXT NOT NULL,state TEXT NOT NULL)''')
    db.execute('''CREATE TABLE IF NOT EXISTS mk_v5_candidates(
      case_id TEXT PRIMARY KEY,solution_code TEXT NOT NULL,outcome TEXT NOT NULL,
      proof_sha TEXT NOT NULL,assurance TEXT NOT NULL DEFAULT 'PROVISIONAL')''')
    db.execute('''CREATE TABLE IF NOT EXISTS mk_v5_verified(
      case_id TEXT PRIMARY KEY,solution_code TEXT NOT NULL,outcome TEXT NOT NULL,
      proof_sha TEXT NOT NULL,authenticated_by TEXT NOT NULL)''')

def accept_report(db,report,event):
    """Idempotent next-step alignment; only existing local ledger is inspected automatically."""
    validate_report(report,event)
    if report['recipient']!='MAC_OSI_MK':raise Hold('HOLD_WRONG_RECIPIENT')
    with db:
        learning_db(db)
        existing=db.execute('SELECT report_sha FROM mk_v5_assessments WHERE report_id=?',(report['reportId'],)).fetchone()
        h=digest(report)
        if existing:
            if existing[0]!=h:raise Hold('HOLD_REPORT_CONFLICT')
            return 'IDEMPOTENT'
        step=report['alignedNextStep']
        if step not in ACTIONS:raise Hold('HOLD_UNSAFE_NEXT_STEP')
        if step=='INSPECT_LOCAL_LEDGER':
            db.execute('SELECT count(*) FROM incoming').fetchone()
            state='READONLY_APPLIED'
        else:state='REVIEW_REQUIRED'
        db.execute('INSERT INTO mk_v5_assessments VALUES(?,?,?,?,?,?)',
            (report['reportId'],report['eventSha256'],h,canon(report),step,state))
        return state

def candidate(db,case_id,solution_code,outcome,proof_sha):
    """Unverified outcomes remain provisional; excluded from learning/choice statistics."""
    if not re.fullmatch(r'CASE-[A-Z0-9]{8,32}',case_id) or solution_code not in CHOICE_COST or outcome not in ('PASS','FAIL') or not isinstance(proof_sha,str) or not HEX.fullmatch(proof_sha):raise Hold('HOLD_OUTCOME_FIELDS')
    with db:
        learning_db(db)
        existing=db.execute('SELECT solution_code,outcome,proof_sha FROM mk_v5_candidates WHERE case_id=?',(case_id,)).fetchone()
        incoming=(solution_code,outcome,proof_sha)
        if existing:
            if existing!=incoming:raise Hold('HOLD_OUTCOME_CONFLICT')
            return 'IDEMPOTENT'
        db.execute('INSERT INTO mk_v5_candidates(case_id,solution_code,outcome,proof_sha) VALUES(?,?,?,?)',(case_id,*incoming))
        return 'PROVISIONAL'

def promote(db,case_id, verifier):
    """Supply *actual* authenticated verification callback; no default accepting verifier.

    callback(case_id, candidate tuple)->(authenticated_actor, trusted_evidence_sha)
    MUST check trusted GitHub CI/owner record cryptographically or via authenticated API.
    """
    if verifier is None or not callable(verifier):raise Hold('HOLD_INDEPENDENT_VERIFIER_REQUIRED')
    r=db.execute('SELECT solution_code,outcome,proof_sha FROM mk_v5_candidates WHERE case_id=?',(case_id,)).fetchone()
    if not r:raise Hold('HOLD_UNKNOWN_CASE')
    actor,trust_sha=verifier(case_id,r)
    if actor not in ('CANONICAL_OWNER','INDEPENDENT_CI') or not isinstance(trust_sha,str) or not HEX.fullmatch(trust_sha) or trust_sha==r[2]:raise Hold('HOLD_UNVERIFIED_PROOF')
    with db:
        old=db.execute('SELECT solution_code,outcome,proof_sha,authenticated_by FROM mk_v5_verified WHERE case_id=?',(case_id,)).fetchone()
        if old:
            if old!=(r[0],r[1],trust_sha,actor):raise Hold('HOLD_VERIFIER_CONFLICT')
            return 'IDEMPOTENT'
        db.execute('INSERT INTO mk_v5_verified VALUES(?,?,?,?,?)',(case_id,r[0],r[1],trust_sha,actor))
    return 'VERIFIED_EVIDENCE_ONLY'

def trusted_stats(db):
    learning_db(db)
    return {r[0]:(r[1],r[2]) for r in db.execute("SELECT solution_code,count(*),sum(outcome='PASS') FROM mk_v5_verified GROUP BY solution_code")}

def scorecard(db):
    learning_db(db)
    return {'assessments':db.execute('SELECT count(*) FROM mk_v5_assessments').fetchone()[0],
            'candidates':db.execute('SELECT count(*) FROM mk_v5_candidates').fetchone()[0],
            'verified':db.execute('SELECT count(*) FROM mk_v5_verified').fetchone()[0],
            'reviewRequired':db.execute("SELECT count(*) FROM mk_v5_assessments WHERE state='REVIEW_REQUIRED'").fetchone()[0],
            'officialAcceptance':'HOLD'}
