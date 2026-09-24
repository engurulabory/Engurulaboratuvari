# ENGÜRÜ Mac Engineering™ — Mac Repository Fabric Preparation — 2026-09-23

## STATE

**PREPARED / REAL MAC ACCEPTANCE PENDING**

## CLAIM

The current connector-accessible `engurulabory` repository surface contains 12 repositories. A full-history Mac mirror fabric has been defined for all 12.

The package does not promote Mac-native canonical authority yet. GitHub remote main remains canonical during migration.

## FRESH INVENTORY

1. `engurulabory/Engurulaboratuvari` — `2fd5553a55ce2a8c42163c81a4d21fc155bc0593`
2. `engurulabory/enguru-website-factory` — `88d00d025945fb170ddd88c5bd97c1f5a69ef999`
3. `engurulabory/enguru-builder-release` — `fc17cbbf913bb46cc7289db3a9e7b583eb4a7e7f`
4. `engurulabory/autonomous-economic-core` — `31aab38a964faf84aac4d71d084605b833f68b8d`
5. `engurulabory/donecheck-core-foundation` — `f555354fa756b47f6e83ab05248e63005b1054bf`
6. `engurulabory/donecheck` — `8b90a8fc93453dd8a84994195d28d14b15e261cb`
7. `engurulabory/shift-core-api` — `5ac8eaa1abc9ccf70b6b93e6eb191743ef25af01`
8. `engurulabory/artist-manager-ai` — `330b993876319ff3dd22443dadec7d903c4844f8`
9. `engurulabory/enguru-publish-engine` — `4cac1cff5fab1db744c5f81b95dbcfe17caba6b6`
10. `engurulabory/zeku-finance-prime` — `0f6ea017d67cafe2deb19c4c65be37811d54e88f`
11. `engurulabory/enguru-mac-engineer` — `5432b9b135499cea18273c0e003877b864af92c6`
12. `engurulabory/adil-pay-kanit-web` — `bd6b1e85234181705adbb8ccd826bbc4bbf04add`

## FABRIC DESIGN

Full-history mirrors:

`~/Enguru/GitVault/RepositoryFabric/engurulabory/<repo>.git`

Existing working checkouts remain in place.

New engineering work may use disposable worktrees derived from local mirrors.

This avoids duplicate permanent checkout trees while preserving full offline repository history.

## ACCEPTANCE

Real Mac acceptance requires:

- manifest: 12 unique repositories;
- mirror sync: 12 / 12;
- each mirror bare: PASS;
- exact-main match: 12 / 12;
- `git fsck --full --no-dangling`: PASS for every mirror;
- current working checkout discovery;
- offline local commit queue proof;
- mirror main remains unchanged by offline fixture;
- machine-readable Evidence.

## AUTHORITY

During migration:

`GitHub remote main = canonical`

`Mac mirror = full-history offline source cache`

`local ahead commits = pending reconciliation`

Mac-native engineering authority opens only after the migration acceptance contract and DoneCheck v1.2 / Human Threshold gates are satisfied.

## DONECHECK

DoneCheck is represented as one product with two repositories:

- current canonical product: `engurulabory/donecheck` v1.2.0;
- historical foundation: `engurulabory/donecheck-core-foundation`.

## NEXT ACTION

Run:

`zsh governance/mac-engineer/MAC_REPOSITORY_FABRIC_ACCEPTANCE.command`

Expected success:

`STATE=MAC_REPOSITORY_FABRIC_LOCAL_ACCEPTANCE_PASS`
