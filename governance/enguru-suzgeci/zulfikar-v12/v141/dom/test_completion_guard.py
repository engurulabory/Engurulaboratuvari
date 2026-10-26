"""Adversarial tests for LLM completion overclaims, fresh review and stage holds."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from engine import Contract, audit_real_work_handoff
from completion_guard import audit_completion_claim


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CompletionGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root/'goal.txt'
        self.source.write_text('fixed original goal')
        self.contract = Contract('USER-GOAL-1','All ten original acceptance requirements','T01',
            tuple('C%02d'%i for i in range(1,11)),digest(self.source))
        self.result = self.root/'real_result.txt'
        self.result.write_text('output actually observed')
        self.checkpoint = self.root/'checkpoint.json'
        self.checkpoint.write_text(json.dumps({'goalId':self.contract.goal_id,'stage':'T01',
            'executionRunId':'run-final-01','resultSha256':digest(self.result)}))
        self.review = self.root/'fresh_review.json'
        self.claim = dict(goalId=self.contract.goal_id,stage='T01',sourceSha256=self.contract.source_pin,
            executorSessionId='session-work',reviewerSessionId='session-independent',
            executorId='worker',reviewerId='external-reviewer',sourcePath=self.source.name,resultPath=self.result.name,
            resultSha256=digest(self.result),reviewPath=self.review.name,
            checkpointPath=self.checkpoint.name,checkpointSha256=digest(self.checkpoint),
            executionRunId='run-final-01',selfReportedScore=100,
            claimedCriteria=list(self.contract.criteria),openItems=[])
        self.review_doc = dict(goalId=self.contract.goal_id,stage='T01',sourceSha256=self.contract.source_pin,
            executorSessionId='session-work',reviewerSessionId='session-independent',
            executorId='worker',reviewerId='external-reviewer',resultSha256=digest(self.result),
            checkpointSha256=digest(self.checkpoint),executionRunId='run-final-01',
            criterionOutcomes={c:True for c in self.contract.criteria},
            unresolvedItems=[],regressionChecked=list(self.contract.criteria),
            negativeCasesCaught=['old-package-corrupted-source-is-rejected'])
        self.save_review()

    def save_review(self):
        self.review.write_text(json.dumps(self.review_doc,sort_keys=True))
        self.claim['reviewSha256']=digest(self.review)

    def audit(self, verifier=None):
        return audit_completion_claim(self.root,self.contract,self.claim,
            independent_session_verifier=verifier)

    def verified(self):
        return self.audit(verifier=lambda *_:True)

    def test_01_missing_fresh_review_blocks_auto_100(self):
        self.assertEqual(audit_completion_claim(self.root,self.contract,None)['state'],'COMPLETION_HOLD')

    def test_02_only_seven_of_ten_claimed_holds(self):
        self.claim['claimedCriteria']=list(self.contract.criteria[:7])
        self.assertIn('ORIGINAL_CRITERIA_COVERAGE',self.verified()['missing'])

    def test_03_new_unsanctioned_criterion_cannot_substitute(self):
        self.claim['claimedCriteria']=list(self.contract.criteria[:9])+['NOT_IN_ORIGINAL_GOAL']
        self.assertIn('ORIGINAL_CRITERIA_COVERAGE',self.verified()['missing'])

    def test_04_70_percent_peer_review_catches_self_reported_100(self):
        for c in self.contract.criteria[7:]:
            self.review_doc['criterionOutcomes'][c]=False
        self.save_review()
        r=self.verified()
        self.assertEqual(r['state'],'COMPLETION_HOLD')
        self.assertEqual(len(r['failedCriteria']),3)
        self.assertIn('CROSS_SESSION_REVIEW_FOUND_GAPS',r['missing'])

    def test_05_same_session_refused(self):
        self.claim['reviewerSessionId']=self.claim['executorSessionId']
        self.assertIn('INDEPENDENT_SESSION_IDENTITY_REQUIRED',self.verified()['missing'])

    def test_06_same_person_refused(self):
        self.claim['reviewerId']=self.claim['executorId']
        self.assertIn('INDEPENDENT_SESSION_IDENTITY_REQUIRED',self.verified()['missing'])

    def test_07_without_external_verifier_is_hold(self):
        self.assertIn('EXTERNAL_SESSION_VERIFIER_REQUIRED',self.audit()['missing'])

    def test_08_external_verifier_refusal_is_hold(self):
        self.assertIn('INDEPENDENT_SESSION_NOT_AUTHENTICATED',self.audit(lambda *_:False)['missing'])

    def test_09_changed_actual_output_is_hold(self):
        self.result.write_text('modified after review')
        self.assertIn('ACTUAL_ARTIFACT_SHA_MISMATCH',self.verified()['missing'])

    def test_10_changed_review_file_is_hold(self):
        self.review.write_text('tampered')
        self.assertIn('ACTUAL_ARTIFACT_SHA_MISMATCH',self.verified()['missing'])

    def test_11_review_wrong_source_is_hold(self):
        self.review_doc['sourceSha256']='f'*64;self.save_review()
        self.assertIn('INDEPENDENT_REVIEW_IDENTITY_DRIFT',self.verified()['missing'])

    def test_12_open_tasks_never_count_as_100(self):
        self.claim['openItems']=['P02.S01.01']
        self.assertIn('OPEN_ITEMS_REMAIN',self.verified()['missing'])

    def test_13_independent_review_open_defect_holds(self):
        self.review_doc['unresolvedItems']=['real Mac interaction not tested'];self.save_review()
        self.assertIn('REVIEW_UNRESOLVED_ITEMS',self.verified()['missing'])

    def test_14_no_adversarial_negative_control_holds(self):
        self.review_doc['negativeCasesCaught']=[];self.save_review()
        self.assertIn('ADVERSARIAL_NEGATIVE_CONTROL_MISSING',self.verified()['missing'])

    def test_15_missing_regression_check_holds(self):
        self.review_doc['regressionChecked']=list(self.contract.criteria[:-1]);self.save_review()
        self.assertIn('REGRESSION_NOT_ALL_CRITERIA',self.verified()['missing'])

    def test_16_missing_one_peer_criterion_holds(self):
        del self.review_doc['criterionOutcomes']['C10'];self.save_review()
        self.assertIn('REVIEW_CRITERIA_INCOMPLETE',self.verified()['missing'])

    def test_17_happy_path_is_candidate_never_official_pass(self):
        r=self.verified()
        self.assertEqual(r['state'],'CROSS_SESSION_LOCAL_COMPLETENESS_CANDIDATE')
        self.assertIsNone(r['acceptedScore'])
        self.assertFalse(r['stagePassIssued'])
        self.assertFalse(r['verifiedFinishIssued'])

    def test_18_goal_drift_is_hold(self):
        self.claim['goalId']='OTHER'
        self.assertIn('GOAL_OR_GATE_DRIFT',self.verified()['missing'])

    def test_19_self_scored_70_without_100_is_hold(self):
        self.claim['selfReportedScore']=70
        self.assertIn('SELF_SCORE_NOT_COMPLETE',self.verified()['missing'])

    def test_20_symlinked_review_file_is_hold(self):
        link=self.root/'review-link.json'
        link.symlink_to(self.review)
        self.claim['reviewPath']=link.name
        self.assertIn('OUTPUT_OR_REVIEW_UNREADABLE_OR_UNSAFE',self.verified()['missing'])

    def test_21_reused_review_for_older_execution_checkpoint_refused(self):
        self.checkpoint.write_text(json.dumps({'goalId':self.contract.goal_id,'stage':'T01',
            'executionRunId':'run-after-new-repair','resultSha256':digest(self.result)}))
        self.claim['checkpointSha256']=digest(self.checkpoint)
        self.assertIn('LATEST_CHECKPOINT_IDENTITY_DRIFT',self.verified()['missing'])

    def test_22_reviewer_receipt_must_bind_latest_checkpoint(self):
        self.checkpoint.write_text(json.dumps({'goalId':self.contract.goal_id,'stage':'T01',
            'executionRunId':'run-final-01','resultSha256':digest(self.result),'rework':1}))
        self.claim['checkpointSha256']=digest(self.checkpoint)
        self.assertIn('INDEPENDENT_REVIEW_IDENTITY_DRIFT',self.verified()['missing'])

    def test_23_existing_handoff_cannot_skip_fresh_review(self):
        requirements={c:{'kinds':['SOURCE'],'minRoots':1} for c in self.contract.criteria}
        result=audit_real_work_handoff(self.contract,self.root,requirements,[],[],
            observed_working_result=True,independent_review={'goalId':self.contract.goal_id,'reviewerId':'a','executorId':'b'},
            owner_decision={'goalId':self.contract.goal_id},donecheck={'goalId':self.contract.goal_id},
            existing_authority_verifier=lambda *_:True)
        self.assertEqual(result['completion']['state'],'COMPLETION_HOLD')
        self.assertEqual(result['finish']['state'],'FINISH_HOLD')
        self.assertIn('CROSS_SESSION_COMPLETENESS_PROOF',result['finish']['missing'])
        self.assertFalse(result['stagePassIssued'])

    def test_25_changed_original_goal_bytes_are_hold(self):
        self.source.write_text('unapproved revision to the original goal')
        self.assertIn('ORIGINAL_GOAL_SOURCE_CHANGED',self.verified()['missing'])

    def test_26_missing_original_goal_is_hold(self):
        self.source.unlink()
        self.assertIn('ORIGINAL_GOAL_SOURCE_UNREADABLE_OR_UNSAFE',self.verified()['missing'])

    def test_27_source_indirection_is_hold(self):
        alias=self.root/'goal_alias.txt';alias.symlink_to(self.source)
        self.claim['sourcePath']=alias.name
        self.assertIn('ORIGINAL_GOAL_SOURCE_UNREADABLE_OR_UNSAFE',self.verified()['missing'])

    def test_28_narrowed_evidence_acceptance_is_hold(self):
        requirements={c:{'kinds':['SOURCE'],'minRoots':1} for c in self.contract.criteria[:7]}
        result=audit_real_work_handoff(self.contract,self.root,requirements,[],[],
            completion_attestation=self.claim,independent_session_verifier=lambda *_:True)
        self.assertEqual(result['evidence']['state'],'EVIDENCE_HOLD')
        self.assertEqual(result['evidence']['originalCriteriaMismatch']['missing'],
            list(self.contract.criteria[7:]))
        self.assertFalse(result['stagePassIssued'])

    def test_29_substituted_evidence_criterion_is_hold(self):
        requirements={c:{'kinds':['SOURCE'],'minRoots':1} for c in self.contract.criteria[:-1]}
        requirements['OTHER_GOAL_CRITERION']={'kinds':['SOURCE'],'minRoots':1}
        result=audit_real_work_handoff(self.contract,self.root,requirements,[],[],
            completion_attestation=self.claim,independent_session_verifier=lambda *_:True)
        self.assertEqual(result['evidence']['state'],'EVIDENCE_HOLD')
        self.assertEqual(result['evidence']['originalCriteriaMismatch']['missing'],['C10'])
        self.assertEqual(result['evidence']['originalCriteriaMismatch']['extra'],['OTHER_GOAL_CRITERION'])

    def test_30_external_verifier_mutates_goal_mid_review_is_hold(self):
        def reviewer(*_):
            self.source.write_text('changed while reviewing')
            return True
        self.assertIn('SOURCE_OR_RESULT_CHANGED_DURING_EXTERNAL_REVIEW',
            self.audit(reviewer)['missing'])

    def test_31_external_verifier_mutates_output_mid_review_is_hold(self):
        def reviewer(*_):
            self.result.write_text('changed while reviewing')
            return True
        self.assertIn('SOURCE_OR_RESULT_CHANGED_DURING_EXTERNAL_REVIEW',
            self.audit(reviewer)['missing'])

    def test_32_missing_entire_evidence_contract_is_hold_not_crash(self):
        result=audit_real_work_handoff(self.contract,self.root,{},[],[],
            completion_attestation=self.claim,independent_session_verifier=lambda *_:True)
        self.assertEqual(result['evidence']['state'],'EVIDENCE_HOLD')
        self.assertEqual(len(result['evidence']['originalCriteriaMismatch']['missing']),10)
        self.assertEqual(result['finish']['state'],'FINISH_HOLD')

    def test_33_malformed_evidence_list_is_hold_not_crash(self):
        requirements={c:{'kinds':['SOURCE'],'minRoots':1} for c in self.contract.criteria}
        result=audit_real_work_handoff(self.contract,self.root,requirements,None,[],
            completion_attestation=self.claim,independent_session_verifier=lambda *_:True)
        self.assertEqual(result['evidence']['state'],'EVIDENCE_HOLD')
        self.assertFalse(result['stagePassIssued'])

    def test_24_true_local_candidate_still_not_official_finish(self):
        requirements={c:{'kinds':['SOURCE'],'minRoots':1} for c in self.contract.criteria}
        result=audit_real_work_handoff(self.contract,self.root,requirements,[],[],
            completion_attestation=self.claim,independent_session_verifier=lambda *_:True)
        self.assertEqual(result['completion']['state'],'CROSS_SESSION_LOCAL_COMPLETENESS_CANDIDATE')
        self.assertEqual(result['finish']['state'],'FINISH_HOLD')
        self.assertFalse(result['stagePassIssued'])

if __name__=='__main__':
    unittest.main(verbosity=2)
