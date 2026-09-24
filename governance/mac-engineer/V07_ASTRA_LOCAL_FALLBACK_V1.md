# ENGÜRÜ Mac Engineering™ v0.7 — Astra Local Fallback Contract v1

## STATE

**Prepared fallback adapter for V07-A09 continuity.**

This contract extends the existing reliability and Evidence layers. It creates no new core and changes no product runtime behavior.

## CLAIM

When GitHub-hosted Actions is temporarily unavailable, Astra may execute the V07-A09 engineering campaign on the real Mac against one exact product candidate SHA and produce a Local Evidence bundle.

The local campaign is an engineering continuity proof. GitHub CI remains the external confirmation authority required by the current v0.7 acceptance matrix. GitHub-hosted compute and OSi self-hosted compute are execution choices; neither changes the Evidence authority model.

## AUTHORITY

Primary path:

`GitHub exact candidate → 5 targeted CI PASS → full regression PASS → scope validation → review → merge → exact-main`

Fallback path:

`Astra → disposable exact-SHA worktree → 5 targeted local PASS → full regression PASS → native checks → scope validation → Local Evidence`

Reconciliation:

`Local Evidence ready → GitHub Actions restored → same/equivalent accepted candidate → external CI confirmation → canonical A09 PASS decision`

A Local Evidence PASS cannot by itself manufacture `V07-A09 PASS`, `v0.7 VERIFIED`, or `v0.7 LOCKED`.

## EXECUTION BOUNDARY

Canonical control-plane repository:

- `~/Enguru/Projects/Engurulaboratuvari`

Technical product repository:

- `~/Enguru/Projects/enguru-mac-engineer`

Current A09 product branch:

- `test/v07-a09-fault-injection-campaign`

Execution uses a disposable detached Git worktree. The operator's existing product worktree remains intact.

## ACCEPTANCE

The fallback campaign records:

1. fresh `origin/main` SHA;
2. fresh A09 candidate SHA;
3. candidate is based on current main;
4. candidate scope matches the current three-file A09/self-hosted workflow change set (`product-ci` + targeted campaign + full regression);
5. targeted v0.7 reliability suite passes **5 consecutive times** on the same candidate SHA;
6. full runtime regression passes;
7. native prep syntax passes;
8. native Swift build verification passes;
9. `git diff --check` passes;
10. disposable worktree remains clean;
11. machine-readable Local Evidence JSON is written under `~/Enguru/Evidence/MacEngineer/v0.7/`.

Any inconclusive or failing gate produces `HOLD`.

## EVIDENCE AUTHORITY

Expected evidence schema:

`enguru.mac-engineer.v07-astra-local-fallback/v1`

Required judgment values:

- `LOCAL_REHEARSAL_PASS_EXTERNAL_CONFIRMATION_PENDING`
- `HOLD`

The Evidence bundle records exact SHAs, command results, targeted run count, log digests, full regression result, native verification result, scope result and authority boundary.

## HUMAN THRESHOLD

Astra may execute this read/test/build campaign locally.

Merge, version lock and final Human Threshold remain under the established canonical authority chain.

## NEXT ACTION

Run:

`zsh governance/mac-engineer/V07_ASTRA_LOCAL_FALLBACK.command`

Then return the terminal summary and generated Evidence path to the ChatGPT Project for reconciliation.
