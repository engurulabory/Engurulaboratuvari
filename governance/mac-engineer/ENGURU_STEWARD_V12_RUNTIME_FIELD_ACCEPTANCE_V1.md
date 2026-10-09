# ENGÜRÜ Steward™ v1.2 — Operational Field Acceptance Contract

**STATE:** GITHUB_CODE_AND_NEGATIVE_CI_PASS / FIELD_PROOF_HOLD / OSI_HOLD / VERIFIED_FINISH_HOLD
**PROJECT:** STEWARD_V12, one canonical core and one final scope.
**SOURCE:** `engurulabory/Engurulaboratuvari` draft PR #179.

## STATE
The project branch contains `steward/fleet-observation.mjs` and its adversarial test suite. A scoped read-only API observation is bound to `steward/run-scheduled-cycle.mjs`. `.github/workflows/steward-scheduled-cycle.yml` supplies `STEWARD_FLEET_READ_TOKEN` from GitHub Actions secrets to the **read-only** runtime.

GitHub CI run **37891267050**, job **113692508198**, completed with success (hybrid tests including fleet negative fixtures). This is CI evidence only.

Repository list observed via connected GitHub interface on 2026-10-09: **11** owner-visible repositories. Historical Product/Core map includes **10** observed connector-accessible repositories on 2026-09-18. Differences may reflect discovery scope, snapshot age, or owner classification. Full visibility requires actual Steward API evidence under the authorized token scope.

## CLAIM
Actual Steward v1.2 field acceptance requires a genuine **scheduled** GitHub Actions event, authenticated fleet discovery, expected canonical fleet visibility, complete three-scope report, evidence freshness, self-health, and subsequent OSi native parity. GitHub `main` accepts scheduled cron only after reviewed merge. Until then schedule definition on the PR is code candidate, not production schedule adoption.

## EVIDENCE — Positive and negative acceptance gates
1. **Fleet credentials and visibility** — `STEWARD_FLEET_READ_TOKEN` configured in GitHub Actions with read-only access to all governed repos; source token value stays in GitHub secret manager; receipt shows `source=GITHUB_AUTHENTICATED_API`, `complete=true`, `missing=[]`.
2. **Safety** — Missing token, 403, offline, schema mismatch, truncated pagination, missing expected repository, duplicate owner yields HOLD.
3. **Scheduled event** — After reviewed PR merge, a genuine `schedule` event at 05:17 UTC, numeric Actions run ID and pinned `main` commit appear in receipt. A manual dispatch or PR fixture is distinct proof.
4. **Three-scope observation** — LABORY, PRODUCT, CORE tracked-file scope probes each have real evidence; repository-fleet type aggregation is a further observation and must be grounded in current Product/Core map.
5. **Maintenance closure** — Real bounded finding → authorized SAFE_AUTO remediation (or REVIEW queue) → reverify → DoneCheck → evidence receipt. Human Threshold remains explicit for consequential changes.
6. **OSi parity** — Scoped digest-pinned artifact, local native and Cockpit tests, baseline preservation (including 8 earlier unrelated modified paths), fresh DoneCheck and approved Human Threshold.
7. **Finalization** — Independently re-read Progress Core and canonical v1.2 acceptance state; record `LOCKED` only on exact verified evidence and authorized finalizer.

## JUDGMENT
`GITHUB_CODE_CI=PASS_SCOPED`  
`GITHUB_SCHEDULED_FIELD=HOLD`  
`MULTI_REPOSITORY_FLEET_PROOF=HOLD`  
`OSI_FIELD=HOLD`  
`VERIFIED_FINISH=HOLD`

## NEXT ACTION
**STEWARD_V12_REVIEWED_GITHUB_RUNTIME_COMMISSIONING:** review PR #179 implementation and rights; configure scoped `STEWARD_FLEET_READ_TOKEN` through GitHub Secrets; review/merge once engineering acceptance is approved; capture the first authentic daily scheduled receipt and evaluate all the gates in one consolidated evidence report. Then deliver digest-locked bundle to OSi and run native/human finalization.

**ONE GOAL → ONE WHOLE-CHAIN PREFLIGHT → ONE INTEGRATED EXECUTION → ONE VERIFIED DELIVERY.**
