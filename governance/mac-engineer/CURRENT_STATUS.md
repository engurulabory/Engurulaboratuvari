# ENGÜRÜ Mac Engineer™ — Current Status

**Updated:** 2026-09-22
**Program target:** ENGÜRÜ Mac Engineer™ v1.1 — Verified Product Engineering Operator
**Current version:** v0.6 — Field Closeout Active
**Current objective:** Package 6 — Recovery Field Proof (7/7)
**Canonical objective id:** `RECOVERY_FIELD_PROOF_RECONCILIATION`

<!-- ENGURU_V06_RECOVERY_SHA_RECONCILIATION_START -->
## Latest material Evidence — bounded recovery commissioning

**COMPLETED / CHANGED WORK**

- Bounded recovery product patch merged through product PR #8.
- Current product exact-main: `7f2e22994d17b913f226eb05691d934f81e1c212`.
- Product exact-main CI run `35753607274`: **PASS**.
- Exact-SHA Mac rebuild/install: **PASS**.
- Runtime source parity: **34/34 EXACT**.
- Runtime/App provenance binding: **PASS**.
- Controlled recovery field fault remains preserved for installed-app acceptance.

**LATEST EVIDENCE**

- `~/Enguru/Evidence/MacEngineer/v0.6/package6-product-ci-exact-main.json`
- `~/Enguru/Evidence/MacEngineer/v0.6/package6-exact-sha-rebuild-install.json`
- `~/Enguru/Evidence/MacEngineer/v0.6/package6-runtime-app-provenance-closure.json`

**JUDGMENT**

GitHub engineering and Mac last-mile commissioning for the bounded recovery capability are **VERIFIED PASS**. Real Mac engineering task remains **6/7 VERIFIED PASS** until the installed app executes the preserved bounded recovery and independent post-recovery verification passes.

**CURRENT OBJECTIVE**

`RECOVERY_FIELD_PROOF_RECONCILIATION`

**REMAINING WORK**

Installed-app bounded recovery → independent post-recovery verification → Local Evidence Bundle → Mandatory DoneCheck™ → v0.6 VERIFIED FINAL / LOCKED.

**NEXT ACTION**

Publish this canonical SHA reconciliation, verify control-plane exact-main, refresh canonical context, then execute the preserved recovery field proof through the installed ENGÜRÜ Mac Engineer™ app.
<!-- ENGURU_V06_RECOVERY_SHA_RECONCILIATION_END -->
**Current verdict:** PASS — restart/resume field continuity is VERIFIED PASS at 6/7; bounded Recovery Field Proof is the single active gate

## 1. STATE

ENGÜRÜ Mac Engineer™ v0.6 is **not yet VERIFIED FINAL / LOCKED**.

The fresh resume-verification patch is fully integrated into product exact-main `8e8d7db9ae811a5855697604800c830334944c1f`; exact-head Product CI run `35738998097` and exact-main Product CI run `35739072411` are completed/success. That exact-main has now been re-commissioned on the real Mac runtime/app, the runtime was restarted, and the installed app returned fresh same-task/checkpoint Evidence with `recovered=True`, `cached=False`, `fresh_revalidation=True`. Real Mac task continuity is therefore VERIFIED PASS at 6/7.

## 2. CANONICAL SURFACES

- Control plane: `engurulabory/Engurulaboratuvari`
- Control-plane exact-main: resolved live by canonical `session-start`; latest publication-status baseline before this update: `8851a5da50705bcc06e90b0ef24b996ad095156c` — Final Gate / IP Gate / Fleet PASS
- Product source: `engurulabory/enguru-mac-engineer`
- Mac product checkout: `~/Enguru/Projects/enguru-mac-engineer`
- Product canonical branch: `main`
- Product continuity patch head: `78dc4aaebbce4fd69ccfdc35544ea49454b27c2b`
- Product exact-main / merge SHA: `8e8d7db9ae811a5855697604800c830334944c1f`
- Product exact-main CI: `35739072411` — PASS
- Runtime: `~/Enguru/Runtime/MacEngineer`
- Installed app: `~/Applications/ENGÜRÜ Mac Engineer.app`
- Local Evidence: `~/Enguru/Evidence/MacEngineer/v0.6`

