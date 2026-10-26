"""Independent data/source/image-integrity review of user-driven native UI events.

Image pixels still need independent visual review. This never issues U/P02 PASS.
"""
import base64,json,re,struct,math
from datetime import datetime
from pathlib import Path
from tools import pilive_native_learning_probe_v1 as safe
from tools.pilive_live_reader_v1 import packet as export_packet
from tools.pilive_core_snapshot_adapter_v1 import build_portfolio

TASKS=[('FJ.NOW','ENGURU_PLIVE_P02_USER_SCREEN'),('FJ.PROJECTS','ENGURU_PROGRESS_CORE'),('FJ.EVIDENCE','ENGURU_PROGRESS_CORE')]

def require(ok,code):
    if not ok:raise ValueError(code)

def validate(journey, folder):
    require(journey.get('schema')=='enguru.pilive.field-journey/v1','HOLD_JOURNEY_SCHEMA')
    identity=journey.get('journeyId');require(isinstance(identity,str) and identity.startswith('PILIVE.FIELD.3SCREEN.'),'HOLD_JOURNEY_ID')
    events=journey.get('events');require(isinstance(events,list) and len(events)==3,'HOLD_TASK_COUNT')
    require(journey.get('escapeObserved') is True and journey.get('focusReturn')=='USER_CONFIRMED_PROJECT_ROW','HOLD_ESCAPE_OR_FOCUS')
    require(journey.get('focusBindingTarget')=='project.ENGURU_PROGRESS_CORE','HOLD_FOCUS_BINDING')
    require(journey.get('productAcceptance')=='HOLD' and journey.get('verifiedFinish')=='HOLD','HOLD_AUTHORITY')
    source_identity=None;prior=None;results=[]
    for event,(task,pid) in zip(events,TASKS):
        require(event['taskId']==task and event['projectId']==pid and event['journeyId']==identity,'HOLD_TASK_IDENTITY')
        require(event.get('userConfirmation')=='EXPLICIT_TASK_BUTTON' and event.get('windowVisible') is True,'HOLD_USER_ACTION')
        packet=json.loads(base64.b64decode(event['readerPacketBase64'],validate=True));observation=packet['observation'];snapshot=observation['snapshot']
        require(packet==export_packet(observation),'HOLD_WIRE_BINDING')
        before=observation['sourceManifestBefore'];after=observation['sourceManifestAfter'];pins=before['pins']
        require(before==after and not before['errors'] and pins==snapshot['sourcePins'],'HOLD_SOURCE_DRIFT')
        require(all(pins.get(k)==v for k,v in safe.CORE_PINS.items()),'HOLD_CORE_PINS')
        registry={'schema':'enguru.progress-core.project-registry/v1','projects':{}}
        for key,pair in observation['coreFacts'].items():
            binding=snapshot['sourceClassification'][key];summary=pair['summary']
            require(binding['projectId']==summary['projectId'],'HOLD_PROJECT_ID')
            for field,digest in [('state','stateDigest'),('worklist','worklistDigest')]:
                require(pins.get(binding[field])==summary[digest],'HOLD_SOURCE_BINDING')
            registry['projects'][key]={'projectId':binding['projectId'],'state':binding['state'],'worklist':binding['worklist']}
        replay=build_portfolio(registry,observation['coreFacts'],revision_before=snapshot['sourceRevision'],revision_after=snapshot['sourceRevision'],pins_before=pins,pins_after=pins,source_read_at=snapshot['sourceReadAt'],adapter_built_at=snapshot['adapterBuiltAt'])
        require(replay['projects']==snapshot['projects'] and replay['projectionDigest']==snapshot['projectionDigest'],'HOLD_REPLAY')
        pair=(snapshot['sourceRevision'],snapshot['projectionDigest'])
        if source_identity is None:source_identity=pair
        require(pair==source_identity and (event['sourceRevision'],event['projectionDigest'])==pair,'HOLD_CROSS_SCREEN_DRIFT')
        row=next(r for r in snapshot['projects'] if r['projectId']==pid)
        for k in ('projectKey','done','total','percent','activeItem','finish','officialAcceptance'):
            source_key='key' if k=='projectKey' else k
            if k=='percent' and row[source_key] is not None:
                require(type(event[k]) in (int,float) and math.isfinite(event[k]) and event[k]==row[source_key],'HOLD_DISPLAY_PERCENT')
            else:require(event[k]==row[source_key] and type(event[k]) is type(row[source_key]),'HOLD_DISPLAY_'+k.upper())
        binding=snapshot['sourceClassification'][row['key']]
        require(event['projectSourcePins']=={binding[k]:pins[binding[k]] for k in ('state','worklist')},'HOLD_PROJECT_EVIDENCE')
        times=[datetime.fromisoformat(event[k].replace('Z','+00:00')) for k in ('sourceReadAt','adapterBuiltAt','uiRenderedAt','eventAt')]
        require(all(t.utcoffset() is not None for t in times) and times==sorted(times),'HOLD_TIME_ORDER')
        require(event['sourceReadAt']==snapshot['sourceReadAt'] and event['adapterBuiltAt']==snapshot['adapterBuiltAt'],'HOLD_TIME_SOURCE')
        require(0<=(times[-1]-times[0]).total_seconds()<=60,'HOLD_STALE_EVENT')
        require(prior is None or prior<=times[-1],'HOLD_EVENT_ORDER');prior=times[-1]
        name=event['screenshot'];require(isinstance(name,str) and re.fullmatch(r'FIELD_[A-Za-z0-9_.-]+\.png',name),'HOLD_IMAGE_PATH')
        raw=safe.read_file(folder,name,12*1024*1024)
        require(safe.digest(raw)==event['screenshotSha256'] and raw[:8]==b'\x89PNG\r\n\x1a\n' and raw[12:16]==b'IHDR','HOLD_IMAGE_SHA')
        width,height=struct.unpack('>II',raw[16:24]);require(200<=width<=6000 and 100<=height<=6000,'HOLD_IMAGE_DIMENSIONS')
        results.append({'taskId':task,'projectId':pid,'dataBinding':'PASS','imageSha256':safe.digest(raw),'imageDimensions':[width,height],'visualReview':'HOLD_INDEPENDENT_REVIEW','productAcceptance':'HOLD'})
    return {'state':'PASS_TASK_DATA_AND_IMAGE_INTEGRITY_ONLY','journeyId':identity,'tasks':results,'sourceRevision':source_identity[0],'projectionDigest':source_identity[1],'independentGuiAcceptance':'HOLD','verifiedFinish':'HOLD'}
