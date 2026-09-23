# ENGÜRÜ Mac Engineer™ — OSi Operator Surface Preparation — 2026-09-23

## STATE

**PREPARED / LOCAL ACCEPTANCE PENDING**

## CLAIM

The existing ENGÜRÜ Mac Engineer™ architecture has been consolidated into a minimal five-command OSi operator surface without introducing a new core.

## IMPLEMENTED DIFFERENCE

Daily operator surface:

- `enguru-mac status`
- `enguru-mac continue`
- `enguru-mac verify`
- `enguru-mac recover`
- `enguru-mac doctor`

Existing canonical context sync, session continuity, ReliabilityManager, Runtime Doctor, product tests, native build and Evidence mechanisms are reused.

Added operational adapters:

- compact Evidence receipts;
- runtime latest-receipt handoff;
- local GitVault recovery mirrors;
- pending reconciliation manifest;
- online fetch + safe fast-forward when possible;
- offline cached-continuity mode;
- explicit fail-closed NEXT_ACTION registry;
- secure OSi self-hosted runner commissioning command;
- one-command OSi operator acceptance campaign.

## GITHUB / A09 STATE

Product PR #13 was moved to a three-workflow self-hosted candidate scope:

- `.github/workflows/product-ci.yml`
- `.github/workflows/v07-a09-full-regression.yml`
- `.github/workflows/v07-reliability-campaign.yml`

Current candidate:

`63dac60d39c93f3936658e8a5c8c80fb8470dfd3`

The prior local rehearsal PASS at:

`d545a6d9d5d9823da5878323022735ad7f47a80e`

remains valid historical Evidence for that exact candidate only.

The current candidate requires a fresh local rehearsal.

GitHub Actions continues to report startup failure before workflow execution, so external A09 confirmation remains HOLD.

## AUTHORITY

GitVault mirrors are recovery-only and never canonical.

Local commits are pending reconciliation until GitHub authority is restored.

Local operator verification cannot manufacture:

- V07-A09 PASS;
- DoneCheck v1.2 PASS;
- Human Threshold;
- version lock.

## NEXT ACTION

Run the one-command Mac acceptance campaign:

`zsh governance/mac-engineer/V07_OSI_OPERATOR_ACCEPTANCE.command`

Expected successful local judgment:

`LOCAL_ACCEPTANCE_PASS_EXTERNAL_GITHUB_CONFIRMATION_PENDING`
