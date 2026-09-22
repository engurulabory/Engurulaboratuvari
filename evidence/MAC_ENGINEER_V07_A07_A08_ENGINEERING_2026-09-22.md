# ENGÜRÜ Mac Engineering™ v0.7 — V07-A07 / V07-A08 Engineering Evidence — 2026-09-22

## STATE

**V07-A07 — PASS / EXACT-MAIN**

**V07-A08 — PASS / EXACT-MAIN**

v0.7 remains **ACTIVE**. This record does not assert v0.7 Verified / Locked.

## CLAIM

The current product exact-main proves resource/artifact discipline and structured Evidence continuity across repeated restart without a production runtime change.

## EVIDENCE

Repository:

- `engurulabory/enguru-mac-engineer`

Product PR #12:

- title: `Mac Engineer v0.7 — prove A07/A08 resource and Evidence continuity`
- base: `199893b07941a82c26c3b39a7942478cb95420b0`
- final exact-head: `e90dace0e34c68af5cec28599ee94a5ddfad0a43`
- patch scope: exactly one test file
- production runtime code changed: **false**
- review threads: **0**
- fresh review: **PASS / no blocking finding**

Initial exact-head CI:

- run #24 / `35770750418`
- result: **FAIL**
- root cause: fixture checkpoint count matched both ordinary `task_*.json` and `.lkg.json`, producing 80 instead of the expected 40
- production runtime defect: **not observed**
- required difference: count ordinary checkpoints separately from LKG checkpoint copies

Corrected exact-head CI:

- run #25 / `35770832924`
- conclusion: **SUCCESS**
- runtime regression: **54 / 54 OK**
- Runtime compile: PASS
- Runtime tests: PASS
- Native prep syntax: PASS
- Native Swift build verification: PASS

V07-A07 exact-head receipt:

- governed tasks: **40**
- artifact scope: `CANONICAL_DURABLE_ONLY`
- unexpected artifacts: **0**
- temp/cache artifacts: **0**
- durable bytes: **128229**
- cleanup: verified
- judgment: **PASS**

V07-A08 exact-head receipt:

- checkpoints: **20**
- restarts: **20**
- canonical task identity: preserved
- lineage verified: **true**
- journal reconciled: **true**
- manifest digest: `fe903cd99ed45556f71f05ff45330dce6cd77299ea362b97a00e526132ea12ac`
- judgment: **PASS**

### Exact-main acceptance

Merge / current product exact-main:

- `5432b9b135499cea18273c0e003877b864af92c6`

Exact-main Product CI:

- run #26 / `35770981787`
- conclusion: **SUCCESS**
- runtime regression: **54 / 54 OK**

V07-A07 exact-main receipt:

- governed tasks: **40**
- artifact scope: `CANONICAL_DURABLE_ONLY`
- unexpected artifacts: **0**
- temp/cache artifacts: **0**
- durable bytes: **128231**
- judgment: **PASS**

V07-A08 exact-main receipt:

- checkpoints: **20**
- restarts: **20**
- lineage verified: **true**
- journal reconciled: **true**
- manifest digest: `43c204d93bb8fd32b1a19f76bdc54087922afcb2905c8bfe830e5a6030e13c0a`
- judgment: **PASS**

Digest values may vary across independent executions because generated task identities are unique per run. The acceptance invariant is canonical identity continuity within each chain, ordered checkpoint/restart linkage, journal reconciliation and machine-verifiable manifest construction.

## REQUIRED DIFFERENCE

Completed:

- `V07-A07 RESOURCE_DISCIPLINE = PASS`
- `V07-A08 EVIDENCE_CONTINUITY_ACROSS_RESTART = PASS`

No new core was required.

## JUDGMENT

**PASS — V07-A01…A08 ENGINEERING VERIFIED ON PRODUCT EXACT-MAIN**

## NEXT ACTION

`V07-A09 → GITHUB_CI_FAULT_INJECTION_CAMPAIGN → FIVE_CONSECUTIVE_TARGETED_PASS_RUNS → FULL_PRODUCT_REGRESSION → SCOPE_VALIDATION`
