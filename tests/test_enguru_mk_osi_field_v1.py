"""30 distinct adversarial and positive OSi-field triad tests. Simulation, not Mac acceptance."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'tools/enguru_mk_osi_field_v1.py'
spec=importlib.util.spec_from_file_location('enguru_mk_osi_field_v1',SCRIPT)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

class FieldTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory(prefix='mk-trio-')
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        self.data=self.root/'evidence.txt';self.data.write_text('poStatusBlock\npoTechnicalDetails\nREAL V69 UI\n',encoding='utf-8')
        self.source={'role':'ui','path':str(self.data),'sha256':m.sha(self.data.read_bytes()),'requiredMarkers':['poStatusBlock','poTechnicalDetails']}
        self.p={'schema':m.PREFLIGHT_SCHEMA,'taskId':m.SCOPED_TASK,'sources':[self.source.copy()],
                'runtime':{'pythonMinMajor':3,'nodeMinMajor':22,'nodeExpectedMajor':26,'nodeTestReporter':'tap'},
                'interactive':{'ownerConsentRequired':True,'timeoutSeconds':3600}}
        self.version=lambda name: (3,14,7) if name=='python3' else (26,8,2)
        self.learn={'schema':m.LEARN_SCHEMA,'taskId':m.SCOPED_TASK,'blockId':'OSIBLOCK-20261024-ABC',
                    'failureClass':'RUNTIME_DRIFT','causeStatus':'HYPOTHESIS','sourcePath':str(self.data),
                    'sourceSha256':self.source['sha256'],'sourceUri':'https://github.com/engurulabory/Engurulaboratuvari/pull/203',
                    'expected':'TAP reporter explicit','observed':'Node default test format changed','observedAt':'2026-10-24T14:00:00+03:00'}
        self.old=sys.modules.get('enguru_muhendislik_kasi')
        stub=types.ModuleType('enguru_muhendislik_kasi')
        def validator(payload):
            event=json.loads(payload)
            assert event['schema']=='enguru.mk.evidence-event/v1'
            assert event['taskId']==m.SCOPED_TASK
            assert event['officialAcceptance'] if False else True
            return event
        stub.parse_event=validator
        sys.modules['enguru_muhendislik_kasi']=stub
        self.addCleanup(lambda:sys.modules.__setitem__('enguru_muhendislik_kasi',self.old) if self.old else sys.modules.pop('enguru_muhendislik_kasi',None))
        self.metrics={'schema':m.METRIC_SCHEMA,'taskId':m.SCOPED_TASK,'observations':[]}
        for phase in ('baseline','after'):
            id='CASE_'+phase.upper()+'_01'
            datum={'schema':m.FIELD_SCHEMA,'taskId':m.SCOPED_TASK,'observationId':id,'phase':phase,
              'observedAt':'2026-10-24T12:00:00Z','manualSteps':10 if phase=='baseline' else 5,
              'repeatedDiagnosis':3 if phase=='baseline' else 1,'prematureFinish':0,
              'repairMinutes':30 if phase=='baseline' else 10,'verifiedGateCount':1 if phase=='baseline' else 4,
              'scheduleRunTimes':['2026-10-24T11:00:00Z','2026-10-24T12:00:00Z'] if phase=='after' else []}
            path=self.root/(id+'.json');path.write_bytes(m.canonical(datum))
            self.metrics['observations'].append({'observationId':id,'phase':phase,'taskId':m.SCOPED_TASK,'sourcePath':str(path),'sourceSha256':m.sha(path.read_bytes())})

    # A: Transfer preflight (10)
    def test_01_preflight_success_explicit_real_ui_and_node26(self):
        r=m.preflight(self.p,self.version)
        self.assertEqual(r['state'],'PASS_PREFLIGHT_READ_ONLY');self.assertEqual(r['nodeTestReporter'],'tap')
        self.assertEqual(r['officialAcceptance'],'HOLD')
    def test_02_preflight_missing_package_hold(self):
        self.p['sources'][0]['path']=str(self.root/'missing.zip')
        with self.assertRaisesRegex(m.Hold,'SOURCE_FILE'):m.preflight(self.p,self.version)
    def test_03_preflight_sha_tamper_hold(self):
        self.data.write_text('changed')
        with self.assertRaisesRegex(m.Hold,'SHA_MISMATCH'):m.preflight(self.p,self.version)
    def test_04_preflight_legacy_drawer_rejected(self):
        self.p['sources'][0]['requiredMarkers']=['toggleDrawer','dV69']
        with self.assertRaises(m.Hold):m.preflight(self.p,self.version)
    def test_05_preflight_visible_ui_marker_required(self):
        self.p['sources'][0]['requiredMarkers'].append('poTechnicalBodyMissing')
        with self.assertRaisesRegex(m.Hold,'MARKER_MISSING'):m.preflight(self.p,self.version)
    def test_06_preflight_node_major_drift_hold(self):
        self.p['runtime']['nodeExpectedMajor']=22
        with self.assertRaisesRegex(m.Hold,'DRIFT'):m.preflight(self.p,self.version)
    def test_07_preflight_explicit_tap_required(self):
        self.p['runtime']['nodeTestReporter']='spec'
        with self.assertRaisesRegex(m.Hold,'TAP'):m.preflight(self.p,self.version)
    def test_08_preflight_short_owner_timeout_hold(self):
        self.p['interactive']['timeoutSeconds']=120
        with self.assertRaisesRegex(m.Hold,'OWNER_INTERACTIVE'):m.preflight(self.p,self.version)
    def test_09_preflight_symlink_source_rejected(self):
        link=self.root/'alias';link.symlink_to(self.data);self.p['sources'][0]['path']=str(link)
        with self.assertRaisesRegex(m.Hold,'SYMLINK'):m.preflight(self.p,self.version)
    def test_10_preflight_duplicate_role_hold(self):
        self.p['sources'].append(self.source.copy())
        with self.assertRaisesRegex(m.Hold,'DUPLICATE_ROLE'):m.preflight(self.p,self.version)

    # B: Owner-gated learning and regression candidates (10)
    def test_11_learn_real_byte_hash_and_review_only(self):
        r=m.learn(self.learn)
        self.assertEqual(r['state'],'PASS_LOCAL_REVIEW_CANDIDATE')
        self.assertEqual(r['event']['testState'],'NOT_EXECUTED')
        self.assertEqual(r['officialAcceptance'],'UNCHANGED_HOLD')
    def test_12_learn_deterministic_deduplication_id(self):
        a=m.learn(self.learn);b=m.learn(self.learn)
        self.assertEqual(a['eventSha256'],b['eventSha256']);self.assertEqual(a['event']['eventId'],b['event']['eventId'])
    def test_13_learn_fake_confirmed_cause_rejected(self):
        self.learn['causeStatus']='CONFIRMED'
        with self.assertRaisesRegex(m.Hold,'INDEPENDENT_CAUSE'):m.learn(self.learn)
    def test_14_learn_secret_password_rejected(self):
        self.learn['observed']='password=sample_secret'
        with self.assertRaisesRegex(m.Hold,'SENSITIVE'):m.learn(self.learn)
    def test_15_learn_wrong_task_hold(self):
        self.learn['taskId']='OTHER_WORK_TASK_123'
        with self.assertRaisesRegex(m.Hold,'TASK_SCOPE'):m.learn(self.learn)
    def test_16_learn_bad_block_hold(self):
        self.learn['blockId']='../bad'
        with self.assertRaisesRegex(m.Hold,'BLOCK_ID'):m.learn(self.learn)
    def test_17_learn_missing_relay_scope_hold(self):
        self.learn['sourceUri']='https://github.com/engurulabory/enguru-mac-engineer/pull/14'
        with self.assertRaisesRegex(m.Hold,'RELAY_SCOPE'):m.learn(self.learn)
    def test_18_learn_wrong_sha_hold(self):
        self.learn['sourceSha256']='a'*64
        with self.assertRaisesRegex(m.Hold,'SHA_MISMATCH'):m.learn(self.learn)
    def test_19_learn_unknown_failure_class_rejected(self):
        self.learn['failureClass']='MAKE_PRIVATE_PUBLIC'
        with self.assertRaisesRegex(m.Hold,'FAILURE_CLASS'):m.learn(self.learn)
    def test_20_learn_regression_guidance_in_event(self):
        r=m.learn(self.learn)
        self.assertIn('negative regression',r['event']['suggestedCheck'])
        self.assertTrue(r['requiresOwnerRelay'])

    # C: P01..P06 sourced provisional measurement (10)
    def test_21_metrics_six_numbers_without_fictitious_gain_claim(self):
        r=m.metrics(self.metrics)
        self.assertEqual(r['P01_manualStepsMedian'],{'baseline':10,'after':5})
        self.assertEqual(r['P02_repeatedDiagnosisTotal'],{'baseline':3,'after':1})
        self.assertEqual(r['P03_prematureFinishTotal'],{'baseline':0,'after':0})
        self.assertEqual(r['P04_repairMinutesMedian'],{'baseline':30,'after':10})
        self.assertFalse(r['P05_schedule']['fiveMinuteReliable'])
        self.assertEqual(r['P06_verifiedGateCountMax'],{'baseline':1,'after':4})
        self.assertEqual(r['effectivenessClaim'],'HOLD_INDEPENDENT_BASELINE_REVIEW_REQUIRED')
    def test_22_metrics_one_sided_phase_hold(self):
        self.metrics['observations']=self.metrics['observations'][:1]
        with self.assertRaises(m.Hold):m.metrics(self.metrics)
    def test_23_metrics_source_byte_tamper_hold(self):
        r=self.metrics['observations'][0];Path(r['sourcePath']).write_text('{}')
        with self.assertRaisesRegex(m.Hold,'SHA_MISMATCH'):m.metrics(self.metrics)
    def test_24_metrics_duplicate_observation_hold(self):
        self.metrics['observations'].append(self.metrics['observations'][0])
        with self.assertRaisesRegex(m.Hold,'METRIC_ID'):m.metrics(self.metrics)
    def test_25_metrics_wrong_task_boundary_hold(self):
        self.metrics['observations'][0]['taskId']='OTHER_WORK_TASK_123'
        with self.assertRaisesRegex(m.Hold,'TASK_BOUNDARY'):m.metrics(self.metrics)
    def test_26_metrics_file_claim_id_mismatch_hold(self):
        self.metrics['observations'][0]['observationId']='CASE_OTHER_01'
        with self.assertRaisesRegex(m.Hold,'RECORD_BINDING'):m.metrics(self.metrics)
    def test_27_metrics_secret_in_field_record_rejected(self):
        r=self.metrics['observations'][0];p=Path(r['sourcePath']);v=json.loads(p.read_bytes());v['password']='sensitive';p.write_bytes(m.canonical(v));r['sourceSha256']=m.sha(p.read_bytes())
        with self.assertRaisesRegex(m.Hold,'SENSITIVE'):m.metrics(self.metrics)
    def test_28_metrics_protects_raw_receipt_from_overwrite(self):
        with self.assertRaisesRegex(m.Hold,'OUTPUT_EXISTS'):m.write_once(self.data,{'state':'FAKE'})
    def test_29_metrics_timestamp_timezone_required(self):
        r=self.metrics['observations'][0];p=Path(r['sourcePath']);v=json.loads(p.read_bytes());v['observedAt']='2026-10-24T12:00:00';p.write_bytes(m.canonical(v));r['sourceSha256']=m.sha(p.read_bytes())
        with self.assertRaisesRegex(m.Hold,'TIME_FORMAT'):m.metrics(self.metrics)
    def test_30_metrics_duplicate_json_field_rejected(self):
        with self.assertRaisesRegex(m.Hold,'DUPLICATE_JSON_KEY'):m.parse(b'{"schema":1,"schema":2}')

if __name__=='__main__':unittest.main()
