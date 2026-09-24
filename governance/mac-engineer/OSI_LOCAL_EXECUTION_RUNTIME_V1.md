# ENGÜRÜ Mac Engineer™ — OSi Local Execution Runtime & Operator Surface v1

## STATE

This package consolidates existing ENGÜRÜ Mac Engineer™ capabilities into one minimal operator surface. It introduces no new core.

## PRODUCT / RUNTIME DISTINCTION

**ENGÜRÜ Mac Engineer™** is the engineering operator product.

**OSi Local Execution Runtime** is the Mac-local execution substrate used by the product.

The product identity remains portable; OSi is the current native execution plane.

## DAILY OPERATOR SURFACE

```text
enguru-mac status
enguru-mac continue
enguru-mac verify
enguru-mac recover
enguru-mac doctor
```

### status

Reads canonical state, local Git truth, current HOLD/NEXT_ACTION, runner readiness and offline reconciliation state.

### continue

Runs Canonical Session Boot, reads the single canonical NEXT_ACTION and dispatches only an explicitly registered bounded handler.

Unknown actions fail closed as HOLD.

### verify

Runs local product compile, full runtime regression, native syntax/build verification, diff validation and a local Mandatory DoneCheck receipt.

Local verification cannot manufacture a version lock or replace DoneCheck v1.2.

### recover

Uses the existing ReliabilityManager task/checkpoint/LKG contract to recover the latest interrupted task when recovery Evidence supports it.

### doctor

Checks the existing product Runtime Doctor, local GitVault mirrors, offline reconciliation state and self-hosted runner readiness.

## CANONICAL SESSION BOOT

The existing control-plane surfaces remain authoritative:

- `CURRENT_STATUS.md`
- `SESSION_STATE_V1.json`
- `PRODUCT_ROADMAP_V1.json`
- `WORKLIST.md`
- existing `mac_engineering_sync_context.py`
- existing `mac_engineer_session_continuity.py`

The operator reuses these surfaces. It does not create a second session model.

## EVIDENCE SPOOL

Every operator command writes:

- machine-readable JSON;
- compact text receipt;
- stable `latest-receipt.json`;
- stable `latest-receipt.txt`.

Location:

`~/Enguru/Evidence/MacEngineer/operator/`

Compact receipt contract:

```text
STATE=
COMMAND=
COMPLETED=
EVIDENCE=
HOLD=
NEXT_ACTION=
RECEIPT=
```

This is the normal handoff surface for ChatGPT Project sessions.

## OFFLINE CONTINUITY

Local recovery mirrors:

- `~/Enguru/GitVault/MacEngineer/Engurulaboratuvari.git`
- `~/Enguru/GitVault/MacEngineer/enguru-mac-engineer.git`

Authority:

`RECOVERY_MIRROR_NOT_CANONICAL`

Local commits ahead of `origin/main` are recorded as pending reconciliation. They preserve engineering continuity and become canonical only after explicit GitHub reconciliation.

Thus GitHub unavailability does not stop engineering, while two competing truths are avoided.

## SELF-HOSTED CI

Preferred labels:

```text
self-hosted
macOS
ARM64
enguru-mac
```

GitHub remains PR/check/merge authority when Actions execution is available.

OSi supplies compute.

If the GitHub account-level Actions service is unavailable, local engineering continues through OSi + Evidence and later reconciles.

## AUTHORITY

`Canonical state → one NEXT_ACTION → OSi execution → Evidence → local DoneCheck → GitHub reconciliation → DoneCheck v1.2 → Human Threshold`

No operator command may promote an inconclusive result to PASS.

## HUMAN EXPERIENCE TARGET

A normal session should require only:

```text
Mac Engineer devam.
```

and, when local execution is needed:

```text
enguru-mac continue
```

Long historical prompts are no longer part of the operating contract.
