"""Zulfikar V1.4.1: two application PREPARATION 100/100 checks, NOT product finish.

8 ordered gates * 5 Git-HEAD pinned source receipts each, scope-aware invariant
validation, 3 evidence rounds, and independent negative tests. All preparation
is made on GitHub runner; real field, owner approval and official PROVEN HOLD.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
CONTRACT=HERE/"TWO_PREPARATION_100_V141.json"
RECEIPT=HERE/"two-preparation-v141-receipt.json"
GATES=("T01","T02","A01","A02","A03","A04","A05","A06")
V3="governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md"
V3_SHA="11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc"
SOURCE_V141="8fbd40c8fde34e7f8d77d5079c4da86a1baa8dad"
HEX40=re.compile(r"^[a-f0-9]{40}$")
READ_MIN=10

def fail(code):
    return {"state":"HOLD","reason":code,"score":0}

def git_bytes(path):
    return subprocess.run(["git","-C",str(ROOT),"show","HEAD:"+path],
                          check=True,timeout=15,capture_output=True).stdout

def contract_guard(data):
    if not isinstance(data,dict) or data.get("schema")!="enguru.harvest.zulfikar-v141-two-preparation-targets/v1":
        return "SCHEMA"
    if (data.get("owner")!="engurulabory" or data.get("source_commit")!=SOURCE_V141 or
        data.get("method")!="ZULFIKAR_V1.4.1_AND_DONGU_ONARIM_V1.0" or
        data.get("official_verified_finish")!="HOLD" or data.get("real_user_acceptance")!="HOLD" or
        data.get("source_rights_acceptance")!="HOLD" or data.get("conditional_pass")!="READINESS_FOR_OWNER_AUTHORIZED_EXECUTION_ONLY" or
        type(data.get("mac_execution")) is not int or data["mac_execution"]!=0 or
        type(data.get("main_merge")) is not int or data["main_merge"]!=0 or
        type(data.get("measured_official_proven_skills")) is not int or data["measured_official_proven_skills"]!=0 or
        type(data.get("mandatory_paid_api")) is not int or data["mandatory_paid_api"]!=0 or
        data.get("peer_reviewer_new_required") is not False):
        return "AUTHORITY"
    if data.get("base_historic_score")!={"github_application_evidence":65,"osi_prefield_evidence":60}:
        return "HISTORY"
    stages=data.get("tracks")
    if not isinstance(stages,dict) or set(stages)!={"github","osi"}:
        return "TRACKS"
    for track,target,prefix in (("github","GITHUB_APPLICATION_PREPARATION","GH"),("osi","OSI_PRE_FIELD_PREPARATION","OSI")):
        rows=stages[track]
        if (not isinstance(rows,dict) or rows.get("target")!=target or
            rows.get("score_type")!="PREPARATION_VERIFIED_ONLY" or
            not isinstance(rows.get("definition"),str) or len(rows["definition"])<25):
            return "TRACK_SCOPE"
        gates=rows.get("stages")
        if not isinstance(gates,list) or len(gates)!=8:
            return "EIGHT_GATES"
        for i,stage in enumerate(gates):
            if (not isinstance(stage,dict) or stage.get("id")!=GATES[i] or
                type(stage.get("order")) is not int or stage["order"]!=i+1 or
                stage.get("stage_pass_scope")!="PREPARATION_ONLY"):
                return "GATE_ORDER"
            controls=stage.get("required_evidence")
            if not isinstance(controls,list) or len(controls)!=5:
                return "FIVE_CONTROLS"
            unique=set()
            for j,control in enumerate(controls):
                if (not isinstance(control,dict) or
                    control.get("check_id")!=f"{prefix}-{GATES[i]}-{j+1:02d}" or
                    control.get("required")!="EXISTS_TRACKED_AND_SHA256_EQ_GIT_HEAD"):
                    return "CONTROL_ID"
                p=control.get("source_path")
                if (not isinstance(p,str) or p in unique or p.startswith("/") or
                    ".." in Path(p).parts or "\\" in p or
                    not (p.startswith("capabilities/enguru-harvest-v1/") or p.startswith(".github/workflows/") or p==V3)):
                    return "UNSAFE_EVIDENCE_PATH"
                unique.add(p)
    return None

def domain_guard(load):
    # Domain contracts are checked as REAL bytes from git HEAD, not self-reported scores.
    try:
        def obj(file):
            return json.loads(load("capabilities/enguru-harvest-v1/"+file))
        goal=obj("goal.json")
        pilots=obj("PILOT_APPLICATION_PREP_V141.json")
        external=obj("external_skill_proof_plan.json")
        sources=obj("UPSTREAM_GITHUB_PINS_30.json")
        license_data=obj("root_license_observations.json")
        scope=obj("ZULFIKAR_V141_SOURCE_REUSE.json")
        history=obj("READINESS_AUDIT_V3.json")
        old_accept=obj("ZULFIKAR_V131_100_GATE_CONTRACT.json")
        osifield=obj("osi_entry_preparation.json")
    except (ValueError,KeyError,TypeError):
        return "UNREADABLE_DOMAIN"
    if (goal.get("schema")!="enguru.harvest.goal/v1.1" or
        goal.get("controls")!=[f"H{i:02d}" for i in range(1,11)] or
        goal.get("official_finish")!="HOLD" or goal.get("osi_field")!="HOLD" or
        goal.get("mandatory_paid_api")!=0):
        return "GOAL_CONTRACT"
    t=pilots.get("tasks")
    if (pilots.get("schema")!="enguru.harvest.v141-pilot-preparation/v1" or
        not isinstance(t,list) or len(t)!=5 or pilots.get("task_count")!=5 or
        [x.get("id") for x in t]!=[f"U{i:02d}" for i in range(1,6)] or
        len({x.get("runner") for x in t})!=5 or
        not all(x.get("real_owner_acceptance")=="HOLD" and x.get("negative_test")=="UNAUTHORIZED_ACTION_HOLD" for x in t) or
        pilots.get("mode")!="PREPARE_ONLY" or pilots.get("owner_approval")!="HOLD" or
        pilots.get("actual_user_receipts")!=0 or pilots.get("osi_execution")!=0):
        return "FIVE_PILOT_INPUT_AND_STOP"
    cases=external.get("cases")
    if (not isinstance(cases,list) or [x.get("id") for x in cases]!=[f"P{i:02d}" for i in range(1,13)] or
        external.get("measured_proven")!=0 or
        any(x.get("actual_run_receipt") is not None or x.get("independent_review") is not None for x in cases)):
        return "TWELVE_SKILL_PLAN_NOT_ACCEPTANCE"
    s=sources.get("sources")
    if (not isinstance(s,list) or len(s)!=30 or sources.get("promotion_allowed") is not False or
        any(x.get("legal_approval")!="HOLD" or x.get("adoption")!="HOLD" for x in s)):
        return "THIRTY_QUARANTINED_SOURCES"
    observations=license_data.get("observations")
    if (not isinstance(observations,list) or len(observations)!=30 or
        sum(x.get("path") is not None for x in observations)!=29 or
        any(x.get("redistribution_approval")!="HOLD" for x in observations)):
        return "LICENSE_USE_RIGHTS_HOLD"
    if (scope.get("source_git_commit")!=SOURCE_V141 or scope.get("osi_execution")!=0 or
        scope.get("official_finish")!="HOLD" or
        [x.get("id") for x in scope.get("gates",[])]!=list(GATES)):
        return "V141_SOURCE_AUTHORITY"
    if (history.get("github",{}).get("current")!=65 or
        history.get("osi",{}).get("current")!=60 or
        history.get("design_coverage",{}).get("real_verified_finish")!="HOLD"):
        return "PRESERVE_HISTORIC_EVIDENCE"
    if (old_accept.get("github",{}).get("state")!="HOLD" or
        old_accept.get("osi",{}).get("state")!="HOLD"):
        return "CANONICAL_PRODUCT_FINISH_HOLD"
    if (osifield.get("status")!="PREPARATION_ONLY" or
        osifield.get("owner_entry_approval")!="HOLD" or
        osifield.get("osi_execution_count")!=0):
        return "FIELD_SCOPE_HOLD"
    return None

def assess(contract,source_reader):
    bad=contract_guard(contract)
    if bad:
        return fail(bad)
    try:
        source_bytes=source_reader(V3)
    except (OSError,ValueError,subprocess.CalledProcessError):
        return fail("CANONICAL_READ")
    if hashlib.sha256(source_bytes).hexdigest()!=V3_SHA:
        return fail("CANONICAL_SHA")
    domain=domain_guard(source_reader)
    if domain:
        return fail(domain)
    result={}
    for name in ("github","osi"):
        stages=[]
        score=0
        for gate in contract["tracks"][name]["stages"]:
            checks=[]
            for ctrl in gate["required_evidence"]:
                path=ctrl["source_path"]
                try:
                    raw=source_reader(path)
                    if len(raw)<READ_MIN or len(raw)>2_000_000:
                        raise ValueError("SOURCE_LENGTH")
                    sha=hashlib.sha256(raw).hexdigest()
                    if len(sha)!=64:
                        raise ValueError("SHA")
                except (OSError,ValueError,subprocess.CalledProcessError):
                    return fail("EVIDENCE_MISSING:"+ctrl["check_id"])
                checks.append({"id":ctrl["check_id"],"sha256":sha})
            gate_pass=len(checks)==5
            if not gate_pass:
                return fail("GATE_EVIDENCE_SHORT")
            stages.append({"id":gate["id"],"checked":len(checks),
                           "stage_preparation_score":100,"state":"PASS_PREPARATION_ONLY",
                           "evidence":checks})
            score+=1
        result[name]={"score":score*100//8,"gates":stages,
                      "state":"PASS_PREPARATION_100_OF_100"}
    return {"state":"PASS_BOTH_PREPARATIONS_100_OF_100","tracks":result,
            "original_historic_evidence":{"github":65,"osi":60},
            "official_verified_finish":"HOLD","owner_threshold":"HOLD",
            "real_user_success":"HOLD","source_reuse_authority":"HOLD",
            "mac_execution":0,"main_merge":0}

def git_reader(path):
    src=ROOT/path
    if src.is_symlink() or not src.is_file() or not src.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("UNSAFE_WORKTREE")
    local=src.read_bytes()
    if local!=git_bytes(path):
        raise ValueError("WORKTREE_DRIFT")
    return local

def main():
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    rounds=[]
    for i in (1,2,3):
        result=assess(contract,git_reader)
        if result["state"]!="PASS_BOTH_PREPARATIONS_100_OF_100":
            raise SystemExit("PREPARATION_HOLD:"+result["reason"])
        for track in result["tracks"].values():
            if len(track["gates"])!=8 or track["score"]!=100:
                raise SystemExit("PREPARATION_GATE_SCORE_HOLD")
        rounds.append({"round":i,"github":100,"osi":100,
                       "state":"PASS_LOGICAL_PREPARATION_AND_REAL_SOURCE_CHECK",
                       "evidence_sha256":hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()})
    if len({x["evidence_sha256"] for x in rounds})!=1:
        raise SystemExit("PREPARATION_NONDETERMINISTIC")
    head=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
    proof={"schema":"enguru.harvest.two-preparation-v141-real-evidence/v1",
           "exact_head":head,"state":"PASS_PREPARATION_CHECKS_ONLY",
           "github_application_preparation":100,"osi_prefield_preparation":100,
           "eight_gates_each_100":True,"checked_individual_evidence":80,
           "simulations":rounds,"head_source_verification":True,
           "github_official_verified_finish":"HOLD","actual_owner_task_pass":False,
           "actual_mac_field_pass":False,"osi_execution":0,
           "main_merge":0,"external_skills_official_proven":0}
    RECEIPT.write_text(json.dumps(proof,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in proof.items() if k!="simulations"},sort_keys=True))

if __name__=="__main__":
    main()