Authorized in-flight fresh resume-verification product patch:

- branch: `fix/v06-fresh-resume-verification`
- base/head before commit: `125be3a4b01b3a4de5faf949c79372de1d249aaf`
- exact scope:
  1. `runtime/app.py`
  2. `runtime/field_reliability.py`
  3. `runtime/tests/test_field_resume_verification.py`

Exact dirty pre-commit and exact clean one-commit-ahead post-commit states are authorized for this objective only. Any branch/head/base/path/commit-count drift remains fail-closed HOLD.

## 3. COMPLETED / VERIFIED

The following v0.6 truths are already closed and remain preserved:

- GitHub engineering closeout — VERIFIED / LOCKED
- Local product-source bootstrap — PASS
- Mac layout audit — PASS
- Dedicated product source authority — PASS
- Product CI exact-main — PASS
- v0.6 source/version alignment — PASS
- Exact-SHA rebuild/install — PASS
- Runtime/app provenance — PASS
- Continuity patch exact-main Mac commissioning — VERIFIED PASS: CI evidence 35711368049, product SHA 6d2fcd923e8fa0417a2e7787acd0dcef6b25e544, runtime parity 31/31 exact, live app/runtime processes
- Archive decision — PASS / preserve-first
- Real Mac engineering task — VERIFIED PASS, stage 6/7
- Session continuity bootstrap — PASS
- GitHub ↔ Mac session-state reconciliation — PASS
- Bounded in-flight dirty-patch authorization — PASS
- Porcelain dirty-path parser regression — PASS
- Runtime generated-cache reconciliation — PASS; tracked cache absent; runtime cache count returned to 0
- Continuity fixture/resume correction — PASS
- Continuity Patch Repeatability Gate — VERIFIED PASS: 5/5 targeted + 35/35 regression + diff + exact scope + cache=0
- Product-patch publication session binding — PASS
- Product Patch GitHub Engineering — VERIFIED PASS: PR #5 + exact-head CI + merge + exact-main CI + local/remote main parity

## 4. CURRENT ENGINEERING TRUTH

Canonical real task:

- task id: `ENGURU-V06-FIELD-001`
- checkpoint id: `v06-field-cp-001`
- verified real-task stage: 6/7

The restart/resume continuity gate is now VERIFIED PASS at 6/7. The single active field objective is bounded Recovery Field Proof.

The active acceptance gate is:

`RECOVERABLE_FAILURE_OBSERVED + ROOT_CAUSE_IDENTIFIED + SMALLEST_RECOVERY_APPLIED + REVERIFICATION_PASS + EVIDENCE_RECORDED + AUTHORITY_PRESERVED`

## 5. LATEST OBSERVED RESULT

### Restart / Same-Task Resume Field Proof — VERIFIED PASS (6/7)

- product exact-main: `8e8d7db9ae811a5855697604800c830334944c1f`
- control authority: **PASS**
- canonical context exact-main binding: **PASS**
- exact-main Product CI Evidence: **PASS**
- rebuild preflight: **PASS**
- exact-SHA rebuild/install: **PASS**
- runtime/app provenance: **PASS**
- field fixture truth: **PASS**
- real runtime restart: **PASS**
- canonical resume prompt identity: **PASS**
- task id: `ENGURU-V06-FIELD-001`
- checkpoint id: `v06-field-cp-001`
- reliability task id: `task_94b95c63865a45db80b85ccba95f8119`
- changed: `CURRENT_STATE.md`
- test count: **1**
- fixture SHA: `f563a779f6d01a46e037e4330383c3adb032d426`
- test code: **0**
- worktree unchanged during fresh revalidation: **true**
- recovered: **true**
- cached: **false**
- fresh revalidation: **true**
- installed-app verdict: **PASS**
- real Mac task stage: **6/7 VERIFIED PASS**

