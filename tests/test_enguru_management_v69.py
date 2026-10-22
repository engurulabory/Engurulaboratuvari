"""Tests for isolated ENGURU Management V6.9 reporting."""
import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).resolve().parents[1] / "tools" / "enguru_management_v69.py"
spec = importlib.util.spec_from_file_location("enguru_management_v69", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def task(id, state="READY", deps=None):
    return {"task_id":id,"goal":"Controlled management review","state":state,
            "dependencies":deps or [],"source_ref":"main/example",
            "source_sha256":"a"*64,"evidence":{"verified":False},
            "verifier":{"verified":False},"authority":{"verified":False}}

class ManagementTests(unittest.TestCase):
    def test_empty_worklist(self):
        self.assertEqual(mod.evaluate({"tasks":[]})["state"], "MANAGEMENT_REVIEW_ONLY")
    def test_missing_data_hold(self):
        self.assertEqual(mod.evaluate({"tasks":[{"task_id":"a"}]})["reason"], "MISSING_REQUIRED_FIELD")
    def test_duplicate_id_hold(self):
        self.assertEqual(mod.evaluate({"tasks":[task("A"),task("A") ]})["reason"],"DUPLICATE_OR_INVALID_ID")
    def test_wrong_digest_hold(self):
        a=task("A");a["source_sha256"]="fake"
        self.assertEqual(mod.evaluate({"tasks":[a]})["reason"],"SOURCE_DIGEST_REQUIRED")
    def test_cycle_hold(self):
        self.assertEqual(mod.evaluate({"tasks":[task("A",deps=["B"]),task("B",deps=["A"])]})["reason"],"DEPENDENCY_CYCLE")
    def test_unknown_dependency_hold(self):
        self.assertEqual(mod.evaluate({"tasks":[task("A",deps=["MISSING"])]})["reason"],"INVALID_DEPENDENCY")
    def test_paused_excluded(self):
        r=mod.evaluate({"tasks":[task("A","PAUSED"),task("B","READY")]})
        self.assertEqual(r["ready_candidates"],["B"])
    def test_fake_accepted_not_counted(self):
        r=mod.evaluate({"tasks":[task("A","ACCEPTED")]})
        self.assertEqual(r["record_declared_accepted"],0)
    def test_self_review_not_counted(self):
        a=task("A","ACCEPTED");a["executor_id"]="same"
        for key in ("evidence","verifier","authority"):
            a[key]={"verified":True}
        a["verifier"]["identity"]="same"
        self.assertEqual(mod.evaluate({"tasks":[a]})["record_declared_accepted"],0)
    def test_explicitly_marked_records_not_real_acceptance(self):
        a=task("A","ACCEPTED");a["executor_id"]="executor"
        for key in ("evidence","verifier","authority"):
            a[key]={"verified":True}
        a["verifier"]["identity"]="separate"
        r=mod.evaluate({"tasks":[a]})
        self.assertEqual(r["record_declared_accepted"],1)
        self.assertEqual(r["evidence_authority"],"UNVERIFIED_INPUT_RECORDS")
    def test_dependencies(self):
        a=task("A","ACCEPTED");a["executor_id"]="executor"
        for key in ("evidence","verifier","authority"):
            a[key]={"verified":True}
        a["verifier"]["identity"]="separate"
        b=task("B","READY",["A"])
        r=mod.evaluate({"tasks":[a,b]})
        self.assertEqual(r["ready_candidates"],["B"])
    def test_hash_repeatable(self):
        self.assertEqual(mod.digest({"a":1,"b":2}),mod.digest({"b":2,"a":1}))

if __name__=="__main__":
    unittest.main()
