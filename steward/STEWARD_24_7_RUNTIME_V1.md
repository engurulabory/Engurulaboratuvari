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

### Every third calendar day — scheduled Labory care cycle
Canonical GitHub schedule: `17 5 */3 * *` (05:17 UTC; approximately 08:17 Europe/Istanbul while UTC+3 applies).

This is the full EngürüLabory care cycle, not a simple heartbeat:
`YOKLAMA → TERTİP → DÜZEN → TEMİZLİK → SADELEŞTİRME → BAKIM → ONARIM → KAPANIŞ → YENİDEN HAZIR`

Run the complete gate and inspect:
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
Labory repository governance does not require a full cleanup every hour. PR/push gates protect changes immediately; the three-day care cycle catches accumulated drift, stale work, hygiene debt and maintenance needs without creating unnecessary churn.

An hourly runtime/heartbeat may still be used by the independent commissioning worker to prove reachability and continuity. Heartbeat frequency and full maintenance frequency are intentionally separate.

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


## Steward 100 operational proof targets
Steward reaches operational 100 only when all three are evidence-backed:

1. **FULL FLEET VISIBILITY** — account-visible repository truth and connector/runtime discovery are reconciled without hidden repositories.
2. **DURABLE SCHEDULED RUNTIME** — PR/push gates remain immediate and the three-day Labory care cycle runs successfully on schedule with durable run evidence.
3. **FINDING-TO-REPAIR CLOSED LOOP** — a real finding is detected, classified, routed through SAFE_AUTO/REVIEW/HUMAN_THRESHOLD, repaired in an isolated branch/PR when authorized, verified, evidenced and closed.

Completion chain:
`DISCOVER FINDING → CLASSIFY → PLAN → REPAIR → TEST → EVIDENCE → DONECHECK → CLOSE → READY_AGAIN`

No synthetic/demo-only run may satisfy this proof.
