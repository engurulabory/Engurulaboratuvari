# ENGÜRÜ Mac Engineer™ — Current Status

**Updated:** 2026-09-22  
**Program target:** ENGÜRÜ Mac Engineering™ v1.1 — Verified Product Engineering Operator  
**Current version:** v0.6 — VERIFIED FINAL / LOCKED  
**Current objective:** v0.7 — Long-Running Reliability  
**Canonical objective id:** `V0_7_LONG_RUNNING_RELIABILITY`

## CURRENT ENGINEERING TRUTH

ENGÜRÜ Mac Engineer™ v0.6 is **VERIFIED FINAL / LOCKED**.

Local field truth, canonical reconciliation, merge provenance and control-plane exact-main acceptance are all complete. Recovery, fixture repair, local field acceptance and v0.6 closure are closed truths.

## CLAIM

The v0.6 product, installed Mac runtime, real task continuity and bounded recovery path have all been independently verified on the real Mac.

The next engineering model is now locked as **GitHub-first / Milestone-Mac**:

- GitHub is the primary engineering production plane.
- ChatGPT Project sessions orchestrate canonical engineering work.
- ENGÜRÜ Mac Engineer™ is the local field executor and Evidence producer.
- Mac commissioning occurs at version/milestone gates rather than after every small engineering change.

## EVIDENCE

### Product authority
- Product repository: `engurulabory/enguru-mac-engineer`
- Product exact-main: `7f2e22994d17b913f226eb05691d934f81e1c212`
- Product exact-main CI: PASS
- Installed/runtime app version: 0.6
- Runtime source parity: 34/34 EXACT
- Runtime/App provenance: PASS
- CONTINUITY_PATCH_REPEATABILITY: VERIFIED PASS

### Real field acceptance
- Canonical task: `ENGURU-V06-FIELD-001`
- Checkpoint: `v06-field-cp-001`
- Fixture HEAD: `f563a779f6d01a46e037e4330383c3adb032d426`
- Real Mac task: **7/7 VERIFIED PASS**
- Controlled failure observed: true
- Root cause: `controlled_bounded_fault_marker_block`
- Bounded correction: `remove_exact_bounded_fault_marker_block`
- Fresh regression: 1/1 PASS
- Working difference after recovery: `CURRENT_STATE.md`
- Authority preserved: true
- Recovery Evidence contract: PASS
- Verifier non-mutation: PASS

### Local closeout artifacts
- `~/Enguru/Evidence/MacEngineer/package6-bounded-recovery-latest.json`
- `~/Enguru/Evidence/MacEngineer/agent-ledger.jsonl`
- `~/Enguru/Evidence/MacEngineer/v0.6/package6-local-evidence-bundle.json`
- `~/Enguru/Evidence/MacEngineer/v0.6/package6-mandatory-donecheck.json`
- Local Evidence Bundle: VERIFIED PASS
- Mac Local Mandatory DoneCheck™: PASS

## DONECHECK AUTHORITY

Canonical authority separation:

1. Markdown DoneCheck = human-readable read-only projection.
2. Mandatory DoneCheck JSON = structured Evidence contract / producer output.
3. DoneCheck v1.2 = machine verification and production closure authority.
4. Human Threshold™ = final human authority.

Canonical document: `governance/mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md`.

## WORKING MODEL

Canonical document: `governance/mac-engineer/GITHUB_FIRST_MILESTONE_MAC_WORKING_MODEL_V1.md`.

Permanent direction:

`GitHub engineering → exact-main → milestone Mac commissioning → local Evidence → DoneCheck v1.2 → Human Threshold → version lock`

## HISTORICAL LINEAGE

**V00_V03_HISTORICAL_RECONSTRUCTION = PASS / CLOSED.**

Fresh Git/Evidence reconstruction supports one collective **PRE-CANONICAL DEVELOPMENT LINEAGE** for v0.0–v0.3. Separate retrospective release boundaries and product titles remain unasserted.

The first Evidence-backed named product boundary is **v0.4**. By the 2026-09-20 build/DoneCheck sequence, canonical provenance records contain:

- historical source: `~/Desktop/ENGURU_Mac_Engineer_Project_Handoff_v1`;
- baseline: `baseline_v0.4`;
- native build receipt: `native_app_prepare_20260920T082338Z.txt`;
- Phase-1 DoneCheck: `phase1_donecheck_20260920T095119Z.json`.

Dedicated product Git authority begins later at root commit `3ac09bd7d022a6114b9066afca14ff170e0177c1` with Product CI run `35640369690` PASS.

Canonical reconstruction Evidence:

- `evidence/MAC_ENGINEER_V00_V03_HISTORICAL_RECONSTRUCTION_2026-09-22.md`

v0.4, v0.5 and v0.6 locked truths remain unchanged.

## CURRENT OBJECTIVE

**v0.7 — Long-Running Reliability**

