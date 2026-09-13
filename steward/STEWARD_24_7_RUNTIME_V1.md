# ENGÜRÜ LABORY STEWARD™ — DURABLE RUNTIME CONTRACT v1.2

## Objective
Keep Labory repository truth, products, cores, security, topology, provenance and evidence current without depending on the user's device.

## Native scopes
- `ENGURU_LABORY` — control plane and portfolio truth.
- `ENGURU_PRODUCT` — user-facing/product execution planes.
- `ENGURU_CORE` — reusable cores and cross-product core workers.

Repository Steward™ is itself a `CORE_WORKER`; it moves across all three scopes.

## Cadence
### On every pull request and push to main
Run the complete Labory Final Gate:
- System Truth / Product-Core Map / Registry consistency;
- IP & Model Trust tests;
- Secret Zero / Fleet Gate;
- Repository Steward tests;
- repository hygiene and conflict-marker checks.

### Daily — full Labory care cycle
Canonical GitHub schedule: `17 5 * * *` (05:17 UTC; approximately 08:17 Europe/Istanbul while UTC+3 applies).

Daily cycle:
`YOKLAMA → TERTIP → DUZEN → TEMIZLIK → SADELESTIRME → BAKIM → ONARIM → KAPANIS → YENIDEN_HAZIR`

Inspect:
- newly visible or missing repositories;
- canonical owner/role drift;
- README and `.enguru` manifest baseline;
- CI/test/evidence health;
- evidence freshness;
- dependency/provenance graph;
- release-mirror parity;
- duplicate/governance drift;
- stale root files and hygiene;
- unresolved HOLD/BLOCKED findings;
- Steward self-health;
- daily Worker Health + Portfolio Health scorecard.

### Incident behavior
Immediate PR/push gates protect changes as they happen. Between daily care cycles, an incident watch may inspect for new material HOLD/BLOCKED conditions. It attempts only SAFE_AUTO, reversible repair first. It notifies the user only when the issue remains unresolved, is BLOCKED, or requires Human Threshold™.

### Manual
`workflow_dispatch` may run the Steward cycle at any time before a consequential decision.

## Finding-to-repair closed loop
`DISCOVER FINDING → CLASSIFY → PLAN → SAFE REPAIR → REVERIFY → EVIDENCE → DONECHECK → CLOSE → READY_AGAIN`

A repair is not complete until verification returns PASS and evidence is recorded.

## Evidence freshness
Evidence used for consequential PASS must satisfy an explicit freshness window. Default Steward TTL is 36 hours unless the domain contract is stricter. Stale evidence produces HOLD; it is refreshed only where required.

## Write discipline
Routine cycles are read-only by default. SAFE_AUTO changes use isolated branch/PR paths and remain small/reversible. Repository archive/delete/rename/merge, visibility change, history rewrite, branch deletion, production source/deployment cutover, money, secrets/account authority and legal certification remain Human Threshold™.

## Daily report
Every daily care cycle emits:
- Worker Health Score;
- Portfolio Health Score;
- repositories scanned;
- repairs applied;
- PASS/HOLD/BLOCKED counts;
- Human Threshold count;
- STATE → CLAIM → EVIDENCE → NEXT ACTION.

No material drift: short `PASS / no material drift` report.
Unresolved issue: immediate bounded alert with exact evidence and next action.

## Failure behavior
Any failed security, consistency, freshness, provenance, self-health or Steward check → HOLD/BLOCKED. No silent bypass and no manufactured green state.

## Runtime PASS gate
Runtime readiness is PASS when:
1. PR/push Final Gate is green on canonical main;
2. daily schedule is enabled and a real scheduled run is green;
3. CORE/PRODUCT/LABORY scopes are machine-tested;
4. at least one real finding-to-repair-to-reverify loop is evidenced;
5. self-health is PASS;
6. Human Threshold accepts any remaining consequential closure.

## 100 operational proof
100/100 requires evidence-backed PASS for:
- full fleet visibility;
- canonical owner/role truth;
- PRODUCT + CORE + CONTROL_PLANE coverage;
- machine-readable baseline/freshness/provenance assessors;
- daily durable runtime;
- finding-to-repair closed loop;
- self-health;
- daily scorecard;
- Human Threshold discipline.

Scores summarize health; they never replace gate truth.
