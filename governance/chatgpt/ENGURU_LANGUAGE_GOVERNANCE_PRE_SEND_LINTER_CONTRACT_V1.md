# ENGÜRÜ Language Governance™ — Pre-Send Linter Contract v1.0

**Parent authority:** `governance/ENGURU_LANGUAGE_GOVERNANCE_V1.md`  
**Applies to:** ChatGPT prompts, execution packages, governed technical responses, handoff prompts and canonical project instructions  
**Reference implementation:** `tools/enguru_language_pre_send_linter.py`  
**Verdict:** `PASS / HOLD`

## 1. Purpose

The Pre-Send Linter is the final language-execution gate before a governed package is released.

It checks whether wording preserves truth, evidence, authority, continuity and executable forward motion.

The linter is not a style beautifier. It is a governance guard.

## 2. Canonical checks

### L01 — VALID_STATE_LANGUAGE
Instruction language defines the valid state or correct action directly.

Examples that require review:
- prohibition-first imperatives;
- repeated “do not / never / yapma / olmayacak” steering where a direct valid-state rule is available.

Verified negative STATE descriptions remain allowed.

### L02 — CURRENT_TRUTH_GROUNDING
Dynamic claims identify or respect current authoritative truth.

Historical summaries, memory and stale context remain discovery inputs rather than automatic technical truth.

### L03 — CLAIM_EVIDENCE_SEPARATION
Material completion or correctness claims remain distinct from their Evidence.

### L04 — EVIDENCE_BOUNDED_CLOSURE
`PASS`, `DONE`, `FINISHED`, `VERIFIED`, `PRODUCTION_READY` and equivalent closure language require scope-matched evidence.

### L05 — EXECUTION_TRUTH
Proposed, attempted and completed work are linguistically distinct.

Tool intent is not tool completion.

### L06 — VERDICT_DISCIPLINE
- PASS = acceptance Evidence complete.
- HOLD = missing/resolvable truth or Evidence.
- BLOCKED = verified external or authority barrier.

### L07 — HUMAN_THRESHOLD
Consequential, irreversible, payment, publication, contract, external representation and equivalent authority-sensitive actions preserve Human Threshold™.

### L08 — REQUIRED_DIFFERENCE
The package preserves verified current structure and introduces only the necessary difference.

### L09 — LOCK_PRESERVATION
Canonical locked names, decisions, boundaries and acceptance rules remain unchanged unless revision authority/evidence is explicit.

### L10 — NEXT_ACTION
Open work ends with a concrete next real action when that action is not already obvious from immediate execution.

### L11 — NO_FABRICATED_EVIDENCE
Evidence references must describe actual observable proof. Narrative recollection and model confidence are not promoted to Evidence.

### L12 — NATURAL_OUTPUT
Governance semantics remain strong without forcing unnecessary labels, repetition or machine-like prose into simple user-facing answers.

## 3. Severity

### CRITICAL
A finding that can manufacture false truth, unsafe authority, false completion or invalid PASS.

Result: `HOLD`.

### MATERIAL
A finding that weakens execution clarity, continuity or governance semantics.

Result: `HOLD` for canonical/execution packages; correction required before release.

### ADVISORY
A wording improvement that does not change truth or authority.

Result may remain `PASS`.

## 4. Static lint scope

The deterministic implementation checks high-signal textual patterns only.

Static checks include:
- prohibition-first instruction patterns;
- governed block field completeness;
- unsupported closure keywords without nearby Evidence semantics;
- placeholder Evidence markers;
- malformed verdict values.

Static PASS means no deterministic issue was found. It does not prove full semantic correctness.

## 5. Semantic lint scope

Semantic review checks:
- whether the valid state is directly defined;
- whether a claim exceeds its evidence;
- whether current truth precedence is preserved;
- whether a historical source is being treated as current authority;
- whether Human Threshold is required;
- whether a proposed change exceeds the necessary difference;
- whether the next action is the smallest real movement.

Semantic review is required for canonical project prompts and material closure packages.

## 6. Input

Accepted input:
- UTF-8 text file;
- stdin text;
- generated prompt/package before sending.

Optional mode:
- `--strict` for canonical or execution packages.

## 7. Output contract

Machine-readable JSON:

```json
{
  "schema": "enguru.language.pre-send-linter/v1",
  "state": "PASS",
  "finding_count": 0,
  "findings": [],
  "checked_rules": ["L01", "L03", "L04", "L06", "L10", "L11"]
}
```

Finding:

```json
{
  "rule": "L01",
  "severity": "MATERIAL",
  "line": 12,
  "message": "Prohibition-first instruction detected.",
  "next_action": "Express the valid state or correct action directly."
}
```

## 8. Fail-closed behavior

The deterministic linter returns:
- exit `0` for PASS;
- exit `20` for HOLD findings;
- exit `30` for invalid invocation/input.

A linter runtime failure never becomes PASS.

## 9. Canonical acceptance

Pre-Send Linter Contract v1.0 is field-acceptable when:
- deterministic implementation exists;
- regression tests cover valid-state and violation cases;
- Master Instruction references this contract;
- canonical parent references the ChatGPT teaching package;
- exact-head CI passes.

Final semantic authority remains the parent ENGÜRÜ Language Governance™ contract plus DoneCheck™ / Human Threshold™ where applicable.
