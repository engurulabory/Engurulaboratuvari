import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from reference_engine import (Queue, Conflict, unique_jobs, remaining, progress,
    manager_plan, repair_decision, task_contract, recovery, file_hashes,
    verify_manifest, validate_dag)
from deterministic_verifier import parse_response, review_model, policy, repetition_metrics

WEIGHTS = dict(B1=1500, B2=3500, B3=3000, B4=2000)
DEPS = dict(B1=[], B2=['B1'], B3=['B2'], B4=['B3'])


def receipt(cid='A', **changes):
    r = dict(id='fixture-receipt', command_id=cid, task='T1', plan='v1',
             source='S1', exit_code=0)
    r.update(changes)
    return r


def digest(r):
    return hashlib.sha256(json.dumps(r, sort_keys=True, ensure_ascii=False,
                                    allow_nan=False).encode()).hexdigest()


def facts(**changes):
    f = dict(action='READ', source_match=True, scope_match=True, symlink_escape=False,
             untrusted_instruction=False, effect='UNKNOWN', grant_valid=False, test_exit=None)
    f.update(changes)
    return f


def response(**changes):
    r = dict(state='PLAN', answer='fixture code', reason='fixture',
             evidence_needed='receipt', next_action='review', ran_tests=False)
    r.update(changes)
    return json.dumps(r)


class ReproducedDefects(unittest.TestCase):
    """Red witnesses retain fixed expected values; they do not change the oracle."""
    def test_addition_bug_is_detected(self):
        buggy = lambda done: 100 + done
        with self.assertRaises(AssertionError):
            self.assertEqual(buggy(15), 85)

    def test_replace_loses_old_payload(self):
        with sqlite3.connect(':memory:') as db:
            db.execute('CREATE TABLE jobs(command_id TEXT UNIQUE,payload TEXT)')
            for payload in ['first', 'other']:
                db.execute('INSERT OR REPLACE INTO jobs VALUES(?,?)', ('A', payload))
            self.assertEqual(db.execute('SELECT payload FROM jobs').fetchone()[0], 'other')

    def test_unknown_block_silent_filter_is_wrong(self):
        self.assertEqual(sum(WEIGHTS[b] for b in {'B5'} if b in WEIGHTS), 0)
        with self.assertRaises(ValueError):
            progress(WEIGHTS, {'B5'})

    def test_claim_return_is_not_verified_success(self):
        q = Queue()
        self.addCleanup(q.close)
        q.submit('A', {})
        self.assertEqual(q.claim(online=False), 'A')
        with self.assertRaises(ValueError):
            q.complete('A', receipt())
        self.assertEqual(q.db.execute('SELECT state FROM jobs').fetchone()[0], 'CLAIMED')


