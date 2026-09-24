# DoneCheck™ v1.2 — Canonical Reconciliation — 2026-09-23

## STATE

**PASS — ONE PRODUCT / TWO REPOSITORIES / CURRENT CANONICAL VERSION 1.2.0**

## CLAIM

The ENGÜRÜ portfolio contains one DoneCheck product, not multiple DoneCheck products.

Repository count, version count and authority-layer count are separate dimensions.

## PRODUCT COUNT

**1 product: DoneCheck™**

## REPOSITORY COUNT

**2 repositories**

### Current canonical product / release surface

`engurulabory/donecheck`

- exact-main: `8b90a8fc93453dd8a84994195d28d14b15e261cb`
- package version: `1.2.0`
- current full-product production controls
- current machine verification implementation
- current Verified Finish runtime
- current Release Authority

### Historical controlled foundation

`engurulabory/donecheck-core-foundation`

- exact-main: `f555354fa756b47f6e83ab05248e63005b1054bf`
- preserves Working Core development lineage
- v1.0 / v1.1 development and promotion history
- not a second product
- not current full-product v1.2 authority

## VERIFIED VERSION MILESTONES

**3**

1. v1.0 — Working Core
2. v1.1 — provenance-gated Evidence Producers
3. v1.2 — Full Product Production Controls

## V1.2 EXACT-MAIN EVIDENCE

Public DoneCheck main:

`8b90a8fc93453dd8a84994195d28d14b15e261cb`

PR #9:

`DoneCheck v1.2 — close full product production controls`

Observed exact-main workflows:

- CI run `35714169933`: SUCCESS
  - lint PASS
  - typecheck PASS
  - 7 test files PASS
  - 32 tests PASS
  - build PASS
- Release Authority run `35714169911`: SUCCESS
  - merged-PR provenance PASS
  - lint/typecheck/test/build PASS
  - release authority receipt produced
- IP Model Trust Fleet run `35714170025`: SUCCESS

## V1.2 PRODUCTION CONTROLS

- append-only JSONL audit ledger
- process-safe write lock
- filesystem sync
- monotonic sequence
- duplicate event rejection
- SHA-256 hash chain
- reopen/full-chain verification
- tamper detection
- Ed25519 reviewer attestation
- decision authorization
- `recordVerifiedFinish()`
- `donecheck.verified-finish/v1` receipt
- merged-PR exact-main Release Authority

## AUTHORITY COUNT

**4 authority layers**

1. Markdown DoneCheck — read-only human projection
2. Mandatory DoneCheck JSON — structured producer Evidence contract
3. DoneCheck™ v1.2 — machine verification + production closure authority
4. Human Threshold™ — final human authority where the governing product contract requires it

## MAC ENGINEER BOUNDARY

DoneCheck™ v1.2 product readiness is **PASS**.

ENGÜRÜ Mac Engineering™ v0.7 A10 integration remains a separate acceptance gate.

A10 must prove that Mac Engineering Evidence is actually consumed through the canonical DoneCheck v1.2 verification/closure path. Product readiness cannot manufacture integration PASS.

## JUDGMENT

**DoneCheck™ v1.2 product = VERIFIED CURRENT CANONICAL AUTHORITY**

**Mac Engineer A10 integration = PENDING**

## NEXT ACTION

Proceed with Mac Repository Fabric while preserving the A10 integration gate. When A10 opens, bind the local Evidence spool and Mandatory DoneCheck JSON producer output to the exact DoneCheck v1.2 authority contract.