**JUDGMENT:** post-restart continuity Evidence is accepted. The single remaining field gate is bounded Recovery Field Proof.


### Fresh Resume Verification GitHub Engineering — VERIFIED PASS

- product patch head: `cc64be04c123f57dfe23fa34581a6b85c15d935f`
- exact-head Product CI run: **35738998097 — PASS**
- product PR: **MERGED**
- merge / new product exact-main: `8e8d7db9ae811a5855697604800c830334944c1f`
- exact-main Product CI run: **35739072411 — PASS**
- local product `main` = remote `origin/main`: **PASS**
- local worktree: **clean**
- final verdict: **FRESH_RESUME_GITHUB_ENGINEERING=PASS**
- real Mac task remains **5/7** only until this exact-main is commissioned and the installed app returns fresh same-task/checkpoint Evidence



### Fresh Resume Verification Patch — PUBLICATION STAGE PASS

- branch: `fix/v06-fresh-resume-verification`
- base exact-main: `125be3a4b01b3a4de5faf949c79372de1d249aaf`
- committed patch head: `cc64be04c123f57dfe23fa34581a6b85c15d935f`
- exact committed scope: **3 files**
- post-commit worktree: **clean**
- ahead of main: **1**
- push: **PASS**
- local HEAD = remote branch HEAD: **PASS**
- post-commit session continuity: **PASS**
- publication verdict: **FRESH_RESUME_PUBLICATION_STAGE=PASS**
- real Mac task remains **5/7** until this exact patch is merged, commissioned and proven in the installed app



### Fresh Resume Verification Patch — LOCAL VERIFIED PASS

- product branch: `fix/v06-fresh-resume-verification`
- base exact-main: `125be3a4b01b3a4de5faf949c79372de1d249aaf`
- exact durable schema: **PASS**
- fixture truth: **PASS**
- resume route before generic repair: **PASS**
- legacy COMPLETE task binding: **PASS**
- fresh post-restart revalidation: **PASS**
- focused resume regression: **PASS**
- full runtime regression: **43 tests PASS**
- exact patch scope: **3 files PASS**
- `git diff --check`: **PASS**
- runtime cache count: **0**
- final local verdict: **V06_FRESH_RESUME_VERIFICATION_PATCH=PASS**
- real Mac task remains **5/7** until this exact patch is published, commissioned, and the installed app returns fresh same-task/checkpoint Evidence



### Exact Resume Routing Diagnosis — PASS / REQUIRED DIFFERENCE NARROWED

Observed durable task:

- reliability task: `task_94b95c63865a45db80b85ccba95f8119`
- task state: **COMPLETE**
- sequence: **7**
- checkpoint digest: `7b2a7ae3cf93f42335d3954905ae222ac8f9a3dc729127d77c4717bc97c5d399`
- legacy structured metadata `canonical_task_id`: **missing**
- legacy structured metadata `checkpoint_id`: **missing**
- fixture HEAD: `f563a779f6d01a46e037e4330383c3adb032d426`
- fixture working difference: **CURRENT_STATE.md only**
- CURRENT_STATE repair content remains present with **1/1 PASS** truth
- diagnostic checkpoint reader returned null fields; this is treated as **schema-read inconclusive**, not checkpoint absence, because the durable task itself retains a checkpoint digest and earlier evidence established persisted checkpoint/LKG surfaces

Required difference is now bounded to one resume package:

1. canonical resume intent must route before generic truth-reconcile handling;
2. the pre-patch COMPLETE durable commissioning task must be safely recognized as the same canonical task despite missing structured metadata;
3. post-restart verification must execute a **fresh** repository test/diff read rather than merely return a cached terminal result;
4. successful result must preserve the same canonical task/checkpoint identity and produce real post-restart Evidence.



