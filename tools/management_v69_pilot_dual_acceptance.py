"""V6.9 Pilot two independent acceptance ledgers; no authority minting."""
THEORY_KEYS=("design_contract","pilot_state_machine","task_ledger","source_sha256","adversarial_tests","github_ci")
FIELD_KEYS=("canonical_owner_grant","ed25519_owner_receipt","donecheck","human_threshold","osi_field_evidence")
def assess(theory,field):
    t_missing=[key for key in THEORY_KEYS if theory.get(key) is not True]
    f_missing=[key for key in FIELD_KEYS if field.get(key) is not True]
    # These bools describe only reviewed *theoretical artifacts*. They never authorize field acceptance.
    theory_state="THEORY_CANDIDATE_PASS" if not t_missing else "THEORY_HOLD"
    # Caller-supplied flags cannot attest to real Ed25519 / Human Threshold authority.
    return {"theory_state":theory_state,"theory_missing":t_missing,
            "field_state":"FIELD_HOLD_CANONICAL_RECEIPTS_REQUIRED",
            "field_missing":f_missing,
            "verified_finish":"HOLD","osi_mutation":0,
            "next_target":"02" if theory_state=="THEORY_CANDIDATE_PASS" else "01"}
