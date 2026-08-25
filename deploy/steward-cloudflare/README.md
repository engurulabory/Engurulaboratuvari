# ENGÜRÜ LABORY STEWARD™ — Cloudflare 24/7 Commissioning

## STATE
READY FOR HUMAN CLOUDFLARE COMMISSIONING — runtime PASS requires deployed evidence.

## Purpose
Run Steward independently of the user's device once per hour, discover the current Engürü Labory repository fleet, persist evidence in D1 and expose a deterministic 24-hour proof endpoint.

## Runtime flow
`CRON → GitHub discovery → inventory digest → D1 persistence → findings → /commissioning/proof`

New repositories are expected. A newly discovered repo is not an error; it changes inventory truth and is recorded for intake. Missing repositories explicitly listed in `EXPECTED_REPOSITORIES` produce HOLD, never a false PASS.

## Security model
Commissioning begins read-only.

- `GITHUB_TOKEN`: fine-grained token with the minimum read access required to see all repositories that Steward must inventory. Do not paste it into chat or commit it.
- `STEWARD_CONTROL_TOKEN`: random secret used only for the protected manual `/commissioning/run` endpoint.
- D1 contains repository metadata/evidence, never GitHub tokens or account secrets.
- Destructive repo actions are not implemented in this commissioning worker.

After 24/7 PASS, maintenance writes should be commissioned as a separate scoped capability with Human Threshold for destructive actions.

## Human commissioning steps
1. Cloudflare Dashboard → Workers & Pages → D1 → create database named `enguru-labory-steward`.
2. Run `schema.sql` against that D1 database.
3. Copy `wrangler.toml.example` to the deployment configuration and replace only `REPLACE_WITH_D1_DATABASE_ID`.
4. Deploy `worker.js` with the D1 binding `DB` and hourly cron `0 * * * *`.
5. Add secrets in Cloudflare, not GitHub source:
   - `GITHUB_TOKEN`
   - `STEWARD_CONTROL_TOKEN`
6. Confirm `GET /health` returns `state: PASS`.
7. Trigger one protected manual run or wait for the first top-of-hour cron.
8. Open `GET /commissioning/proof` and record the Worker URL plus first evidence.

## GitHub token boundary
For commissioning, prefer a fine-grained token limited to the Engürü Labory repositories with read-only Metadata and Contents access. If the three UI-visible repositories are private, the token must explicitly be allowed to see them or their expected-name checks will correctly remain HOLD.

## PASS gate
Steward 24/7 continuity is PASS only when `/commissioning/proof` reports:

- `state: PASS`
- `runtime_reachable: PASS`
- `inventory_discovery: PASS`
- `observation_24_hourly_cycles: PASS`
- `hourly_cycles_seen >= 24`
- `hourly_cycles_pass = 24`
- `distinct_hourly_windows >= 24`
- `hourly_cycles_blocked = 0`

Architecture, deployment, or one successful call is not 24/7 PASS.

## Failure semantics
- GitHub/API/runtime error → BLOCKED for that cycle.
- Expected repository not visible → HOLD.
- Inventory changed/new repository discovered → finding recorded; intake review required, but discovery itself remains healthy.
- Missing evidence → HOLD.

## Human Threshold
Delete/archive/rename/merge/history rewrite/public cutover/credentials/financial/legal actions remain outside this worker and require explicit human approval.
