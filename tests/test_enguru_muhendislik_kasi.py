import base64
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/'tools'))
import enguru_muhendislik_kasi as m

BASE = '''# ENGÜRÜ OSi × ChatGPT — Mühendislik Kası™\n\nSome preserved previous history.\n'''

def fixture(**changes):
    e = dict(schema=m.SCHEMA,eventId='MK-EVT-ABC123',taskId=m.TASK_ID,
             observedAt='2026-10-23T13:00:00+03:00',type='MISMATCH',evidenceLevel='B',
             sourceUri='https://github.com/engurulabory/Engurulaboratuvari/pull/203',
             sourceSha256='a'*64,expected='valid expected',observed='different observation',
             causeStatus='HYPOTHESIS',fixProposal='add validated new rule',testState='NOT_EXECUTED')
    e.update(changes)
    return e


def payload(e): return json.dumps(e,ensure_ascii=False).encode()

class EngineeringMuscle(unittest.TestCase):
    def test_01_accepted_candidate(self):
        doc, r = m.process(BASE,payload(fixture()))
        self.assertEqual(r['state'],'NEW_REVIEW_CANDIDATE')
        self.assertIn('MK-EVT-ABC123',doc)
    def test_02_idempotent(self):
        d,_=m.process(BASE,payload(fixture()))
        b,r=m.process(d,payload(fixture()))
        self.assertEqual(b,d);self.assertEqual(r['state'],'IDEMPOTENT_SAME_EVENT')
    def test_03_conflict(self):
        d,_=m.process(BASE,payload(fixture()))
        with self.assertRaisesRegex(m.IntakeHold,'ID_CONTENT_CONFLICT'): m.process(d,payload(fixture(observed='altered')))
    def test_04_wrong_scope(self):
        with self.assertRaisesRegex(m.IntakeHold,'TASK_SCOPE'): m.process(BASE,payload(fixture(taskId='OTHER_TASK')))
    def test_05_unknown_field(self):
        with self.assertRaisesRegex(m.IntakeHold,'SCHEMA_FIELDS'):m.process(BASE,payload(fixture(injected='a')))
    def test_06_duplicate_json_keys(self):
        raw=payload(fixture())[:-1]+b',"eventId":"MK-EVT-DUP123"}'
        with self.assertRaisesRegex(m.IntakeHold,'DUPLICATE_JSON_KEY'):m.process(BASE,raw)
    def test_07_bad_sha(self):
        with self.assertRaisesRegex(m.IntakeHold,'SHA_FORMAT'):m.process(BASE,payload(fixture(sourceSha256='a'*12)))
    def test_08_no_evidence_no_pass(self):
        _,r=m.process(BASE,payload(fixture(evidenceLevel='D',causeStatus='CONFIRMED')))
        self.assertEqual(r['officialAcceptance'],'UNCHANGED_HOLD')
        self.assertIn('OWNER_ATTESTATION_REQUIRES_EXTERNAL_CANONICAL_VERIFIER',r['issues'])
    def test_09_zero_examined(self):
        _,r=m.process(BASE,payload(fixture(examinedCount=0)))
        self.assertIn('ZERO_COVERAGE_IS_NOT_ABSENCE_PROOF',r['issues'])
    def test_10_bad_time(self):
        with self.assertRaisesRegex(m.IntakeHold,'TIME_FORMAT'):m.process(BASE,payload(fixture(observedAt='2026-10-23')))
    def test_11_secret_key(self):
        with self.assertRaisesRegex(m.IntakeHold,'POTENTIAL_SECRET'):m.process(BASE,payload(fixture(observed='-----BEGIN PRIVATE KEY-----')))
    def test_12_password_value(self):
        with self.assertRaisesRegex(m.IntakeHold,'POTENTIAL_SECRET'):m.process(BASE,payload(fixture(observed='password=sekret123')))
    def test_13_raw_html_escaped(self):
        d,_=m.process(BASE,payload(fixture(observed='<script>alert(1)</script>')))
        self.assertIn('&lt;script&gt;',d)
    def test_14_pipe_escaped(self):
        d,_=m.process(BASE,payload(fixture(observed='foo | bar')))
        self.assertIn('foo &#124; bar',d)
    def test_15_evidence_sha_valid(self):
        with tempfile.TemporaryDirectory() as x:
            file=pathlib.Path(x)/'proof.json';file.write_text('proof')
            e=fixture(sourcePath=str(file),sourceSha256=m.sha(file.read_bytes()))
            _,r=m.process(BASE,payload(e));self.assertEqual(r['evidenceState'],'PASS_BYTE_SHA_ONLY')
    def test_16_evidence_sha_invalid(self):
        with tempfile.TemporaryDirectory() as x:
            file=pathlib.Path(x)/'proof.json';file.write_text('proof')
            with self.assertRaisesRegex(m.IntakeHold,'SHA_MISMATCH'):m.process(BASE,payload(fixture(sourcePath=str(file))))
    def test_17_evidence_symlink(self):
        with tempfile.TemporaryDirectory() as x:
            file=pathlib.Path(x)/'proof';file.write_text('proof');link=pathlib.Path(x)/'link';link.symlink_to(file)
            with self.assertRaisesRegex(m.IntakeHold,'EVIDENCE_FILE'):m.process(BASE,payload(fixture(sourcePath=str(link))))
    def test_18_existing_record_protection(self):
        with self.assertRaisesRegex(m.IntakeHold,'RECORD_AUTHORITY'):m.process('# Other document',payload(fixture()))
    def test_19_marker_tamper(self):
        d,_=m.process(BASE,payload(fixture()));d=d.replace('ENGURU_MK_EVENT_V1:', 'ENGURU_MK_EVENT_V1:AA')
        with self.assertRaises(m.IntakeHold):m.process(d,payload(fixture()))
    def test_20_large_event(self):
        with self.assertRaisesRegex(m.IntakeHold,'EVENT_SIZE'):m.process(BASE,b' '*25000)
    def test_21_unknown_enum(self):
        with self.assertRaisesRegex(m.IntakeHold,'EVENT_ENUM'):m.process(BASE,payload(fixture(type='OWNER_PASS')))
    def test_22_missing_authorized_actor(self):
        with tempfile.TemporaryDirectory() as x:
            env=pathlib.Path(x)/'event.json';rec=pathlib.Path(x)/'record.md';out=pathlib.Path(x)/'out.md'
            rec.write_text(BASE)
            env.write_text(json.dumps({'issue':{'number':203,'pull_request':{}},'sender':{'login':'attacker'},'comment':{'body':'```enguru-mk-event\n'+payload(fixture()).decode()+'\n```'}}))
            try:
                os.environ['ENGURU_MK_OWNER_LOGIN']='owner'
                with self.assertRaisesRegex(m.IntakeHold,'ACTOR'):m.run(['--record',str(rec),'--github-event',str(env),'--output',str(out),'--receipt',str(pathlib.Path(x)/'receipt.json')])
            finally: os.environ.pop('ENGURU_MK_OWNER_LOGIN',None)
    def test_23_scope_comment(self):
        with tempfile.TemporaryDirectory() as x:
            path=pathlib.Path(x);rec=path/'rec.md';out=path/'out.md';evt=path/'event.json';rec.write_text(BASE)
            evt.write_text(json.dumps({'issue':{'number':100,'pull_request':{'url':'yes'}},'sender':{'login':'owner'},'comment':{'body':'```enguru-mk-event\n'+payload(fixture()).decode()+'\n```'}}))
            try:
                os.environ['ENGURU_MK_OWNER_LOGIN']='owner'
                with self.assertRaisesRegex(m.IntakeHold,'ISSUE_SCOPE'):m.run(['--record',str(rec),'--github-event',str(evt),'--output',str(out),'--receipt',str(path/'receipt.json')])
            finally: os.environ.pop('ENGURU_MK_OWNER_LOGIN',None)
    def test_24_authorized_comment(self):
        with tempfile.TemporaryDirectory() as x:
            path=pathlib.Path(x);rec=path/'rec.md';out=path/'out.md';evt=path/'event.json';rec.write_text(BASE)
            evt.write_text(json.dumps({'issue':{'number':203,'pull_request':{'url':'yes'}},'sender':{'login':'owner'},'comment':{'body':'```enguru-mk-event\n'+payload(fixture()).decode()+'\n```'}}))
            try:
                os.environ['ENGURU_MK_OWNER_LOGIN']='owner'
                m.run(['--record',str(rec),'--github-event',str(evt),'--output',str(out),'--receipt',str(path/'receipt.json')])
            finally: os.environ.pop('ENGURU_MK_OWNER_LOGIN',None)
            self.assertIn('MK-EVT-ABC123',out.read_text());self.assertEqual(rec.read_text(),BASE)
    def test_25_negative_not_owner_decision(self):
        _,r=m.process(BASE,payload(fixture(type='SUCCESS',evidenceLevel='D',testState='PASS')))
        self.assertEqual(r['productGatesModified'],0)
    def test_26_no_automatic_code_execution(self):
        d,_=m.process(BASE,payload(fixture(observed='$(rm -rf ~/Enguru)')))
        self.assertIn('$(rm -rf',d)
    def test_27_replay_hash(self):
        d,_=m.process(BASE,payload(fixture())); self.assertEqual(len(m.markers(d)),1)
    def test_28_broken_event_id(self):
        with self.assertRaisesRegex(m.IntakeHold,'ID_SCHEMA'): m.process(BASE,payload(fixture(eventId='../../bad')))
    def test_29_unsupported_empty_source(self):
        with self.assertRaisesRegex(m.IntakeHold,'EMPTY_FIELD'):m.process(BASE,payload(fixture(sourceUri=' ')))
    def test_30_no_mutation_on_failure(self):
        with tempfile.TemporaryDirectory() as x:
            path=pathlib.Path(x);rec=path/'rec.md';out=path/'out.md';ev=path/'ev.json';rec.write_text(BASE);ev.write_bytes(payload(fixture(taskId='WRONG')))
            with self.assertRaises(m.IntakeHold):m.run(['--record',str(rec),'--event',str(ev),'--output',str(out),'--receipt',str(path/'receipt.json')])
            self.assertFalse(out.exists());self.assertEqual(rec.read_text(),BASE)

if __name__=='__main__':unittest.main(verbosity=1)