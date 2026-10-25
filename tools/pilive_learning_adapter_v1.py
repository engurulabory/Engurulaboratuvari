"""PiLive scoped learning through the existing MK parser and review record.

This module validates source evidence and returns review candidates in memory.
It owns no progress counter, scheduler, canonical writer or acceptance authority.
Raw native files and local paths remain local. Public facts use a fixed vocabulary.
"""
from __future__ import annotations
from datetime import datetime
import hashlib
import json
import re

try:
    from tools import enguru_muhendislik_kasi as muscle
except ModuleNotFoundError:
    import enguru_muhendislik_kasi as muscle

TASK_ID = muscle.PILIVE_TASK_ID
MAX_RECEIPT_BYTES = 20*1024*1024
SCHEMA_V2 = 'enguru.pilive.source-observation/v2'
SCHEMA_V3 = 'enguru.pilive.source-link-observation/v3'
HASH = re.compile(r'[0-9a-f]{64}\Z')
FACTS = {
 'SOURCE_SCOPE': (
  'Tracked filename scope and bounded native source scope are reported separately.',
  'The tracked inventory had zero Swift candidates; the bounded archive capture contained Swift sources.',
  'Retain examined-file count, search roots, depth and limit evidence for every absence claim.'),
 'SOURCE_BINARY_LINEAGE': (
  'An installed binary digest and historical source pins have distinct proof scope.',
  'Historical Swift source pins matched captured bytes; Python projection pins and exact build lineage remain open.',
  'Require exact source, build recipe, toolchain, signing transformation and resulting binary identity.'),
 'COUNT_INTEGRITY': (
  'Display counters consume canonical qualified integer values.',
  'An archived Swift bridge converts NSNumber using intValue and permits a percentage tolerance.',
  'Accept exact non-boolean integers and derive the displayed percentage from the verified numerator and denominator.'),
}

def canonical(value):
    return muscle.canonical(value)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def require(value, reason):
    if not value: raise muscle.IntakeHold(reason)

def strict_receipt(raw):
    require(isinstance(raw,bytes) and len(raw)<=MAX_RECEIPT_BYTES,'HOLD_RECEIPT_SIZE')
    def constant(_): raise muscle.IntakeHold('HOLD_NONFINITE_JSON')
    try:
        value=json.loads(raw,object_pairs_hook=muscle.strict_object,parse_constant=constant)
    except (ValueError,UnicodeError) as exc:
        raise muscle.IntakeHold('HOLD_RECEIPT_JSON') from exc
    require(isinstance(value,dict),'HOLD_RECEIPT_TYPE')
    return value

def verify_chain(v2_raw, v3_raw, *, expected_v2_sha, expected_v3_sha):
    for raw,pin in [(v2_raw,expected_v2_sha),(v3_raw,expected_v3_sha)]:
        require(isinstance(pin,str) and HASH.fullmatch(pin) is not None,'HOLD_RECEIPT_PIN_FORMAT')
        require(digest(raw)==pin,'HOLD_RECEIPT_PIN_MISMATCH')
    v2=strict_receipt(v2_raw);v3=strict_receipt(v3_raw)
    require(v2.get('schema')==SCHEMA_V2 and v3.get('schema')==SCHEMA_V3,'HOLD_RECEIPT_SCHEMA')
    require(v3.get('parentReceiptSha256')==digest(v2_raw),'HOLD_RECEIPT_PARENT')
    for receipt in [v2,v3]:
        require(receipt.get('platform')=='Darwin','HOLD_NATIVE_PLATFORM')
        require(receipt.get('stableBracket') is True and receipt.get('before')==receipt.get('after'),'HOLD_SOURCE_DRIFT')
        require(receipt.get('errors')==[],'HOLD_CAPTURE_ERRORS')
        for field in ['appLaunches','canonicalWrites','keychainReads','networkRequests']:
            require(type(receipt.get(field)) is int and receipt[field]==0,'HOLD_CAPTURE_SCOPE')
    matched=0
    for group in ['sources','externalSourceCandidates']:
        records=v3.get(group)
        require(isinstance(records,dict),'HOLD_CONTENT_GROUP')
        for record in records.values():
            require(isinstance(record,dict) and isinstance(record.get('contentUtf8'),str),'HOLD_CONTENT_TYPE')
            raw=record['contentUtf8'].encode('utf-8')
            require(type(record.get('bytes')) is int and len(raw)==record['bytes'],'HOLD_CONTENT_SIZE')
            require(digest(raw)==record.get('sha256'),'HOLD_CONTENT_SHA')
            matched+=1
    # Bind every V2 named file to exactly one matching V3 canonical file.
    prior=v2.get('sources');require(isinstance(prior,dict) and len(prior)==7,'HOLD_SEVEN_SOURCES')
    for relative,record in prior.items():
        require(isinstance(relative,str) and relative.startswith(('governance/','tools/')) and '..' not in relative.split('/'),'HOLD_SOURCE_PATH')
        require(isinstance(record,dict) and isinstance(record.get('contentUtf8'),str),'HOLD_PARENT_CONTENT')
        require(digest(record['contentUtf8'].encode())==record.get('sha256'),'HOLD_PARENT_CONTENT_SHA')
        candidates=[entry for path,entry in v3['sources'].items() if path.endswith('/'+relative)]
        require(len(candidates)==1 and candidates[0]['sha256']==record['sha256'],'HOLD_CANONICAL_CHAIN')
    return {'state':'PASS_CAPTURE_INTEGRITY_ONLY','contentRecordsVerified':matched,
      'parentSha256':digest(v2_raw),'sourceSha256':digest(v3_raw),
      'nativeExecution':'NOT_EXECUTED','officialAcceptance':'UNCHANGED_HOLD'}

