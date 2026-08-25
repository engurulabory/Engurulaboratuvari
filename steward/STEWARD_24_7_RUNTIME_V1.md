# ENGÜRÜ LABORY STEWARD™ — 24/7 RUNTIME CONTRACT v1

## Objective
Run Steward independently of a user's device and continuously maintain observable repository health.

## Required cycles
### Hourly
- discover newly visible repositories;
- compare inventory digest with previous cycle;
- check active product manifest presence/alignment;
- check open HOLD/BLOCKED findings;
- run lightweight security/config drift checks;
- record cycle evidence.

### Daily
- dependency/canonical-owner drift review;
- stale documentation and dead-link review;
- release/source provenance review;
- product health summary;
- maintenance queue prioritization.

### Weekly
- duplicate/overlap review;
- archive candidate review;
- deep security posture review;
- 100-scorecard recalculation;
- Map Completeness DoneCheck refresh.

## Scheduler strategy
Preferred durable scheduler: existing zero-cost Cloudflare Worker/Cron pattern already proven in the ENGÜRÜ environment, with GitHub API access scoped to read/write only what Steward needs.

GitHub Actions may be used as a secondary/verification runner when account billing/Actions availability is confirmed. Absence of Actions runs must never be treated as PASS evidence.

## Write discipline
Routine cycles may only auto-write SAFE_AUTO artifacts such as inventories, health ledgers, issues, reports, manifests and repair branches. Destructive operations remain Human Threshold.

## Evidence per cycle
Each cycle records:
- startedAt / finishedAt;
- inventory count and digest;
- new/changed/missing assets;
- manifest alignment result;
- security findings count;
- health PASS/HOLD/BLOCKED counts;
- maintenance actions opened/completed;
- runtime/scheduler identity;
- errors/retries;
- next action.

## Failure behavior
Scheduler or API failure → HOLD, bounded retry, evidence record. Never silently skip and never manufacture a green state.

## 24/7 PASS gate
24/7 operational continuity is PASS only after deployed durable runtime evidence demonstrates repeated successful cycles across at least 24 consecutive hourly windows. Architecture/documentation alone is not runtime PASS.
