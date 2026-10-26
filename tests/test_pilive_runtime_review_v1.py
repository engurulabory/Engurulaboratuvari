import copy
import json
import unittest
from tools import pilive_learning_adapter_v1 as p
from tools.enguru_muhendislik_kasi import IntakeHold

PINS={name:'a'*64 for name in ('tools/enguru_mk_bridge_v1.py','tools/enguru_mk_autopilot_v5.py',
                              'tools/enguru_mk_intelligence_v5.py','tools/enguru_mk_intelligence_github_v5.py')}

def fixture():
    members=[{'member':name,'sha256':pin,'scopeConstants':
              {'TASK':'ENGURU_MK_BRIDGE_PILOT_V1'} if name.endswith('bridge_v1.py') else {}}
             for name,pin in PINS.items()]
    return {'schema':'enguru.pilive.runtime-lineage-observation/v1',
      'packageManifestSha256':'b'*64,'observerSourceCommit':'c'*40,'errors':[],
      **{key:0 for key in ('canonicalWrites','nativeMuscleWrites','sqliteConnections','keychainReads',
                          'networkRequests','runtimeActivations','appLaunches')},
      'agents':[{'label':'com.enguru.mk.bridge.pilot-v5','installedSha256':'d'*64,
        'nonAllowlistedEnvironmentValuesExported':False,
        'launchd':{'returncode':0,'fields':{'state':'active'}},
        'runtimes':[{'installedPinState':'PASS_PIN_MATCH','sha256':'d'*64,'sourceInventory':members}]}],
      'lineage':{'matchedPythonPins':[]},'priorReceiptPairs':[{'state':'HOLD_RECEIPT_COPY'}]}

def review(doc,**changes):
    raw=p.canonical(doc)
    args={'expected_sha':p.digest(raw),'expected_manifest':'b'*64,
          'expected_observer_commit':'c'*40,'expected_v5_members':PINS}
    args.update(changes)
    return p.verify_runtime_receipt(raw,**args)

class RuntimeReviewTests(unittest.TestCase):
    def test_active_never_elevates_pilot_or_finish(self):
        r=review(fixture())
        self.assertTrue(r['v5ActiveAtObservation'])
        self.assertEqual(r['piliveRuntimeIntegration'],'HOLD_SEPARATE_TASK_ADAPTER')
        self.assertEqual(r['verifiedFinish'],'HOLD')
        self.assertEqual(r['scheduleContinuity'],'NOT_PROVEN_BY_LAUNCHD_STATE')
        self.assertEqual(r['canonicalFreshness'],'NOT_RECAPTURED')
    def test_prior_missing_preserved(self):
        r=review(fixture());self.assertEqual((r['priorReceiptPairsPassed'],r['priorReceiptPairsTotal']),(0,1))
    def test_wrong_receipt_pin(self):
        with self.assertRaises(IntakeHold):review(fixture(),expected_sha='e'*64)
    def test_manifest_or_commit_drift(self):
        for k in ('packageManifestSha256','observerSourceCommit'):
            d=fixture();d[k]='e'*len(d[k])
            with self.subTest(k=k),self.assertRaises(IntakeHold):review(d)
    def test_boolean_or_nonzero_write_scope(self):
        for k in ('canonicalWrites','nativeMuscleWrites','sqliteConnections','networkRequests','runtimeActivations'):
            for v in (True,False,1):
                d=fixture();d[k]=v
                with self.subTest(k=k,v=v),self.assertRaises(IntakeHold):review(d)
    def test_source_pin_drift(self):
        d=fixture();d['agents'][0]['runtimes'][0]['sourceInventory'][0]['sha256']='e'*64
        with self.assertRaises(IntakeHold):review(d)
    def test_self_pin_is_not_independent_source_proof(self):
        with self.assertRaises(IntakeHold):review(fixture(),expected_v5_members={})
    def test_pilot_task_reassignment_rejected(self):
        d=fixture();d['agents'][0]['runtimes'][0]['sourceInventory'][0]['scopeConstants']['TASK']=p.TASK_ID
        with self.assertRaises(IntakeHold):review(d)
    def test_duplicate_agent_or_member_rejected(self):
        for where in ('agent','member'):
            d=fixture();rows=d['agents'] if where=='agent' else d['agents'][0]['runtimes'][0]['sourceInventory']
            rows.append(copy.deepcopy(rows[0]))
            with self.subTest(where=where),self.assertRaises(IntakeHold):review(d)
    def test_python_content_tamper_rejected(self):
        d=fixture();d['lineage']['matchedPythonPins']=[{'pinName':'projection_v6.py','contentUtf8':'tamper','sha256':'a'*64,'path':'/private/example'}]
        with self.assertRaises(IntakeHold):review(d)
    def test_unloaded_and_failure_are_not_active(self):
        for code,state in ((113,'active'),(0,'waiting'),(False,'active')):
            d=fixture();d['agents'][0]['launchd']={'returncode':code,'fields':{'state':state}}
            self.assertFalse(review(d)['v5ActiveAtObservation'])
    def test_sanitized_output_and_candidates(self):
        d=fixture();d['privateExtra']='/Users/private/path'
        self.assertNotIn('/Users/',json.dumps(review(d)))
        for fact in ('RUNTIME_SCOPE_RECONCILED','BUNDLED_SOURCE_RUNTIME_BOUNDARY','RECEIPT_LOCATION_BOUNDARY'):
            record,r=p.review_candidate('# ENGÜRÜ OSi × ChatGPT — Mühendislik Kası™\n',fact_id=fact,source_sha256='a'*64,
              observed_at='2026-10-25T17:44:27Z',correlation_id='OSIBLOCK-PILIVE-RUNTIME')
            self.assertNotIn('/Users/',record);self.assertEqual(r['productGatesModified'],0)

if __name__=='__main__':unittest.main()