def review_candidate(record, *, fact_id, source_sha256, observed_at, correlation_id):
    require(fact_id in FACTS,'HOLD_FACT_VOCABULARY')
    require(isinstance(source_sha256,str) and HASH.fullmatch(source_sha256) is not None,'HOLD_FACT_SOURCE_SHA')
    expected,observed,fix=FACTS[fact_id]
    # No native path or raw source text enters an event or its replay marker.
    event={'schema':muscle.SCHEMA,'eventId':'MK-EVT-PILIVE-'+fact_id+'-'+source_sha256[:12].upper(),
      'taskId':TASK_ID,'observedAt':observed_at,'type':'NEW_REQUIREMENT','evidenceLevel':'A',
      'sourceUri':'urn:enguru:pilive:reviewed-source:'+source_sha256,'sourceSha256':source_sha256,
      'expected':expected,'observed':observed,'causeStatus':'UNKNOWN','fixProposal':fix,
      'testState':'NOT_EXECUTED','correlationId':correlation_id}
    return muscle.process(record,canonical(event),expected_task_id=TASK_ID)

def exact_counts(done,total):
    """Display boundary validation only; Progress Core remains the counter authority."""
    require(type(done) is int and type(total) is int and 0<=done<=total and total>0,'HOLD_DISPLAY_COUNTS')
    return {'done':done,'total':total,'percentNumerator':done*100,'percentDenominator':total}

def schedule_evidence(runs, *, workflow_id, current_sha):
    require(isinstance(runs,list) and type(workflow_id) is int and isinstance(current_sha,str),'HOLD_SCHEDULE_INPUT')
    rows=[r for r in runs if isinstance(r,dict) and r.get('workflow_id')==workflow_id and r.get('event')=='schedule']
    require(all(type(r.get('id')) is int and r['id']>0 for r in rows),'HOLD_RUN_ID')
    require(len({r.get('id') for r in rows})==len(rows),'HOLD_DUPLICATE_RUN')
    try:rows.sort(key=lambda r:datetime.fromisoformat(r['created_at'].replace('Z','+00:00')),reverse=True)
    except (KeyError,ValueError,TypeError) as exc:raise muscle.IntakeHold('HOLD_SCHEDULE_TIME') from exc
    latest=rows[:4];times=[]
    for row in latest:
        time=datetime.fromisoformat(row['created_at'].replace('Z','+00:00'))
        require(time.tzinfo is not None,'HOLD_SCHEDULE_TIME');times.append(time)
    gaps=[(a-b).total_seconds() for a,b in zip(times,times[1:])]
    good=len(latest)==4 and all(r.get('status')=='completed' and r.get('conclusion')=='success' and r.get('head_sha')==current_sha for r in latest) and all(0<g<=420 for g in gaps)
    return {'state':'PASS_BOUNDED_FOUR_RUN_WINDOW' if good else 'HOLD_SCHEDULE_CONTINUITY',
      'workflowId':workflow_id,'runIds':[r['id'] for r in latest],'gapsSeconds':gaps,
      'thresholdSeconds':420,'officialAcceptance':'UNCHANGED_HOLD'}
