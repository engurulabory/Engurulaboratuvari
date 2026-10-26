"""K03: inspect installed CLI binaries without login, API calls or user data.

GitHub runner installs into ephemeral isolated temp root with npm scripts disabled.
This is a CLI *smoke test*, not an authorized Codex/Claude agent task.
"""
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
def run(command, timeout=50):
    cp=subprocess.run(command,text=True,capture_output=True,timeout=timeout,
                      env={k:v for k,v in os.environ.items() if k in ("PATH","HOME","LANG","LC_ALL","TERM","CI")})
    return {"returncode":cp.returncode,"stdout":cp.stdout[-600:],"stderr":cp.stderr[-500:]}

def main():
    out={"schema":"enguru.harvest.k03-cli-smoke/v1","scope":"GITHUB_EPHEMERAL_VERSION_ONLY",
         "agent_task_executed":False,"authenticated":False,"paid_api_calls":0,
         "osi_execution":0,"official_proven":"HOLD","cli":{}}
    for label,command in (("P01_codex",["codex","--version"]),
                          ("P02_claude",["claude","--version"])):
        obs=run(command)
        obs["nonempty_version"]=bool(obs["stdout"].strip() or obs["stderr"].strip())
        if obs["returncode"]!=0 or not obs["nonempty_version"]:
            out["status"]="HOLD_CLI_SMOKE"
        out["cli"][label]=obs
    if "status" not in out:
        out["status"]="PASS_UNAUTHENTICATED_CLI_VERSION_SMOKE"
    (HERE/"k03-cli-version-receipt.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    if out["status"].startswith("HOLD"):
        raise SystemExit(1)

if __name__=="__main__":
    main()
