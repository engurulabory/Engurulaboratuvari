#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "governance/mac-engineer/CAPABILITY_DEPENDENCY_GRAPH_V1.json"
REGISTRY = ROOT / "governance/mac-engineer/CAPABILITY_REGISTRY_V1.json"
GUARD = ROOT / "tools/mac_engineer_capability_graph_guard.py"


def run_guard(graph: Path = GRAPH):
    return subprocess.run(
        [
            sys.executable,
            str(GUARD),
            "--graph",
            str(graph),
            "--registry",
            str(REGISTRY),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def variant(mutator):
    data = json.loads(GRAPH.read_text(encoding="utf-8"))
    mutator(data)
    td = tempfile.TemporaryDirectory()
    path = Path(td.name) / "graph.json"
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return td, path


results = []

p = run_guard()
results.append((
    "CANONICAL_GRAPH_PASS",
    p.returncode == 0
    and "STATE=PASS" in p.stdout
    and "GRAPH_VALIDATION=PASS" in p.stdout
    and "PACKAGE04_INTENT_ROUTING_PREAUTHORIZED=FALSE" in p.stdout,
))

td, path = variant(
    lambda d: d["forwardEdges"].append({
        "FROM": "EVIDENCE_DONECHECK",
        "TO": "BUILD",
        "FAIL_CLOSED": True,
        "REQUIRES_HUMAN_THRESHOLD": False,
    })
)
p = run_guard(path)
results.append((
    "FORWARD_CYCLE_FAIL_CLOSED",
    p.returncode != 0 and "UNSAFE_FORWARD_CYCLE" in p.stdout,
))
td.cleanup()

def red_mutation(d):
    for e in d["forwardEdges"]:
        if e["TO"] == "FINISHED_PRODUCT_DELIVERY_ACCEPTANCE":
            e["REQUIRES_HUMAN_THRESHOLD"] = False

td, path = variant(red_mutation)
p = run_guard(path)
results.append((
    "RED_EDGE_BYPASS_REJECTED",
    p.returncode != 0 and "RED_EDGE_HUMAN_THRESHOLD_MISMATCH" in p.stdout,
))
td.cleanup()

td, path = variant(
    lambda d: d["authorityBoundary"].__setitem__(
        "intentRoutingPreauthorized", True
    )
)
p = run_guard(path)
results.append((
    "PACKAGE04_PREAUTH_REJECTED",
    p.returncode != 0 and "PACKAGE04_INTENT_ROUTING_PREAUTHORIZED" in p.stdout,
))
td.cleanup()

def loop_mutation(d):
    d["controlledLoops"][0]["MAX_ATTEMPTS"] = 99

td, path = variant(loop_mutation)
p = run_guard(path)
results.append((
    "UNBOUNDED_LOOP_REJECTED",
    p.returncode != 0 and "UNBOUNDED_LOOP" in p.stdout,
))
td.cleanup()

td, path = variant(
    lambda d: d["forwardEdges"].append({
        "FROM": "TERMINAL_EXECUTION",
        "TO": "BUILD",
        "FAIL_CLOSED": True,
        "REQUIRES_HUMAN_THRESHOLD": False,
    })
)
p = run_guard(path)
results.append((
    "SUBSTRATE_AUTHORITY_REJECTED",
    p.returncode != 0 and "SUBSTRATE_TRANSITION_AUTHORITY" in p.stdout,
))
td.cleanup()

passed = sum(1 for _, ok in results if ok)
for name, ok in results:
    print(f"{name}={'PASS' if ok else 'HOLD'}")

print(f"TESTS={passed}_OF_{len(results)}_PASS")

if passed != len(results):
    print("STATE=HOLD")
    print("REASON=PACKAGE03_GRAPH_REGRESSION_FAILED")
    raise SystemExit(20)

print("STATE=PASS")
print("CLAIM=PACKAGE03_NATIVE_GRAPH_REGRESSION_PASS")
