"""Review-only Block 01 provenance inventory verification."""
import json
import hashlib
import copy
import unittest
from itertools import combinations
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_PROVENANCE_V425.json"
IDS = {f"A{x:02d}" for x in range(1, 10)}
ROOT = FILE.parents[3]
A04_PARTIAL = ("A04", "license_security_review")
PINNED_BLOB = "86dbf7a09997854019448a3a8266f1de1885694f"

def reconcile(value):
    categories=value.get("required_categories", {})
    if set(categories) != IDS: return "HOLD_SCOPE"
    expected={(task, category) for task, names in categories.items() for category in names}
    entries=value.get("unverified_categories", [])
    observed={(e.get("task_id"),e.get("category")) for e in entries}
    if len(entries)!=len(expected) or observed!=expected: return "HOLD_PROVENANCE_GAP"
    for e in entries:
        k=(e.get("task_id"), e.get("category"))
        want="HOLD_PARTIAL_RESEARCH_SOURCE_VERIFIED" if k==A04_PARTIAL else "HOLD_SOURCE_NOT_VERIFIED"
        if e.get("state")!=want: return "HOLD_UNEXPECTED_PROVENANCE_STATUS"
    if value.get("verified_sources"): return "HOLD_INDEPENDENT_AUTHENTICATION"
    proofs=value.get("partial_research_source_proofs",{})
    if set(proofs)!={"A04.license_security_review"}: return "HOLD_PARTIAL_PROOF_SCOPE"
    proof=proofs["A04.license_security_review"]
    if proof.get("state")!="PASS_SCOPED_SOURCE_PROVENANCE_ONLY":return "HOLD_PARTIAL_PROOF_LEVEL"
    if proof.get("scope")!="SEVEN_UPSTREAM_REPOS_SOURCE_ONLY_NOT_CUSTOMER_PRODUCT":
        return "HOLD_PARTIAL_PROOF_LEVEL"
    manifest=ROOT / str(proof.get("source_pins_manifest",""))
    if not manifest.is_file():return "HOLD_SOURCE_PIN_MISSING"
    body=manifest.read_bytes()
    calculated=hashlib.sha1(b"blob "+str(len(body)).encode()+b"\\0"+body).hexdigest()
    if calculated!=proof.get("source_pins_manifest_git_blob_sha1") or calculated!=PINNED_BLOB:
        return "HOLD_SOURCE_PIN_DRIFT"
    counts=proof.get("source_counts",{})
    if counts!={"upstream_repos":7,"license_and_security_files_byte_match":13,
                "dependency_seed_files_byte_match":7}:return "HOLD_PARTIAL_PROOF_COUNTS"
    osv=proof.get("source_scoped_osv",{})
    if (osv.get("component_candidates_queried")!=3559 or
        osv.get("package_advisory_matches")!=216 or
        osv.get("distinct_advisory_ids")!=188 or
        osv.get("classified_metadata_ids")!=188 or
        osv.get("disposable_patch_regression")!="PASS_PROXY_ADDR_2_0_7_TO_2_0_8"):
        return "HOLD_PARTIAL_PROOF_COUNTS"
    if (proof.get("exact_pr_head_tested")!="0f84e7181a5dc15d6a9212c458d786c4be1f57ed"
        or not proof.get("exact_ci_url","").endswith("/actions/runs/40206547243")):
        return "HOLD_UNPINNED_CI"
    refs=proof.get("source_proof_refs",[])
    if len(refs)!=5 or any(not (ROOT/str(p)).is_file() for p in refs):
        return "HOLD_SOURCE_PROOF_REF"
    holds=proof.get("original_acceptance_remaining",{})
    needed={"kasifi_canonical_source":"HOLD", "official_A04":"HOLD",
            "real_installed_version":"HOLD","customer_deployment_sbom":"HOLD",
            "legal_license_clearance":"HOLD", "customer_e5":"HOLD_0_OF_18",
            "mac_osi_field":"HOLD","donecheck_human":"HOLD"}
    if holds!=needed:return "HOLD_PREMATURE_ACCEPTANCE"
    if value.get("acceptance")!="HOLD" or value.get("osi")!="NOT_STARTED": return "HOLD_PREMATURE_ACCEPTANCE"
    return "INVENTORY_PARTIAL_SOURCE_PROVEN_ACCEPTANCE_HOLD"

class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.item=json.loads(FILE.read_text(encoding="utf-8"))
    def test_inventory_complete(self):
        self.assertEqual(reconcile(self.item),"INVENTORY_PARTIAL_SOURCE_PROVEN_ACCEPTANCE_HOLD")
    def test_pair_loss_20_percent(self):
        for ids in combinations(sorted(IDS),2):
            with self.subTest(ids=ids):
                x=dict(self.item)
                x["required_categories"]={k:v for k,v in self.item["required_categories"].items() if k not in ids}
                self.assertEqual(reconcile(x),"HOLD_SCOPE")
    def test_missing_provenance_holds(self):
        for idx in range(len(self.item["unverified_categories"])):
            with self.subTest(idx=idx):
                x=dict(self.item)
                x["unverified_categories"]=self.item["unverified_categories"][:idx]+self.item["unverified_categories"][idx+1:]
                self.assertEqual(reconcile(x),"HOLD_PROVENANCE_GAP")
    def test_scope_and_authority_mutations_hold(self):
        for change in ("unverified","wrong_scope","fake_complete","wrong_sha",
                       "wrong_ci","source_removed","fake_official","wrong_count"):
            with self.subTest(change=change):
                x=copy.deepcopy(self.item)
                evidence=x["partial_research_source_proofs"]["A04.license_security_review"]
                if change=="unverified":
                    next(r for r in x["unverified_categories"] if r["task_id"]=="A04"
                         and r["category"]=="license_security_review")["state"]="PASS"
                elif change=="wrong_scope":evidence["scope"]="COMPLETE_PRODUCT_SBOM"
                elif change=="fake_complete":evidence["state"]="PASS_OFFICIAL"
                elif change=="wrong_sha":evidence["source_pins_manifest_git_blob_sha1"]="a"*40
                elif change=="wrong_ci":evidence["exact_ci_url"]="https://github.com/other/run/123"
                elif change=="source_removed":evidence["source_proof_refs"]=[]
                elif change=="fake_official":evidence["original_acceptance_remaining"]["official_A04"]="PASS"
                elif change=="wrong_count":evidence["source_scoped_osv"]["component_candidates_queried"]=1
                self.assertNotEqual(reconcile(x),
                                    "INVENTORY_PARTIAL_SOURCE_PROVEN_ACCEPTANCE_HOLD")

    def test_claimed_verified_source_needs_independent_validation(self):
        x=dict(self.item)
        x["verified_sources"]={"A03":"SELF_ASSERTED"}
        self.assertEqual(reconcile(x),"HOLD_INDEPENDENT_AUTHENTICATION")

if __name__=="__main__":
    unittest.main()
