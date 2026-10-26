"""Real Git HEAD source-bound HYM V1.4.1 A01 architecture + three repair simulations."""
import copy
import json
import hashlib
import pathlib
import subprocess
import tempfile
import unittest
from tools import arge_hym_v141_crosswalk_v1 as m


def baseline():
    h=json.loads((m.ROOT/m.HANDOFF).read_text(encoding="utf8"))
    cases=json.loads((m.ROOT/m.CASES).read_text(encoding="utf8"))
    manifest=json.loads((m.ROOT/m.A01_DESIGN_PATH).read_text(encoding="utf8"))
    method={"state":"PASS_METHOD_SOURCE_CROSSWALK_ONLY","verifiedFinish":"HOLD",
            "stageAcceptance":{s:"HOLD_STAGE_100_EVIDENCE_REQUIRED" for s in m.STAGES}}
    rootproof=m.proof_from_git()
    foundation=m.assess_foundations(h,cases,rootproof,method)
    designproof=m.proof_single_git_file()
    return h,cases,manifest,method,foundation,designproof


class HYMArchitectureV141Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h,cls.c,cls.design,cls.method,cls.foundation,cls.proof=baseline()

    def assess(self,manifest=None,h=None,c=None,method=None,foundation=None,proof=None):
        return m.assess_a01_architecture(
            self.design if manifest is None else manifest,
            self.h if h is None else h,
            self.c if c is None else c,
            self.proof if proof is None else proof,
            self.foundation if foundation is None else foundation,
            self.method if method is None else method)

    def test_real_git_source_and_five_architecture_outputs_100_preparation_only(self):
        self.assertEqual(self.proof["state"],"PASS_GIT_HEAD_DESIGN_BYTES_ONLY",self.proof)
        self.assertEqual(self.foundation["state"],"PASS_T01_T02_GITHUB_SOURCE_PREPARATION_ONLY")
        verdict=self.assess()
        self.assertEqual(verdict["state"],"PASS_A01_ARCHITECTURE_SOURCE_PREPARATION_ONLY",
                         verdict["checks"])
        self.assertEqual(verdict["score"],100)
        self.assertEqual(len(verdict["checks"]),5)
        self.assertEqual(verdict["original_a01"],"HOLD")
        self.assertEqual(verdict["method_a01"],"HOLD")
        self.assertEqual(verdict["verified_finish"],"HOLD")
        self.assertEqual(verdict["original_total"],"0/40")

    def family(self,tag,attacks):
        for name,kind,mutation,expected in attacks:
            with self.subTest(family=tag,name=name):
                d=copy.deepcopy(self.design)
                h=copy.deepcopy(self.h)
                c=copy.deepcopy(self.c)
                p=copy.deepcopy(self.proof)
                x={"m":d,"h":h,"c":c,"p":p}
                mutation(x[kind])
                v=self.assess(manifest=d,h=h,c=c,proof=p)
                self.assertEqual(v["state"],"HOLD_A01_DESIGN_SOURCE_PREPARATION")
                self.assertFalse(v["checks"][expected])
                self.assertLess(v["score"],100)
                self.assertEqual(v["verified_finish"],"HOLD")
                self.assertEqual(v["original_a01"],"HOLD")

    def test_sim1_component_source_transition_and_git_byte_drift(self):
        self.family("SIM1",(
            ("original_A01_missing","m",
                lambda x:x["architecture"]["components"].pop(0),"AD01_architecture"),
            ("fake_upstream_binding","m",
                lambda x:x["architecture"]["components"][3].update(
                    source_path="https://attacker.example/FAKE"),"AD01_architecture"),
            ("missing_dependency","m",
                lambda x:x["architecture"]["components"][0].update(
                    next_task="A09"),"AD01_architecture"),
            ("unverified_design_source","p",
                lambda x:x.update(state="HOLD_GIT_SOURCE_DRIFT"),"AD02_implementation_paths"),
        ))

    def test_sim2_18_cases_k01_k13_and_source_inventory(self):
        self.family("SIM2",(
            ("missing_case","c",lambda x:x["cases"].pop(),"AD03_source_bindings"),
            ("duplicate_case_id","c",
                lambda x:x["cases"][1].update(case_id="01"),"AD03_source_bindings"),
            ("domain_count_drift","c",
                lambda x:x["cases"][0].update(domain="Motor"),"AD03_source_bindings"),
            ("e5_forged","c",
                lambda x:x["cases"][0].update(independent_e5="PASS"),"AD03_source_bindings"),
            ("wrong_original_234","c",
                lambda x:x["baseline"].update(rows=233),"AD03_source_bindings"),
            ("swap_customers_same_domain","c",
                lambda x: (
                    x["cases"][0].update(customer=self.c["cases"][1]["customer"]),
                    x["cases"][1].update(customer=self.c["cases"][0]["customer"])),
                "AD03_source_bindings"),
            ("swap_technologies_same_domain","c",
                lambda x: (
                    x["cases"][0].update(technology=self.c["cases"][1]["technology"]),
                    x["cases"][1].update(technology=self.c["cases"][0]["technology"])),
                "AD03_source_bindings"),
            ("spoof_case_identity_digest","m",
                lambda x:x["sourceBindings"].update(original_case_identity_sha256="f"*64),
                "AD03_source_bindings"),
            ("forge_all_234_cell_acceptance","c",
                lambda x:x["baseline"].update(all_234_original_verdicts="PASS"),"AD03_source_bindings"),
            ("forge_18_independent_e5","c",
                lambda x:x["baseline"].update(all_18_e5_original_status="PASS"),"AD03_source_bindings"),
            ("forge_v19_baseline_reconciliation","c",
                lambda x:x["source_audit"].update(v19_exact_case_identity="RECONCILED_WITHOUT_CSV"),
                "AD03_source_bindings"),
        ))

    def test_sim3_owner_issuer_field_finish_and_recovery(self):
        self.family("SIM3",(
            ("owner_spoof","m",
                lambda x:x["securityBoundaries"].update(human_owner="fake"),"AD04_security_boundaries"),
            ("auto_merge","m",
                lambda x:x["securityBoundaries"].update(no_auto_merge=False),"AD04_security_boundaries"),
            ("new_issuer","m",
                lambda x:x["securityBoundaries"].update(issuer="SELF_ISSUER"),"AD04_security_boundaries"),
            ("e5_fake","h",
                lambda x:x["A05_A06"].update(independent_e5="18/18"),"AD04_security_boundaries"),
            ("lost_recovery","m",
                lambda x:x["recoveryPlan"].update(no_new_writer=False),"AD05_recovery_plan"),
            ("remove_swap_recovery","m",
                lambda x:x["recoveryPlan"].pop("customer_technology_swap"),"AD05_recovery_plan"),
        ))

    def test_identity_hash_uses_original_v428_case_fields(self):
        observed=[[r["case_id"],r["domain"],r["customer"],r["technology"]]
                  for r in self.c["cases"]]
        digest=hashlib.sha256(
            json.dumps(observed,ensure_ascii=False,separators=(",",":")).encode("utf8")
        ).hexdigest()
        self.assertEqual(len(observed),18)
        self.assertEqual(digest,m.A01_IDENTITY_PIN)
        self.assertEqual(self.design["sourceBindings"]["original_case_identity_sha256"],digest)
        # V428's original V19 comparison is an upstream claim; this test does
        # not independently open the separately stored original CSV.
        self.assertEqual(self.c["source_audit"]["v19_exact_case_identity"],
                         "18/18_RECONCILED_FROM_ORIGINAL_CSV")

    def test_real_disposable_git_head_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="hym-v141-a01-git-") as wd:
            root=pathlib.Path(wd)
            target=root/m.A01_DESIGN_PATH
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((m.ROOT/m.A01_DESIGN_PATH).read_bytes())
            for argv in (
                ["git","init","-q"],
                ["git","add","."],
                ["git","-c","user.name=Verification Fixture",
                 "-c","user.email=a01@example.invalid","commit","-qm","original design bytes"],
            ):
                subprocess.run(argv,cwd=root,check=True,timeout=15,capture_output=True)
            self.assertEqual(m.proof_single_git_file(root)["state"],
                             "PASS_GIT_HEAD_DESIGN_BYTES_ONLY")
            target.write_bytes(target.read_bytes()+b"\nmodified without commit\n")
            rejected=m.proof_single_git_file(root)
            self.assertEqual(rejected["state"],"HOLD")
            self.assertIn("ARCHITECTURE_GIT_HEAD_BYTES_DRIFT",rejected["reason"])

    def test_empty_or_malformed_inputs_produce_hold(self):
        for bad in ({},False,[],None):
            with self.subTest(value=repr(bad)):
                v=m.assess_a01_architecture(bad,self.h,self.c,self.proof,self.foundation,self.method)
                self.assertEqual(v["state"],"HOLD_A01_DESIGN_SOURCE_PREPARATION")
                self.assertEqual(v["verified_finish"],"HOLD")

if __name__=="__main__":
    unittest.main()
