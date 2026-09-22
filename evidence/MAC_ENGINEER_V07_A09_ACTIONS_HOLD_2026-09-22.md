# ENGÜRÜ Mac Engineering™ v0.7 — V07-A09 GitHub Actions Execution Gate — 2026-09-22

## STATE

**V07-A09 — HOLD**

**Reason:** private technical repository GitHub-hosted Actions jobs are failing before the first workflow step is allocated/executed.

This is an external execution-surface HOLD. It does not overturn V07-A01…A08 verified GitHub-first truth.

## CLAIM

The observed V07-A09 failures are not test failures from ENGÜRÜ Mac Engineering™ runtime code.

Across multiple exact candidate heads and runner labels, GitHub created workflow jobs but returned:

- `status = completed`
- `conclusion = failure`
- `steps = null`
- no executable job log blob

The failure therefore occurs before checkout, compile, test, or candidate scope validation begins.

## EVIDENCE

Technical repository:

- `engurulabory/enguru-mac-engineer`
- private repository
- last verified product exact-main before A09: `5432b9b135499cea18273c0e003877b864af92c6`
- Product CI #26 / run `35770981787`: **SUCCESS**, 54 tests / OK

A09 PR:

- Product PR #13
- branch: `test/v07-a09-fault-injection-campaign`
- campaign PASS counter: **0 / 5**

### Candidate 1 — macos-latest

Exact candidate:

- `97074e6f681204e795a4bff3000bc90418a9a641`

Observed failures:

- targeted run #1 / `35771642847`: failure before steps
- Product CI #28 / `35771642754`: failure before steps
- same SHA close/reopen targeted run #2 / `35771819889`: failure before steps
- targeted run #2 rerun attempt 2: failure before steps
- Product CI #29 / `35771819834`: failure before steps
- Product CI #29 rerun attempt 2: failure before steps

GitHub accepted rerun mutations, proving Actions write authority is present; execution still failed before step allocation.

### Candidate 2 — explicit macos-15

Exact candidate:

- `12e9e7c54f5fff5b6b9eedcfba5d7cd53eb66084`

Observed failures:

- targeted campaign run #3 / `35772106786`: failure before steps
- A09 full regression run #1 / `35772106855`: failure before steps
- Product CI #30 / `35772106978`: failure before steps

This rules out a `macos-latest` / macOS 26-only explanation.

### Candidate 3 — ubuntu targeted + macOS full regression

Exact candidate:

- `d545a6d9d5d9823da5878323022735ad7f47a80e`

Observed failures:

- Ubuntu targeted campaign run #4 / `35772188104`: failure before steps
- macOS 15 A09 full regression run #2 / `35772187806`: failure before steps
- Product CI #31 / `35772187950`: failure before steps

The Ubuntu job also has `steps = null`. This rules out a macOS-only runner-image explanation.

## OBSERVED BOUNDARY

Connected GitHub tooling can:

- read/write the repository;
- create/update branches and workflow files;
- open/close/reopen PR #13;
- request workflow reruns.

Connected tooling cannot read the private account billing/usage or repository Actions policy endpoint required to distinguish among:

- private-repository Actions usage/budget exhaustion;
- billing/payment execution restriction;
- repository/account Actions policy restriction;
- GitHub-hosted runner assignment/provisioning failure.

No unsupported root-cause claim is made.

## JUDGMENT

**HOLD — GITHUB_PRIVATE_REPO_HOSTED_ACTIONS_EXECUTION_GATE**

A09 remains `0/5 PASS`.

Production source remains at the last verified exact-main truth. No production-code repair is justified by current Evidence.

## HUMAN THRESHOLD

Read-only account/UI inspection is required:

1. GitHub → **Settings → Billing & licensing → Usage / Budgets and alerts**
   - inspect GitHub Actions usage, remaining included usage, spending limit/budget, and any payment/billing restriction;
2. Product repo → **Settings → Actions → General**
   - confirm GitHub Actions are enabled and GitHub-hosted runners/workflows are permitted.

No credential or payment detail belongs in Git/Evidence.

## NEXT ACTION

After the execution gate is cleared:

`PR #13 exact candidate → 5 consecutive targeted PASS run IDs → full product regression PASS → diff/scope validation → fresh review → merge → exact-main → control-plane reconciliation`
