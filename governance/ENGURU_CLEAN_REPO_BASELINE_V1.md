# ENGÜRÜ Clean Repo Baseline™ v1

## Niyet
Her aktif Engurulabory deposunun aynı temel düzen, hakikat ve doğrulama disiplinine sahip olmasını sağlamak.

## State
PREPARED — portfolio-wide adoption pending Repository Deep Clean & Order Pass™ v2.

## Core rule
A repository is not considered healthy because code exists. A healthy repository must make its purpose, canonical ownership, runtime truth, verification path and lifecycle state obvious to a new human or agent without guesswork.

## Mandatory baseline
Every active PRODUCT / CORE / PRODUCT_CORE / CONTROL_PLANE repository must include, where applicable:

1. `README.md`
   - what the repository is
   - why it exists
   - canonical product/core name
   - repository role
   - current STATE
   - truth boundary / known HOLDs
   - how to install/run/test
   - canonical source declaration
   - evidence / DoneCheck / deployment pointer

2. `.enguru/labory-manifest.json`
   - canonical identity
   - role: PRODUCT / CORE / PRODUCT_CORE / CONTROL_PLANE / RELEASE_MIRROR / EXPERIMENT / ARCHIVE
   - owner repository
   - version / lifecycle state
   - dependencies / adapters
   - evidence pointers
   - release/deploy relation

3. Source hygiene
   - `.gitignore`
   - `.env.example` when env configuration exists
   - no real secrets or credentials
   - deterministic dependency lockfile where ecosystem supports it

4. Verification
   - reproducible build/test command
   - meaningful CI when active runtime exists
   - fail-closed checks for critical claims
   - evidence pointer for important PASS statements

5. Public/open repository hygiene when applicable
   - `LICENSE`
   - `SECURITY.md`
   - `CONTRIBUTING.md` when contributions are invited
   - release/version notes or `CHANGELOG.md` for versioned software

6. Production repositories when applicable
   - deployment/runbook pointer
   - production source SHA/version binding
   - rollback or recovery path
   - external credential/provider HOLDs explicitly stated

## Repository role rules

### CONTROL_PLANE
Owns portfolio-wide governance, maps, registries and shared contract/version governance. Must not silently absorb product-domain runtime.

### PRODUCT
Owns one independent user-facing product and its local runtime, tests, evidence and deployment truth.

### CORE
Owns one reusable capability with a clear consumer boundary. A new core repository is justified only if reuse, ownership and testing boundaries are real.

### PRODUCT_CORE
Independent operational/economic product that also provides reusable core capability.

### RELEASE_MIRROR
Never canonical source. Must declare source repository + source SHA/provenance. If separation no longer provides operational value, it becomes ARCHIVE-CANDIDATE after Human Threshold review.

### EXPERIMENT
Must declare purpose, owner, promotion condition and review state. An experiment cannot look like a production product indefinitely.

### ARCHIVE
Read-only historical reference. Must state what replaced it or why it was retired.

## Root cleanliness rule
The repository root should contain only entrypoints and high-value operational files. Product code, docs, evidence, scripts, packages and governance material should live in named directories unless a root file is a deliberate entrypoint.

Do not reorganize root files only for visual neatness. Move only when dependency paths, CI, deployment and documentation references are verified.

## Canonical ownership rule
One product/core = one canonical source repository.

Mirrors, release repos, adapters and public distributions may exist, but they must point back to the canonical source and may not independently claim ownership.

## Evidence rule
`CLAIM != EVIDENCE`.

Repository health and product PASS statements require evidence appropriate to the claim. README wording cannot elevate a HOLD runtime to PASS.

## Lifecycle rule
Every repository must resolve to one lifecycle state:

`INTAKE_HOLD → ACTIVE / REPAIR / EXPERIMENT / RELEASE_MIRROR → ARCHIVE_CANDIDATE → ARCHIVE`

`DELETE_CANDIDATE` is reserved for repositories with no unique code, history, evidence, dependency, product value or archival value. Delete always requires Human Threshold™.

## Human Threshold™
Explicit human approval is required before:
- repository archive
- repository deletion
- repository rename
- repository merge/consolidation
- public/private visibility change
- production source/deployment cutover
- history rewrite or destructive branch cleanup

## Clean Repo score
A repository is scored over 100:
- Canonical identity & role clarity — 20
- README / operational entrypoint quality — 20
- Source & secret hygiene — 15
- Test / CI / evidence quality — 20
- Security / license / release hygiene — 10
- Dependency / duplication discipline — 10
- Lifecycle / archive truth — 5

Judgment:
- 95–100: PASS — CLEAN
- 85–94: PASS WITH MINOR DELTA
- 70–84: REPAIR
- below 70: HOLD — ORDER REQUIRED

## Portfolio acceptance
The Engurulabory portfolio can receive final repository-order PASS only when:
- every accessible repository has a canonical role;
- every active repo is scored;
- no unexplained duplicate ownership remains;
- release mirrors have provenance;
- experiments are explicit;
- Product & Core Map™ is PASS;
- archive/delete decisions are separately approved where needed;
- Repository Steward™ records final evidence and DoneCheck™ judgment.

## Principle
**Mevcut hakikat + gerekli fark. Önce sahiplik, sonra düzen; önce kanıt, sonra hüküm.**
