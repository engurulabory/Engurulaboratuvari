# ENGÜRÜ Steward™ v1.2 — Full-Chain Preflight & Implementation Plan

**STATE:** PRE_EXECUTION_SIMULATION_PASS / STEWARD_V12_FIELD_HOLD  
**PROJECT:** STEWARD_V12 — existing single canonical worker  
**PREPARED:** 2026-10-09  
**PR:** #179, isolated hybrid engineering branch  
**CANONICAL OWNER:** `engurulabory/Engurulaboratuvari/steward/`

## STATE — Preflight evidence

The executable preflight `tools/hybrid_handoff/steward-v12-preflight.mjs` and adversarial tests `tools/hybrid_handoff/steward-v12-preflight.test.mjs` are now integrated into `.github/workflows/mac-engineer-hybrid-preflight.yml`.

GitHub Actions workflow run **37890575062**, job **113690346911**: completed successfully, including handoff template, previous validator adversarial checks, and new Steward full-chain simulation/adversarial suite. This is a **simulation and infrastructure acceptance** and not a live runtime, scheduled field or OSi Verified Finish PASS.

Live baseline report deliberately has **HOLD**, because current implementation is `1.1.0`, current Steward cron `23 6 */3 * *`, real scheduled-run receipt is unconfirmed, and the new OSi field acceptance has not yet occurred.

### S01–S10 coverage map

| Gate | Current executable preflight | Real v1.2 closure requirement |
|---|---|---|
| S01 | Source identity, preservation and contract baseline | fresh exact-head and real OSi worktree check |
| S02 | Version-label and behavior gate | version 1.2 only after implementation+tests |
| S03 | All three scope probes required | real scope-specific input/observation receipts |
| S04 | Exact cron + read-only permissions + real run condition | real **daily scheduled** run after approved workflow adoption |
| S05 | existing TTL and provenance assessors verified present | real ledger/input freshness and ownership graph |
| S06 | repair/reverify + scoped authority fixture | actual finding-to-safe-repair-to-reverify receipt |
| S07 | existing scorecard/self-health code present | real report with actual worker and portfolio health |
| S08 | 4 historical artifacts referenced and scope preserved | verify digests/HEAD at reuse time |
| S09 | native OSi parity acceptance required | real OSi runtime and Cockpit integration receipt |
| S10 | native finalizer/human/Progress reread required | authorized v1.2-specific Verified Finish |

### Negative-path suite

The new tests exercise identity/preservation failure, version-only promotion, subset scope, cron drift, missing scheduled receipt, stale provenance, repair scope violation, missing reverify, scorecard honesty, missing OSi receipt, wrong parity, absent human approval, absent finalizer, missing Progress reread and historical evidence scope drift. All scenarios reject an unsupported end-to-end PASS.

## CLAIM — Implement one bounded difference

**Necessary difference:** extend canonical `steward/` v1.1 worker to operationally meet v1.2 durable daily three-scope care and field proof; reuse existing freshness/graph/repair/self-health/scorecard assessors and OSi Cockpit integration.

## Integrated implementation plan (one project)

**Implementation transaction A — version & tested behavior (S02/S03/S05/S07).** Extend the existing scheduled runner to collect meaningful LABORY/PRODUCT/CORE inputs (typed ownership, evidence, health), derive truthful statuses and create one deterministic receipt. Add tests for all scopes, missing inventory, stale evidence, score-vs-gate drift and unchanged canonical ownership. Only then advance reported worker version and related tests to v1.2.

**Implementation transaction B — daily schedule and genuine cycle (S04/S06).** Align Steward workflow cadence with v1.2 contract (daily 05:17 UTC); preserve least-privilege permission; implement scoped incident/finding-repair-reverify with explicit SAFE_AUTO proof and Human Threshold routing. Ensure HOLD/BLOCKED states are visible to workflow and post-run receipt; capture a **real** scheduled run on the accepted commit. The existing Labory Final Gate has its own daily schedule; distinguish its run from the Steward worker's dedicated daily run.

**Implementation transaction C — handoff (S01/S08/S09/S10).** Pin exact source commit and artifact digest, verify four existing OSi evidence references for their original claims, test actual native Steward/Cockpit parity and safe recovery against OSi's current canonical HEAD. Bind a fresh DoneCheck, authorized Human Threshold and existing/approved versioned finalizer to independent native Progress Core verification.

**Cloudflare/D1 choice:** Separate commissioning proof is required for a 24-hour continuous service. Project acceptance authority must explicitly select daily GitHub Steward operations versus continuous Cloudflare commissioning (or both) before the release gate. A real **24 distinct hourly windows** evidence obligation applies to the Cloudflare 24/7 claim.

## PRESERVATION & EXECUTION BOUNDARIES

`CURRENT_OSI_CONTROL_HEAD=a056fd29f5a12f302216628e638a614640ff0d4e` (snapshot; refresh before execution)  
`CURRENT_OSI_PRODUCT_HEAD=26925c21c7816a90edc0eb047382aba8c696764c` (snapshot; refresh before execution)  
`CONTROL_WORKTREE_UNRELATED_EDITS=PRESERVED` (8 modified paths at snapshot)  
`STEWARDSHIP_CORE_COUNT=1`  
`SOURCE_REUSE=REQUIRED`  
`HISTORICAL_RECEIPTS=PRESERVED_IN_ORIGINAL_SCOPE`  
`IMPLEMENTATION_AUTHORITY=ISOLATED_GITHUB_BRANCH`  
`OSi_FIELD_STATE=HOLD`  
`VERIFIED_FINISH=HOLD`

## EVIDENCE / JUDGMENT / NEXT ACTION

**EVIDENCE:** CI preflight run 37890575062 SUCCESS; S01–S10 fixtures and negative cases PASS; baseline and actual product remain HOLD.

**JUDGMENT:** full-chain **pre-execution model** is ready for engineering. Native and schedule field facts retain their actual gate authority. A simulated `READY_FOR_FINAL_EXECUTION` fixture is an acceptance-path test and cannot be used as evidence of real readiness.

**NEXT ACTION:** `STEWARD_V12_ONE_BOUNDED_IMPLEMENTATION`: reuse worker hardening and scheduled-cycle source, produce exact S02–S07 code changes in one reviewable diff, run Steward unit/negative tests and repository CI, and then proceed to real scheduled and OSi field acceptance. Record GitHub and OSi claims separately.

**ENGÜRÜ rule:** 1 Ana Hedef = 1 Proje → 1 Uçtan Uca Ön Analiz ve Simülasyon → 1 Bütünleşik Yürütme → 1 Doğrulanmış Teslim.
