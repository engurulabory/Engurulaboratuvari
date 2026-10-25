"""Pure presentation boundary for EXISTING Progress Core results.

The caller obtains registry() (including Work Contract discovery), summarize()
and structural_verify() from the same verified Core. No filesystem, execution,
discovery, progress qualification or acceptance authority is implemented here.
"""
from datetime import datetime
import hashlib
import json
import re

class Hold(ValueError):
    pass

def require(ok, reason):
    if not ok: raise Hold(reason)

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def stamp(value):
    require(isinstance(value,str),'HOLD_TIME')
    try: result=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError as exc: raise Hold('HOLD_TIME') from exc
    require(result.utcoffset() is not None,'HOLD_TIMEZONE')
    return result

def build(registry, facts, *, revision_before, revision_after, pins_before,
          pins_after, source_read_at, adapter_built_at):
    """Return one complete model or raise HOLD. Failed projects remain visible.

    Bracket identity and caller provenance are validated, not authenticated here.
    This is not an atomic multi-file capture or native UI publication proof.
    """
    require(isinstance(revision_before,str) and re.fullmatch('[a-f0-9]{40}',revision_before)
            and revision_before==revision_after,'HOLD_REVISION_DRIFT')
    require(isinstance(pins_before,dict) and pins_before and pins_before==pins_after,
            'HOLD_SOURCE_DRIFT')
    require(all(isinstance(k,str) and isinstance(v,str) and re.fullmatch('[a-f0-9]{64}',v)
                for k,v in pins_before.items()),'HOLD_SOURCE_MANIFEST')
    require(stamp(source_read_at)<=stamp(adapter_built_at),'HOLD_TIME_ORDER')
    require(isinstance(registry,dict) and registry.get('schema')=='enguru.progress-core.project-registry/v1',
            'HOLD_CORE_REGISTRY')
    entries=registry.get('projects')
    require(isinstance(entries,dict) and 0<len(entries)<=1000 and isinstance(facts,dict),
            'HOLD_PROJECT_SET')
    require(not (set(facts)-set(entries)),'HOLD_EXTRA_PROJECT_FACTS')
    rows=[];seen=set()
    checks=('worklist','state','itemSetAgreement','singleActivePackage','singleActiveItem',
            'deterministicProjection','evidenceQualification','progressIntegrity')
    for key,entry in sorted(entries.items()):
        require(isinstance(key,str) and re.fullmatch('[a-z0-9][a-z0-9-]{0,127}',key)
                and isinstance(entry,dict),'HOLD_PROJECT_KEY')
        pid=entry.get('projectId')
        require(isinstance(pid,str) and re.fullmatch('[A-Za-z0-9_.-]{1,128}',pid)
                and pid not in seen,'HOLD_PROJECT_ID')
        seen.add(pid)
        row={'key':key,'projectId':pid,'status':'HOLD','reason':'CORE_FACTS_UNAVAILABLE',
             'done':None,'total':None,'percent':None,'activeItem':None,
             'activePackage':None,'nextAction':None,'finish':'HOLD',
             'officialAcceptance':'HOLD','closed':False}
        pair=facts.get(key)
        if pair is not None:
            require(isinstance(pair,dict),'HOLD_PROJECT_FACTS')
            summary=pair.get('summary',{});verify=pair.get('verify',{})
            require(isinstance(summary,dict) and isinstance(verify,dict),'HOLD_PROJECT_FACTS')
            require(summary.get('project')==verify.get('project')==key and
                    summary.get('projectId')==pid,'HOLD_CORE_PROJECT_DRIFT')
            for field,digest_field in (('state','stateDigest'),('worklist','worklistDigest')):
                require(isinstance(entry.get(field),str) and entry[field] in pins_before
                        and summary.get(digest_field)==pins_before[entry[field]],'HOLD_PROJECT_SOURCE_BINDING')
            if all(verify.get(c)=='PASS' for c in checks) and verify.get('stateDrift')=='NONE':
                done,total=verify.get('countedPass'),summary.get('total')
                require(type(done) is int and type(total) is int and 0<=done<=total
                        and total>0,'HOLD_COUNTER_TYPE_OR_RANGE')
                declared=summary.get('declaredPass')
                require(type(declared) is int and type(verify.get('declaredPass')) is int
                        and declared==verify.get('declaredPass')==done
                        and type(verify.get('unverifiedPass')) is int and verify['unverifiedPass']==0
                        and type(verify.get('evidencedPass')) is int and verify['evidencedPass']==done,
                        'HOLD_COUNTER_AGREEMENT')
                for name in ('activeItem','activePackage','nextAction'):
                    require(isinstance(summary.get(name),str) and bool(summary[name]),'HOLD_CORE_FOCUS')
                require(summary.get('verifiedFinish') in ('HOLD','VERIFIED','LOCKED','PENDING','INTERNAL_P01_ONLY')
                        and isinstance(verify.get('finishState'),str),'HOLD_FINISH_SCHEMA')
                require(not(done<total and verify['finishState'] in
                            ('VERIFIED','LOCKED','VERIFIED_FINISH','VERIFIED_LOCKED')),'HOLD_EARLY_FINISH')
                row.update(status='PASS_CORE_READ_ONLY',reason='QUALIFIED_CORE_FACTS',done=done,
                    total=total,percent=round(done*100/total,2),activeItem=summary['activeItem'],
                    activePackage=summary['activePackage'],nextAction=summary['nextAction'],
                    finish=verify['finishState'])
            else:row['reason']='CORE_VERIFICATION_HOLD'
        rows.append(row)
    # Content digest excludes wall-clock metadata, preserving same-revision replay.
    content={'sourceRevision':revision_before,'sourcePins':dict(sorted(pins_before.items())),
             'projects':rows,'canonicalWrite':'NONE','productionGrant':'HOLD',
             'verifiedFinish':'HOLD','technicalPassIsOfficial':False}
    return {**content,'schema':'enguru.pilive.core-presentation/v1',
        'projectionDigest':hashlib.sha256(canonical(content)).hexdigest(),
        'sourceReadAt':source_read_at,'adapterBuiltAt':adapter_built_at,
        'uiRenderedAt':None,'uiPublication':'NOT_EXECUTED',
        'atomicity':'CALLER_PIN_BRACKET_ONLY; MULTI_FILE_CAPTURE_NOT_ATOMIC'}

def freshness(snapshot, *, now, stale_after_seconds):
    require(type(stale_after_seconds) is int and stale_after_seconds>0,'HOLD_STALE_THRESHOLD')
    age=(stamp(now)-stamp(snapshot.get('sourceReadAt'))).total_seconds()
    require(age>=0,'HOLD_SOURCE_FROM_FUTURE')
    return {'state':'STALE' if age>stale_after_seconds else 'WITHIN_CALLER_AGE_LIMIT',
            'sourceAgeSeconds':age,'cacheAcceptance':'UNCHANGED_HOLD'}
