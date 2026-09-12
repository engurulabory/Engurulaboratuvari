# ENGÜRÜ LABORY PHYSICAL INVENTORY RECONCILIATION — 2026-09-12

## STATE
PASS WITH ADMINISTRATIVE LIMITS

## CLAIM
The GitHub account visibly contains 12 repositories, while the connected Steward/GitHub tool can inspect and govern 8 repositories. These are different scopes and must not be conflated.

## EVIDENCE
Human GitHub repository screen evidence shows 12 account-visible repositories.

Connected GitHub tool inventory returns 8 accessible/governed repositories.

### Governed / connector-accessible — 8
- engurulabory/Engurulaboratuvari
- engurulabory/enguru-website-factory
- engurulabory/enguru-builder-release
- engurulabory/autonomous-economic-core
- engurulabory/donecheck-core-foundation
- engurulabory/donecheck
- engurulabory/shift-core-api
- engurulabory/artist-manager-ai

### Account-visible but outside connector scope — 4
- engurulabory/readdy-fbdccc — RETIRE
- engurulabory/adil-pay-kanit-web — ARCHIVE
- engurulabory/enguru-maya-kurumsal-web — KEEP
- engurulabory/enguru-lab-gelir-çekirdek-portal — KEEP

Adil Pay evidence: public repository currently contains only a 119-byte README and no active runtime/governance surface.

The three private repositories cannot be inspected by the current connector, so destructive actions are not authorized from connector evidence alone.

## PR HYGIENE EXECUTED
Closed as superseded/history-preserved:
- shift-core-api #50
- enguru-website-factory #181

Closed as parked/reference-history:
- enguru-website-factory #169
- enguru-website-factory #166

No commit history was deleted.

## REMAINING ACTIVE PR SURFACE
- Engurulaboratuvari #31 — Billing Core
- artist-manager-ai #44 — iyzico/Readdy handoff
- Builder #175 — Atoms.dev parity
- Builder #177 — Builder v1.1 commercial architecture
- Builder #187 — Aesthetic Final Calibration

## REPOSITORY ACTION BOUNDARY
No repository deletion/archive mutation was executed because the connected GitHub tool does not expose repository-level archive/delete settings.

## FINAL ORDER
12 account-visible
→ 8 connector-accessible / governed
→ 4 explicitly classified extras
→ no silent scope mixing
