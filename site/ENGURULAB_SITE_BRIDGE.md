# ENGÜRÜ LAB™ — GitHub ↔ Readdy Site Bridge

## Goal
Make GitHub the product-truth source and engurulab.com the verified public display surface.

## Current state
HOLD — GitHub-side contract is defined here; the live Readdy project is not yet connected through an authenticated Readdy write/deploy channel.

## Locked publication rule
A product must not appear on engurulab.com as active/sellable merely because it exists as an idea, repository or draft.

Public product eligibility requires all of:

1. canonical product record exists;
2. repository identity is verified;
3. Labory governance manifest is valid where applicable;
4. productState = verified;
5. DoneCheck evidence exists;
6. Verified Finish evidence exists;
7. production URL is known when the product is web-delivered;
8. publication is not blocked by Human Threshold;
9. Steward confirms registry consistency.

If any required signal is missing, publication status is HOLD.

## Canonical flow

`Product repository → evidence → DoneCheck → Verified Finish → Steward registry → public catalog feed → Readdy render → browser verification → final DoneCheck`

## Source hierarchy

1. Product repository = domain truth
2. Labory operating contract = governance truth
3. ENGÜRÜ PRODUCT & CORE MAP™ = portfolio/topology truth
4. `site/product-registry.json` = public catalog truth
5. Readdy = presentation/deployment surface

Readdy must not become the canonical product database.

## Readdy integration modes

### Mode A — preferred
Readdy project consumes a generated JSON/HTTP catalog feed sourced from this repository or a deployment endpoint backed by it.

### Mode B — transitional
A release workflow exports `site/product-registry.json` and a human/agent applies the generated content to Readdy. The applied site must then be browser-verified against the same registry digest.

Mode B is acceptable only until authenticated automatic Readdy integration is available.

## Fail-closed behavior

- unknown product → do not publish;
- missing verification evidence → HOLD;
- registry/schema mismatch → BLOCKED;
- site claims more active products than registry → BLOCKED;
- stale Readdy catalog → HOLD until corrected;
- destructive repository action before map PASS → BLOCKED.

## Site sections after migration

- Verified Products
- In Development
- Core Technologies
- Research / Archive
- Trust & Evidence
- About Engürü Labory

Only Verified Products may carry purchase/trial/production claims.

## Migration boundary
The current Readdy site remains live until replacement content has passed registry validation, visual/browser QA and Human Threshold for public publication.

Do not blank the current public site before the replacement is independently verifiable.
