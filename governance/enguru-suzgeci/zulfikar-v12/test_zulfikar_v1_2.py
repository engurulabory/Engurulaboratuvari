#!/usr/bin/env python3
"""Independent test definitions for Zulfikar V1.2 offline design oracle."""
import copy
import random
import unittest
from zulfikar_v1_2_engine import *

S='a'*64

def golden():
    return {
        'Z02_EVENT':{'event_id':'E-101','task_id':'T-101','owner':'reviewer-1',
           'source_uri':'fixture://event/101','provenance_digest':S,'observed_at':'2026-10-25T12:00:00+03:00',
           'outcome':'FAILURE','cause_status':'HYPOTHESIS','promote_as_success':False},
        'Z03_TRANSFER':{'family':'code-review','cohort_frozen_before_results':True,
            'cohort':[{'task_id':f'T-{i}','family':'code-review','baseline_evidence':f'fixture://base/{i}',
            'candidate_evidence':f'fixture://after/{i}','author_id':'author-x','reviewer_id':f'reviewer-{i}',
            'baseline_effort':50+i,'candidate_effort':40+i,'independent_reviewed':True,
            'regression':False,'real_task_observed':True} for i in (1,2,3)]},
        'Z04_LINEAGE':{'project_id':'DEMO','target_sha':S,'contract_controls':['D01','D02'],
            'claim_scope':'DEMO_SCOPE','contract_scope':'DEMO_SCOPE',
            'chain':[{'stage':v,'project_id':'DEMO','source_sha':S,'control_id':'D01',
                    'evidence_ref':f'fixture://lineage/{v}'} for v in CHAIN]},
        'Z05_BENCHMARK':{'task_manifest_sha':S,'input_manifest_sha':S,'rubric_sha':S,
           'peer_id':'Peer-X','candidate_id':'Zulfikar', 'same_task':True,'same_inputs':True,
           'equalized_budget':True,'metric_equivalence':True,'environment_disclosed':True,
           'versions_pinned':True,'capability_parity_or_limitations_reported':True,
           'blinded_grader':True,'all_trials_accounted':True,'real_peer_execution':True,
           'trials':[{'trial_id':f'P-{i}','candidate_proof':f'fixture://candidate/{i}',
             'peer_proof':f'fixture://peer/{i}','candidate_measure':20+i,'peer_measure':21+i}
             for i in range(5)]},
        'Z08_IMPACT':{'user_goal':'shorter task completion','metric':'task_minutes','unit':'min',
           'baseline_evidence':'fixture://impact/before','after_evidence':'fixture://impact/after',
           'observed_at_baseline':'2026-10-01','observed_at_after':'2026-10-25',
           'privacy_review':'fixture://privacy','real_users_observed':True,'matched_cohort':True,
           'baseline':60,'after':40,'direction':'lower_is_better'},
        'Z10_CONCURRENCY':{'active_writer_count':1,'writer_id':'work-owner-1','authorized_writer_id':'work-owner-1',
           'snapshot_sha':S,'expected_snapshot_sha':S,'lease_current':True,'idempotency_verified':True,
           'rollback_checkpoint':'fixture://rollback','work_session_mutation_allowed':False},
        'Z10_SAFE_FIN':{'k_gates':{f'K{i}':True for i in range(1,8)},
           'unique_controls':True,'evidence_verified':True,'independent_review':True,
           'field_required':True,'field_evidence':True,'human_threshold_required':True,
           'human_authorization':True,'benchmark_claimed':True,'benchmark_real_evidence':True,
           'verified_finish_claim':False},
    }

