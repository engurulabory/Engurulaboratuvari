# ENGÜRÜ Labory Final Three Gates — 2026-09-18

## STATE

**HOLD — exactly three closure gates remain.**

## Gate 1 — Governance intake exact-main Fleet evidence

### Publish Engine
- Governance PR #10 merged.
- exact main: `3719c720674a145c5a77b6d8e89267b72b5b310d`.
- `.enguru/labory-manifest.json`: present.
- `.enguru/ip-model-trust.json`: present, T4.
- pinned `ENGURU IP Model Trust Fleet` workflow: present.
- PR-head Fleet run `35335074270`: SUCCESS.
- product CI run `35335074204`: SUCCESS.
- exact-main push-run is not exposed by the current connector wrapper.

### ZEKÜ FINANCE PRIME
- Governance PR #13 merged.
- exact main: `4be0746db95feac21fa321a1a57937ee53ba7733`.
- `.enguru/labory-manifest.json`: present.
- `.enguru/ip-model-trust.json`: present, T4.
- pinned `ENGURU IP Model Trust Fleet` workflow: present.
- PR-head Fleet run `35335077542`: SUCCESS.
- exact-main push-run is not exposed by the current connector wrapper.

**Verdict:** HOLD_EXACT_MAIN_FLEET_EVIDENCE. Do not promote governed fleet 8 → 10 until the exact-main push CI evidence is observed.

## Gate 2 — Branch protection required checks

Current System Truth records:
- `labory-final-gate` is required;
- `IP Model Trust Gate` and `IP Model Trust Fleet` are not both required status checks.

The connected GitHub tool surface exposes no branch-protection/ruleset mutation action.

**Verdict:** HOLD_ADMIN_CONFIGURATION.

Required configuration:
- add `IP Model Trust Gate` as required status check for `main`;
- add `IP Model Trust Fleet` as required status check for `main`;
- preserve pull-request requirement and deletion/non-fast-forward protections.

## Gate 3 — PARK production read-only proof

Required runtime-only configuration:
- `PARK_API_USERNAME`
- `PARK_API_PASSWORD`
- `PARK_API_BASE_URL`
- `PARK_API_VERSION`

Then prove, read-only:
1. live authentication;
2. ENGÜRÜ Maya account identity;
3. taxpayer lookup;
4. redacted evidence;
5. DoneCheck read-only triple PASS.

Stop before first fiscal write/invoice at Human Threshold™.

**Verdict:** HOLD_HUMAN_THRESHOLD_CREDENTIALS.

## Closed in the preceding package

- Builder release mirror: PASS, 94/94 parity.
- Repository Steward approximately-3-day read-only schedule: merged.
- This PR additionally runs `steward/run-scheduled-cycle.mjs` inside Labory Final Gate, so the actual scheduled runner is CI-proven.

## EXIT

`Gate 1 PASS → Gate 2 PASS → Gate 3 read-only PASS → final DoneCheck → Human Threshold → ENGÜRÜ LABORY VERIFIED FINISH`
