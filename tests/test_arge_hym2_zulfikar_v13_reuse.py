"""HYM2 Zülfikar V1.3: byte-pinned reuse and anti-premature-acceptance tests."""
import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
import tools.arge_hym2_zulfikar_v13_reuse as z


class V13HYM2ReuseTests(unittest.TestCase):
    def test_v13_is_a_distinct_pinned_additive_source(self):
        self.assertEqual(z.Z13_HEAD,"28db999ba676e4764ae1b644950865674661d0b8")
        self.assertEqual(len(z.FILES),6)
        self.assertIn("zulfikar_v1_3_gates.py",z.FILES)
        self.assertIn("ZULFIKAR_GOAL_V1_3.json",z.FILES)

    def test_original_canonical_v3_is_sha256_locked(self):
        v3,lock=z.read_canonical(Path(__file__).resolve().parents[1])
        import hashlib
        self.assertEqual(hashlib.sha256(v3).hexdigest(),z.PIN_V3)
        self.assertEqual(json.loads(lock)["sha256"],z.PIN_V3)

    def test_untrusted_byte_substitution_fails_closed_before_execution(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_PIN_MISMATCH"):
            z.verify_source(fetcher=lambda name:b"substituted")

    def test_unreachable_source_produces_hold_not_100(self):
        receipt=z.evaluate(Path(__file__).resolve().parents[1],
                           fetcher=lambda name:(_ for _ in ()).throw(OSError("offline")))
        self.assertEqual(receipt["state"],"HOLD")
        self.assertEqual(receipt["original_V47_github_readiness"],"50/100_HOLD")
        self.assertEqual(receipt["verified_finish"],"HOLD")
        self.assertEqual(receipt["main_writes"],0)

    def synthetic(self,values=None,owner_override=None):
        files={name:("fixture:"+name).encode() for name in z.FILES}
        owner_policy={
            "schema":"enguru.zulfikar.goal-contract/v1.3.1",
            "authority":{
                "review_mode":"SOLO_OWNER_AUTOMATED_CI",
                "owner_id":"engurulabory",
                "peer_review_required":False,
                "issuer":"EXISTING_CANONICAL_ONLY",
                "decision_scope":"GITHUB_TECHNICAL_ACCEPTANCE_ONLY",
            },
        }
        if owner_override is not None:
            key,value=owner_override
            owner_policy["authority"][key]=value
        files["ZULFIKAR_GOAL_V1_3.json"]=json.dumps(owner_policy).encode()
        pins={name:z.blob_hash(contents) for name,contents in files.items()}
        def runner(command,**kwargs):
            k=command[-1]
            if k=="goal":
                reply={"verdict":"GOAL_SPECIFICATION_100_CANDIDATE",
                       "assessment":{"score":100,"passed_ids":list(range(10))},
                       "actual_user_goal_success":"HOLD_NOT_OBSERVED","human_authority":"HOLD"}
            elif k=="infra":
                reply={"verdict":"INFRA_GITHUB_CODE_100_CANDIDATE",
                       "assessment":{"score":100,"passed_ids":list(range(10))},
                       "python_unittest_exit_code":0,"cli_roundtrip":True,
                       "osi_infrastructure":"HOLD_NOT_EXECUTED","official_finish":"HOLD"}
            else:
                reply={"official_finish":"HOLD","osi_field":"HOLD"}
            if values:
                key,field,val=values
                if key==k:reply[field]=val
            return subprocess.CompletedProcess(command,0,json.dumps(reply),"")
        with patch.dict(z.FILES,pins,clear=True):
            return z.evaluate(Path(__file__).resolve().parents[1],
                              fetcher=lambda name:files[name],runner=runner)

    def test_synthetic_happy_path_still_keeps_all_authority_hold(self):
        receipt=self.synthetic()
        self.assertEqual(receipt["state"],"PASS_Z13_PINNED_OPERATIONAL_ADAPTER_ONLY")
        self.assertEqual(receipt["z13_goal_specification"],100)
        self.assertEqual(receipt["solo_owner_github_policy"],"VALIDATED")
        self.assertEqual(receipt["checkout_integrity"],"TEMP_GIT_HEAD_EQUALS_PINNED_BLOBS")
        self.assertEqual(receipt["zulfikar_V13_commit"],
                         "28db999ba676e4764ae1b644950865674661d0b8")
        self.assertEqual(receipt["z13_infra_github_code"],100)
        self.assertEqual(receipt["original_V47_github_readiness"],"50/100_HOLD")
        self.assertEqual(receipt["original_40_official"],"0/40")
        self.assertEqual(receipt["osi_handoff"],"HOLD")
        self.assertEqual(receipt["verified_finish"],"HOLD")

    def test_fake_human_permission_or_finish_fails_closed(self):
        for kind,field,value in (
            ("goal","human_authority","PASS_OWNER"),
            ("infra","official_finish","PASS"),
            ("status","osi_field","PASS"),
            ("status","official_finish","PASS"),
        ):
            with self.subTest(kind=kind,field=field):
                receipt=self.synthetic((kind,field,value))
                self.assertEqual(receipt["state"],"HOLD")
                self.assertEqual(receipt["original_40_official"],"0/40")

    def test_fake_peer_mode_or_canonical_issuer_rejected(self):
        for name,modified in (
            ("owner_id","other-person"),
            ("peer_review_required",True),
            ("review_mode","FAKE_PEER"),
            ("issuer","NEW_ISSUER"),
            ("decision_scope","VERIFIED_FINISH"),
        ):
            with self.subTest(name=name):
                receipt=self.synthetic(owner_override=(name,modified))
                self.assertEqual(receipt["state"],"HOLD")
                self.assertIn("Z13_MERGED_OWNER_POLICY_DRIFT",
                              receipt.get("hold_reason",""))
                self.assertEqual(receipt["original_40_official"],"0/40")

    def test_wrong_goal_or_infra_denominator_fails_closed(self):
        for phase in ("goal","infra"):
            with self.subTest(phase=phase):
                receipt=self.synthetic((phase,"verdict","FAKE_100"))
                self.assertEqual(receipt["state"],"HOLD")


if __name__=="__main__":
    unittest.main()
