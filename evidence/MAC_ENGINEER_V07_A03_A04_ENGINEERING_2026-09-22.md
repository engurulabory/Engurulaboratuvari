# ENGÜRÜ Mac Engineering™ v0.7 — V07-A03 / V07-A04 Engineering Evidence — 2026-09-22

## STATE

**V07-A03 — PASS / EXACT-MAIN**

**V07-A04 — PASS / EXACT-MAIN**

v0.7 remains **ACTIVE**. This record does not assert v0.7 Verified / Locked.

## CLAIM

The existing idempotency index and single-writer lock satisfy the v0.7 idempotency and concurrency stress gates without a production runtime behavior change.

The smallest sufficient engineering difference was an extension of the existing deterministic v0.7 Product CI acceptance test package.

## EVIDENCE

### Product authority

Repository:

- `engurulabory/enguru-mac-engineer`

Baseline product main:

- `443fd4455b6c2f095c7944ee7bc00445d96d2d2a`

Engineering PR:

- PR #10 — `Mac Engineer v0.7 — prove A03/A04 idempotency and writer stress`
- exact-head: `f401ae760481dfad762a0de7fae6a2d9139b8977`
- patch scope: exactly one file
- modified file: `runtime/tests/test_v07_long_running_reliability.py`
- production `runtime/reliability.py`: unchanged
- review threads: 0
- fresh review: PASS / no blocking finding

Exact-head Product CI:

- run id: `35769088949`
- run number: **20**
- conclusion: **SUCCESS**
- full runtime tests: **50 / OK**
- native syntax/build gates: PASS

V07-A03 exact-head receipt:

- same work unit replays: **100**
- created: **1**
- deterministic duplicates: **99**
- durable side effects: **1**
- task identity stable: **true**
- durable receipt SHA-256:
  `d3c86c268b12b26cbe5f4d65e23821a65e6ac000b754c4dcc04a2bbc73f7f7b5`
- judgment: **PASS**

V07-A04 exact-head receipt:

- concurrent contenders: **16**
- canonical writers: **1**
- `WriterBusy` outcomes: **15**
- committed transitions: **1**
- final persisted state: `RUNNING`
- judgment: **PASS**

### Exact-main acceptance

Merge SHA / current product exact-main:

- `1dcbc795e4b949448206fbad93b239aca297cc0f`

Exact-main Product CI:

- run id: `35769257875`
- run number: **21**
- conclusion: **SUCCESS**
- full runtime tests: **50 / OK**
- Runtime compile: PASS
- Runtime tests: PASS
- Native prep syntax: PASS
- Native Swift build verification: PASS

Exact-main V07-A03 receipt:

- replays: **100**
- created: **1**
- duplicates: **99**
- durable side effects: **1**
- task identity stable: **true**
- durable receipt SHA-256:
  `d3c86c268b12b26cbe5f4d65e23821a65e6ac000b754c4dcc04a2bbc73f7f7b5`
- judgment: **PASS**

Exact-main V07-A04 receipt:

- concurrent contenders: **16**
- canonical writers: **1**
- `WriterBusy`: **15**
- transition commits: **1**
- final state: `RUNNING`
- judgment: **PASS**

## REQUIRED DIFFERENCE

Completed:

- `V07-A03 IDEMPOTENCY_STRESS = PASS`
- `V07-A04 SINGLE_WRITER_CONCURRENCY_SAFETY = PASS`

No new core was required.

Production reliability behavior remained unchanged.

## JUDGMENT

**PASS — V07-A03 + V07-A04 ENGINEERING VERIFIED ON PRODUCT EXACT-MAIN**

v0.7 remains active because V07-A05…A12 remain subject to their own acceptance contracts.

## NEXT ACTION

`V07-A05 + V07-A06 → BOUNDED_RETRY_WATCHDOG_AND_RECOVERY_FIXTURES → GITHUB_FIRST_ENGINEERING`
