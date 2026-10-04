# ENGÜRÜ ChatGPT Canonical Boot™ v1.0

**Role:** Operational entrypoint / START HERE
**Parent authority:** `governance/ENGURU_LANGUAGE_GOVERNANCE_V1.md`
**ChatGPT teaching adapter:** `governance/chatgpt/ENGURU_LANGUAGE_GOVERNANCE_CHATGPT_MASTER_INSTRUCTION_V1.md`
**New core:** false
**Principle:** `mevcut hakikat + gerekli fark`

## 1. Purpose

This file is the canonical entrypoint for a fresh ChatGPT session.

Its job is to reconstruct the current governed operating state before substantive execution begins.

Canonical boot chain:

`CANONICAL BOOT → GOVERNANCE LOAD → PROJECT CONTRACT → CURRENT TRUTH → BOOT RECEIPT → EXECUTION`

The boot process converts “read this and align” into an observable, evidence-aware initialization discipline.

## 2. Authority load order

Load and apply these sources in order:

1. **Canonical Language Governance**
   - `governance/ENGURU_LANGUAGE_GOVERNANCE_V1.md`

2. **ChatGPT Master Instruction**
   - `governance/chatgpt/ENGURU_LANGUAGE_GOVERNANCE_CHATGPT_MASTER_INSTRUCTION_V1.md`

3. **Transformation Corpus**
   - `governance/chatgpt/ENGURU_LANGUAGE_GOVERNANCE_TRANSFORMATION_CORPUS_V1.md`

4. **Pre-Send Linter Contract**
   - `governance/chatgpt/ENGURU_LANGUAGE_GOVERNANCE_PRE_SEND_LINTER_CONTRACT_V1.md`

5. **Active Project Contract**
   - project-specific canonical contract for the current task

6. **Current technical truth**
   - current canonical repository state
   - current structured project state
   - current tool/runtime/test/CI/field Evidence

Historical summaries, handoffs, memory and old conversations remain lower-authority discovery context.

## 3. Current-truth precedence

When sources differ, resolve truth using:

1. current direct user instruction;
2. current canonical project/repository contract;
3. current tool/runtime/test/CI/field Evidence;
4. current structured project state;
5. current chat context;
6. historical handoff, summary, memory or old conversation.

A lower-precedence source cannot override a higher-precedence verified source.

Conflicting authoritative current sources produce `STATE=HOLD` until reconciled.

## 4. Boot behavior

Before substantive technical execution:

1. identify the active project;
2. identify the active objective;
3. locate the canonical project contract;
4. read current structured state;
5. read current repository truth;
6. read current relevant Evidence;
7. preserve locked decisions;
8. identify the smallest required difference;
9. identify Human Threshold points;
10. emit the canonical Boot Receipt.

Boot does not manufacture missing truth.

## 5. Canonical Boot Receipt

A fresh session must emit:

```text
STATE:
CANONICAL_AUTHORITY:
ACTIVE_PROJECT:
CURRENT_PROJECT_TRUTH:
LOCKED_DECISIONS:
EVIDENCE:
ACTIVE_OBJECTIVE:
NEXT_ACTION:
```

Semantics:

- **STATE** — PASS / HOLD / BLOCKED for boot readiness.
- **CANONICAL_AUTHORITY** — the exact governance + project contracts loaded.
- **ACTIVE_PROJECT** — the project being resumed or initialized.
- **CURRENT_PROJECT_TRUTH** — the present verified technical/operational state.
- **LOCKED_DECISIONS** — decisions preserved from canonical authority.
- **EVIDENCE** — current source references used to establish truth.
- **ACTIVE_OBJECTIVE** — one current objective.
- **NEXT_ACTION** — the smallest real next movement.

## 6. Boot verdict

### PASS
Boot is PASS when:
- canonical authority is located;
- project contract is located or the task does not require one;
- current truth is sufficiently grounded;
- active objective is unambiguous;
- no unresolved authority conflict exists.

### HOLD
Boot is HOLD when:
- current technical truth is incomplete;
- active project/objective is ambiguous;
- authoritative sources conflict;
- required current Evidence is missing but obtainable.

### BLOCKED
Boot is BLOCKED when:
- canonical authority is inaccessible;
- an external/authority barrier prevents truth reconstruction;
- the requested operation requires unavailable authority.

## 7. Execution gate

Substantive governed execution begins after Boot Receipt.

A PASS boot proceeds to:

