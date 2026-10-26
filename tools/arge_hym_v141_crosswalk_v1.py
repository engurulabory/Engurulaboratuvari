"""HYM source-bound Zülfikar V1.4.1 method crosswalk; no official acceptance."""
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
import subprocess
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

FOUNDATION_SOURCE_PATHS=(
 "AGENTS.md",
 "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md",
 "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json",
 HANDOFF,
 CASES,
 "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_EVIDENCE_MATRIX_V424.json",
 "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_PUBLIC_SOURCES_V427.json",
)
V3_SHA="11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc"
V19_SHA="3906f7bd6ae07d26547babc172d1337cfdfeff85244ece95efb76c3cb448df08"

def proof_from_git(root=ROOT, paths=FOUNDATION_SOURCE_PATHS):
    """Compare current file bytes to actual Git HEAD tree blobs, fail closed."""
    result={"state":"HOLD","files":{},"head":None}
    try:
        root=Path(root).resolve()
        p=subprocess.run(["git","-C",str(root),"rev-parse","--show-toplevel"],
                         capture_output=True,text=True,check=True,timeout=15)
        if Path(p.stdout.strip()).resolve()!=root:
            raise ValueError("NOT_REPOSITORY_ROOT")
        head=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],
                            capture_output=True,text=True,check=True,timeout=15).stdout.strip()
        if len(head)!=40 or any(c not in "0123456789abcdef" for c in head):
            raise ValueError("INVALID_GIT_HEAD")
        result["head"]=head
        if len(paths)!=len(set(paths)) or len(paths)!=7:
            raise ValueError("SOURCE_SET_DRIFT")
        for rel in paths:
            if rel not in FOUNDATION_SOURCE_PATHS or not isinstance(rel,str):
                raise ValueError("SOURCE_OUT_OF_SCOPE")
            f=root/rel
            if f.is_symlink() or not f.is_file() or f.stat().st_nlink!=1:
                raise ValueError("SOURCE_PATH_UNSAFE:"+rel)
            if f.stat().st_size>1500000:
                raise ValueError("SOURCE_TOO_LARGE:"+rel)
            raw=f.read_bytes()
            actual=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
            want=subprocess.run(["git","-C",str(root),"rev-parse","HEAD:"+rel],
                                capture_output=True,text=True,check=True,timeout=15).stdout.strip()
            if actual!=want:
                raise ValueError("SOURCE_GIT_HEAD_BYTES_DRIFT:"+rel)
            result["files"][rel]={"blob_sha1":actual,
                                  "sha256":hashlib.sha256(raw).hexdigest()}
        if result["files"][FOUNDATION_SOURCE_PATHS[1]]["sha256"]!=V3_SHA:
            raise ValueError("CANONICAL_V3_SHA_MISMATCH")
        lock= json.loads((root/FOUNDATION_SOURCE_PATHS[2]).read_text(encoding="utf8"),
                         object_pairs_hook=duplicate_guard)
        if not isinstance(lock,dict) or lock.get("sha256")!=V3_SHA:
            raise ValueError("CANONICAL_LOCK_MISMATCH")
        result["state"]="PASS_GIT_HEAD_SOURCE_BYTES_ONLY"
    except (OSError,ValueError,subprocess.SubprocessError,UnicodeError,
            json.JSONDecodeError,TypeError) as exc:
        result["reason"]=type(exc).__name__+":"+str(exc)[:180]
    return result

