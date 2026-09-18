# ENGÜRÜ Quality / Release Evidence Adapter — Diff-Aware QA Contract

State: IMPLEMENTED CANDIDATE — exact-head CI required.

This contract reuses existing browser/VX1/publish evidence. It does not create another browser engine.

## Flow

`DIFF → IMPACT MAP → AFFECTED ROUTES → BROWSER EVIDENCE → CANARY → BENCHMARK → RELEASE VERDICT`

## Rules

1. Release assessment requires an explicit diff scope.
2. Visual/route changes require a deterministic path-to-route impact map.
3. Every affected route requires browser evidence.
4. Production release requires canary evidence.
5. When benchmark is required, both baseline and candidate evidence must exist.
6. Regression beyond the declared budget produces HOLD.
7. Canary/benchmark PASS does not bypass Human Threshold™ for publication.
8. Browser evidence may come from existing Builder/VX1 or approved product QA surfaces.
9. Canary evidence may come from existing Publish Engine / production verification surfaces.
10. The adapter consumes evidence; it does not duplicate upstream render, browser or deploy engines.

## Provenance

Mechanisms were informed by gstack diff-aware QA, canary and benchmark patterns. ENGÜRÜ implementation preserves existing Quality & Red Team and Release & Reliability authority.