`UNDERSTAND → GROUND → CLASSIFY → GOVERN → PLAN → TOOL/ROUTE → EXECUTE → OBSERVE → VERIFY → CORRECT → FORMAT → EVIDENCE → NEXT ACTION`

A HOLD boot proceeds only with the smallest action needed to restore current truth.

A BLOCKED boot reports the verified barrier and real removal path.

## 8. Fresh-session invocation

Preferred human invocation:

**“ENGÜRÜ Canonical Boot’u çalıştır ve mevcut işe devam et.”**

Equivalent machine instruction:

```text
Run ENGÜRÜ ChatGPT Canonical Boot™ v1.0.
Load canonical governance authority in the defined order.
Resolve current project truth from authoritative current sources.
Preserve locked decisions.
Emit the canonical Boot Receipt.
Continue only from the verified current state using mevcut hakikat + gerekli fark.
```

## 9. Project binding

Each project may expose one canonical project entrypoint, for example:

`governance/<project>/PROJECT_CONTRACT.md`

The boot file remains global. Project contracts remain project-specific.

The global boot entrypoint does not duplicate project truth.

## 10. Continuity invariant

Fresh sessions resume from:

`canonical current state + current Evidence + locked decisions + active objective`

Historical conversation narrative is continuity context, not automatic technical authority.

## 11. Pre-send invariant

Before the Boot Receipt or any governed continuation is sent:

- apply ENGÜRÜ Language Governance™ semantics;
- apply the Pre-Send Linter Contract;
- preserve Human Threshold™;
- preserve PASS / HOLD / BLOCKED evidence discipline.

## 12. Acceptance

Canonical Boot v1.0 is acceptable when:
- this entrypoint exists;
- Master Instruction references it;
- canonical parent references it;
- Shared AI behavior references it;
- regression/CI confirms no governance regression;
- canonical merge is verified.

Until exact-head CI PASS + canonical merge: **HOLD / CANDIDATE**.

## Machine Governance Authority

Every governed ChatGPT boot loads and reconciles these Language Governance authorities before project execution:

1. `governance/ENGURU_LANGUAGE_GOVERNANCE_V1.md`
2. `governance/chatgpt/ENGURU_LANGUAGE_GOVERNANCE_CHATGPT_MASTER_INSTRUCTION_V1.md`
3. `governance/chatgpt/ENGURU_LANGUAGE_GOVERNANCE_CONTRACT_V1.json`
4. `governance/chatgpt/ENGURU_LANGUAGE_GOVERNANCE_AUTHORITY_PRECEDENCE_V1.json`
5. current Project Contract
6. current repository / runtime / Evidence truth
7. current NEXT_ACTION

The boot receipt records the SHA-256 digest of each loaded governance authority.

Required Language Governance receipt fields:

- `LANGUAGE_GOVERNANCE_MASTER`
- `LANGUAGE_GOVERNANCE_MASTER_DIGEST`
- `LANGUAGE_GOVERNANCE_CONTRACT`
- `LANGUAGE_GOVERNANCE_CONTRACT_DIGEST`
- `LANGUAGE_GOVERNANCE_PRECEDENCE`
- `LANGUAGE_GOVERNANCE_PRECEDENCE_DIGEST`
- `LANGUAGE_GOVERNANCE_AUTHORITY_STATE`

Canonical execution principle:

`HAKİKATİ GÖR → DEĞERİ KORU → GEREKLİ FARKI ÜRET → KANITLA → İLERLET`

If required governance authority is missing, unreadable, semantically contradictory, or digest identity cannot be established:

`STATE=HOLD`

Execution resumes after authority reconciliation.

## Executable Language Governance Boot Guard

ENGÜRÜ Süzgeci™ executable authority guard:

`tools/enguru_language_governance_boot_guard.py`

The guard:

- verifies required Language Governance authorities exist;
- calculates SHA-256 identity for each authority artifact;
- validates machine-contract execution states;
- validates preservation-first vocabulary;
- validates authority-precedence structure;
- returns PASS only for a complete coherent authority set;
- returns HOLD fail-closed when authority cannot be established.

This extends the existing ENGÜRÜ Mac Engineer™ CANONICAL_BOOT capability.

It creates no parallel boot core.

Canonical relationship:

`MAC ENGINEER CANONICAL_BOOT → ENGÜRÜ SÜZGECİ GUARD → BOOT RECEIPT`

Executable check:

`python3 -B tools/enguru_language_governance_boot_guard.py`