def assess_foundations(h,c,inventory,method,root=ROOT):
    """Five T01 plus five T02 evidence checks; scoped preparation only."""
    out={"state":"HOLD_FOUNDATION_SOURCE_PREPARATION","scope":"T01_T02_GITHUB_PREPARATION_ONLY",
         "T01":{},"T02":{},"stagesAccepted":{"T01":"HOLD","T02":"HOLD"},
         "originalOfficial":"0/40","independentE5":"0/18","verifiedFinish":"HOLD"}
    if not isinstance(h,dict) or not isinstance(c,dict) or not isinstance(inventory,dict) or not isinstance(method,dict):
        return out
    p=h.get("preserved_scope",{})
    a=h.get("solo_owner_github_preparation_v2",{})
    g=h.get("governance",{})
    count=h.get("current_counters",{})
    q=h.get("single_active_execution_queue",[])
    a03=h.get("A03",{})
    a04=h.get("A04",{})
    e=h.get("A05_A06",{})
    base=c.get("baseline",{})
    if (not all(isinstance(x,dict) for x in (p,a,g,count,a03,a04,e,base))
        or not isinstance(q,list)
        or not isinstance(method.get("stageAcceptance"),dict)):
        return out
    # Source and authority are observed in CI, never inferred from self-PASS.
    files=inventory.get("files",{})
    t01={
       "F01_goal_identity":g.get("issue")==205 and g.get("pr")==207 and
         g.get("repository")=="engurulabory/Engurulaboratuvari" and
         g.get("fixed_goal","").startswith("6_BLOK") and p.get("active_package")=="B01-M01",
       "F02_live_source_inventory":inventory.get("state")=="PASS_GIT_HEAD_SOURCE_BYTES_ONLY" and
         set(files)==set(FOUNDATION_SOURCE_PATHS) and
         files.get(FOUNDATION_SOURCE_PATHS[1],{}).get("sha256")==V3_SHA,
       "F03_owner_scope":a.get("approved_owner")=="engurulabory" and
         a.get("second_human_github_reviewer_required") is False and
         a.get("decision_scope")=="GITHUB_RESEARCH_AND_TECHNICAL_PREPARATION_ONLY" and
         a.get("ready_to_automatically_merge") is False,
       "F04_protected_assets":p.get("blocks")==6 and p.get("original_tasks")==40 and
         p.get("cases")==18 and p.get("cells")==234 and
         count.get("overall_official")=="0/40" and count.get("osi_field")=="0/100",
       "F05_initial_risks":a03.get("decision")=="HOLD_REAL_A03_OWNER_ISSUER_REVIEWER_AUTHORITY" and
         a04.get("decision")=="HOLD_OWNER_CANONICAL_SCOPE" and
         e.get("customer_deployment")=="0/18" and e.get("independent_e5")=="0/18",
    }
    original=[task for block in SOLO_ORIGINAL_BLOCKS for task in block]
    tasks=[]
    if isinstance(q,list):
        for item in q:
            if not isinstance(item,dict) or not isinstance(item.get("scope"),list):
                tasks=[];break
            tasks.extend(item["scope"])
    task_ok=all(isinstance(t,str) for t in tasks) and len(tasks)==40 and len(set(tasks))==40 and set(tasks)==set(original)
    e_matrix={}
    pub={}
    if set(files)==set(FOUNDATION_SOURCE_PATHS) and inventory.get("state")=="PASS_GIT_HEAD_SOURCE_BYTES_ONLY":
        try:
            e_matrix=json.loads((Path(root)/FOUNDATION_SOURCE_PATHS[5]).read_text(encoding="utf8"),
                                object_pairs_hook=duplicate_guard)
            pub=json.loads((Path(root)/FOUNDATION_SOURCE_PATHS[6]).read_text(encoding="utf8"),
                           object_pairs_hook=duplicate_guard)
        except (OSError,ValueError,TypeError):
            pass
    t02={
       "G01_fixed_target":p.get("chosen")==["A03","A04","A05","A06"] and
         g.get("fixed_goal","").endswith("BITTI_DUR") and
         method.get("state")=="PASS_METHOD_SOURCE_CROSSWALK_ONLY",
       "G02_original_ids":task_ok and
         sorted(e_matrix.get("tasks",{}))==list(SOLO_ORIGINAL_BLOCKS[0]) and
         base.get("rows")==234 and base.get("cases")==18 and
         base.get("sha256")==V19_SHA,
       "G03_test_and_evidence_needs":all(x in pub.get("task_links",{}) for x in SOLO_ORIGINAL_BLOCKS[0]) and
         a03.get("real_owner_grant_ref") is None and
         e.get("independent_e5")=="0/18",
       "G04_dependency_order":isinstance(q,list) and len(q)==10 and
         [x.get("id") for x in q if isinstance(x,dict)]==
            [f"{i:02d}" for i in range(1,11)] and task_ok and
         p.get("block01")==list(SOLO_ORIGINAL_BLOCKS[0]),
       "G05_safe_stop":count.get("block01_official")=="0/9" and
         count.get("overall_official")=="0/40" and
         a.get("official_donecheck_issuer")=="EXISTING_CANONICAL_ONLY" and
         method.get("verifiedFinish")=="HOLD" and
         set(method["stageAcceptance"])==set(STAGES) and
         all(isinstance(v,str) and v.startswith("HOLD_")
             for v in method["stageAcceptance"].values()),
    }
    out["T01"]={"checks":t01,"score":20*sum(x is True for x in t01.values()),
                "state":"PASS_SOURCE_PREP_ONLY" if all(x is True for x in t01.values()) else "HOLD"}
    out["T02"]={"checks":t02,"score":20*sum(x is True for x in t02.values()),
                "state":"PASS_TARGET_PREP_ONLY" if all(x is True for x in t02.values()) else "HOLD"}
    if out["T01"]["score"]==out["T02"]["score"]==100:
        out["state"]="PASS_T01_T02_GITHUB_SOURCE_PREPARATION_ONLY"
    return out

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
    source_inventory=proof_from_git()
    foundations=assess_foundations(h,c,source_inventory,result)
    result["sourceInventory"]=source_inventory
    result["foundationReadiness"]=foundations
    print(json.dumps(result,sort_keys=True))
    return 0 if (result["state"]=="PASS_METHOD_SOURCE_CROSSWALK_ONLY"
                 and foundations["state"]==
                     "PASS_T01_T02_GITHUB_SOURCE_PREPARATION_ONLY") else 2

if __name__=="__main__":raise SystemExit(main())
