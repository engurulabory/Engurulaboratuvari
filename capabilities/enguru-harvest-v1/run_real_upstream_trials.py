"""Three real upstream tool trials performed only on GitHub runner.

P09 Hypothesis property regressions run as a separate subprocess.
P10 Ruff validates actual ENGURU Harvest Python source.
P11 uv creates and checks an offline lock for a no-dependency fixture.
Outputs are technical execution observations, not human-reviewed PROVEN skills.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from importlib.metadata import version

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
def run(command,cwd=HERE):
    r=subprocess.run(command,cwd=cwd,text=True,capture_output=True,timeout=120)
    return {"command":command,"returncode":r.returncode,"stdout_tail":r.stdout[-3500:],"stderr_tail":r.stderr[-1800:]}
def main():
    observations={
        "schema":"enguru.harvest.real-upstream-ci-trials/v1",
        "scope":"GITHUB_ONLY_THREE_EXTERNAL_TOOLS",
        "osi_execution":0,
        "github_head":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO,text=True).strip(),
        "versions":{x:version(x) for x in ("ruff","hypothesis","uv")},
        "paid_api_required":0,
        "results":{},
        "external_proven_skills":0,
        "independent_review":"HOLD",
        "github_verified_finish":"HOLD",
    }
    files=sorted(p.name for p in HERE.glob("*.py"))
    observations["results"]["P10_ruff"]=run(["ruff","check","--select","E4,E7,E9,F",*files])
    observations["results"]["P09_hypothesis"]=run([sys.executable,"-B","-m","unittest","-q","test_upstream_hypothesis"])
    with tempfile.TemporaryDirectory(prefix="enguru-uv-ci-") as tmp:
        d=Path(tmp)
        (d/"pyproject.toml").write_text(
            '[project]\nname = "enguru-harvest-ci-fixture"\nversion = "0.1.0"\nrequires-python = ">=3.12"\ndependencies = []\n',
            encoding="utf-8",
        )
        first=run(["uv","lock","--offline"],d)
        lock=d/"uv.lock"
        digest1=hashlib.sha256(lock.read_bytes()).hexdigest() if lock.is_file() else None
        second=run(["uv","lock","--offline","--check"],d)
        digest2=hashlib.sha256(lock.read_bytes()).hexdigest() if lock.is_file() else None
        observations["results"]["P11_uv"]={
            "first":first,"second":second,
            "lock_sha256_first":digest1,"lock_sha256_second":digest2,
            "identical_bytes":digest1 is not None and digest1==digest2,
        }
    status=(
        observations["results"]["P10_ruff"]["returncode"]==0 and
        observations["results"]["P09_hypothesis"]["returncode"]==0 and
        observations["results"]["P11_uv"]["first"]["returncode"]==0 and
        observations["results"]["P11_uv"]["second"]["returncode"]==0 and
        observations["results"]["P11_uv"]["identical_bytes"]
    )
    observations["status"]="PASS_GITHUB_REAL_EXECUTION_UNREVIEWED" if status else "HOLD_TRIAL_FAILURE"
    Path("upstream-tool-trial-receipt.json").write_text(
        json.dumps(observations,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8",
    )
    print(json.dumps(observations,indent=2,ensure_ascii=False))
    if not status:
        raise SystemExit(1)

if __name__=="__main__":
    main()
