# ENGÜRÜ Mac Engineer™ — Capability Orchestration Finish Worklist v1

## STATE

This worklist locks the next bounded finish objective after the v0.8 Product Engineering Operator lock.

No new core is authorized.

The existing operator spine remains authoritative:

`OPERATOR_ACTION_REGISTRY → enguru-mac continue → Evidence → DoneCheck™ → Human Threshold™`

A Capability Orchestration Layer may extend this spine, but may not bypass it.

## FINAL OBJECTIVE

ENGÜRÜ Mac Engineer™ will preserve the current 19 capability inventory and orchestrate the required capabilities automatically from human intent, while remaining fail-closed, bounded, recoverable, evidence-driven and Human-Threshold-aware.

Final acceptance requires:

`CAPABILITY_FIELD_VERIFICATION = 19_OF_19_PASS`

`ORCHESTRATION = VERIFIED`

`AUTOMATION = VERIFIED`

`RECOVERY = VERIFIED`

`EVIDENCE = COMPLETE`

`DONECHECK = PASS`

`HUMAN_THRESHOLD = PASS_WHERE_REQUIRED`

`FINAL_STATE = CAPABILITY_ORCHESTRATION_VERIFIED`

## CANONICAL CAPABILITY COUNT

Exactly 19 capability IDs will be reconciled and kept unique:

1. Current Technical Truth Read
2. Canonical Boot
3. Doctor
4. Continue / Dispatch
5. Fail-Closed
6. Source / Product Change
7. Build
8. Test / Regression
9. Root-Cause Repair
10. Migration / Reconciliation
11. Advanced Code Engineering
12. New Product from Brief
13. Release Lifecycle
14. Product Delivery Acceptance
15. Evidence / DoneCheck™
16. Recovery / Offline Continuity
17. Terminal Execution
18. Filesystem / macOS Automation
19. Internet / Research Harvest / Astra

## ORCHESTRATION CONTRACT

Human gives intent and boundary.

Mac Engineer selects and orchestrates the required capability chain:

`CURRENT TRUTH READ`
→ `CAPABILITY SELECTION`
→ `SAFE PLAN`
→ `PREFLIGHT / AUTHORITY`
→ `EXECUTION`
→ `TEST / VERIFY`
→ `BOUNDED REPAIR LOOP when needed`
→ `EVIDENCE`
→ `DONECHECK™`
→ `HUMAN THRESHOLD™ when required`
→ `VERIFIED RESULT`

Target future entry surface:

`enguru-mac work "<human intent>"`

This command is a target surface only and must not be treated as currently available until implemented and field-verified.

## AUTHORITY CLASSES

### GREEN

Mac Engineer may execute autonomously within policy:

- read
- inspect
- build
- test
- research
- temporary workspace
- Evidence production

### AMBER

Bounded mutation only:

- source modification
- filesystem modification
- local install
- release preparation

Mutation scope must be explicit.

### RED

Human Threshold™ required:

- permanent deletion
- broad filesystem mutation
- credential use
- payment
- production publish
- remote destructive action
- irreversible migration
- critical security change

## REQUIRED ORCHESTRATION SAFEGUARDS

- deterministic execution
- idempotency
- durable checkpoint
- rollback / recovery point
- mutation budget
- network allow policy
- bounded retry budget
- Evidence per material step
- fresh verification
- single-writer discipline
- no stale PASS as final authority
- no unsupported canonical claim
- no authority bypass

## 8-PACKAGE FINISH WORKLIST

### [ ] PACKAGE 01 — 19-Capability Inventory Reconciliation

Finish and reconcile `CURRENT_PROVEN_CAPABILITY_INVENTORY_V1.md`.

Acceptance:
- exactly 19 unique capability IDs
- no duplicate numbering
- no truncated content
- each capability has current truth status
- each capability has invocation/use path
- current evidence lineage preserved
- Finder GUI and general-browser claims remain bounded to current evidence
- diff check PASS
- Second Look PASS
- canonical commit + exact remote parity

### [ ] PACKAGE 02 — Capability Registry

Create a governed registry for all 19 capabilities.

Each capability must define:

