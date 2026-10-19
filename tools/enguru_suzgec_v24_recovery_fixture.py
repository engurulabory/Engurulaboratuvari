"""Deterministic subprocess interruption/restart rehearsal, bounded to temporary files.

No native OSi authority; test verifies idempotent recovery of a fixture journal only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

WORKER = r'''
import json, os, pathlib, sys, time
root=pathlib.Path(sys.argv[1])
phase=sys.argv[2]
journal=root/"journal.json"
if phase=="begin":
    journal.write_text(json.dumps({"status":"PREPARED","item":"fixture-001"}))
    print("PREPARED",flush=True)
    time.sleep(45)
elif phase=="resume":
    state=json.loads(journal.read_text())
    if state.get("item")!="fixture-001" or state.get("status") not in ("PREPARED","COMMITTED"):
        raise SystemExit(52)
    state["status"]="COMMITTED"
    (root/"result.json").write_text(json.dumps({"item":"fixture-001","count":1},sort_keys=True))
    journal.write_text(json.dumps(state,sort_keys=True))
    print("COMMITTED",flush=True)
else:
    raise SystemExit(53)
'''

def run_recovery_fixture():
    with tempfile.TemporaryDirectory(prefix="enguru-recovery-") as folder:
        root=Path(folder)
        proc=subprocess.Popen([sys.executable,"-B","-c",WORKER,str(root),"begin"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        try:
            # Wait for durable PREPARED marker; inject a real subprocess SIGKILL.
            for _ in range(200):
                if (root/"journal.json").exists():
                    try:
                        if json.loads((root/"journal.json").read_text()).get("status")=="PREPARED":
                            break
                    except (OSError,ValueError):
                        pass
                if proc.poll() is not None: raise RuntimeError("WORKER_EARLY_EXIT")
                time.sleep(0.02)
            else: raise RuntimeError("PREPARE_TIMEOUT")
            os.kill(proc.pid, signal.SIGKILL)
            proc.communicate(timeout=5)
            if proc.returncode == 0: raise RuntimeError("INTERRUPTION_NOT_OBSERVED")
            observed=[]
            for _ in range(2):
                result=subprocess.run([sys.executable,"-B","-c",WORKER,str(root),"resume"],capture_output=True,text=True,timeout=8)
                if result.returncode: raise RuntimeError("RESUME_FAILED")
                observed.append((root/"result.json").read_bytes())
            final=json.loads(observed[-1])
            if observed[0]!=observed[1] or final!={"item":"fixture-001","count":1}:
                raise RuntimeError("NON_IDEMPOTENT_REPLAY")
            return {"state":"PASS_FIXTURE_INTERRUPTION_RECOVERY","kill_signal":"SIGKILL","resume_runs":2,"result_sha256":hashlib.sha256(observed[-1]).hexdigest(),"scope":"TEMP_FIXTURE_ONLY"}
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate(timeout=5)
if __name__=="__main__":
    print(json.dumps(run_recovery_fixture(),sort_keys=True))
