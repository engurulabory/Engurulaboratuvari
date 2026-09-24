# ENGÜRÜ Mac Engineer™ — Session Continuity Contract v1.0

## STATE

**CANONICAL / SESSION-DRIFT PREVENTION**

This contract prevents a new ChatGPT session, Terminal session or operator handoff from re-discovering or re-interpreting ENGÜRÜ Mac Engineer™ architecture.

## 1. Canonical working method

Every engineering session follows exactly this chain:

`SESSION START → CANONICAL SYNC → SESSION STATE → ONE ACTIVE OBJECTIVE → PROGRAMMER AGENT → PRE-SEND FILTER → CHANGE → TEST/CI → EXACT-MAIN → MAC FIELD ACTION → EVIDENCE → MANDATORY DONECHECK™ → CURRENT_STATUS RECONCILE → WORKLIST/SESSION_STATE RECONCILE → SESSION HANDOFF`

No session starts directly from an old chat summary, an old Terminal directory, an installed runtime file or a remembered next step.

### 1.1 Active working-path bootstrap

When `governance/mac-engineer/ACTIVE_WORKING_PATH.md` is present, a new ChatGPT engineering session reads it immediately after this contract and before dynamic session-state evaluation.

The active working-path file records the current human/ChatGPT execution model: GitHub-first engineering, Mac last-mile commissioning, target → result discipline, role separation, Evidence, Human Threshold™ and Mandatory DoneCheck™.

While active development is in progress, `governance/mac-engineer/CURRENT_STATUS.md` is the compact human-readable handoff surface. It records what is already verified, where the program is now, the latest observed result, the remaining canonical work and the single next action.

Dynamic technical truth continues to come from `CURRENT_STATUS.md`, `SESSION_STATE_V1.json`, `PRODUCT_ROADMAP_V1.json`, `WORKLIST.md`, exact GitHub state and current Mac Evidence. Structured state and direct Evidence remain authoritative when a summary line is stale.

When the ENGÜRÜ Mac Engineer™ active development program reaches its verified locked finish, the active working-path bootstrap may be removed without changing this permanent continuity contract.

## 2. Authority order

When sources disagree, use this order:

1. **GitHub canonical WORKLIST / governance**
2. **Dedicated product repository exact-main**
3. **Current Mac product checkout exact-main**
4. **Verified Mac runtime/install Evidence**
5. **Current chat context**
6. **Historical handoff / backup / old conversation**

A lower source never overrides a higher source without new Evidence and a governed change.

## 3. Fixed surfaces

- CONTROL_PLANE: `engurulabory/Engurulaboratuvari`
- PRODUCT_SOURCE: `engurulabory/enguru-mac-engineer`
- Mac product checkout: `~/Enguru/Projects/enguru-mac-engineer`
- Runtime: `~/Enguru/Runtime/MacEngineer`
- Installed app: `~/Applications/ENGÜRÜ Mac Engineer.app`
- Local Evidence: `~/Enguru/Evidence/MacEngineer`

These roles are not rediscovered in each session.

## 4. One active objective

A session may execute only the single objective declared by canonical WORKLIST/session-state.

A new session must not:
- reopen VERIFIED/LOCKED packages;
- create a parallel source tree;
- move product source into Runtime/Applications;
- infer a new repository role from folder names;
- continue from a stale remembered SHA;
- treat health-only evidence as real task completion.

If new evidence contradicts canonical truth, state the contradiction and reconcile it before execution.

## 4.1 Governed working branch exception

Product source normally begins a session on clean exact-main.

A feature branch is accepted only when the current canonical SESSION_STATE explicitly records:

- the active objective that requires that branch;
- the exact authorized branch name;
- the exact authorized head commit;
- the exact expected base `origin/main`;
- a clean worktree.

This is a narrow continuity exception for a verified in-flight change, not a second source authority.

For an explicitly recorded in-flight patch, SESSION_STATE may authorize a bounded dirty worktree when all of these match exactly:

- active objective;
- branch;
- HEAD;
- origin/main base;
- complete expected dirty-path set.

An extra, missing or different path returns HOLD. This allows a verified patch to survive a new chat/session before commit without weakening source authority.

Any unrecorded branch/head/base/path difference returns HOLD.

## 5. Session start gate

Canonical entry:

```bash
cd "$LABORY" &&
git fetch origin main &&
git checkout main &&
git pull --ff-only origin main &&
python3 tools/mac_engineer_control.py session-start
```

Session start must report:
- control-plane HEAD / exact-main;
- product-source HEAD / origin-main / clean state;
- canonical paths;
- active objective;
- locked working method;
- current next action;
- contradictions/issues.

If the gate returns HOLD, execution pauses at the reported difference.

