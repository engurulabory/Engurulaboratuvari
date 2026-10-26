"""Zulfikar V1.3.1 ten goal/capability evidence sources — anti-inflation tests."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

import zulfikar_v131_ten_capabilities as ten
import zulfikar_v131_operational_bridge as bridge


class TenCapabilities(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.score,_=bridge.source_read(bridge.ROOT,ten.SCORECARD)
        cls.policy,_=bridge.source_read(bridge.ROOT,ten.POLICY)
        cls.goal,_=bridge.source_read(bridge.ROOT,ten.GOAL)
        cls.head=bridge.head_sha(bridge.ROOT)
        cls.agents=bridge.read_no_symlink(bridge.ROOT,"AGENTS.md",100_000).decode("utf8")

    def scorecard(self):return copy.deepcopy(self.score)
    def inspect(self,score=None,pol=None,goal=None,agents=None,verified=False):
        return ten.inspect(self.score if score is None else score,
           self.policy if pol is None else pol,
           self.goal if goal is None else goal,self.head,
           self.agents if agents is None else agents,verify_files=verified)
    def error_for(self,change,expected):
        x=self.scorecard()
        change(x)
        result=self.inspect(score=x)
        self.assertIn(expected,result["faults"],result)
        self.assertIsNone(result["acceptedOverallScore"])
        self.assertFalse(result["verifiedFullCapabilityPass"])

    def test_all_ten_present_and_one_scorecard(self):
        result=self.inspect()
        self.assertEqual(result["checksPassed"],10,result)
        self.assertEqual(result["checksRequired"],10)
        self.assertEqual([x["id"] for x in result["capabilities"]],list(ten.IDS))
        self.assertEqual(result["singleAcceptanceAuthority"],ten.SCORECARD)

    def test_end_to_end_and_finish_never_auto_pass(self):
        result=self.inspect()
        for row in result["capabilities"]:
            self.assertIsNone(row["acceptedScore"])
            self.assertFalse(row["fullCapabilityPass"])
            self.assertEqual(row["realFieldOrOwnerEvidence"],"AWAIT_AUTHORIZED_PROOF")
        self.assertFalse(result["verifiedFullCapabilityPass"])

    def test_scopes_present_six_domain_refs(self):
        result=self.inspect()
        self.assertEqual({x["stage"] for x in result["capabilities"]},set(ten.STAGES))
        self.assertEqual(len(result["capabilities"]),10)

    def test_remove_a_capability(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"]["capabilities"].pop(),
                       "TEN_CAPABILITIES_REQUIRED")

    def test_forged_capability_identifier(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"]["capabilities"][0].update(id="K17"),
                       "CAPABILITY_ROUTE_REQUIREMENTS_OPEN")

    def test_swap_stage(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"]["capabilities"][5].update(stage="PREPARATION"),
                       "CAPABILITY_ROUTE_REQUIREMENTS_OPEN")

    def test_unknown_six_domain_link(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"]["capabilities"][3].update(existingDomainRefs=["MADEUP"]),
                       "CAPABILITY_ROUTE_REQUIREMENTS_OPEN")

    def test_duplicate_domain_ref(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"]["capabilities"][0].update(existingDomainRefs=["GOAL","GOAL"]),
                       "CAPABILITY_ROUTE_REQUIREMENTS_OPEN")

    def test_duplicate_source_file(self):
        def mutate(x):
            q=x["canonicalClosure"]["tenCapabilityMap"]["capabilities"][0]
            q["preparationSourceFiles"]=[q["preparationSourceFiles"][0]]*2
        self.error_for(mutate,"CAPABILITY_ROUTE_REQUIREMENTS_OPEN")

    def test_traversal_path_rejected(self):
        def mutate(x):
            x["canonicalClosure"]["tenCapabilityMap"]["capabilities"][0]["preparationSourceFiles"][0]="../../.git/config"
        self.error_for(mutate,"CAPABILITY_ROUTE_REQUIREMENTS_OPEN")

    def test_missing_requirement_rejected(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"]["capabilities"][0].update(realFieldRequirement=""),
                       "CAPABILITY_ROUTE_REQUIREMENTS_OPEN")

    def test_fake_full_capability_pass_rejected(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"]["capabilities"][4].update(verifiedFull100=True),
                       "CAPABILITY_ROUTE_REQUIREMENTS_OPEN")

    def test_fake_owner_state_rejected(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"]["capabilities"][9].update(realAuthority="OWNER_SIGNED"),
                       "CAPABILITY_ROUTE_REQUIREMENTS_OPEN")

    def test_global_fake_ten_pass_rejected(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"]["globalAcceptance"].update(allTenVerified=True),
                       "PREMATURE_TEN_CAPABILITY_ACCEPTANCE")

    def test_global_fake_ten_score_rejected(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"]["globalAcceptance"].update(acceptedCapabilities=10),
                       "PREMATURE_TEN_CAPABILITY_ACCEPTANCE")

    def test_first_stage_cannot_auto_accept_successors(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"].update(
            goalToOutcomeRule="FIRST_100_IMPLIES_ALL_100"),"TEN_METHOD_SINGLE_AUTHORITY_DRIFT")

    def test_stage_dependency_order_fixed(self):
        self.error_for(lambda x:x["canonicalClosure"]["tenCapabilityMap"]["stageDependency"].reverse(),
                       "TEN_METHOD_SINGLE_AUTHORITY_DRIFT")

    def test_policy_99_rejected(self):
        p=copy.deepcopy(self.policy)
        p["acceptanceUniverse"]["passThreshold"]=99
        self.assertIn("ORIGINAL_ONE_HUNDRED_ONLY_AUTHORITY_DRIFT",self.inspect(pol=p)["faults"])

    def test_new_scorecard_cannot_override_original(self):
        s=self.scorecard()
        s["acceptedOperationalScore"]=100
        self.assertIn("ORIGINAL_ONE_HUNDRED_ONLY_AUTHORITY_DRIFT",self.inspect(score=s)["faults"])

    def test_goal_id_link_drift(self):
        g=copy.deepcopy(self.goal)
        g["universalUmbrella"]["policyRef"]="FAKE"
        self.assertIn("GOAL_TO_POLICY_LINK_DRIFT",self.inspect(goal=g)["faults"])

    def test_session_context_entrypoint_required(self):
        self.assertIn("GLOBAL_SESSION_ENTRYPOINT_DRIFT",
                      self.inspect(agents="AGENTS OMITTED")["faults"])

    def test_simulated_loop_reaches_100_but_is_not_authorized(self):
        output=ten.simulate_repair_loop({"architecture":False,"tests":False},
                  [{"architecture":True},{"tests":True}],3)
        self.assertEqual(output["decision"],"SIMULATED_100_NOT_FIELD_ACCEPTANCE")
        self.assertIsNone(output["acceptedScore"])
        self.assertEqual([r["diagnostic"] for r in output["history"]],[0,50,100])

    def test_simulated_loop_budget_is_bounded(self):
        out=ten.simulate_repair_loop({"a":False,"b":False},
             [{"a":True}],max_rounds=2)
        self.assertEqual(out["decision"],"CONTINUE_IMPROVEMENT")
        self.assertIsNone(out["acceptedScore"])

    def test_simulated_loop_regression_rejected(self):
        out=ten.simulate_repair_loop({"a":True,"b":False},
              [{"a":False}],3)
        self.assertEqual(out["decision"],"REGRESSION_GUARD")

    def test_simulated_loop_invalid_patch_rejected(self):
        out=ten.simulate_repair_loop({"a":False},[{"b":True}])
        self.assertEqual(out["decision"],"INVALID_PATCH")

    def test_simulated_loop_invalid_state_rejected(self):
        self.assertEqual(ten.simulate_repair_loop({"a":1},[])["decision"],"INVALID_DIAGNOSTIC")

    def test_simulated_loop_no_magical_later_100(self):
        a=ten.simulate_repair_loop({"first":True,"later":False},[{}],3)
        self.assertEqual(a["decision"],"CONTINUE_IMPROVEMENT")
        self.assertIsNone(a["acceptedScore"])

    def test_exact_head_sources_for_all_ten(self):
        result=self.inspect(verified=True)
        self.assertEqual(result["checksPassed"],10,result["faults"])
        self.assertTrue(all(row["sourcePins"] for row in result["capabilities"]))
        self.assertEqual(result["sourceRoutesDecision"],
                         "TEN_SOURCE_ROUTES_VERIFIED_CI_REVIEW_REQUIRED")

    def test_actual_cli_does_not_grant_10_real_passes(self):
        cmd=[sys.executable,"-B",str(Path(__file__).with_name("zulfikar_v131_ten_capabilities.py"))]
        result=subprocess.run(cmd,cwd=Path(__file__).parent,
                              text=True,capture_output=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stdout[-700:]+result.stderr)
        data=json.loads(result.stdout)
        self.assertEqual(data["checksPassed"],10)
        self.assertEqual(data["fullyVerifiedCapabilityCount"],0)
        self.assertIsNone(data["acceptedOverallScore"])
        self.assertEqual(data["officialVerifiedFinish"],
                         "AWAIT_AUTHORIZED_DONECHECK_HUMAN_THRESHOLD")


if __name__=="__main__":
    unittest.main(verbosity=2)
