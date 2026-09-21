# ENGÜRÜ Mac Engineer™ v0.6 — Package 6 Mac Local Final Commissioning v0.1

## STATE

TOOLING CANDIDATE — GitHub-side commissioning harness can be verified in CI; product-level Package 6 remains HOLD until the user's real Mac produces local field Evidence.

## NIYET

Prove that the exact canonical GitHub engineering result is the same system that actually runs, persists, recovers and completes a real engineering task on the user's Mac.

## Environment authority

- **GitHub = canonical source / version / CI / engineering Evidence.**
- **Mac local = real runtime / user operating environment / final field Evidence.**

Neither side substitutes for the other.

Canonical closure:

`GitHub exact-main PASS → Mac exact-main sync → runtime discovery → runtime READY → real task → checkpoint → restart → resume → recoverable failure → bounded recovery → reverify → local Evidence → Mac Local Mandatory DoneCheck™ → v0.6 VERIFIED FINAL / LOCKED`

## Phase 1 — Local discovery

Run from the canonical Labory checkout:

```bash
git fetch origin main
python3 tools/mac_engineer_local_discovery.py
```

Default local evidence path:

`~/Enguru/Evidence/MacEngineer/v0.6/package6-local-discovery.json`

The discovery harness is non-destructive. It observes:

- macOS platform truth;
- canonical checkout branch / HEAD / origin-main / cleanliness;
- repositories under `~/Enguru`;
- likely Engürü / Mac Engineer / OSi `.app` candidates;
- relevant running processes;
- Shared AI `127.0.0.1:8787/health`;
- Ollama `127.0.0.1:11434/api/tags`.

Discovery deliberately returns HOLD when a real engineering task has not yet been commissioned.

## Phase 2 — Exact-main sync

Required before execution:

- current branch = `main`;
- local HEAD = `origin/main`;
- worktree is clean or explicitly reconciled;
- no stale local copy is treated as canonical runtime.

A divergent or dirty checkout produces HOLD.

## Phase 2.5 — Runtime provenance discovery

After exact-main sync and before the real task, fingerprint the installed Mac Engineer app/runtime:

```bash
python3 tools/mac_engineer_runtime_provenance.py
```

Default evidence:

`~/Enguru/Evidence/MacEngineer/v0.6/package6-runtime-provenance.json`

The tool records the installed app bundle identity, executable SHA-256, runtime files/metadata candidates, active Mac Engineer processes and any existing source/version signals. It does **not** invent provenance from app names.

PASS requires an existing evidence-backed source/version signal matching the canonical GitHub HEAD. If no such signal exists, state remains `HOLD — RUNTIME_PROVENANCE_UNBOUND`.

## Phase 3 — Runtime identity

The discovery evidence must identify the actual Mac Engineer execution surface.

Accepted runtime identity evidence may include:

- native `.app` bundle path + bundle/executable identity;
- canonical local command/runtime path;
- running process identity;
- Shared AI local route;
- Ollama local provider/model.

Shared AI by itself is a supporting runtime layer. It is not automatically treated as the full Mac Engineer product.

Required local AI route for the current locked v0.6 path:

- provider: `local_runtime`;
- model: `qwen3:14b`;
- Shared AI route: PASS.

## Phase 4 — Real Mac engineering task

Health checks do not satisfy this phase.

A real task must:

1. have one durable task ID;
2. operate through the actual Mac Engineer execution path;
3. touch a bounded real engineering artifact/repository;
4. produce inspectable artifact/diff output;
5. run relevant tests/verification;
6. return Evidence into the same task record.

Preferred first commissioning task:

`canonical Labory checkout → inspect one bounded repository fixture or safe real repo → make the smallest reversible engineering change → test → record diff/artifact → DoneCheck`

A consequential production/public/payment action is not required and remains outside this commissioning task.

## Phase 5 — Persistent continuity

For the same task:

`checkpoint → stop/restart runtime/process → resume exact task ID/checkpoint → continue`

PASS requires:

- same task ID before/after;
- explicit checkpoint ID;
- real restart observed;
- no stale-state substitution;
- resumed evidence remains attached to the same durable record.

## Phase 6 — Recovery field proof

A bounded recoverable failure must be observed or intentionally induced in a disposable/safe scope.

Canonical chain:

`failure → evidence → root cause → smallest correction/recovery → reverify`

A fabricated failure record does not count.

## Phase 7 — Local evidence bundle

Final local commissioning bundle schema:

`enguru.mac-engineer.local-commissioning/v0.1`

Required sections:

- `canonical_sync`
- `runtime`
- `real_task`
- `continuity`
- `recovery`
- `authority`
- `critical_failures`
- `mandatory_donecheck`

Use the repository template:

`governance/mac-engineer/MAC_LOCAL_COMMISSIONING_BUNDLE_TEMPLATE.json`

Validate it with:

```bash
python3 tools/mac_engineer_local_donecheck.py \
  --bundle ~/Enguru/Evidence/MacEngineer/v0.6/package6-local-commissioning.json
```

## Phase 8 — Final judgment

PASS requires:

- GitHub Engineering state = `GITHUB_ENGINEERING_VERIFIED`;
- macOS;
- exact-main sync;
- clean/reconciled worktree;
- actual runtime identity + READY;
- Shared AI local route PASS;
- qwen3:14b local provider;
- real engineering task PASS;
- restart/resume PASS;
- recovery PASS;
- authority/Human Threshold preserved;
- unresolved critical failures = 0;
- all Mac Local Mandatory DoneCheck™ items evidence-backed PASS.

Only then:

**ENGÜRÜ Mac Engineer™ v0.6 — VERIFIED FINAL / LOCKED**

## Truth boundary

GitHub CI can verify the evaluator and commissioning tooling.

GitHub CI cannot prove:

- what is currently installed on the user's Mac;
- which local app/runtime is actually running;
- whether the user Mac successfully resumed after restart;
- whether a real local task actually executed.

Those facts require Mac-local Evidence.

## NEXT ACTION

On Mac, keep exact-main clean, run `python3 tools/mac_engineer_runtime_provenance.py`, reconcile only the reported provenance gap, then run the real-task commissioning sequence.
