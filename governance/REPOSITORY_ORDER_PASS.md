# Repository Order Pass™

## Purpose
Run alongside ENGÜRÜ PRODUCT & CORE MAP™ and convert discovery into a safe repository-order plan.

## Non-destructive phase only
Until Product & Core Map reaches PASS:

- do not delete repositories;
- do not merge repositories;
- do not rename canonical products;
- do not move large code surfaces;
- do not retire products;
- do not rewrite repository history.

Allowed before map completion:

- read/search/fetch;
- add inventory records;
- add missing documentation;
- record canonical pointers;
- identify duplicates and stale structures;
- open issues/PRs for review;
- add non-destructive manifests when their truth is verified.

## Steward checks per repository

1. repository purpose is explicit;
2. product/core classification is explicit;
3. canonical source/path is known;
4. README reflects current truth;
5. `.enguru/labory-manifest.json` exists where applicable;
6. governance contract link is current;
7. evidence and DoneCheck paths are discoverable;
8. release/deployment truth is separated from claims;
9. secrets are absent from repository content;
10. stale branches/docs are identified, not silently removed;
11. duplicate capabilities are mapped;
12. archive candidates are evidence-backed.

## Output
For every finding, Steward records:

`state → claim → evidence → next action`

Actions are tagged:

- SAFE_AUTO — non-destructive documentation/metadata order
- REVIEW — architecture or ownership judgment
- HUMAN_THRESHOLD — rename, merge, delete, retire, payment/publish/legal or irreversible external effect

## DoneCheck gate
Repository Order Pass can only close when Product & Core Map is PASS and all high-impact actions are either completed with evidence or explicitly held at Human Threshold.


## ENGÜRÜ YAYIN MOTORU™ — IMPLEMENTATION ADMISSION

**STATE — PASS TO IMPLEMENTATION / NOT YET GOVERNED FLEET**

This is a non-destructive repository-order admission for the implementation of the already-merged foundation specification at:
`governance/publish-engine/ENGURU_PUBLISH_ENGINE_FOUNDATION_V0_1.md`.

Planned canonical implementation repository:
`engurulabory/enguru-publish-engine`

Classification:
- assetType: CORE
- role: verified publication control plane / local Mac execution surface
- canonical truth: GitHub repository
- execution surface: Mac local runtime
- production runtime: provider adapter target; Mac is not the public web server

Admission rules:
1. Repository creation is allowed as a new independent core; no existing repository is renamed, moved, merged or retired.
2. Existing strategic sequence remains unchanged; this admission does not manufacture PASS for any earlier Labory gate.
3. The repository is not counted in governed fleet totals until its Labory manifest, security gates, evidence path and exact-main acceptance are installed and verified.
4. Initial provider implementation is Cloudflare-first and adapter-bound.
5. Automatic paid upgrade is forbidden; cost escalation produces HOLD.
6. Production publication and rollback remain Human Threshold™ actions.
7. Canonical delivery sequence is:
   `repository → executable core → tests → CI → field proof → DoneCheck™ → verified release → Mac local install`.
8. Mac local runtime is the operating surface only after the GitHub canonical implementation reaches its technical release gate.

Action tag:
**SAFE_AUTO — non-destructive implementation admission**


---

## 2026-09-18 — REPOSITORY TRUTH RECONCILIATION

**STATE — PASS FOR CONNECTOR INVENTORY / HOLD FOR FLEET PROMOTION**

Observed through the connected GitHub account:

- connector-accessible repositories: **10**;
- evidenced governed fleet: **8**;
- governance-intake repositories: **2**.

### ENGÜRÜ YAYIN MOTORU™

- repository: `engurulabory/enguru-publish-engine`;
- classification: **CORE**;
- exact observed main: `91c35efd6fd24ce0e515c2f977a83743cdf46516`;
- `.enguru/labory-manifest.json`: present;
- canonical truth: GitHub;
- execution surface: Mac local;
- production/rollback: Human Threshold™;
- fleet promotion: **HOLD** until Labory security/fleet acceptance evidence is explicit.

The earlier “planned canonical implementation repository” admission is historical. The repository now exists; no new repository is required.

### ZEKÜ FINANCE PRIME

- repository: `engurulabory/zeku-finance-prime`;
- classification: **PRODUCT**;
- exact observed main: `c2ca3adb848e1098ceeefd0e4d64adb169c08800`;
- runtime: single Mac / local-only;
- DoneCheck™ and Human Threshold™ boundaries: present;
- `.enguru/labory-manifest.json`: not found during this reconciliation;
- fleet promotion: **HOLD** until explicit Labory manifest/adoption and fleet/security evidence are present.

### Governing rule

`accessible ≠ governed`.

Neither repository may be silently added to the governed fleet count. Promotion requires evidence, not repository existence.

Action tag: **SAFE_AUTO — truth reconciliation; fleet promotion remains HOLD**
