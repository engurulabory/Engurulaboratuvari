#!/usr/bin/env python3
"""Candidate-only SHA256 delivery inventory. Produces no native authority or OSi writes."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

FILES = (
 "tools/enguru_suzgec_v24_source_preflight.py",
 "tools/enguru_suzgec_v24_presend_source_binding.py",
 "tools/enguru_suzgec_v24_github_test_terminal.py",
 "tools/enguru_suzgec_v24_dependency_inventory.py",
 "tools/enguru_suzgec_v24_recovery_fixture.py",
 "tools/enguru_suzgec_v24_terminal_twin_parity.py",
 "tools/enguru_suzgec_v24_language_presend.py",
 "tests/test_enguru_suzgec_v24_source_preflight.py",
 "tests/test_enguru_suzgec_v24_presend_source_binding.py",
 "tests/test_enguru_suzgec_v24_recovery_fixture.py",
 "tests/test_enguru_suzgec_v24_dependency_inventory.py",
 "tests/test_enguru_suzgec_v24_terminal_twin_parity.py",
 "tests/test_enguru_suzgec_v24_finish_verdict_stop.py",
 "tests/test_enguru_plive_progress_contract_v1.py",
 "tools/enguru_suzgec_v24_goal_acceptance_loop.py",
 "tests/test_enguru_suzgec_v24_goal_acceptance_loop.py",
 "tests/test_enguru_suzgec_v24_final_sequence_lock.py",
 "tests/test_enguru_suzgec_v24_delivery_inventory_scope.py",
 "tools/enguru_suzgec_v24_transitive_closure.py",
 "tests/test_enguru_suzgec_v24_transitive_closure.py",
 "governance/work-protocol/ENGURU_SUZGEC_V24_LANGUAGE_ALIGNMENT_CONTRACT_V1.json",
)
def build(root):
 root=Path(root).resolve(strict=True)
 result={"schema":"enguru.suzgec.v24.github-delivery-inventory/v1","state":"HOLD_GUVENLI_DUR","verifiedFinish":"HOLD","scope":"GITHUB_CANDIDATE_ONLY","files":{},"blockers":[],"dependencyClosure":"HOLD_NOT_PROVEN","nativeProducerBinding":"HOLD_NOT_PROVEN"}
 for name in FILES:
  target=root/name
  if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root):
   result["blockers"].append("MISSING_OR_UNSAFE:"+name)
  else:
   result["files"][name]=hashlib.sha256(target.read_bytes()).hexdigest()
 try:
  p=subprocess.run(["git","rev-parse","HEAD"],cwd=root,text=True,capture_output=True,timeout=5,check=True)
  result["git_commit"]=p.stdout.strip()
 except (OSError,subprocess.SubprocessError):
  result["blockers"].append("GIT_HEAD_UNAVAILABLE")
 if not result["blockers"]:
  result["state"]="PASS_BOUNDED_GITHUB_SOURCE_INVENTORY_ONLY"
 return result
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--root",required=True)
 ap.add_argument("--out",required=True)
 args=ap.parse_args()
 result=build(args.root)
 dest=Path(args.out)
 if dest.exists() or dest.is_symlink():
  raise SystemExit("HOLD_OUTPUT_EXISTS")
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(result,indent=2,sort_keys=True),encoding="utf-8")
 print(json.dumps({"state":result["state"],"file_count":len(result["files"]),"blockers":result["blockers"],"verifiedFinish":"HOLD"},sort_keys=True))
 return 0 if result["state"]=="PASS_BOUNDED_GITHUB_SOURCE_INVENTORY_ONLY" else 50
if __name__=="__main__":
 raise SystemExit(main())
