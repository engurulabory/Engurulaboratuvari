# ENGÜRÜ OS-R0 — Overlap & Repository Order Report v1

## STATE
HOLD — discovery complete for the declared 9-repository scope; fleet manifest alignment and final DoneCheck completeness proof remain open.

## CLAIM
The repository topology is now sufficiently mapped to separate intentional dual-repository patterns from misplaced cross-product control-plane ownership without performing destructive moves.

## EVIDENCE

### 1. Labory ↔ Builder control-plane overlap
- `engurulabory/Engurulaboratuvari` is the intended portfolio/control-plane home.
- `engurulabory/enguru-website-factory` currently contains transitional `repository-steward` and `labory-operating-contract` implementations.
- Builder now has a product-local `.enguru/labory-manifest.json`.

Decision: KEEP Builder product runtime. HOLD removal/migration of cross-product governance copies until dependency verification and fleet manifest migration close.

### 2. Builder Factory ↔ Builder Release
- Factory is product source of truth.
- `enguru-builder-release/HANDOFF_META.json` declares `sourceRepository=engurulabory/enguru-website-factory` and source SHA `39b5ff98...`.
- Release mirror therefore represents a handoff/distribution snapshot, not canonical product source.

Decision: KEEP as RELEASE_MIRROR. Refresh or archive only after Builder finalization and Human Threshold review.

### 3. DoneCheck Foundation ↔ DoneCheck public release
- `donecheck-core-foundation` README explicitly defines itself as controlled development/source repository.
- `donecheck` README explicitly identifies the public Working Core and preserves release provenance.

Decision: INTENTIONAL DUAL-REPO MODEL. Do not merge. Preserve development → promotion → public release provenance.

### 4. Shift Core ↔ DoneCheck
- Shift Core governs bounded 1–10 task shifts, task acceptance, revision, dependency impact and selective rollback.
- DoneCheck verifies evidence against success criteria and preserves final human judgment.

Decision: COMPLEMENTARY, NOT DUPLICATE. Keep independent product/core ownership.

### 5. AEC ↔ DoneCheck
- AEC declares a QA / DoneCheck Worker role and economic-finality evidence chain.
- No evidence supports merging AEC with DoneCheck.

Decision: LOGICAL GOVERNANCE DEPENDENCY only. Keep AEC independent.

### 6. Artist Manager AI
- Product is explicitly Local Beta with browser localStorage persistence.
- Production auth/database/storage/AI/payment items remain roadmap work.

Decision: KEEP as PRODUCT / HOLD for verified production claims.

### 7. Adil Pay Kanıt Web
- Repository contains only a minimal README and no implementation/evidence surface.

Decision: classify EXPERIMENT / HOLD. Do not publish as verified active product.

## Repository-order actions

### SAFE_AUTO / non-destructive
1. Maintain Labory as canonical Product & Core Map / Steward coordination repository.
2. Add missing product-local Labory manifests where the asset is an active execution-plane product/core and truth is known.
3. Add canonical pointers between controlled-source and public-release repositories.
4. Record Builder release mirror as non-canonical source.
5. Keep experiment and HOLD states out of verified public-product registry.

### REVIEW
1. Decide whether DoneCheck public release should use PRODUCT_CORE rather than PRODUCT in all public registry surfaces.
2. Decide the long-term publication role of `enguru-builder-release` after Builder final acceptance.
3. Confirm whether `adil-pay-kanit-web` remains research, is revived, or is later archived.

### HUMAN_THRESHOLD
1. Move/delete Builder's transitional cross-product governance packages.
2. Rename, merge, archive or delete any repository.
3. Change public/product publication status where commercial claims are affected.

## NEXT ACTION
Complete fleet alignment by adding/validating applicable `.enguru/labory-manifest.json` files, then run a final machine-readable map completeness check. Only after that should OS-R0 be considered for PASS and migration actions be opened.
