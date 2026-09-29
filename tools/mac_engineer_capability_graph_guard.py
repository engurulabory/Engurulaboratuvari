#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


ALLOWED_ROLES = {
    "CONTROL_PLANE",
    "CONTROL_PLANE_GUARD",
    "WORKFLOW",
    "CONTROLLED_REPAIR",
    "CONTROLLED_RECOVERY",
    "EXECUTION_SUBSTRATE",
    "RED_WORKFLOW",
}

REQUIRED_LOOPS = {
    "BOUNDED_REPAIR_REVERIFY",
    "RECOVERY_RETURN_TO_TRUTH",
    "POST_DELIVERY_REVERIFY",
}


def fail(reason: str, code: int = 20) -> int:
    print("STATE=HOLD")
    print(f"REASON={reason}")
    return code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--graph",
        default="governance/mac-engineer/CAPABILITY_DEPENDENCY_GRAPH_V1.json",
    )
    parser.add_argument(
        "--registry",
        default="governance/mac-engineer/CAPABILITY_REGISTRY_V1.json",
    )
    args = parser.parse_args()

    graph_path = Path(args.graph)
    registry_path = Path(args.registry)

    if not graph_path.is_file():
        return fail("GRAPH_MISSING")
    if not registry_path.is_file():
        return fail("REGISTRY_MISSING")

    try:
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return fail("JSON_PARSE_ERROR")

    reg_nodes = {
        c.get("CAPABILITY_ID"): c
        for c in registry.get("capabilities", [])
        if isinstance(c, dict) and c.get("CAPABILITY_ID")
    }
    nodes_list = graph.get("nodes", [])
    nodes = {
        n.get("CAPABILITY_ID"): n
        for n in nodes_list
        if isinstance(n, dict) and n.get("CAPABILITY_ID")
    }

    if len(reg_nodes) != 19 or len(nodes) != 19:
        return fail("NODE_COUNT_MISMATCH")

    if set(nodes) != set(reg_nodes):
        return fail("REGISTRY_GRAPH_PARITY_MISMATCH")

    if len(nodes_list) != len(nodes):
        return fail("DUPLICATE_GRAPH_NODE")

    missing_role = [
        cid for cid, node in nodes.items()
        if node.get("NODE_ROLE") not in ALLOWED_ROLES
    ]
    if missing_role:
        return fail("UNKNOWN_OR_MISSING_NODE_ROLE")

    for cid, node in nodes.items():
        reg = reg_nodes[cid]
        if node.get("AUTHORITY") != reg.get("AUTHORITY"):
            return fail("AUTHORITY_PARITY_MISMATCH")
        if node.get("RISK_CLASS") != reg.get("RISK_CLASS"):
            return fail("RISK_PARITY_MISMATCH")
        if node.get("REQUIRES_HUMAN_THRESHOLD") != reg.get("REQUIRES_HUMAN_THRESHOLD"):
            return fail("HUMAN_THRESHOLD_PARITY_MISMATCH")

    edges = graph.get("forwardEdges", [])
    pairs = []
    duplicate_edge_count = 0
    seen = set()

    for edge in edges:
        if not isinstance(edge, dict):
            return fail("INVALID_EDGE_SHAPE")
        src = edge.get("FROM")
        dst = edge.get("TO")
        if src not in nodes or dst not in nodes:
            return fail("UNKNOWN_EDGE_NODE")
        if src == dst:
            return fail("SELF_EDGE")
        pair = (src, dst)
        if pair in seen:
            duplicate_edge_count += 1
        seen.add(pair)
        pairs.append(pair)

        if edge.get("FAIL_CLOSED") is not True:
            return fail("EDGE_NOT_FAIL_CLOSED")

        expected_ht = nodes[dst].get("AUTHORITY") == "RED"
        if edge.get("REQUIRES_HUMAN_THRESHOLD") is not expected_ht:
            return fail("RED_EDGE_HUMAN_THRESHOLD_MISMATCH")

    if duplicate_edge_count:
        return fail("DUPLICATE_FORWARD_EDGE")

    substrates = {"TERMINAL_EXECUTION", "FILESYSTEM_MACOS_AUTOMATION"}
    if any(src in substrates for src, _ in pairs):
        return fail("SUBSTRATE_TRANSITION_AUTHORITY")

    if ("EVIDENCE_DONECHECK", "RELEASE_LIFECYCLE") in seen:
        return fail("AMBIGUOUS_RELEASE_REENTRY_EDGE")

    adj = defaultdict(list)
    for src, dst in pairs:
        adj[src].append(dst)

    visiting = set()
    visited = set()

    def dfs(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for nxt in adj[node]:
            if dfs(nxt):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    if any(dfs(node) for node in nodes):
        return fail("UNSAFE_FORWARD_CYCLE")

    boundary = graph.get("authorityBoundary", {})
    if boundary.get("intentRoutingPreauthorized") is not False:
        return fail("PACKAGE04_INTENT_ROUTING_PREAUTHORIZED")
    if boundary.get("unlistedTransitionPolicy") != "HOLD":
        return fail("UNLISTED_TRANSITION_NOT_HOLD")
    if boundary.get("redCapabilityBypassAllowed") is not False:
        return fail("RED_BYPASS_ALLOWED")
    if boundary.get("substrateNodesGrantTransitionAuthority") is not False:
        return fail("SUBSTRATE_AUTHORITY_ENABLED")
    if boundary.get("releaseEntryPolicy") != "PACKAGE04_ROUTER_PLUS_RED_AUTHORITY_REQUIRED":
        return fail("RELEASE_ENTRY_POLICY_INVALID")

    loops = graph.get("controlledLoops", [])
    loop_ids = set()
    for loop in loops:
        if not isinstance(loop, dict):
            return fail("INVALID_LOOP_SHAPE")
        loop_id = loop.get("LOOP_ID")
        if not loop_id or loop_id in loop_ids:
            return fail("DUPLICATE_OR_MISSING_LOOP_ID")
        loop_ids.add(loop_id)

        path = loop.get("PATH")
        if not isinstance(path, list) or len(path) < 2:
            return fail("INVALID_LOOP_PATH")
        if any(node not in nodes for node in path):
            return fail("UNKNOWN_LOOP_NODE")
        if loop.get("MAX_ATTEMPTS") not in (1, 2):
            return fail("UNBOUNDED_LOOP")
        if loop.get("OVER_LIMIT") != "HOLD":
            return fail("LOOP_OVER_LIMIT_NOT_HOLD")
        if loop.get("REQUIRES_FRESH_EVIDENCE") is not True:
            return fail("LOOP_FRESH_EVIDENCE_NOT_REQUIRED")

    if loop_ids != REQUIRED_LOOPS:
        return fail("CONTROLLED_LOOP_SET_MISMATCH")

    expected_paths = {
        "BOUNDED_REPAIR_REVERIFY": [
            "TEST_REGRESSION",
            "ROOT_CAUSE_REPAIR",
            "TEST_REGRESSION",
        ],
        "RECOVERY_RETURN_TO_TRUTH": [
            "RECOVERY_OFFLINE_CONTINUITY",
            "CURRENT_TECHNICAL_TRUTH_READ",
        ],
        "POST_DELIVERY_REVERIFY": [
            "FINISHED_PRODUCT_DELIVERY_ACCEPTANCE",
            "EVIDENCE_DONECHECK",
        ],
    }
    for loop in loops:
        if loop.get("PATH") != expected_paths[loop["LOOP_ID"]]:
            return fail("CONTROLLED_LOOP_PATH_MISMATCH")

    red_nodes = [cid for cid, n in nodes.items() if n.get("AUTHORITY") == "RED"]
    red_bypass = [
        cid for cid in red_nodes
        if nodes[cid].get("REQUIRES_HUMAN_THRESHOLD") is not True
    ]
    if red_bypass:
        return fail("RED_CAPABILITY_BYPASS")

    print("STATE=PASS")
    print("CLAIM=CAPABILITY_DEPENDENCY_GRAPH_NATIVE_GUARD_PASS")
    print("NODE_COUNT=19")
    print("REGISTRY_PARITY=19_OF_19")
    print(f"FORWARD_EDGE_COUNT={len(edges)}")
    print("UNKNOWN_NODE_COUNT=0")
    print("UNKNOWN_EDGE_COUNT=0")
    print("SELF_EDGE_COUNT=0")
    print("UNSAFE_CYCLE_COUNT=0")
    print("RED_BYPASS_COUNT=0")
    print("NODE_ROLE_MISSING_COUNT=0")
    print("SUBSTRATE_TRANSITION_AUTHORITY_COUNT=0")
    print("CONTROLLED_LOOP_COUNT=3")
    print("CONTROLLED_LOOP_POLICY_VIOLATION_COUNT=0")
    print("REPAIR_LOOP_BOUNDED=PASS")
    print("RECOVERY_RETURN_PATH=PASS")
    print("POST_DELIVERY_REVERIFY=PASS")
    print("PACKAGE04_INTENT_ROUTING_PREAUTHORIZED=FALSE")
    print("UNLISTED_TRANSITION_POLICY=HOLD")
    print("GRAPH_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