### Real Restart / Same-Task Resume Attempt — HOLD / ROUTING DIFFERENCE REMAINS

Observed after exact-main context-durability re-commission and real installed-app restart:

- canonical resume prompt used task `ENGURU-V06-FIELD-001`
- canonical checkpoint `v06-field-cp-001`
- application response:
  - STATE: canonical state reconciliation executed
  - CLAIM: executable truth passed through repair chain
  - EVIDENCE: `changed=None test_count=None sha=None rollback=False`
  - VERDICT: **HOLD**
- field task remains **5/7**
- context-warning symptom is no longer the active blocker
- classification: **resume intent is still reaching a generic repair/reconciliation path instead of the deterministic same-task field continuity path**

Required difference is now bounded to the exact `execute_local_field_task → field_reliability` resume-routing / intent-classification chain.



### Context Durability Exact-Main Mac Re-Commission — VERIFIED PASS

- product exact-main: `125be3a4b01b3a4de5faf949c79372de1d249aaf`
- local product `main` = `origin/main`: **PASS**
- exact-main Product CI Evidence: **PASS**
- canonical context exact-main binding: **PASS**
- rebuild preflight: **PASS**
- exact-SHA rebuild/install: **PASS**
- runtime/app provenance: **PASS**
- post-commission session continuity: **PASS**
- final verdict: **CONTEXT_DURABILITY_EXACT_MAIN_RECOMMISSION=PASS**
- real Mac task remains **5/7** only until the governed restart + same-task resume field proof succeeds



### Context Durability GitHub Engineering — VERIFIED PASS

- product PR: **#6 — MERGED**
- exact-head: `f980a47716eaace5b4fb1d9e37cc95ff0a1b5da2`
- exact-head Product CI run: **35724995225 — completed/success**
- merge SHA / new product exact-main: `125be3a4b01b3a4de5faf949c79372de1d249aaf`
- exact-main Product CI run: **35726087972 — completed/success**
- local product `main` = remote `origin/main`: **PASS**
- local product worktree: **clean**
- final verdict: **CONTEXT_DURABILITY_GITHUB_ENGINEERING=PASS**
- real Mac task remains **5/7** until this exact-main is commissioned and the same-task restart/resume field proof passes



### Product PR #6 Exact-Head Product CI — VERIFIED PASS

- product PR: **#6**
- PR state: **OPEN**
- merge state: **CLEAN**
- PR head: `f980a47716eaace5b4fb1d9e37cc95ff0a1b5da2` — exact expected head
- PR base: `6d2fcd923e8fa0417a2e7787acd0dcef6b25e544` — exact expected base
- workflow: `ENGURU Mac Engineer Product CI`
- exact-head run: **35724995225**
- event: `pull_request`
- status: `completed`
- conclusion: **success**
- check name: `product-ci`
- CI visibility HOLD: **resolved as registration timing only**
- merge: pending
- real Mac task remains **5/7**



### Context Durability Product Patch — PUBLICATION STAGE PASS

- control-plane publication status PR: **#148** — merged
- PR #148 exact-main Final Gate / IP Gate / Fleet: **PASS**

- product branch: `fix/v06-context-durability-resume-routing`
- base exact-main: `6d2fcd923e8fa0417a2e7787acd0dcef6b25e544`
- committed patch HEAD: `f980a47716eaace5b4fb1d9e37cc95ff0a1b5da2`
- committed scope: exact 5 files
- post-commit worktree: clean
- ahead of main: exactly 1 commit
- push: **PASS**
- local HEAD = remote branch HEAD: **PASS**
- post-commit session continuity: **PASS**
- publication verdict: **CONTEXT_DURABILITY_PUBLICATION_STAGE=PASS**

The verified product patch is now published to the remote feature branch. Product PR → exact-head Product CI → merge → exact-main Product CI is the next engineering step. Real Mac task remains **5/7** until re-commissioned field restart/resume succeeds.



