# ENGÜRÜ PRODUCT & CORE MAP™

## State
HOLD — accessible repository inventory is now enumerated; embedded-core/dependency/evidence discovery remains open.

This map is the canonical inventory surface for Engürü Lab products, shared cores, governance layers, infrastructure, experiments and archives.

## Locked rule
No large repository move, delete, merge, rename or product retirement may occur before this map reaches PASS and consequential actions pass Human Threshold™.

## Classification
- PRODUCT — independent user-facing/sellable product
- CORE — reusable capability
- CORE_WORKER — non-product autonomous/semi-autonomous worker that operates across control-plane surfaces and product/core adapters
- PRODUCT_CORE — independent economic/operational product with reusable core role
- GOVERNANCE — authority, evidence, language or verification layer
- CONTROL_PLANE — Labory portfolio/governance coordination surface
- INFRASTRUCTURE — deployment, billing, auth, data or platform support
- RELEASE_MIRROR — release/distribution surface, not canonical product source
- EXPERIMENT — not yet promoted
- ARCHIVE — historical reference
- UNKNOWN_REVIEW — purpose/status not yet evidenced

## Accessible repository inventory — 2026-08-25
Canonical machine-readable source: `governance/repository-inventory.json`.

1. `engurulabory/Engurulaboratuvari` — CONTROL_PLANE — ACTIVE
2. `engurulabory/enguru-website-factory` — PRODUCT — ENGÜRÜ Builder™ — ACTIVE
3. `engurulabory/enguru-builder-release` — RELEASE_MIRROR — REVIEW
4. `engurulabory/donecheck` — PRODUCT — DoneCheck™ — ACTIVE
5. `engurulabory/donecheck-core-foundation` — CORE — ACTIVE
6. `engurulabory/shift-core-api` — PRODUCT_CORE — Shift Core™ — ACTIVE
7. `engurulabory/artist-manager-ai` — PRODUCT — ACTIVE
8. `engurulabory/autonomous-economic-core` — PRODUCT_CORE — AEC — ACTIVE
9. `engurulabory/adil-pay-kanit-web` — UNKNOWN_REVIEW — HOLD

## Core worker registration — 2026-09-07

### Repository Steward™
Classification: CORE_WORKER / CONTROL-PLANE WORKER
Canonical home: `engurulabory/Engurulaboratuvari/steward/`
Canonical contract: `steward/STEWARD_CORE_WORKER_CONTRACT_V1.md`
State: ACTIVE CORE WORKER / GOVERNANCE PLACEMENT LOCKED

Repository Steward™ is not a product and must not become product-owned runtime truth.

Operating surface:
`LAB HOME → PRODUCT REGISTRY → PRODUCT REPOSITORIES → SHARED CORES → EVIDENCE / DONECHECK → REPOSITORY HEALTH → WORKLIST → HUMAN THRESHOLD WHEN REQUIRED`

Steward may:
- inspect Labory home/control-plane state;
- traverse registered products and cores through manifests/adapters;
- compare canonical ownership, dependency, evidence, CI/test, security and lifecycle state;
- perform bounded, reversible maintenance when explicitly permitted;
- register drift, HOLD/BLOCKED states and next actions;
- return destructive or authority-changing actions to Human Threshold™.

Steward may not:
- become embedded as canonical product logic;
- silently mutate product behavior or product policy;
- archive/delete/rename/merge repositories;
- rewrite history;
- change visibility;
- delete protected branches;
- cut over production sources/deployments without Human Threshold™.

Product boundary rule: product repositories may contain only a Steward adapter, manifest, evidence hook or pointer. The canonical Steward runtime and governance contract remain in Labory.

## Shared core registration — 2026-08-30

### ENGÜRÜ CLOSED-LOOP PRODUCTION CORE™ v0.1
Classification: CORE / GOVERNANCE-RUNTIME BRIDGE
Canonical specification: `governance/ENGURU_CLOSED_LOOP_PRODUCTION_CORE_V0_1.md`
State: DESIGN LOCKED / IMPLEMENTATION HOLD

Purpose:
`INTENT → TASK CONTRACT → SUCCESS CRITERIA → EXECUTE → OBSERVE → COLLECT EVIDENCE → VERIFY → CORRECT/RETRY → DONECHECK™ → HUMAN THRESHOLD™ WHEN REQUIRED → VERIFIED FINISH`

Initial consumers:
- ENGÜRÜ Builder™ — adapter target;
- Autonomous Economic Core™ — adapter target;
- ENGÜRÜ Lab / Repository Steward™ — canonical control-plane consumer;
- ENGÜRÜ Verified Business OS™ — future consumer after multi-surface proof.

Ownership rule: Labory owns the shared contract; product repositories keep domain logic, product-local evidence and observation adapters. No product logic move/delete is authorized by this registration.

## Control-plane placement finding
Repository Steward™ and Labory Operating Contract™ currently exist inside `engurulabory/enguru-website-factory` even though their scope is cross-product Labory governance.

Current action:
- canonical Steward runtime is this Labory repository at `steward/`;
- Builder copies remain compatibility/protected references until dependency review is complete;
- long-term Builder state should be adapter/pointer only;
- no destructive move has been performed.

## Builder boundary
ENGÜRÜ Builder™ should retain:
- Builder product runtime and UI/UX;
- Builder-specific domain logic and flows;
- product-local `.enguru/labory-manifest.json`;
- Steward adapter/pointer, not canonical Steward runtime;
- adapter/reference to canonical Labory governance;
- Builder-specific evidence, tests, deployment and release truth;
- Builder Reference Loop Adapter™ for ENGÜRÜ CLOSED-LOOP PRODUCTION CORE™.

Builder should not remain the long-term canonical home of cross-product Labory control-plane policy or Repository Steward™.

## Labory boundary
ENGÜRÜ Labory should own:
- Product & Core Map™;
- Repository Order Pass™;
- Repository Steward™ canonical CORE_WORKER runtime and contract;
- portfolio/product registry;
- Labory operating/control-plane contract after compatibility migration is verified;
- cross-product governance pointers and repository health state;
- site/catalog bridge and verified publication inventory;
- ENGÜRÜ CLOSED-LOOP PRODUCTION CORE™ canonical specification and version governance.

## Existing governance contract transition
Current production reference remains:
`engurulabory/enguru-website-factory/packages/labory-operating-contract/index.mjs`

Principle ID: `ENGURU_LABORY_CONTROL_PLANE_V1`

Do not change Builder's canonical pointer until the Labory copy, manifests and tests are verified together. This is a controlled migration, not a blind move.

## Remaining discovery pass
Repository Steward™ must still:
1. find embedded cores across product repositories;
2. map dependencies and canonical paths;
3. locate DoneCheck / evidence / Verified Finish records;
4. detect duplicates, stale names and overlapping capabilities;
5. classify `adil-pay-kanit-web`;
6. verify Builder release-mirror relationship;
7. audit product-local Labory manifests;
8. produce final canonical topology;
9. verify Closed-Loop Core adapters do not duplicate product-local logic;
10. verify product-local Steward copies can be reduced to adapters/pointers without breaking tests or evidence.

## Acceptance gate
Map may move to PASS only when:
- accessible repositories are inventoried;
- known products/shared cores/core workers have canonical records;
- embedded-core and dependency discovery is complete;
- duplicate/overlap report is complete;
- repository-order recommendations are evidence-linked;
- no unresolved destructive action is auto-approved;
- DoneCheck verifies completeness against declared scope.
