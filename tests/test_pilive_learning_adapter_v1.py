import copy
import json
import unittest
from tools import enguru_muhendislik_kasi as mk
from tools import pilive_learning_adapter_v1 as p

RECORD='# ENGÜRÜ OSi × ChatGPT — Mühendislik Kası™\nManagement V6.9 scope preserved.\n'

def event(task=mk.TASK_ID):
    return {'schema':mk.SCHEMA,'eventId':'MK-EVT-UNIT-12345','taskId':task,
      'observedAt':'2026-10-25T15:26:00Z','type':'SUCCESS','evidenceLevel':'A',
      'sourceUri':'urn:unit:source','sourceSha256':'a'*64,'expected':'source',
      'observed':'scope','causeStatus':'UNKNOWN','fixProposal':'review','testState':'NOT_EXECUTED'}

def chain():
    files={f'tools/unit{i}.py':{'contentUtf8':'unit'+str(i),'bytes':5,'sha256':p.digest(('unit'+str(i)).encode())} for i in range(7)}
    base={'platform':'Darwin','stableBracket':True,'before':{'head':'a'*40},'after':{'head':'a'*40},'errors':[],
      'appLaunches':0,'canonicalWrites':0,'keychainReads':0,'networkRequests':0}
    v2={**base,'schema':p.SCHEMA_V2,'sources':files};b2=p.canonical(v2)
    v3={**base,'schema':p.SCHEMA_V3,'parentReceiptSha256':p.digest(b2),
      'sources':{'/native/root/'+k:v for k,v in files.items()},'externalSourceCandidates':{}}
    return b2,p.canonical(v3)

def check(b2,b3):return p.verify_chain(b2,b3,expected_v2_sha=p.digest(b2),expected_v3_sha=p.digest(b3))

class ScopeTests(unittest.TestCase):
    def test_management_default_preserved(self):self.assertEqual(mk.parse_event(p.canonical(event()))['taskId'],mk.TASK_ID)
    def test_pilive_default_rejected(self):
        with self.assertRaises(mk.IntakeHold):mk.parse_event(p.canonical(event(p.TASK_ID)))
    def test_management_rejected_by_pilive_scope(self):
        with self.assertRaises(mk.IntakeHold):mk.parse_event(p.canonical(event()),expected_task_id=p.TASK_ID)
    def test_unknown_adapter_scope_rejected(self):
        with self.assertRaises(mk.IntakeHold):mk.parse_event(p.canonical(event()),expected_task_id='ANY_TASK')
    def test_pilive_scoped_event_accepted_only_as_candidate(self):
        _,r=mk.process(RECORD,p.canonical(event(p.TASK_ID)),expected_task_id=p.TASK_ID)
        self.assertEqual(r['officialAcceptance'],'UNCHANGED_HOLD');self.assertEqual(r['productGatesModified'],0)
    def test_sanitized_candidate_replay(self):
        args=dict(fact_id='SOURCE_SCOPE',source_sha256='a'*64,observed_at='2026-10-25T15:26:00Z',correlation_id='OSIBLOCK-PILIVE-V3')
        updated,_=p.review_candidate(RECORD,**args);replay,r=p.review_candidate(updated,**args)
        self.assertEqual(updated,replay);self.assertEqual(r['state'],'IDEMPOTENT_SAME_EVENT');self.assertNotIn('/Users/',updated)
    def test_arbitrary_raw_text_fact_rejected(self):
        with self.assertRaises(mk.IntakeHold):p.review_candidate(RECORD,fact_id='raw native payload',source_sha256='a'*64,observed_at='',correlation_id='')
    def test_secret_rejected_in_explicit_pilive_scope(self):
        e=event(p.TASK_ID);e['observed']='password=unit-example'
        with self.assertRaises(mk.IntakeHold):mk.parse_event(p.canonical(e),expected_task_id=p.TASK_ID)
    def test_fact_hash_malformed_rejected(self):
        with self.assertRaises(mk.IntakeHold):p.review_candidate(RECORD,fact_id='SOURCE_SCOPE',source_sha256='bad',observed_at='',correlation_id='')

