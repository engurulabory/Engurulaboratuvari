import copy
import unittest
from tools.enguru_suzgec_v23_forecast import (
    SCHEMA, MANDATORY_SCENARIOS, sha256_json, validate_forecast,
    simulate_missing_authority,
)
from tools.enguru_suzgec_v23_execution import readiness, ExecutionHold

def example():
    state={"project":"ENGURU_SUZGEC_V23", "operatingFramework":{"holisticFinishV22":{"state":"ENFORCE"}}}
    contract={"project":state["project"], "goal":"Verified Finish", "sourcePins":{"guard":"3f2c"},
        "allowedMutations":["tools/example.py"], "executorIdentity":"existing-authorized-operator",
        "precheckBound":True,"postcheckBound":True,"testCommands":["unittest"],
        "donecheckBinding":"v1.2","githubPlan":"draft-pr","humanThreshold":"HUMAN_ONLY",
        "acceptanceCriteria":["T01","T02","T03","T04"]}
    steps=[]
    for i,key in enumerate(("T01","T02","T03","T04")):
        steps.append({"id":key,"owner":"HUMAN_ONLY" if key=="T04" else "existing-authorized-operator",
            "dependencies":[] if i==0 else ["T0"+str(i)],"holdConditions":["real-evidence-missing"],
            "passEvidence":["signed-or-sha256-receipt"],"authorizedRecovery":"bounded-in-gate",
            "status":"PENDING_HUMAN" if i==3 else "HOLD"})
    f={"schema":SCHEMA,"project":state["project"],"version":"2.3",
        "goal":contract["goal"],"sourcePins":contract["sourcePins"],
        "canonicalStateSha256":sha256_json(state),"humanThreshold":"HUMAN_ONLY",
        "steps":steps,
        "simulations":[{"scenario":x,"expectedState":"PENDING" if x=="HUMAN_DECISION_PENDING" else "HOLD"} for x in MANDATORY_SCENARIOS],
        "predictionVsObservation":"REQUIRED_POST_EXECUTION"}
    contract["finishPathForecast"]=f
    abilities={"authorizedExecutor":True,"realCallerBound":True,"testEnvironmentReady":True,
        "donecheckAvailable":True,"scopeAuthorized":True,"sourcePinsMatch":True,
        "simulationEvidence":"REAL_TEST_RECEIPT_REQUIRED","realCallerEvidence":"REAL_CALLER_RECEIPT_REQUIRED"}
    return state,contract,f,abilities

class ForesightTests(unittest.TestCase):
    def test_complete_path_structure(self):
        s,c,f,a=example(); self.assertEqual(validate_forecast(f,c,s)["state"],"PASS_FORECAST_STRUCTURE_ONLY")
    def test_readiness_requires_real_abilities(self):
        s,c,f,a=example();a["realCallerBound"]=False
        with self.assertRaisesRegex(ExecutionHold,"REAL_CALLER_BINDING_UNVERIFIED"):readiness(c,s,a)
    def test_readiness_structural_only(self):
        s,c,f,a=example(); self.assertEqual(readiness(c,s,a)["state"],"EXECUTION_READY")
    def test_forecast_missing(self):
        s,c,f,a=example(); del c["finishPathForecast"]
        with self.assertRaisesRegex(ExecutionHold,"FORECAST_MISSING_FORECAST"):readiness(c,s,a)
    def test_gate_missing(self):
        s,c,f,a=example();f["steps"].pop()
        with self.assertRaisesRegex(ValueError,"GATE_COUNT"):validate_forecast(f,c,s)
    def test_human_auto(self):
        s,c,f,a=example();f["steps"][-1]["status"]="PASS"
        with self.assertRaises(ValueError): validate_forecast(f,c,s)
    def test_fake_pass(self):
        s,c,f,a=example();f["steps"][0]["status"]="PASS"
        with self.assertRaisesRegex(ValueError,"UNVERIFIED_STEP_PASS"):validate_forecast(f,c,s)
    def test_incomplete_simulations(self):
        s,c,f,a=example();f["simulations"].pop()
        with self.assertRaisesRegex(ValueError,"SCENARIO_COVERAGE"):validate_forecast(f,c,s)
    def test_no_forward_dependency(self):
        s,c,f,a=example();f["steps"][0]["dependencies"]=["T03"]
        with self.assertRaisesRegex(ValueError,"DEPENDENCY_NOT_PRIOR"):validate_forecast(f,c,s)
    def test_source_drift(self):
        s,c,f,a=example();s["changed"]=True
        with self.assertRaisesRegex(ValueError,"STATE_PIN"):validate_forecast(f,c,s)
    def test_missing_scope(self):
        s,c,f,a=example();a["scopeAuthorized"]=False
        with self.assertRaisesRegex(ExecutionHold,"SCOPE_UNAUTHORIZED"):readiness(c,s,a)
    def test_negative_simulation(self):
        s,c,f,a=example(); self.assertEqual(simulate_missing_authority(f,c,s)["state"],"PASS")
    def test_prediction_cannot_claim_actual(self):
        s,c,f,a=example();r=validate_forecast(f,c,s)
        self.assertFalse(r["runtimeVerified"]);self.assertEqual(r["verifiedFinish"],"HOLD")

if __name__ == "__main__": unittest.main()
