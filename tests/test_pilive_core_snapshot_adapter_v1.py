import copy
import unittest
from tools import pilive_core_snapshot_adapter_v1 as p

def fixture():
    registry={'schema':'enguru.progress-core.project-registry/v1','projects':{
      'plive-p02-user-screen':{'projectId':'ENGURU_PLIVE_P02_USER_SCREEN',
                             'state':'governance/p02/STATE.json','worklist':'governance/p02/WORKLIST.json'}}}
    summary={'project':'plive-p02-user-screen','projectId':'ENGURU_PLIVE_P02_USER_SCREEN',
      'total':12,'declaredPass':0,'activeItem':'P02.S01.01','activePackage':'P02.S01',
      'nextAction':'Source reconciliation','verifiedFinish':'HOLD','stateDigest':'b'*64,'worklistDigest':'c'*64}
    verify={k:'PASS' for k in ('worklist','state','itemSetAgreement','singleActivePackage',
      'singleActiveItem','deterministicProjection','evidenceQualification','progressIntegrity')}
    verify.update(project='plive-p02-user-screen',stateDrift='NONE',countedPass=0,
      declaredPass=0,evidencedPass=0,unverifiedPass=0,finishState='HOLD')
    return registry,{'plive-p02-user-screen':{'summary':summary,'verify':verify}}

def run(registry=None,facts=None,**kw):
    r,f=fixture()
    args=dict(revision_before='a'*40,revision_after='a'*40,
      pins_before={'governance/p02/STATE.json':'b'*64,'governance/p02/WORKLIST.json':'c'*64},
      pins_after={'governance/p02/STATE.json':'b'*64,'governance/p02/WORKLIST.json':'c'*64},
      source_read_at='2026-10-25T18:49:20Z',adapter_built_at='2026-10-25T18:49:21Z')
    args.update(kw)
    return p.build(r if registry is None else registry,f if facts is None else facts,**args)

class CoreSnapshotTests(unittest.TestCase):
    def test_dynamic_p02_included_once(self):
        s=run();self.assertEqual(len(s['projects']),1)
        row=s['projects'][0];self.assertEqual((row['done'],row['total'],row['percent']),(0,12,0))
        self.assertEqual(row['activeItem'],'P02.S01.01');self.assertEqual(row['officialAcceptance'],'HOLD')
        self.assertFalse(row['closed']);self.assertEqual(s['verifiedFinish'],'HOLD')
    def test_missing_core_facts_stay_visible(self):
        row=run(facts={})['projects'][0]
        self.assertIsNone(row['done']);self.assertIsNone(row['percent']);self.assertEqual(row['status'],'HOLD')
    def test_core_failure_is_hold_without_cached_counts(self):
        _,f=fixture();f['plive-p02-user-screen']['verify']['progressIntegrity']='HOLD'
        self.assertIsNone(run(facts=f)['projects'][0]['done'])
    def test_boolean_float_out_of_range_counts(self):
        for value in (True,False,0.0,-1,13):
            _,f=fixture();f['plive-p02-user-screen']['verify']['countedPass']=value
            with self.subTest(value=value),self.assertRaises(p.Hold):run(facts=f)
    def test_zero_or_float_denominator(self):
        for total in (0,12.0,True):
            _,f=fixture();f['plive-p02-user-screen']['summary']['total']=total
            with self.subTest(total=total),self.assertRaises(p.Hold):run(facts=f)
    def test_counter_disagreement_or_boolean(self):
        for key,value in [('declaredPass',True),('evidencedPass',1),('unverifiedPass',1)]:
            _,f=fixture();f['plive-p02-user-screen']['verify'][key]=value
            with self.subTest(key=key),self.assertRaises(p.Hold):run(facts=f)
    def test_duplicate_project_id(self):
        r,_=fixture();r['projects']['alias']=copy.deepcopy(r['projects']['plive-p02-user-screen'])
        with self.assertRaises(p.Hold):run(registry=r)
    def test_extra_unknown_facts(self):
        _,f=fixture();f['foreign']=copy.deepcopy(f['plive-p02-user-screen'])
        with self.assertRaises(p.Hold):run(facts=f)
    def test_source_revision_drift(self):
        with self.assertRaises(p.Hold):run(revision_after='b'*40)
    def test_source_pin_drift(self):
        with self.assertRaises(p.Hold):run(pins_after={'state':'d'*64})
    def test_project_source_binding_drift(self):
        _,f=fixture();f['plive-p02-user-screen']['summary']['stateDigest']='d'*64
        with self.assertRaises(p.Hold):run(facts=f)
    def test_cross_project_identity(self):
        _,f=fixture();f['plive-p02-user-screen']['summary']['projectId']='OTHER'
        with self.assertRaises(p.Hold):run(facts=f)
    def test_missing_or_conflicting_active_focus(self):
        _,f=fixture();f['plive-p02-user-screen']['verify']['singleActiveItem']='HOLD'
        self.assertEqual(run(facts=f)['projects'][0]['status'],'HOLD')
        f['plive-p02-user-screen']['verify']['singleActiveItem']='PASS'
        f['plive-p02-user-screen']['summary']['activeItem']=None
        with self.assertRaises(p.Hold):run(facts=f)
    def test_early_verified_finish_rejected(self):
        _,f=fixture();f['plive-p02-user-screen']['verify']['finishState']='VERIFIED'
        with self.assertRaises(p.Hold):run(facts=f)
    def test_even_complete_technical_count_never_issues_acceptance(self):
        _,f=fixture();f['plive-p02-user-screen']['summary']['declaredPass']=12
        f['plive-p02-user-screen']['verify'].update(countedPass=12,declaredPass=12,evidencedPass=12,finishState='VERIFIED')
        s=run(facts=f);self.assertEqual(s['projects'][0]['officialAcceptance'],'HOLD')
        self.assertFalse(s['projects'][0]['closed']);self.assertEqual(s['verifiedFinish'],'HOLD')
    def test_replay_digest_excludes_wall_clock(self):
        self.assertEqual(run()['projectionDigest'],run(adapter_built_at='2026-10-25T18:50:00Z')['projectionDigest'])
    def test_three_timestamps_remain_separate(self):
        s=run();self.assertNotEqual(s['sourceReadAt'],s['adapterBuiltAt']);self.assertIsNone(s['uiRenderedAt'])
        self.assertEqual(s['uiPublication'],'NOT_EXECUTED')
    def test_future_source_or_naive_timestamp(self):
        for kw in ({'source_read_at':'2026-10-26T00:00:00Z'},{'source_read_at':'2026-10-25T00:00:00'}):
            with self.subTest(kw=kw),self.assertRaises(p.Hold):run(**kw)
    def test_freshness_stale_explicit(self):
        s=run();self.assertEqual(p.freshness(s,now='2026-10-25T18:49:21Z',stale_after_seconds=60)['state'],'WITHIN_CALLER_AGE_LIMIT')
        self.assertEqual(p.freshness(s,now='2026-10-25T18:51:00Z',stale_after_seconds=60)['state'],'STALE')
    def test_unordered_core_registry_is_deterministic(self):
        r,f=fixture();r['projects']['alpha']={'projectId':'A'}
        s=run(registry=r,facts=f);r['projects']=dict(reversed(list(r['projects'].items())))
        self.assertEqual(s['projectionDigest'],run(registry=r,facts=f)['projectionDigest'])

if __name__=='__main__':unittest.main()
