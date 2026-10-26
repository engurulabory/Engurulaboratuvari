"""K03: inspect installed CLI binaries without login, API calls or user data.

GitHub runner installs into ephemeral isolated temp root with npm scripts disabled.
This is a CLI *smoke test*, not an authorized Codex/Claude agent task.
"""
import errno
import json
import os
import shutil
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
def run(command, timeout=50):
    env={k:v for k,v in os.environ.items() if k in ("PATH","HOME","LANG","LC_ALL","TERM","CI")}
    try:
        cp=subprocess.run(command,text=True,capture_output=True,timeout=timeout,env=env)
    except OSError as exc:
        # Deprecated npm Claude CLI can ship a JS entrypoint without a shebang
        # on Linux. Explicit Node invocation is equivalent to npm's wrapper.
        if exc.errno==errno.ENOEXEC and command[0]=="claude":
            file=shutil.which("claude",path=env.get("PATH"))
            if file:
                command=["node",file,*command[1:]]
                cp=subprocess.run(command,text=True,capture_output=True,timeout=timeout,env=env)
            else:
                raise
        else:
            raise
    return {"returncode":cp.returncode,"stdout":cp.stdout[-600:],
            "stderr":cp.stderr[-500:],"invoked_with_node":command[0]=="node"}

def main():
    out={"schema":"enguru.harvest.k03-cli-smoke/v1","scope":"GITHUB_EPHEMERAL_VERSION_ONLY",
         "agent_task_executed":False,"authenticated":False,"paid_api_calls":0,
         "osi_execution":0,"official_proven":"HOLD","cli":{}}
    for label,command in (("P01_codex",["codex","--version"]),
                          ("P02_claude",["claude","--version"])):
        obs=run(command)
        obs["nonempty_version"]=bool(obs["stdout"].strip() or obs["stderr"].strip())
        obs["state"]="PASS_VERSION_ONLY" if obs["returncode"]==0 and obs["nonempty_version"] else "HOLD_DISTRIBUTION_OR_RUNTIME"
        out["cli"][label]=obs
    out["codex_version_observed"]=out["cli"]["P01_codex"]["state"]=="PASS_VERSION_ONLY"
    out["claude_version_observed"]=out["cli"]["P02_claude"]["state"]=="PASS_VERSION_ONLY"
    out["evidence_collection_pass"]=True
    out["state"]="PASS_BOTH_VERSION_ONLY" if out["codex_version_observed"] and out["claude_version_observed"] else "PARTIAL_CLI_OBSERVATION_CLAUDE_HOLD"
    out["claude_native_installer_executed"]=False
    (HERE/"k03-cli-version-receipt.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    if not out["codex_version_observed"]:
        raise SystemExit("HOLD_CODEX_VERSION_NOT_OBSERVED")

if __name__=="__main__":
    main()
