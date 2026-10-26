"""Detect duplicate/empty/placeholder assertions in the three 100-control evidence design."""
from collections import Counter
from tools.management_v69_triple100_gate import AREAS
def audit(registry):
    ids=[f"{a}_{i:03d}" for a in AREAS for i in range(1,101)]
    rows={key:registry.get(key) for key in ids} if isinstance(registry,dict) else {}
    complete={key:row for key,row in rows.items() if isinstance(row,dict) and all(
      isinstance(row.get(field),str) and row[field].strip()
      for field in ("description","assertion_id","source_path"))}
    fingerprints=Counter((row["assertion_id"],row["source_path"]) for row in complete.values())
    duplicate=[key for key,row in complete.items() if fingerprints[(row["assertion_id"],row["source_path"])]>1]
    placeholder=[key for key,row in complete.items() if row["description"].strip().lower() in
      {"pass","todo","test","placeholder","generic","ok"}]
    return {"named_controls":len(ids),"described_controls":len(complete),
      "duplicate_assertion_claims":duplicate,"placeholder_descriptions":placeholder,
      "missing_descriptions":[x for x in ids if x not in complete],
      "final":"HOLD_INDEPENDENT_CI_AND_EVIDENCE","osi_mutation":0}
