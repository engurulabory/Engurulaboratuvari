#!/usr/bin/env python3
"""ENGURU MK: one read-only OSi preflight, evidence learning candidate, P01-P06 metrics.

Advisory only. No app install, GitHub mutation, signing, audit write or owner claim.
Source SHA is byte integrity, not independent authority. Every output is HOLD for official acceptance.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import zipfile

SCOPED_TASK = 'ENGURU_MANAGEMENT_V69_PR_203'
PREFLIGHT_SCHEMA='enguru.mk.osi-preflight/v1'
LEARN_SCHEMA='enguru.mk.osi-learn/v1'
METRIC_SCHEMA='enguru.mk.osi-metrics/v1'
FIELD_SCHEMA='enguru.mk.osi-field-receipt/v1'
HEX64=re.compile(r'[a-f0-9]{64}\Z')
TASK=re.compile(r'[A-Z][A-Z0-9_-]{7,90}\Z')
BLOCK=re.compile(r'OSIBLOCK-[A-Z0-9_-]{6,64}\Z')
SOURCE_MAX=12_000_000
SECRET=re.compile(r"(?i)(?:password|private[_-]?key|access[_-]?token|secret[_-]?key|passphrase)['\"]?\s*[:=]\s*['\"]?\S+|-----BEGIN (?:OPENSSH |RSA |EC |ENCRYPTED )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}")
CLASSES={
 'PACKAGE_ABSENT':'Check package delivery, exact path and SHA-256 before execution',
 'RUNTIME_DRIFT':'Pin Node/Python versions and explicitly use Node TAP reporter',
 'UI_SURFACE_MISMATCH':'Bind actual visible Product Operator drawer and check served HTML identity',
 'INTERACTIVE_TIMEOUT':'Use a bounded owner-interaction timeout separate from machine tests',
 'LEDGER_PARTIAL':'Read existing audit ledger and reconcile partial transaction before append',
 'OTHER':'Independent source diagnosis and negative regression test required',
}

class Hold(ValueError): pass

def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()
def canonical(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
def strict_pairs(items):
    d={}
    for k,v in items:
        if k in d:raise Hold('HOLD_DUPLICATE_JSON_KEY')
        d[k]=v
    return d

def read(path,limit=SOURCE_MAX):
    p=Path(path).expanduser()
    if p.is_symlink() or not p.is_file():raise Hold('HOLD_SOURCE_FILE_OR_SYMLINK')
    size=p.stat().st_size
    if size>limit or size<1:raise Hold('HOLD_SOURCE_SIZE')
    try:return p.read_bytes()
    except OSError as e:raise Hold('HOLD_SOURCE_READ') from e

def parse(raw):
    try:
        v=json.loads(raw,object_pairs_hook=strict_pairs,parse_constant=lambda x:(_ for _ in ()).throw(Hold('HOLD_JSON_CONSTANT')))
        if not isinstance(v,dict):raise Hold('HOLD_JSON_OBJECT')
        return v
    except (ValueError,UnicodeError) as e:
        if isinstance(e,Hold):raise
        raise Hold('HOLD_JSON') from e

def secret_free(v):
    if SECRET.search(canonical(v).decode('utf-8')):raise Hold('HOLD_SENSITIVE_CONTENT')

def valid_task(v):
    if not isinstance(v,str) or not TASK.fullmatch(v):raise Hold('HOLD_TASK_SCOPE')
    return v

def digest_file(path,pin):
    if not isinstance(pin,str) or not HEX64.fullmatch(pin):raise Hold('HOLD_SHA_FORMAT')
    blob=read(path)
    if sha(blob)!=pin:raise Hold('HOLD_SHA_MISMATCH')
    return blob

def runtime_version(program):
    try:
        cp=subprocess.run([program,'--version'] if program!='node' else ['node','--version'],capture_output=True,text=True,timeout=5)
        if cp.returncode:raise Hold('HOLD_RUNTIME_UNAVAILABLE_'+program.upper())
        v=(cp.stdout+cp.stderr).strip()
        m=re.search(r'v?(\d+)\.(\d+)\.(\d+)',v)
        if not m:raise Hold('HOLD_RUNTIME_VERSION_'+program.upper())
        return tuple(map(int,m.groups()))
    except (OSError,subprocess.TimeoutExpired) as e:raise Hold('HOLD_RUNTIME_UNAVAILABLE_'+program.upper()) from e

def preflight(doc,version_provider=runtime_version):
    if doc.get('schema')!=PREFLIGHT_SCHEMA:raise Hold('HOLD_PREFLIGHT_SCHEMA')
    valid_task(doc.get('taskId'))
    sources=doc.get('sources')
    if not isinstance(sources,list) or not 1<=len(sources)<=12:raise Hold('HOLD_SOURCES_COUNT')
    if len({x.get('role') for x in sources if isinstance(x,dict)})!=len(sources):raise Hold('HOLD_DUPLICATE_ROLE')
    constraints=doc.get('runtime',{})
    if not isinstance(constraints,dict) or set(constraints)-{'pythonMinMajor','nodeMinMajor','nodeExpectedMajor','nodeTestReporter'}:raise Hold('HOLD_RUNTIME_SCHEMA')
    for field in ('pythonMinMajor','nodeMinMajor'):
        if type(constraints.get(field)) is not int or not 3<=constraints[field]<=30:raise Hold('HOLD_RUNTIME_MIN_'+field)
    if constraints.get('nodeTestReporter')!='tap':raise Hold('HOLD_NODE_TAP_EXPLICIT')
    pv=version_provider('python3')
    nv=version_provider('node')
    if pv[0]<constraints['pythonMinMajor'] or nv[0]<constraints['nodeMinMajor']:raise Hold('HOLD_RUNTIME_BELOW_MINIMUM')
    if 'nodeExpectedMajor' in constraints and (type(constraints['nodeExpectedMajor']) is not int or nv[0]!=constraints['nodeExpectedMajor']):raise Hold('HOLD_NODE_EXACT_MAJOR_DRIFT')
    interactive=doc.get('interactive',{})
    if not isinstance(interactive,dict) or interactive.get('ownerConsentRequired') is not True or type(interactive.get('timeoutSeconds')) is not int or not 300<=interactive['timeoutSeconds']<=7200:raise Hold('HOLD_OWNER_INTERACTIVE_BOUNDARY')
    results=[]
    for source in sources:
        if not isinstance(source,dict) or set(source)-{'role','path','sha256','requiredMarkers'}:raise Hold('HOLD_SOURCE_SCHEMA')
        role=source.get('role')
        if role not in ('package','runtime','ui','verifier','evidence'):raise Hold('HOLD_SOURCE_ROLE')
        path=source.get('path')
        if not isinstance(path,str) or not path or len(path)>1024 or SECRET.search(path) or re.search(r'(?i)(?:private[_-]?key|reviewer.*key|\.pem$|\.key$|\.p12$|/\.env(?:$|\.))',path):raise Hold('HOLD_SOURCE_PATH')
        raw=digest_file(path,source.get('sha256'))
        markers=source.get('requiredMarkers',[])
        if not isinstance(markers,list) or len(markers)>12 or any(not isinstance(m,str) or not 2<=len(m)<=100 for m in markers):raise Hold('HOLD_MARKERS')
        if role!='ui' and markers:raise Hold('HOLD_MARKER_NON_UI')
        for token in markers:
            if token.encode('utf-8') not in raw:raise Hold('HOLD_VISIBLE_UI_MARKER_MISSING')
        if role=='ui' and not {'poStatusBlock','poTechnicalDetails'}.issubset(set(markers)):
            raise Hold('HOLD_REAL_VISIBLE_DRAWER_UNPINNED')
        results.append({'role':role,'sha256':sha(raw),'markersVerified':len(markers)})
    return {'schema':'enguru.mk.osi-preflight-result/v1','taskId':doc['taskId'],
        'sources':results,'pythonVersion':'.'.join(map(str,pv)), 'nodeVersion':'.'.join(map(str,nv)),
        'nodeTestReporter':'tap','humanTimeoutSeconds':interactive['timeoutSeconds'],
        'state':'PASS_PREFLIGHT_READ_ONLY','actualInstall':'NOT_EXECUTED','officialAcceptance':'HOLD'}

def learn(doc):
    if doc.get('schema')!=LEARN_SCHEMA:raise Hold('HOLD_LEARN_SCHEMA')
    if doc.get('taskId')!=SCOPED_TASK:raise Hold('HOLD_EXISTING_MUSCLE_TASK_SCOPE')
    bid=doc.get('blockId')
    if not isinstance(bid,str) or not BLOCK.fullmatch(bid):raise Hold('HOLD_BLOCK_ID')
    kind=doc.get('failureClass')
    if kind not in CLASSES:raise Hold('HOLD_FAILURE_CLASS')
    if doc.get('causeStatus') not in ('UNKNOWN','HYPOTHESIS','CONFIRMED'):
        raise Hold('HOLD_CAUSE_STATUS')
    # Local byte integrity is not independent root-cause adjudication.
    if doc['causeStatus']=='CONFIRMED':raise Hold('HOLD_INDEPENDENT_CAUSE_AUTHORITY_REQUIRED')
    for k in ('sourcePath','sourceSha256','expected','observed','observedAt'):
        if not isinstance(doc.get(k),str) or not doc[k]:raise Hold('HOLD_MISSING_'+k)
    for k in ('expected','observed'):
        if len(doc[k])>1300:raise Hold('HOLD_TEXT_LIMIT')
    secret_free({'expected':doc['expected'],'observed':doc['observed']})
    try:
        obs=dt.datetime.fromisoformat(doc['observedAt'].replace('Z','+00:00'))
        if not obs.tzinfo:raise ValueError('timezone')
    except ValueError as e:raise Hold('HOLD_TIMESTAMP') from e
    digest_file(doc['sourcePath'],doc['sourceSha256'])
    src=doc.get('sourceUri')
    if not isinstance(src,str) or not src.startswith('https://github.com/engurulabory/Engurulaboratuvari/') or len(src)>400:raise Hold('HOLD_PUBLIC_RELAY_SCOPE')
    raw=canonical({k:v for k,v in doc.items() if k!='sourcePath'})
    uid='MK-EVT-OSI-FIELD-'+sha(raw)[:18].upper()
    event={'schema':'enguru.mk.evidence-event/v1','eventId':uid,'taskId':SCOPED_TASK,
        'observedAt':doc['observedAt'],'type':'ERROR' if kind!='OTHER' else 'NEW_REQUIREMENT',
        'evidenceLevel':'B','sourceUri':src,'sourceSha256':doc['sourceSha256'],
        'expected':doc['expected'],'observed':doc['observed'],'causeStatus':doc['causeStatus'],
        'fixProposal':CLASSES[kind], 'testState':'NOT_EXECUTED','correlationId':bid,
        'suggestedCheck':'Add a negative regression candidate under existing MK suite after owner review'}
    secret_free(event)
    try:
        import enguru_muhendislik_kasi as existing
        existing.parse_event(canonical(event))
    except ImportError as e:raise Hold('HOLD_CANONICAL_LEARNING_MODULE_REQUIRED') from e
    return {'schema':'enguru.mk.osi-learning-candidate/v1','state':'PASS_LOCAL_REVIEW_CANDIDATE',
        'officialAcceptance':'UNCHANGED_HOLD','requiresOwnerRelay':True,'taskId':SCOPED_TASK,
        'failureClass':kind,'byteEvidenceSha256':doc['sourceSha256'], 'event':event,
        'eventSha256':sha(canonical(event))}

def stamp(x):
    if not isinstance(x,str):raise Hold('HOLD_TIME_FORMAT')
    try:
        d=dt.datetime.fromisoformat(x.replace('Z','+00:00'))
        if d.tzinfo is None:raise ValueError()
        return d.timestamp()
    except ValueError as e:raise Hold('HOLD_TIME_FORMAT') from e

def metric_value(obs,k):
    v=obs.get(k)
    if type(v) is not int or v<0 or v>100000:raise Hold('HOLD_METRIC_'+k)
    return v

def metrics(doc):
    if doc.get('schema')!=METRIC_SCHEMA:raise Hold('HOLD_METRIC_SCHEMA')
    valid_task(doc.get('taskId'))
    rows=doc.get('observations')
    if not isinstance(rows,list) or not 2<=len(rows)<=300:raise Hold('HOLD_METRIC_ROWS')
    ids=set(); phases={'baseline':[],'after':[]}; stamps={'baseline':[],'after':[]}
    for r in rows:
        if not isinstance(r,dict) or r.get('phase') not in phases:raise Hold('HOLD_METRIC_PHASE')
        ident=r.get('observationId')
        if not isinstance(ident,str) or not re.fullmatch('[A-Z0-9_-]{8,80}',ident) or ident in ids:raise Hold('HOLD_METRIC_ID')
        ids.add(ident)
        if r.get('taskId')!=doc['taskId']:raise Hold('HOLD_METRIC_TASK_BOUNDARY')
        raw=digest_file(r.get('sourcePath'),r.get('sourceSha256'))
        evidence=parse(raw)
        if evidence.get('schema')!=FIELD_SCHEMA or evidence.get('observationId')!=ident or evidence.get('taskId')!=doc['taskId'] or evidence.get('phase')!=r['phase']:
            raise Hold('HOLD_FIELD_RECORD_BINDING')
        secret_free(evidence)
        stamp(evidence.get('observedAt'))
        for k in ('manualSteps','repeatedDiagnosis','prematureFinish'):
            metric_value(evidence,k)
        dur=evidence.get('repairMinutes')
        if dur is not None and (type(dur) not in (int,float) or not math.isfinite(dur) or dur<0 or dur>100000):raise Hold('HOLD_REPAIR_DURATION')
        g=evidence.get('verifiedGateCount')
        if type(g) is not int or not 0<=g<=6:raise Hold('HOLD_GATE_COUNT')
        run_times=evidence.get('scheduleRunTimes',[])
        if not isinstance(run_times,list) or len(run_times)>100 or any(not isinstance(t,str) for t in run_times):raise Hold('HOLD_SCHEDULE')
        intervals=sorted(stamp(t) for t in run_times)
        if len(intervals)!=len(set(intervals)):raise Hold('HOLD_SCHEDULE_DUPLICATE')
        phases[r['phase']].append(evidence)
        stamps[r['phase']]+=intervals
    if not phases['baseline'] or not phases['after']:raise Hold('HOLD_METRIC_BOTH_PHASES_REQUIRED')
    def median(phase,key):
        xs=[x.get(key) for x in phases[phase] if x.get(key) is not None]
        return round(statistics.median(xs),3) if xs else None
    def total(phase,key):return sum(x[key] for x in phases[phase])
    a,b='baseline','after'
    times=sorted(set(stamps[b])); intervals=[round(times[i]-times[i-1],2) for i in range(1,len(times))]
    p05={'actualScheduleRuns':len(times),'observedIntervalsSeconds':intervals,
        'intervalsWithinFiveMinutes':sum(x<=300 for x in intervals),'fiveMinuteReliable':bool(intervals) and all(x<=300 for x in intervals)}
    return {'schema':'enguru.mk.osi-metrics-result/v1','state':'PASS_PROVISIONAL_METRICS_SOURCE_BYTES',
        'taskId':doc['taskId'],'observedSourceReceipts':len(rows),'baselineCount':len(phases[a]),'afterCount':len(phases[b]),
        'P01_manualStepsMedian':{'baseline':median(a,'manualSteps'),'after':median(b,'manualSteps')},
        'P02_repeatedDiagnosisTotal':{'baseline':total(a,'repeatedDiagnosis'),'after':total(b,'repeatedDiagnosis')},
        'P03_prematureFinishTotal':{'baseline':total(a,'prematureFinish'),'after':total(b,'prematureFinish')},
        'P04_repairMinutesMedian':{'baseline':median(a,'repairMinutes'),'after':median(b,'repairMinutes')},
        'P05_schedule':p05,
        'P06_verifiedGateCountMax':{'baseline':max(x['verifiedGateCount'] for x in phases[a]),'after':max(x['verifiedGateCount'] for x in phases[b])},
        'measurementClaim':'ADVISORY_ONLY_SOURCE_BYTES_VERIFIED','effectivenessClaim':'HOLD_INDEPENDENT_BASELINE_REVIEW_REQUIRED',
        'officialAcceptance':'UNCHANGED_HOLD'}

def write_once(path,obj):
    p=Path(path).expanduser()
    if p.is_symlink() or p.exists():raise Hold('HOLD_OUTPUT_EXISTS')
    p.parent.mkdir(parents=True,exist_ok=True)
    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0)
    fd=os.open(str(p),flags,0o600)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False).encode()+b'\n')
            f.flush();os.fsync(f.fileno())
    except BaseException:
        raise
    return sha(p.read_bytes())

def main(argv=None):
    ap=argparse.ArgumentParser(description='Read-only ENGURU OSi transfer trio: preflight, learn, P01-P06 metrics')
    ap.add_argument('--mode',choices=['preflight','learn','metrics'],required=True)
    ap.add_argument('--input',required=True)
    ap.add_argument('--output',required=True)
    args=ap.parse_args(argv)
    try:
        source=Path(args.input).expanduser();dest=Path(args.output).expanduser()
        if source.resolve()==dest.resolve():raise Hold('HOLD_SOURCE_OUTPUT_COLLISION')
        doc=parse(read(source,500_000))
        if args.mode=='preflight':result=preflight(doc)
        elif args.mode=='learn':result=learn(doc)
        else:result=metrics(doc)
        dig=write_once(dest,result)
        print('STATE='+result['state'])
        print('OUTPUT='+str(dest))
        print('OUTPUT_SHA256='+dig)
        print('OFFICIAL_ACCEPTANCE='+result['officialAcceptance'])
        return 0
    except (Hold,OSError,TypeError,KeyError,OverflowError) as e:
        print('STATE=HOLD_GUVENLI_DUR')
        print('HOLD_REASON='+str(e)[:130])
        return 50

if __name__=='__main__':raise SystemExit(main())
