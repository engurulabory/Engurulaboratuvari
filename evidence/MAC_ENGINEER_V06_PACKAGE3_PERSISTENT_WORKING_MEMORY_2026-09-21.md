# ENGÜRÜ Mac Engineer™ v0.6 — Package 3 Persistent Working Memory — Evidence + Mandatory DoneCheck™

Date: 2026-09-21

## STATE

PASS — implementation, exact-head CI and executable Mandatory DoneCheck™ are verified on the Package 3 candidate.

## CLAIM

Package 3 extends existing Task State + Evidence + Verified Learning with durable restart-safe task continuity and governed learning promotion without creating a new core, daemon, agent framework or parallel authority path.

## IMPLEMENTATION

- `shared_ai/working_memory.py`
  - immutable durable `task_id`
  - objective + authority snapshot + required capabilities
  - monotonic revision
  - stale-write rejection
  - atomic JSON persistence: temp → fsync → replace
  - state transitions
  - artifact/evidence refs
  - Human decision + authority + evidence binding
  - resume checkpoint
  - evidence-gated final outcome
  - completed PASS cannot silently resume
- governed learning:
  - `OBSERVED → LEARNING_CANDIDATE → EVIDENCE → FRESH_REVIEW → ACCEPT / REJECT → PROMOTED`
  - repeated observation required
  - benchmark + evidence required
  - producer and fresh reviewer identities must differ
  - existing `EvidenceGatedSkillLearning` + Human Threshold reused for ACCEPT
  - promotion records explicit version + target
  - REJECT cannot promote

## EXACT-HEAD EVIDENCE

Verified candidate head before this evidence-only commit:

`4d03d5cabef731bce653c7a67bcba67e123b2814`

GitHub Actions:

- ENGURU Labory Final Gate #198 — PASS
- IP Model Trust Gate #218 — PASS
- IP Model Trust Fleet #203 — PASS
- PARK Adapter CI #70 — PASS

Labory Final Gate specifically verified:

- existing Shared AI offline/runtime/behavior regression — PASS
- Package 3 persistent working memory unit tests — PASS
- Package 3 Mandatory DoneCheck™ — PASS
- Quality & Red Team — PASS
- Security & Authority — PASS
- Verified production discipline — PASS
- Shared AI runtime smoke — PASS
- Billing/PARK regressions — PASS
- Secret Zero / Fleet Gate — PASS
- Repository Steward + scheduled runner — PASS

## FIRST DONECHECK FAILURE + REPAIR

First executable DoneCheck run failed because direct invocation from `tools/package3_working_memory_donecheck.py` did not include repository root on Python import path.

Root cause:
`ModuleNotFoundError: No module named 'shared_ai'`

The Package 3 implementation/unit tests were already PASS.

Smallest correction:
- resolve repository root from `__file__`
- add that root to `sys.path` for direct script execution

Second exact-head run:
- Package 3 tests — PASS
- Mandatory DoneCheck™ — PASS
- full Labory Final Gate — PASS

## MANDATORY DONECHECK™

| Check | Evidence | Judgment |
|---|---|---|
| One durable task identity | restart reload test + executable scenario | PASS |
| Objective / authority / capabilities bound | persisted record assertions | PASS |
| Atomic persistence | implementation contract + regression | PASS |
| Stale task revision rejected | unit + DoneCheck scenario | PASS |
| Checkpoint/resume survives restart | unit + DoneCheck scenario | PASS |
| Artifact/evidence references persist | task record tests | PASS |
| Human decision bound to authority + evidence | unit test | PASS |
| Evidence-less final PASS rejected | unit test | PASS |
| Verified PASS cannot silently resume | unit test | PASS |
| One observation cannot self-promote | unit test | PASS |
| Fresh review independence enforced | unit test | PASS |
| Learning ACCEPT remains Human Threshold-gated | unit + DoneCheck scenario | PASS |
| REJECT cannot promote | unit test | PASS |
| Versioned promotion persists | unit + reload | PASS |
| Existing runtime/governance behavior preserved | Labory Final Gate | PASS |
| Security/IP/fleet gates preserved | exact-head workflows | PASS |

## SECOND LOOK

The implementation stores bounded engineering truth; it does not claim unlimited model memory.

The runtime storage root is caller-owned. No repository-tracked live task state, credential, private user memory, or daemon is introduced.

Learning promotion increases verified reuse discipline; it does not expand authority.

## JUDGMENT

**PACKAGE 3 — PERSISTENT WORKING MEMORY — VERIFIED PASS CANDIDATE**

Canonical closeout still requires:
1. this Evidence/worklist reconciliation commit;
2. exact-head CI after that documentation-only delta;
3. merge;
4. exact-main verification.

## NEXT ACTION

Reconcile canonical WORKLIST → exact-head CI → merge → exact-main → Package 4.
