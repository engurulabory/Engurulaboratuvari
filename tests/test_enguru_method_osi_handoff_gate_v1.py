"""Source-bound, 3+2 OSi handoff policy adversarial tests; mock verifiers only."""
import copy
import unittest
from tools.enguru_method_osi_handoff_gate_v1 import review_full_chain, OSI_REQUIRED
from test_enguru_method_three_phase_gate_v1 import plan, verifier, digest

GITHUB_HEAD = "a"*40


def case():
    p = plan()
    p["userGoal"] = "PiLive working Mac cockpit, exact source and protected official finish"
    p["originalAcceptanceIds"] = ["P02-12", "SCREEN-USER", "DONECHECK-4", "FIELD-7"]
    p["controls"]["OSI_HANDOFF"] = list(OSI_REQUIRED)
    p["osiHandoffRounds"] = [
        {"caseId": "OSI-1"}, {"caseId": "OSI-2"}, {"caseId": "OSI-3"},
    ]
    return p


def controls(phase, challenge):
    if challenge["caseId"] == "FINAL_SOURCE_REVALIDATION":
        return {"passedIds": case()["controls"][phase],
                "sourceSha256": challenge["sourceSha256"],
                "evidenceSha256": digest(800 if phase=="DESIGN" else 801),
                "oracleId": "real-source-revalidation-"+phase}
    if phase == "OSI_HANDOFF":
        i = int(challenge["caseId"].split("-")[-1])
        return {"passedIds": list(OSI_REQUIRED)[:(2 if i==1 else 6 if i==2 else 8)],
                "sourceSha256": challenge["sourceSha256"],
                "evidenceSha256": digest(1200+i),
                "oracleId": "osi-independent-3" if i == 3 else "osi-primary"}
    return verifier(phase, challenge)


def github(source):
    return {"head": GITHUB_HEAD, "sourceSha256": source, "ciHead":GITHUB_HEAD,
            "checksState": "SUCCESS", "canonicalLockVerified":True,
            "originalAcceptanceIds": case()["originalAcceptanceIds"],
            "receiptSha256": digest(1500)}


def osi(head):
    return {"readOnly": True, "canonicalWrites":0, "targetChecked":True,
            "sourceHead": head, "targetHead": "b"*40,
            "receiptSha256": digest(1600)}


