"""ENGURU B09 authenticated one-case source correction verifier.

The live GitHub API is the sole source of provenance. This never authorizes
product changes, owner signatures, DoneCheck or generalized learning claims.
"""
import hashlib
import json
import os
import sqlite3
from urllib.request import Request, urlopen
from tools import enguru_mk_intelligence_v5 as v5

REPO="engurulabory/Engurulaboratuvari"
HEAD="80b2ca7fde92ec74c3e08229ac179ff8f5c27a3b"
BRANCH="feat/enguru-mk-verified-learning-regression-20261024"
CASE="CASE-V4SILENTCLI20261024"
SOURCE="d23588e0996d1e20ce1a17974d1c3fd4d1cd4b39333371f36de7cd456b19f0da"
WF=".github/workflows/enguru-mk-v5-real-regression-verify.yml"
RUNS={40116582389:("push",WF),
      40116627850:("pull_request",WF),
      40116627848:("pull_request",".github/workflows/ip-model-trust-fleet.yml")}
PINS={
"governance/enguru-suzgeci/learning/bridge/evidence/v4_dispatch_legacy_entrypoint.txt":"ac9c058ad8b0e05c5702da61b6462b1353adee1b284656675f0699bd87476d98",
"governance/enguru-suzgeci/learning/bridge/evidence/v4_dispatch_repaired_entrypoint.txt":SOURCE,
"tests/test_mk_real_regression_case_v1.py":"60741ff3f537fd979652bf1ec147e82bc2d65b834f40af1ad0314b6368d00d04",
WF:"05d1809d3d0bd869d7b814d73ea46a47bed2e8a874463fa73e00e8b549b71790"}
class Hold(Exception):pass
def sha(x):return hashlib.sha256(x).hexdigest()
def canon(x):return (json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()
def api(token):
    if not isinstance(token,str) or len(token)<12:raise Hold("HOLD_AUTH")
    paths={f"/repos/{REPO}/actions/runs/{i}" for i in RUNS}
    paths|={f"/repos/{REPO}/actions/runs/40116627850/jobs?per_page=100",f"/repos/{REPO}/pulls/218"}
    def get(path):
        if path not in paths:raise Hold("HOLD_API_SCOPE")
        req=Request("https://api.github.com"+path,headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json"})
        try:
            with urlopen(req,timeout=20) as r:
                if r.status!=200:raise Hold("HOLD_HTTP")
                raw=r.read(1048577)
            if len(raw)>1048576:raise Hold("HOLD_SIZE")
            return json.loads(raw)
        except (OSError,ValueError) as e:raise Hold("HOLD_API") from e
    return get
def verify(get,root):
    from pathlib import Path
    for rel,pin in PINS.items():
        p=Path(root)/rel
        if p.is_symlink() or not p.is_file() or sha(p.read_bytes())!=pin:raise Hold("HOLD_SOURCE_SHA")
    confirmed=[]
    for run_id,(event,path) in RUNS.items():
        r=get(f"/repos/{REPO}/actions/runs/{run_id}")
        if not isinstance(r,dict):raise Hold("HOLD_RUN")
        for key,value in {"id":run_id,"event":event,"path":path,"head_sha":HEAD,"head_branch":BRANCH,"status":"completed","conclusion":"success"}.items():
            if type(r.get(key)) is not type(value) or r[key]!=value:raise Hold("HOLD_RUN_"+key)
        if r.get("repository",{}).get("full_name")!=REPO or r.get("actor",{}).get("login")!="engurulabory":raise Hold("HOLD_ACTOR")
        if not isinstance(r.get("workflow_id"),int):raise Hold("HOLD_WORKFLOW")
        confirmed.append((run_id,r["workflow_id"]))
    jobs=get(f"/repos/{REPO}/actions/runs/40116627850/jobs?per_page=100")
    matches=[j for j in jobs.get("jobs",[]) if j.get("name")=="independent-regression"] if isinstance(jobs,dict) else []
    if len(matches)!=1 or matches[0].get("status")!="completed" or matches[0].get("conclusion")!="success":raise Hold("HOLD_JOB")
    if any(s.get("conclusion") in ("failure","cancelled","timed_out") for s in (matches[0].get("steps") or [])):raise Hold("HOLD_STEPS")
    pr=get(f"/repos/{REPO}/pulls/218")
    if pr.get("number")!=218 or pr.get("state")!="open" or pr.get("head",{}).get("sha")!=HEAD or pr.get("head",{}).get("ref")!=BRANCH:raise Hold("HOLD_PR")
    proof=sha(canon({"schema":"enguru.mk.b09-single-case/v1","case":CASE,"commit":HEAD,"runs":confirmed,"pins":PINS}))
    if proof==SOURCE:raise Hold("HOLD_DISTINCT_PROOF")
    return proof
def check_learning(get,root):
    def verifier(case,candidate):
        if case!=CASE or tuple(candidate)!=("SOURCE_AUDIT","PASS",SOURCE):raise Hold("HOLD_CASE_BINDING")
        return "INDEPENDENT_CI",verify(get,root)
    with sqlite3.connect(":memory:") as db:
        v5.candidate(db,CASE,"SOURCE_AUDIT","PASS",SOURCE)
        result=v5.promote(db,CASE,verifier)
        if result!="VERIFIED_EVIDENCE_ONLY" or v5.trusted_stats(db)!={"SOURCE_AUDIT":(1,1)}:raise Hold("HOLD_LEARNING")
    return {"state":"PASS_ONE_HISTORIC_CASE_CI_ONLY","verifiedCases":1,"macProductWrites":0,
      "generalizedLearning":"HOLD_MULTI_CASE_FIELD","officialAcceptance":"HOLD_CANONICAL_DONECHECK"}
if __name__=="__main__":
    try:
        if os.environ.get("GITHUB_ACTIONS")!="true":raise Hold("HOLD_LIVE_GITHUB_ACTIONS_REQUIRED")
        print(json.dumps(check_learning(api(os.environ.get("GITHUB_TOKEN","")),"."),sort_keys=True))
    except (Hold,v5.Hold) as e:
        print("STATE=HOLD_GUVENLI_DUR;REASON="+str(e));raise SystemExit(50)
