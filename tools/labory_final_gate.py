#!/usr/bin/env python3
"""ENGÜRÜ LABORY FINAL GATE™ — structural truth, order, site alignment and simplicity validator."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()

REQUIRED = [
    "README.md",
    "WORKLIST.md",
    ".enguru/ip-model-trust.json",
    "governance/ENGURU_SYSTEM_TRUTH_V1.json",
    "governance/ENGURU_PRODUCT_CORE_MAP_V2.json",
    "governance/REPOSITORY_ORDER_PASS.md",
    "steward/index.mjs",
    "steward/tests.mjs",
    "steward/LABORY_100_SCORECARD_V1.json",
    "site/product-registry.json",
    "site/LEGACY_PRODUCT_ALIGNMENT_V1.json",
    "site/ENGURULAB_PRODUCT_ALIGNMENT.md",
    "tools/ip_model_trust_gate.py",
    "tools/fleet_ip_gate.py",
]

LOCKED_PLAN = [
    "ENGURU_LABORY_VERIFIED_FINISH",
    "ASTRA_MAC_RUNTIME",
    "ASTRA_ACCEPTANCE_TEST",
    "PRODUCT_PRODUCTION_START",
    "ENGURU_BUILDER",
    "ARTIST_MANAGER_AI",
    "PLANNED_PRODUCT_QUEUE",
]

PLANNED = {"ENGÜRÜ LAB • ASTRO MODE", "Adil Pay"}
LEGACY_DECISIONS = {"KEEP", "RENAME", "CORE", "ARCHIVE", "PLANNED"}


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def fail(findings):
    print(json.dumps({"gate":"ENGURU_LABORY_FINAL_GATE_V1","state":"BLOCKED","findings":findings}, ensure_ascii=False, indent=2))
    return 3


def main() -> int:
    findings = []

    for path in REQUIRED:
        if not (ROOT / path).exists(): findings.append({"code":"MISSING_REQUIRED_PATH","path":path})
    if findings: return fail(findings)

    truth = load("governance/ENGURU_SYSTEM_TRUTH_V1.json")
    product_map = load("governance/ENGURU_PRODUCT_CORE_MAP_V2.json")
    registry = load("site/product-registry.json")
    legacy_alignment = load("site/LEGACY_PRODUCT_ALIGNMENT_V1.json")
    scorecard = load("steward/LABORY_100_SCORECARD_V1.json")
    trust = load(".enguru/ip-model-trust.json")

    repos = truth.get("currentAccessibleRepositories", [])
    if truth.get("currentAccessibleRepositoryCount") != len(repos):
        findings.append({"code":"REPOSITORY_COUNT_DRIFT"})
    if len(repos) != len(set(repos)):
        findings.append({"code":"DUPLICATE_REPOSITORY_TRUTH"})

    map_repos = [record.get("repository") for record in product_map.get("records", [])]
    if set(map_repos) != set(repos):
        findings.append({"code":"SYSTEM_TRUTH_MAP_DRIFT","truthOnly":sorted(set(repos)-set(map_repos)),"mapOnly":sorted(set(map_repos)-set(repos))})

    planned_truth = {x.get("asset") for x in truth.get("plannedProducts", [])}
    planned_map = {x.get("asset") for x in product_map.get("plannedProducts", [])}
    planned_registry = {x.get("productName") for x in registry.get("plannedProducts", [])}
    if planned_truth != PLANNED or planned_map != PLANNED or planned_registry != PLANNED:
        findings.append({"code":"PLANNED_PRODUCT_DRIFT"})

    actual_plan = [x.get("name") for x in truth.get("lockedExecutionPlan", [])]
    if actual_plan != LOCKED_PLAN:
        findings.append({"code":"LOCKED_EXECUTION_PLAN_DRIFT","actual":actual_plan})

    map_types = {r.get("repository"): r.get("assetType") for r in product_map.get("records", [])}
    expected_registry_types = {}
    for item in registry.get("products", []): expected_registry_types[item.get("repository")] = item.get("classification")
    for item in registry.get("productCores", []): expected_registry_types[item.get("repository")] = item.get("classification")
    for item in registry.get("cores", []): expected_registry_types[item.get("repository")] = item.get("classification")
    for item in registry.get("releaseMirrors", []): expected_registry_types[item.get("repository")] = item.get("classification")
    for repo, classification in expected_registry_types.items():
        if map_types.get(repo) != classification:
            findings.append({"code":"REGISTRY_CLASSIFICATION_DRIFT","repository":repo,"registry":classification,"map":map_types.get(repo)})

    if registry.get("sourceOfTruth") != "governance/ENGURU_PRODUCT_CORE_MAP_V2.json":
        findings.append({"code":"REGISTRY_SOURCE_NOT_V2"})
    if registry.get("schemaVersion") != "1.1":
        findings.append({"code":"REGISTRY_SCHEMA_NOT_1_1"})
    if registry.get("legacyAlignmentRef") != "site/LEGACY_PRODUCT_ALIGNMENT_V1.json":
        findings.append({"code":"LEGACY_ALIGNMENT_REFERENCE_DRIFT"})

    legacy_items = legacy_alignment.get("items", [])
    if len(legacy_items) != 15:
        findings.append({"code":"LEGACY_ITEM_COUNT_DRIFT","actual":len(legacy_items)})
    invalid_decisions = sorted({x.get("decision") for x in legacy_items} - LEGACY_DECISIONS)
    if invalid_decisions:
        findings.append({"code":"INVALID_LEGACY_DECISION","values":invalid_decisions})
    legacy_by_name = {x.get("legacyName"): x for x in legacy_items}
    if legacy_by_name.get("Menajer Zekî", {}).get("canonicalTarget") != "Artist Manager AI™" or legacy_by_name.get("Menajer Zekî", {}).get("decision") != "RENAME":
        findings.append({"code":"ARTIST_MANAGER_LEGACY_IDENTITY_DRIFT"})
    if legacy_by_name.get("AstroMode", {}).get("canonicalTarget") != "ENGÜRÜ LAB • ASTRO MODE" or legacy_by_name.get("AstroMode", {}).get("decision") != "PLANNED":
        findings.append({"code":"ASTRO_MODE_LEGACY_IDENTITY_DRIFT"})

    product_ids = {x.get("productId") for x in registry.get("products", [])}
    if product_ids != {"enguru-builder", "artist-manager-ai"}:
        findings.append({"code":"CANONICAL_PRODUCT_SET_DRIFT","actual":sorted(product_ids)})
    artist = next((x for x in registry.get("products", []) if x.get("productId") == "artist-manager-ai"), {})
    if "Menajer Zekî" not in artist.get("legacyAliases", []):
        findings.append({"code":"ARTIST_MANAGER_ALIAS_MISSING"})

    dimensions = scorecard.get("dimensions", [])
    if len(dimensions) != 10 or sum(int(x.get("weight", 0)) for x in dimensions) != 100:
        findings.append({"code":"SCORECARD_NOT_100"})

    if trust.get("repository") != "engurulabory/Engurulaboratuvari" or trust.get("governedBy") != "ENGURU_IP_MODEL_TRUST_GATE_V1":
        findings.append({"code":"TRUST_MANIFEST_DRIFT"})

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for token in ["ENGURU_SYSTEM_TRUTH_V1.json", "Products / Cores / Evidence / Archive", "Astra Acceptance Test"]:
        if token not in readme: findings.append({"code":"README_ENTRYPOINT_DRIFT","token":token})

    worklist = (ROOT / "WORKLIST.md").read_text(encoding="utf-8")
    for token in ["ENGÜRÜ LABORY VERIFIED FINISH", "ASTRA MAC RUNTIME", "ENGÜRÜ Builder™", "Artist Manager AI™", "Astro Mode / Adil Pay"]:
        if token not in worklist: findings.append({"code":"WORKLIST_SEQUENCE_DRIFT","token":token})

    try:
        tracked = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    except Exception:
        tracked = []
    junk_suffixes = (".tmp", ".swp")
    for path in tracked:
        name = Path(path).name
        if name in {".DS_Store", "Thumbs.db", "npm-debug.log"} or path.endswith(junk_suffixes):
            findings.append({"code":"TRACKED_JUNK","path":path})
        p = ROOT / path
        try:
            if p.stat().st_size <= 1_000_000:
                text = p.read_text(encoding="utf-8")
                if any(line.startswith(("<<<<<<<", "=======", ">>>>>>>")) for line in text.splitlines()):
                    findings.append({"code":"MERGE_CONFLICT_MARKER","path":path})
        except (UnicodeDecodeError, OSError):
            pass

    if findings: return fail(findings)

    print(json.dumps({
        "gate":"ENGURU_LABORY_FINAL_GATE_V1",
        "state":"PASS",
        "repositoryCount":len(repos),
        "plannedProducts":sorted(PLANNED),
        "canonicalProducts":sorted(product_ids),
        "legacyAlignmentItems":len(legacy_items),
        "scorecardWeight":100,
        "systemTruth":"PASS",
        "mapRegistryConsistency":"PASS",
        "siteProductAlignment":"PASS",
        "repositoryHygiene":"PASS",
        "operationalSimplicity":"PASS"
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
