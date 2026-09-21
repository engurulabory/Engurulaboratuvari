# ENGÜRÜ Mac Engineer™ v0.6 — Package 6 Runtime Delta Authority

Date: 2026-09-21

## STATE

**RUNTIME DELTA AUTHORITY — PASS**

## Mac exact-main

- Labory local HEAD: `2b61adfc2cfae204b2b05d7f5dcc7c5a635409a7`
- origin/main: same
- worktree: clean

## Verification

Current runtime authority review:

- compile: **PASS**
- runtime tests: **PASS**
- test return code: `0`
- review targets: **13**
- runtime authority candidates: **13**

Verified current-field authority candidates:

1. `repair.py`
2. `reliability.py`
3. `repo_manager.py`
4. `app.py`
5. `field_reliability.py`
6. `steward_handshake.py`
7. `local_ci.py`
8. `support_repair_loop.py`
9. `governance.py`
10. `tests/test_operating_character.py`
11. `tests/test_steel_operating_character.py`
12. `tests/test_reliability.py`
13. `static/index.html`

## Authority judgment

Historical handoff remains baseline/native-source evidence.

For these thirteen files, the active Mac runtime is the verified current-field source candidate because:

- it is the observed active runtime;
- compile PASS;
- runtime tests PASS;
- delta authority review returned PASS;
- no privilege/authority expansion is implied.

This judgment does not make Runtime itself canonical source. The verified deltas must now be promoted into a dedicated product-source checkout/repository.

## NEXT ACTION

Bootstrap `~/Enguru/Projects/enguru-mac-engineer` from:

`historical safe source + verified current-field delta overrides`

Then establish dedicated private GitHub product source `engurulabory/enguru-mac-engineer`, verify product exact-main CI, and rebuild/install from that exact source SHA.
