# ENGÜRÜ Mac Engineer™ v0.6 — Package 6 Historical Provenance Reconciliation

Date: 2026-09-21

## STATE

**HISTORICAL PROVENANCE CONTINUITY — PASS**

**CANONICAL SOURCE INTAKE — HOLD / REVIEW REQUIRED**

## Canonical GitHub state observed on Mac

- HEAD: `087cc4b960c5b2f84eabfa25adde47c3b0e4634a`
- origin/main: same
- branch: `main`
- worktree: clean

## Historical source/build chain

Observed:

- source root: `~/Desktop/ENGURU_Mac_Engineer_Project_Handoff_v1`
- baseline: `baseline_v0.4`
- native build receipt: `~/Enguru/Evidence/MacEngineer/native_app_prepare_20260920T082338Z.txt`
- Phase‑1 DoneCheck evidence: `~/Enguru/Evidence/MacEngineer/phase1_donecheck_20260920T095119Z.json`

## Current installed app

- path: `~/Applications/ENGÜRÜ Mac Engineer.app`
- bundle id: `com.engurumaya.macengineer`
- version: `0.4`
- executable: `EnguruMacEngineer`
- executable size: `192784`
- executable SHA‑256: `168d9560148bb61e20b05aa7abea2a0546f7b23568551e8724997fd2e2c5c784`

## Runtime reconciliation

Current runtime root:

`~/Enguru/Runtime/MacEngineer/runtime`

Comparison:

- runtime files scanned: **26**
- exact source matches: **13**
- same-name / hash-different: **8**
- runtime-only / unmatched: **5**
- exact ratio: **0.50**

## Interpretation

The historical source/build/runtime chain is real and evidence-backed.

The 50% exact match ratio proves continuity, but also proves the current runtime has evolved beyond the original handoff snapshot. Therefore a blind source import would risk replacing verified local evolution with stale code.

## JUDGMENT

- Historical source package exists — PASS
- Baseline v0.4 exists — PASS
- Build receipt exists — PASS
- Phase‑1 DoneCheck evidence exists — PASS
- Current app identity exists — PASS
- Current runtime continuity to historical source — PASS
- Current runtime fully identical to historical source — NO
- Canonical GitHub source intake — HOLD until source hygiene + runtime delta authority review

## NEXT ACTION

Run Package 6 source intake hygiene review. Identify safe source files, native Swift source, sensitive material, excluded binaries/caches, and the exact 8 divergent + 5 runtime-only files. Then choose the authoritative version per delta before canonical GitHub intake.