## 6. Session handoff gate

At the end of a working session, run:

```bash
python3 tools/mac_engineer_control.py session-handoff
```

The handoff writes a compact local Evidence snapshot containing:
- exact SHAs;
- active objective;
- current next action;
- canonical paths;
- runtime/app process truth;
- unresolved HOLD/BLOCKED items.

A new chat can begin from this snapshot plus GitHub canonical truth instead of conversational memory.

## 7. ChatGPT operating rule

For ENGÜRÜ Mac Engineer engineering sessions, ChatGPT must:

Before a material Mac Terminal package is presented, the session applies the ENGÜRÜ Programmer Agent™ authoring discipline and Pre-Send Filter. The package reaches Terminal only after canonical objective, necessary difference, Language Governance, positive language, Second Look, syntax, scope, recovery and DoneCheck™ v1.2 pre-send checks align.


1. read `CURRENT_STATUS.md`, canonical WORKLIST and structured session-state first;
2. identify the single necessary difference;
3. perform GitHub-side work itself when tooling permits;
4. ask the user for Mac Terminal execution only when local execution is required;
5. reconcile returned Mac evidence;
6. update `CURRENT_STATUS.md` after every completed work package or material PASS / HOLD / BLOCKED result;
7. reconcile WORKLIST / SESSION_STATE when the result changes canonical state;
8. move to the next action only after the status surface reflects the latest Evidence.

ChatGPT must not manufacture continuity from memory when canonical state is available.

## 7.1 Current Status mandatory update invariant

`governance/mac-engineer/CURRENT_STATUS.md` is a living canonical handoff surface during active development.

After every material engineering package or field-verification result, the operator reconciles it **before the next action**.

The update records:

- what was completed or changed;
- the latest Evidence;
- the resulting PASS / HOLD / BLOCKED judgment;
- the current objective;
- the remaining canonical work;
- the single next action.

A session may remain on the same objective across several iterations; CURRENT_STATUS still advances with each material result. This keeps a fresh ChatGPT session aligned without depending on conversation history.

## 8. Positive governance language

Use:

`STATE → CLAIM → EVIDENCE → JUDGMENT / NEXT ACTION`

Describe the desired/verified path positively. Constraints are expressed as authority boundaries and gates, not as an accumulating list of prohibitions.

## 9. Session closure invariant

A session is safe to hand off when:

- CURRENT_STATUS, WORKLIST and SESSION_STATE reflect current truth;
- GitHub changes are merged or explicitly HOLD;
- local field Evidence is recorded;
- one next action is explicit;
- no hidden parallel source/runtime authority exists.

## JUDGMENT

**Conversation continuity is advisory. Canonical continuity is GitHub + Mac Evidence.**

This contract is the permanent session working method for ENGÜRÜ Mac Engineer™.
## Permanent Scenario-Gate Execution Rule

ENGÜRÜ Mac Engineer™ uses one stable construction model.

Architecture remains.
Foundation is frozen after verified foundation work.
Scenario gates remain scenario gates.
Terminal packages are engineering work units inside the active Gate; they are not roadmap nodes.

Canonical v0.8 order:

`Gate 6 → Gate 7 → Gate 8 → Gate 9 → Gate 10 → Gate 11 → Gate 12`

Every Gate follows:

`CURRENT TRUTH → GATE CONTRACT → NECESSARY DIFFERENCE → PROGRAMMER AGENT → PRE-SEND FILTER → IMPLEMENT → TEST → BOUNDED REPAIR WHEN OBSERVED → REGRESSION → EVIDENCE → PASS/HOLD → NEXT GATE`

The next Gate becomes active only after the current Gate earns PASS.

Scenario-specific findings remain bounded repairs inside the active Gate.

Foundation reopens only when fresh Evidence establishes a real foundation defect.

Existing verified mechanisms are reused before extension.
Adapters remain adapters.
No duplicate core and no second canonical truth are created.

v0.8 proves the complete Product Engineering Operator lifecycle.

v0.9 owns cross-product breadth and world-class field benchmark/generalization after v0.8 lifecycle verification.

Verified Finish remains:

`Evidence → DoneCheck™ v1.2 → Human Threshold™ where required → canonical reconciliation → version lock`
## Mandatory Pre-Output ENGÜRÜ Filter

Before ChatGPT presents any material ENGÜRÜ Mac Engineer™ engineering output to the human operator, the existing ENGÜRÜ authoring discipline is applied first.

Material output includes Terminal or programming code, executable packages, engineering prompts, implementation prompts, repair or migration instructions, architecture-changing instructions, state-changing instructions and Human Threshold decision surfaces.

Mandatory sequence:

