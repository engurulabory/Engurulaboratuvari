#!/usr/bin/env python3
"""ENGURU v2.4 four-cycle GitHub test terminal. Candidate-only, no OSi authority."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.enguru_suzgec_v24_dependency_inventory import inventory
OUT=Path(os.environ.get("RUNNER_TEMP", "/tmp"))/"enguru-v24-terminal-receipt.json"
TESTS=[
 "test_enguru_suzgec_v24_finish_verdict_stop.py",
 "test_enguru_plive_progress_contract_v1.py",
 "test_enguru_suzgec_v24_source_preflight.py",
 "test_enguru_suzgec_v24_presend_source_binding.py",
 "test_enguru_suzgec_v24_recovery_fixture.py",
 "test_enguru_suzgec_v24_dependency_inventory.py",
]
def sha(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()
def execute():
 receipt={"schema":"enguru.suzgec.v24.github-test-terminal/v1","verifiedFinish":"HOLD","officialOSiAcceptance":"HOLD","cycles":{},"state":"HOLD_GUVENLI_DUR"}
 c=receipt["cycles"]
 try:
  if platform.system()!="Darwin" or not os.environ.get("GITHUB_ACTIONS"):
   raise ValueError("REQUIRES_GITHUB_MACOS_RUNNER")
  paths=[ROOT/"tools"/"enguru_suzgec_v24_source_preflight.py", ROOT/"tools"/"enguru_suzgec_v24_presend_source_binding.py", ROOT/"tools"/"enguru_suzgec_v24_recovery_fixture.py", ROOT/"tools"/"enguru_suzgec_v24_dependency_inventory.py"]
  paths.extend(ROOT/"tests"/name for name in TESTS)
  if not all(p.is_file() and not p.is_symlink() for p in paths):
   raise ValueError("REQUIRED_SOURCE_MISSING")
  deps=inventory(ROOT,TESTS)
  if deps["state"]!="PASS_DIRECT_IMPORTS_RESOLVED": raise ValueError("TEST_IMPORT_DEPENDENCIES_HOLD:"+json.dumps(deps["blockers"]))
  c["D1"]={"dependencies":deps,"state":"PASS_TEST_SCOPE_DISCOVERED","test_files":TESTS,"source_sha256":{str(p.relative_to(ROOT)):sha(p) for p in paths},"os":platform.platform()}
  prediction={"schema":"enguru.suzgec.v24.github-prediction/v1","source_sha256":c["D1"]["source_sha256"],"expected_return_codes":{name:0 for name in TESTS},"scope":"GITHUB_TEST_FIXTURES_ONLY"}
  c["D1"]["prediction"]=prediction
  results=[]
  for name in TESTS:
   start=time.monotonic()
   proc=subprocess.run([sys.executable,"-B","-m","unittest","discover","-s","tests","-p",name,"-v"],cwd=ROOT,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},capture_output=True,text=True,timeout=90)
   results.append({"file":name,"rc":proc.returncode,"duration_seconds":round(time.monotonic()-start,4),"output_tail":(proc.stdout+proc.stderr)[-6000:]})
  observed={r["file"]:r["rc"] for r in results}
  matches=observed==prediction["expected_return_codes"]
  c["D2"]={"state":"PASS_ACTUAL_COMMANDS" if matches else "HOLD_PREDICTION_OBSERVATION_MISMATCH","executions":results,"prediction_observation_match":matches}
  if c["D2"]["state"]!="PASS_ACTUAL_COMMANDS":
   raise ValueError("TEST_EXECUTION_FAILED")
  # Verify adversarial test names really executed by runner; not real process-recovery proof.
  logs="\n".join(r["output_tail"] for r in results)
  expected=("test_changed_source_holds","test_stale_prediction_holds","test_source_change_skips_language","test_missing_draft_holds")
  if any(n not in logs for n in expected): raise ValueError("NEGATIVE_TEST_EVIDENCE_MISSING")
  if "test_actual_kill_and_idempotent_resume" not in logs: raise ValueError("FIXTURE_RECOVERY_TEST_MISSING")
  c["D3"]={"state":"PASS_FIXTURE_RECOVERY_AND_NEGATIVE_TESTS","required":list(expected),"actual_recovery":"PASS_TEMP_FIXTURE_ONLY","native_recovery":"HOLD_NOT_TESTED"}
  if any(sha(p)!=c["D1"]["source_sha256"][str(p.relative_to(ROOT))] for p in paths):
   raise ValueError("SOURCE_CHANGED_DURING_RUN")
  c["D4"]={"state":"PASS_GITHUB_SOURCE_RECHECK","native_osi_source_parity":"HOLD_NOT_OBSERVED","native_authority":"HOLD_NOT_OBSERVED"}
  receipt["state"]="PASS_GITHUB_TERMINAL_PREPARATION_ONLY"
 except Exception as exc:
  receipt["reason"]=str(exc)
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True),encoding="utf-8")
 print(json.dumps({"state":receipt["state"],"receipt":str(OUT),"verifiedFinish":"HOLD","cycles":{k:v["state"] for k,v in c.items()}},ensure_ascii=False))
 return 0 if receipt["state"]=="PASS_GITHUB_TERMINAL_PREPARATION_ONLY" else 50
if __name__=="__main__":
 raise SystemExit(execute())
