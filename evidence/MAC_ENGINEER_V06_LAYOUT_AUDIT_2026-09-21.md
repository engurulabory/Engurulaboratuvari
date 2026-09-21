# ENGÜRÜ Mac Engineer™ v0.6 — Package 6 Mac Layout Audit

Date: 2026-09-21

## STATE

**MAC LAYOUT AUDIT — PASS**

## Summary

Observed on Mac after canonical path reconciliation:

- total findings: 15
- canonical: 8
- canonical roots: 5
- canonical children: 3
- known secondary: 7
- unknown: **0**
- stale bootstrap temp: **0**
- missing canonical: **0**
- unknown active process paths: **0**
- cleanup candidates: **0**

## Canonical paths

- control-plane: `~/Enguru/Projects/Engurulaboratuvari`
- product source: `~/Enguru/Projects/enguru-mac-engineer`
- runtime: `~/Enguru/Runtime/MacEngineer`
- installed app: `~/Applications/ENGÜRÜ Mac Engineer.app`
- Evidence: `~/Enguru/Evidence/MacEngineer`

## Known secondary paths

The following are intentional and do not constitute drift:

- `~/Desktop/ENGURU_Mac_Engineer_Project_Handoff_v1` — historical provenance source
- `~/Enguru/Backup/MacEngineer` — backup root
- `~/Enguru/Runtime/MacEngineer/App/ENGÜRÜ Mac Engineer.app` — runtime build artifact

## Active processes

Both observed Mac Engineer processes resolve to canonical execution paths:

- installed `EnguruMacEngineer` app process — CANONICAL_PROCESS
- `~/Enguru/Runtime/MacEngineer/runtime/app.py` — CANONICAL_PROCESS

## JUDGMENT

No unexplained duplicate, stale bootstrap, missing canonical path or unknown active Mac Engineer process was observed.

**Layout is clean enough to proceed to dedicated GitHub product-source publication.**

## NEXT ACTION

Publish the already verified local product-source repository:

`~/Enguru/Projects/enguru-mac-engineer`

to private GitHub:

`engurulabory/enguru-mac-engineer`

Then verify product CI on exact-main before any rebuild/install.
