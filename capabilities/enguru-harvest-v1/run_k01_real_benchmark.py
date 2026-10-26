"""K01: real GitHub-runner benchmark for a real ENGURU source operation.

Compare a verbatim old quadratic duplicate scan against the current optimized
kernel, on five identical-task paired inputs. No synthetic timings accepted.
Quality parity must pass first; results demonstrate microbenchmark value only.
"""
import hashlib
import json
import platform
import random
import subprocess
import time
from pathlib import Path
from skill_kernel import execute

HERE=Path(__file__).resolve().parent
BASELINE_SOURCE="sorted({x for x in ids if ids.count(x)>1})"
OLD_SHA=hashlib.sha256(BASELINE_SOURCE.encode("utf-8")).hexdigest()

def old_duplicate_check(ids):
    return sorted({x for x in ids if ids.count(x)>1})

def trial_input(seed):
    values=[f"SRC-{i:05d}" for i in range(3300)]
    values+=["SRC-00004","SRC-02000","SRC-02000","SRC-03299"]
    rng=random.Random(seed)
    rng.shuffle(values)
    return values

def run_trials():
    pairs=[]
    samples=[]
    negative_cases=[[],[""],[None],["A","A"],["x","y"]]
    for ids in negative_cases:
        actual=execute("duplicate-check",{"identifiers":ids})
        if not ids or all(isinstance(x,str) and bool(x) for x in ids):
            expected=old_duplicate_check(ids)
            if actual.get("duplicates")!=expected:
                raise RuntimeError("NEGATIVE_ORACLE_DIVERGENCE")
        elif actual["state"]!="HOLD":
            raise RuntimeError("UNTRUSTED_ID_ACCEPTED")
    for seed in (11,17,23,31,47):
        data=trial_input(seed)
        snapshot=json.dumps(data,separators=(",",":"),ensure_ascii=True).encode()
        t0=time.perf_counter_ns()
        expected=old_duplicate_check(data)
        t1=time.perf_counter_ns()
        result=execute("duplicate-check",{"identifiers":data})
        t2=time.perf_counter_ns()
        if result["duplicates"]!=expected or result["state"]!="HOLD":
            raise RuntimeError("QUALITY_REGRESSION")
        baseline=(t1-t0)/1_000_000_000
        candidate=(t2-t1)/1_000_000_000
        if baseline<=0 or candidate<=0:
            raise RuntimeError("INVALID_REAL_TIMING")
        samples.append({"seed":seed,"input_sha256":hashlib.sha256(snapshot).hexdigest(),
                        "items":len(data),"identical_output":True,
                        "baseline_seconds":baseline,"candidate_seconds":candidate,
                        "output_sha256":hashlib.sha256(json.dumps(expected).encode()).hexdigest()})
        pairs.append({"task_id":"ENGURU_DUPLICATE_SOURCE_ID_RECONCILIATION",
                      "baseline_seconds":baseline,"candidate_seconds":candidate,
                      "baseline_quality":100,"candidate_quality":100,
                      "baseline_success":True,"candidate_success":True})
    gain=execute("paired-gain",{"paired_runs":pairs})
    record={"schema":"enguru.harvest.k01-real-github-microbench/v1",
            "github_head":subprocess.check_output(["git","rev-parse","HEAD"],cwd=HERE.parents[1],text=True).strip(),
            "python":platform.python_version(),"device":"GITHUB_ACTIONS_UBUNTU_RUNNER",
            "task":"Duplicate source identity reconciliation over 3,304 items",
            "samples":samples,"measured_gain_classifier":gain,
            "baseline_expression_sha256":OLD_SHA,
            "quality_parity":all(x["identical_output"] for x in samples),
            "real_user_effect":"HOLD_NOT_MEASURED",
            "independent_review":"HOLD","external_skill_proven":0,"osi_execution":0}
    record["state"]="PASS_REAL_GITHUB_MICROBENCH_CANDIDATE" if gain["state"]=="MEASURED_GAIN_CANDIDATE" else "HOLD_MICROBENCH"
    (HERE/"k01-real-microbench-receipt.json").write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(record,indent=2,sort_keys=True))
    if record["state"].startswith("HOLD"):
        raise SystemExit(1)

if __name__=="__main__":
    run_trials()
