"""Heterogeneous task, adversity and repair evidence tests. Local and fail-closed."""
from __future__ import annotations
import copy
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from proof_chain import audit_evidence, assess_three_phase_runs, finish_readiness, PHASES
from engine import Contract, audit_real_work_handoff


class TruthBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.phase_tmp = tempfile.TemporaryDirectory()
        cls.phase_dir = Path(cls.phase_tmp.name)
        cls.phase_prepared = []
        # Three genuinely different child processes, once for the shared pilot.
        for phase, value, exit_code in [(PHASES[0], 'initial-defect', 1),
                                         (PHASES[1], 'fault-recovered', 0),
                                         (PHASES[2], 'repaired-and-tested', 0)]:
            name = phase.lower() + '.json'
            run = subprocess.run([sys.executable, '-B', '-c',
              'import json,sys,pathlib; phase=sys.argv[2];c=int(sys.argv[4]);d={"phase":phase,"observed":sys.argv[3],"goalId":sys.argv[5],"runId":"run-"+phase,"exitCode":c,"processObserved":True};d.update(({"taskOutcome":False} if phase=="REAL_TASK" else ({"faultInjected":True,"faultObserved":True,"faultKind":"SIMULATED_RESTART","recoveryObserved":True} if phase=="ADVERSARIAL_RECOVERY" else {"taskOutcome":True,"regressionClear":True})));pathlib.Path(sys.argv[1]).write_text(json.dumps(d));sys.exit(c)',
              str(cls.phase_dir / name), phase, value, str(exit_code), 'PILIVE-SAMPLE-01'],
              capture_output=True, timeout=10, check=False)
            cls.phase_prepared.append((phase, name, run.returncode))

    @classmethod
    def tearDownClass(cls):
        cls.phase_tmp.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.goal = 'PILIVE-SAMPLE-01'
        self.files = {}
        for name, value in [('sourceA', 'unique proof A'), ('sourceB', 'unique proof B'),
                            ('sourceC', 'unique proof C')]:
            path = self.base / f'{name}.json'
            path.write_text(json.dumps({'evidence': value}), encoding='utf8')
            self.files[name] = path
        self.requirements = {
            'WORKING': {'kinds': ['SOURCE', 'EXECUTION'], 'minRoots': 2},
            'REVIEW': {'kinds': ['INDEPENDENT_REVIEW'], 'minRoots': 1},
        }
        self.bindings = [self.binding('sourceA', 'WORKING', 'SOURCE', 'root-source'),
                         self.binding('sourceB', 'WORKING', 'EXECUTION', 'root-exec'),
                         self.binding('sourceC', 'REVIEW', 'INDEPENDENT_REVIEW', 'root-review')]

    def binding(self, file, criterion, kind, root):
        return {'evidenceId': file + '-' + criterion + '-' + kind,
                'goalId': self.goal, 'criterionId': criterion, 'kind': kind,
                'provenanceRoot': root, 'relativePath': self.files[file].name,
                'contentSha256': hashlib.sha256(self.files[file].read_bytes()).hexdigest()}

    def audit(self, overrides=None, criteria=None):
        return audit_evidence(self.base, criteria or self.requirements,
                              self.bindings if overrides is None else overrides, goal_id=self.goal)

    def runs(self):
        prepared = []
        for phase, fname, code in self.phase_prepared:
            shutil.copyfile(self.phase_dir / fname, self.base / fname)
            event = dict(goalId=self.goal, phase=phase, runId='run-'+phase,
                         processObserved=True, exitCode=code, relativePath=fname,
                         artifactSha256=hashlib.sha256((self.base / fname).read_bytes()).hexdigest())
            prepared.append(event)
        prepared[0]['taskOutcome'] = False
        prepared[1].update(faultInjected=True, faultObserved=True,
                           faultKind='SIMULATED_RESTART', recoveryObserved=True)
        prepared[2].update(taskOutcome=True, regressionClear=True)
        return prepared

    def test_a01_real_files_verified_and_three_origins(self):
        r = self.audit()
        self.assertEqual(r['state'], 'EVIDENCE_READY_FOR_EXTERNAL_REVIEW')
        self.assertEqual((r['criteriaMet'], r['criteriaTotal']), (2,2))
        self.assertEqual(r['uniqueContentSources'], 3)
        self.assertFalse(r['officialPassIssued'])

    def test_a02_80_controls_on_39_unique_files_not_80_sources(self):
        c = {f'C{i:02d}': {'kinds':['SOURCE'], 'minRoots': 1} for i in range(80)}
        for i in range(39):
            (self.base / f'f{i}.txt').write_text(f'unique source {i}')
        b=[]
        for i in range(80):
            path = self.base / f'f{i % 39}.txt'
            b.append({'evidenceId': f'e{i}', 'goalId':self.goal,'criterionId':f'C{i:02d}',
                'kind':'SOURCE','provenanceRoot':f'original-{i%39}',
                'relativePath':path.name,'contentSha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        r = audit_evidence(self.base,c,b,goal_id=self.goal)
        self.assertEqual(r['criteriaMet'],80)
        self.assertEqual(r['uniqueContentSources'],39)
        self.assertEqual(r['uniqueProvenanceRoots'],39)
        self.assertEqual(r['duplicateContentBindings'],41)
        self.assertGreater(r['reusedContentAcrossCriteria'],0)
        self.assertFalse(r['officialPassIssued'])

    def test_a03_relabelled_same_source_cannot_fake_two_roots(self):
        b=copy.deepcopy(self.bindings)
        b[1]['relativePath']=b[0]['relativePath']
        b[1]['contentSha256']=b[0]['contentSha256']
        b[1]['provenanceRoot']='pretend-new-root'
        r=self.audit(b)
        self.assertFalse(r['requirements']['WORKING']['met'])
        self.assertEqual(r['requirements']['WORKING']['independentSourceUpperBound'],1)

    def test_a04_identical_source_with_other_filename_not_independent(self):
        path=self.base/'copy.json';path.write_bytes(self.files['sourceA'].read_bytes())
        b=copy.deepcopy(self.bindings)
        b[1]['relativePath']=path.name;b[1]['contentSha256']=b[0]['contentSha256']
        self.assertEqual(self.audit(b)['state'],'EVIDENCE_HOLD')

    def test_a05_tampered_file_not_counted(self):
        self.files['sourceB'].write_text('tampered')
        r=self.audit()
        self.assertEqual(r['state'],'EVIDENCE_HOLD')
        self.assertIn('CONTENT_SHA_MISMATCH', [x['reason'] for x in r['invalid']])

    def test_a06_missing_kind_holds(self):
        b=copy.deepcopy(self.bindings)
        b[1]['kind']='SOURCE'
        self.assertEqual(self.audit(b)['requirements']['WORKING']['missingKinds'],['EXECUTION'])

    def test_a07_duplicate_evidence_id_rejected(self):
        b=copy.deepcopy(self.bindings);b[1]['evidenceId']=b[0]['evidenceId']
        self.assertIn('DUPLICATE_OR_BAD_EVIDENCE_ID',[x['reason'] for x in self.audit(b)['invalid']])

    def test_a08_symlink_proof_refused(self):
        link=self.base/'link.json';link.symlink_to(self.files['sourceB'])
        b=copy.deepcopy(self.bindings);b[1]['relativePath']=link.name
        self.assertEqual(self.audit(b)['state'],'EVIDENCE_HOLD')

    def test_a09_path_escape_refused(self):
        b=copy.deepcopy(self.bindings);b[0]['relativePath']='../x'
        self.assertEqual(self.audit(b)['state'],'EVIDENCE_HOLD')

    def test_a10_goal_change_invalidates_evidence(self):
        b=copy.deepcopy(self.bindings);b[1]['goalId']='ANOTHER-GOAL'
        self.assertEqual(self.audit(b)['state'],'EVIDENCE_HOLD')

    def test_b01_real_three_distinct_subprocess_observations(self):
        r=assess_three_phase_runs(self.base, self.runs(), goal_id=self.goal)
        self.assertEqual(r['state'],'THREE_PHASE_LOCAL_PROOF_CANDIDATE')
        self.assertEqual(r['uniqueRunIds'],3)
        self.assertEqual(r['uniqueArtifactContent'],3)
        self.assertFalse(r['officialPassIssued'])

    def test_b02_three_repeated_baseline_runs_rejected(self):
        e=self.runs();[x.update(phase=PHASES[0]) for x in e]
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['state'],'EXECUTION_HOLD')

    def test_b03_repeated_run_id_rejected(self):
        e=self.runs();e[1]['runId']=e[0]['runId']
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],'REPEATED_OR_MISSING_RUN_ID')

    def test_b04_no_fault_injection_proof_holds(self):
        e=self.runs();e[1]['faultInjected']=False
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],'RUN_RECEIPT_OUTCOME_OR_FAULT_DRIFT')

    def test_b05_unrecovered_fault_holds(self):
        e=self.runs();e[1]['recoveryObserved']=False
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['state'],'EXECUTION_HOLD')

    def test_b06_repaired_run_nonzero_exit_holds(self):
        e=self.runs();e[2]['exitCode']=17
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],'RUN_RECEIPT_PROCESS_OR_EXIT_DRIFT')

    def test_b07_tamper_artifact_after_test_holds(self):
        e=self.runs();(self.base/e[2]['relativePath']).write_text('unexpected change')
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],'RUN_ARTIFACT_MISMATCH')

    def test_b09_relabelled_old_phase_artifact_is_rejected(self):
        e=self.runs()
        # Fake three phase labels without the corresponding phase receipt bytes.
        e[1]['relativePath']=e[0]['relativePath']
        e[1]['artifactSha256']=e[0]['artifactSha256']
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],
                         'RUN_RECEIPT_IDENTITY_MISMATCH')

    def test_b10_claimed_other_task_using_same_bytes_rejected(self):
        e=self.runs()
        e[2]['goalId']='NEW-GOAL'
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],
                         'PHASE_OR_GOAL_MISMATCH')

    def test_b08_wrong_goal_holds(self):
        e=self.runs();e[0]['goalId']='DIFFERENT'
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],'PHASE_OR_GOAL_MISMATCH')

    def test_d01_claim_success_receipt_says_failure_is_hold(self):
        e=self.runs()
        data=json.loads((self.base/e[2]['relativePath']).read_text())
        data['taskOutcome']=False
        (self.base/e[2]['relativePath']).write_text(json.dumps(data))
        e[2]['artifactSha256']=hashlib.sha256((self.base/e[2]['relativePath']).read_bytes()).hexdigest()
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],
                         'RUN_RECEIPT_OUTCOME_OR_FAULT_DRIFT')

    def test_d02_claim_recovery_receipt_says_no_recovery_is_hold(self):
        e=self.runs()
        path=self.base/e[1]['relativePath']
        data=json.loads(path.read_text()); data['recoveryObserved']=False
        path.write_text(json.dumps(data));e[1]['artifactSha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],
                         'RUN_RECEIPT_OUTCOME_OR_FAULT_DRIFT')

    def test_d03_claim_exit_zero_receipt_exit_failure_is_hold(self):
        e=self.runs()
        path=self.base/e[2]['relativePath']
        data=json.loads(path.read_text());data['exitCode']=9
        path.write_text(json.dumps(data));e[2]['artifactSha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],
                         'RUN_RECEIPT_PROCESS_OR_EXIT_DRIFT')

    def test_d04_claim_regression_clear_receipt_says_false_is_hold(self):
        e=self.runs();path=self.base/e[2]['relativePath']
        data=json.loads(path.read_text());data['regressionClear']=False
        path.write_text(json.dumps(data));e[2]['artifactSha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],
                         'RUN_RECEIPT_OUTCOME_OR_FAULT_DRIFT')

    def test_d05_receipt_process_not_observed_is_hold(self):
        e=self.runs();path=self.base/e[0]['relativePath']
        data=json.loads(path.read_text());data['processObserved']=False
        path.write_text(json.dumps(data));e[0]['artifactSha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(assess_three_phase_runs(self.base,e,goal_id=self.goal)['reason'],
                         'RUN_RECEIPT_PROCESS_OR_EXIT_DRIFT')

    def _finish(self, **kwargs):
        d=dict(goal_id=self.goal, evidence_audit=self.audit(),
               three_phase=assess_three_phase_runs(self.base,self.runs(),goal_id=self.goal),
               observed_working_result=True,
               independent_review={'goalId':self.goal,'reviewerId':'reviewer','executorId':'executor'},
               owner_decision={'goalId':self.goal,'decision':'PASS'},
               donecheck={'goalId':self.goal,'status':'PASS'}, existing_authority_verifier=lambda *_:True)
        d.update(kwargs)
        return finish_readiness(**d)

    def test_c00_existing_engine_handoff_uses_one_goal_and_no_issuer(self):
        source = self.files['sourceA']
        contract = Contract(self.goal, 'PiLive example', 'T01', ('WORKING','REVIEW'),
                            hashlib.sha256(source.read_bytes()).hexdigest())
        report = audit_real_work_handoff(contract,self.base,self.requirements,
                                         self.bindings,self.runs(), observed_working_result=True)
        self.assertEqual(report['goalId'],self.goal)
        self.assertEqual(report['evidence']['criteriaMet'],2)
        self.assertEqual(report['realExecution']['observedRuns'],3)
        self.assertEqual(report['finish']['state'],'FINISH_HOLD')
        self.assertEqual(report['nextAction'],'REPAIR_MISSING_REAL_EVIDENCE')
        self.assertIn('CROSS_SESSION_COMPLETENESS_PROOF',report['finish']['missing'])
        self.assertFalse(report['stagePassIssued'])

    def test_c01_claimed_pass_without_existing_authority_holds(self):
        r=self._finish(existing_authority_verifier=None)
        self.assertEqual(r['state'],'FINISH_HOLD')
        self.assertIn('EXISTING_AUTHORITY_BRIDGE',r['missing'])

    def test_c02_reviewer_not_executor(self):
        r=self._finish(independent_review={'goalId':self.goal,'reviewerId':'executor','executorId':'executor'})
        self.assertIn('REVIEWER_SEPARATION',r['missing'])

    def test_c03_missing_owner_cannot_finish(self):
        r=self._finish(owner_decision=None)
        self.assertIn('OWNER_DECISION_RECORD',r['missing'])

    def test_c04_missing_donecheck_cannot_finish(self):
        r=self._finish(donecheck=None)
        self.assertIn('OFFICIAL_DONECHECK_RECORD',r['missing'])

    def test_c05_authority_bridge_refuses_record(self):
        r=self._finish(existing_authority_verifier=lambda *_:False)
        self.assertEqual(r['state'],'FINISH_HOLD')

    def test_c06_verified_external_records_do_not_issue_new_authority(self):
        r=self._finish()
        self.assertEqual(r['state'],'EXTERNAL_BRIDGE_RESPONSE_CANDIDATE_NOT_ISSUED')
        self.assertFalse(r['verifiedFinishIssued'])
        self.assertIsNone(r['acceptedScore'])

    def test_c07_missing_working_user_result_holds(self):
        r=self._finish(observed_working_result=False)
        self.assertIn('WORKING_USER_RESULT',r['missing'])

    def test_c08_wrong_goal_run_cannot_be_reused_for_finish(self):
        d=assess_three_phase_runs(self.base,self.runs(),goal_id=self.goal)
        d['goalId']='OTHER'
        r=self._finish(three_phase=d)
        self.assertIn('REAL_THREE_PHASE_EXECUTION',r['missing'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
