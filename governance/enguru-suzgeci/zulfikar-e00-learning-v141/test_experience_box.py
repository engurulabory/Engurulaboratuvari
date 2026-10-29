"""E00 ExperienceBox: real SQLite persistence, failure and recovery guards.

Test-worker receipts are isolated harness fixtures, never owner signatures.
The existing DÖM adapter has its own real subprocess + checkpoint tests.
"""
import copy
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from experience_box import ExperienceBox, DOMAINS, KINDS, event_valid

class BoxTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.path=Path(self.t.name)/"queue.sqlite3"
        self.box=ExperienceBox(self.path)
        self.addCleanup(self.box.close)
        self.e={
            "eventId":"EV-001", "goalId":"ZF-141",
            "sourceSha256":"a"*64,"domain":"CODE","kind":"FAILURE",
            "outcome":"NEGATIVE","need":"RELIABILITY",
            "description":"Checkpoint no longer matches observed content",
            "lesson":"Read current bytes before accepting a previous checkpoint",
        }
    def insert(self, event=None):
        return self.box.put(event or self.e)
    def ready(self, event=None):
        e=event or self.e;self.insert(e)
        self.box.triage(e["eventId"],solution="Recheck bytes and run regression",
                        solution_ref="source/recovery-proof")
        return e["eventId"]
    def batch(self):
        eid=self.ready()
        return self.box.make_batch([eid])["batchId"]
    def worker(self,e,solution,round_index):
        # This test-only worker invokes an actual subprocess, and supplies a
        # candidate receipt. It does NOT grant production operating authority.
        p=subprocess.run([sys.executable,"-B","-c","print('test subprocess')"],
                         capture_output=True,timeout=10,text=True)
        if p.returncode!=0: return {}
        return {"state":"E00_ISOLATED_TEST_CANDIDATE",
                "realTestObserved":True,"officialPassIssued":False,
                "journalHeadSha256":hashlib.sha256(p.stdout.encode()).hexdigest()}
    def test_01_96_open_categories(self):
        self.assertEqual((len(DOMAINS),len(KINDS)),(12,8))
        self.assertEqual(self.box.summary()["categories"],96)
    def test_02_insert_observation(self):
        self.assertEqual(self.insert()["state"],"NEW")
        self.assertEqual(self.box.summary()["states"]["NEW"],1)
    def test_03_exact_idempotence(self):
        self.insert();self.assertEqual(self.insert()["state"],"IDEMPOTENT_EXISTING")
        self.assertEqual(self.box.summary()["active"],1)
    def test_04_duplicate_open_fingerprint(self):
        self.insert();e=dict(self.e,eventId="EV-002")
        self.assertEqual(self.insert(e)["state"],"DEDUPLICATED_OPEN")
        self.assertEqual(self.box.summary()["active"],1)
    def test_05_event_id_reused_with_different_evidence(self):
        self.insert()
        with self.assertRaises(ValueError):self.insert(dict(self.e,lesson="Changed"))
    def test_06_unknown_domain(self):
        with self.assertRaises(ValueError):self.insert(dict(self.e,domain="INVALID"))
    def test_07_unhashable_domain(self):
        with self.assertRaises(ValueError):self.insert(dict(self.e,domain=["CODE"]))
    def test_08_unknown_outcome(self):
        with self.assertRaises(ValueError):self.insert(dict(self.e,outcome="APPROVED"))
    def test_09_wrong_source_hash(self):
        with self.assertRaises(ValueError):self.insert(dict(self.e,sourceSha256="BAD"))
    def test_10_no_ready_solution_stays_research(self):
        self.insert()
        r=self.box.triage("EV-001")
        self.assertEqual(r["state"],"RESEARCH")
        self.assertEqual(self.box.summary()["states"]["RESEARCH"],1)
    def test_11_solution_can_follow_research(self):
        self.insert();self.box.triage("EV-001")
        r=self.box.triage("EV-001",solution="Recheck sha",solution_ref="proof/source")
        self.assertEqual(r["state"],"READY")
        self.assertFalse(r["solutionVerified"])
    def test_12_solution_without_source_ref_rejected(self):
        self.insert()
        with self.assertRaises(ValueError):self.box.triage("EV-001",solution="repair")
        self.assertEqual(self.box.summary()["states"]["NEW"],1)
    def test_13_make_batch_moves_to_testing(self):
        x=self.batch()
        self.assertTrue(x.startswith("E00B-"))
        self.assertEqual(self.box.summary()["states"]["BATCHED"],1)
    def test_14_unresolved_case_cannot_batch(self):
        self.insert();self.box.triage("EV-001")
        with self.assertRaises(ValueError):self.box.make_batch(["EV-001"])
    def test_15_different_goal_cannot_batch(self):
        one=self.ready()
        e=dict(self.e,eventId="EV-002",goalId="OTHER",description="Different goal")
        two=self.ready(e)
        with self.assertRaises(ValueError):self.box.make_batch([one,two])
        self.assertEqual(self.box.summary()["states"]["READY"],2)
    def test_16_different_source_cannot_batch(self):
        one=self.ready()
        e=dict(self.e,eventId="EV-002",sourceSha256="b"*64,description="Source diff")
        two=self.ready(e)
        with self.assertRaises(ValueError):self.box.make_batch([one,two])
    def test_17_different_domain_cannot_batch(self):
        one=self.ready()
        e=dict(self.e,eventId="EV-002",domain="DATA",description="Different work")
        two=self.ready(e)
        with self.assertRaises(ValueError):self.box.make_batch([one,two])
    def test_18_duplicate_event_id_in_batch(self):
        self.ready()
        with self.assertRaises(ValueError):self.box.make_batch(["EV-001","EV-001"])
    def test_19_empty_batch_rejected(self):
        with self.assertRaises(ValueError):self.box.make_batch([])
    def test_20_real_subprocess_isolated_candidate(self):
        b=self.batch();r=self.box.assess_batch(b,self.worker)
        self.assertEqual(r["state"],"ISOLATED_BATCH_CANDIDATE")
        self.assertEqual(r["candidate"],1)
        self.assertFalse(r["officialPassIssued"])
        self.assertEqual(self.box.summary()["states"]["CANDIDATE"],1)
    def test_21_fake_worker_success_without_receipt_is_hold(self):
        b=self.batch()
        r=self.box.assess_batch(b,lambda *_:{"state":"E00_ISOLATED_TEST_CANDIDATE"})
        self.assertEqual(r["state"],"BATCH_HOLD")
        self.assertEqual(r["rounds"],3)
        self.assertEqual(self.box.summary()["states"]["HOLD"],1)
    def test_22_only_pass_on_third_round(self):
        b=self.batch()
        r=self.box.assess_batch(b,lambda e,s,i:self.worker(e,s,i) if i==3 else {})
        self.assertEqual((r["rounds"],r["candidate"],r["hold"]),(3,1,0))
    def test_23_unbounded_round_rejected(self):
        b=self.batch()
        with self.assertRaises(ValueError):self.box.assess_batch(b,self.worker,max_rounds=4)
        self.assertEqual(self.box.summary()["states"]["BATCHED"],1)
    def test_24_bool_round_rejected(self):
        b=self.batch()
        with self.assertRaises(ValueError):self.box.assess_batch(b,self.worker,max_rounds=True)
    def test_25_forged_official_pass_from_worker_rejected(self):
        b=self.batch()
        def forged(e,s,i):return dict(self.worker(e,s,i),officialPassIssued=True)
        self.assertEqual(self.box.assess_batch(b,forged,max_rounds=1)["state"],"BATCH_HOLD")
    def test_26_no_archive_without_candidate(self):
        b=self.batch()
        with self.assertRaises(ValueError):
            self.box.archive_authorized(b,commit_sha="b"*40,ci_url="https://github.com",
                owner_verifier=lambda _:True,source_verifier=lambda _:True)
    def test_27_owner_rejects_archive(self):
        b=self.batch();self.box.assess_batch(b,self.worker)
        with self.assertRaises(ValueError):
            self.box.archive_authorized(b,commit_sha="b"*40,ci_url="https://github.com",
                owner_verifier=lambda _:False,source_verifier=lambda _:True)
        self.assertEqual(self.box.summary()["states"]["CANDIDATE"],1)
    def test_28_source_verifier_rejects_archive(self):
        b=self.batch();self.box.assess_batch(b,self.worker)
        with self.assertRaises(ValueError):
            self.box.archive_authorized(b,commit_sha="b"*40,ci_url="https://github.com",
                owner_verifier=lambda _:True,source_verifier=lambda _:False)
    def test_29_external_attested_archive_preserves_journal(self):
        b=self.batch();self.box.assess_batch(b,self.worker)
        r=self.box.archive_authorized(b,commit_sha="b"*40,ci_url="https://github.com/engurulabory/Engurulaboratuvari/actions",
                    owner_verifier=lambda _:True,source_verifier=lambda _:True)
        self.assertEqual(r["state"],"ARCHIVED_INACTIVE_QUEUE")
        snap=self.box.summary()
        self.assertEqual(snap["archived"],1)
        self.assertEqual(snap["active"],0)
        self.assertGreaterEqual(snap["journalRecords"],5)
        self.assertEqual(snap["officialVerifiedFinish"],"NOT_ISSUED")
    def test_30_reopen_same_case_after_archive(self):
        b=self.batch();self.box.assess_batch(b,self.worker)
        self.box.archive_authorized(b,commit_sha="b"*40,ci_url="https://github.com",
                    owner_verifier=lambda _:True,source_verifier=lambda _:True)
        e=dict(self.e,eventId="EV-002")
        self.assertEqual(self.insert(e)["state"],"NEW")
        self.assertEqual(self.box.summary()["active"],1)
        self.assertEqual(self.box.summary()["archived"],1)
    def test_31_idempotent_retest_blocked(self):
        b=self.batch();self.box.assess_batch(b,self.worker)
        with self.assertRaises(ValueError):self.box.assess_batch(b,self.worker)
    def test_32_durable_reopen_keeps_backlog(self):
        self.ready()
        other=dict(self.e,eventId="EV-002",domain="SECURITY",description="Unknown rights")
        self.insert(other);self.box.triage("EV-002")
        self.box.close()
        self.box=ExperienceBox(self.path)
        self.assertEqual(self.box.summary()["states"]["READY"],1)
        self.assertEqual(self.box.summary()["states"]["RESEARCH"],1)
    def test_33_multiple_ready_one_package(self):
        one=self.ready()
        e=dict(self.e,eventId="EV-002",kind="REGRESSION",description="Repeated regression")
        two=self.ready(e)
        b=self.box.make_batch([one,two])["batchId"]
        r=self.box.assess_batch(b,self.worker)
        self.assertEqual(r["candidate"],2)
        self.assertEqual(self.box.summary()["states"]["CANDIDATE"],2)
    def test_34_partial_batch_keeps_hold_visible(self):
        one=self.ready()
        e=dict(self.e,eventId="EV-002",kind="REGRESSION",description="Second problem")
        two=self.ready(e)
        b=self.box.make_batch([one,two])["batchId"]
        r=self.box.assess_batch(b,lambda ev,s,i:self.worker(ev,s,i) if ev["eventId"]==one else {},max_rounds=2)
        self.assertEqual((r["candidate"],r["hold"]),(1,1))
        self.assertEqual(self.box.summary()["states"]["HOLD"],1)
        with self.assertRaises(ValueError):
            self.box.archive_authorized(b,commit_sha="b"*40,ci_url="https://github.com",
                owner_verifier=lambda _:True,source_verifier=lambda _:True)
    def test_35_no_change_positive_stays_observation(self):
        e=dict(self.e,kind="SUCCESS",outcome="POSITIVE")
        self.insert(e)
        self.assertEqual(self.box.summary()["states"]["NEW"],1)
        self.assertEqual(self.box.summary()["archived"],0)
    def test_36_invalid_id_blocks_sql_trick(self):
        with self.assertRaises(ValueError):
            self.insert(dict(self.e,eventId="X';DROP TABLE cases;--"))
        self.assertEqual(self.box.summary()["active"],0)
    def test_37_bad_git_sha_rejected(self):
        b=self.batch();self.box.assess_batch(b,self.worker)
        with self.assertRaises(ValueError):
            self.box.archive_authorized(b,commit_sha="bad",ci_url="https://github.com",
                owner_verifier=lambda _:True,source_verifier=lambda _:True)
    def test_39_failure_diagnosis_preserves_cause_gap_need_correction(self):
        b=self.batch();self.box.assess_batch(b,lambda *_:{},max_rounds=2)
        r=self.box.diagnose("EV-001",cause="Stale checkpoint",
            gap="Output digest differs",requirement="Current bytes match",
            correction="Rebuild source-bound artifact and compare SHA")
        self.assertTrue(r["diagnosisRecorded"])
        self.assertEqual(self.box.summary()["failureDiagnoses"],1)
        self.assertEqual(self.box.summary()["attemptRecords"],2)
        self.assertEqual(self.box.summary()["states"]["HOLD"],1)

    def test_40_retry_requires_cause_analysis(self):
        b=self.batch();self.box.assess_batch(b,lambda *_:{},max_rounds=1)
        with self.assertRaises(ValueError):
            self.box.retry_batch(b,{"EV-001":{"solution":"New fix","solution_ref":"new/evidence"}})
        self.assertEqual(self.box.summary()["states"]["HOLD"],1)

    def test_41_retry_requires_meaningful_difference(self):
        b=self.batch();self.box.assess_batch(b,lambda *_:{},max_rounds=1)
        self.box.diagnose("EV-001",cause="Incorrect output",gap="Missing criterion",
            requirement="Correct artifact",correction="Repair source and rerun")
        with self.assertRaises(ValueError):
            self.box.retry_batch(b,{"EV-001":{"solution":"Recheck bytes and run regression",
                                           "solution_ref":"source/recovery-proof"}})
        self.assertEqual(self.box.summary()["states"]["HOLD"],1)

    def test_42_corrected_retry_then_verified_candidate(self):
        b=self.batch()
        first=self.box.assess_batch(b,lambda *_:{},max_rounds=3)
        self.assertEqual(first["state"],"BATCH_HOLD")
        self.box.diagnose("EV-001",cause="Old output mismatch",
            gap="Failed SHA",requirement="Reverified bytes",
            correction="New source-bound check")
        self.box.retry_batch(b,{"EV-001":{"solution":"New source-bound byte repair",
                                           "solution_ref":"fix/recovery-v2"}})
        second=self.box.assess_batch(b,self.worker)
        self.assertEqual(second["state"],"ISOLATED_BATCH_CANDIDATE")
        summary=self.box.summary()
        self.assertEqual(summary["attemptRecords"],4)
        self.assertEqual(summary["failureDiagnoses"],1)
        self.assertEqual(summary["states"]["CANDIDATE"],1)
        self.assertEqual(summary["states"]["ARCHIVED"],0)

    def test_43_failed_retry_stays_in_box_for_next_cycle(self):
        b=self.batch();self.box.assess_batch(b,lambda *_:{},max_rounds=1)
        self.box.diagnose("EV-001",cause="First reason",gap="First gap",
            requirement="First fix required",correction="Change validator")
        self.box.retry_batch(b,{"EV-001":{"solution":"Fix v2","solution_ref":"proof/v2"}})
        self.box.assess_batch(b,lambda *_:{},max_rounds=1)
        self.assertEqual(self.box.summary()["states"]["HOLD"],1)
        self.box.diagnose("EV-001",cause="Second reason",gap="Second gap",
            requirement="Second fix required",correction="Change patch")
        self.box.retry_batch(b,{"EV-001":{"solution":"Fix v3","solution_ref":"proof/v3"}})
        self.box.assess_batch(b,self.worker)
        self.assertEqual(self.box.summary()["states"]["CANDIDATE"],1)
        self.assertEqual(self.box.summary()["attemptRecords"],3)
        self.assertEqual(self.box.summary()["failureDiagnoses"],2)

    def test_44_partial_batch_retests_previously_passed_case(self):
        a=self.ready()
        e=dict(self.e,eventId="EV-002",kind="REGRESSION",description="Second failure")
        self.ready(e)
        bid=self.box.make_batch([a,"EV-002"])["batchId"]
        prior=self.box.assess_batch(
            bid,lambda ev,s,i:self.worker(ev,s,i) if ev["eventId"]==a else {},
            max_rounds=1)
        self.assertEqual((prior["candidate"],prior["hold"]),(1,1))
        self.box.diagnose("EV-002",cause="Regressed source",gap="Second mismatch",
            requirement="All criteria true",correction="Revalidate both cases")
        self.box.retry_batch(bid,{"EV-002":{"solution":"Second fix","solution_ref":"proof/v2"}})
        count=[]
        def verified(ev,s,i):
            count.append(ev["eventId"])
            return self.worker(ev,s,i)
        after=self.box.assess_batch(bid,verified,max_rounds=1)
        self.assertEqual(after["candidate"],2)
        self.assertEqual(set(count),{"EV-001","EV-002"})
        self.assertEqual(self.box.summary()["attemptRecords"],4)

    def test_45_no_premature_archive_on_failed_batch(self):
        b=self.batch();self.box.assess_batch(b,lambda *_:{})
        with self.assertRaises(ValueError):
            self.box.archive_authorized(b,commit_sha="b"*40,ci_url="https://github.com",
                owner_verifier=lambda _:True,source_verifier=lambda _:True)
        self.assertEqual(self.box.summary()["archived"],0)

    def test_46_archive_after_retry_and_external_approval(self):
        b=self.batch();self.box.assess_batch(b,lambda *_:{},max_rounds=1)
        self.box.diagnose("EV-001",cause="Broken check",gap="Wrong output",
            requirement="Retest true",correction="Patch checker")
        self.box.retry_batch(b,{"EV-001":{"solution":"Patch v2",
                                           "solution_ref":"proof/final"}})
        self.box.assess_batch(b,self.worker,max_rounds=1)
        self.box.archive_authorized(b,commit_sha="b"*40,ci_url="https://github.com",
            owner_verifier=lambda _:True,source_verifier=lambda _:True)
        s=self.box.summary()
        self.assertEqual(s["active"],0)
        self.assertEqual(s["archived"],1)
        self.assertEqual(s["attemptRecords"],2)
        self.assertEqual(s["failureDiagnoses"],1)
        self.assertGreaterEqual(s["journalRecords"],8)

    def test_47_restart_reloads_failed_history_and_retry(self):
        b=self.batch();self.box.assess_batch(b,lambda *_:{},max_rounds=2)
        self.box.diagnose("EV-001",cause="Restart failure",gap="Journal gap",
            requirement="Resume safely",correction="Fresh source checkpoint")
        self.box.close();self.box=ExperienceBox(self.path)
        self.assertEqual(self.box.summary()["attemptRecords"],2)
        self.box.retry_batch(b,{"EV-001":{"solution":"Correct restart flow",
                                           "solution_ref":"proof/restart"}})
        self.box.assess_batch(b,self.worker,max_rounds=1)
        self.assertEqual(self.box.summary()["states"]["CANDIDATE"],1)

    def test_38_sqlite_research_queue_survives_failure(self):
        self.insert();self.box.triage("EV-001")
        self.box.close()
        self.box=ExperienceBox(self.path)
        self.assertEqual(self.box.summary()["states"]["RESEARCH"],1)


if __name__=="__main__":unittest.main()
