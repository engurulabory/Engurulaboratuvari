# ENGÜRÜ Mac Engineering™ v0.7 — V07-A01 / V07-A02 Engineering Evidence — 2026-09-22

## STATE

**V07-A01 — PASS / EXACT-MAIN**

**V07-A02 — PASS / EXACT-MAIN**

v0.7 remains **ACTIVE**. This record does not assert v0.7 Verified / Locked.

## CLAIM

The existing v0.5/v0.6 reliability foundation satisfies the first two v0.7 acceptance gates without a production runtime behavior change.

The smallest sufficient engineering difference was one deterministic Product CI acceptance test package.

## EVIDENCE

### Product authority

Repository:

- `engurulabory/enguru-mac-engineer`

Baseline product main:

- `7f2e22994d17b913f226eb05691d934f81e1c212`
- Product CI run `35753607274` / run #17 — **SUCCESS**

Engineering PR:

- PR #9 — `Mac Engineer v0.7 — prove A01/A02 long-run reliability`
- exact-head: `56a932bf98e4fc24e549bd953133401898e47eaa`
- patch scope: exactly one file
- added file: `runtime/tests/test_v07_long_running_reliability.py`
- production `runtime/reliability.py`: unchanged
- review threads: 0
- fresh review: PASS / no blocking finding

Exact-head Product CI:

- run id: `35768412377`
- run number: **18**
- conclusion: **SUCCESS**
- full runtime tests: **48 / OK**
- native syntax/build gates: PASS

V07-A01 log receipt:

- governed tasks: **200**
- governed state transitions: **1,000**
- terminal state: `COMPLETE`
- terminal transition rejection: verified
- task/checkpoint/journal reconciliation: verified
- persisted-state digest:
  `28f32004cee1d9cc66d931abb3771eef31f44f9842427f2d9e5d680fc89f2a73`

V07-A02 log receipt:

- `before_durable_commit`: **10 / PASS**
- `after_checkpoint_commit`: **10 / PASS**
- `after_side_effect_receipt`: **10 / PASS**
- total repetitions: **30**
- task identity continuity: **true**
- continuity digest:
  `b8a5e6665d344e886c014d69068480275b5b9b5a68973154208d7db2a37dd641`

### Exact-main acceptance

Merge SHA / current product exact-main:

- `443fd4455b6c2f095c7944ee7bc00445d96d2d2a`

Exact-main Product CI:

- run id: `35768544303`
- run number: **19**
- conclusion: **SUCCESS**
- full runtime tests: **48 / OK**
- Runtime compile: PASS
- Runtime tests: PASS
- Native prep syntax: PASS
- Native Swift build verification: PASS

Exact-main V07-A01 log receipt:

- governed transitions: **1,000**
- tasks: **200**
- judgment: **PASS**
- persisted-state digest:
  `fe27c7f010539bf15f85b3e326e08fca4f118d4479dedc84b0581b0667acf2f8`

Exact-main V07-A02 log receipt:

- three interruption classes: **10 repetitions each**
- total repetitions: **30**
- task identity continuity: **true**
- judgment: **PASS**
- continuity digest:
  `5e5d87b437daeba41b72d692474bf257b07584b9811c1e78c21540cbd954cac2`

Digest values differ across independent CI executions because generated task identities are unique per run. The acceptance invariant is the verified transition count, persisted reconciliation, interruption-class coverage, and identity continuity within each run.

## REQUIRED DIFFERENCE

Completed:

- `V07-A01 LONG_RUN_TASK_STATE_CORRECTNESS = PASS`
- `V07-A02 DURABLE_RESUME_ACROSS_INTERRUPTION = PASS`

No new core was required.

Production reliability behavior remained unchanged.

## JUDGMENT

**PASS — V07-A01 + V07-A02 ENGINEERING VERIFIED ON PRODUCT EXACT-MAIN**

v0.7 remains active because V07-A03…A12 remain subject to their own acceptance contracts.

## NEXT ACTION

`V07-A03 + V07-A04 → IDEMPOTENCY_AND_SINGLE_WRITER_STRESS → GITHUB_FIRST_ENGINEERING`
