# ENGÜRÜ PRODUCT & CORE MAP™

## State
HOLD — discovery in progress.

This map is the canonical inventory surface for Engürü Lab products, shared cores, governance layers, infrastructure, experiments and archives.

## Locked rule
No large repository move, delete, merge, rename or product retirement may occur before this map is completed and reviewed through Human Threshold™.

## Classification
Every discovered asset must be classified as one of:

- PRODUCT — independent user-facing/sellable product
- CORE — reusable capability used by one or more products
- GOVERNANCE — authority, evidence, language or verification layer
- INFRASTRUCTURE — deployment, billing, auth, data, tooling or platform support
- EXPERIMENT — not yet promoted to product/core status
- ARCHIVE — historical reference; not active product truth

## Required fields
For every mapped asset record:

- canonicalName
- assetType
- repository
- canonicalPath
- currentState: PASS | HOLD | BLOCKED
- productState: research | development | verified | retired
- owners / execution surface
- dependencies
- governance links
- evidence path
- production URL if any
- lastVerifiedAt
- duplicate / overlap notes
- Steward recommendation
- Human Threshold required: yes/no

## Confirmed starting points
These are discovery anchors, not a final map:

- ENGÜRÜ Builder™ — engurulabory/enguru-website-factory
- Shift Core™ — engurulabory/shift-core-api
- Artist Manager AI™ — engurulabory/artist-manager-ai
- DoneCheck™ — engurulabory/donecheck
- DoneCheck Core Foundation — engurulabory/donecheck-core-foundation
- ENGÜRÜ Lab / Labory control surface — engurulabory/Engurulaboratuvari

## Existing governance contract to preserve
Canonical Labory operating contract currently lives at:

`engurulabory/enguru-website-factory/packages/labory-operating-contract/index.mjs`

Principle ID:
`ENGURU_LABORY_CONTROL_PLANE_V1`

Until a later Human Threshold decision says otherwise, this map must reference that contract rather than duplicate or replace it.

## Discovery pass
Repository Steward™ must:

1. enumerate accessible Engürü repositories;
2. identify product, core, governance, infrastructure and archive assets;
3. detect duplicates, forks, stale names and embedded cores;
4. trace dependency relationships;
5. locate evidence / DoneCheck / Verified Finish records;
6. separate historical ideas from current product truth;
7. mark unresolved claims HOLD;
8. produce a proposed canonical topology;
9. request Human Threshold only for consequential moves, merges, deletions, renames or retirements.

## Acceptance gate
Map may move to PASS only when:

- accessible repositories have been inventoried;
- known products and shared cores have canonical records;
- duplicate/overlap report is complete;
- repository-order recommendations are evidence-linked;
- no unresolved destructive action is auto-approved;
- DoneCheck verifies map completeness against the declared inventory scope.
