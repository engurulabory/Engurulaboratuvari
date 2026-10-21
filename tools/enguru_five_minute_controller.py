#!/usr/bin/env python3
"""ENGURU governed scheduled Management -> Engineer -> Verifier, scoped to public Labory."""
import argparse,hashlib,json,os,re,subprocess,sys
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

REPO="engurulabory/Engurulaboratuvari"
ISSUE=192
MARKER="ENGURU_CONTROLLER_V2:"
TEST="tests/test_enguru_five_minute_controller.py"
def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"))
def hold(reason):return {"state":"HOLD_GUVENLI_DUR","reason":reason}
def key(task):return sha(canonical({k:task.get(k) for k in ("id","action","path","expected_sha256","dependencies","target_repo")}).encode())
def safe_file(root,relative):
    if not isinstance(relative,str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts or ".git" in Path(relative).parts:return None
    try:
        root=root.resolve(strict=True);p=(root/relative).resolve(strict=True);p.relative_to(root)
        return p if p.is_file() else None
    except (OSError,ValueError):return None
def gate_valid(gate):
    required={"state":"ENABLED_READONLY","repository":REPO,"max_tasks_per_cycle":1,"max_additional_spend_usd":0,"paid_providers":False,"human_final_authority":"OWNER"}
    return isinstance(gate,dict) and all(gate.get(k)==v for k,v in required.items())
def select(worklist,completed):
    tasks=worklist.get("tasks") if isinstance(worklist,dict) else None
    if not isinstance(tasks,list):return None,"WORKLIST_REQUIRED"
    ids=[]
    for t in tasks:
        if not isinstance(t,dict) or not re.fullmatch("[A-Z][A-Z0-9_]{2,79}",str(t.get("id",""))):return None,"TASK_ID_INVALID"
        ids.append(t["id"])
        if t.get("target_repo")!=REPO:return None,"PRIVATE_REPO_GRANT_REQUIRED"
        if t.get("action") not in ("verify_file_digest","run_unit_test"):return None,"ACTION_GRANT_REQUIRED"
        if t.get("action")=="verify_file_digest" and not re.fullmatch("[0-9a-f]{64}",str(t.get("expected_sha256",""))):return None,"EXPECTED_DIGEST_REQUIRED"
        if t.get("action")=="run_unit_test" and t.get("path")!=TEST:return None,"TEST_RECIPE_SCOPE"
        if not isinstance(t.get("dependencies",[]),list):return None,"DEPENDENCY_SCHEMA"
    if len(ids)!=len(set(ids)):return None,"DUPLICATE_TASK_IDS"
    if any(d not in ids for t in tasks for d in t.get("dependencies",[])):return None,"DEPENDENCY_AUTHORITY"
    candidates=[t for t in tasks if t.get("state")=="READY" and t["id"] not in completed and set(t.get("dependencies",[])).issubset(completed)]
    if not candidates:return None,"NO_ELIGIBLE_TASK"
    try:candidates.sort(key=lambda t:(int(t.get("priority",100)),t["id"]))
    except (TypeError,ValueError):return None,"INVALID_PRIORITY"
    return candidates[0],None
def test_once(root):
    return subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-p","test_enguru_five_minute_controller.py","-v"],cwd=root,capture_output=True,text=True,timeout=60,check=False)
def engineer(task,root):
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
def cycle(root,worklist,gate,completed=None):
    if not gate_valid(gate):return hold("AUTHORITY_OR_ZERO_COST_GATE")
    task,reason=select(worklist,set(completed or []))
    if reason=="NO_ELIGIBLE_TASK":return {"state":"PASS_IDLE","tasks_executed":0,"owner_approval":"RESERVED"}
    if reason:return hold(reason)
    e=engineer(task,root);v=verifier(task,e,root)
    result={"schema":"enguru.controller.v2","state":"PASS" if v["state"]=="PASS" else "HOLD_GUVENLI_DUR","task_id":task["id"],"fingerprint":key(task),"management":"TASK_SELECTED","engineering":e,"verification":v,"tasks_executed":1,"human_final_authority":"OWNER_RESERVED","authorized_merge":False,"additional_spend_usd":0}
    result["receipt_sha256"]=sha(canonical(result).encode())
    return result
def github(url,token,body=None):
    data=None if body is None else json.dumps(body).encode()
    h={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}
    if data is not None:h["Content-Type"]="application/json"
    with urlopen(Request(url,headers=h,data=data,method="POST" if data is not None else "GET"),timeout=12) as f:return json.load(f)
def receipts(token):
    out=set()
    for page in range(1,6):
        comments=github(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/comments?per_page=100&page={page}",token)
        for c in comments:
            if c.get("user",{}).get("login")=="github-actions[bot]" and MARKER in c.get("body",""):
                out.add(c["body"].split(MARKER,1)[1].split("-->",1)[0].strip())
        if len(comments)<100:return out
    raise ValueError("EVIDENCE_PAGINATION_LIMIT")
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
            token=os.environ["GITHUB_TOKEN"];old=receipts(token)
            completed={t["id"] for t in tasks.get("tasks",[]) if t["id"]+":"+key(t) in old}
            result=cycle(root,tasks,gate,completed)
            if result["state"]=="PASS" and result["task_id"]+":"+result["fingerprint"] not in receipts(token):
                marker=MARKER+result["task_id"]+":"+result["fingerprint"]
                body=f"<!-- {marker} -->\nENGURU verified task: {result['task_id']}\nEngineer PASS; verifier PASS; receipt {result['receipt_sha256']}; owner final authority reserved."
                github(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/comments",token,{"body":body})
        except (HTTPError,URLError,TimeoutError,ValueError) as e:result=hold("GITHUB_EVIDENCE_TRANSPORT_"+type(e).__name__)
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("STATE="+result["state"])
    return 0 if result["state"] in ("PASS","PASS_IDLE") else 50
if __name__=="__main__":raise SystemExit(main())
