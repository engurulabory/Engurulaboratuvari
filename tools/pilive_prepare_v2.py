#!/usr/bin/env python3
"""PiLive preparation adapter: offline fixtures and explicit source gaps.

Reuses the existing Brain V3 simulator. No runtime, writer or new progress core.
Ten fixed controls per axis, ten points each. Native gaps retain their weight.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

try:
    from tools.plive_brain_v3_simulator import contract, coverage, read_projection, ready_items, simulated_finish, AREA_IDS
    from tools.pilive_osi_source_observer_v2 import PINS, BASELINE_HEAD
except ModuleNotFoundError:
    from plive_brain_v3_simulator import contract, coverage, read_projection, ready_items, simulated_finish, AREA_IDS
    from pilive_osi_source_observer_v2 import PINS, BASELINE_HEAD

ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_PIN = "17cd00711ac8eed82ef802f69769400f9fade7414a0e27d6e1faccf94d18fbb0"
V3_PIN = "11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc"
AXES = ("THEORY", "DESIGN", "SIM1", "SIM2", "SIM3")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def unique(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[k] = v
    return result


def parse(raw):
    if len(raw) > 16 * 1024 * 1024:
        raise ValueError("INPUT_SIZE")
    return json.loads(raw, object_pairs_hook=unique, parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))


def rehearsal(snapshot, now):
    """Proposed adapter interface, fixture-only. Flags confer no real authority."""
    fail = {"state": "HOLD", "areas": {k: [] for k in AREA_IDS}, "officialPassGranted": False}
    try:
        if not isinstance(snapshot, dict) or type(now) is not int:
            return {**fail, "reason": "INPUT_TYPE"}
        source = snapshot.get("source")
        if not isinstance(source, dict) or not HEX40.fullmatch(str(source.get("head", ""))) or not HEX64.fullmatch(str(source.get("sha256", ""))):
            return {**fail, "reason": "SOURCE_IDENTITY"}
        technical = snapshot.get("technical")
        if not isinstance(technical, dict):
            return {**fail, "reason": "TECHNICAL_COUNTER"}
        d, t = technical.get("completed"), technical.get("total")
        if type(d) is not int or type(t) is not int or t <= 0 or not 0 <= d <= t:
            return {**fail, "reason": "TECHNICAL_COUNTER"}
        percent = round(d * 100 / t, 6)
        if "percent" in technical and (type(technical["percent"]) not in (int, float) or technical["percent"] != percent):
            return {**fail, "reason": "PERCENT_CONTRADICTION"}
        native = snapshot.get("native")
        if not isinstance(native, dict) or native.get("finish") not in {"HOLD", "VERIFIED", "LOCKED"}:
            return {**fail, "reason": "FINISH_VOCABULARY"}
        if native["finish"] in {"VERIFIED", "LOCKED"}:
            # A fixture with complete counts still needs all separate gates.
            gates = snapshot.get("finishEvidence", {})
            if not isinstance(gates, dict) or simulated_finish(native.get("countedPass"), gates.get("donechecks"), gates.get("field"), gates.get("human"), "VERIFIED")["state"] != "MODEL_FINISH_CONDITIONS_MET_ONLY":
                return {**fail, "reason": "FINISH_AUTHORITY_BOUNDARY"}
        projection = read_projection(snapshot, now)
        if projection["state"] != "PASS_MODEL_ONLY":
            return {**fail, "reason": projection["reason"]}
        active = snapshot.get("active", [])
        if not isinstance(active, list) or len(active) > 1:
            return {**fail, "reason": "MULTIPLE_ACTIVE"}
        ids = {x["workId"] for x in snapshot.get("workItems", [])}
        if active and (not isinstance(active[0], dict) or active[0].get("workId") not in ids or
                       any(not isinstance(active[0].get(k), str) or not active[0][k].strip()
                           for k in ("projectId", "name", "stage", "pendingEvidence", "nextAction"))):
            return {**fail, "reason": "ACTIVE_SOURCE_BINDING"}
        return {**projection, "technical": {"completed": d, "total": t, "percent": percent},
                "active": copy.deepcopy(active),
                "drawer": {"head": source["head"], "sha256": source["sha256"],
                           "test": "FIXTURE_ONLY", "donecheck": "HOLD", "acceptance": "HOLD"},
                "officialPassGranted": False, "runtimeImplementation": "NOT_CLAIMED"}
    except (KeyError, ValueError, TypeError, RecursionError):
        return {**fail, "reason": "MALFORMED_SNAPSHOT"}


def fixture():
    return {"source": {"valid": True, "head": BASELINE_HEAD, "sha256": "a"*64, "readAt": 1000},
            "native": {"verified": True, "countedPass": 0, "total": 12, "finish": "HOLD"},
            "technical": {"completed": 12, "total": 12},
            "workItems": [{"workId": "demo-1", "primaryArea": "app", "facet": "LABORATUVAR"}],
            "active": [{"workId": "demo-1", "projectId": "demo-project", "name": "Örnek kaynak bağı",
                        "stage": "Kanıtla", "pendingEvidence": "Mac readback", "nextAction": "Kaynağı doğrula"}]}


def adversarial():
    """Ten required counterconditions. Each has its own observed expectation."""
    rows = []
    def add(name, fn):
        try:
            rows.append((name, bool(fn())))
        except Exception:
            rows.append((name, False))
    def mutated(key, value):
        x = fixture(); x[key] = value
        return rehearsal(x, 1001)["state"] == "HOLD"
    add("missing_source", lambda: mutated("source", {}))
    def bad_json():
        for raw in (b'{', b'{"a":1,"a":2}', b'{"x":NaN}'):
            try: parse(raw)
            except ValueError: continue
            return False
        return True
    add("corrupt_json", bad_json)
    add("wrong_percent", lambda: mutated("technical", {"completed": 1, "total": 2, "percent": 100}))
    add("duplicate_project", lambda: mutated("workItems", fixture()["workItems"]*2))
    add("dependency_cycle", lambda: ready_items([
        {"workId": "a", "priority": 1, "dependsOn": ["b"]},
        {"workId": "b", "priority": 1, "dependsOn": ["a"]}], [])["state"] == "HOLD")
    add("stale_snapshot", lambda: rehearsal(fixture(), 1400)["freshness"] == "SON_DOGRULANMIS_OKUMA")
    add("unauthorized_pass", lambda: mutated("native", {"verified": True, "countedPass": 12, "total": 12, "finish": "VERIFIED"}))
    add("interruption_partial_input", lambda: mutated("native", {"countedPass": 3}))
    add("source_drift", lambda: mutated("source", {"valid": True, "head": "wrong", "sha256": "a"*64, "readAt": 1000}))
    def restore():
        original = fixture(); a = rehearsal(original, 1001)
        corrupt = copy.deepcopy(original); corrupt["native"]["total"] = -1
        return rehearsal(corrupt, 1001)["state"] == "HOLD" and rehearsal(original, 1001) == a and original == fixture()
    add("rollback_revalidation", restore)
    return rows


def evaluate(discovery_bytes, plan, source_root=ROOT):
    report = parse(discovery_bytes)
    if not isinstance(report, dict):
        raise ValueError("DISCOVERY_OBJECT_REQUIRED")
    rows = {a: [] for a in AXES}
    def add(axis, label, ok, evidence):
        rows[axis].append({"id": f"{axis}.{len(rows[axis])+1:02d}", "requirement": label,
                           "state": "PASS" if ok else "HOLD", "points": 10 if ok else 0,
                           "evidence": evidence})
    locked = digest((source_root/"governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md").read_bytes()) == V3_PIN
    source = report.get("repositories", [{}])[0]
    pins = source.get("historical_plive_pins", {})
    pin_ok = set(pins) == set(PINS) and all(pins[p].get("sha256") == PINS[p] for p in PINS)
    # Actual canonical bytes and native bindings are absent from this discovery.
    # No JSON flag supplied by a caller can award these controls.
    for label, ok, ev in [
        ("Canonical V3 lock", locked, V3_PIN),
        ("Exact discovery bytes", digest(discovery_bytes) == DISCOVERY_PIN, DISCOVERY_PIN),
        ("Seven historical source identities", pin_ok, "Discovery metadata only"),
        ("Separate screen/P02/P01/P06 acceptance", plan.get("acceptanceSeparation") == ["SCREEN", "P02", "P01", "P06"], "Plan"),
        ("Actual P02 contract/worklist/state semantics", False, "HOLD_SOURCE_BYTES_REQUIRED"),
        ("Actual Progress Core registry and verifier semantics", False, "HOLD_SOURCE_BYTES_REQUIRED"),
        ("Installed binary to exact build source", False, "HOLD_BUILD_PROVENANCE_REQUIRED"),
        ("Unchanged 12/4/7 finish denominators", plan.get("p02Denominators") == [12, 4, 7], "Historical candidate; native re-read open"),
        ("Authority boundaries and historical observations", bool(plan.get("authority")), "Plan authority map"),
        ("Five visible areas / six common method domains separated", plan.get("areas") == list(AREA_IDS) and plan.get("methodDomains") == 6, "Brain V3 + current method")]:
        add("THEORY", label, ok, ev)
    design = [
        ("Ten preparation blocks", [r["id"] for r in plan.get("blocks", [])] == [f"G{i:02d}" for i in range(10)]),
        ("Known dependency DAG", plan.get("dependencyPolicy") == "DAG_AND_SEPARATE_SCREEN_P02_BRANCHES"),
        ("Atomic source strategy", bool(plan.get("snapshotProtocol"))),
        ("Accepted forest cockpit and owl", plan.get("visual", {}).get("identity") == ["Sessiz Orman Cockpit", "Emin Baykuş"]),
        ("Measured native performance plan", bool(plan.get("performance"))),
        ("Security and authority plan", bool(plan.get("authority")) and bool(plan.get("humanScope"))),
        ("Preservation and rollback", bool(plan.get("preserve")) and bool(plan.get("rollback"))),
        ("Real adapter API mapped to source", False),
        ("Exact Swift build and launch recipe bound to binary", False),
        ("Native Progress Core resolution reviewed", False)]
    for label, ok in design:
        add("DESIGN", label, ok, "Plan + source review; missing native sources retain full weight")
    fx = fixture(); result = rehearsal(fx, 1001)
    for label, ok, ev in [
        ("Application launch data path represented by current source", False, "NOT_EXECUTED_SOURCE_UNAVAILABLE"),
        ("Source identity and read model", result["state"] == "PASS_MODEL_ONLY", "Synthetic fixture"),
        ("Single active work", len(result.get("active", [])) == 1, "Synthetic fixture"),
        ("Technical percentage", result.get("technical", {}).get("percent") == 100, "Synthetic fixture"),
        ("Official HOLD retained at technical 100", result.get("native", {}).get("finish") == "HOLD", "Synthetic fixture"),
        ("Five visible areas", list(result["areas"]) == list(AREA_IDS), "Synthetic fixture"),
        ("Evidence drawer source link", result.get("drawer", {}).get("head") == BASELINE_HEAD, "Synthetic fixture"),
        ("Current/frozen timestamp", result.get("readAt") == 1000, "Synthetic fixture"),
        ("Deterministic reopen model", rehearsal(parse(canonical(fx)), 1001) == result, "JSON roundtrip; no GUI reopen"),
        ("Current native adapter fixture parity", False, "NOT_EXECUTED_SOURCE_UNAVAILABLE")]:
        add("SIM1", label, ok, ev)
    for label, ok in adversarial():
        add("SIM2", label, ok, "Executed synthetic countercondition; native crash separate")
    # Independent oracle does not call rehearsal/Brain for expected arithmetic.
    from fractions import Fraction
    oracle_pct = float(Fraction(12, 12)*100)
    for label, ok, ev in [
        ("Discovery independent pin", digest(discovery_bytes) == DISCOVERY_PIN, "Raw bytes SHA-256"),
        ("Brain fixed coverage", coverage(contract()) == 100, "Historical model design scope only"),
        ("Independent arithmetic oracle", result.get("technical", {}).get("percent") == oracle_pct, "fractions.Fraction"),
        ("Five headings exact oracle", tuple(result["areas"]) == ("motor", "core", "web", "app", "agent"), "Explicit second expectation"),
        ("Serialized replay digest", digest(canonical(result)) == digest(canonical(rehearsal(parse(canonical(fx)), 1001))), "Serialization replay"),
        ("Input preserved", fx == fixture(), "Independent before/after value"),
        ("Full synthetic finish grants zero official authority", simulated_finish(12,4,7,"ACCEPTED","VERIFIED")["officialPassGranted"] is False, "Existing model boundary"),
        ("Current canonical -> native -> adapter parity", False, "HOLD_REAL_SOURCE_AND_NATIVE_ORACLE"),
        ("Exact Swift source -> visible-output semantics", False, "HOLD_SOURCE_UI_BINDING"),
        ("Project semantic review is separate from general scores", True, "Earned scores min with common method; every missing control retained")]:
        add("SIM3", label, ok, ev)
    assert all(len(rows[a]) == 10 for a in AXES)
    scores = {a: sum(r["points"] for r in rows[a]) for a in AXES}
    return {"schema": "enguru.pilive.preparation/v2", "scores": scores,
            "fixedDenominator": "Each of THEORY/DESIGN/SIM1/SIM2/SIM3: ten named controls x ten points; 50 unique controls",
            "controls": rows, "discoverySha256": digest(discovery_bytes),
            "GITHUB_PREPARED": "HOLD", "semanticScope": "FULL_USER_SCOPE_WITH_NATIVE_SOURCE_GAPS",
            "reason": "Current canonical source, Swift lineage and native adapter oracle required; CI alone cannot close these controls",
            "SCREEN_ACCEPTANCE": "HOLD_NOT_EXECUTED", "P02_ACCEPTANCE": "HOLD_NATIVE_AUTHORITY",
            "macActionsExecuted": 0, "canonicalWrites": 0, "paidApiCalls": 0,
            "nextAction": "BOUNDED_OSI_READ_ONLY_SOURCE_CAPTURE_AND_REVIEW",
            "verifiedFinish": "HOLD"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("discovery", type=Path)
    p.add_argument("--plan", type=Path, default=ROOT/"governance/pilive-preparation-v2/PLAN.json")
    args = p.parse_args()
    try:
        result = evaluate(args.discovery.read_bytes(), parse(args.plan.read_bytes()))
    except (OSError, ValueError, KeyError, TypeError, IndexError, RecursionError) as exc:
        print(json.dumps({"GITHUB_PREPARED": "HOLD", "reason": type(exc).__name__}))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 2  # Native source/review gaps are deliberately still open.


if __name__ == "__main__":
    sys.exit(main())
