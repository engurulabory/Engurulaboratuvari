# ENGÜRÜ Mac Engineer™ — DoneCheck Authority Model v1

## STATE

**CANONICAL / LOCKED**

## NIYET

Keep one verification authority while preserving readable human summaries, structured evidence and final human authority.

## AUTHORITY STACK

### 1. Markdown DoneCheck

Role: **human-readable read-only projection**.

It renders current State, Claim, Evidence, Judgment and Next Action for people.

It does not create a second verification authority.

### 2. Mandatory DoneCheck JSON

Role: **structured Evidence contract / producer output**.

It records completion questions, evidence references, freshness and authority preservation in a machine-readable form.

A PASS inside this producer record is evidence about the producer contract; production-level Verified Finish remains a higher authority decision.

### 3. DoneCheck v1.2

Role: **machine verification and production closure authority**.

Canonical public surface: `engurulabory/donecheck`.

Relevant v1.2 controls:
- deterministic verification;
- provenance-gated evidence handling;
- durable tamper-evident audit ledger;
- reviewer authentication and authorization;
- Verified Finish receipt;
- Release Authority for merged-PR exact-main provenance.

### 4. Human Threshold™

Role: **final human authority**.

Human Threshold™ owns final acceptance, irreversible external authority, credentials, payment/publication authority and other explicitly human decisions.

## CANONICAL CHAIN

`Producer Evidence → Mandatory DoneCheck JSON → DoneCheck v1.2 verification → Human Threshold™ → Verified Finish`

Markdown is a projection over this chain.

## MAC ENGINEER v0.6 BOUNDARY

The v0.6 local Mandatory DoneCheck JSON is accepted as structured closeout Evidence:

`~/Enguru/Evidence/MacEngineer/v0.6/package6-mandatory-donecheck.json`

The v0.6 Local Evidence Bundle is:

`~/Enguru/Evidence/MacEngineer/v0.6/package6-local-evidence-bundle.json`

From v0.7 onward, milestone closure integrates these producer artifacts with DoneCheck v1.2 as the machine verification authority.

## LANGUAGE GOVERNANCE

`STATE → CLAIM → EVIDENCE → JUDGMENT / NEXT ACTION`

Claims remain distinct from Evidence. Every higher authority earns its own PASS from its acceptance contract.
