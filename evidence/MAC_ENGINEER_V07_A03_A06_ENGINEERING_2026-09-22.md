# ENGÜRÜ Mac Engineering™ v0.7 — V07-A03…A06 Engineering Evidence — 2026-09-22

## STATE

**V07-A03 — PASS / EXACT-MAIN**  
**V07-A04 — PASS / EXACT-MAIN**  
**V07-A05 — PASS / EXACT-MAIN**  
**V07-A06 — PASS / EXACT-MAIN**

v0.7 remains **ACTIVE**. This record does not assert v0.7 Verified / Locked.

## CLAIM

The current product exact-main proves idempotency stress, single-writer concurrency safety, bounded retry/watchdog behavior, and provider/network/process recovery fixtures under the canonical v0.7 acceptance matrix.

The engineering path reused the existing ReliabilityManager. A03/A04 required acceptance tests only. A05/A06 required one bounded retry extension inside the existing reliability layer; no new core was introduced.

## EVIDENCE

Repository:

- `engurulabory/enguru-mac-engineer`

### V07-A03 + V07-A04

Product PR #10:

- title: `Mac Engineer v0.7 — prove A03/A04 idempotency and writer stress`
- exact-head: `f401ae760481dfad762a0de7fae6a2d9139b8977`
- exact-head Product CI: run `35769088949` / #20 — **SUCCESS**
- exact-main merge: `1dcbc795e4b949448206fbad93b239aca297cc0f`
- exact-main Product CI: run `35769257875` / #21 — **SUCCESS**
- runtime regression: **50 tests / OK**
- review threads: **0**

V07-A03 exact-main receipt:

- replays: **100**
- created: **1**
- deterministic duplicates: **99**
- durable side effects: **1**
- task identity stable: **true**
- receipt sha256: `d3c86c268b12b26cbe5f4d65e23821a65e6ac000b754c4dcc04a2bbc73f7f7b5`
- judgment: **PASS**

V07-A04 exact-main receipt:

- concurrent contenders: **16**
- canonical writers: **1**
- WriterBusy outcomes: **15**
- transition commits: **1**
- final persisted state: `RUNNING`
- judgment: **PASS**

### V07-A05 + V07-A06

Product PR #11:

- title: `Mac Engineer v0.7 — bounded retry and recovery fixtures`
- base: `1dcbc795e4b949448206fbad93b239aca297cc0f`
- exact-head: `6dd92012859f77c0e70ef43d3c6833734ea82b64`
- exact-head Product CI: run `35770093773` / #22 — **SUCCESS**
- exact-main merge/current product main: `199893b07941a82c26c3b39a7942478cb95420b0`
- exact-main Product CI: run `35770247337` / #23 — **SUCCESS**
- runtime regression: **52 tests / OK**
- review threads: **0**

Minimal production extension:

- `BOUNDED_RETRY_POLICY.retry_limit = 2`
- `BOUNDED_RETRY_POLICY.max_attempts = 3`
- `ReliabilityManager.bounded_retry(...)`
- retry exception allowlist required
- configured retry limit cannot exceed policy
- over-limit input fails closed
- every attempt writes durable journal intent/commit Evidence
- non-retryable exceptions remain fail-closed and are re-raised

V07-A05 exact-main receipt:

- retry limit: **2**
- maximum attempts: **3**
- observed exhausted attempts: **3**
- over-limit fail-closed: **true**
- watchdog governed decisions: **1**
- repeated watchdog findings after decision: **0**
- watchdog state: `RECOVERY_REQUIRED`
- judgment: **PASS**

V07-A06 exact-main receipt:

Three deterministic failure classes each prove a recoverable and exhausted path:

- `provider_unavailable`: recoverable at attempt 2 / exhausted at attempt 3
- `network_timeout`: recoverable at attempt 2 / exhausted at attempt 3
- `child_process_exit`: recoverable at attempt 2 / exhausted at attempt 3

For every class:

- task identity continuity: **true**
- durable Evidence continuity: **true**
- exhausted path remains bounded
- judgment: **PASS**

## REQUIRED DIFFERENCE

Completed:

- `V07-A03 IDEMPOTENCY_STRESS = PASS`
- `V07-A04 SINGLE_WRITER_CONCURRENCY_SAFETY = PASS`
- `V07-A05 BOUNDED_RETRY_WATCHDOG = PASS`
- `V07-A06 PROVIDER_NETWORK_PROCESS_RECOVERY = PASS`

v0.7 remains active.

## JUDGMENT

**PASS — V07-A01…A06 ENGINEERING VERIFIED ON CURRENT PRODUCT EXACT-MAIN**

## NEXT ACTION

`V07-A07 + V07-A08 → RESOURCE_DISCIPLINE_AND_EVIDENCE_CONTINUITY → GITHUB_FIRST_ENGINEERING`
