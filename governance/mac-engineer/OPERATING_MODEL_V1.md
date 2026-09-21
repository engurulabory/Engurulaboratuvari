# ENGÜRÜ Mac Engineer™ — Canonical Operating Model v1.0

## STATE

CANONICAL OPERATING MODEL — ACTIVE CANDIDATE

This document defines the permanent separation of authority between ChatGPT, Labory/GitHub, the Mac Engineer product source, the installed Mac runtime and Evidence.

## 1. One system, four surfaces

### A. ChatGPT — engineering operator interface
Role:
- read current canonical truth;
- keep one active objective;
- derive only the necessary difference;
- coordinate GitHub and Mac evidence;
- return PASS / HOLD / BLOCKED.

ChatGPT is **not** the canonical source of truth.

### B. ENGÜRÜ Labory — CONTROL_PLANE
Canonical repository:

`engurulabory/Engurulaboratuvari`

Role:
- governance;
- global WORKLIST;
- Product/Core map and system truth;
- cross-product CI/security/fleet gates;
- commissioning contracts;
- aggregate Evidence / DoneCheck references.

Labory does **not** own ENGÜRÜ Mac Engineer product source.

### C. ENGÜRÜ Mac Engineer — PRODUCT SOURCE
Canonical repository target:

`engurulabory/enguru-mac-engineer` — dedicated private PRODUCT repository.

Canonical local checkout:

`~/Enguru/Projects/enguru-mac-engineer`

Role:
- native Swift app source;
- Python runtime source;
- product-local tests;
- build/install scripts;
- product-local CI;
- source/build provenance.

Source authority rule:

`GitHub product exact-main → Mac product checkout → build → runtime/install`

No installed runtime file becomes canonical merely because it exists locally. Field-evolved runtime code may enter canonical source only through Evidence + tests + governed source intake.

### D. Mac local — EXECUTION_SURFACE

Installed app:

`~/Applications/ENGÜRÜ Mac Engineer.app`

Runtime:

`~/Enguru/Runtime/MacEngineer`

Evidence:

`~/Enguru/Evidence/MacEngineer`

Role:
- real app/process execution;
- local Ollama / Shared AI use;
- real engineering task execution;
- checkpoint/restart/resume;
- recovery;
- field Evidence.

Mac local is the real execution surface, but not the development source authority.

## 2. Permanent operating chain

`TARGET → Labory WORKLIST → product-source change → product CI → product exact-main → Mac product sync → local build/install → real task → Evidence → DoneCheck™ → Labory reconciliation → NEXT TARGET`

For control-plane changes:

`TARGET → Labory branch/PR → Labory CI → Labory exact-main → Mac sync → field verification`

For product changes:

`TARGET → enguru-mac-engineer branch/PR → product CI → product exact-main → Mac sync/build/install → field verification`

## 3. Source / runtime invariant

The following paths have different authority:

| Surface | Canonical role |
|---|---|
| `Engurulaboratuvari` | CONTROL_PLANE |
| `~/Enguru/Projects/enguru-mac-engineer` | PRODUCT SOURCE CHECKOUT |
| `~/Enguru/Runtime/MacEngineer` | RUNTIME STATE / STAGED EXECUTION |
| `~/Applications/ENGÜRÜ Mac Engineer.app` | INSTALLED APP |
| `~/Enguru/Evidence/MacEngineer` | LOCAL FIELD EVIDENCE |

Invariant:

**product source is never developed inside Runtime or Applications.**

Runtime changes discovered in the field follow:

`OBSERVED DELTA → Evidence → compile/tests → authority review → product-source PR → exact-main → rebuild/reinstall`

## 4. One active objective

At any moment there is one canonical active objective in Labory WORKLIST.

Mac Engineer may work on many repositories, but its own product-development objective remains singular.

## 5. Daily control command

During v0.6 commissioning, the canonical control-plane entry point is:

`python3 tools/mac_engineer_control.py status`

Bootstrap of the dedicated product source is:

`python3 tools/mac_engineer_control.py bootstrap-source`

Remote GitHub publication, when the local source is verified and GitHub CLI is authenticated:

`python3 tools/mac_engineer_control.py publish-source`

The control command fails closed when truth is incomplete.

## 6. Evidence placement

Local, potentially large or machine-specific Evidence remains under:

`~/Enguru/Evidence/MacEngineer`

GitHub stores:
- compact canonical summaries;
- hashes / source SHAs / run IDs;
- redacted Evidence references;
- DoneCheck judgments.

Secrets, access tokens, local caches and machine-specific transient state never become Git truth.

## 7. Final v0.6 closure

Product-level **ENGÜRÜ Mac Engineer™ v0.6 VERIFIED FINAL / LOCKED** requires:

1. Labory engineering closeout PASS.
2. Dedicated Mac Engineer product source canonicalized.
3. Product exact-main CI PASS.
4. Mac runtime/install proven built from that product exact-main.
5. One real engineering task PASS.
6. Restart/resume PASS.
7. Recovery field proof PASS.
8. Local Evidence bundle PASS.
9. Mandatory DoneCheck™ PASS.
10. Unresolved critical failures = 0.

## Judgment

This model replaces ad-hoc path ambiguity with one clean rule:

**Labory governs. Product repo owns source. Mac runs. Evidence proves. DoneCheck closes.**
