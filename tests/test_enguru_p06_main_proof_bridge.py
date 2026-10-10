from __future__ import annotations
import copy
import unittest
from tools.enguru_p06_main_proof_bridge import evaluate,MAIN,PR,REQUIRED_G2,REQUIRED_HUMAN,EXPECTED_V7

def fixture():
    g={'state':'PASS_G2_NEW_MAIN_MACHINE_REVALIDATED_OFFICIAL_ISSUER_HOLD',
       'preservation':'PASS','issues':[],
       'expected':{'main':MAIN,'reviewedPr':PR},
       'evidence':{'main':{'head':MAIN,'reviewedPrHead':PR,'tree':'tree','prTree':'tree'},
                   'officialReadOnlyEvaluation':{'authorized':False,'reasons':['HEAD_MISMATCH']}},
       'gates':{k:'PASS' for k in REQUIRED_G2}}
    v={'state':'PASS_DISPOSABLE_ONE_TEST_FIXTURE_COMPATIBILITY_ONLY_G2_OFFICIAL_HOLD',
       'preservation':'PASS','issues':[],
       'source':{'canonicalMain':MAIN},
       'gates':{'FOUR_EXACT_FOCUSED_SUITES':'PASS',
                'HISTORICAL_861_FILE_ADOPTION':'REJECTED',
                'RESTORED_GENERAL_ACTION_BINDING':'HOLD_REJECT_HISTORICAL_AUTHORITY_IMPORT'},
       'tests':{key:{'state':'PASS','discovered':val,'executed':val,'returnCode':0}
                for key,val in EXPECTED_V7.items()}}
    m={'authority':'ENGINEERING_CANDIDATE_ONLY','autoHumanDecision':False,
       'autoVerifiedFinish':False,'scope':'PINNED_BOUNDED_NATIVE_ONLY_NOT_OFFICIAL_ACCEPTANCE',
       'humanThresholdRequires':list(REQUIRED_HUMAN)}
    return g,v,m

class TestP06MainProofBridge(unittest.TestCase):
    def judge(self, mutator=None, head=MAIN):
        g,v,m=fixture()
        if mutator:mutator(g,v,m)
        return evaluate(g,v,m,observed_head=head)
    def test_valid_machine_proof_remains_official_hold(self):
        q=self.judge();self.assertTrue(q['machineProofCandidateReady'])
        self.assertFalse(q['authorizedAcceptedCandidate']);self.assertEqual(q['officialP06DoneCheck'],'HOLD')
        self.assertEqual(q['humanThreshold'],'HOLD');self.assertEqual(q['verifiedFinish'],'HOLD')
    def test_other_head_rejected(self):
        self.assertFalse(self.judge(head='0'*40)['machineProofCandidateReady'])
    def test_source_tree_mismatch_rejected(self):
        self.assertFalse(self.judge(lambda g,v,m:g['evidence']['main'].update(tree='wrong'))['machineProofCandidateReady'])
    def test_missing_native_gate_rejected(self):
        self.assertFalse(self.judge(lambda g,v,m:g['gates'].update(NATIVE_7_OF_7='HOLD'))['machineProofCandidateReady'])
    def test_legacy_issuer_authority_forgery_rejected(self):
        self.assertFalse(self.judge(lambda g,v,m:g['evidence']['officialReadOnlyEvaluation'].update(authorized=True))['machineProofCandidateReady'])
    def test_disposable_test_zero_not_pass(self):
        self.assertFalse(self.judge(lambda g,v,m:v['tests']['EVIDENCE_IO_11'].update(executed=0))['machineProofCandidateReady'])
    def test_v7_861_adoption_rejected(self):
        self.assertFalse(self.judge(lambda g,v,m:v['gates'].update(HISTORICAL_861_FILE_ADOPTION='PASS'))['machineProofCandidateReady'])
    def test_restored_general_authority_rejected(self):
        self.assertFalse(self.judge(lambda g,v,m:v['gates'].update(RESTORED_GENERAL_ACTION_BINDING='PASS'))['machineProofCandidateReady'])
    def test_auto_verified_finish_rejected(self):
        self.assertFalse(self.judge(lambda g,v,m:m.update(autoVerifiedFinish=True))['machineProofCandidateReady'])
    def test_human_threshold_requirement_missing_rejected(self):
        self.assertFalse(self.judge(lambda g,v,m:m['humanThresholdRequires'].remove('EXPLICIT_HUMAN_REVIEW'))['machineProofCandidateReady'])
