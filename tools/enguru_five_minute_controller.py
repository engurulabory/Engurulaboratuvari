#!/usr/bin/env python3
"""ENGURU governed scheduled Management -> Engineer -> Verifier, scoped to public Labory."""
import argparse,base64,hashlib,json,os,re,subprocess,sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

REPO="engurulabory/Engurulaboratuvari"
ISSUE=192
MARKER="ENGURU_CONTROLLER_V3:"
TEST="tests/test_enguru_five_minute_controller.py"
WORKFLOW=".github/workflows/enguru-five-minute-controller.yml"
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
    if any(not isinstance(d,str) or d not in ids for t in tasks for d in t.get("dependencies",[])):return None,"DEPENDENCY_AUTHORITY"
    # A dependency cycle is a governed error, not successful idle work.
    remaining={t["id"]:set(t.get("dependencies",[])) for t in tasks}
    while remaining:
        released={name for name,deps in remaining.items() if not deps}
        if not released:return None,"DEPENDENCY_CYCLE"
        for name in released:del remaining[name]
        for deps in remaining.values():deps.difference_update(released)
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
def finalize_receipt(result):
    payload={k:v for k,v in result.items() if k!="receipt_sha256"}
    result["receipt_sha256"]=sha(canonical(payload).encode())
    return result

def donecheck_producer_candidate(result,task):
    """Structured producer evidence; DoneCheck v1.2 and human authority decide final closure."""
    engineering=result.get("engineering",{})
    verification=result.get("verification",{})
    observed=engineering.get("evidence",{}) if isinstance(engineering,dict) else {}
    hashes={k:observed[k] for k in ("sha256","base_sha256","candidate_sha256","size","count","already_repaired") if k in observed}
    proof=verification.get("proof") if isinstance(verification,dict) else None
    verifier_state=verification.get("state") if isinstance(verification,dict) else "HOLD"
    return {
        "schema":"enguru.controller.donecheck_producer.v1",
        "authority_contract":"governance/mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md",
        "intent":"Complete one approved bounded GitHub controller task with observable evidence",
        "task":{"id":task["id"],"action":task["action"],"target_repo":task["target_repo"],"path":task.get("path")},
        "successCriteria":["exact_current_source_and_task_contract","allowlisted_engineering_execution",
                           "second_source_or_test_verification","authentic_worker_and_commit_provenance",
                           "owner_authority_preservation"],
        "executionState":result["state"],
        "observation":[{"role":"ENGINEER","state":engineering.get("state")},
                       {"role":"VERIFIER","state":verifier_state,"proof":proof}],
        "evidence":[{"kind":"task_fingerprint","sha256":result["fingerprint"]},
                    {"kind":"source_commit","commit":result["source_commit"]},
                    {"kind":"engineering_observation","metadata":hashes},
                    {"kind":"internal_receipt","sha256":result.get("receipt_sha256")},
                    {"kind":"pr_handoff","url":result.get("pull_request")}],
        "verificationResult":"PASS" if verifier_state=="PASS" else "HOLD",
        "failureClass":verification.get("reason") if isinstance(verification,dict) else None,
        "correctionAction":"OWNER_REVIEW" if result["state"]=="PR_PENDING" else "GOVERNED_RETRY_OR_REVIEW",
        "attempt":result.get("attempt",1),
        "maxAttempts":result.get("max_attempts",task.get("max_attempts",2)),
        "doneCheckResult":"HOLD_EXTERNAL_DONECHECK_V1_2",
        "humanThresholdRequired":True,
        "finalState":"HOLD",
    }

def public_receipt(result,runid,task=None):
    """Publish independently hashable metadata without exposing candidate source bytes."""
    producer=result.get("engineering",{})
    evidence=producer.get("evidence",{}) if isinstance(producer,dict) else {}
    visible={k:evidence[k] for k in ("path","sha256","size","count","base_sha256","candidate_sha256","already_repaired") if k in evidence}
    verification=result.get("verification",{})
    receipt={
       "schema":"enguru.controller.public_receipt.v1",
       "state":result["state"],"task_id":result["task_id"],
       "fingerprint":result["fingerprint"],"source_commit":result["source_commit"],
       "producer_workflow":WORKFLOW,"producer_run_id":str(runid),
       "engineering":{"state":producer.get("state"),"evidence":visible},
       "verification":{"state":verification.get("state"),"proof":verification.get("proof"),"reason":verification.get("reason")},
       "full_receipt_sha256":result.get("receipt_sha256"),
       "pull_request":result.get("pull_request"),
       "official_verified_finish":result.get("official_verified_finish"),
    }
    if "schedule_observation" in result:receipt["schedule_observation"]=result["schedule_observation"]
    if task is not None:receipt["donecheck_producer_candidate"]=donecheck_producer_candidate(result,task)
    return receipt

