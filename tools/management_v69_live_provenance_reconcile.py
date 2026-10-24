"""Classify immutable historical provenance separately from current-main acceptance."""
import re
def reconcile_historical(record_commit, observed_main_commit, source_verified_at_record_commit, owner_signature_receipt):
    valid=lambda x:isinstance(x,str) and re.fullmatch(r"[0-9a-f]{40}",x) is not None
    if not valid(record_commit) or not valid(observed_main_commit):
        return {"state":"HOLD_GUVENLI_DUR","reason":"COMMIT_PIN_REQUIRED"}
    if record_commit!=observed_main_commit:
        return {"state":"HOLD_GUVENLI_DUR","reason":"HISTORICAL_RECORD_CURRENT_MAIN_DRIFT",
                "historical_source_recheck":"REQUIRED","next_action":"NEW_CURRENT_MAIN_RECEIPT"}
    if not source_verified_at_record_commit:
        return {"state":"HOLD_GUVENLI_DUR","reason":"SOURCE_PROVENANCE_REQUIRED"}
    if not isinstance(owner_signature_receipt,dict) or owner_signature_receipt.get("verified_by_canonical_donecheck") is not True:
        return {"state":"HOLD_GUVENLI_DUR","reason":"CANONICAL_OWNER_RECEIPT_REQUIRED"}
    # External booleans/document dictionaries are not authentication or signature verification.
    return {"state":"HOLD_GUVENLI_DUR","reason":"TRUSTED_VERIFIER_ORIGINAL_RECEIPT_REQUIRED"}
