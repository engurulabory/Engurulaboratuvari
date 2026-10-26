"""Read-only three-task receipt intake. Synthetic fixtures cannot become field PASS."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from zulfikar_v131_field_evidence_intake import audit_manifest,format_receipt,load_json,SHA256,sha256

HERE=Path(__file__).resolve().parent
EXE=HERE/"zulfikar_v131_field_evidence_intake.py"
FAMILIES=("NATIVE_SWIFTUI_PRODUCT","LOCAL_RECOVERY_IDEMPOTENCY","WEB_BUILD_TEST_REPAIR")


def make_bundle(root:Path):
    tasks=[]
    for i,family in enumerate(FAMILIES,1):
        name=f"receipt_{i}.json"
        rec={"schema":"enguru.zulfikar.external-task-observation/v1",
             "taskId":f"TASK.{i}","workId":f"W.{i}","family":family,
             "sourceRepo":"repo.example","registeredHandler":f"HANDLER.{i}",
             "contractId":f"C.{i}","sourceHead":"a"*40,
             "preStateSha256":"1"*64,"postStateSha256":"2"*64,
             "actualOutputDigest":"3"*64,"claimedTaskExecuted":True,
             "testReturnCode":0,"testCount":3,
             "independentReviewState":"EXTERNAL_REVIEW_REQUIRED",
             "officialVerifiedFinish":"HOLD","ownerDecision":"PENDING"}
        raw=(json.dumps(rec,sort_keys=True)+"\n").encode()
        (root/name).write_bytes(raw)
        tasks.append({"taskId":rec["taskId"],"family":family,
                      "sourceHead":rec["sourceHead"],"receiptFile":name,
                      "receiptSha256":sha256(raw)})
    manifest={"schema":"enguru.zulfikar.field-evidence-bundle/v1",
              "tasks":tasks,"realMacAuthorityVerified":False,"humanThreshold":"HOLD"}
    (root/"manifest.json").write_text(json.dumps(manifest),encoding="utf-8")
    return manifest


class EvidenceIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.manifest=make_bundle(self.root)

    def verdict(self):
        return audit_manifest(self.manifest,self.root)

    def mutate_receipt(self,i,callback):
        name=f"receipt_{i}.json"
        path=self.root/name
        item=json.loads(path.read_text())
        callback(item)
        data=json.dumps(item,sort_keys=True).encode()
        path.write_bytes(data)
        self.manifest["tasks"][i-1]["receiptSha256"]=sha256(data)

    def test_positive_byte_reconciliation_is_still_unverified(self):
        r=self.verdict()
        self.assertEqual(r["evidenceByteReconciliation"],"CANDIDATE_REVIEW_ONLY")
        self.assertEqual(r["claimedTaskObservationsWithMatchingBytes"],3)
        self.assertEqual(r["independentlyVerifiedRealTaskCount"],0)
        self.assertFalse(r["ownerIdentityCryptographicallyAuthenticated"])
        self.assertEqual(r["verifiedFinish"],"HOLD")

    def test_all_three_families_are_required(self):
        self.manifest["tasks"].pop()
        self.assertEqual(self.verdict()["evidenceByteReconciliation"],"HOLD")

    def test_duplicate_family_blocks(self):
        self.manifest["tasks"][1]["family"]=FAMILIES[0]
        self.assertIn("DUPLICATE_FAMILY_OR_TASK",self.verdict()["holds"])

    def test_duplicate_task_blocks(self):
        self.manifest["tasks"][1]["taskId"]="TASK.1"
        self.assertIn("DUPLICATE_FAMILY_OR_TASK",self.verdict()["holds"])

    def test_wrong_receipt_pin_blocks(self):
        self.manifest["tasks"][0]["receiptSha256"]="f"*64
        self.assertIn("RECEIPT_PIN_MISMATCH",self.verdict()["holds"])

    def test_wrong_source_head_blocks(self):
        self.manifest["tasks"][0]["sourceHead"]="b"*40
        self.assertIn("SOURCE_HEAD_MISMATCH",self.verdict()["holds"])

    def test_wrong_task_id_blocks(self):
        self.manifest["tasks"][0]["taskId"]="TASK.999"
        self.assertIn("TASK_ID_MISMATCH",self.verdict()["holds"])

    def test_claimed_human_signature_blocks(self):
        self.mutate_receipt(1,lambda x:x.update(ownerDecision="ACCEPTED"))
        self.assertIn("CLAIMED_OWNER_APPROVAL",self.verdict()["holds"])

    def test_fake_official_pass_blocks(self):
        self.mutate_receipt(1,lambda x:x.update(officialVerifiedFinish="PASS"))
        self.assertIn("PREMATURE_OFFICIAL_FINISH",self.verdict()["holds"])

    def test_bad_test_exit_blocks(self):
        self.mutate_receipt(1,lambda x:x.update(testReturnCode=1))
        self.assertIn("NO_TEST_EXIT_ZERO_CLAIM",self.verdict()["holds"])

    def test_bool_test_count_blocks(self):
        self.mutate_receipt(1,lambda x:x.update(testCount=True))
        self.assertIn("NO_TEST_COUNT_CLAIM",self.verdict()["holds"])

    def test_weird_test_count_list_blocks(self):
        self.mutate_receipt(1,lambda x:x.update(testCount=[]))
        self.assertIn("NO_TEST_COUNT_CLAIM",self.verdict()["holds"])

    def test_unauthorized_manifest_promotion_blocks(self):
        self.manifest["humanThreshold"]="PASS"
        self.assertIn("PREMATURE_AUTHORITY_IN_MANIFEST",self.verdict()["holds"])

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            load_json(b'{"a":1,"a":2}')

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            load_json(b'{"a":NaN}')

    def test_symlink_receipt_blocks(self):
        path=self.root/"receipt_1.json"
        source=self.root/"content.txt"
        source.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(source)
        self.assertIn("RECEIPT_UNREADABLE_OR_INVALID",self.verdict()["holds"])

    def test_bad_plan_type_hold_no_crash(self):
        self.manifest["tasks"][0]["family"]=[]
        self.assertEqual(self.verdict()["evidenceByteReconciliation"],"HOLD")

    def test_wrong_record_schema_hold(self):
        self.mutate_receipt(1,lambda x:x.update(schema="fake"))
        self.assertIn("INVALID_RECEIPT_SCHEMA",self.verdict()["holds"])

    def test_three_task_cli_is_not_authority(self):
        proc=subprocess.run([sys.executable,"-B",str(EXE),"--bundle",str(self.root)],
                            capture_output=True,text=True,timeout=20)
        self.assertEqual(proc.returncode,0,proc.stderr)
        result=json.loads(proc.stdout)
        self.assertEqual(result["independentlyVerifiedRealTaskCount"],0)
        self.assertEqual(result["verifiedFinish"],"HOLD")

    def test_bad_manifest_cli_hold(self):
        (self.root/"manifest.json").write_text("{broken",encoding="utf-8")
        proc=subprocess.run([sys.executable,"-B",str(EXE),"--bundle",str(self.root)],
                            capture_output=True,text=True,timeout=20)
        self.assertEqual(proc.returncode,2)
        self.assertEqual(json.loads(proc.stdout)["verifiedFinish"],"HOLD")

    def test_source_sha_wrong_type_hold(self):
        self.manifest["tasks"][0]["sourceHead"]={}
        self.assertIn("INVALID_EXPECTED_HEAD",self.verdict()["holds"])

    def test_really_empty_receipt_blocks(self):
        (self.root/"receipt_1.json").write_bytes(b"")
        self.assertIn("RECEIPT_PIN_MISMATCH",self.verdict()["holds"])


if __name__=="__main__":
    unittest.main(verbosity=2)