MUTATIONS=[
 ('Z02_EVENT',lambda x:x.update(outcome='UNVERIFIED'),'wrong event type'),
 ('Z02_EVENT',lambda x:x.update(provenance_digest='b'),'invalid provenance'),
 ('Z02_EVENT',lambda x:x.update(cause_status='EVIDENCE_CONFIRMED',cause_evidence_uri=None),'unproven root cause'),
 ('Z02_EVENT',lambda x:x.update(outcome='FALSE_PASS',promote_as_success=True),'false PASS promoted'),
 ('Z03_TRANSFER',lambda x:x.update(cohort=x['cohort'][:2]),'2 transfer tasks'),
 ('Z03_TRANSFER',lambda x:x.update(cohort_frozen_before_results=False),'cherry picking'),
 ('Z03_TRANSFER',lambda x:x['cohort'][0].update(task_id='T-2'),'duplicate transfer'),
 ('Z03_TRANSFER',lambda x:x['cohort'][1].update(regression=True),'transfer regression'),
 ('Z03_TRANSFER',lambda x:x['cohort'][2].update(candidate_effort=100),'no improvement'),
 ('Z03_TRANSFER',lambda x:x['cohort'][0].update(independent_reviewed=False),'review not independent'),
 ('Z03_TRANSFER',lambda x:x['cohort'][0].update(real_task_observed=False),'real observation absent'),
 ('Z04_LINEAGE',lambda x:x['chain'][3].update(source_sha='b'*64),'drift inside chain'),
 ('Z04_LINEAGE',lambda x:x['chain'][4].update(control_id='D89'),'unknown control'),
 ('Z04_LINEAGE',lambda x:x['chain'][1].update(project_id='OTHER'),'cross project contamination'),
 ('Z04_LINEAGE',lambda x:x.update(claim_scope='WIDER'),'scope drift'),
 ('Z04_LINEAGE',lambda x:x['chain'][8].update(evidence_ref=''),'missing end proof'),
 ('Z04_LINEAGE',lambda x:x['chain'].pop(),'missing authority hop'),
 ('Z05_BENCHMARK',lambda x:x.update(real_peer_execution=False),'comparison only researched'),
 ('Z05_BENCHMARK',lambda x:x.update(peer_id='Zulfikar'),'self comparator'),
 ('Z05_BENCHMARK',lambda x:x.update(same_inputs=False),'unequal input'),
 ('Z05_BENCHMARK',lambda x:x.update(equalized_budget=False),'unequal budget'),
 ('Z05_BENCHMARK',lambda x:x.update(blinded_grader=False),'nonblind judge'),
 ('Z05_BENCHMARK',lambda x:x.update(trials=x['trials'][:4]),'inadequate peer trials'),
 ('Z05_BENCHMARK',lambda x:x['trials'][2].update(peer_proof=None),'unproven peer outcome'),
 ('Z05_BENCHMARK',lambda x:x['trials'][0].update(trial_id='P-1'),'duplicate paired trial'),
 ('Z05_BENCHMARK',lambda x:x.update(versions_pinned=False),'unversioned peers'),
 ('Z08_IMPACT',lambda x:x.update(real_users_observed=False),'fabricated user value'),
 ('Z08_IMPACT',lambda x:x.update(after=70),'no value improvement'),
 ('Z08_IMPACT',lambda x:x.update(matched_cohort=False),'unmatched cohort'),
 ('Z08_IMPACT',lambda x:x.update(after_evidence=None),'missing measured after'),
 ('Z08_IMPACT',lambda x:x.update(privacy_review=None),'privacy gap'),
 ('Z10_CONCURRENCY',lambda x:x.update(active_writer_count=2),'conflicting writers'),
 ('Z10_CONCURRENCY',lambda x:x.update(writer_id='intruder'),'unauthorized writer'),
 ('Z10_CONCURRENCY',lambda x:x.update(snapshot_sha='b'*64),'snapshot drift'),
 ('Z10_CONCURRENCY',lambda x:x.update(lease_current=False),'lease expired'),
 ('Z10_CONCURRENCY',lambda x:x.update(idempotency_verified=False),'replay unverified'),
 ('Z10_CONCURRENCY',lambda x:x.update(rollback_checkpoint=None),'no rollback checkpoint'),
 ('Z10_CONCURRENCY',lambda x:x.update(work_session_mutation_allowed=True),'Work write collision'),
 ('Z10_SAFE_FIN',lambda x:x['k_gates'].update(K6=False),'canonical gate open'),
 ('Z10_SAFE_FIN',lambda x:x.update(independent_review=False),'second look missing'),
 ('Z10_SAFE_FIN',lambda x:x.update(field_evidence=False),'field missing'),
 ('Z10_SAFE_FIN',lambda x:x.update(human_authorization=False),'human missing'),
 ('Z10_SAFE_FIN',lambda x:x.update(evidence_verified=False),'evidence missing'),
 ('Z10_SAFE_FIN',lambda x:x.update(benchmark_real_evidence=False),'unsupported peer superiority'),
 ('Z10_SAFE_FIN',lambda x:x.update(verified_finish_claim=True),'unauthorized finished claim'),
]


