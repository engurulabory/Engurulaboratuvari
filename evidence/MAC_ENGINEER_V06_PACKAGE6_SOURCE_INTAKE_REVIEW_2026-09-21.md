# ENGÜRÜ Mac Engineer™ v0.6 — Package 6 Source Intake Review

Date: 2026-09-21

## STATE

**SOURCE HYGIENE — PASS**

**RUNTIME DELTA AUTHORITY — HOLD / REVIEW REQUIRED**

## Observed source intake review

Historical source root:

`~/Desktop/ENGURU_Mac_Engineer_Project_Handoff_v1`

Results:

- safe source files: **97**
- native Swift source files: **1**
- excluded files: **5**
- app bundles inside source intake: **0**
- secret/sensitive findings: **0**

Runtime comparison:

- total runtime files: **26**
- exact source matches: **13**
- divergent same-name/hash-different: **8**
- runtime-only: **5**

Divergent runtime files:

1. `repair.py`
2. `repo_manager.py`
3. `app.py`
4. `steward_handshake.py`
5. `local_ci.py`
6. `support_repair_loop.py`
7. `governance.py`
8. `static/index.html`

Runtime-only files:

1. `reliability.py`
2. `field_reliability.py`
3. `tests/test_operating_character.py`
4. `tests/test_steel_operating_character.py`
5. `tests/test_reliability.py`

## Interpretation

The source package is clean enough for governed intake: one native Swift source exists, no secret finding was observed, and no app bundle would be imported.

However, the current active runtime contains thirteen later field deltas. Those deltas must not be replaced by the older baseline merely because the baseline is the historical source.

## Authority rule

**Mevcut hakikat + gerekli fark**

For files that differ from or postdate the historical baseline:

- historical handoff = baseline/native-source evidence;
- currently active runtime = current field-truth candidate;
- runtime delta becomes technical authority candidate only when the current runtime compiles and its current runtime test suite PASSes;
- canonical GitHub source intake remains a separate step after that review.

## NEXT ACTION

Run `python3 tools/mac_engineer_delta_authority_review.py` on the Mac. If runtime compile + runtime tests PASS, preserve the thirteen verified field deltas as runtime authority candidates for canonical intake.
