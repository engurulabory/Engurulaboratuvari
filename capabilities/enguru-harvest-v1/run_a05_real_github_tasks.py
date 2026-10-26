"""A05: five *actual GitHub repository* tasks with exact HEAD evidence.

The user requested these real engineering workflows. This executes operational
work on genuine tracked input bytes, not hand-built positive fixture records.
These are still GitHub TECHNICAL observations, NOT proof of field/user benefit.
Three real repetitions/rounds and two-sided adversarial tests are required.
"""
import hashlib
import json
import subprocess
import time
from pathlib import Path
from skill_kernel import execute
from license_gate import check as license_check
from k02_source_policy import reconcile
from test_upstream_github_pins import validate as validate_pins
from build_github_osi_handoff import build, inspect

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCES={
    "catalog":"source_candidates.json",
    "git_pins":"UPSTREAM_GITHUB_PINS_30.json",
    "licenses":"root_license_observations.json",
    "handoff":"OSI_HANDOFF_PREPARATION.md",
}
FILES=list(SOURCES.values())
def source_bytes(name):
    file=HERE/name
    if file.is_symlink() or not file.is_file():
        raise ValueError("UNSAFE_SOURCE")
    raw=file.read_bytes()
    recorded=subprocess.run(["git","-C",str(ROOT),"show","HEAD:capabilities/enguru-harvest-v1/"+name],
                            check=True,capture_output=True,timeout=15).stdout
    if raw!=recorded:
        raise ValueError("SOURCE_HEAD_DRIFT")
    return raw

def task_catalog(source):
    registry=json.loads(source)
    result=execute("catalog-check",registry)
    if result.get("state")!="CATALOG_FORMAT_PASS" or result.get("count")!=30:
        raise ValueError("REAL_CATALOG_RECONCILIATION")
    return {"state":"PASS_TECHNICAL","catalog_count":result["count"]}

def task_git_pins(pin,source):
    pins=json.loads(pin)
    registry=json.loads(source)
    state=validate_pins(pins,registry)
    if state!="PASS_SOURCE_COMMIT_BLOB_OBSERVATION_ONLY":
        raise ValueError(state)
    return {"state":"PASS_TECHNICAL","source_commit_count":len(pins["sources"]),"legal_approval":"HOLD"}

def task_license(source,licenses):
    result=license_check(json.loads(source),json.loads(licenses))
    if result.get("state")!="LICENSE_OBSERVATION_PASS" or result.get("approved_for_reuse")!=0:
        raise ValueError("LICENSE_TRIAGE")
    return {"state":"PASS_TECHNICAL","license_files_observed":result["root_files_observed"],
            "approved_for_reuse":0}

def task_quarantine(source,licenses):
    result=reconcile(json.loads(source),json.loads(licenses))
    if result.get("state")!="PASS_SAFE_QUARANTINE" or result.get("observed")!=30 or result.get("proven")!=0:
        raise ValueError("SOURCE_NOT_QUARANTINED")
    return {"state":"PASS_TECHNICAL","quarantined":result["observed"],"adopted":0}

def task_handoff(source):
    source_sha=hashlib.sha256(source).hexdigest()
    packet=build()
    data=(HERE/packet["package_filename"]).read_bytes()
    state=inspect(data)
    if state["state"]!="PASS_GITHUB_PACKAGE_INTEGRITY_ONLY" or packet.get("osi_execution_count")!=0:
        raise ValueError("HANDOFF_PACKAGE")
    return {"state":"PASS_TECHNICAL","handoff_guide_sha256":source_sha,
            "packet_sha256":packet["zip_sha256"],"file_count":state["files"],
            "field_authorized":False,"mac_execution":0}

TASKS=(
    ("A05-GH-01","CATALOG_30",lambda b:task_catalog(b["catalog"])),
    ("A05-GH-02","IMMUTABLE_GIT_PINS_30",lambda b:task_git_pins(b["git_pins"],b["catalog"])),
    ("A05-GH-03","ROOT_LICENSE_CLASSIFICATION",lambda b:task_license(b["catalog"],b["licenses"])),
    ("A05-GH-04","SOURCE_ADOPTION_QUARANTINE",lambda b:task_quarantine(b["catalog"],b["licenses"])),
    ("A05-GH-05","SHA256_OSI_HANDOFF_SELF_CHECK",lambda b:task_handoff(b["handoff"])),
)

def run():
    head=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
    source={key:source_bytes(name) for key,name in SOURCES.items()}
    hashes={name:hashlib.sha256(source[key]).hexdigest() for key,name in SOURCES.items()}
    rounds=[]
    expected=None
    for round_number in (1,2,3):
        tasks=[]
        for id_,name,fn in TASKS:
            start=time.perf_counter_ns()
            outcome=fn(source)
            seconds=(time.perf_counter_ns()-start)/1_000_000_000
            if seconds<=0 or outcome["state"]!="PASS_TECHNICAL":
                raise ValueError("REAL_TASK_MEASUREMENT")
            result_bytes=json.dumps(outcome,sort_keys=True,separators=(",",":")).encode()
            tasks.append({"id":id_,"task":name,"input_sha256":hashes,
                          "result_sha256":hashlib.sha256(result_bytes).hexdigest(),
                          "elapsed_seconds":round(seconds,8),
                          "technical_pass":True})
        signatures=[(x["id"],x["result_sha256"]) for x in tasks]
        if expected is None:
            expected=signatures
        elif signatures!=expected:
            raise ValueError("NONDETERMINISTIC_REAL_TASK_RESULT")
        rounds.append({"round":round_number,"task_count":len(tasks),"tasks":tasks,
                       "status":"PASS_GITHUB_REAL_REPOSITORY_TASKS_ONLY"})
    receipt={"schema":"enguru.harvest.a05-github-real-repository-trials/v1",
            "github_head":head,"round_count":3,"distinct_task_types":len(TASKS),
            "total_actual_task_executions":len(TASKS)*len(rounds),
            "source_input_sha256":hashes,"rounds":rounds,
            "state":"PASS_GITHUB_TECHNICAL_REPOSITORY_WORK_ONLY",
            "actual_user_satisfaction_verified":False,
            "external_skills_independently_proven":0,
            "independent_ci_observation":True,
            "owner_human_threshold":"HOLD",
            "github_verified_finish":"HOLD","osi_execution":0}
    (HERE/"a05-real-github-tasks-receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"state":receipt["state"],"github_head":head,"round_count":3,
                      "distinct_tasks":5,"real_executions":15,"user_acceptance":"HOLD",
                      "external_proven":0,"osi_execution":0},sort_keys=True))
if __name__=="__main__":
    run()