First required difference **PASS**: exact v0.7 acceptance matrix is canonical at `governance/mac-engineer/V07_LONG_RUNNING_RELIABILITY_ACCEPTANCE_MATRIX_V1.md`, with Evidence at `evidence/MAC_ENGINEER_V07_ACCEPTANCE_MATRIX_2026-09-22.md`.

V07-A01 + V07-A02 **PASS / exact-main verified**: product PR #9 merged to `443fd4455b6c2f095c7944ee7bc00445d96d2d2a`; exact-main Product CI run #19 PASS with 48/48 runtime tests OK. Canonical Evidence: `evidence/MAC_ENGINEER_V07_A01_A02_ENGINEERING_2026-09-22.md`.

V07-A03 + V07-A04 **PASS / exact-main verified**: product PR #10 merged to `1dcbc795e4b949448206fbad93b239aca297cc0f`; exact-main Product CI run #21 PASS with 50/50 runtime tests OK. Canonical Evidence: `evidence/MAC_ENGINEER_V07_A03_A04_ENGINEERING_2026-09-22.md`.

V07-A05 + V07-A06 **PASS / exact-main verified**: product PR #11 merged to `199893b07941a82c26c3b39a7942478cb95420b0`; exact-main Product CI run #23 PASS with 52/52 runtime tests OK. Canonical Evidence: `evidence/MAC_ENGINEER_V07_A05_A06_ENGINEERING_2026-09-22.md`.

V07-A07 + V07-A08 **GitHub-first acceptance PASS / Mac acceptance pending**: Product PR #12 merged to `5432b9b135499cea18273c0e003877b864af92c6`; exact-main Product CI run #26 PASS with 54/54 runtime tests OK. A07 confirms canonical-durable-only artifact scope with 0 unexpected/temp/cache residue. A08 confirms 20 checkpoint + 20 restart Evidence lineage and journal reconciliation. The ≥8h/RSS and Local Evidence bundle requirements remain reserved for consolidated Mac commissioning. Canonical Evidence: `evidence/MAC_ENGINEER_V07_A07_A08_ENGINEERING_2026-09-22.md`.

V07-A09 **HOLD — external GitHub-hosted Actions execution gate**. Product PR #13 campaign remains 0/5. Jobs on `macos-latest`, explicit `macos-15`, and `ubuntu-latest` were created but failed before any workflow step (`steps=null`). No production-code defect is evidenced. Canonical Evidence: `evidence/MAC_ENGINEER_V07_A09_ACTIONS_HOLD_2026-09-22.md`.

Astra local fallback **PREPARED**: governed contract `governance/mac-engineer/V07_ASTRA_LOCAL_FALLBACK_V1.md`, runnable command `governance/mac-engineer/V07_ASTRA_LOCAL_FALLBACK.command`, and field prompt `governance/mac-engineer/V07_ASTRA_LOCAL_FALLBACK_PROMPT.md`. This path can produce local engineering Evidence while A09 remains HOLD until external GitHub CI confirmation.

Current required difference: clear the private-repository GitHub Actions execution gate through read-only billing/usage + Actions policy inspection, then resume PR #13 on an exact candidate head.

## REMAINING v0.6 CLOSEOUT

**NONE — v0.6 VERIFIED FINAL / LOCKED.**

Canonical closeout:
- PR #165 merged.
- control-plane exact-main: `777904a957dfd475713dfd5de7b499c88247f4de`
- ENGURU Labory Final Gate push run #366: PASS
- IP Model Trust Gate push run #385: PASS
- IP Model Trust Fleet push run #370: PASS

The next active objective is v0.7 Long-Running Reliability.

## MAINTENANCE RULE

CURRENT_STATUS is updated after every material engineering package or PASS / HOLD / BLOCKED result, **before the next action**. Required reconciliation fields remain: COMPLETED_OR_CHANGED_WORK, LATEST_EVIDENCE, JUDGMENT, CURRENT_OBJECTIVE, REMAINING_WORK and NEXT_ACTION.

## JUDGMENT

**v0.6 LOCAL FIELD CLOSEOUT = VERIFIED PASS.**

**v0.6 VERIFIED FINAL / LOCKED = PASS.**

**V00_V03_HISTORICAL_RECONSTRUCTION = PASS / CLOSED.**

Recovery, fixture repair, local field acceptance and the reconstructed pre-canonical boundary are closed truths and reopen only when new contradictory Evidence materially changes current truth.

## NEXT ACTION

`V0_7_LONG_RUNNING_RELIABILITY → V07-A09 HOLD_GITHUB_PRIVATE_REPO_HOSTED_ACTIONS_EXECUTION_GATE → HUMAN READ-ONLY ACTIONS/BILLING INSPECTION → RESUME PR #13 → 5 TARGETED PASS → FULL REGRESSION → SCOPE VALIDATION`
