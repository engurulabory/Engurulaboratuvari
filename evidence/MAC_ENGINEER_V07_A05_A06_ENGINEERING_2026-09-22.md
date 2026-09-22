# ENGÜRÜ Mac Engineering™ v0.7 — V07-A05 / V07-A06 Engineering Evidence — 2026-09-22

## STATE

**V07-A05 — PASS / EXACT-MAIN**

**V07-A06 — PASS / EXACT-MAIN**

v0.7 remains **ACTIVE**.

## CLAIM

The existing reliability layer was minimally extended with a bounded-retry primitive. The existing watchdog remains recovery authority. Provider/network/process recovery behavior is now deterministically verified without a new core.

## EVIDENCE

Product repository: `engurulabory/enguru-mac-engineer`

Engineering PR #11:
- exact-head: `6dd92012859f77c0e70ef43d3c6833734ea82b64`
- Product CI #22 / run `35770093773`: **SUCCESS**
- runtime tests: **52 / OK**
- patch scope: `runtime/reliability.py` + `runtime/tests/test_v07_long_running_reliability.py`
- review threads: 0
- fresh review: PASS

Runtime extension:
- `BOUNDED_RETRY_POLICY.retry_limit = 2`
- `BOUNDED_RETRY_POLICY.max_attempts = 3`
- retry exception classes are explicit
- retry limit above policy fails closed
- each attempt writes durable journal receipts
- watchdog remains the stale-task recovery authority

V07-A05 exact-head:
- attempts: 3
- max attempts: 3
- over-limit fail-closed: true
- watchdog decisions: 1
- repeated watchdog findings: 0
- resulting state: `RECOVERY_REQUIRED`
- judgment: PASS

V07-A06 exact-head:
- provider unavailable: recoverable 2 attempts / exhausted 3
- network timeout: recoverable 2 attempts / exhausted 3
- child-process exit: recoverable 2 attempts / exhausted 3
- task identity continuity: true
- durable Evidence continuity: true
- judgment: PASS

Product exact-main:
- `199893b07941a82c26c3b39a7942478cb95420b0`
- Product CI #23 / run `35770247337`: **SUCCESS**
- runtime tests: **52 / OK**
- Runtime compile / native prep / native Swift build: PASS
- exact-main A05/A06 receipts reproduce the same acceptance invariants.

## REQUIRED DIFFERENCE

Completed:
- `V07-A05 BOUNDED_RETRY_WATCHDOG = PASS`
- `V07-A06 PROVIDER_NETWORK_PROCESS_RECOVERY = PASS`

No new core was required.

## JUDGMENT

**PASS — V07-A05 + V07-A06 ENGINEERING VERIFIED ON PRODUCT EXACT-MAIN**

## NEXT ACTION

`V07-A07 + V07-A08 → RESOURCE_AND_EVIDENCE_CONTINUITY → GITHUB_FIRST_ENGINEERING`