def cycle(root,worklist,gate,completed=None,failed=None,commit=None,pending=None):
    if not gate_valid(gate):return hold("AUTHORITY_OR_ZERO_COST_GATE")
    if pending:
        return {"state":"AWAITING_HUMAN","reason":"GOVERNED_PR_REVIEW_PENDING","human_final_authority":"OWNER_RESERVED"}
    task,reason=select(worklist,set(completed or []),set(pending or []))
    if task is not None and (failed or {}).get(task["id"],0)>=task.get("max_attempts",2):
        return {"state":"AWAITING_MANAGEMENT","reason":"RETRY_BUDGET_REQUIRES_MANAGEMENT_REVIEW","human_final_authority":"OWNER_RESERVED"}
    if reason=="NO_ELIGIBLE_TASK":return {"state":"PASS_IDLE","tasks_executed":0,"owner_approval":"RESERVED"}
    if reason:return hold(reason)
    e=engineer(task,root);v=verifier(task,e,root)
    result={"schema":"enguru.controller.v3","state":"PR_PENDING" if e["state"]=="CANDIDATE_READY" and v["state"]=="PASS" else "PASS" if e["state"]=="PASS" and v["state"]=="PASS" else "HOLD_GUVENLI_DUR","task_id":task["id"],"fingerprint":key(task,root,commit),"source_commit":commit or "0"*40,"management":"TASK_SELECTED","engineering":e,"verification":v,"tasks_executed":1,"attempt":(failed or {}).get(task["id"],0)+1,
            "max_attempts":task.get("max_attempts",2),"human_final_authority":"OWNER_RESERVED","authorized_merge":False,"additional_spend_usd":0,"official_verified_finish":"HOLD_DONECHECK_HUMAN_GATE"}
    return finalize_receipt(result)
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
    worker_cache={}
    counted_hold_runs=set()
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
                if run.get("head_sha")!=commit or run.get("path")!=WORKFLOW or run.get("status")!="completed" or run.get("event") not in ("schedule","workflow_dispatch","push"):continue
                # A workflow's SUCCESS alone cannot prove the privileged worker actually executed.
                if runid not in worker_cache:
                    jobs=github(f"https://api.github.com/repos/{REPO}/actions/runs/{runid}/jobs?per_page=100",token)
                    entries=jobs.get("jobs") if isinstance(jobs,dict) else None
                    matches=[j for j in entries if isinstance(j,dict) and j.get("name")=="worker"] if isinstance(entries,list) else []
                    worker_cache[runid]=(matches[0].get("conclusion") if len(matches)==1 and matches[0].get("status")=="completed" else None)
                worker=worker_cache[runid]
                name=known[taskkey]
                if status=="PASS" and worker=="success" and run.get("conclusion")=="success":completed.add(name)
                if status=="PR_PENDING" and worker=="success" and run.get("conclusion")=="success":pending.add(name)
                # A governed HOLD exits 50, so the real worker and workflow both fail.
                # Its authenticated receipt must remain visible to the bounded retry budget.
                if status=="HOLD" and worker=="failure" and run.get("conclusion")=="failure":
                    event=(name,runid)
                    if event not in counted_hold_runs:
                        counted_hold_runs.add(event)
                        failed[name]=failed.get(name,0)+1
            except (ValueError,KeyError,TypeError):continue
        if len(comments)<100:return completed,pending,failed
    raise ValueError("HISTORY_PAGINATION_LIMIT")
