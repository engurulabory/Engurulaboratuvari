# ENGÜRÜ Mac Engineer™ v0.6 — Exact-SHA Install Attempt 1 Recovery

Date: 2026-09-21

## STATE

**INSTALL ATTEMPT 1 — HOLD / RECOVERED**

## Source authority

Product source remained canonical and exact-main:

`28b901ab3303f4be3c7356b11218b62422f2da42`

Session start before the attempt: PASS.

## Field outcome

The exact-SHA rebuild/install reached post-launch verification and returned:

`INSTALLED_APP_PROCESS_REQUIRED`

The failure was in installed-app process recognition, not source/build/version/runtime parity.

The process verifier used a raw path substring for:

`~/Applications/ENGÜRÜ Mac Engineer.app`

macOS may expose the same Unicode path in a different normalization form. The layout audit had already required Unicode-normalized path comparison; the install verifier had not yet inherited that rule. A short process-readiness window is also appropriate after `open`.

## Recovery evidence

Backup:

`~/Enguru/Backup/MacEngineer/v06_exact_sha_install_20260921T195339Z`

Rollback:
- prepared: true
- used: true
- installed app restored: PASS
- runtime build app restored: PASS
- restored app relaunch: PASS

## JUDGMENT

The fail-closed + rollback contract worked in the field.

The necessary difference is limited to process verification:
- normalize macOS Unicode command paths;
- wait briefly for both installed-app and runtime processes;
- preserve all existing exact-SHA/build/backup/rollback gates.

## NEXT ACTION

Merge the process-verification correction after CI, then retry the same canonical `rebuild-install` objective.
