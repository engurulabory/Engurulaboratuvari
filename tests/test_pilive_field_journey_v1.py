"""Synthetic hostile journey fixtures, not real Mac field acceptance."""
import base64,copy,hashlib,json,struct,tempfile,unittest,zlib
from pathlib import Path
from tools.pilive_field_journey_v1 import validate,TASKS
from tools.pilive_live_reader_v1 import packet
from test_pilive_screen_wire_v1 import native_model

def png():
    def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',400,240,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\x10\x20\x10'*400)*240))+chunk(b'IEND',b'')

def fixture(folder):
    s=native_model();facts=json.loads((Path(__file__).parent/'fixtures/pilive_native_portfolio_review_v1.json').read_text())
    s['sourceClassification']={key:dict(entry) for key,entry in facts['registry']['projects'].items()}
    observation={'state':'PASS_NATIVE_PORTFOLIO_CAPTURE_ONLY','snapshot':s,'coreFacts':facts['facts'],'sourceManifestBefore':{'pins':s['sourcePins'],'errors':{}},'sourceManifestAfter':{'pins':s['sourcePins'],'errors':{}}}
    raw=json.dumps(packet(observation)).encode();data=png();jid='PILIVE.FIELD.3SCREEN.TEST';events=[]
    for task,pid in TASKS:
        row=next(r for r in s['projects'] if r['projectId']==pid);binding=s['sourceClassification'][row['key']];name='FIELD_'+task+'.png';(folder/name).write_bytes(data)
        event={k:row[k] for k in ('done','total','percent','activeItem','finish','officialAcceptance')}
        event.update(taskId=task,journeyId=jid,projectId=pid,projectKey=row['key'],userConfirmation='EXPLICIT_TASK_BUTTON',windowVisible=True,sourceRevision=s['sourceRevision'],projectionDigest=s['projectionDigest'],sourceReadAt=s['sourceReadAt'],adapterBuiltAt=s['adapterBuiltAt'],uiRenderedAt='2026-10-26T06:03:59Z',eventAt='2026-10-26T06:04:00Z',projectSourcePins={binding[k]:s['sourcePins'][binding[k]] for k in ('state','worklist')},readerPacketBase64=base64.b64encode(raw).decode(),screenshot=name,screenshotSha256=hashlib.sha256(data).hexdigest())
        events.append(event)
    return {'schema':'enguru.pilive.field-journey/v1','journeyId':jid,'events':events,'escapeObserved':True,'focusReturn':'USER_CONFIRMED_PROJECT_ROW','focusBindingTarget':'project.ENGURU_PROGRESS_CORE','productAcceptance':'HOLD','verifiedFinish':'HOLD'}

class FieldJourneyTests(unittest.TestCase):
    def test_three_tasks_preserve_two_different_project_identities(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();r=validate(fixture(root),root)
            self.assertEqual(len(r['tasks']),3);self.assertEqual(r['tasks'][1]['projectId'],'ENGURU_PROGRESS_CORE');self.assertEqual(r['independentGuiAcceptance'],'HOLD')
    def test_wrong_evidence_counter_time_and_user_claim_rejected(self):
        for key,value in [('projectId','ENGURU_PLIVE_P02_USER_SCREEN'),('done',0),('percent',True),('eventAt','2026-10-26T07:00:00Z'),('userConfirmation','AUTOMATIC')]:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as folder:
                root=Path(folder).resolve();d=fixture(root);d['events'][2][key]=value
                with self.assertRaises(ValueError):validate(d,root)
    def test_missing_duplicate_tasks_and_fake_authority_rejected(self):
        for change in [lambda d:d['events'].pop(),lambda d:d['events'].reverse(),lambda d:d.update(verifiedFinish='VERIFIED'),lambda d:d.update(escapeObserved=False)]:
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder).resolve();d=fixture(root);change(d)
                with self.assertRaises(ValueError):validate(d,root)
    def test_screenshot_tamper_path_escape_and_symlink_rejected(self):
        for mode in ('bytes','path','link'):
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder).resolve();d=fixture(root);event=d['events'][0];image=root/event['screenshot']
                if mode=='bytes':image.write_bytes(b'changed')
                elif mode=='path':event['screenshot']='../outside.png'
                else:image.unlink();image.symlink_to(root/d['events'][1]['screenshot'])
                with self.assertRaises((OSError,ValueError)):validate(d,root)
    def test_numeric_json_normalization_does_not_change_percent_meaning(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();d=fixture(root)
            for e in d['events']:e['percent']=int(e['percent'])
            self.assertEqual(validate(d,root)['state'],'PASS_TASK_DATA_AND_IMAGE_INTEGRITY_ONLY')
