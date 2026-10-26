"""OSi entry preflight is a scoped design verifier; never calls Mac."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXPECTED={
"schema":"enguru.harvest.osi-entry-preparation/v1",
"repository":"engurulabory/Engurulaboratuvari",
"source_pr":243,"status":"PREPARATION_ONLY","osi_execution_count":0,
"mac_hardware_verified":False,"mac_environment_verified":False,
"sqlite_receipt_field_test_verified":False,"owner_entry_approval":"HOLD",
"github_official_verified_finish":"HOLD","source_and_license_authorization":"HOLD",
"source_archive_pin_status":"HOLD","field_action_authorization":"HOLD",
"first_allowed_action_if_authorized":"READ_ONLY_ENVIRONMENT_INVENTORY",
"rollback":"ISOLATED_BRANCH_REVERT_AND_ORIGINAL_COPY_WITH_SHA",
"one_owner":True,"mandatory_paid_api":0,
"no_original_file_overwrite":True,"sha_match_required_before_any_extract":True,
"runtime_source":"DISCOVER_ON_ACTUAL_OSI_WITH_OWNER_PERMISSION",
}
REQUIRED=["exact_head_ci","canonical_v3","source_sha256","licenses_and_security",
"owner_threshold","mac_runtime","sqlite_receipts","rollback"]

def classify(value):
    if not isinstance(value,dict):
        return {"state":"HOLD_SCHEMA"}
    for key,expected in EXPECTED.items():
        actual=value.get(key)
        if type(actual) is not type(expected) or actual!=expected:
            return {"state":"HOLD_SCOPE_OR_AUTHORITY","field":key}
    if value.get("preflight_checks")!=REQUIRED:
        return {"state":"HOLD_STAGE_ORDER"}
    if value.get("prepared_os_arch_check")!="MAC_ARM64_OS_VERSION_RUNTIME_SQLITE":
        return {"state":"HOLD_RUNTIME_SPEC"}
    return {"state":"PASS_PREPARATION_ONLY","field_authorized":False,
            "owner_acceptance":"HOLD","osi_execution":0}
if __name__=="__main__":
    x=json.loads((HERE/"osi_entry_preparation.json").read_text(encoding="utf-8"))
    result=classify(x)
    print(json.dumps(result,sort_keys=True))
    if result["state"]!="PASS_PREPARATION_ONLY":
        raise SystemExit(1)