- CAPABILITY_ID
- STATE
- INPUTS
- OUTPUTS
- PRECONDITIONS
- AUTHORITY
- RISK_CLASS
- MUTATION_SCOPE
- NETWORK_POLICY
- REQUIRES_HUMAN_THRESHOLD
- RETRY_POLICY
- ROLLBACK_POLICY
- EVIDENCE_REQUIREMENTS
- NEXT_COMPATIBLE_CAPABILITIES

Acceptance:
- 19/19 registry coverage
- no orphan capability
- fail-closed defaults
- validation tests PASS

### [ ] PACKAGE 03 — Capability Dependency Graph / DAG

Bind safe capability dependencies and legal transitions.

Acceptance:
- no unsafe cyclic execution path
- explicit prerequisites
- explicit compatible next capabilities
- RED authority cannot be bypassed
- graph validation PASS

### [ ] PACKAGE 04 — Intent → Execution Plan Router

Transform bounded human intent into a deterministic capability plan.

Acceptance:
- same intent + same truth produces stable plan
- unsupported intent returns HOLD
- no invented capability
- authority requirements resolved before execution
- plan Evidence produced

### [ ] PACKAGE 05 — Safe Execution Orchestrator

Execute the approved plan through existing operator authority.

Acceptance:
- no new core
- existing OPERATOR_ACTION_REGISTRY authority preserved
- mutation budget enforced
- network policy enforced
- single-writer lock enforced
- step Evidence emitted
- unexpected state returns HOLD

### [ ] PACKAGE 06 — Automation Reliability

Implement and prove:

- Auto-plan
- Auto-execute
- Auto-repair
- Auto-recover
- Auto-finish

Acceptance:
- bounded repair attempts
- no infinite loop
- checkpoint/restart continuity
- fresh revalidation after recovery
- rollback/recovery proof for mutating flows
- terminal failure states deterministic

### [ ] PACKAGE 07 — Evidence / DoneCheck™ / Human Threshold™ Binding

Bind orchestration finish to governance authority.

Acceptance:
- material steps produce Evidence
- final verification is fresh
- DoneCheck™ PASS required
- RED actions require Human Threshold™
- cached PASS cannot authorize final finish
- no unsupported final claim

### [ ] PACKAGE 08 — 19/19 Real OSi Field Verification Campaign

Each capability must pass the same minimum field acceptance chain:

`DISCOVERED`
→ `INVOCABLE`
→ `REAL_TASK_EXECUTED`
→ `EXPECTED_RESULT_OBSERVED`
→ `FAILURE_PATH_TESTED`
→ `FRESH_REVERIFY`
→ `EVIDENCE_BOUND`
→ `DONECHECK_PASS`
→ `FIELD_VERIFIED`

Additional requirements:

- mutating capabilities: rollback or recovery proof
- RED authority capabilities: Human Threshold™ proof
- capability 18: real filesystem/macOS automation field proof; Finder GUI authority must be classified separately
- capability 19: real internet/Research Harvest/Astra field proof; general-browser operation must be classified separately

Final acceptance:

- 19/19 FIELD_VERIFIED
- CRITICAL_FALSE_PASS = 0
- UNTRACKED_MUTATION = 0
- AUTHORITY_BYPASS = 0
- UNBOUNDED_RETRY = 0
- EVIDENCE_MISSING = 0
- STALE_PASS_USED_AS_FINAL = 0
- HUMAN_THRESHOLD_MISS = 0

## PROGRESS ACCOUNTING

Top-level finish progress is measured only by completed packages:

- Total packages: 8
- Completed packages: 0
- Remaining packages: 8
- Completion: 0%

Existing historical capability evidence is baseline evidence and does not count as a completed package until reconciled through this worklist.

After every material package result, report:

- package completed or HOLD
- evidence path / digest / exact HEAD where applicable
- completed package count
- remaining package count
- completion percentage
- next threshold

## CURRENT JUDGMENT

STATE — WORKLIST_LOCKED / EXECUTION_NOT_STARTED

CLAIM — The next bounded objective is not future-version design. It is to finish, harden, orchestrate and field-verify the existing 19 capabilities.

CURRENT COMPLETION — 0 / 8 packages = 0%

NEXT ACTION — PACKAGE 01 / 19-CAPABILITY INVENTORY RECONCILIATION

No orchestration final PASS before 19/19 capability field verification.
