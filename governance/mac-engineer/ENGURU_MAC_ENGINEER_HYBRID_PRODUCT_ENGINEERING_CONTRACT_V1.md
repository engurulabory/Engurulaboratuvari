# ENGÜRÜ Mac Engineer™ — Hybrid Product Engineering Contract v1.0

**STATE:** PROPOSED / GITHUB_PREPARATION
**AUTHORITY:** ENGÜRÜ Labory control-plane review; OSi remains authoritative for local runtime and field acceptance.
**GOAL:** Engineer Mac Engineer subproducts through the best-fit development surface and deliver each through one end-to-end verified project.
**SCOPE:** Process and handoff contract only; no runtime changes, no new core, no release promotion.

## 1. One project, one finish
**1 Ana Hedef = 1 Proje → 1 Uçtan Uca Ön Analiz ve Simülasyon → 1 Bütünleşik Yürütme → 1 Doğrulanmış Teslim.**

The selected subproduct is the single project throughout GitHub development and local OSi installation. GitHub CI PASS is a development gate, **not** OSi Verified Finish. Preserve existing canonical assets; prefer REUSE → EXTEND → ADAPTER → NEW CORE only with evidence.

## 2. Execution-surface decision
Classify each subproduct using current repository ownership and real dependencies:
- **GITHUB_FIRST:** portable packages, governance contracts, schemas, deterministic tests, cross-platform adapters. GitHub PR/CI/artifact followed by OSi acceptance.
- **OSI_FIRST:** Swift/macOS native app, UI, Keychain, local models, MLX/Ollama, hardware-sensitive workloads. Local test first, controlled GitHub provenance, then exact-head OSi acceptance.
- **HYBRID:** product operators, provider boundaries, runtime orchestration, Progress/DoneCheck integrations. Shared contract and CI, native parity on OSi.
Classification is a proposal until per-subproduct canonical inventory and OSi capability check. Never create a second canonical source.

## 3. Pre-execution whole-chain contract
Before authorizing execution, pin: project objective and success/exit criteria; repository and branch HEAD; owner; dirty-worktree preservation; versioned input/output schemas; dependencies and versions; Python/Node/Swift toolchains; tests and negative cases; provenance and artifact digest; human authority; finalizer identity; rollback; exact local install commands; and **native Progress Core project resolution**.
Run a simulated happy path and fail-closed cases for invalid schema, unavailable toolchain, stale artifact, missing authority, wrong producerKind, version mismatch, signature failure, interrupted publish, foreign-file collision, state drift and inaccessible finalizer. A simulation PASS must cover *all* final dependencies, not merely the first guards.

## 4. Single integrated execution
1. Pin current truths for GitHub and OSi separately. Existing accepted evidence may be reused only if source pin and scope still match.
2. Develop in the selected canonical product repository; open PR and run applicable CI/security/license tests.
3. Produce immutable artifact manifest: source repository/ref/commit, artifact SHA-256, build/test commands, toolchain versions, provenance, known limitations.
4. OSi imports only an authenticated, digest-matching artifact. Preserve local changes and runtime secrets.
5. Run actual native regression, integration, negative tests, DoneCheck with a **schema-valid and trusted producer provenance**, scoped Human Threshold, and the *approved* project finalizer.
6. Independently re-read canonical worklist/state and native Progress Core projection; compare digest, authority, and final state before declaring Verified Finish.
7. Failure => HOLD with one consolidated receipt and recovery path. Do not invent PASS or auto-promote a missing authority.

## 5. Non-negotiable boundaries
- GitHub controls source review/CI provenance; **OSi controls runtime facts** and local acceptance.
- DoneCheck machine proof does not itself authenticate a human. Human approval scope is explicit.
- Never use Gate12 reviewer authorization for another project without separate approved scope.
- Progress Core is a **reader/projection**, not an invented final-state writer.
- No mutation of SHA-pinned historical records; create versioned successor artifacts only under authorized policy.
- No release, merge, publish, destructive changes or production promotion by this contract alone.
- The present GitHub `main` governance view can be older than OSi's local feature branch; reconcile exact heads before any production change.

## 6. Handoff artifact acceptance
Each subproduct handoff must contain:
`projectId`, `executionMode`, `canonicalRepo`, `sourceRef`, `sourceCommit`, `artifactDigest`, `toolchain`, `testEvidence`, `negativeEvidence`, `licenseSecurity`, `osiInstallPlan`, `rollbackPlan`, `doneCheckRef`, `humanAuthorityScope`, `progressProjectBinding`, `finalizerRef`, `verifiedFinish`.

Initial state of all unverified fields is PENDING/HOLD. Machine-readable template: `ENGURU_MAC_ENGINEER_HYBRID_HANDOFF_TEMPLATE_V1.json`.

## 7. Acceptance and next action
**GitHub preparation acceptance:** isolated branch, reviewed contract, template schema syntactically valid, PR review. **OSi field acceptance:** real machine/installation/run; test, provenance, Human Threshold and native Progress reconciliation PASS. Final acceptance remains HOLD until completed on OSi.

**NEXT_ACTION:** Reconcile Mac Engineer subproduct inventory against current OSi canonical HEAD; classify GITHUB_FIRST / OSI_FIRST / HYBRID; pilot **one** bounded subproduct with this same contract; measure cycle time, regression count, defects surfaced after preflight and field parity. Do not assert a speed improvement without comparative evidence.

**RESULT LANGUAGE:** STATE → CLAIM → EVIDENCE → JUDGMENT → NEXT ACTION.