def design_contract():
    return {
      'closure_ids':list(CHECKS.keys()),
      'proof_mapping':{cid:{'positive_case':f'good:{cid}','negative_case':f'bad:{cid}',
                  'fixed_scope':'10 categories / 93-point original baseline / 7 missing elements',
                  'oracle':f'check_{cid.lower()}'} for cid in CHECKS},
    }

class TestSim1Golden(unittest.TestCase):
    def test_01_positive_policy_paths(self):
        fixtures=golden()
        for name,fn in CHECKS.items():
            with self.subTest(name=name):self.assertEqual(fn(fixtures[name]),[])
        result=assess(fixtures)
        self.assertEqual(result['state'],'SIMULATED_DESIGN_READY_TO_REQUEST_REVIEW')
        self.assertEqual(result['official_verdict'],'NOT_EVALUATED')
        self.assertFalse(result['eligible_for_automatic_signature'])

    def test_02_new_design_rubric_requires_7_evidenced_mappings(self):
        r=evaluate_design_coverage(design_contract(),True)
        self.assertEqual(r['provisional'],100)
        self.assertEqual(r['design_coverage'],'DESIGN_CANDIDATE_100_OF_100')
        self.assertEqual(r['official_verified_finish'],'HOLD_NOT_AUTHORIZED')

    def test_03_any_missing_map_keeps_93(self):
        for key in CHECKS:
            c=design_contract();del c['proof_mapping'][key]
            with self.subTest(key=key): self.assertEqual(evaluate_design_coverage(c,True)['provisional'],93)

    def test_04_unrun_tests_keep_93(self):
        self.assertEqual(evaluate_design_coverage(design_contract(),False)['provisional'],93)

class TestSim2Mutation(unittest.TestCase):
    def test_targeted_all_45_negative_paths(self):
        base=golden()
        for key,mut,reason in MUTATIONS:
            c=copy.deepcopy(base);mut(c[key]);got=assess(c)
            with self.subTest(reason=reason):
                self.assertEqual(got['state'],'SIMULATED_HOLD')
                self.assertTrue(got['holds'].get(key))
                self.assertFalse(got['eligible_for_automatic_signature'])
                self.assertEqual(got['official_verdict'],'NOT_EVALUATED')

class TestSchemaResistance(unittest.TestCase):
    def test_schema_512_malformed_fixtures_fail_closed(self):
        rng=random.Random(2663)
        for i in range(512):
            case=golden();key=rng.choice(list(CHECKS))
            case[key]=rng.choice([None, '', 14, [], True])
            a=assess(case)
            with self.subTest(i=i):
                self.assertEqual(a['state'],'SIMULATED_HOLD')
                self.assertEqual(a['official_verdict'],'NOT_EVALUATED')

    def test_non_dictionary_top_level_fail_closed(self):
        for c in (None,True,[],12,'bad'):
            self.assertEqual(assess(c)['state'],'SIMULATED_HOLD')

class TestSim3Stress(unittest.TestCase):
    def test_replay_3072_mutated_cases(self):
        rng=random.Random(20261025)
        for i in range(3072):
            base=golden()
            selections=rng.sample(MUTATIONS,k=rng.randint(1,7))
            for key,mut,reason in selections:
                # Some conflicts mutate same families; each mutation must induce HOLD or preserve a prior HOLD.
                try: mut(base[key])
                except (IndexError,KeyError): pass
            r1=assess(base);r2=assess(copy.deepcopy(base))
            with self.subTest(i=i):
                self.assertEqual(r1,r2)
                self.assertEqual(r1['state'],'SIMULATED_HOLD')
                self.assertEqual(r1['official_verdict'],'NOT_EVALUATED')

if __name__=='__main__': unittest.main(verbosity=2)