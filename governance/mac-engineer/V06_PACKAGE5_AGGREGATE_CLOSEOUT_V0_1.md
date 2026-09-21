# ENGÜRÜ Mac Engineer™ v0.6 — Package 5 Aggregate Evidence + Mandatory DoneCheck™ v0.1

## STATE

IMPLEMENTED CANDIDATE — exact-head CI and post-merge exact-main verification required.

## NIYET

Close the GitHub engineering phase of v0.6 only from reconciled package evidence, locked target thresholds, zero unresolved critical failures and one executable engineering DoneCheck.

Package 5 is the GitHub engineering closure layer. It does not introduce a new Core or change runtime authority. It cannot by itself issue the product-level v0.6 VERIFIED FINAL / LOCKED judgment; Package 6 Mac Local Final Commissioning remains mandatory.

## Canonical target set

| Domain | Locked target |
|---|---:|
| Operating Character | 98–99+ field |
| Architecture Foundations | 97+ applied |
| Engineering Foundations | 98+ |
| Intellectual Depth | 97+ |
| Finished Ability | 98+ |
| Human-Centered Conversation | 97+ |
| Persistent Working Memory | 97+ |
| Unresolved critical failures | 0 |

## Score semantics

The Package 5 scores are **v0.6 internal field/applied closure scores on the previously locked rubric**.

They are not:
- an external industry ranking;
- a universal model capability score;
- a claim that every future task will perform at the same level;
- a substitute for Human Threshold or future v0.9 World-Class Field Benchmark.

The scorecard is canonical evidence at:

`evidence/mac-engineer/V06_PACKAGE5_AGGREGATE_SCORECARD.json`

Every score requires:
1. the locked target;
2. explicit evidence references;
3. an evidence-bounded basis statement;
4. no unresolved applicable HOLD.

Operating Character is additionally bound to the mean of the same locked 12 Package 1 dimensions. The aggregate value cannot be typed independently.

## Package reconciliation

Required package states:

- Package 1 — VERIFIED PASS
- Package 2A — VERIFIED AUDIT COMPLETE
- Package 2A.1 — REAL GAP REVIEW COMPLETE
- Package 2B — VERIFIED FINAL / LOCKED
- Package 2C — completed user-locked program decision; supporting Builder technical candidate remains separately truth-bounded
- Package 3 — VERIFIED FINAL / LOCKED
- Package 4 — VERIFIED FINAL / LOCKED

A supporting external-product PR is never represented as merged when it is not merged.

## Critical-failure rule

`unresolved critical failures > 0 → HOLD`

A historical failure that was reproduced, root-caused, repaired, regression-tested and reverified is recovery evidence; it is not an unresolved critical failure.

## Mandatory DoneCheck™

Final closure requires all of the following to remain PASS:

1. all v0.6 packages reconciled;
2. real implementation and real field evidence present;
3. every locked field/applied target met;
4. regression PASS;
5. canonical truth preserved;
6. authority boundaries explicit;
7. aggregate evidence present;
8. Human authority preserved;
9. unresolved critical failures = 0;
10. reported judgment aligned with current truth.

Any failed item produces HOLD.

## Current evidence-bounded scores

- Operating Character — **98.7 field**
- Architecture Foundations — **98 applied**
- Engineering Foundations — **98**
- Intellectual Depth — **98**
- Finished Ability — **99 field**
- Human-Centered Conversation — **97 field floor**
- Persistent Working Memory — **99**
- Unresolved critical failures — **0**

The detailed bases and evidence refs live in the scorecard and are executable through `assess_v06_aggregate`.

## Closure sequence

`aggregate scorecard → negative tests → Package 5 Mandatory DoneCheck™ → exact-head CI → Evidence/WORKLIST reconciliation → merge → exact-main verification → GITHUB_ENGINEERING_VERIFIED / MAC_COMMISSIONING_REQUIRED → Package 6 Mac Local Final Commissioning → v0.6 VERIFIED FINAL / LOCKED`

## NEXT ACTION

Run Package 5 tests + Mandatory DoneCheck™ inside the full Labory Final Gate. If exact-head is green, record Package 5 evidence, reconcile its engineering-closeout WORKLIST items, merge and verify exact-main. Then move directly to Package 6 Mac Local Final Commissioning; only Package 6 may unlock product-level v0.6 VERIFIED FINAL / LOCKED.