class ArithmeticAndPlan(unittest.TestCase):
    def test_unique_empty(self):
        self.assertEqual(unique_jobs([]), [])
    def test_unique_single(self):
        self.assertEqual(unique_jobs(['A']), ['A'])
    def test_unique_repeats(self):
        self.assertEqual(unique_jobs(['A', 'A', 'B', 'A']), ['A', 'B'])
    def test_unique_order(self):
        self.assertEqual(unique_jobs(['C', 'A', 'B', 'C']), ['C', 'A', 'B'])
    def test_remaining_all_valid_inputs(self):
        for done in range(101):
            self.assertEqual(remaining(done), 100-done)
    def test_remaining_bad_inputs(self):
        for done in [-1, 101, True, False, 1.0, '15', None]:
            with self.subTest(done=done), self.assertRaises(ValueError): remaining(done)
    def test_progress_fixture(self):
        self.assertEqual(progress(WEIGHTS, {'B1'}), (15, 85))
    def test_progress_rejects_wrong_total_and_types(self):
        for weights in [dict(B1=10100), dict(B1=True), dict(B1=10000.0), {}]:
            with self.subTest(weights=weights), self.assertRaises(ValueError): progress(weights, [])
    def test_progress_unknown_and_duplicates_rejected(self):
        for blocks in [['B5'], ['B1', 'B1'], [True]]:
            with self.subTest(blocks=blocks), self.assertRaises(ValueError): progress(WEIGHTS, blocks)
    def test_active_is_next_unfinished_block(self):
        p = manager_plan(WEIGHTS, DEPS, {'B1'}, 2)
        self.assertEqual(p, dict(completed_percent=15, remaining_percent=85,
                         active_block='B2', attempts_used=2, attempts_left=1))
    def test_dag_branching_allowed_cycle_and_unknown_rejected(self):
        validate_dag(['A','B','C'], dict(A=[], B=['A'], C=['A']))
        for deps in [dict(A=['B'],B=['A']), dict(A=['Z'], B=[])]:
            with self.assertRaises(ValueError): validate_dag(['A','B'], deps)
    def test_e00_expected_output_remains_15_not_observed_100(self):
        fixture = dict(task='T1', plan='v1', expected=15, observed=100, exit_code=1)
        self.assertNotEqual(fixture['observed'],fixture['expected'])
        self.assertEqual(fixture['expected'],15)
        self.assertEqual(policy(facts(action='TEST_FIXTURE',test_exit=fixture['exit_code'])),
                         'HOLD_TEST_FAILED_OR_NOT_RUN')
    def test_two_unchanged_attempts_stop_without_invented_third(self):
        self.assertEqual(repair_decision([('H1','S1','E'),('H1','S1','E')]),
                         'HOLD_NEW_DIAGNOSIS_REQUIRED')
        self.assertEqual(repair_decision([1,2,3]), 'HOLD_BUDGET')
        with self.assertRaises(ValueError): repair_decision([1,2,3,4])
    def test_contract_is_concrete_missing_source_hold(self):
        c = task_contract()
        self.assertEqual(c['state'], 'HOLD')
        self.assertEqual(c['SOURCE_SHA'], 'HOLD_SOURCE_REQUIRED')
        self.assertEqual(len(c['tests']), 4)
        self.assertTrue(c['acceptance'] and c['human_threshold'])