class FourthStageTests(unittest.TestCase):
    def test_complete_chain_stops_at_owner(self):
        result=review_full_chain(case(), controls, github, osi)
        self.assertEqual(result["state"], "PASS_HANDOFF_POLICY_AWAIT_HUMAN")
        self.assertEqual(result["stageOrder"], ["DESIGN","THEORY","GITHUB","OSI_HANDOFF"])
        self.assertEqual(result["osiRoundScores"], [25,75,100])
        self.assertEqual(result["GITHUB_PREPARED"], "PASS_EXTERNAL_CI")
        self.assertEqual(result["OSI_HANDOFF_PREPARED"], "PASS_READ_ONLY_PLAN_ONLY")
        self.assertEqual(result["HUMAN_AUTHORIZED"], "HOLD")
        self.assertEqual(result["VERIFIED_FINISH"], "HOLD")
        self.assertEqual(result["macWrites"],0)

    def test_user_goal_and_original_acceptance_required(self):
        for k,v in (("userGoal", ""), ("originalAcceptanceIds",[])):
            p=case();p[k]=v
            self.assertEqual(review_full_chain(p, controls, github, osi)["activeStage"],"DESIGN")

    def test_design_hold_never_calls_github_or_osi(self):
        p=case();p["rounds"]["DESIGN"][2]["passed"]=["DESIGN1"]
        invoked=[]
        def no_github(source):
            invoked.append("GitHub"); return github(source)
        def no_osi(head):
            invoked.append("OSi"); return osi(head)
        r=review_full_chain(p,controls,no_github,no_osi)
        self.assertEqual(r["activeStage"],"DESIGN")
        self.assertEqual(invoked,[])

    def test_last_source_revalidation_is_mandatory(self):
        def wrong(phase,challenge):
            v=controls(phase,challenge)
            if challenge["caseId"]=="FINAL_SOURCE_REVALIDATION":
                v["sourceSha256"] = digest(78)
            return v
        r=review_full_chain(case(),wrong,github,osi)
        self.assertEqual(r["reason"],"HOLD_FINAL_SOURCE_REVALIDATION")
        self.assertEqual(r["OSI_HANDOFF_PREPARED"],"HOLD")

    def test_wrong_github_ci_or_source_holds_before_osi(self):
        for k,v in (("ciHead","0"*40), ("checksState","FAILURE"),
                    ("canonicalLockVerified",False), ("sourceSha256",digest(1)),
                    ("originalAcceptanceIds",["SCREEN-USER"])):
            with self.subTest(k=k):
                called=[]
                def broken(source):
                    r=github(source);r[k]=v;return r
                def guard(head):
                    called.append(True);return osi(head)
                r=review_full_chain(case(),controls,broken,guard)
                self.assertEqual(r["reason"],"HOLD_EXACT_GITHUB_SOURCE_CI_AND_SCOPE")
                self.assertEqual(called,[])

    def test_osi_read_only_target_observation_required(self):
        for k,v in (("canonicalWrites",1),("readOnly",False),("targetChecked",False),
                    ("targetHead","bad"),("sourceHead","0"*40)):
            with self.subTest(k=k):
                def broken(head):
                    r=osi(head);r[k]=v;return r
                r=review_full_chain(case(),controls,github,broken)
                self.assertEqual(r["reason"],"HOLD_OSI_REAL_READ_ONLY_PREFLIGHT")

    def test_forged_osi_100_cannot_expand_original_scope(self):
        p=case()
        p["OSI_HANDOFF_PREPARED"]="PASS"
        p["controls"]["OSI_HANDOFF"] = list(OSI_REQUIRED[:-1])
        r=review_full_chain(p,controls,github,osi)
        self.assertEqual(r["reason"],"HOLD_OSI_FIXED_CONTROL_SCOPE")

    def test_osi_round_3_missing_control_is_hold(self):
        def gap(phase,challenge):
            r=controls(phase,challenge)
            if phase=="OSI_HANDOFF" and challenge["caseId"]=="OSI-3":
                r["passedIds"]=r["passedIds"][:-1]
            return r
        r=review_full_chain(case(),gap,github,osi)
        self.assertEqual(r["reason"],"HOLD_OSI_HANDOFF_CONTROL_GAPS")

    def test_osi_fourth_and_fifth_meaningful_rounds(self):
        p=case();p["osiHandoffRounds"].extend([{"caseId":"OSI-4"},{"caseId":"OSI-5"}])
        def progressive(phase,challenge):
            r=controls(phase,challenge)
            if phase=="OSI_HANDOFF":
                n=int(challenge["caseId"].split("-")[-1])
                r["passedIds"]=list(OSI_REQUIRED)[:min(n+3,8)]
                r["evidenceSha256"]=digest(2000+n)
            return r
        self.assertEqual(review_full_chain(p,progressive,github,osi)["osiHandoffScore"],100)
        def stalled(phase,challenge):
            r=progressive(phase,challenge)
            if phase=="OSI_HANDOFF" and challenge["caseId"]=="OSI-4":
                r["passedIds"]=list(OSI_REQUIRED)[:6]
            return r
        self.assertEqual(review_full_chain(p,stalled,github,osi)["reason"],
                         "HOLD_OSI_EXTRA_ROUND_NO_NEW_PASS")

    def test_osi_source_drift_or_duplicate_evidence_hold(self):
        def drift(phase,challenge):
            r=controls(phase,challenge)
            if phase=="OSI_HANDOFF" and challenge["caseId"]=="OSI-3":
                r["sourceSha256"]=digest(19)
            return r
        self.assertEqual(review_full_chain(case(),drift,github,osi)["reason"],"HOLD_OSI_SOURCE_DRIFT")
        def duplicate(phase,challenge):
            r=controls(phase,challenge)
            if phase=="OSI_HANDOFF" and challenge["caseId"]=="OSI-2":
                r["evidenceSha256"]=digest(1201)
            return r
        self.assertEqual(review_full_chain(case(),duplicate,github,osi)["reason"],
                         "HOLD_OSI_REPLAY_WITHOUT_EVIDENCE")

    def test_osi_independent_oracle_required(self):
        def fake(phase,challenge):
            r=controls(phase,challenge)
            if phase=="OSI_HANDOFF" and challenge["caseId"]=="OSI-3":
                r["oracleId"]="osi-primary"
            return r
        self.assertEqual(review_full_chain(case(),fake,github,osi)["reason"],
                         "HOLD_OSI_THIRD_INDEPENDENT_ORACLE")


if __name__=="__main__":
    unittest.main()
