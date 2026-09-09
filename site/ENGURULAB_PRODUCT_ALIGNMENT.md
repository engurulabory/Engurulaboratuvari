# ENGÜRÜ LAB SITE PRODUCT ALIGNMENT PASS™

## State
HOLD — registry is prepared; live engurulab.com remains unchanged until ENGÜRÜ Builder replacement, browser QA, DoneCheck™ and Human Threshold™.

## Purpose
Align the legacy engurulab.com catalog with current repository truth before rebuilding the site.

## Source truth
- Portfolio topology: `governance/ENGURU_PRODUCT_CORE_MAP_V2.json`
- Public catalog contract: `site/product-registry.json`
- Legacy 15-item decision matrix: `site/LEGACY_PRODUCT_ALIGNMENT_V1.json`

## Legacy result
The current site presents 15 Revenue Core items as one product family. The replacement catalog separates user-facing products, planned products, core technologies, internal governance capabilities and research/archive.

Decision totals:
- KEEP: 0
- RENAME: 1
- CORE: 7
- ARCHIVE: 6
- PLANNED: 1

### Locked identity changes
- `Menajer Zekî` → `Artist Manager AI™` — RENAME
- `AstroMode` → `ENGÜRÜ LAB • ASTRO MODE` — PLANNED
- `Akıllı Üretim Çekirdeği` → internal Closed-Loop Production Core capability — CORE
- `Karar ve Dil Rehberi` → internal ENGÜRÜ Language Governance™ capability — CORE

`Creator Deal Desk` has scope overlap with Artist Manager AI, but exact identity is not evidence-backed; it remains archived legacy evidence rather than a separate product or automatic rename.

## Replacement public information architecture
1. Verified Products
2. In Development
3. Planned Products
4. Core Technologies
5. Research / Archive
6. Trust & Evidence

## Current canonical product queue
1. ENGÜRÜ Builder™
2. Artist Manager AI™
3. ENGÜRÜ LAB • ASTRO MODE — planned after Artist Manager
4. Adil Pay — planned after Artist Manager

## Publication discipline
A repository, idea, old site card or legacy product name never becomes an active public product by itself. Active/sellable publication requires the registry publication gate and evidence-backed Verified Finish.

The live Readdy site remains legacy infrastructure. It is not edited by this pass.

## Builder handoff
Future site generation flow:

`Product/Core Map → product-registry.json → ENGÜRÜ Builder → preview → browser QA → DoneCheck™ → Human Threshold™ → engurulab.com publish`

Builder should read the registry rather than hard-code product names/counts. Counts must be derived by class and publication state.
