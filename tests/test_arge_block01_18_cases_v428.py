"""18-case V19 evidence reconciliation, GitHub-only review."""
import json
import unittest
from pathlib import Path
P = Path(__file__).resolve().parents[1] / "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_18_CASE_RECONCILIATION_V428.json"
REQUIRED = ("independent_e5", "g01", "g02", "g03", "k12", "exact_customer_deployment_sha")
def exit_decision(data):
    entries = data.get("cases", [])
    if len(entries) != 18 or {x.get("case_id") for x in entries} != {f"{i:02d}" for i in range(1,19)}:
        return "HOLD_SCOPE"
    if data.get("baseline", {}).get("rows") != 234:
        return "HOLD_BASELINE"
    if any(x.get(field) != "PASS_VERIFIED" for x in entries for field in REQUIRED):
        return "HOLD_REAL_EVIDENCE"
    return "SIMULATION_ONLY_NO_AUTHORIZED_FINISH"
class ReconciliationTests(unittest.TestCase):
    def setUp(self): self.record=json.loads(P.read_text(encoding="utf-8"))
    def test_baseline(self):
        self.assertEqual(len(self.record["cases"]),18)
        self.assertEqual(self.record["rollup"]["independent_e5_pass"],0)
        self.assertEqual(exit_decision(self.record),"HOLD_REAL_EVIDENCE")
    def test_twenty_percent_four_missing_cases(self):
        for first in range(0,15):
            x=dict(self.record)
            x["cases"]=self.record["cases"][:first]+self.record["cases"][first+4:]
            self.assertEqual(exit_decision(x),"HOLD_SCOPE")
    def test_each_evidence_type_failure(self):
        for field in REQUIRED:
            x=dict(self.record)
            x["cases"]=[dict(v, **{g:"PASS_VERIFIED" for g in REQUIRED}) for v in self.record["cases"]]
            x["cases"][0][field]="HOLD"
            self.assertEqual(exit_decision(x),"HOLD_REAL_EVIDENCE")
    def test_fully_simulated_state_stays_unofficial(self):
        x=dict(self.record)
        x["cases"]=[dict(v,**{g:"PASS_VERIFIED" for g in REQUIRED}) for v in self.record["cases"]]
        self.assertEqual(exit_decision(x),"SIMULATION_ONLY_NO_AUTHORIZED_FINISH")
    def test_all_customer_technology_pairs_match_original(self):
        expected = [
            ("Bookshop.org","Meilisearch"), ("Matt Sleeps","Medusa"), ("Lush","Saleor"),
            ("Mobbin","Supabase"), ("Resend","Supabase"), ("Hugging Face Hub","Meilisearch"),
            ("Replit Agent","Temporal"), ("Auth0 FGA","OpenFGA"), ("Headspace","OpenFGA"),
            ("Xendit","Supabase"), ("Mapped","OpenFGA"), ("Temporal Cloud","Temporal"),
            ("Klarna","LangGraph"), ("LinkedIn","LangGraph"), ("Uber","LangGraph"),
            ("Tekla","Medusa"), ("Fastweb + Vodafone","LangGraph"), ("BFI Finance","Temporal")
        ]
        actual = [(entry["customer"],entry["technology"]) for entry in self.record["cases"]]
        self.assertEqual(actual,expected)
        self.assertEqual(self.record["baseline"]["sha256"],"3906f7bd6ae07d26547babc172d1337cfdfeff85244ece95efb76c3cb448df08")
        self.assertEqual(self.record["baseline"]["all_234_original_verdicts"],"HOLD")

    def test_public_witness_coverage_is_complete_but_unofficial(self):
        for case in self.record["cases"]:
            with self.subTest(case_id=case["case_id"]):
                witness = case["current_public_source"]
                self.assertTrue(witness["url"].startswith("https://"))
                self.assertNotEqual(witness["source_class"],"INDEPENDENT_E5")
                self.assertEqual(witness["independent_E5_attestation"],"HOLD_NOT_ESTABLISHED")
                self.assertEqual(witness["customer_deployment_commit_sha256"],"HOLD_NOT_ESTABLISHED")
                self.assertEqual(witness["k12_ENGURU_NET_TCO"],"HOLD_NOT_MEASURED")
        self.assertEqual(self.record["rollup"]["public_source_candidates"],18)
        self.assertEqual(self.record["rollup"]["independent_e5_pass"],0)
        self.assertEqual(self.record["rollup"]["exact_deployment_sha_pass"],0)

    def test_replit_temporal_to_restate_transition_flagged(self):
        conflicts=self.record["source_conflicts"]
        self.assertTrue(any(c["case_id"]=="07" and c["acceptance"]=="HOLD_ON_CURRENT_TEMPORAL_USAGE" for c in conflicts))
        self.assertEqual(self.record["cases"][6]["current_public_source"]["freshness"],"HISTORICAL_SUPERSEDED_CLAIM")

if __name__=="__main__": unittest.main()