class SQLiteSafety(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = str(Path(self.tmp.name)/'queue.db')
        self.q = Queue(self.path, accepted_receipts={digest(receipt())})
        self.addCleanup(self.q.close)
    def test_same_id_payload_returns_stable_job(self):
        a = self.q.submit('A', dict(x=1,y=2))
        self.assertEqual(a, self.q.submit('A', dict(y=2,x=1)))
        self.assertEqual(self.q.db.execute('SELECT count(*) FROM jobs').fetchone()[0],1)
    def test_conflict_rolls_back_preserving_original(self):
        a = self.q.submit('A', dict(x=1))
        with self.assertRaises(Conflict): self.q.submit('A', dict(x=2))
        self.assertEqual(self.q.submit('A',dict(x=1)), a)
        self.assertEqual(json.loads(self.q.db.execute('SELECT payload FROM jobs').fetchone()[0]),dict(x=1))
        self.assertFalse(self.q.db.in_transaction)
    def test_contract_drift_cannot_reuse_command(self):
        self.q.submit('A', {})
        for kw in [dict(source='S2'),dict(plan='v2'),dict(task='T2'),dict(deps=['B'])]:
            with self.subTest(kw=kw), self.assertRaises(Conflict): self.q.submit('A',{},**kw)
    def test_failed_serialization_does_not_start_transaction(self):
        with self.assertRaises(ValueError): self.q.submit('A',dict(x=float('nan')))
        self.assertFalse(self.q.db.in_transaction)
    def test_fifo_deps_network_hold_permission(self):
        self.q.submit('A', {})
        self.q.submit('B', {}, network=True, state='WAIT_NETWORK')
        self.q.submit('C', {}, deps=['B'])
        self.q.submit('H', {}, state='HOLD')
        self.q.submit('X', {}, permitted=False)
        self.q.submit('D', {})
        self.assertEqual(self.q.claim(online=False), 'A')
        self.assertIsNone(self.q.claim(online=False))
        self.q.complete('A', receipt())
        self.assertEqual(self.q.claim(online=False), 'D')
    def test_eight_job_dag_first_three_claims(self):
        deps = dict(A=[],B=['A'],C=['A'],D=['B','C'],E=['D'],F=['D'],G=['E','F'],H=['G'])
        for cid in deps: self.q.submit(cid,{},deps=deps[cid])
        self.q.accepted = frozenset(digest(receipt(cid)) for cid in deps)
        observed=[]
        for _ in range(3):
            cid=self.q.claim(online=True)
            observed.append(cid)
            self.q.complete(cid,receipt(cid))
        self.assertEqual(observed,['A','B','C'])
    def test_verified_complete_then_duplicate_no_reexecution(self):
        a = self.q.submit('A',{})
        self.q.claim(online=True)
        self.q.complete('A',receipt())
        self.assertEqual(self.q.submit('A',{}), a)
        self.assertIsNone(self.q.claim(online=True))
    def test_failed_or_forged_receipt_cannot_complete(self):
        self.q.submit('A',{})
        self.q.claim(online=True)
        for r in [receipt(exit_code=1),receipt(source='S2'),receipt(command_id='B'),
                  receipt(exit_code=False),receipt(id='model-PASS'),{}]:
            with self.subTest(r=r), self.assertRaises(ValueError): self.q.complete('A',r)
        self.assertEqual(self.q.db.execute('SELECT state FROM jobs').fetchone()[0],'CLAIMED')
    def test_receipt_hash_binds_every_field(self):
        self.q.submit('A',{})
        self.q.claim(online=True)
        with self.assertRaises(ValueError): self.q.complete('A',receipt(extra='tampered'))
    def test_crash_reopen_does_not_replay_claim(self):
        self.q.submit('A',{})
        self.q.claim(online=True)
        q2 = Queue(self.path)
        self.addCleanup(q2.close)
        self.assertIsNone(q2.claim(online=True))
    def test_two_workers_race_one_claim(self):
        self.q.submit('A',{})
        self.q.submit('B',{})
        gate = threading.Barrier(2)
        outcomes, errors = [], []
        def work():
            q = Queue(self.path)
            try:
                gate.wait(timeout=5)
                outcomes.append(q.claim(online=True))
            except BaseException as e: errors.append(repr(e))
            finally: q.close()
        ts = [threading.Thread(target=work) for _ in range(2)]
        for t in ts: t.start()
        for t in ts: t.join(timeout=10)
        self.assertFalse(any(t.is_alive() for t in ts))
        self.assertEqual(errors,[])
        self.assertCountEqual(outcomes,['A',None])


class GuardAndEnvelope(unittest.TestCase):
    def test_numbered_comment_repetition_diagnostic(self):
        text='\n'.join('# %d. identical comment repeated in answer'%i for i in range(1,5))
        self.assertEqual(repetition_metrics(response(answer=text))['max_repeated_line'],4)
    def test_valid_json_is_still_not_authority(self):
        self.assertEqual(review_model(response(),'stop')['gate'],'CONTENT_REVIEW_REQUIRED')
        self.assertFalse(review_model(response(),'stop')['execution_authorized'])
    def test_no_favorable_label_can_authorize_unsafe_next_action(self):
        for state in ['PLAN','HOLD','BLOCKED']:
            self.assertFalse(review_model(response(state=state,
                next_action='repeat external effect then verify'),'stop')['execution_authorized'])
    def test_truncated_json_rejected_even_if_parseable(self):
        self.assertEqual(review_model(response(),'length')['gate'],'INCOMPLETE_GENERATION')
    def test_bad_json_stop_rejected(self):
        self.assertEqual(review_model('{"state":"PLAN"','stop')['state'],'HOLD')
    def test_duplicate_keys_and_extra_fields_rejected(self):
        for raw in [response()[:-1]+',"state":"BLOCKED"}',response(extra='authority')]:
            with self.subTest(raw=raw), self.assertRaises(ValueError): parse_response(raw,'stop')
    def test_false_claim_invalid_types_nonfinite_rejected(self):
        for raw in [response(ran_tests=True),response(state=[]),response(answer=''),
                    response(reason=None),response().replace('false','NaN')]:
            with self.subTest(raw=raw), self.assertRaises(ValueError): parse_response(raw,'stop')
    def test_unknown_and_incomplete_actions_blocked(self):
        for f in [{},facts(action='RUN_SHELL'),facts(scope_match='true'),
                  facts(action=[]),facts(effect={})]:
            self.assertTrue(policy(f).startswith('BLOCKED'))
    def test_owner_cannot_override_data_authority_boundary(self):
        for f in [facts(untrusted_instruction=True,grant_valid=True),
                  facts(symlink_escape=True,grant_valid=True),facts(scope_match=False,grant_valid=True)]:
            self.assertEqual(policy(f),'BLOCKED_AUTHORITY_BOUNDARY')
    def test_unknown_effect_no_replay_even_with_owner(self):
        self.assertEqual(policy(facts(action='REPLAY',grant_valid=True)), 'HOLD_RECONCILE_FIRST')
        self.assertEqual(policy(facts(action='REPLAY',grant_valid=True,effect='APPLIED_VERIFIED')),
                         'BLOCKED_DUPLICATE_EFFECT')
    def test_critical_actions_require_pre_action_grant(self):
        for action in ['INSTALL','DELETE','MERGE','PUBLISH']:
            self.assertEqual(policy(facts(action=action)),'NEEDS_APPROVAL')
            self.assertEqual(policy(facts(action=action,grant_valid=True)),'REVIEW_ONLY_NO_EXECUTION')
    def test_failure_and_source_drift_cannot_pass(self):
        for code in [1,None,False,'0']:
            self.assertEqual(policy(facts(action='TEST_FIXTURE',test_exit=code)), 'HOLD_TEST_FAILED_OR_NOT_RUN')
        self.assertEqual(policy(facts(source_match=False)), 'HOLD_SOURCE_DRIFT')
    def test_recovery_source_effect_gate(self):
        a=('T1','v1','S1')
        self.assertEqual(recovery(a,('T1','v1','S2'),'UNKNOWN'),'HOLD_SOURCE_PLAN_TASK_DRIFT')
        self.assertEqual(recovery(a,a,'UNKNOWN'),'HOLD_READ_ONLY_RECONCILE')
        self.assertEqual(recovery(a,a,'APPLIED_VERIFIED'),'RESTORE_VERIFIED_RECEIPT_NO_REPLAY')


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'output.txt').write_text('actual fixture')
        (self.root/'test-receipt.json').write_text('{"exit_code":1}')
        self.manifest=file_hashes(self.root)
    def test_hash_match_does_not_imply_test_success(self):
        self.assertEqual(verify_manifest(self.root,self.manifest),'INTEGRITY_ONLY_NOT_TEST_SUCCESS')
    def test_changed_file_rejected(self):
        (self.root/'output.txt').write_text('changed')
        with self.assertRaises(ValueError): verify_manifest(self.root,self.manifest)
    def test_missing_file_rejected(self):
        (self.root/'output.txt').unlink()
        with self.assertRaises(FileNotFoundError): verify_manifest(self.root,self.manifest)
    def test_unknown_manifest_member_rejected(self):
        with self.assertRaises(ValueError): verify_manifest(self.root,{**self.manifest,'secret':'x'})
    def test_symlink_and_hardlink_rejected(self):
        (self.root/'output.txt').unlink()
        (self.root/'output.txt').symlink_to(self.root/'test-receipt.json')
        with self.assertRaises(OSError): file_hashes(self.root)
        (self.root/'output.txt').unlink()
        import os
        os.link(self.root/'test-receipt.json',self.root/'output.txt')
        with self.assertRaises(ValueError): file_hashes(self.root)