def observe_schedule(token,runid):
    """Report a bounded observed cron window; platform scheduler has no timing guarantee."""
    url=f"https://api.github.com/repos/{REPO}/actions/workflows/enguru-five-minute-controller.yml/runs?event=schedule&per_page=25"
    try:
        response=github(url,token)
        runs=response["workflow_runs"]
        if not isinstance(runs,list):raise TypeError("SCHEDULE_LIST_SCHEMA")
        current=next((r for r in runs if str(r.get("id"))==str(runid) and r.get("event")=="schedule"),None)
        if current is None:return {"state":"HOLD","reason":"CURRENT_SCHEDULE_NOT_OBSERVED"}
        def timestamp(run):
            return datetime.fromisoformat(run["created_at"].replace("Z","+00:00"))
        now=timestamp(current)
        earlier=[]
        for run in runs:
            if str(run.get("id"))==str(runid) or run.get("event")!="schedule" or not run.get("created_at"):continue
            observed=timestamp(run)
            if observed<now:earlier.append((observed,run["id"]))
        earlier.sort(reverse=True)
        if not earlier:return {"state":"HOLD","reason":"PREVIOUS_SCHEDULE_NOT_OBSERVED"}
        window=[(now,int(runid))]+earlier[:3]
        gaps=[int((window[i][0]-window[i+1][0]).total_seconds()) for i in range(len(window)-1)]
        if any(gap<=0 for gap in gaps):return {"state":"HOLD","reason":"SCHEDULE_TIMESTAMP_ORDER"}
        over=sum(gap>420 for gap in gaps)
        state="PASS" if len(gaps)>=3 and over==0 else "HOLD"
        reason=("OBSERVED_THREE_INTERVAL_WINDOW" if state=="PASS" else
                "SCHEDULE_CADENCE_GAP" if over else "INSUFFICIENT_CONSECUTIVE_OBSERVATIONS")
        return {"state":state,"reason":reason,"last_gap_seconds":gaps[0],
                "gap_seconds":gaps[0],"expected_seconds":300,
                "observed_intervals":len(gaps),"observed_gaps_seconds":gaps,
                "gaps_over_tolerance":over,"tolerance_seconds":420,
                "previous_run_id":window[1][1],"observed_run_id":int(runid)}
    except (HTTPError,URLError,TimeoutError,ValueError,KeyError,TypeError,OSError):
        return {"state":"HOLD","reason":"SCHEDULE_TELEMETRY_UNAVAILABLE"}

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
        # A matching file SHA alone is insufficient: protect against hidden extra PR changes.
        files=github(f"https://api.github.com/repos/{REPO}/pulls/{prior}/files?per_page=100",token)
        if not isinstance(files,list) or len(files)!=1 or files[0].get("filename")!=path or files[0].get("status")!="modified":
            raise ValueError("PR_REFERENCE_DIFF_SCOPE")
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
            if os.getenv("GITHUB_EVENT_NAME")=="schedule":
                result["schedule_observation"]=observe_schedule(token,runid)
            finalize_receipt(result)
            if result.get("task_id"):
                name=result["task_id"]
                status="PASS" if result["state"]=="PASS" else "PR_PENDING" if result["state"]=="PR_PENDING" else "HOLD"
                marker=MARKER+status+":"+name+":"+result["fingerprint"]+":"+runid+":"+commit
                public=public_receipt(result,runid,next(t for t in tasks["tasks"] if t["id"]==name))
                public_json=canonical(public)
                public_sha=sha(public_json.encode())
                body=(f"<!-- {marker} -->\nENGURU verified task: {name}\n"
                      f"Engineer: {result['engineering']['state']}; verifier: {result['verification']['state']}; "
                      f"receipt: {result['receipt_sha256']}; Human Threshold: owner; "
                      f"PR handoff: {result.get('pull_request', 'N/A')}.\n"
                      f"PUBLIC_RECEIPT_SHA256={public_sha}\n"
                      f"\x60\x60\x60json\n{public_json}\n\x60\x60\x60")
                github(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/comments",token,{"body":body})
        except (HTTPError,URLError,TimeoutError,ValueError,KeyError,TypeError,OSError) as e:result=hold("GITHUB_EVIDENCE_TRANSPORT_"+type(e).__name__)
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("STATE="+result["state"])
    if "schedule_observation" in result:print("SCHEDULE_OBSERVATION="+canonical(result["schedule_observation"]))
    return 0 if result["state"] in ("PASS","PASS_IDLE","PR_PENDING","AWAITING_HUMAN","AWAITING_MANAGEMENT") else 50
if __name__=="__main__":raise SystemExit(main())