### Context-durability publication authority — VERIFIED PASS

- control-plane reconciliation PR: **#146**
- merge / control-plane exact-main: `30aa6555f494a83da4eaa798a0f0687ef3106558`
- exact-main ENGURU Labory Final Gate: **PASS**
- exact-main IP Model Trust Gate: **PASS**
- exact-main IP Model Trust Fleet: **PASS**
- exact dirty pre-commit product state: authorized only for the recorded 5-file context-durability patch
- exact clean one-commit-ahead post-commit state: authorized only for the same branch/base/diff
- unexpected path / branch / base / commit-count drift: fail-closed HOLD
- next action remains: product patch commit → push



### Context Durability Product Patch — LOCAL VERIFIED PASS

- product branch: `fix/v06-context-durability-resume-routing`
- base exact-main: `6d2fcd923e8fa0417a2e7787acd0dcef6b25e544`
- identity parser: colon + equals syntax **PASS**
- canonical-context injection: **PASS**
- durable task pinning: **PASS**
- bounded recent history: **96 messages / 48,000 chars**
- active-context warning policy: **PASS**
- focused context-durability regression: **PASS**
- full runtime regression: **40 tests PASS**
- exact patch scope: **5 files PASS**
- `git diff --check`: **PASS**
- generated runtime cache reconciled: **0**
- final local verdict: **V06_CONTEXT_DURABILITY_PATCH=PASS**

The product patch is verified locally but is not yet GitHub-published or commissioned onto the installed/runtime surfaces. Real Mac task therefore remains **5/7**.



### Governed canonical-context refresh binding — VERIFIED PASS

- control-plane PR: **#144**
- exact-head controls: **PASS**
- merge / control-plane exact-main: `34bbe6888196c2627ab5d66faa8182637be78165`
- exact-main ENGURU Labory Final Gate: **PASS**
- exact-main IP Model Trust Gate: **PASS**
- exact-main IP Model Trust Fleet: **PASS**
- `session-start` now refreshes `canonical-context.json` before continuity start
- `refresh-real-task-runtime` now refreshes `canonical-context.json` before runtime restart
- context-sync HOLD remains fail-closed and stops the target action
- focused control-plane regression added

This closes the stale canonical-context **refresh-path** half of the root cause. Product runtime still requires the bounded companion patch for identity parsing, canonical-context injection/pinning, longer bounded history and near-capacity-only warning behavior.



### Restart / same-task resume field attempt — HOLD / CONTEXT DURABILITY REQUIRED

Observed in the installed ENGÜRÜ Mac Engineer™ v0.6 conversation after the governed restart:

- canonical resume prompt carried the correct task id `ENGURU-V06-FIELD-001`;
- canonical checkpoint id `v06-field-cp-001` was present;
- the application returned `VERDICT — HOLD`;
- response Evidence was non-actionable: `changed=None test_count=None sha=None rollback=False`;
- the UI simultaneously displayed an early conversation-pressure warning: `Bu sohbet ağırlaşıyor. Yeni sohbet açmak daha sağlıklı.`;
- the field task therefore remains **5/7**; restart/resume PASS is not yet evidenced.

This is treated as a reliability/working-memory gap inside the existing conversation + durable-task layers, not as a new core.

Required product behavior:

1. long-running conversation/project work remains durable across many turns;
2. full transcript may stay locally persisted while the active model context is budgeted;
3. canonical task/checkpoint/Evidence/current objective are always pinned into active context;
4. older turns may be compacted into evidence-backed rolling summaries without losing task identity;
5. archive cleanup stays separate from active durable task/current-state records;
6. context pressure is measured by real active-context utilization, not a small message-count heuristic;
7. background compaction begins silently before pressure becomes user-visible;
8. user warning appears only near genuine capacity;
9. context pressure never converts an otherwise valid task into `changed=None / test_count=None / sha=None`;
10. near-capacity handoff preserves exact task/checkpoint/current-status state.



