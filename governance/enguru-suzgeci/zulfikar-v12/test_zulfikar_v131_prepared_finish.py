"""Zulfikar V1.3.1: adversarial verification of distinct PREP vs FIELD claims."""
import copy
import json
from pathlib import Path
import unittest

import zulfikar_v131_prepared_finish as prep
import zulfikar_v131_operational_bridge as bridge

class PreparedFinishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract,cls.contract_sha=bridge.source_read(prep.ROOT,prep.CONFIG)
        cls.head=bridge.head_sha(prep.ROOT)
        cls.bind,cls.bind_sha=bridge.source_read(prep.ROOT,bridge.BINDING_PATH)
        cls.actions,cls.action_sha=bridge.source_read(prep.ROOT,bridge.ACTION_PATH)
        cls.hashes={bridge.BINDING_PATH:cls.bind_sha,bridge.ACTION_PATH:cls.action_sha}
        cls.source_sha={}
        for p in cls.contract["technicalSources"]:
            cls.source_sha[p]=prep.tracked_digest(p,cls.head)
    def checks(self,c=None,bindings=None,actions=None,tests=True,read_only=True,pins=None,goal=100,infra=100,code=100):
        return prep.inspect(c if c is not None else self.contract,self.head,
              bindings if bindings is not None else self.bind,
              actions if actions is not None else self.actions,
              self.hashes,goal,infra,code,tests,pins if pins is not None else self.source_sha,read_only)
    def fail_check(self, mutate,domain,control):
        c=copy.deepcopy(self.contract)
        mutate(c)
        got=self.checks(c)
        self.assertIs(got[domain]["checks"][control],False)
        self.assertLess(got[domain]["score"],100)
    def test_positive_source_contract_has_three_100_targets(self):
        result=self.checks()
        self.assertEqual(tuple(result),prep.READINESS_IDS)
        self.assertTrue(all(x["score"]==100 for x in result.values()))
        self.assertEqual(sum(len(x["checks"]) for x in result.values()),30)
    def test_real_field_stays_separate(self):
        c=self.contract
        self.assertEqual(c["fieldBoundaries"]["officialProductVerifiedFinish"],"HOLD")
        self.assertEqual(c["fieldBoundaries"]["actualMacTasksAccepted"],0)
        self.assertEqual(c["fieldBoundaries"]["realMacRuntime"],"HOLD")
        self.assertFalse(c["fieldBoundaries"]["syntheticProofEqualsReal"])
    def test_three_distinct_existing_registered_handlers(self):
        out=self.checks()
        self.assertTrue(all(out["CROSS_PROJECT_PREPARATION"]["checks"].values()))
    def test_forged_action_handler_breaks_preparation(self):
        b=copy.deepcopy(self.bind)
        next(x for x in b["bindings"] if x["CAPABILITY_ID"]=="BUILD")["REGISTERED_HANDLER"]="FAKE"
        out=self.checks(bindings=b)
        self.assertLess(out["CROSS_PROJECT_PREPARATION"]["score"],100)
    def test_untrusted_goals_rejected(self):
        self.assertFalse(self.checks(goal=90)["OPERATIONAL_PREPARATION"]["checks"]["OP01_GOAL_SOURCE_100"])
    def test_untrusted_infra_rejected(self):
        self.assertFalse(self.checks(infra=90)["OPERATIONAL_PREPARATION"]["checks"]["OP02_GITHUB_INFRA_100"])
    def test_failed_registered_action_code_gate_rejected(self):
        self.assertFalse(self.checks(code=90)["OPERATIONAL_PREPARATION"]["checks"]["OP03_REGISTERED_ACTION_PREFLIGHT_100"])
    def test_corrupted_source_pin_rejected(self):
        bad=dict(self.source_sha)
        bad[next(iter(bad))]="f"*7
        self.assertFalse(self.checks(pins=bad)["OPERATIONAL_PREPARATION"]["checks"]["OP04_REGISTRY_HEAD_BYTES_PINNED"])
    def test_unchecked_ci_scope_rejected(self):
        self.assertFalse(self.checks(read_only=False)["OPERATIONAL_PREPARATION"]["checks"]["OP09_REVIEW_BRANCH_ONLY_NO_REMOTE_PUSH"])
    def test_test_failure_blocks_two_domains(self):
        out=self.checks(tests=False)
        self.assertLess(out["OPERATIONAL_PREPARATION"]["score"],100)
        self.assertLess(out["E2E_FINISH_PREPARATION"]["score"],100)
    def test_wrong_phase_order_blocks_e2e(self):
        self.fail_check(lambda x:x["phaseSequence"].reverse(),
           "E2E_FINISH_PREPARATION","E01_PHASE_ORDER_FROZEN")
    def test_fake_mac_finish_blocks_e2e(self):
        self.fail_check(lambda x:x["fieldBoundaries"].update(officialProductVerifiedFinish="PASS"),
           "E2E_FINISH_PREPARATION","E08_DONECHECK_HUMAN_SCOPE_PRESERVED")
    def test_fake_field_mac_task_blocks_e2e(self):
        self.fail_check(lambda x:x["fieldBoundaries"].update(actualMacTasksAccepted=3),
           "E2E_FINISH_PREPARATION","E09_REAL_FIELD_NOT_AUTO_PROMOTED")
    def test_missing_owner_approval_boundary_blocks_e2e(self):
        self.fail_check(lambda x:x["authority"].update(ownerFieldApprovalRequired=False),
           "E2E_FINISH_PREPARATION","E08_DONECHECK_HUMAN_SCOPE_PRESERVED")
    def test_paid_api_expansion_blocks_portability(self):
        self.fail_check(lambda x:x["authority"].update(paidApiDependency=4),
           "CROSS_PROJECT_PREPARATION","P09_NO_DUPLICATE_EXECUTOR")
    def test_duplicate_family_blocks_portability(self):
        self.fail_check(lambda x:x["pilots"][1].update(family="NATIVE_SWIFTUI_PRODUCT"),
           "CROSS_PROJECT_PREPARATION","P01_THREE_FAMILIES_EXACT")
    def test_wrong_capability_blocks_portability(self):
        self.fail_check(lambda x:x["pilots"][0].update(capability="UNKNOWN"),
           "CROSS_PROJECT_PREPARATION","P03_REGISTRY_HANDLER_AND_AUTHORITY_MATCH")
    def test_unauthorized_scope_blocks_portability(self):
        self.fail_check(lambda x:x["pilots"][1].update(ownerScope="OWNER_ALREADY_APPROVED"),
           "CROSS_PROJECT_PREPARATION","P08_FAMILY_SCOPE_RECONCILED")
    def test_proof_schema_cannot_be_truncated(self):
        self.fail_check(lambda x:x["privateReceiptProofFields"].pop(),
           "CROSS_PROJECT_PREPARATION","P07_SHARED_PROOF_FIELDS_DEFINED")
    def test_changed_control_identity_closes_domain(self):
        self.fail_check(lambda x:x["domains"][0]["controls"].pop(),
           "OPERATIONAL_PREPARATION","OP01_GOAL_SOURCE_100")
    def test_real_cli_github_checked_out_bytes(self):
        import subprocess,sys
        r=subprocess.run([sys.executable,"-B",str(prep.HERE/"zulfikar_v131_prepared_finish.py")],
          cwd=prep.HERE,capture_output=True,text=True,timeout=120)
        self.assertEqual(r.returncode,0,r.stderr+r.stdout[-600:])
        j=json.loads(r.stdout)
        self.assertEqual(j["preparationScore"],100)
        self.assertEqual(j["canonicalProductVerifiedFinish"],"HOLD")
        self.assertEqual(j["githubExactHeadCI"],"EXTERNAL_GITHUB_ACTIONS_VERIFICATION_REQUIRED")
        self.assertEqual(j["realTaskTransfer"],"HOLD_0_OF_3")

if __name__=="__main__":unittest.main()
