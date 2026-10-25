import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from tools import pilive_core_snapshot_adapter_v1 as a
from tools import pilive_portfolio_probe_v1 as probe
from test_pilive_core_snapshot_adapter_v1 import fixture

START='2026-10-25T20:00:00Z'
READ='2026-10-25T20:00:01Z'
END='2026-10-25T20:00:02Z'

def portfolio_fixture():
    r,f=fixture();base_entry=r['projects']['plive-p02-user-screen'];base_pair=f['plive-p02-user-screen']
    identities=json.loads((Path(__file__).parent/'fixtures/pilive_core_keys_15_v1.json').read_text())['coreKeysAndProjectIds']
    r['projects']={k:{**copy.deepcopy(base_entry),'projectId':pid} for k,pid in identities.items()}
    facts={}
    for key,entry in r['projects'].items():
        pair=copy.deepcopy(base_pair);pair['summary'].update(project=key,projectId=entry['projectId'])
        pair['verify']['project']=key;pair['sourceReadAt']=READ;facts[key]=pair
    identity={'revision_before':'a'*40,'revision_after':'a'*40,
      'pins_before':{'governance/p02/STATE.json':'b'*64,'governance/p02/WORKLIST.json':'c'*64},
      'pins_after':{'governance/p02/STATE.json':'b'*64,'governance/p02/WORKLIST.json':'c'*64},
      'source_read_at':START,'adapter_built_at':END}
    return r,facts,identity

def build():
    r,f,i=portfolio_fixture();return a.build_portfolio(r,f,**i)

class PortfolioModelTests(unittest.TestCase):
    def test_all_fifteen_core_fact_pairs_are_projected(self):
        s=build();self.assertEqual(len(s['projects']),15)
        self.assertTrue(all(r['status']=='PASS_CORE_READ_ONLY' for r in s['projects']))
        self.assertEqual(s['factCoverage']['qualifiedCounters'],15)
        self.assertTrue(all(r['officialAcceptance']=='HOLD' and not r['closed'] for r in s['projects']))
    def test_project_timeout_preserves_others_and_never_uses_cache(self):
        r,f,i=portfolio_fixture();f['academy']={'error':'CORE_TIMEOUT','summary':f['academy']['summary']}
        s=a.build_portfolio(r,f,**i);row=next(x for x in s['projects'] if x['key']=='academy')
        self.assertEqual(row['reason'],'CORE_TIMEOUT');self.assertIsNone(row['done'])
        self.assertEqual(s['factCoverage']['qualifiedCounters'],14)
    def test_missing_broken_unknown_and_counter_corruption_isolated(self):
        changes=[lambda f:f.pop('academy'),lambda f:f.update(academy=[]),
          lambda f:f['academy']['summary'].update(stateDigest='d'*64),
          lambda f:f['academy']['verify'].update(countedPass=True)]
        for change in changes:
            r,f,i=portfolio_fixture();change(f);s=a.build_portfolio(r,f,**i)
            self.assertEqual(len(s['projects']),15)
            self.assertEqual(sum(x['status']=='PASS_CORE_READ_ONLY' for x in s['projects']),14)
    def test_unverified_progress_keeps_focus_but_counter_na(self):
        r,f,i=portfolio_fixture();f['academy']['verify']['progressIntegrity']='HOLD'
        row=next(x for x in a.build_portfolio(r,f,**i)['projects'] if x['key']=='academy')
        self.assertIsNone(row['percent']);self.assertEqual(row['activeItem'],'P02.S01.01')
    def test_global_drift_and_extra_facts_still_reject_entire_model(self):
        for kind in ('revision','pins','extra','duplicate'):
            r,f,i=portfolio_fixture()
            if kind=='revision':i['revision_after']='b'*40
            elif kind=='pins':i['pins_after']={'other':'d'*64}
            elif kind=='extra':f['unknown']={}
            else:r['projects']['academy']['projectId']=r['projects']['suzgec_v24']['projectId']
            with self.subTest(kind=kind),self.assertRaises(a.Hold):a.build_portfolio(r,f,**i)
    def test_canonical_pass_is_source_fact_not_authority(self):
        r,f,i=portfolio_fixture();f['academy']['summary']['verifiedFinish']='PASS'
        row=next(x for x in a.build_portfolio(r,f,**i)['projects'] if x['key']=='academy')
        self.assertEqual(row['canonicalFinish'],'PASS');self.assertEqual(row['officialAcceptance'],'HOLD')
    def test_project_read_time_is_separate_and_not_in_digest(self):
        r,f,i=portfolio_fixture();first=a.build_portfolio(r,f,**i)
        for pair in f.values():pair['sourceReadAt']='2026-10-25T20:00:01.5Z'
        second=a.build_portfolio(r,f,**i)
        self.assertEqual(first['projectionDigest'],second['projectionDigest'])
        self.assertNotEqual(first['sourceObservations'],second['sourceObservations'])
        self.assertIsNone(first['uiRenderedAt'])
    def test_future_or_naive_project_time_is_isolated_hold(self):
        for value in ('2026-10-26T00:00:00Z','2026-10-25T20:00:01'):
            r,f,i=portfolio_fixture();f['academy']['sourceReadAt']=value
            s=a.build_portfolio(r,f,**i);self.assertEqual(s['factCoverage']['qualifiedCounters'],14)
    def test_stale_snapshot_has_explicit_age(self):
        s=build();v=a.freshness(s,now='2026-10-25T20:02:00Z',stale_after_seconds=60)
        self.assertEqual(v['state'],'STALE');self.assertEqual(v['sourceAgeSeconds'],120)

