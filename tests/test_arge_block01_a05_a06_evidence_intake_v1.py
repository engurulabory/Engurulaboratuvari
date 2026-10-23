"""A05/A06 real-file hash intake adversarial tests, original 18 V19 cases.

All material is synthetic; test success proves integrity screening only.
Never issue independent E5, deployment verification or official acceptance.
"""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.arge_block01_a05_a06_evidence_intake_v1 import SCHEMA, CANDIDATE, audit_packet, file_pin

CATALOG = Path(__file__).resolve().parents[1] / "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_18_CASE_RECONCILIATION_V428.json"

def pinned(root, relative, payload):
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return relative, hashlib.sha256(payload).hexdigest()

class A05A06EvidenceIntake(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root=Path(self.folder.name)
        self.catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
        self.packet={"schema":SCHEMA,
                     "baseline_sha256":self.catalog["baseline"]["sha256"],
                     "cases":[]}
        for item in self.catalog["cases"]:
            cid=item["case_id"]
            manifests=pinned(self.root, cid+"/deployed.json",
                             json.dumps({"deployment":cid}).encode())
            sbom=pinned(self.root, cid+"/sbom.json",
                        json.dumps({"bomFormat":"CycloneDX","specVersion":"1.5","components":[]}).encode())
            owner=pinned(self.root, cid+"/owner.json",json.dumps({"owner":cid}).encode())
            owner_sig=pinned(self.root, cid+"/owner.sig",b"unsigned-test-owner-"+cid.encode())
            report=pinned(self.root, cid+"/e5-report.json",json.dumps({"independent_observation":cid}).encode())
            e5=pinned(self.root, cid+"/e5.json",json.dumps({"observer":cid}).encode())
            e5_sig=pinned(self.root, cid+"/e5.sig",b"unsigned-test-e5-"+cid.encode())
            self.packet["cases"].append({
                "case_id":cid,"customer":item["customer"],"technology":item["technology"],
                "deployment":{
                    "release":"test-only","edition":"unknown-test",
                    "source_commit":"a"*40,"customer_owner_id":"test-owner-"+cid,
                    "deployed_manifest":manifests[0],"manifest_sha256":manifests[1],
                    "customer_sbom":sbom[0],"sbom_sha256":sbom[1],
                    "customer_assertion":owner[0],"customer_assertion_sha256":owner[1],
                    "customer_signature":owner_sig[0],"customer_signature_sha256":owner_sig[1],
                },
                "e5":{
                    "verifier_identity":"test-external-reviewer-"+cid,
                    "verifier_organization":"Independent Test Labs",
                    "observed_at":"2026-10-20T09:00:00+03:00",
                    "report":report[0],"report_sha256":report[1],
                    "verifier_assertion":e5[0],"verifier_assertion_sha256":e5[1],
                    "verifier_signature":e5_sig[0],"verifier_signature_sha256":e5_sig[1],
                }
            })

    def test_complete_synthetic_files_never_pass_authority(self):
        result=audit_packet(self.catalog,self.packet,self.root)
        self.assertEqual(result["state"],"HOLD_EXTERNAL_SIGNATURE_AND_AUTHORITY")
        self.assertEqual(result["a05_files_hash_matched_untrusted"],18)
        self.assertEqual(result["a06_files_hash_matched_untrusted"],18)
        self.assertEqual(result["a05_official_verified"],0)
        self.assertEqual(result["a06_independent_e5_verified"],0)
        self.assertEqual(result["official_block01_pass"],"0/9")
        self.assertEqual({x["a05"] for x in result["cases"]},{CANDIDATE})

    def test_20_percent_missing_cases_holds(self):
        for start in range(15):
            p=copy.deepcopy(self.packet)
            del p["cases"][start:start+4]
            self.assertEqual(audit_packet(self.catalog,p,self.root)["state"],
                             "HOLD_18_CASE_DELIVERY")

    def test_duplicate_case_identity_holds(self):
        p=copy.deepcopy(self.packet)
        p["cases"][3]["case_id"]="01"
        self.assertEqual(audit_packet(self.catalog,p,self.root)["state"],
                         "HOLD_DUPLICATE_OR_UNKNOWN_CASE")

    def test_customer_and_tech_identity_tampering_holds(self):
        p=copy.deepcopy(self.packet)
        p["cases"][2]["technology"]="Arbitrary"
        x=audit_packet(self.catalog,p,self.root)
        self.assertEqual(x["cases"][2]["a05"],"HOLD_IDENTITY_DRIFT")
        self.assertEqual(x["cases"][2]["a06"],"HOLD_IDENTITY_DRIFT")

    def test_tampered_real_file_fails_hash(self):
        file=self.root/"01/deployed.json"
        file.write_bytes(b"changed after digest")
        x=audit_packet(self.catalog,self.packet,self.root)
        self.assertEqual(x["cases"][0]["a05"],"HOLD_FILE_SHA256_MISMATCH")
        self.assertEqual(x["a05_files_hash_matched_untrusted"],17)

    def test_missing_signature_file_keeps_hold(self):
        (self.root/"01/e5.sig").unlink()
        x=audit_packet(self.catalog,self.packet,self.root)
        self.assertEqual(x["cases"][0]["a06"],"HOLD_FILE_READ_OR_SCHEMA")
        self.assertEqual(x["a06_independent_e5_verified"],0)

    def test_wrong_customer_same_verifier_org_holds(self):
        p=copy.deepcopy(self.packet)
        p["cases"][0]["e5"]["verifier_organization"]="Bookshop.org"
        x=audit_packet(self.catalog,p,self.root)
        self.assertEqual(x["cases"][0]["a06"],
                         "HOLD_DECLARED_VERIFIER_IS_CUSTOMER_OR_VENDOR")

    def test_futureless_timestamp_holds(self):
        p=copy.deepcopy(self.packet)
        p["cases"][0]["e5"]["observed_at"]="2026-10-20"
        x=audit_packet(self.catalog,p,self.root)
        self.assertEqual(x["cases"][0]["a06"],"HOLD_OBSERVATION_TIMESTAMP")

    def test_invalid_sbom_is_explicit_hold(self):
        p=copy.deepcopy(self.packet)
        name=p["cases"][0]["deployment"]["customer_sbom"]
        (self.root/name).write_text('{"not":"SBOM"}',encoding="utf-8")
        p["cases"][0]["deployment"]["sbom_sha256"]=hashlib.sha256((self.root/name).read_bytes()).hexdigest()
        self.assertEqual(audit_packet(self.catalog,p,self.root)["cases"][0]["a05"],"HOLD_SBOM_FORMAT")

    def test_symlink_escapes_rejected_even_when_sha_correct(self):
        data=b"malicious outside scope"
        outside=Path(self.folder.name)/"other-file.txt"
        outside.write_bytes(data)
        symlink=self.root/"01/linked.txt"
        symlink.symlink_to(outside)
        self.assertEqual(file_pin(self.root,"01/linked.txt",hashlib.sha256(data).hexdigest()),"HOLD_SYMLINK")
        self.assertEqual(file_pin(self.root,"../other-file.txt",hashlib.sha256(data).hexdigest()),"HOLD_FILE_PATH_SCOPE")

    def test_catalog_sha_tamper_holds(self):
        catalog=copy.deepcopy(self.catalog)
        catalog["baseline"]["sha256"]="a"*64
        self.assertEqual(audit_packet(catalog,self.packet,self.root)["state"],
                         "HOLD_ORIGINAL_V19_BASELINE")

    def test_unsigned_assertion_is_not_signature_authority(self):
        out=audit_packet(self.catalog,self.packet,self.root)
        self.assertEqual(out["a06_independent_e5_verified"],0)
        self.assertEqual(out["official_block01_pass"],"0/9")

if __name__=="__main__":
    unittest.main()
