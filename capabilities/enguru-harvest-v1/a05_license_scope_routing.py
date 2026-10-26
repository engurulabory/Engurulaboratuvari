"""A05 scope-based, fail-closed legal-use routing for *actual* SHA256 receipts.

This is a machine-verifiable REVIEW WORKLIST, never a legal opinion, grant,
source adoption or permission to copy/redistribute proprietary skill assets.
Consumes the prior GitHub-runner's 29 real license fulltext byte receipt.
"""
import hashlib
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
SHA40=re.compile(r"^[a-f0-9]{40}$")
SHA64=re.compile(r"^[a-f0-9]{64}$")
SPECIAL={
    "anthropics/claude-code":("VENDOR_TERMS_RESTRICTED",["VERIFY_ACCOUNT_TERMS","REJECT_SOURCE_COPY_UNTIL_AUTHORIZED"]),
    "meilisearch/meilisearch":("MIXED_COMPONENT_LICENSE",["COMPONENT_FILE_SCOPE","BUSL_ENTERPRISE_REVIEW","MIT_NOTICE_REVIEW"]),
    "HypothesisWorks/hypothesis":("FILE_SCOPE_COPYLEFT_REVIEW",["MPL_FILE_SCOPE","THIRD_PARTY_NOTICE_REVIEW"]),
    "semgrep/semgrep":("COPYLEFT_LICENSE_REVIEW",["LGPL_2_1_LINKING_AND_MODIFICATION_SCOPE","NOTICE_AND_COMPONENT_LICENSES"]),
    "astral-sh/uv":("MULTIPLE_LICENSE_FILES_REVIEW",["ADDITIONAL_LICENSE_FILES","OPTION_AND_NOTICE_REVIEW"]),
    "anthropics/skills":("NO_ROOT_PER_SKILL_VENDOR_RESTRICTED",["PER_SKILL_LICENSE","VENDOR_NO_EXTRACTION_OR_DERIVATIVE_RIGHTS","USE_AGREEMENT_REVIEW"]),
}
def classify(repository, license_risk):
    if repository in SPECIAL:
        category,actions=SPECIAL[repository]
        return category,list(actions)
    if repository.startswith("modelcontextprotocol/"):
        return "TRANSITION_OR_MULTI_COMPONENT_REVIEW",["MCP_VERSIONED_LICENSE_TRANSITION","FILE_LICENSE_AND_DOCUMENTATION_SCOPE"]
    if license_risk=="APACHE_2_NOTICE_PATENT_REVIEW":
        return "PERMISSIVE_WITH_OBLIGATIONS_REVIEW",["COPYRIGHT_AND_NOTICE","PATENT_AND_TRADEMARK_SCOPE","DEPENDENCY_LICENSE_CHECK"]
    if license_risk=="MIT_NOTICE_REVIEW":
        return "PERMISSIVE_WITH_OBLIGATIONS_REVIEW",["COPYRIGHT_AND_NOTICE","DEPENDENCY_LICENSE_CHECK"]
    return "UNCLASSIFIED_REVIEW_REQUIRED",["READ_FULL_LICENSE_AND_DEPENDENCIES","OWNER_SOURCE_SCOPE_DECISION"]

