# ENGÜRÜ Mac Engineer™ v0.8 — Native App Productization + Version/Provenance Contract v1

## STATE

**CANONICAL / ACTIVE — GATE 5**

## INTENT

Apply the first real v0.8 product mutation on the real ENGÜRÜ Mac Engineer™ product repository while preserving v0.7 reliability and the Gate 3 UX contract for Gate 6 implementation.

Gate 5 is limited to native productization, version identity and exact source/runtime/install provenance.

## AUTHORITIES

Execution:

> **ENGÜRÜ Mac-Native Engineering Authority™**

Machine verification:

> **DoneCheck™ v1.2 / 1.2.0 / exact-main `8b90a8fc93453dd8a84994195d28d14b15e261cb`**

Final human authority remains Human Threshold™.

## PRODUCT SOURCE BOUNDARY

Repository:

`engurulabory/enguru-mac-engineer`

Baseline exact-main:

`5432b9b135499cea18273c0e003877b864af92c6`

Working branch:

`feat/v08-native-productization-provenance`

Remote branch begins at the exact baseline. Product mutation occurs locally on the Mac under ENGÜRÜ Mac-Native Engineering Authority™.

Remote push during Gate 5 field proof: **false**.

## REQUIRED DIFFERENCE

Gate 5 applies only these product differences:

1. Native bundle source version becomes `0.8`.
2. Native preparation uses source-bound runtime synchronization instead of preserving stale installed runtime.
3. Native package carries a generated exact-source release manifest.
4. Release manifest records:
   - product repository identity;
   - product working branch;
   - exact source commit;
   - bundle version;
   - deterministic runtime source digest.
5. Installed runtime is verified against source runtime.
6. Native bundle receives local ad-hoc code signing and verification.
7. Installed app bundle version equals source bundle version.
8. Installed release manifest equals the product commit used to build it.
9. Product branch receives one bounded local commit after targeted + full regression and diff/scope verification.
10. Fresh local app launch proves runtime readiness after installation.

## EXCLUDED FROM GATE 5

Gate 5 does not implement the Gate 3 UX redesign.

Gate 5 does not claim deploy / rollback / full lifecycle acceptance.

Gate 5 does not remote-push the product mutation.

Gate 5 does not promote v0.8 to VERIFIED / LOCKED.

## EXPECTED PRODUCT MUTATION SCOPE

Only these product paths are authorized:

- `execution_prep/native_app/Info.plist`
- `execution_prep/native_app/prepare_native_app.command`
- `runtime/tests/test_v08_native_productization.py`

Any additional product path requires HOLD and fresh reconciliation.

## FIELD SEQUENCE

`EXACT MAIN → LOCAL PRODUCT BRANCH → BACKUP → MUTATE → TARGETED TEST → FULL REGRESSION → DIFF/SCOPE → LOCAL COMMIT → NATIVE PACKAGE → INSTALL → FRESH LAUNCH → READY → SOURCE/RUNTIME/INSTALLED PROVENANCE VERIFY → EVIDENCE`

## VERSION RULE

`0.8` is a v0.8 product candidate identity, not a final Verified Finish claim.

The version string proves package identity only.

The v0.8 VERIFIED / LOCKED judgment remains gated by Gates 5–12 and Human Threshold™.

## PROVENANCE RULE

Historical `PROVENANCE.json` remains historical source-composition Evidence.

Gate 5 release provenance is a separate runtime/install artifact:

`ENGÜRÜ Mac Engineer.app/Contents/Resources/release.json`

and local runtime copy:

`~/Enguru/Runtime/MacEngineer/state/release.json`

No second canonical source truth is created.

## ROLLBACK / RECOVERY

Before source mutation, the three authorized product files are copied into the Gate 5 Evidence run directory.

Git branch baseline remains the source rollback authority.

The native install script keeps the previous installed app backup during replacement and restores on activation failure.

Installed runtime synchronization keeps a recoverable previous runtime during replacement.

## PASS REQUIREMENTS

Gate 5 PASS requires all of:

- baseline exact-main verified;
- product main clean before branch creation;
- working branch exact identity verified;
- product mutation scope exactly three paths;
- targeted test PASS;
- full runtime regression PASS;
- native preparation syntax PASS;
- native Swift build PASS;
- `git diff --check` PASS;
- local product commit created;
- remote push false;
- source bundle version = `0.8`;
- installed bundle version = `0.8`;
- release manifest source commit = local product commit;
- installed runtime parity = PASS;
- local ad-hoc code-sign verification = PASS;
- fresh app launch / runtime readiness = PASS;
- Evidence written;
- DoneCheck™ v1.2 authority preserved.

## EXIT

`V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE_PASS`

Next:

`V08_EXISTING_PRODUCT_CHANGE_SCENARIO`
