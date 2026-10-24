"""Pilot independent theoretical scope checker: verifies repository evidence, never owner authority."""
from pathlib import Path
import hashlib
REQUIRED={
 "tools/management_v69_pilot_dual_acceptance.py":("THEORY_CANDIDATE_PASS","FIELD_HOLD_CANONICAL_RECEIPTS_REQUIRED"),
 "tools/management_v69_pilot_proof_gates.py":("PASS_SOURCE_SHA256","CANONICAL_VERIFIER_RECEIPT_REQUIRED"),
 "tools/management_v69_live_provenance_reconcile.py":("HISTORICAL_RECORD_CURRENT_MAIN_DRIFT","NEW_CURRENT_MAIN_RECEIPT"),
 "governance/management-v69/handoff/OWNER_TRUST_ROOT_RECONCILIATION_V1.md":("producer provenance","owner grant"),
 "governance/management-v69/handoff/SINGLE_OWNER_ZERO_ROUTINE_V1.md":("CURRENT_CANONICAL_AUTHORITY=UNCHANGED","OSI_MUTATION=0"),
}
def inspect(root):
 root=Path(root)
 evidence=[]
 for name,tokens in REQUIRED.items():
  path=root/name
  if not path.is_file() or path.is_symlink():
   return {"state":"THEORY_HOLD","reason":"MISSING_SOURCE","path":name}
  content=path.read_bytes()
  for token in tokens:
   if token.encode() not in content:
    return {"state":"THEORY_HOLD","reason":"MISSING_CONTRACT","path":name,"token":token}
  evidence.append({"path":name,"sha256":hashlib.sha256(content).hexdigest()})
 return {"state":"THEORY_SOURCE_REVIEW_PASS","evidence":evidence,
  "design_100":"HOLD_INDEPENDENT_FINAL","owner_authority":"HOLD",
  "official_verified_finish":"HOLD","osi_mutation":0}
