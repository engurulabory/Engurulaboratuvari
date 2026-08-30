# ENGÜRÜ CLOSED-LOOP PRODUCTION CORE™ v0.1

## State
DESIGN LOCKED — implementation remains staged and evidence-gated.

## Purpose
Provide one reusable closed-loop production contract for ENGÜRÜ products and operating surfaces so that work is not considered finished because an agent claims completion. Every meaningful task must move through observable execution, evidence-backed verification, bounded correction and an explicit finish gate.

## Locked production loop
`INTENT → TASK CONTRACT → SUCCESS CRITERIA → EXECUTE → OBSERVE → COLLECT EVIDENCE → VERIFY → CORRECT/RETRY → DONECHECK™ → HUMAN THRESHOLD™ WHEN REQUIRED → VERIFIED FINISH`

## Core rule
A claim is not evidence. A task may reach PASS only when its success criteria are supported by verifiable evidence.

## Runtime contract
Every loop run must expose at minimum:

- `intent`
- `task`
- `successCriteria[]`
- `executionState`
- `observation[]`
- `evidence[]`
- `verificationResult`
- `failureClass` when verification fails
- `correctionAction` when retry/revision is allowed
- `attempt`
- `maxAttempts` or another bounded-stop rule
- `doneCheckResult`
- `humanThresholdRequired`
- `finalState`: `PASS | HOLD | BLOCKED`

## Non-negotiable rules
1. Every task has a verifiable finish condition.
2. Every execution plane has at least one observation surface: tests, browser, API, preview, filesystem/artifact, runtime telemetry, financial settlement evidence, or another domain-appropriate verifier.
3. Changes should be the smallest reviewable unit compatible with the task.
4. Retry is bounded and must follow failure classification; blind repetition is prohibited.
5. The producing agent cannot self-certify final completion without evidence.
6. The same failed attempt must not be repeated with the same state and same evidence as though it were a new correction.
7. Consequential publication, payment, destructive repository action, legal/compliance claim, or irreversible external action remains behind Human Threshold™.
8. Fail closed: missing critical evidence produces HOLD; a real execution blocker produces BLOCKED.

## Canonical responsibilities

### Reuse
Existing ENGÜRÜ capabilities that should remain canonical and be referenced rather than duplicated:

- ENGÜRÜ Language Governance™ — `state → claim → evidence → next action` language/decision discipline.
- DoneCheck™ — verification and final acceptance logic.
- Human Threshold™ — authority boundary for consequential decisions.
- Evidence collection patterns already present in product repositories.
- Repository Steward™ — cross-repository discovery, drift and control-plane truth.
- Shift Core™ rollback/revision concepts where task acceptance or reversal semantics are needed.
- AEC bounded retry, persistence, failure-recovery and settlement-proof patterns where economic/runtime semantics are needed.

### Extend
Capabilities that exist but require a shared cross-product contract:

- standardized Task Contract;
- standardized Success Criteria schema;
- standardized Evidence Envelope;
- failure taxonomy;
- correction/revision policy;
- bounded-loop policy;
- Verified Finish record;
- loop telemetry and run history;
- adapter interface for product-local observation tools.

### Adapter needed
Product-local adapters must translate domain truth into the shared loop contract. The core must not absorb product-specific business logic.

## Reuse / Extend / Adapter Needed Map

| Surface | Reuse | Extend | Adapter needed | Initial state |
|---|---|---|---|---|
| ENGÜRÜ Builder™ | Existing product runtime, tests, evidence surfaces, DoneCheck/governance references, publish/preview flow | Shared Task Contract, Evidence Envelope, failure taxonomy, bounded correction loop, Verified Finish record | Browser/preview adapter; build/test/type-check adapter; publish/deploy adapter; asset/revision adapter | HOLD — design integration only |
| Autonomous Economic Core™ (AEC) | Orchestrator/worker runtime, persistence, retry/recovery, audit evidence, economic finality chain | Shared loop envelope, normalized success criteria, failure taxonomy, run telemetry, cross-product DoneCheck handoff | Revenue-door adapter; work acceptance adapter; settlement/payout/bank-proof adapter | HOLD — design integration only |
| ENGÜRÜ Lab / Engurulaboratuvari | Product & Core Map™, Repository Order Pass™, Steward, registry/evidence control-plane | Cross-product loop registry, loop health state, canonical core ownership, policy/version tracking | Repository/CI adapter; site-registry adapter; deployment-health adapter | HOLD — canonical control-plane target |
| ENGÜRÜ Verified Business OS™ | Language Governance™, DoneCheck™, Human Threshold™, Closed-Loop Production Core™ when proven | Business State Core™ integration, cross-department orchestration, audit/economic/operational state transitions | Future business-domain adapters: finance, sales, delivery, compliance, customer, operations | HOLD — future target; no premature implementation |

