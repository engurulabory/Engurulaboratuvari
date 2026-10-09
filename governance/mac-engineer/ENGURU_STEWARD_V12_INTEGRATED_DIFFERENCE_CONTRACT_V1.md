# ENGÜRÜ Steward™ v1.2 — Integrated Difference & Verified Delivery Contract v1.0

**STATE:** CONTRACT_PREPARED / IMPLEMENTATION_HOLD / VERIFIED_FINISH_HOLD  
**PROJECT:** STEWARD_V12 (one canonical subproduct project)  
**AUTHORITATIVE SOURCE:** `engurulabory/Engurulaboratuvari/steward/`  
**EXECUTION MODEL:** GitHub engineering + OSi native field acceptance  
**GOVERNANCE:** ENGÜRÜ Süzgeci™ (meaning/judgment) → ENGÜRÜ Work Protocol™ (execution) → GitHub/OSi adapters (capabilities)  
**FINISH:** one end-to-end preflight + one integrated implementation + one evidence-backed verified handoff.

## 1. STATE — Current truth and preservation baseline

GitHub baseline observed 2026-10-09:
- `steward/index.mjs` reports `STEWARD_VERSION = '1.1.0'`.
- `steward/STEWARD_24_7_RUNTIME_V1.md` defines v1.2 daily runtime and three native scopes.
- `.github/workflows/steward-scheduled-cycle.yml` uses `23 6 */3 * *`; v1.2 contract targets `17 5 * * *`.
- `steward/run-scheduled-cycle.mjs` collects the LABORY scope, with BLOCKED as its nonzero exit condition.
- Steward Cloudflare/D1 commissioning is a distinct 24-hour live-proof boundary.

OSi snapshot (2026-10-09 05:43:33Z):
- Control repo branch `feat/mac-engineer-v08-product-engineering-operator`, HEAD `a056fd29f5a12f302216628e638a614640ff0d4e`.
- Product repo branch `feat/v08-native-productization-provenance`, HEAD `26925c21c7816a90edc0eb047382aba8c696764c`, worktree clean at observation.
- Control repo contains eight unrelated modified paths, all preserved as existing work.
- GitHub and OSi steward source blobs match for the observed `index.mjs`, runtime contract, schedule and runner.

**Accepted historical OSi evidence — reuse with original scope and original HEAD:**

| Existing artifact | Historical claim | Recorded evidence | Valid reuse scope |
|---|---|---|---|
| `governance/osi-foundation-100/Evidence/F100_P05_STEWARD_ACTIVATION_FIELD_PROOF_V1.json` | OSi safe inspection + canonical parity | PASS; 8/8 focused; 1467/1467 regression; operator 1.1.0 | OSi read-only activation, source parity and worktree preservation |
| `governance/osi-foundation-100/Evidence/F100_P09_STEWARD_LIVE_COCKPIT_FIELD_PROOF_V1.json` | OSi live Cockpit integration and recovery | PASS; 39/39 focused; 1482/1482 regression; runtime recoveryCount=2 | Cockpit/projection field integration; original record `verifiedFinish=HOLD` |
| `governance/osi-runtime/ENGURU_OSI_STEWARD_BINDING_V1.json` | Canonical source/OSi adapter boundary | `READY_FOR_FIELD_PROOF`; `READ_ONLY_INSPECT_AND_PLAN`; one canonical Steward | Binding/authority contract; is not final runtime acceptance |
| `governance/operator-fabric/C1_P04_STEWARD_RECEIPT_V1.json` | Operator Fabric Steward scope | PASS; 10/10 itemResults; scoped DoneCheck PASS | C1.P04 package acceptance; `verifiedFinishClaimed=false` |

Historical evidence remains original, immutable in scope, and linked by artifact path/HEAD/digests. Fresh v1.2 full-project acceptance is separate.

## 2. CLAIM — One necessary integrated difference

**Move existing canonical Steward worker from v1.1 implementation and partial scheduled cycle to the explicitly contracted v1.2 runtime, with testable three-scope daily care, evidence freshness, closed-loop recovery, self-health, secure authority, and independently proven GitHub → OSi parity.**

Preserve one Steward core, the canonical repository, existing Cockpit adapter, historical OSi evidence and human authority. Use REUSE → EXTEND → ADAPTER → NEW CORE only after explicit architectural review; this project targets REUSE/EXTEND.

## 3. EVIDENCE — Required executable acceptance matrix

| ID | Difference / proof | Positive acceptance | Negative / boundary probe | Gate |
|---|---|---|---|---|
| S01 | Pin exact canonical source and dependencies | steward tree, branch, HEAD, SHA-256 and OSi source match | stale branch, foreign artifact, dirty unrelated path | PRE_EXECUTION |
| S02 | v1.2 implementation semantics | version report accurately reflects implemented v1.2 behavior | version-only bump without features | GITHUB_CI |
| S03 | Three native scopes | LABORY, PRODUCT, CORE each tested with representative repository facts | absent scope/unknown role and partial observation | GITHUB_CI |
| S04 | Daily durable scheduler | schedule `17 5 * * *`, dispatch and least-privilege readonly runner; genuine scheduled receipt | cron drift, missed schedule, transient failure | GITHUB_RUNTIME |
| S05 | Baseline/freshness/provenance | 36-hour default TTL or stricter domain policy, owner map and provenance connected to evidence | stale receipt, missing repo, duplicate canonical authority | GITHUB_CI |
| S06 | Finding-to-repair-to-reverify | representative real finding reaches evidence, DoneCheck and READY_AGAIN within approved SAFE_AUTO scope | unsafe action, reverify fail, partial recovery, permission escalation | GITHUB_FIELD |
| S07 | Self-health and scorecard | daily worker+portfolio scores from actual scans; PASS/HOLD/BLOCKED preserve gate truth | misleading 100 score with HOLD gate; blank evidence | GITHUB_CI |
| S08 | Existing OSi linkage | prior F100.P05/P09, binding and C1.P04 receipts reused for their original scopes | outdated receipts asserted as fresh v1.2 finish | OSI_FIELD |
| S09 | Native integration parity | real OSi Steward read-only cycle, test harness and Cockpit show correct state on pinned release | mismatch, restart, missing adapter, worktree collateral mutation | OSI_FIELD |
| S10 | Scoped final acceptance | exact GitHub source/CI, scheduled run, artifact digest, OSi DoneCheck, Human Threshold and native Progress reread bind one receipt | expired evidence, fabricated authority, mismatched DoneCheck ID, unauthorized LOCKED | VERIFIED_FINISH |

