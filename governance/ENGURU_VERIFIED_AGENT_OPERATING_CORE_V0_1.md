# ENGÜRÜ VERIFIED AGENT OPERATING CORE™ v0.1

## State
VISION LOCKED — architecture positioning established; implementation remains evidence-gated.

## Purpose
Provide one shared operating architecture for ENGÜRÜ agentic products and workers so that autonomy, execution, evidence, verification, authority and learning remain governed by a common contract.

This is not a new product and does not replace existing cores. It is the upper operating architecture that composes existing ENGÜRÜ capabilities without duplicating product-local logic.

## Locked architecture

`Task Contract
→ Capability Contract
→ Agent Runtime
→ Closed-Loop Production Core™
→ Evidence
→ DoneCheck™
→ Human Threshold™
→ Verified Finish
→ Verified Learning`

## Core principle
Autonomy is not completion.

A task reaches a trusted final state only when execution is bounded by declared capability, produces verifiable evidence, passes independent acceptance logic, respects Human Threshold™, and records learning without converting unverified output into truth.

## Layer responsibilities

### 1. Task Contract
Declares:
- intent;
- scope;
- success criteria;
- constraints;
- expected evidence;
- stop conditions;
- final-state rules.

### 2. Capability Contract
Declares what an agent may and may not do for the task.

Examples:
- repository read/write scope;
- branch creation permission;
- runtime/tool access;
- external communication scope;
- publication authority;
- payment authority;
- destructive-action restrictions;
- Human Threshold™ requirements.

Default rule: least necessary authority.

### 3. Agent Runtime
Executes the task through one or more workers, specialists or orchestrators.

The runtime may be model- and vendor-independent. Models are replaceable execution engines; governance, contracts, evidence and domain truth remain ENGÜRÜ-owned.

### 4. Closed-Loop Production Core™
Canonical shared loop:
`INTENT → TASK CONTRACT → SUCCESS CRITERIA → EXECUTE → OBSERVE → COLLECT EVIDENCE → VERIFY → CORRECT/RETRY → DONECHECK™ → HUMAN THRESHOLD™ WHEN REQUIRED → VERIFIED FINISH`

Canonical specification:
`governance/ENGURU_CLOSED_LOOP_PRODUCTION_CORE_V0_1.md`

### 5. Evidence
Every material claim must be backed by an inspectable evidence surface appropriate to the task.

Examples:
- tests;
- CI;
- browser observation;
- API response;
- file/artifact digest;
- deployment health;
- financial settlement record;
- provenance;
- human acceptance record.

A claim is not evidence.

### 6. DoneCheck™
Determines whether declared success criteria are actually satisfied by evidence.

The producing agent must not self-certify PASS merely because execution completed.

### 7. Human Threshold™
Consequential or irreversible authority remains human-governed where required.

Typical threshold classes:
- merge to protected/canonical state;
- public publication;
- payment or economic commitment;
- legal/compliance representation;
- destructive repository or data action;
- external action on behalf of a real person or institution;
- acceptance where evidence cannot resolve responsibility.

### 8. Verified Finish
Allowed final states:
- PASS — required evidence exists and acceptance criteria are satisfied;
- HOLD — missing evidence, stale truth or human threshold remains;
- BLOCKED — a real execution blocker prevents completion.

### 9. Verified Learning
Learning may update future execution only from verified outcomes.

Verified Learning must preserve:
- source/provenance;
- evidence link;
- freshness;
- acceptance state;
- scope;
- version;
- revocation/correction path.

Unverified model output, failed attempts and stale assumptions must not silently become canonical memory or policy.

## Application positioning

### ENGÜRÜ Builder™
Position: application/product running on the shared operating core.

Retains:
- Builder UI/UX;
- generation and revision behavior;
- product-local domain logic;
- preview/publish behavior;
- Builder-specific adapters and evidence.

Consumes:
- Task Contract;
- Capability Contract;
- Closed-Loop Production Core™;
- DoneCheck™;
- Human Threshold™;
- Verified Finish;
- Verified Learning.

### Repository Steward™
Position: control-plane worker running on the shared operating core.

Retains:
- repository discovery;
- drift detection;
- inventory;
- health observation;
- governance synchronization.

Consumes the shared operating contract for bounded authority, evidence, acceptance and learning.

### Autonomous Economic Core™ — AEC
Position: economic/operational application running on the shared operating core.

Retains:
- opportunity logic;
- orchestrator/worker semantics;
- settlement and economic finality rules;
- economic evidence.

Payment, payout and irreversible economic actions remain capability-bounded and Human Threshold™ governed where required.

### ZEKÜ PRIME
Position: agent operating application/foundation consuming the shared core.

Specialist cores and workers operate under Task Contract + Capability Contract and must return evidence into the same verification and acceptance path.

### Future agents and products
New agentic products should reuse this operating architecture before introducing a parallel execution/governance stack.

Rule:
`reuse → extend → adapter`

Forking shared governance semantics requires explicit evidence-backed governance approval.

## Ownership boundary
Canonical ownership: `engurulabory/Engurulaboratuvari`.

Labory owns:
- shared operating contract;
- version governance;
- capability semantics;
- evidence/acceptance interfaces;
- cross-product architecture references.

Product repositories own:
- domain logic;
- local runtime integration;
- product-specific success criteria;
- observation/verifier adapters;
- product-local evidence;
- product-specific UI and business behavior.

No product-local logic move/delete/rename is authorized by this vision document.

## Relationship to existing ENGÜRÜ cores

This architecture reuses and composes existing canonical capabilities:

- ENGÜRÜ Language Governance™;
- Machine-Readable Contract™;
- ENGÜRÜ CLOSED-LOOP PRODUCTION CORE™;
- Evidence patterns / Evidence Envelope;
- DoneCheck™;
- Human Threshold™;
- Repository Steward™;
- ENGÜRÜ IP & MODEL TRUST GATE™;
- Verified Finish;
- verified-learning governance.

It does not supersede them.

## Six-month architectural target

The target is not "more autonomous agents".

The target is:

**reliable, bounded, observable, evidence-backed, replaceable-model autonomous work.**

Success means:
1. one shared operating contract can govern Builder, Steward, AEC and ZEKÜ PRIME;
2. agent authority is explicit and machine-readable;
3. product-local adapters preserve existing working behavior;
4. evidence is inspectable;
5. false completion cannot produce PASS;
6. Human Threshold™ cannot be bypassed where required;
7. verified outcomes can improve future runs without promoting unverified claims into truth;
8. model/provider replacement does not require rewriting ENGÜRÜ governance.

## Governance judgment

STATE — VISION LOCKED / IMPLEMENTATION HOLD

CLAIM — ENGÜRÜ VERIFIED AGENT OPERATING CORE™ is the upper shared operating architecture for ENGÜRÜ agentic products and workers.

EVIDENCE — Existing Labory governance already provides the Closed-Loop Production Core™, DoneCheck™, Human Threshold™, Evidence, Repository Steward™, IP & Model Trust Gate™ and product/core ownership rules. This architecture composes those existing capabilities and adds the missing explicit Capability Contract + Verified Learning placement.

NEXT ACTION — Register this architecture in the Product & Core Map™, then implement only the missing shared contracts/adapters in dependency order. Existing PASS behavior remains protected; no large migration is authorized by vision lock alone.
