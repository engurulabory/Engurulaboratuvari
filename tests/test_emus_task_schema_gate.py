import copy
import unittest
from tools.emus_task_schema_gate import validate,REQUIRED
FIX={"CONTROL_ID":"GH-05","TASK_ID":"GH-05","SOURCE_REPO":"engurulabory/Engurulaboratuvari",
"SOURCE_COMMIT":"0"*40,"ACCEPTANCE_VERSION":"V1","REQUIRED_EVIDENCE":["CI:run"],
"INDEPENDENT_VERIFIER":"UNVERIFIED","OWNER_AUTHORITY":"UNVERIFIED",
"EXECUTION_STATE":"HOLD","EVIDENCE_STATE":"HOLD","AUTHORITY_STATE":"HOLD","NEXT_ACTION":"Independent test"}
class SchemaTests(unittest.TestCase):
    def test_valid_hold_fixture(self):self.assertEqual(validate(FIX),[])
    def test_missing_every_required_field(self):
        for name in REQUIRED:
            with self.subTest(name=name):
                r=copy.deepcopy(FIX);r.pop(name)
                self.assertTrue(validate(r))
    def test_wrong_id(self):
        r=copy.deepcopy(FIX);r["TASK_ID"]="GH-20";self.assertTrue(validate(r))
    def test_wrong_commit(self):
        r=copy.deepcopy(FIX);r["SOURCE_COMMIT"]="unverified";self.assertTrue(validate(r))
    def test_authority_without_grant(self):
        r=copy.deepcopy(FIX);r["AUTHORITY_STATE"]="PASS"
        self.assertIn("UNAUTHORIZED_ACCEPTANCE",validate(r))