## Surface-specific interpretation

### Builder loop
`intent → plan/alternative → generation → browser/build/test observation → evidence → revision if needed → publish verification → DoneCheck → Human Threshold where consequential → Verified Finish`

Builder remains owner of UI, UX, asset intake, generation, revision and publish behavior. Closed-Loop Core owns only the common loop contract.

### AEC loop
`opportunity → qualification → work execution → acceptance evidence → settlement evidence → payout/bank evidence where required → DoneCheck → Verified Economic Finish`

AEC remains owner of economic opportunity logic, worker execution and settlement semantics. Closed-Loop Core normalizes the loop and evidence contract; it does not redefine economic finality.

### ENGÜRÜ Lab loop
`repository/product state → observe inventory/health → collect evidence → verify map/order/registry rules → correction queue → DoneCheck → registry/publication eligibility`

Labory is the canonical control-plane home for the shared Closed-Loop Production Core specification and version governance.

### Verified Business OS loop
`business intent → business state → delegated execution loops → evidence-backed state transitions → DoneCheck → Human Threshold → verified business outcome`

Verified Business OS™ must consume the proven core later. It must not fork or duplicate it.

## Ownership rule
Canonical specification ownership: `engurulabory/Engurulaboratuvari`.

Product repositories retain only:
- local runtime logic;
- domain-specific success criteria;
- observation/verifier adapters;
- product-local evidence;
- compatibility/reference pointers to the canonical core.

No large move/delete/merge/rename is authorized by this document.

## Implementation sequence
1. Lock v0.1 specification in Labory.
2. Add machine-readable schema for Task Contract / Evidence Envelope / Final State.
3. Build reference loop runner with bounded retry and failure classification.
4. Build Builder adapters first because Builder is the next locked product target.
5. Prove Builder loop on one real end-to-end publish journey.
6. Add AEC adapters without disturbing its already-proven commissioning/finality logic.
7. Add Labory Steward adapter for repository/control-plane loops.
8. Run cross-product DoneCheck and drift tests.
9. Promote core from design HOLD only after evidence-backed multi-surface PASS.
10. Reuse the proven core later inside ENGÜRÜ Verified Business OS™.

## Acceptance gate for v0.1 implementation
PASS requires evidence that:

- the same core contract executes in at least Builder + AEC + Labory;
- each surface uses product-specific adapters rather than copied core logic;
- failed verification triggers classified bounded correction;
- false completion claims cannot produce PASS without evidence;
- loop history/evidence can be inspected;
- Human Threshold cannot be bypassed where required;
- existing product behavior is preserved unless a deliberate, tested change is part of the task;
- DoneCheck verifies the final state.

Until these are demonstrated, implementation state remains HOLD.

## Governance judgment
STATE — DESIGN LOCKED / IMPLEMENTATION HOLD

CLAIM — ENGÜRÜ CLOSED-LOOP PRODUCTION CORE™ v0.1 is the canonical shared loop architecture for future cross-product production work.

EVIDENCE — Existing Labory governance already establishes centralized Product & Core Map™, Repository Order Pass™, Steward ownership and a migration direction in which cross-product governance is centralized and product repositories retain adapters/local truth. Builder and AEC both already expose product-local evidence/runtime surfaces suitable for adapter integration.

NEXT ACTION — Add the v0.1 work package to the Labory worklist, then implement the machine-readable contract and Builder reference adapter without moving or deleting existing product logic.
