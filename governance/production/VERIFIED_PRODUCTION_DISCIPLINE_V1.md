# ENGÜRÜ Verified Production Discipline — Harvest Contract

State: IMPLEMENTED CANDIDATE — exact-head CI required.

This extends existing Closed-Loop Production / Verified Agent Operating discipline. No new core is created.

## Runtime Guard

`allowed scope → frozen scope → destructive-operation gate → execution`

- edits outside the declared scope -> HOLD;
- frozen paths cannot be changed by the active task;
- destructive operations require Human Threshold™;
- an approval cannot expand the declared path scope.

## Systematic Debugging

Canonical order:

`REPRODUCE → CAPTURE EVIDENCE → ROOT CAUSE → HYPOTHESIS → SMALLEST EXPERIMENT → FAILING REGRESSION TEST → FIX → REVERIFY`

A patch is not accepted merely because it appears to work. Fix-before-root-cause/test and fix-without-reverify both produce HOLD.

## Worktree Isolation

Risky or parallel work requires an isolated worktree/branch surface. Isolation is an execution-safety mechanism, not a second repository authority.

## Verification Before Completion

A completion claim without verification evidence produces HOLD.

## Skill / Agent TDD

Reusable skills and agent behavior require:

- golden case;
- negative/fail-closed case;
- regression fixture.

## Provenance

Mechanisms were informed by Superpowers systematic-debugging/TDD/worktree patterns and gstack careful/freeze/guard patterns. ENGÜRÜ governance remains authoritative.
