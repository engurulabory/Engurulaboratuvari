# ENGÜRÜ Mac Engineer™ — Current Status

**Updated:** 2026-09-22  
**Program target:** ENGÜRÜ Mac Engineer™ v1.1 — Verified Product Engineering Operator  
**Current version:** v0.6 — Field Closeout Active  
**Current objective:** Package 6 — Checkpoint / Restart / Same-Task Resume Field Proof  
**Canonical objective id:** `CHECKPOINT_RESTART_RESUME_FIELD_PROOF`  
**Current verdict:** HOLD — context-durability product patch is locally VERIFIED PASS; GitHub publication, re-commissioning and real restart/resume proof remain

## 1. STATE

ENGÜRÜ Mac Engineer™ v0.6 is **not yet VERIFIED FINAL / LOCKED**.

The continuity patch is fully integrated into product exact-main `6d2fcd923e8fa0417a2e7787acd0dcef6b25e544` and is now commissioned onto the Mac execution surfaces. Exact-main Product CI Evidence was refreshed to run `35711368049`; rebuild/install completed with runtime source parity **31/31 exact**; runtime/app provenance binds the same product SHA across product source, provenance and install evidence; installed app + runtime process are live. The active objective is now the real checkpoint → runtime restart → same-task resume field proof.

## 2. CANONICAL SURFACES

- Control plane: `engurulabory/Engurulaboratuvari`
- Control-plane exact-main: `09bdf578ea90666615c2333704516c91f850e668` — Final Gate / IP Gate / Fleet PASS
- Product source: `engurulabory/enguru-mac-engineer`
- Mac product checkout: `~/Enguru/Projects/enguru-mac-engineer`
- Product canonical branch: `main`
- Product continuity patch head: `78dc4aaebbce4fd69ccfdc35544ea49454b27c2b`
- Product exact-main / merge SHA: `6d2fcd923e8fa0417a2e7787acd0dcef6b25e544`
- Product exact-main CI: `35711368049` — PASS
- Runtime: `~/Enguru/Runtime/MacEngineer`
- Installed app: `~/Applications/ENGÜRÜ Mac Engineer.app`
- Local Evidence: `~/Enguru/Evidence/MacEngineer/v0.6`

Authorized in-flight context-durability product patch:

- branch: `fix/v06-context-durability-resume-routing`
- base/head before commit: `6d2fcd923e8fa0417a2e7787acd0dcef6b25e544`
- exact scope:
  1. `runtime/app.py`
  2. `runtime/cockpit_store.py`
  3. `runtime/field_reliability.py`
  4. `runtime/static/index.html`
  5. `runtime/tests/test_context_durability.py`

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
- Real Mac engineering task — VERIFIED PASS, stage 5/7
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
- verified real-task stage: 5/7

The continuity patch exists to preserve the same canonical task/checkpoint/repository identity through runtime restart and resume while reusing the existing ReliabilityManager mechanisms.

The active acceptance gate is:

`TARGETED_REPEATABILITY=5/5_PASS + FULL_RUNTIME_REGRESSION=PASS + DIFF_CHECK=PASS + PATCH_SCOPE=3_FILES_PASS + PRODUCT_RUNTIME_CACHE_COUNT=0`

## 5. LATEST OBSERVED RESULT

### Context Durability Product Patch — PUBLICATION STAGE PASS

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

Close the smallest sufficient conversation/context durability gap inside the existing persistent-working-memory and durable-task path, then repeat the same restart/resume proof.

Acceptance requires:

1. canonical task/checkpoint/current objective remain pinned across long conversations;
2. active context uses bounded recent turns + durable state + rolling compact summary rather than unbounded raw replay;
3. compaction is automatic and silent before user-visible pressure;
4. warning threshold is near genuine provider/context capacity and is informational, not a task verdict;
5. archive cleanup cannot remove active task/checkpoint/current-status truth;
6. resume returns real changed-file/test/SHA/Evidence values;
7. same reliability task is reused with expected duplicate/recovered semantics;
8. regression PASS and post-restart Evidence bind to the same durable task.

Only after that Evidence may the real Mac task advance from 5/7 to 6/7.

## 7. REMAINING v0.6 CLOSEOUT — CANONICAL ORDER

1. **Continuity fixture / resume correction** — PASS
2. **Continuity Patch Repeatability Gate** — VERIFIED PASS
3. **Product patch GitHub engineering** — VERIFIED PASS
4. **Continuity patch exact-main Mac commissioning** — VERIFIED PASS
5. **Mac checkpoint/restart/same-task resume field proof** — HOLD / context durability hardening active
6. **Recovery field proof** — bounded recoverable failure → diagnosis → smallest recovery → reverify
7. **Local Evidence bundle**
8. **Mac Local Mandatory DoneCheck™**
9. **WORKLIST + SESSION_STATE + Current Status reconciliation**
10. **v0.6 VERIFIED FINAL / LOCKED**

Only after item 9 may v0.6 be described as finished.

## 8. AFTER v0.6

Canonical program line:

`v0.7 Long-Running Reliability → v0.8 Product Engineering Operator → v0.9 World-Class Field Benchmark → v1.0 milestone → v1.1 Verified Product Engineering Operator`

The program target remains v1.1.

## 9. NEXT ACTION

**Single next action:** create the product PR from `fix/v06-context-durability-resume-routing` at exact head `f980a47716eaace5b4fb1d9e37cc95ff0a1b5da2`, verify exact-head Product CI, merge, and verify product exact-main CI.

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

**v0.6 FIELD CLOSEOUT ACTIVE / RESTART-RESUME FIELD HOLD.**  
Exact-main commissioning remains VERIFIED PASS. The latest real resume attempt preserved the visible task/checkpoint prompt but returned non-actionable Evidence while the conversation-pressure warning fired. The bounded next difference is long-running conversation/context durability inside the existing working-memory path.
