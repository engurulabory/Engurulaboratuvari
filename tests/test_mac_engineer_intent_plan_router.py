#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER_PATH = ROOT / "tools/mac_engineer_intent_plan_router.py"
CONTRACT_PATH = ROOT / "governance/mac-engineer/INTENT_EXECUTION_PLAN_ROUTER_V1.json"

spec = importlib.util.spec_from_file_location("router_mod", ROUTER_PATH)
router = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(router)

results = []

def check(name, condition):
    results.append((name, bool(condition)))

a = router.route("mevcut ürünü güncelle")
b = router.route("mevcut ürünü güncelle")
check(
    "DETERMINISTIC_SAME_INTENT_SAME_TRUTH",
    a["STATE"] == "PLAN_READY"
    and a["PLAN_ID"] == b["PLAN_ID"]
    and a["TRUTH_FINGERPRINT"] == b["TRUTH_FINGERPRINT"]
    and a["CAPABILITY_PLAN"] == b["CAPABILITY_PLAN"]
)

u = router.route("mars yüzeyinde kahve pişir")
check(
    "UNSUPPORTED_INTENT_HOLD",
    u["STATE"] == "HOLD"
    and u["HOLD_REASON"] == "UNSUPPORTED_INTENT"
    and u["EXECUTION_AUTHORIZED"] is False
)

empty = router.route("   ")
check(
    "EMPTY_INTENT_HOLD",
    empty["STATE"] == "HOLD"
    and empty["HOLD_REASON"] == "EMPTY_INTENT"
)

amb = router.route("araştırma yap ve mevcut ürünü güncelle")
check(
    "AMBIGUOUS_INTENT_HOLD",
    amb["STATE"] == "HOLD"
    and amb["HOLD_REASON"] == "AMBIGUOUS_INTENT_CLASS"
    and len(amb.get("MATCHED_INTENT_CLASSES", [])) >= 2
)

release = router.route("ürünü yayınla")
check(
    "RED_PLAN_HT_PROJECTED",
    release["STATE"] == "PLAN_READY"
    and release["REQUIRES_HUMAN_THRESHOLD"] is True
    and release["MAX_AUTHORITY"] == "RED"
    and release["EXECUTION_AUTHORIZED"] is False
)

research = router.route("araştırma yap")
check(
    "RESEARCH_MINIMUM_PLAN",
    research["STATE"] == "PLAN_READY"
    and research["CAPABILITY_PLAN"] == ["INTERNET_RESEARCH_HARVEST_ASTRA"]
)

new_product = router.route("brief ile yeni ürün")
check(
    "NEW_PRODUCT_GRAPH_PLAN",
    new_product["STATE"] == "PLAN_READY"
    and new_product["CAPABILITY_PLAN"] == [
        "NEW_PRODUCT_FROM_BRIEF",
        "INTERNET_RESEARCH_HARVEST_ASTRA",
        "ADVANCED_CODE_ENGINEERING",
        "BUILD",
        "TEST_REGRESSION",
        "EVIDENCE_DONECHECK",
    ]
)

check(
    "PLAN_EVIDENCE_PRESENT",
    a["EVIDENCE"]["planValidated"] is True
    and a["EVIDENCE"]["authorityResolved"] is True
    and a["EVIDENCE"]["executionAuthorized"] is False
)

original_contract = router.CONTRACT
with tempfile.TemporaryDirectory() as td:
    mutated = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    target = next(x for x in mutated["intentClasses"] if x["INTENT_CLASS"] == "EXISTING_PRODUCT_CHANGE")
    target["PLAN"][1] = "INVENTED_CAPABILITY"
    p = Path(td) / "contract.json"
    p.write_text(json.dumps(mutated, ensure_ascii=False), encoding="utf-8")
    router.CONTRACT = p
    invented = router.route("mevcut ürünü güncelle")
    check(
        "INVENTED_CAPABILITY_FAIL_CLOSED",
        invented["STATE"] == "HOLD"
        and invented["HOLD_REASON"] == "UNKNOWN_CAPABILITY"
    )
router.CONTRACT = original_contract

passed = sum(1 for _, ok in results if ok)
for name, ok in results:
    print(f"{name}={'PASS' if ok else 'HOLD'}")
print(f"TESTS={passed}_OF_{len(results)}_PASS")

if passed != len(results):
    print("STATE=HOLD")
    print("CLAIM=PACKAGE04_NATIVE_ROUTER_REGRESSION_HOLD")
    raise SystemExit(20)

print("STATE=PASS")
print("CLAIM=PACKAGE04_NATIVE_ROUTER_REGRESSION_PASS")