def reconcile(fulltext,pins):
    if (not isinstance(fulltext,dict) or not isinstance(pins,dict) or
        fulltext.get("state")!="PASS_PINNED_29_LICENSE_FULLTEXT_DIGESTS_OBSERVED_ONLY" or
        fulltext.get("schema")!="enguru.harvest.a05-license-fulltext-evidence/v1" or
        fulltext.get("license_usage_authority")!="HOLD" or
        fulltext.get("official_finish")!="HOLD" or
        type(fulltext.get("osi_execution")) is not int or fulltext["osi_execution"]!=0 or
        fulltext.get("legal_reuse_approvals")!=0 or
        fulltext.get("official_proven_skills")!=0 or
        fulltext.get("root_license_fulltext_sha256_count")!=29 or
        fulltext.get("missing_root_license_count")!=1 or
        pins.get("promotion_allowed") is not False):
        return {"state":"HOLD_SOURCE_OR_AUTHORITY"}
    rows=fulltext.get("records")
    inventory=pins.get("sources")
    if not isinstance(rows,list) or len(rows)!=29 or not isinstance(inventory,list) or len(inventory)!=30:
        return {"state":"HOLD_SOURCE_COUNT"}
    byname={}
    for observed in rows:
        if not isinstance(observed,dict):
            return {"state":"HOLD_INVALID_OBSERVATION"}
        name=observed.get("repository")
        digest=observed.get("license_fulltext_sha256")
        blob=observed.get("license_blob_sha1")
        if (not isinstance(name,str) or name in byname or
            not isinstance(digest,str) or SHA64.fullmatch(digest) is None or
            not isinstance(blob,str) or SHA40.fullmatch(blob) is None or
            type(observed.get("license_bytes")) is not int or observed["license_bytes"]<=0 or
            observed.get("state")!="PASS_LICENSE_BYTES_OBSERVED_ONLY" or
            observed.get("legal_reuse_authorized") is not False or
            observed.get("security_approval") is not False or
            observed.get("source_archive_sha256") is not None or
            observed.get("license_text_redistributed") is not False):
            return {"state":"HOLD_UNTRUSTED_LICENSE_RECEIPT"}
        byname[name]=observed
    results=[]
    ids=set()
    names=set()
    for i,pin in enumerate(inventory,1):
        if not isinstance(pin,dict) or pin.get("id")!="SRC-"+str(i).zfill(2):
            return {"state":"HOLD_SOURCE_ID"}
        name=pin.get("repository")
        commit=pin.get("commit_sha")
        if (not isinstance(name,str) or name in names or
            not isinstance(commit,str) or SHA40.fullmatch(commit) is None or
            pin.get("legal_approval")!="HOLD" or pin.get("adoption")!="HOLD" or
            pin.get("security_acceptance")!="HOLD" or
            pin.get("source_archive_sha256") is not None):
            return {"state":"HOLD_SOURCE_PROMOTION"}
        names.add(name)
        if name=="anthropics/skills":
            if name in byname:
                return {"state":"HOLD_MISSING_ROOT_DISAGREEMENT"}
            category,requirements=classify(name,"")
            info={"license_path":None,"license_fulltext_sha256":None,
                  "license_bytes":None,"root_license":"ABSENT_PER_SKILL_HOLD"}
        else:
            obs=byname.get(name)
            if obs is None or obs.get("source_commit_sha")!=commit or not isinstance(obs.get("license_path"),str):
                return {"state":"HOLD_COMMIT_OR_LICENSE_MISSING"}
            category,requirements=classify(name,obs.get("license_risk"))
            info={"license_path":obs["license_path"],"license_fulltext_sha256":obs["license_fulltext_sha256"],
                  "license_bytes":obs["license_bytes"],"root_license":"SHA256_VERIFIED_AT_SOURCE_COMMIT"}
        if name in ids:
            return {"state":"HOLD_REPEATED_SOURCE"}
        ids.add(name)
        results.append({
            "id":pin["id"],"repository":name,"source_commit_sha":commit,
            **info,"review_category":category,"required_owner_checks":requirements,
            "upstream_metadata_inspection":True,
            "actual_skill_source_incorporation":False,
            "source_redistribution":False,
            "product_adoption":False,
            "security_accepted":False,
            "legal_scope_accepted":False,
            "action_state":"HOLD_SCOPE_SPECIFIC_ACCEPTANCE",
        })
    if set(byname)!=names-{"anthropics/skills"}:
        return {"state":"HOLD_EXTRA_OR_MISSING_SOURCE"}
    if not any(x["review_category"]=="VENDOR_TERMS_RESTRICTED" for x in results):
        return {"state":"HOLD_VENDOR_SCOPE_MISSING"}
    if not any(x["review_category"]=="MIXED_COMPONENT_LICENSE" for x in results):
        return {"state":"HOLD_MIXED_LICENSE_MISSING"}
    return {
        "schema":"enguru.harvest.a05-source-use-rights-routing/v1",
        "state":"PASS_DETAILED_30_SOURCE_USE_SCOPE_REVIEW_PLAN_ONLY",
        "sha256_verified_root_license_records":29,
        "per_skill_license_root_missing":1,
        "source_records":len(results),
        "permission_grants":0,
        "official_proven_skill_adoptions":0,
        "osi_execution":0,
        "owner_human_threshold":"HOLD",
        "scope":"RESEARCH_EVIDENCE_AND_OWNER_REVIEW_ONLY",
        "records":results,
    }

def main():
    upstream=json.loads((HERE/"a05-license-fulltext-digests-receipt.json").read_text(encoding="utf-8"))
    pin=json.loads((HERE/"UPSTREAM_GITHUB_PINS_30.json").read_text(encoding="utf-8"))
    outcome=reconcile(upstream,pin)
    if outcome["state"]!="PASS_DETAILED_30_SOURCE_USE_SCOPE_REVIEW_PLAN_ONLY":
        raise SystemExit("LICENSE_SCOPE_HOLD: "+outcome["state"])
    (HERE/"a05-source-rights-routing-receipt.json").write_text(
        json.dumps(outcome,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    counts={}
    for row in outcome["records"]:
        key=row["review_category"]
        counts[key]=counts.get(key,0)+1
    print(json.dumps({k:v for k,v in outcome.items() if k!="records"}|{"review_categories":counts},
                     sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