### Continuity Patch Exact-Main Mac Commissioning — VERIFIED PASS

- exact-main Product CI Evidence: **PASS**
- product SHA / local main / origin-main / remote-main: `6d2fcd923e8fa0417a2e7787acd0dcef6b25e544`
- Product CI run: `35711368049` — completed/success
- rebuild preflight: **PASS**
- exact-SHA rebuild/install: **PASS**
- runtime source parity after install: **31/31 EXACT**
- backup prepared: **yes**
- rollback used: **no**
- installed app: v0.6
- runtime-build app: v0.6
- product source SHA = provenance SHA = install Evidence SHA: **true**
- installed executable hash = runtime-build executable hash = provenance executable hash: **true**
- live `/api/status`: **RUNNING**
- installed app process: **PASS**
- runtime process: **PASS**
- post-commission session-start: **PASS**
- final verdict: **CONTINUITY_PATCH_EXACT_MAIN_COMMISSIONING=PASS**



### Exact-main Mac commissioning attempt — HOLD / REQUIRED DIFFERENCE IDENTIFIED

- control-plane session-start: **PASS**
- product local `main` = `origin/main` = `6d2fcd923e8fa0417a2e7787acd0dcef6b25e544`
- product worktree: **clean**
- rebuild preflight: **PASS**
- preflight runtime delta: 31 product files / 30 current files / 28 exact / 2 changed / 1 missing / 0 current-only
- expected new continuity delta: `app.py` changed, `field_reliability.py` changed, `tests/test_field_continuity_binding.py` missing from current runtime
- exact-SHA rebuild/install: **HOLD**
- issue: `CI_EVIDENCE_SOURCE_SHA_MISMATCH`
- mutation started: **no**
- backup created: **no**

Root cause: the rebuild/install gate reads local `package6-product-ci-exact-main.json`. That evidence still points to the previous product exact-main and has not yet been refreshed to the new exact-main `6d2fcd923...` / Product CI run `35711368049`.



### Control-plane reconciliation — PASS

- status reconciliation PR: **#136**
- control-plane exact-main: `6c8bbf8832ea1c1408b87d9879b3a1cfa83a8036`
- ENGURU Labory Final Gate: **PASS**
- IP Model Trust Gate: **PASS**
- IP Model Trust Fleet: **PASS**
- active objective remains: `CONTINUITY_PATCH_EXACT_MAIN_COMMISSIONING`


### Product Patch GitHub Engineering — VERIFIED PASS

- product PR: **#5**
- PR head: `78dc4aaebbce4fd69ccfdc35544ea49454b27c2b`
- PR base: `6f424c0b815d8c0cf8aa761124be3f743e412ee1`
- exact-head Product CI: **PASS**
- merge SHA / product exact-main: `6d2fcd923e8fa0417a2e7787acd0dcef6b25e544`
- exact-main Product CI run: `35711368049`
- exact-main Product CI: **completed/success**
- local product main = remote product main: **PASS**
- local worktree: **clean**
- final verdict: **PRODUCT_PATCH_GITHUB_ENGINEERING=PASS**

The earlier ChatGPT connector 404 was limited to that connector access surface and was resolved operationally through the authenticated Mac-local GitHub CLI.



### Product patch publication stage — PASS

- branch: `fix/v06-durable-continuity-binding`
- base main: `6f424c0b815d8c0cf8aa761124be3f743e412ee1`
- commit: `78dc4aaebbce4fd69ccfdc35544ea49454b27c2b`
- commit message: `fix: preserve durable field continuity across restart`
- committed scope: exactly 3 authorized files
- worktree after commit: clean
- ahead of main: 1 commit
- push: PASS
- local HEAD = remote branch HEAD: PASS
- publication stage verdict: **PASS**



### Cache gate

Initial repeatability run stopped safely because 10 generated Python cache artifacts were present.

Reconciliation proved:

