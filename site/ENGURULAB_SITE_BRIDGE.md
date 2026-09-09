# ENGÜRÜ LAB™ — GitHub ↔ Site Bridge

## Goal
Make GitHub the product-truth source and engurulab.com the verified public display surface.

## Current state
HOLD — the live engurulab.com surface is legacy Readdy infrastructure. The replacement site will be generated with ENGÜRÜ Builder from the canonical registry after Labory and Astra acceptance gates are complete.

## Locked publication rule
A product must not appear on engurulab.com as active/sellable merely because it exists as an idea, repository, draft or legacy site card.

Public product eligibility requires all of:
1. canonical product record exists;
2. repository identity is verified;
3. productState is verified for publication;
4. DoneCheck evidence exists;
5. Verified Finish evidence exists;
6. production URL is known when web-delivered;
7. publication is clear at Human Threshold;
8. Steward confirms registry consistency.

If any required signal is missing, publication status is HOLD.

## Canonical flow
`Product repository → Product/Core Map → product-registry.json → ENGÜRÜ Builder → preview → browser QA → DoneCheck™ → Human Threshold™ → engurulab.com publish → Live Verify`

## Source hierarchy
1. Product repository = domain truth
2. `governance/ENGURU_PRODUCT_CORE_MAP_V2.json` = portfolio/topology truth
3. `site/product-registry.json` = public catalog truth
4. `site/LEGACY_PRODUCT_ALIGNMENT_V1.json` = legacy-name disposition evidence
5. ENGÜRÜ Builder = replacement production surface
6. engurulab.com = public presentation surface

The website must never become the canonical product database.

## Replacement rendering rule
ENGÜRÜ Builder reads the registry instead of hard-coding product names or counts. Product counts are derived from classification + publication state.

The replacement information architecture is:
- Verified Products
- In Development
- Planned Products
- Core Technologies
- Research / Archive
- Trust & Evidence

Only Verified Products may carry active purchase/trial/production claims.

## Legacy boundary
The current Readdy site remains live as legacy infrastructure until the Builder replacement has passed registry validation, desktop/mobile TR/EN browser QA, DoneCheck and Human Threshold.

No blank-site cutover. Replacement must be independently verifiable before publication.

## Fail-closed behavior
- unknown product → do not publish;
- legacy-only product card → archive/review, not active product;
- missing verification evidence → HOLD;
- registry/schema mismatch → BLOCKED;
- site claims more active products than registry → BLOCKED;
- stale site catalog → HOLD until replacement/correction;
- destructive repository action before required governance gates → BLOCKED.
