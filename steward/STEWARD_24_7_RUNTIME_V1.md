# ENGÜRÜ LABORY STEWARD™ — DURABLE RUNTIME CONTRACT v1.1

## Objective
Keep Labory repository truth, security, topology and evidence current without depending on the user's device.

## Cadence
### On every pull request and push to main
Run the complete Labory Final Gate:
- System Truth / Product-Core Map / Registry consistency;
- IP & Model Trust tests;
- Secret Zero / Fleet Gate;
- Repository Steward tests;
- repository hygiene and conflict-marker checks.

### Approximately every 3 days
Run the same gate as a scheduled Steward cycle and inspect:
- newly visible or missing repositories;
- stale Product/Core Map records;
- registry drift;
- release-mirror drift;
- security/config drift;
- unresolved HOLD/BLOCKED findings;
- next action.

### Manual
`workflow_dispatch` may run the Steward cycle at any time before a consequential decision.

## Why this cadence
Labory repository governance does not require hourly polling. PR/push gates protect changes immediately; the periodic cycle detects external drift with lower operational complexity.

## Write discipline
The scheduled cycle is read-only by default. SAFE_AUTO changes are proposed through a branch/PR. Repository delete/rename/merge/archive, publication, payment, legal and other high-impact actions remain Human Threshold™.

## Evidence
GitHub Actions run history is the durable scheduler evidence. Each run must expose PASS/HOLD/BLOCKED through logs and job state. Missing or failed runs never count as PASS.

## Failure behavior
Any failed security, consistency or Steward check → HOLD/BLOCKED. The next action is repair through an isolated branch; no silent bypass.

## Runtime PASS gate
Runtime readiness is PASS when:
1. PR/push Final Gate is green on canonical main;
2. manual/scheduled Steward cycle has at least one green commissioning run;
3. schedule remains enabled;
4. Human Threshold™ accepts Step 1 closure.
