import copy
import json
from pathlib import Path
import random
import unittest
from tools import pilive_core_snapshot_adapter_v1 as adapter
from tools import pilive_learning_adapter_v1 as learning
from test_pilive_core_snapshot_adapter_v1 import fixture, run

def native_identity_fixture():
    data=json.loads((Path(__file__).parent/'fixtures/pilive_core_keys_15_v1.json').read_text())
    registry,facts=fixture()
    p02=registry['projects']['plive-p02-user-screen']
    registry['projects']={k:{'projectId':v} for k,v in data['coreKeysAndProjectIds'].items()}
    registry['projects']['plive-p02-user-screen']=p02
    return registry,facts

class CanonicalKeyTests(unittest.TestCase):
    def test_all_fifteen_native_identities_preserved(self):
        registry,facts=native_identity_fixture();model=run(registry=registry,facts=facts)
        self.assertEqual(len(model['projects']),15)
        self.assertEqual({r['key'] for r in model['projects']},set(registry['projects']))
        self.assertEqual(len({r['projectId'] for r in model['projects']}),15)
    def test_underscore_key_and_project_id_are_separate(self):
        registry,facts=native_identity_fixture();rows=run(registry=registry,facts=facts)['projects']
        row=next(r for r in rows if r['key']=='suzgec_v24')
        self.assertEqual(row['projectId'],'ENGURU_SUZGEC_V24')
        self.assertEqual(row['status'],'HOLD');self.assertIsNone(row['done'])
    def test_p02_is_single_exact_count_and_active_focus(self):
        registry,facts=native_identity_fixture();rows=run(registry=registry,facts=facts)['projects']
        p02=[r for r in rows if r['projectId']=='ENGURU_PLIVE_P02_USER_SCREEN']
        self.assertEqual(len(p02),1);self.assertEqual((p02[0]['done'],p02[0]['total']),(0,12))
        self.assertEqual(p02[0]['activeItem'],'P02.S01.01')
        self.assertEqual(p02[0]['officialAcceptance'],'HOLD');self.assertFalse(p02[0]['closed'])
    def test_missing_p02_facts_stay_visible_on_hold(self):
        registry,_=native_identity_fixture();rows=run(registry=registry,facts={})['projects']
        self.assertEqual(len(rows),15);self.assertTrue(all(r['status']=='HOLD' for r in rows))
    def test_missing_and_extra_project_sets_are_hold(self):
        registry,facts=native_identity_fixture();expected=[r['projectId'] for r in registry['projects'].values()]
        for change in ('missing','extra'):
            altered=copy.deepcopy(registry)
            if change=='missing':del altered['projects']['suzgec_v24']
            else:altered['projects']['unknown_test_project']={'projectId':'UNKNOWN_TEST_PROJECT'}
            rows=run(registry=altered,facts=facts)['projects']
            self.assertEqual(learning.project_set_evidence(expected,[r['projectId'] for r in rows])['state'],'HOLD_PROJECT_SET')
    def test_duplicate_project_identity_rejected(self):
        registry,facts=native_identity_fixture();registry['projects']['alias_test']=registry['projects']['suzgec_v24']
        with self.assertRaisesRegex(adapter.Hold,'HOLD_PROJECT_ID'):run(registry=registry,facts=facts)
    def test_unsafe_and_mixed_type_keys_are_exact_hold(self):
        unsafe=['../suzgec_v24','/tmp/x','suzgec/v24','suzgec.v24','suzgec%5fv24',
                'suzgec v24','suzgec_v24\n','süzgec_v24','SUZGEC_V24','_v24','-v24','',1,None,True,'a'*129]
        for key in unsafe:
            registry,_=native_identity_fixture();registry['projects'][key]={'projectId':'UNSAFE_TEST'}
            with self.subTest(key=key),self.assertRaisesRegex(adapter.Hold,'HOLD_PROJECT_KEY'):
                run(registry=registry,facts={})
    def test_unknown_fact_key_is_hold(self):
        registry,facts=native_identity_fixture();facts['unknown_test']={}
        with self.assertRaisesRegex(adapter.Hold,'HOLD_EXTRA_PROJECT_FACTS'):run(registry=registry,facts=facts)
    def test_key_project_id_substitution_is_hold(self):
        registry,facts=native_identity_fixture();registry['projects']['plive-p02-user-screen']['projectId']='plive-p02-user-screen'
        with self.assertRaisesRegex(adapter.Hold,'HOLD_CORE_PROJECT_DRIFT'):run(registry=registry,facts=facts)
    def test_source_or_revision_drift_remains_hold(self):
        registry,facts=native_identity_fixture()
        for changes in ({'revision_after':'b'*40},{'pins_after':{'changed':'d'*64}}):
            with self.subTest(changes=changes),self.assertRaises(adapter.Hold):run(registry=registry,facts=facts,**changes)
    def test_fifteen_project_order_is_deterministic(self):
        registry,facts=native_identity_fixture();expected=run(registry=registry,facts=facts)['projectionDigest']
        rng=random.Random(20261025)
        for _ in range(20):
            items=list(registry['projects'].items());rng.shuffle(items);registry['projects']=dict(items)
            self.assertEqual(run(registry=registry,facts=facts)['projectionDigest'],expected)

if __name__=='__main__':unittest.main()
