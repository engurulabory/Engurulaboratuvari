"""Three *logical* simulations, with explicit separation from external field evidence."""
import hashlib
import json
from pathlib import Path
from skill_kernel import OPERATIONS, execute

HERE=Path(__file__).resolve().parent
def load(name):
    return json.loads((HERE/name).read_text(encoding="utf-8"))
def assess(name, checks):
    passed=sum(bool(x) for x in checks)
    return {"simulation":name,"passed":passed,"total":len(checks),"state":"PASS_LOGICAL_SIM" if passed==len(checks) else "HOLD"}

def main():
    goal=load("goal.json")
    registry=load("source_candidates.json")
    manifest=registry["candidates"]
    sim1=assess("SIM1_TARGET_STRUCTURE",[
        goal["controls"]==[f"H{i:02d}" for i in range(1,11)],
        len(goal["libraries"])==6,
        len(goal["promotion"])==4,
        len(OPERATIONS)==12,
        registry["record_count"]==30,
        len(manifest)==30,
        execute("catalog-check",registry)["state"]=="CATALOG_FORMAT_PASS",
        goal["mandatory_paid_api"]==0,
        goal["osi_field"]=="HOLD",
        goal["official_finish"]=="HOLD",
    ])
    declared={"id":"ONE","library":"skills","source_url":"https://example.com/a",
              "source_sha256":hashlib.sha256(b"sample").hexdigest(),"license":"MIT",
              "security_review":"PASS","mandatory_paid_api":0,"human_authority":"PASS",
              "independent_review":"PASS","test_receipt":"PASS","real_task_receipt":"PASS"}
    corrupt=json.loads(json.dumps(registry))
    corrupt["candidates"][0]["license"]="MIT"
    sim2=assess("SIM2_ADVERSARIAL",[
        execute("source-candidate",{"record":declared})["state"]=="CANDIDATE",
        execute("catalog-check",corrupt)["state"]=="HOLD",
        execute("source-candidate",{"record":{**declared,"source_sha256":[]}})["state"]=="HOLD",
        execute("source-candidate",{"record":{**declared,"license":"UNVERIFIED"}})["state"]=="HOLD",
        execute("cost-bound",{"mandatory_paid_api":1})["state"]=="HOLD",
        execute("cost-bound",{"mandatory_paid_api":0,"compute_budget_recorded":False})["state"]=="HOLD",
        execute("evidence-bytes",{"manifest":{},"assets":{"evil":"GG"}})["state"]=="HOLD",
        execute("osi-handoff",{"osi_executed":True})["state"]=="HOLD",
        execute("prompt-audit",{"prompt":{"claim":"hi"}})["state"]=="HOLD",
        execute("paired-gain",{"paired_runs":[]})["state"]=="HOLD",
    ])
    runs=[{"task_id":"fixture-task","baseline_success":True,"candidate_success":True,
            "baseline_seconds":10,"candidate_seconds":9,"baseline_quality":95,"candidate_quality":95} for _ in range(5)]
    sim3=assess("SIM3_FIXTURE_END_TO_END",[
        execute("source-candidate",{"record":declared})["state"]=="CANDIDATE",
        execute("fingerprint",{"utf8_text":"source"})["state"]=="DIGEST",
        execute("source-url",{"url":"https://example.com/a"})["state"]=="CHECKED",
        execute("license-triage",{"license_status":"UNVERIFIED"})["state"]=="HOLD",
        execute("cost-bound",{"mandatory_paid_api":0,"compute_budget_recorded":True})["state"]=="BUDGET_CONTRACT_PASS",
        execute("prompt-audit",{"prompt":{"state":"candidate","claim":"fixture","evidence":"fake","next_action":"review"}})["state"]=="STRUCTURE_PASS",
        execute("duplicate-check",{"identifiers":["a","b","a"]})["state"]=="HOLD",
        execute("readme-drift",{"recorded_git_blob_sha1":"a"*40,"observed_git_blob_sha1":"a"*40})["state"]=="MATCH_RECORDED_README",
        execute("paired-gain",{"paired_runs":runs})["state"]=="MEASURED_GAIN_CANDIDATE",
        execute("osi-handoff",{"osi_executed":False})["state"]=="HANDOFF_PREPARATION_ONLY",
    ])
    output={"scope":"SYNTHETIC_LOCAL_LOGIC_ONLY", "simulations":[sim1,sim2,sim3],
            "github_verified_finish":"HOLD", "osi_execution_count":0,
            "external_skill_tested_count":0,"real_independent_review":"HOLD"}
    print(json.dumps(output,ensure_ascii=False,indent=2))
    if any(s["state"]!="PASS_LOGICAL_SIM" for s in output["simulations"]):
        raise SystemExit(1)

if __name__=="__main__":
    main()