- tracked cache: none
- generated cache cleanup: PASS
- `PRODUCT_RUNTIME_CACHE_COUNT=0`
- patch scope remained exactly the authorized three files
- `git diff --check`: PASS

### Repeatability run — VERIFIED PASS

Latest final integrity result:

- targeted continuity repeatability: **5/5 PASS**
- full runtime regression: **35 tests PASS**
- full runtime regression verdict: **PASS**
- diff check: **PASS**
- patch scope: exactly the authorized three files
- observed generated cache entries: `runtime/__pycache__` + `runtime/__pycache__/reliability.cpython-314.pyc`
- tracked cache authority check: **PASS — none tracked**
- generated cache reconciliation: **PASS**
- final runtime cache count: **0**
- final gate verdict: **CONTINUITY_PATCH_REPEATABILITY_GATE=PASS**

The continuity repeatability acceptance is now closed.

### Long-conversation durability discovery — EXACT READ-ONLY RESULT

Observed product authority:

- branch: `main`
- local HEAD = origin/main = `6d2fcd923e8fa0417a2e7787acd0dcef6b25e544`
- source integrity: clean

Observed runtime durable-state surfaces:

- `checkpoints/task_*.json` + `.lkg.json`
- `tasks/task_*.json`
- `logs/task-journal.jsonl`
- `state/canonical-context.json`
- `state/task-idempotency.json`
- `state/task-writer.lock`

Storage remains small:

- runtime: ~1.3 MB
- v0.6 Evidence: ~308 KB

Exact discovery findings:

- warning source is confirmed in product code:
  - `runtime/app.py` lines around 828–843;
  - `runtime/static/index.html` lines around 1148–1151;
- message/context assembly exists in `runtime/app.py` around history/context/message construction;
- canonical task/checkpoint are persisted in runtime and Evidence;
- exact durable task record: `tasks/task_94b95c63865a45db80b85ccba95f8119.json`;
- that task record contains both canonical ids and is currently internal state `COMPLETE`;
- `state/cockpit.json` also contains the canonical ids;
- `state/task-idempotency.json` does not contain literal canonical ids because its top-level keys are digests; this is not by itself evidence of loss;
- `logs/task-journal.jsonl` contains no literal canonical-id match;
- `state/canonical-context.json` is stale relative to current truth:
  - observed_at = `2026-09-21T20:17:20.743204Z`;
  - activeObjective = `Package 6 — Runtime/App Provenance Closure`;
  - sessionStateObjective = `RUNTIME_APP_PROVENANCE_CLOSURE`;
  - method is also the older pre-CURRENT_STATUS chain.

Root cause is now materially resolved:

1. **Warning heuristic is early and disconnected from active model context.**
   - chat DENSE: >=30 messages or >=7,000 chars;
   - chat HEAVY: >=60 messages or >=14,000 chars;
   - work DENSE: >=80 messages or >=20,000 chars;
   - work HEAVY: >=150 messages or >=40,000 chars.
   These weights are computed from the full stored transcript, while provider history is separately bounded to 24 messages / 12,000 chars. The current banner therefore measures archive size, not actual active-context saturation.

2. **Resume identity parser rejects the syntax emitted by the real resume handoff.**
   - `commissioning_identity()` accepts only `task_id: VALUE` and `checkpoint_id: VALUE`;
   - the real handoff uses `task_id=ENGURU-V06-FIELD-001` and `checkpoint_id=v06-field-cp-001`;
   - the observed durable task metadata stores those ids only inside `user_intent`, not as structured `canonical_task_id` / `checkpoint_id` fields;
   - therefore same-task deterministic commissioning identity was not structurally recovered on the field resume attempt.

3. **Canonical context refresh is decoupled from session start.**
   - `sync-context` exists and writes `state/canonical-context.json`;
   - `session-start` does not invoke it;
   - product chat context construction does not currently load `canonical-context.json` into `CURRENT LOCAL CONTEXT`;
   - the runtime context therefore remained at the earlier Runtime/App Provenance objective.

