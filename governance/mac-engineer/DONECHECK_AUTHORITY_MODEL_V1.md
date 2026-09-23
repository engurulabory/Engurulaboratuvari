# ENGÜRÜ Mac Engineer™ — DoneCheck Authority Model v1

## STATE

**CANONICAL / LOCKED — reconciled to DoneCheck™ v1.2 on 2026-09-23**

## PRODUCT IDENTITY

There is **one DoneCheck product**.

Canonical product:

**DoneCheck™ v1.2**

Current canonical active product / release repository:

`engurulabory/donecheck`

Exact-main verified product SHA:

`8b90a8fc93453dd8a84994195d28d14b15e261cb`

Historical controlled foundation repository:

`engurulabory/donecheck-core-foundation`

The foundation repository preserves the v1.0/v1.1 Working Core development lineage. It is not a second DoneCheck product and is not the current full-product v1.2 source of truth.

## VERIFIED VERSION LINEAGE

### v1.0 — Working Core

Established the deterministic provider-neutral verification domain:

`task → success criteria → AI output → evidence → verification → human review`

### v1.1 — Provenance-Gated Evidence Producers

Added producer provenance and trusted-producer policy while preserving deterministic verification semantics.

### v1.2 — Full Product Production Controls

Current canonical version.

Adds:

- durable append-only JSONL audit ledger;
- SHA-256 hash chaining and tamper detection;
- Ed25519 reviewer authentication;
- per-reviewer decision authorization;
- `recordVerifiedFinish()`;
- Verified Finish receipt;
- merged-PR exact-main Release Authority.

## EXACT-MAIN EVIDENCE

DoneCheck v1.2 PR #9:

`DoneCheck v1.2 — close full product production controls`

Merged to canonical main before exact-main:

`8b90a8fc93453dd8a84994195d28d14b15e261cb`

Observed exact-main verification on 2026-09-22:

- CI run `35714169933`: **SUCCESS**
- 7 test files: **PASS**
- 32 tests: **PASS**
- lint: **PASS**
- typecheck: **PASS**
- build: **PASS**
- Release Authority run `35714169911`: **SUCCESS**
- merged-PR provenance gate: **PASS**
- release receipt creation: **PASS**
- IP Model Trust Fleet run `35714170025`: **SUCCESS**

## AUTHORITY STACK

### 1. Markdown DoneCheck

Role: **human-readable read-only projection**.

It renders:

`STATE → CLAIM → EVIDENCE → JUDGMENT / NEXT ACTION`

It does not create verification authority.

### 2. Mandatory DoneCheck JSON

Role: **structured producer Evidence contract**.

It records completion questions, evidence references, freshness and authority preservation.

A producer-level PASS is Evidence supplied to DoneCheck; it is not Verified Finish.

### 3. DoneCheck™ v1.2

Role: **machine verification + production closure authority**.

It owns:

- deterministic criterion verification;
- fail-closed `pass / fail / inconclusive`;
- evidence provenance validation;
- durable tamper-evident audit history;
- authenticated / authorized human-review verification;
- Verified Finish receipt production;
- exact-main Release Authority receipt production.

### 4. Human Threshold™

Role: **final human authority**.

Human Threshold owns explicit final acceptance and any irreversible external authority reserved for a human.

## CANONICAL FINISH CHAIN

`Producer Evidence → Mandatory DoneCheck JSON → DoneCheck™ v1.2 verification → authenticated/authorized Human Review → durable audit → Verified Finish receipt → Human Threshold where the product contract requires explicit final human authority`

Markdown is a read-only projection over this chain.

## REPOSITORY MODEL

### `engurulabory/donecheck`

**CURRENT CANONICAL PRODUCT / RELEASE SURFACE**

- version: `1.2.0`
- active machine authority implementation;
- production controls;
- Verified Finish runtime;
- Release Authority;
- exact-main verified.

### `engurulabory/donecheck-core-foundation`

**HISTORICAL CONTROLLED FOUNDATION / DEVELOPMENT LINEAGE**

- v1.0 Working Core preparation;
- v1.1 provenance development lineage;
- retained for provenance, history and controlled reference;
- does not create a second DoneCheck authority;
- cannot override the current v1.2 product repository.

## MAC ENGINEER INTEGRATION

ENGÜRÜ Mac Engineering™ consumes DoneCheck v1.2 rather than implementing a second verifier.

Mac Engineering producers emit structured Evidence.

Milestone closure chain:

`OSi / Mac Engineering Evidence → Mandatory DoneCheck JSON → DoneCheck v1.2 → Human Threshold → version lock`

The local Mandatory DoneCheck artifact remains a producer contract, not a substitute for DoneCheck v1.2.

## COUNTING RULE

When reporting DoneCheck inventory:

- **Products:** 1
- **Repositories:** 2
- **Verified version milestones:** 3 (`v1.0`, `v1.1`, `v1.2`)
- **Authority layers:** 4 (Markdown projection, Mandatory JSON producer contract, DoneCheck v1.2 machine authority, Human Threshold)

This counting rule prevents repository count, version count and authority-layer count from being confused.

## LANGUAGE GOVERNANCE

Claims remain distinct from Evidence.

Every higher authority earns its own PASS from its own acceptance contract.