class PortfolioReaderTests(unittest.TestCase):
    def test_scope_and_symlink_reader(self):
        for value in ('../outside','/tmp/out','tools/unapproved.py','governance/../out'):
            with self.subTest(value=value),self.assertRaises(ValueError):probe.governed(value)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve();(root/'good').write_text('safe');(root/'link').symlink_to(root/'good')
            result=probe.source_manifest(root,{'good','link'})
            self.assertIn('good',result['pins']);self.assertIn('link',result['errors'])
    def test_strict_json_and_manifest_limits(self):
        for raw in (b'{"x":1,"x":2}',b'{"x":NaN}',b'[]'):
            with self.subTest(raw=raw),self.assertRaises(ValueError):probe.strict_json(raw)
        with self.assertRaises(ValueError):probe.source_manifest(Path('/unused'),set(map(str,range(513))))
    def test_discovery_paths_include_contract_and_schema_only(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve();p=root/'governance/x/A_WORK_CONTRACT_V1.json';p.parent.mkdir(parents=True)
            p.write_text(json.dumps({'schemaContract':'governance/schema.json'}))
            self.assertEqual(probe.contract_inputs(root),{'governance/x/A_WORK_CONTRACT_V1.json','governance/schema.json'})
    def test_core_worker_isolated_and_failure_is_hold(self):
        with patch.object(probe.subprocess,'run',return_value=SimpleNamespace(returncode=1,stdout=b'')) as run:
            with self.assertRaisesRegex(ValueError,'CORE_API_FAILURE'):probe.core_call('/scope','project','/tmp','academy')
        self.assertIn('-I',run.call_args.args[0]);self.assertIn('-S',run.call_args.args[0])
    def test_core_failure_detail_stays_private_not_in_screen_model(self):
        proc=SimpleNamespace(returncode=2,stdout=b'',stderr=b'private diagnostic /Users/example')
        with patch.object(probe.subprocess,'run',return_value=proc):
            with self.assertRaises(probe.CoreAPIHold) as caught:probe.core_call('/scope','project','/tmp','academy')
        r,f,i=portfolio_fixture();f['academy']={'error':'CORE_API_FAILURE','privateDiagnostic':caught.exception.diagnostic}
        model=a.build_portfolio(r,f,**i)
        self.assertNotIn('/Users/',json.dumps(model));self.assertIn('/Users/',caught.exception.diagnostic['stderrTail'])
        self.assertEqual(model['factCoverage']['qualifiedCounters'],14)
    def test_portfolio_manifest_drift_does_not_publish_snapshot(self):
        r,_,_=portfolio_fixture();empty={'pins':{'x':'b'*64},'errors':{}}
        changed={'pins':{'x':'c'*64},'errors':{}}
        initial=[{'match':True}]
        with patch.object(probe.safe,'core_pin_check',return_value=initial),patch.object(probe,'revision',return_value='a'*40),patch.object(probe,'contract_inputs',return_value=set()),patch.object(probe,'source_manifest',side_effect=[empty,empty,changed]),patch.object(probe,'core_call',return_value=r):
            result=probe.portfolio_read('/test-owned-home','/test-owned-temp')
        self.assertEqual(result['state'],'HOLD_PORTFOLIO_SOURCE_DRIFT');self.assertNotIn('snapshot',result)

if __name__=='__main__':unittest.main()
