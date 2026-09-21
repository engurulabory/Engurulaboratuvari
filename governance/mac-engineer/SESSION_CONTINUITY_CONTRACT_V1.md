# ENGÜRÜ Mac Engineer™ — Session Continuity Contract v1.0

## STATE

**CANONICAL / SESSION-DRIFT PREVENTION**

This contract prevents a new ChatGPT session, Terminal session or operator handoff from re-discovering or re-interpreting ENGÜRÜ Mac Engineer™ architecture.

## 1. Canonical working method

Every engineering session follows exactly this chain:

`SESSION START → CANONICAL SYNC → SESSION STATE → ONE ACTIVE OBJECTIVE → CHANGE → TEST/CI → EXACT-MAIN → MAC FIELD ACTION → EVIDENCE → MANDATORY DONECHECK™ → WORKLIST RECONCILE → SESSION HANDOFF`

No session starts directly from an old chat summary, an old Terminal directory, an installed runtime file or a remembered next step.

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

1. read canonical WORKLIST/state first;
2. identify the single necessary difference;
3. perform GitHub-side work itself when tooling permits;
4. ask the user for Mac Terminal execution only when local execution is required;
5. reconcile returned Mac evidence;
6. update canonical truth before moving to the next objective.

ChatGPT must not manufacture continuity from memory when canonical state is available.

## 8. Positive governance language

Use:

`STATE → CLAIM → EVIDENCE → JUDGMENT / NEXT ACTION`

Describe the desired/verified path positively. Constraints are expressed as authority boundaries and gates, not as an accumulating list of prohibitions.

## 9. Session closure invariant

A session is safe to hand off when:

- WORKLIST reflects current truth;
- GitHub changes are merged or explicitly HOLD;
- local field Evidence is recorded;
- one next action is explicit;
- no hidden parallel source/runtime authority exists.

## JUDGMENT

**Conversation continuity is advisory. Canonical continuity is GitHub + Mac Evidence.**

This contract is the permanent session working method for ENGÜRÜ Mac Engineer™.
