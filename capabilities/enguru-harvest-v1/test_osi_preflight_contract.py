import json
import unittest
from pathlib import Path
from osi_preflight_contract import classify
HERE=Path(__file__).resolve().parent
ENTRY=json.loads((HERE/"osi_entry_preparation.json").read_text(encoding="utf-8"))
class FieldScopeTests(unittest.TestCase):
    def test_actual_readiness(self):
        self.assertEqual(classify(ENTRY)["state"],"PASS_PREPARATION_ONLY")
    def test_live_mac_not_claimed(self):
        self.assertIs(classify(ENTRY)["field_authorized"],False)
        self.assertEqual(classify(ENTRY)["osi_execution"],0)
    def test_no_false_field_pass(self):
        for key in ("owner_entry_approval","field_action_authorization","github_official_verified_finish"):
            x={**ENTRY,key:"PASS"}
            self.assertEqual(classify(x)["state"],"HOLD_SCOPE_OR_AUTHORITY")
    def test_source_rights(self):
        self.assertEqual(classify({**ENTRY,"source_and_license_authorization":"PASS"})["state"],"HOLD_SCOPE_OR_AUTHORITY")
    def test_no_fake_mac(self):
        for key in ("mac_hardware_verified","mac_environment_verified","sqlite_receipt_field_test_verified"):
            self.assertEqual(classify({**ENTRY,key:True})["state"],"HOLD_SCOPE_OR_AUTHORITY")
    def test_execution_exact_integer_zero(self):
        for val in (1,False,"0"):
            self.assertEqual(classify({**ENTRY,"osi_execution_count":val})["state"],"HOLD_SCOPE_OR_AUTHORITY")
    def test_originals_protected(self):
        self.assertEqual(classify({**ENTRY,"no_original_file_overwrite":False})["state"],"HOLD_SCOPE_OR_AUTHORITY")
    def test_wrong_first_step(self):
        self.assertEqual(classify({**ENTRY,"first_allowed_action_if_authorized":"WRITE_TO_MAC"})["state"],"HOLD_SCOPE_OR_AUTHORITY")
    def test_rollback(self):
        self.assertEqual(classify({**ENTRY,"rollback":"DELETE_ORIGINALS"})["state"],"HOLD_SCOPE_OR_AUTHORITY")
    def test_wrong_order(self):
        bad={**ENTRY,"preflight_checks":list(reversed(ENTRY["preflight_checks"]))}
        self.assertEqual(classify(bad)["state"],"HOLD_STAGE_ORDER")
    def test_budget_and_owner(self):
        for key,value in (("mandatory_paid_api",1),("one_owner",False)):
            self.assertEqual(classify({**ENTRY,key:value})["state"],"HOLD_SCOPE_OR_AUTHORITY")
    def test_malformed(self):
        self.assertEqual(classify(None)["state"],"HOLD_SCHEMA")
if __name__=="__main__":
    unittest.main()