**Separate runtime clarification:** The Cloudflare/D1 24-hour continuous service requires deployed 24-hour /commissioning/proof observations, independent of daily GitHub schedule. Include this in S04/S10 **only if** the v1.2 approved product scope includes Cloudflare 24/7 operational delivery. Resolve scope with canonical owner before asserting any 24/7 PASS. Both schedules may coexist as separately identified surfaces.

## 4. Integrated whole-chain preflight

Before a GitHub source write, inspect exact main and OSi worktree, source ownership and licenses; enumerate toolchains, workflow permissions, source/build provenance, artifact identities, schema/producerKind compatibility, existing positive and negative tests, timeout/recovery, state authority, Human Threshold and finalizer entrypoint.

Simulate the complete path with fixtures: `source → tests → CI → digest → scheduled receipt → OSi field → scoped DoneCheck → authorized human acceptance → native Progress Core reread`. Count a complete preflight as PASS only with the finalizer and all downstream dependencies modeled. Negative cases must fail closed with a single evidence receipt and a recovery instruction.

## 5. Bounded integrated execution

**P1 — Source reconciliation and classification.** Current GitHub main, OSi product/control HEAD and existing Steward artifacts matched, preservation baseline captured.  
**P2 — GitHub v1.2 implementation.** Extend existing `steward/`, tests and scheduled workflow as needed by S02–S07, with source ownership and no second core.  
**P3 — GitHub acceptance.** Test results, negative matrix, security/fleet gates and actual daily scheduled-run evidence pinned to exact commit.  
**P4 — OSi field acceptance.** Authorized local operator imports digest-verified artifact into isolated working branch, runs real native parity and scoped DoneCheck, preserving unrelated local changes.  
**P5 — Verified handoff.** Human Threshold decision + project-specific approved finalizer + independent native Progress Core check; receipt binds GitHub commit, artifact hash, scheduled work evidence, local field evidence, canonical state.

Execution pauses at evidence-gated boundaries inside this *same project*. Failures yield HOLD with an explicit single recovery action. The plan retains a single authoritative finish.

## 6. Authority, positive-language and preservation contract

`SOURCE_PRESERVATION=ENABLED`  
`ALLOWED_SOURCE_PATHS=steward/**,.github/workflows/steward-scheduled-cycle.yml,governance/mac-engineer/ENGURU_STEWARD_V12_* (upon explicit review)`  
`UNRELATED_WORKTREE=PRESERVED`  
`HISTORICAL_EVIDENCE=IMMUTABLE_IN_SCOPE`  
`CANONICAL_STEWARD_COUNT=1`  
`HUMAN_THRESHOLD=SCOPED_AND_REQUIRED`  
`GITHUB_CI_AUTHORITY=DEVELOPMENT_EVIDENCE`  
`OSI_AUTHORITY=NATIVE_FIELD_TRUTH`  
`VERIFIED_FINISH=HOLD_UNTIL_FINAL_RECEIPT`

Authority for local or deployment actions is obtained and verified at the corresponding gate. A green CI run, an old scoped PASS receipt, or a version label are never a stand-alone final claim.

## 7. JUDGMENT — Present acceptance state

- `HISTORICAL_STEWARD_ACTIVATION=PASS_SCOPED`
- `HISTORICAL_STEWARD_LIVE_COCKPIT=PASS_SCOPED`
- `HISTORICAL_OPERATOR_FABRIC_C1_P04=PASS_SCOPED`
- `STEWARD_V12_GITHUB_RUNTIME=HOLD`
- `STEWARD_V12_REAL_DAILY_SCHEDULE=UNVERIFIED`
- `STEWARD_V12_OSI_FIELD=HOLD`
- `STEWARD_V12_VERIFIED_FINISH=HOLD`

## 8. NEXT ACTION — Single project next work

`STEWARD_V12_FULL_CHAIN_PREFLIGHT_AND_IMPLEMENTATION_PLAN`

Perform a complete preflight against current GitHub and OSi exact HEADs, resolve daily GitHub / Cloudflare 24-hour scope, and implement the **one bounded v1.2 difference** using the current canonical Steward and pre-existing tests. Publish a fresh PR-scoped CI receipt, then OSi field receipt, then Human Threshold and Verified Finish.

**ENGÜRÜ Final System Execution Engineering™**: **1 Ana Hedef = 1 Proje → 1 Uçtan Uca Ön Analiz ve Simülasyon → 1 Bütünleşik Yürütme → 1 Doğrulanmış Teslim.**
