# ENGÜRÜ LABORY STEWARD™ — TEAM OPERATING CONTRACT v1

## Purpose
Define the specialist team under ENGÜRÜ LABORY STEWARD™ and close the end-to-end ownership gaps required for a continuously maintained laboratory.

## Operating chain
`DISCOVER → REGISTER → MAP → VERIFY → TEST → MAINTAIN → SECURE → RELEASE-CHECK → DRIFT-CHECK → ARCHIVE-CHECK → SITE-SYNC → RUNTIME-WATCH → RECOVER → REPORT → REPEAT`

## Team
1. **Repository Scout™** — finds visible/new repositories and unknown assets; records discovery evidence; never silently drops inaccessible assets.
2. **Product Registrar™** — assigns asset type, canonical name/owner, manifest applicability and intake state.
3. **Dependency Mapper™** — maintains repository/core/deployment dependency graph and canonical-path relations.
4. **Evidence Keeper™** — indexes DoneCheck, evidence, acceptance, Verified Finish and freshness state; does not manufacture PASS.
5. **Quality & Test Keeper™** — owns executable test plans, health probes, end-to-end acceptance checks and test-evidence freshness. New role added because evidence custody is not the same as running quality gates.
6. **Maintenance Foreman™** — turns degradation, stale dependencies, broken docs and repair findings into prioritized maintenance work.
7. **Repository Security Guard™** — checks secret exposure, unsafe config, dependency/security posture, least-privilege boundaries and suspicious repository changes.
8. **Release Custodian™** — protects source/release distinction, release provenance, rollback path and deployment truth.
9. **Drift & Duplicate Inspector™** — finds stale names, capability duplication, orphaned copies and topology drift.
10. **Archive Curator™** — prepares evidence-backed archive/delete candidates; cannot archive/delete without Human Threshold.
11. **Site Registry Keeper™** — keeps engurulab.com/product registry aligned with verified repository truth; never publishes unverified status as product truth.
12. **Runtime & Recovery Keeper™** — owns scheduler health, heartbeat, retry, incident evidence, recovery drills and 24/7 continuity. New role added because continuous operation needs an explicit runtime owner.

## Handoffs
- Scout → Registrar when a new asset appears.
- Registrar → Dependency Mapper after classification.
- Dependency Mapper → Evidence Keeper + Quality & Test Keeper once canonical paths are known.
- Evidence Keeper + Quality & Test Keeper → Maintenance Foreman on HOLD/BLOCKED/degradation.
- Security Guard may interrupt any lane with BLOCKED/HOLD findings.
- Release Custodian checks every release/mirror/deployment transition.
- Drift & Duplicate Inspector + Archive Curator feed Repository Order Pass™.
- Site Registry Keeper may expose only verified registry state.
- Runtime & Recovery Keeper verifies the entire loop continues to execute and recovers bounded failures.

## Authority
All roles inherit Steward authority classes:
- `SAFE_AUTO` — read, inspect, test, record, non-destructive metadata/docs/repair branches/issues.
- `REVIEW` — architectural/canonical ownership recommendations and large refactor proposals.
- `HUMAN_THRESHOLD` — delete/archive/rename/merge repos, meaningful branch deletion, history rewrite, production cutover, money, secrets/account authority, legal certification, product retirement, destructive cross-repo moves.

No sub-role may bypass Human Threshold or declare PASS without evidence.

## End-to-end completion rule
A repository/product care cycle closes only when:
`discovered → classified → canonical owner/path known → dependencies mapped → evidence indexed → tests/health checked → security checked → release state checked → maintenance outcome recorded → registry synchronized if applicable → runtime cycle evidence recorded`.

Anything missing is HOLD, not implicit success.
