#!/usr/bin/env python3
"""ENGURU governed scheduled Management -> Engineer -> Verifier, scoped to public Labory."""
import argparse,base64,hashlib,json,os,re,subprocess,sys
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

REPO="engurulabory/Engurulaboratuvari"
ISSUE=192
MARKER="ENGURU_CONTROLLER_V3:"
TEST="tests/test_enguru_five_minute_controller.py"
def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"))
def hold(reason):return {"state":"HOLD_GUVENLI_DUR","reason":reason}
def key(task,root=None,commit=None):
    values={k:task.get(k) for k in ("id","action","path","expected_sha256","desired_sha256","replace_from","replace_to","dependencies","target_repo","acceptance_version","existing_pr_number")}
    if root is not None:
        file=safe_file(root,task.get("path"))
        values["observed_source_sha256"]=sha(file.read_bytes()) if file else "MISSING"
    values["source_commit"]=commit or "0"*40
    return sha(canonical(values).encode())
def safe_file(root,relative):
    if not isinstance(relative,str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts or ".git" in Path(relative).parts:return None
    try:
        root=root.resolve(strict=True);p=(root/relative).resolve(strict=True);p.relative_to(root)
        return p if p.is_file() else None
    except (OSError,ValueError):return None
def gate_valid(gate):
    required={"state":"ENABLED_BOUNDED_PR","repository":REPO,"max_tasks_per_cycle":1,"max_additional_spend_usd":0,"paid_providers":False,"human_final_authority":"OWNER"}
    return isinstance(gate,dict) and all(gate.get(k)==v for k,v in required.items())
def select(worklist,completed,pending=None):
    tasks=worklist.get("tasks") if isinstance(worklist,dict) else None
    if not isinstance(tasks,list):return None,"WORKLIST_REQUIRED"
    ids=[]
    for t in tasks:
        if not isinstance(t,dict) or not re.fullmatch("[A-Z][A-Z0-9_]{2,79}",str(t.get("id",""))):return None,"TASK_ID_INVALID"
        ids.append(t["id"])
        if t.get("target_repo")!=REPO:return None,"PRIVATE_REPO_GRANT_REQUIRED"
        if t.get("action") not in ("verify_file_digest","run_unit_test","propose_exact_repair"):return None,"ACTION_GRANT_REQUIRED"
        if t.get("action")=="propose_exact_repair":
            path=t.get("path")
            if not isinstance(path,str) or not path.startswith("governance/controller/work/"):return None,"REPAIR_PATH_GRANT"
            for k in ("expected_sha256","desired_sha256"):
                if not re.fullmatch("[0-9a-f]{64}",str(t.get(k,""))):return None,"REPAIR_DIGEST_REQUIRED"
            old,new=t.get("replace_from"),t.get("replace_to")
            if not isinstance(old,str) or not isinstance(new,str) or not 1<=len(old)<=512 or len(new)>512 or old==new:return None,"REPAIR_EXACT_DIFF"
        if t.get("action")=="verify_file_digest" and not re.fullmatch("[0-9a-f]{64}",str(t.get("expected_sha256",""))):return None,"EXPECTED_DIGEST_REQUIRED"
        if t.get("action")=="run_unit_test" and t.get("path")!=TEST:return None,"TEST_RECIPE_SCOPE"
        if not isinstance(t.get("dependencies",[]),list):return None,"DEPENDENCY_SCHEMA"
        if not isinstance(t.get("max_attempts",2),int) or not 1<=t.get("max_attempts",2)<=3:return None,"RETRY_POLICY"
        if not isinstance(t.get("priority",100),int) or not 0<=t.get("priority",100)<=999:return None,"PRIORITY_POLICY"
    if len(ids)!=len(set(ids)):return None,"DUPLICATE_TASK_IDS"
    if any(d not in ids for t in tasks for d in t.get("dependencies",[])):return None,"DEPENDENCY_AUTHORITY"
    candidates=[t for t in tasks if t.get("state")=="READY" and t["id"] not in completed and t["id"] not in (pending or set()) and set(t.get("dependencies",[])).issubset(completed)]
    if not candidates:return None,"NO_ELIGIBLE_TASK"
    try:candidates.sort(key=lambda t:(int(t.get("priority",100)),t["id"]))
    except (TypeError,ValueError):return None,"INVALID_PRIORITY"
    return candidates[0],None
def test_once(root):
    return subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-p","test_enguru_five_minute_controller.py","-v"],cwd=root,capture_output=True,text=True,timeout=60,check=False)
def repair_candidate(task,root):
    target=safe_file(root,task.get("path"))
    if target is None:return hold("REPAIR_SOURCE_SCOPE")
    data=target.read_bytes()
    observed=sha(data)
    if observed==task["desired_sha256"]:
        return {"state":"PASS","evidence":{"sha256":observed,"already_repaired":True}}
    if observed!=task["expected_sha256"]:return hold("REPAIR_SOURCE_SHA256_DRIFT")
    try:old=data.decode("utf8")
    except UnicodeDecodeError:return hold("REPAIR_SOURCE_UTF8_REQUIRED")
    if old.count(task["replace_from"])!=1:return hold("REPAIR_UNIQUE_MATCH_REQUIRED")
    new=old.replace(task["replace_from"],task["replace_to"],1).encode("utf8")
    if sha(new)!=task["desired_sha256"]:return hold("REPAIR_CANDIDATE_DIGEST_MISMATCH")
    return {"state":"CANDIDATE_READY","evidence":{"base_sha256":observed,"candidate_sha256":sha(new),"candidate_base64":base64.b64encode(new).decode("ascii")}}
def engineer(task,root):
    if task["action"]=="propose_exact_repair":return repair_candidate(task,root)
    if task["action"]=="verify_file_digest":
        file=safe_file(root,task.get("path"))
        if file is None:return hold("SOURCE_SCOPE")
        raw=file.read_bytes()
        if sha(raw)!=task["expected_sha256"]:return hold("SOURCE_DIGEST_DIFFERENCE")
        return {"state":"PASS","evidence":{"path":task["path"],"sha256":sha(raw),"size":len(raw)}}
    if safe_file(root,TEST) is None:return hold("TEST_SOURCE_REQUIRED")
    try:r=test_once(root)
    except subprocess.TimeoutExpired:return hold("TEST_TIME_LIMIT")
    m=re.search(r"Ran (\d+) tests",r.stderr)
    if r.returncode!=0 or not m or "OK" not in r.stderr:return hold("TEST_EXECUTION_HOLD")
    return {"state":"PASS","evidence":{"count":m.group(1)}}
def verifier(task,result,root):
    if task["action"]=="propose_exact_repair":
        if result.get("state")=="HOLD_GUVENLI_DUR":return hold("ENGINEER_REPAIR_EVIDENCE_REQUIRED")
        path=safe_file(root,task["path"])
        if path is None:return hold("VERIFIER_REPAIR_SOURCE_SCOPE")
        raw=path.read_bytes()
        current=sha(raw)
        if result["state"]=="PASS":
            return {"state":"PASS","proof":"REPAIR_FINAL_SOURCE_RECHECK"} if current==task["desired_sha256"] and result["evidence"].get("sha256")==current else hold("VERIFIER_FINAL_REPAIR_DRIFT")
        if current!=task["expected_sha256"]:return hold("VERIFIER_REPAIR_BASE_DRIFT")
        try:
            candidate=base64.b64decode(result["evidence"]["candidate_base64"],validate=True)
            text=raw.decode("utf8")
        except (ValueError,KeyError,UnicodeDecodeError):return hold("VERIFIER_REPAIR_CANDIDATE_FORMAT")
        if text.count(task["replace_from"])!=1:return hold("VERIFIER_REPAIR_UNIQUE_MATCH")
        independent=text.replace(task["replace_from"],task["replace_to"],1).encode("utf8")
        if candidate!=independent or sha(independent)!=task["desired_sha256"]:return hold("VERIFIER_REPAIR_CANDIDATE_DRIFT")
        return {"state":"PASS","proof":"REPAIR_INDEPENDENT_RECOMPUTE"}
    if result.get("state")!="PASS":return hold("ENGINEERING_EVIDENCE_REQUIRED")
    if task["action"]=="verify_file_digest":
        file=safe_file(root,task["path"])
        if file is None:return hold("VERIFIER_SOURCE_SCOPE")
        raw=file.read_bytes();ev=result["evidence"]
        if sha(raw)!=task["expected_sha256"] or sha(raw)!=ev.get("sha256") or len(raw)!=ev.get("size"):return hold("VERIFIER_DIGEST_DIFFERENCE")
        return {"state":"PASS","proof":"SECOND_SOURCE_DIGEST"}
    try:r=test_once(root)
    except subprocess.TimeoutExpired:return hold("VERIFIER_TEST_TIME_LIMIT")
    m=re.search(r"Ran (\d+) tests",r.stderr)
    if r.returncode!=0 or not m or "OK" not in r.stderr or m.group(1)!=result["evidence"]["count"]:return hold("VERIFIER_TEST_DIFFERENCE")
    return {"state":"PASS","proof":"SECOND_REGRESSION_EXECUTION"}
def cycle(root,worklist,gate,completed=None,failed=None,commit=None,pending=None):
    if not gate_valid(gate):return hold("AUTHORITY_OR_ZERO_COST_GATE")
    if pending:
        return {"state":"AWAITING_HUMAN","reason":"GOVERNED_PR_REVIEW_PENDING","human_final_authority":"OWNER_RESERVED"}
    task,reason=select(worklist,set(completed or []),set(pending or []))
    if task is not None and (failed or {}).get(task["id"],0)>=task.get("max_attempts",2):
        return hold("RETRY_BUDGET_REQUIRES_MANAGEMENT_REVIEW")
    if reason=="NO_ELIGIBLE_TASK":return {"state":"PASS_IDLE","tasks_executed":0,"owner_approval":"RESERVED"}
    if reason:return hold(reason)
    e=engineer(task,root);v=verifier(task,e,root)
    result={"schema":"enguru.controller.v3","state":"PR_PENDING" if e["state"]=="CANDIDATE_READY" and v["state"]=="PASS" else "PASS" if e["state"]=="PASS" and v["state"]=="PASS" else "HOLD_GUVENLI_DUR","task_id":task["id"],"fingerprint":key(task,root,commit),"source_commit":commit or "0"*40,"management":"TASK_SELECTED","engineering":e,"verification":v,"tasks_executed":1,"human_final_authority":"OWNER_RESERVED","authorized_merge":False,"additional_spend_usd":0,"official_verified_finish":"HOLD_DONECHECK_HUMAN_GATE"}
    result["receipt_sha256"]=sha(canonical(result).encode())
    return result
def github(url,token,body=None,method=None):
    data=None if body is None else json.dumps(body).encode()
    h={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}
    if data is not None:h["Content-Type"]="application/json"
    with urlopen(Request(url,headers=h,data=data,method=method or ("POST" if data is not None else "GET")),timeout=12) as f:return json.load(f)
def receipts(token,root,tasks,commit):
    completed=set()
    pending=set()
    failed={}
    known={t["id"]+":"+key(t,root,commit):t["id"] for t in tasks}
    run_cache={}
    for page in range(1,6):
        comments=github(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/comments?per_page=100&page={page}",token)
        for c in comments:
            if c.get("user",{}).get("login")!="github-actions[bot]" or MARKER not in c.get("body",""):continue
            try:
                payload=c["body"].split(MARKER,1)[1].split("-->",1)[0].strip()
                fields=payload.split(":")
                if len(fields)!=5:continue
                status,taskid,fingerprint,runid,source=fields
                taskkey=taskid+":"+fingerprint
                if taskkey not in known or source!=commit or not runid.isdigit():continue
                if runid not in run_cache:
                    run_cache[runid]=github(f"https://api.github.com/repos/{REPO}/actions/runs/{runid}",token)
                run=run_cache[runid]
                if run.get("head_sha")!=commit or run.get("status")!="completed" or run.get("event") not in ("schedule","workflow_dispatch"):continue
                name=known[taskkey]
                if status=="PASS" and run.get("conclusion")=="success":completed.add(name)
                if status=="PR_PENDING" and run.get("conclusion")=="success":pending.add(name)
                if status=="HOLD" and run.get("conclusion") in ("failure","success"):failed[name]=failed.get(name,0)+1
            except (ValueError,KeyError,TypeError):continue
        if len(comments)<100:return completed,pending,failed
    raise ValueError("HISTORY_PAGINATION_LIMIT")
def prepare_repair_pr(token,task,result,commit):
    path=task["path"]
    if not path.startswith("governance/controller/work/"):raise ValueError("REPAIR_SCOPE")
    desired=task["desired_sha256"]
    prior=task.get("existing_pr_number")
    if prior is not None:
        if not isinstance(prior,int) or prior<1:raise ValueError("PR_REFERENCE_FORMAT")
        pr=github(f"https://api.github.com/repos/{REPO}/pulls/{prior}",token)
        if pr.get("state")!="open" or pr.get("base",{}).get("ref")!="main" or pr.get("head",{}).get("repo",{}).get("full_name")!=REPO:
            raise ValueError("PR_REFERENCE_AUTHORITY")
        linked=pr["head"]["ref"]
        blob=github(f"https://api.github.com/repos/{REPO}/contents/{path}?ref={linked}",token)
        if sha(base64.b64decode(blob["content"]))!=desired:raise ValueError("PR_REFERENCE_SOURCE_DIGEST")
        return pr["html_url"]
    branch="enguru/controller-"+task["id"].lower().replace("_","-")+"-"+task["expected_sha256"][:10]+"-"+desired[:10]
    original=github(f"https://api.github.com/repos/{REPO}/contents/{path}?ref=main",token)
    if sha(base64.b64decode(original["content"]))!=task["expected_sha256"]:
        raise ValueError("REPAIR_REMOTE_SOURCE_DRIFT")
    try:
        current=github(f"https://api.github.com/repos/{REPO}/contents/{path}?ref={branch}",token)
    except HTTPError as error:
        if error.code!=404:raise
        github(f"https://api.github.com/repos/{REPO}/git/refs",token,{"ref":"refs/heads/"+branch,"sha":commit})
        current=github(f"https://api.github.com/repos/{REPO}/contents/{path}?ref={branch}",token)
    digest=sha(base64.b64decode(current["content"]))
    if digest==task["expected_sha256"]:
        github(f"https://api.github.com/repos/{REPO}/contents/{path}",token,{
            "message":"ENGURU governed bounded fix "+task["id"],"branch":branch,
            "sha":current["sha"],"content":result["engineering"]["evidence"]["candidate_base64"]},method="PUT")
    elif digest!=desired:
        raise ValueError("REPAIR_BRANCH_SOURCE_CONFLICT")
    try:
        pr=github(f"https://api.github.com/repos/{REPO}/pulls",token,{
            "title":"ENGURU guarded fix: "+task["id"],"head":branch,"base":"main","draft":True,
            "body":"Verified bounded change. Final merge and DoneCheck remain owner-controlled."})
        return pr["html_url"]
    except HTTPError as error:
        if error.code==403:
            return "OWNER_PR_CREATION_REQUIRED:"+branch
        raise

def main():
    p=argparse.ArgumentParser()
    for field in ("root","worklist","gate","output"):p.add_argument("--"+field,required=True)
    p.add_argument("--pilot",action="store_true")
    args=p.parse_args();root=Path(args.root)
    tasks=json.loads(Path(args.worklist).read_text());gate=json.loads(Path(args.gate).read_text())
    if args.pilot:result=cycle(root,tasks,gate)
    elif os.getenv("GITHUB_REPOSITORY")!=REPO or not os.getenv("GITHUB_TOKEN"):result=hold("GITHUB_AUTHORIZATION_REQUIRED")
    else:
        try:
            token=os.environ["GITHUB_TOKEN"]
            commit=os.getenv("GITHUB_SHA","")
            runid=os.getenv("GITHUB_RUN_ID","")
            if not re.fullmatch("[a-f0-9]{40}",commit) or not runid.isdigit():raise ValueError("RUNTIME_PROVENANCE_REQUIRED")
            completed,pending,failed=receipts(token,root,tasks.get("tasks",[]),commit)
            result=cycle(root,tasks,gate,completed,failed,commit,pending)
            if result.get("task_id") and result["state"]=="PR_PENDING":
                candidate=next(t for t in tasks["tasks"] if t["id"]==result["task_id"])
                result["pull_request"]=prepare_repair_pr(token,candidate,result,commit)
            if result.get("task_id"):
                name=result["task_id"]
                status="PASS" if result["state"]=="PASS" else "PR_PENDING" if result["state"]=="PR_PENDING" else "HOLD"
                marker=MARKER+status+":"+name+":"+result["fingerprint"]+":"+runid+":"+commit
                body=f"<!-- {marker} -->\nENGURU verified task: {name}\nEngineer: {result['engineering']['state']}; verifier: {result['verification']['state']}; receipt: {result['receipt_sha256']}; Human Threshold: owner; PR handoff: {result.get('pull_request', 'N/A')}."
                github(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/comments",token,{"body":body})
        except (HTTPError,URLError,TimeoutError,ValueError,KeyError,TypeError,OSError) as e:result=hold("GITHUB_EVIDENCE_TRANSPORT_"+type(e).__name__)
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("STATE="+result["state"])
    return 0 if result["state"] in ("PASS","PASS_IDLE","PR_PENDING","AWAITING_HUMAN") or result.get("reason")=="RETRY_BUDGET_REQUIRES_MANAGEMENT_REVIEW" else 50
if __name__=="__main__":raise SystemExit(main())
