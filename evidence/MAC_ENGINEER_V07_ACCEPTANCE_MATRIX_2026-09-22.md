# ENGÜRÜ Mac Engineering™ v0.7 — Acceptance Matrix Evidence — 2026-09-22

## STATE

**V0.7 ACCEPTANCE MATRIX — DEFINED / CANONICAL CANDIDATE**

## CLAIM

The first required difference for `V0_7_LONG_RUNNING_RELIABILITY` is complete on this branch: existing v0.5/v0.6 reliability truth is expressed as an exact, testable acceptance contract without introducing a new core.

## EVIDENCE

Baseline exact-main:

- control-plane main: `7d8b7e489f10d8c74db673d662399a9a572448e3`
- v0.0–v0.3 historical reconstruction: PASS / CLOSED
- v0.6: VERIFIED FINAL / LOCKED
- active objective: `V0_7_LONG_RUNNING_RELIABILITY`

Canonical acceptance contract:

- `governance/mac-engineer/V07_LONG_RUNNING_RELIABILITY_ACCEPTANCE_MATRIX_V1.md`

The matrix defines twelve gates covering:

- task-state correctness;
- durable resume;
- idempotency stress;
- single-writer/concurrency safety;
- bounded retry/watchdog;
- provider/network/process recovery;
- resource discipline;
- Evidence continuity;
- repeated fault-injection CI;
- DoneCheck v1.2 integration;
- one consolidated Mac long-run commissioning campaign;
- Human Threshold™ / version lock.

## REQUIRED DIFFERENCE

Canonical records advance only the first v0.7 work item:

`DEFINE_EXACT_ACCEPTANCE_MATRIX = PASS`

The next active engineering package becomes:

`V07-A01 + V07-A02 → LONG_RUN_TASK_STATE_AND_DURABLE_RESUME`

## JUDGMENT

**PASS — ACCEPTANCE CONTRACT DEFINED**

This judgment covers the governance/acceptance contract only. It does not assert that v0.7 engineering or Mac commissioning has already passed.

## NEXT ACTION

Implement and verify `V07-A01` and `V07-A02` in the technical product source, then continue through the matrix under GitHub-first / Milestone-Mac governance.
