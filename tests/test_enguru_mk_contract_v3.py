"""ENGURU MK V3: additional 25 adversarial cases (20%+ coverage reserve)."""
import hashlib, json, pathlib, sys, unittest
from copy import deepcopy
from datetime import datetime
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'tools'))
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import enguru_muhendislik_kasi as m
import enguru_mk_five_minute_watch as w
from test_enguru_mk_five_minute_watch import FakeGH,BASE,NOW,comment
from test_enguru_muhendislik_kasi import fixture,payload

class LearningContractV3(unittest.TestCase):
    def setUp(self):
        self.gh=FakeGH();self.rec,self.ck,_=w.evaluate(self.gh,BASE,None,'owner',NOW)
    def cycle(self,owner='owner'):
        self.rec,self.ck,out=w.evaluate(self.gh,self.rec,self.ck,owner,NOW)
        return out
    def add(self,id,text,pr=203,owner='owner'):
        self.gh.comments[w.TARGETS[0][:2] if pr==203 else w.TARGETS[1][:2]].append(comment(id,text,user=owner,number=pr))
    def test_01_owner_command_is_data(self):
        self.add(10001,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID=OSIBLOCK-AAAAAA\n$(curl https://example.com)')
        self.cycle();self.assertIn('$(curl https:',self.rec);self.assertIn('REVIEW_REQUIRED',self.rec)
    def test_02_script_tags_escaped(self):
        self.add(10002,'<!-- ENGURU_OSI_RESPONSE_V1 -->\nBLOCK_ID=OSIBLOCK-AAAAAA\n<script>bad</script>')
        self.cycle();self.assertIn('&lt;script&gt;',self.rec)
    def test_03_private_early_abort(self):
        def f(endpoint):
            if 'enguru-mac-engineer' in endpoint: raise AssertionError('PRIVATE_EXTERNAL_CALL')
            return self.gh(endpoint)
        w.evaluate(f,self.rec,self.ck,'owner',NOW)
    def test_04_bad_correlation_bytes_rejected(self):
        self.add(10004,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID=evil space\nresult')
        self.cycle();self.assertEqual(self.rec,BASE)
    def test_05_correlation_small_rejected(self):
        self.add(10005,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID=A\nresult')
        self.cycle();self.assertEqual(self.rec,BASE)
    def test_06_multiple_known_blocks_persist(self):
        for id,v in [(10006,'OSIBLOCK-AAAAAA'),(10007,'OSIBLOCK-BBBBBB')]:
            self.add(id,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID='+v+'\ncommand')
        self.cycle();k=w.key(*w.TARGETS[0][:2]);self.assertEqual(len(self.ck['targets'][k]['osiBlockIds']),2)
    def test_07_unpaired_response_hold(self):
        self.add(10008,'<!-- ENGURU_OSI_RESPONSE_V1 -->\nBLOCK_ID=OSIBLOCK-UNSEEN\nresponse')
        self.cycle();self.assertIn('PAIR_MISSING_REVIEW_REQUIRED',self.rec)
    def test_08_pair_from_different_pr_is_not_auto_match(self):
        self.add(10009,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID=OSIBLOCK-XPR001\ncommand',203)
        self.add(10010,'<!-- ENGURU_OSI_RESPONSE_V1 -->\nBLOCK_ID=OSIBLOCK-XPR001\nresponse',206)
        self.cycle();self.assertIn('PAIR_MISSING_REVIEW_REQUIRED',self.rec)
    def test_09_duplicate_block_stays_deduped_in_checkpoint(self):
        self.add(10011,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID=OSIBLOCK-DUP001\nfirst')
        self.add(10012,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID=OSIBLOCK-DUP001\nsecond')
        self.cycle();k=w.key(*w.TARGETS[0][:2]);self.assertEqual(self.ck['targets'][k]['osiBlockIds'].count('OSIBLOCK-DUP001'),1)
    def test_10_same_event_twice_stays_idempotent(self):
        self.add(10013,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID=OSIBLOCK-AAAAAA\nfirst')
        self.cycle();old=self.rec;self.cycle();self.assertEqual(self.rec,old)
    def test_11_signer_pass_word_not_authority(self):
        self.add(10014,'<!-- ENGURU_OSI_RESPONSE_V1 -->\nBLOCK_ID=OSIBLOCK-AAAAAA\nVERIFIED_FINISH=PASS')
        self.cycle();self.assertIn('ürün kabul sayacı değişimi `0`',self.rec)
    def test_12_non_owner_purported_owner_rejected(self):
        self.add(10015,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID=OSIBLOCK-AAAAAA\ncommand',owner='attacker')
        self.cycle();self.assertEqual(self.rec,BASE)
    def test_13_empty_owner_rejected(self):
        self.add(10016,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID=OSIBLOCK-AAAAAA\ncommand')
        self.cycle(owner='');self.assertEqual(self.rec,BASE)
    def test_14_private_access_hold_is_explicit(self):
        self.cycle();self.assertEqual(self.ck['accessHolds'],[w.PRIVATE_SOURCE_HOLD])
    def test_15_known_source_is_exclusively_review_branch(self):
        self.add(10017,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID=OSIBLOCK-AAAAAA\ncommand')
        old=BASE;self.cycle();self.assertEqual(old,BASE);self.assertTrue(self.rec.startswith(old))
    def test_16_missing_evidence_not_independently_pass(self):
        _,receipt=m.process(BASE,payload(fixture()))
        self.assertEqual(receipt['evidenceState'],'UNVERIFIED_EVIDENCE_POINTER')
    def test_17_signed_scope_declared_in_event_still_hold(self):
        _,receipt=m.process(BASE,payload(fixture(evidenceLevel='D',testState='PASS')))
        self.assertEqual(receipt['officialAcceptance'],'UNCHANGED_HOLD')
    def test_18_digest_conflict_resists_overwrite(self):
        e=fixture(eventId='MK-EVT-CONTRACT18');d,_=m.process(BASE,payload(e))
        with self.assertRaisesRegex(m.IntakeHold,'ID_CONTENT_CONFLICT'):
            m.process(d,payload(fixture(eventId='MK-EVT-CONTRACT18',observed='other')))
    def test_19_time_requires_timezone(self):
        with self.assertRaisesRegex(m.IntakeHold,'TIME_FORMAT'):
            m.process(BASE,payload(fixture(observedAt='2026-10-23T14:21:00')))
    def test_20_tampered_record_marker_fails_closed(self):
        e=fixture(eventId='MK-EVT-CONTRACT20');d,_=m.process(BASE,payload(e));d=d.replace('ENGURU_MK_EVENT_V1:','ENGURU_MK_EVENT_V1:AA')
        with self.assertRaises(m.IntakeHold):m.process(d,payload(e))
    def test_21_unsupported_json_keys_hold(self):
        with self.assertRaisesRegex(m.IntakeHold,'SCHEMA_FIELDS'):
            m.process(BASE,payload(fixture(ownerSigned=True)))
    def test_22_wrong_exact_task_rejected(self):
        self.add(10022,'<!-- ENGURU_OSI_BLOCK_V1 -->\nTASK_ID=ENGURU_OTHER_TASK\nBLOCK_ID=OSIBLOCK-AAAAAA\ncommand')
        self.cycle();self.assertEqual(self.rec,BASE)
    def test_23_paired_event_not_actual_cryptographic_pass(self):
        self.add(10023,'<!-- ENGURU_OSI_BLOCK_V1 -->\nBLOCK_ID=OSIBLOCK-AAAAAA\ncommand')
        self.add(10024,'<!-- ENGURU_OSI_RESPONSE_V1 -->\nBLOCK_ID=OSIBLOCK-AAAAAA\nreal evidence')
        self.cycle();self.assertIn('PAIR_MATCHED_REVIEW_ONLY',self.rec)
        self.assertIn('ürün kabul sayacı değişimi `0`',self.rec)
    def test_24_invalid_checkpoint_corruption_hold(self):
        k=w.key(*w.TARGETS[0][:2]);self.ck['targets'][k]['osiBlockIds']=['$RUN_SHELL']
        with self.assertRaisesRegex(ValueError,'OSI_PAIR_CHECKPOINT'):self.cycle()
    def test_25_empty_evidence_source_hold(self):
        with self.assertRaisesRegex(m.IntakeHold,'EMPTY_FIELD'):
            m.process(BASE,payload(fixture(sourceUri='')))