"""HYM source-bound Zülfikar V1.4.1 method crosswalk; no official acceptance."""
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
from tools.arge_a03_preflight_v419 import SOLO_ORIGINAL_BLOCKS

ROOT=Path(__file__).resolve().parents[1]
HEAD="4780d96ccb16ca4a922846ab48918262c7845f47"
PREFIX="governance/enguru-suzgeci/zulfikar-v12/v141/"
PINS={
 "architecture/zulfikar_v141_8_gate_architecture.json":"8281b324330d8b89c11c429e4e524ede4fcbe9ebe468063c410c822077525988",
 "architecture/dom_v10_design.json":"a3907e2916f3c67bcc023abd9e3d23b4bcc64102541fecab5a8841a45c825b69",
}
STAGES=("T01","T02","A01","A02","A03","A04","A05","A06")
HANDOFF="governance/enguru-suzgeci/reviews/ENGURU_ARGE_B01_M01_A03_A04_MANAGEMENT_DECISION_HANDOFF_V1.json"
CASES="governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_18_CASE_RECONCILIATION_V428.json"

def duplicate_guard(pairs):
    x={}
    for k,v in pairs:
        if k in x: raise ValueError("DUPLICATE_JSON_KEY")
        x[k]=v
    return x

def fetch(name):
    if name not in PINS: raise ValueError("SOURCE_NOT_PINNED")
    url=("https://raw.githubusercontent.com/engurulabory/Engurulaboratuvari/"
         +HEAD+"/"+urllib.parse.quote(PREFIX+name))
    req=urllib.request.Request(url,headers={"User-Agent":"HYM-V141-RESEARCH/1"})
    with urllib.request.urlopen(req,timeout=20) as r:
        if r.geturl()!=url: raise ValueError("SOURCE_REDIRECT")
        raw=r.read(60001)
    return raw

def verify(fetcher=fetch,pins=None):
    expected=PINS if pins is None else pins
    if set(expected)!=set(PINS): raise ValueError("SOURCE_SET_CHANGED")
    out=[]
    for path in PINS:
        raw=fetcher(path)
        if not isinstance(raw,bytes) or not 0<len(raw)<=60000:
            raise ValueError("SOURCE_BYTES_INVALID")
        if hashlib.sha256(raw).hexdigest()!=expected[path]:
            raise ValueError("SOURCE_SHA256_MISMATCH")
        item=json.loads(raw,object_pairs_hook=duplicate_guard)
        if not isinstance(item,dict):raise ValueError("SOURCE_JSON_OBJECT_REQUIRED")
        out.append(item)
    return out

def assess(h,c,fetcher=fetch,pins=None):
    out={"state":"HOLD","methodHead":HEAD,"methodPr":246,
         "methodAuthority":"REVIEW_BRANCH_ONLY",
         "official":"0/40","E5":"0/18","OSI":"0/100","verifiedFinish":"HOLD",
         "stageAcceptance":{s:"HOLD_STAGE_100_EVIDENCE_REQUIRED" for s in STAGES},
         "namespace":{"methodA03":"ZF.V141.A03","originalA03":"HYM.A03"}}
    try:
        arch,dom=verify(fetcher,pins)
        scope=h["preserved_scope"];owner=h["solo_owner_github_preparation_v2"]
        q=h["single_active_execution_queue"]
        tasks=[t for item in q for t in item["scope"]]
        original=[t for group in SOLO_ORIGINAL_BLOCKS for t in group]
        gates=arch["gates"];weights=dom["fiveEqualWeightEngineeringRequirements"]
        checks={
            "S01":arch["id"]=="ENGURU_ZULFIKAR_V1_4_1" and
                   [g["id"] for g in gates]==list(STAGES),
            "S02":len(gates)==8 and len({g["acceptance"] for g in gates})==8
                   and all(len(g["requiredOutputs"])==5 for g in gates),
            "S03":dom["id"]=="ENGURU_DOM_V1_0" and
                   dom["scope"]=="PRE_GITHUB_PREPARATION_AND_DISPOSABLE_TESTS_ONLY"
                   and [x["weight"] for x in weights]==[20]*5,
            "S04":arch["transitionRule"]=="ONLY_CURRENT_GATE_EVIDENCED_100_PASS_ALLOWS_NEXT_GATE",
            "S05":len(q)==10 and len(tasks)==len(set(tasks))==40
                   and set(tasks)==set(original) and scope["blocks"]==6,
            "S06":scope["chosen"]==["A03","A04","A05","A06"]
                   and scope["cases"]==18 and scope["cells"]==234
                   and len(c["cases"])==18 and c["baseline"]["rows"]==234,
            "S07":owner["approved_owner"]=="engurulabory"
                   and owner["second_human_github_reviewer_required"] is False
                   and owner["official_donecheck_issuer"]=="EXISTING_CANONICAL_ONLY",
            "S08":h["A03"]["decision"]=="HOLD_REAL_A03_OWNER_ISSUER_REVIEWER_AUTHORITY"
                   and h["A03"]["real_owner_grant_ref"] is None
                   and h["A04"]["decision"]=="HOLD_OWNER_CANONICAL_SCOPE",
            "S09":h["A05_A06"]["customer_deployment"]=="0/18"
                   and h["A05_A06"]["independent_e5"]=="0/18"
                   and h["current_counters"]["overall_official"]=="0/40",
            "S10":h["current_counters"]["github_preparation"]=="50/100"
                   and h["current_counters"]["osi_field"]=="0/100"
                   and arch["userGoalContract"]["id"]=="ZF.V141.PREGH.2026-10-26"
        }
        out["passed"]=[k for k,v in checks.items() if v is True]
        out["failed"]=[k for k,v in checks.items() if v is not True]
        out["crosswalkScore"]=len(out["passed"])*10
        if not out["failed"]:out["state"]="PASS_METHOD_SOURCE_CROSSWALK_ONLY"
    except (OSError,ValueError,KeyError,TypeError,AttributeError,UnicodeError) as exc:
        out["reason"]=type(exc).__name__+":"+str(exc)[:140]
    return out

def main():
    h=json.loads((ROOT/HANDOFF).read_text(encoding="utf8"))
    c=json.loads((ROOT/CASES).read_text(encoding="utf8"))
    result=assess(h,c)
    print(json.dumps(result,sort_keys=True))
    return 0 if result["state"]=="PASS_METHOD_SOURCE_CROSSWALK_ONLY" else 2

if __name__=="__main__":raise SystemExit(main())