**Judgment:** durable persistence works; the bounded gap is identity parsing + canonical-context injection/refresh + misleading transcript-weight warning.

## 6. REQUIRED DIFFERENCE

Close the single remaining real field gap through one bounded recovery proof on the existing Mac runtime/fixture path.

Acceptance requires:

1. one real recoverable failure is observed and recorded;
2. root cause is identified from direct Evidence;
3. the smallest sufficient recovery is applied;
4. the same affected path is reverified successfully;
5. repository/runtime truth is preserved without unrelated mutation;
6. Human Threshold™ and authority boundaries remain unchanged;
7. recovery Evidence is written to the local v0.6 Evidence surface;
8. unresolved critical failures remain zero.

Only after that Evidence may the real Mac task advance from 6/7 to 7/7.

## 7. REMAINING v0.6 CLOSEOUT — CANONICAL ORDER

1. **Continuity fixture / resume correction** — PASS
2. **Continuity Patch Repeatability Gate** — VERIFIED PASS
3. **Product patch GitHub engineering** — VERIFIED PASS
4. **Continuity patch exact-main Mac commissioning** — VERIFIED PASS
5. **Mac checkpoint/restart/same-task resume field proof** — **6/7 VERIFIED PASS**
6. **Recovery field proof** — **ACTIVE / 7/7**
7. **Local Evidence bundle**
8. **Mac Local Mandatory DoneCheck™**
9. **WORKLIST + SESSION_STATE + Current Status reconciliation**
10. **v0.6 VERIFIED FINAL / LOCKED**

Only after item 10 may v0.6 be described as finished.

## 8. AFTER v0.6

Canonical program line:

`v0.7 Long-Running Reliability → v0.8 Product Engineering Operator → v0.9 World-Class Field Benchmark → v1.0 milestone → v1.1 Verified Product Engineering Operator`

The program target remains v1.1.

## 9. NEXT ACTION

**Single next action:** execute one bounded recoverable failure scenario on the real Mac field fixture/runtime, verify diagnosis → smallest recovery → revalidation → Evidence, and close 7/7 only from observed recovery proof.

## 9.1 MAINTENANCE RULE

This file is a living canonical status surface during active development.

After every material work package or PASS / HOLD / BLOCKED verification result, update this file before the next action so it reflects:

- completed or changed work;
- latest Evidence;
- current judgment;
- active objective;
- remaining canonical work;
- single next action.

The purpose is continuous session handoff: a fresh ChatGPT session should understand the latest state directly from GitHub without reconstructing it from chat history.

## 10. NEW SESSION BOOTSTRAP

A new ChatGPT session must first read:

1. `governance/mac-engineer/SESSION_CONTINUITY_CONTRACT_V1.md`
2. `governance/mac-engineer/ACTIVE_WORKING_PATH.md`
3. `governance/mac-engineer/CURRENT_STATUS.md`
4. `governance/mac-engineer/SESSION_STATE_V1.json`
5. `governance/mac-engineer/PRODUCT_ROADMAP_V1.json`
6. the ENGÜRÜ Mac Engineer™ section of `WORKLIST.md`
7. relevant current GitHub commit / PR / CI and Mac-local Evidence

Canonical session start:

```bash
cd "$HOME/Enguru/Projects/Engurulaboratuvari" &&
git fetch origin main &&
git checkout main &&
git pull --ff-only origin main &&
python3 tools/mac_engineer_control.py session-start
```

The new session continues from the single active objective and the single required difference recorded above.

## JUDGMENT

**v0.6 FIELD CLOSEOUT ACTIVE / 6 OF 7 VERIFIED PASS.**
Checkpoint → runtime restart → same-task resume continuity is VERIFIED PASS on the installed app with fresh, non-cached repository revalidation. The single active field gate is bounded Recovery Field Proof (7/7).