class EvidenceTests(unittest.TestCase):
    def test_valid_chain(self):self.assertEqual(check(*chain())['contentRecordsVerified'],7)
    def test_wrong_expected_receipt_pin(self):
        b2,b3=chain()
        with self.assertRaises(mk.IntakeHold):p.verify_chain(b2,b3,expected_v2_sha='b'*64,expected_v3_sha=p.digest(b3))
    def test_parent_mismatch(self):
        b2,b3=chain();v=p.strict_receipt(b3);v['parentReceiptSha256']='b'*64
        with self.assertRaises(mk.IntakeHold):check(b2,p.canonical(v))
    def test_source_content_tamper(self):
        b2,b3=chain();v=p.strict_receipt(b3);next(iter(v['sources'].values()))['contentUtf8']='tamper'
        with self.assertRaises(mk.IntakeHold):check(b2,p.canonical(v))
    def test_source_alias_collision(self):
        b2,b3=chain();v=p.strict_receipt(b3);v['sources']['/other/tools/unit0.py']=v['sources']['/native/root/tools/unit0.py']
        with self.assertRaises(mk.IntakeHold):check(b2,p.canonical(v))
    def test_boolean_zero_scope_rejected(self):
        b2,b3=chain();v=p.strict_receipt(b3);v['canonicalWrites']=False
        with self.assertRaises(mk.IntakeHold):check(b2,p.canonical(v))
    def test_drift_rejected(self):
        b2,b3=chain();v=p.strict_receipt(b3);v['after']['head']='b'*40
        with self.assertRaises(mk.IntakeHold):check(b2,p.canonical(v))
    def test_duplicate_json_key(self):
        with self.assertRaises(mk.IntakeHold):p.strict_receipt(b'{"x":1,"x":2}')
    def test_nonfinite_json(self):
        with self.assertRaises(mk.IntakeHold):p.strict_receipt(b'{"x":NaN}')
    def test_empty_or_outside_source_set(self):
        b2,b3=chain();v=p.strict_receipt(b2);v['sources']={}
        with self.assertRaises(mk.IntakeHold):check(p.canonical(v),b3)

class DisplayAndScheduleTests(unittest.TestCase):
    def test_exact_integer_counts(self):self.assertEqual(p.exact_counts(8,12)['percentNumerator'],800)
    def test_bool_float_zero_and_overflow_rejected(self):
        for d,t in [(True,12),(1.5,12),(1,12.0),(0,0),(13,12),(-1,12)]:
            with self.subTest(d=d,t=t),self.assertRaises(mk.IntakeHold):p.exact_counts(d,t)
    def runs(self):return [{'id':i+1,'workflow_id':10,'event':'schedule','created_at':f'2026-10-25T15:{i*5:02d}:00Z','status':'completed','conclusion':'success','head_sha':'a'*40} for i in range(4)]
    def test_four_current_runs_within_bound(self):self.assertEqual(p.schedule_evidence(self.runs(),workflow_id=10,current_sha='a'*40)['state'],'PASS_BOUNDED_FOUR_RUN_WINDOW')
    def test_large_gap_is_hold(self):
        r=self.runs();r[-1]['created_at']='2026-10-25T17:15:00Z'
        self.assertEqual(p.schedule_evidence(r,workflow_id=10,current_sha='a'*40)['state'],'HOLD_SCHEDULE_CONTINUITY')
    def test_wrong_head_failed_and_skipped_hold(self):
        for k,v in [('head_sha','b'*40),('status','queued'),('conclusion','skipped')]:
            r=self.runs();r[0][k]=v
            self.assertEqual(p.schedule_evidence(r,workflow_id=10,current_sha='a'*40)['state'],'HOLD_SCHEDULE_CONTINUITY')
    def test_duplicate_run_rejected(self):
        r=self.runs();r.append(copy.deepcopy(r[0]))
        with self.assertRaises(mk.IntakeHold):p.schedule_evidence(r,workflow_id=10,current_sha='a'*40)
    def test_dispatch_is_not_schedule(self):
        r=self.runs();r[0]['event']='workflow_dispatch'
        self.assertEqual(p.schedule_evidence(r,workflow_id=10,current_sha='a'*40)['state'],'HOLD_SCHEDULE_CONTINUITY')

if __name__=='__main__':unittest.main()
