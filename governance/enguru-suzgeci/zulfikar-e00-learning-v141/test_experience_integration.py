"""Real local integration: durable experience box -> E00 -> existing DÖM.

No second executor or official human authority is implemented. All processes
run in disposable local fixtures and remain isolated GitHub technical proofs.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from experience_box import ExperienceBox
from experience_learning import SCHEMA, SCOPE, run_isolated_learning


class ActualIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir=Path(self.tmp.name)
        self.source=self.dir/"goal.txt"
        self.source.write_text("SOURCE_1",encoding="utf8")
        self.artifact=self.dir/"artifact.json"
        self.artifact.write_text('{"ok":false}',encoding="utf8")
        self.journal=self.dir/"dom-journal"
        self.journal.mkdir()
        self.box=ExperienceBox(self.dir/"e00.sqlite3")
        self.addCleanup(self.box.close)
        self.expected_source=hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.event={"eventId":"EV-INT-01","goalId":"ZF-INT-01",
            "sourceSha256":self.expected_source, "domain":"CODE","kind":"FAILURE",
            "outcome":"NEGATIVE","need":"RELIABILITY",
            "description":"Broken source-bound artifact in isolated fixture",
            "lesson":"Verify output bytes and DÖM checkpoint before promotion"}
        self.box.put(self.event)
        self.box.triage("EV-INT-01",solution="repair local JSON output",
                       solution_ref="fixture/repair-v1")
        self.can_repair=True
        self.real_processes=0

    def worker(self,case,solution,round_number):
        event={"schema":SCHEMA,"eventId":case["eventId"],
            "goalId":case["goalId"],
            "userValue":"Repair existing source-bound artifact",
            "sourceSha256":case["sourceSha256"],
            "scope":SCOPE,"kind":case["kind"],"need":"RELIABILITY",
            "criteria":["artifact_correct"],"observedCriteria":{"artifact_correct":False},
            "lesson":case["lesson"]}
        def evaluate(state,contract):
            j=json.loads(self.artifact.read_text())
            return {"artifact_correct":j["ok"] is True and state["fixed"] is True}
        def repair(state,missing,contract):
            if self.can_repair:
                self.artifact.write_text('{"ok":true}',encoding="utf8")
                state["fixed"]=True
            return state
        def real_test(state,contract):
            self.real_processes+=1
            p=subprocess.run([sys.executable,"-B","-c",
                 "import hashlib,pathlib,sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())",
                 str(self.artifact)],capture_output=True,text=True,timeout=10,check=False)
            return {"processObserved":True,"exitCode":p.returncode,
                    "scope":SCOPE,"artifactSha256":p.stdout.strip(),
                    "artifactPath":str(self.artifact)}
        def separate_verify(state,contract,proof):
            return (proof["artifactSha256"]==hashlib.sha256(self.artifact.read_bytes()).hexdigest()
                and json.loads(self.artifact.read_text())["ok"] is True)
        return run_isolated_learning(
            event,self.source,self.journal,
            start_state={"artifactPath":str(self.artifact),"fixed":False},
            simulator=lambda state,contract:{"valid":True},
            evaluator=evaluate,repairer=repair,real_tester=real_test,
            independent_verifier=separate_verify,source_probe=lambda _:True,
            max_rounds=1)

    def test_01_real_existing_dom_repair_proves_technical_candidate(self):
        b=self.box.make_batch(["EV-INT-01"])["batchId"]
        result=self.box.assess_batch(b,self.worker,max_rounds=1)
        self.assertEqual(result["state"],"ISOLATED_BATCH_CANDIDATE")
        self.assertEqual(self.real_processes,1)
        self.assertEqual(self.box.summary()["attemptRecords"],1)
        self.assertEqual(self.box.summary()["states"]["CANDIDATE"],1)
        self.assertEqual(self.box.summary()["archived"],0)

    def test_02_failure_remains_until_corrected_then_real_dom_repairs(self):
        b=self.box.make_batch(["EV-INT-01"])["batchId"]
        self.can_repair=False
        first=self.box.assess_batch(b,self.worker,max_rounds=1)
        self.assertEqual(first["state"],"BATCH_HOLD")
        self.assertEqual(self.real_processes,0)
        self.assertEqual(self.box.summary()["states"]["HOLD"],1)
        self.box.diagnose("EV-INT-01",cause="Repair did not change artifact",
            gap="Criterion still false",requirement="Source-backed true JSON",
            correction="Install corrected bounded repair callback")
        self.box.retry_batch(b,{"EV-INT-01":{
            "solution":"Repair with fresh source-pinned callback",
            "solution_ref":"fixture/repair-v2"}})
        self.can_repair=True
        second=self.box.assess_batch(b,self.worker,max_rounds=1)
        self.assertEqual(second["state"],"ISOLATED_BATCH_CANDIDATE")
        self.assertEqual(self.real_processes,1)
        self.assertEqual(self.box.summary()["attemptRecords"],2)
        self.assertEqual(self.box.summary()["failureDiagnoses"],1)
        self.assertEqual(self.box.summary()["archived"],0)

    def test_03_source_drift_keeps_box_hold(self):
        self.source.write_text("SOURCE_CHANGED",encoding="utf8")
        b=self.box.make_batch(["EV-INT-01"])["batchId"]
        result=self.box.assess_batch(b,self.worker,max_rounds=1)
        self.assertEqual(result["state"],"BATCH_HOLD")
        self.assertEqual(self.real_processes,0)
        self.assertEqual(self.box.summary()["states"]["HOLD"],1)


if __name__=="__main__":
    unittest.main()
