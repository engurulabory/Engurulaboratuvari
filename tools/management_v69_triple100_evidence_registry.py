"""Evidence-bound triple-100 control registry; 300 named criteria require distinct source proof."""
from tools.management_v69_triple100_gate import AREAS
def evaluate_registry(registry):
    result={}
    for area in AREAS:
        ids=[f"{area}_{i:03d}" for i in range(1,101)]
        observed=[]
        for key in ids:
            x=registry.get(key) if isinstance(registry,dict) else None
            if not isinstance(x,dict) or set(x)!={"description","source_path","source_sha256","assertion_id","test_run_id","independent_review"}:
                continue
            if not all(isinstance(x[k],str) and x[k].strip() for k in ("description","source_path","source_sha256","assertion_id","independent_review")):
                continue
            if len(x["source_sha256"])!=64 or any(c not in "0123456789abcdef" for c in x["source_sha256"]):
                continue
            if type(x["test_run_id"]) is not int or x["test_run_id"]<=0:
                continue
            observed.append(key)
        result[area]={"structured_candidates":len(observed),"missing":[k for k in ids if k not in observed],"target":100,"verified":"HOLD_EXTERNAL_SHA_AND_RUN_CHECK"}
    result["three_dimensions_verified"]="HOLD"
    result["field_acceptance"]="HOLD"
    return result