`CURRENT TRUTH → ONE ACTIVE OBJECTIVE → NECESSARY DIFFERENCE → PROGRAMMER AGENT → ENGÜRÜ LANGUAGE GOVERNANCE → POSITIVE LANGUAGE → SECOND LOOK → SCOPE / AUTHORITY / RECOVERY → DoneCheck™ PRE-SEND → OUTPUT`

For executable Terminal packages:

`python3 tools/mac_engineer_pre_send_filter.py <terminal-package.command>`

The package reaches Terminal after this executable gate returns PASS.

Material non-executable engineering prompts are reviewed against the same objective, necessary-difference, authority, recovery, Evidence and Language Governance boundaries before presentation.

Terminal work units remain inside the active scenario Gate and do not create roadmap nodes.

This is a permanent session invariant.
No new core and no second canonical truth are introduced.

## Visual Aesthetic Timing — Canonical Rule

STATE

ENGÜRÜ Mac Engineer™ engineering and scenario-gate
execution remains the current priority.

The present Cockpit surface is the functional visual
baseline.

CLAIM

Major visual refinement is intentionally scheduled
after product engineering, scenario execution,
reliability and long-running behavior reach their
planned maturity.

The established ENGÜRÜ Mac Engineer™ visual direction,
including the approved mountain/lake/owl reference,
remains the preserved design reference.

VERSION RULE

- v0.8 → complete the real product-engineering
  scenario gates.
- v0.9–v1.0 → strengthen autonomous product-engineering
  behavior and field capability.
- v1.1 → consolidate the visual system:
  typography, spacing, navigation, page hierarchy,
  panels, background treatment and interaction
  consistency.
- v1.2 → perform final Human Artistic Authority
  refinement and whole-product aesthetic acceptance.

CURRENT EXECUTION RULE

During the engineering-first phase, visual work is
limited to differences that materially affect:

- usability,
- readability,
- overflow or layout integrity,
- navigation,
- task execution,
- conversation,
- human decision surfaces,
- product correctness.

Major aesthetic refinement does not create scenario
sub-gates, roadmap nodes, a new core or a second
canonical truth.

Functional product acceptance remains evidence-based:
working behavior → regression → Evidence → DoneCheck™
→ declared Human Threshold.

Final premium visual quality is independently accepted
at the declared v1.1–v1.2 boundary.

LOCKED DECISION

ARCHITECTURE_REMAINS=true
ROADMAP_REMAINS=true
FOUNDATION_FROZEN=true
ENGINEERING_FIRST=true
CURRENT_VISUAL_BASELINE=PRESERVED
MAJOR_VISUAL_CONSOLIDATION=v1.1
FINAL_HUMAN_ARTISTIC_AUTHORITY=v1.2
NEW_CORE=false
SECOND_CANONICAL_TRUTH=false

CURRENT NEXT ACTION

V08_MIGRATION_REPAIR_SCENARIO

After Gate 6 PASS, activate Gate 7 — Migration / Repair.

## Mac Engineer Version Semantics — Canonical Final Target

STATE

ENGÜRÜ Mac Engineer™ has one final product target.

VERSION SEMANTICS

- v0.8 — Product Engineering Operator Field Proof.
- v0.9 — World-Class Field Benchmark.
- v1.0 — Verified Product Engineering Operator.
- v1.1 — Reliability + Product-System + Visual-System Consolidation.
- v1.2 — FINAL TARGET — Local Mac Astra Verified Final.

PRODUCT VERSION DISTINCTION

DoneCheck™ product version = 1.2.0
ENGÜRÜ Mac Engineer™ final product version = v1.2

VERIFIED FINISH RULE

Engineering → regression → criterion-scoped Evidence
→ DoneCheck™ v1.2 machine verification
→ real-Mac final commissioning
→ Human Threshold™
→ Human Artistic Authority™
→ version lock.

LOCKED TARGET

MAC_ENGINEER_FINAL_TARGET=v1.2
V11_ROLE=RELIABILITY_PRODUCT_SYSTEM_VISUAL_CONSOLIDATION
V12_ROLE=VERIFIED_FINAL
V12_EXIT=VERIFIED_FINAL_LOCKED
THEORETICAL_COHERENCE_TARGET=99_PLUS
FIELD_100_REQUIRES_REAL_HUMAN_ACCEPTANCE=true
NEW_CORE=false
SECOND_CANONICAL_TRUTH=false

CURRENT NEXT ACTION

V08_MIGRATION_REPAIR_SCENARIO


## Current Scenario Transition

V08 Gate 6 = PASS / SEALED.
Current scenario gate = Gate 7 — Migration / Repair.
Current objective = `V08_MIGRATION_REPAIR_SCENARIO`.
