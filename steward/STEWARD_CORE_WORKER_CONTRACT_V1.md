# Repository Steward™ — Core Worker Contract v1

## Classification
**CORE_WORKER / CONTROL-PLANE WORKER**

Repository Steward™ is not a product. It is a Labory-owned worker core that moves across the control plane, registered products, registered cores, evidence surfaces and repository health records.

## Canonical home
`engurulabory/Engurulaboratuvari/steward/`

Product repositories may expose only adapters, manifests, evidence hooks and pointers to Steward. They must not become the canonical home of Steward policy or runtime.

## Operating loop
`LAB HOME → PRODUCT REGISTRY → PRODUCTS → CORES → MANIFESTS → DEPENDENCIES → CI/TEST → EVIDENCE → DONECHECK → REPOSITORY HEALTH → WORKLIST → SAFE MAINTENANCE → HUMAN THRESHOLD WHEN REQUIRED → LOOP`

## Worker responsibilities
Repository Steward™ must:
1. read the canonical Product & Core Map™;
2. inspect each registered product/core using its manifest and repository evidence;
3. detect canonical-owner drift, duplicate capability, stale naming, stale evidence and release-mirror ambiguity;
4. inspect README, manifest, CI/test, security, lifecycle and evidence health;
5. compare product-local governance with Labory canonical governance;
6. apply only bounded, reversible maintenance where authority is explicit;
7. record every material finding as state, claim, evidence and next action;
8. update central worklists/health records when safe;
9. stop at Human Threshold™ for destructive, authority-changing or production-cutover actions;
10. repeat on the configured maintenance cadence.

## Allowed maintenance
Examples:
- documentation truth alignment;
- manifest correction where canonical ownership is already evidenced;
- stale pointer repair;
- worklist/health-state updates;
- non-destructive evidence indexing;
- adapter/pointer normalization after compatibility proof;
- safe formatting/organization changes that do not alter runtime behavior.

## Human Threshold required
Steward must not autonomously:
- archive or delete repositories;
- rename repositories;
- merge/consolidate repositories;
- change repository visibility;
- rewrite history or force-push;
- delete protected branches;
- change canonical product ownership without evidence/review;
- change legal/commercial authority;
- cut over production deployment/source;
- make product-retirement decisions.

## Product boundary
A product owns:
- product runtime;
- product UI/UX;
- product-specific domain logic;
- local tests/evidence/deployment truth;
- product-specific adapters to shared cores/workers.

Steward owns none of the product's domain logic. Steward observes, verifies, maintains repository/order health and opens bounded corrections.

## Labory surface model
Steward traverses these surfaces as one worker:

1. **Laboratory Home / Control Plane** — portfolio truth, registry, central worklist.
2. **Products** — product manifests, runtime/evidence pointers, release state.
3. **Cores** — shared capability ownership, versions, adapters, dependency health.
4. **Evidence / DoneCheck™** — proof freshness and final-state consistency.
5. **Repository Health** — hygiene, CI, security, duplication, lifecycle state.

It does not need a separate user-facing product surface to exist.

## Cadence
Default maintenance cadence: every 3 days unless a faster incident/commissioning loop is explicitly activated.

Each cycle outputs:
`STATE → CLAIM → EVIDENCE → SAFE ACTION TAKEN → HUMAN THRESHOLD (if any) → NEXT ACTION`

## Success condition
Repository Steward™ is healthy when:
- all registered assets are discoverable;
- every active asset has one canonical role/owner;
- product/core adapters resolve to current canonical contracts;
- no unexplained duplicate ownership remains;
- stale/broken evidence and repository-health issues are surfaced quickly;
- safe drift is corrected without touching product authority;
- destructive decisions are never auto-approved.
