# ECC Selective Harvest v1 — Engürü Integration Contract

State: IMPLEMENTED CANDIDATE — exact-head CI required.

Purpose: harvest only the useful mechanisms from Everything Claude Code (ECC) into existing Engürü layers. This does not create a new Core, framework, agent authority, or governance hierarchy.

## Canonical rule

`reuse → extend → adapter → new core`

ECC is a donor/reference system only. ENGÜRÜ Language Governance™, Security & Authority, Quality & Red Team, DoneCheck™ and Human Threshold™ remain canonical.

## Harvested capabilities

1. **Fresh Review** — REUSE existing `shared_ai/quality_review.py`.
   - independent reviewer identity;
   - evidence-bound findings;
   - disagreement → HOLD;
   - history-sensitive regression review.

2. **AgentShield semantic scan** — EXTEND existing Security & Authority.
   - prompt, hook, MCP/config, permission and secret-sensitive surfaces;
   - deterministic pre-scan;
   - finding → HOLD for semantic review;
   - never self-authorizes remediation.

3. **Context Budget** — EXTEND Shared AI Behavior.
   - verified truth and latest instruction are preserved before disposable prior context;
   - context compression must not manufacture or silently drop canonical truth.

4. **Harness Capability Matrix** — EXTEND Verified Agent Operating behavior.
   - capability truth is explicit: SUPPORTED / DEGRADED / UNSUPPORTED / HUMAN_THRESHOLD;
   - unsupported or authority-bound capability fails closed.

5. **Preflight / Dry-run** — EXTEND existing runtime discipline.
   - mutations require declared scope and dry-run evidence;
   - Human Threshold remains external authority.

6. **Evidence-gated Skill Learning** — EXTEND existing learning discipline.
   - repeated observation is only a candidate;
   - evidence + benchmark required;
   - default promotion path requires Human Threshold;
   - no autonomous authority growth.

7. **Doctor / Self-Diagnostic** — EXTEND Steward / DoneCheck™ preparation.
   - aggregates deterministic subsystem checks;
   - any unresolved HOLD prevents a doctor PASS;
   - doctor output is evidence, not final governance authority.

## Explicit non-harvest

Default REJECT / NEED-BASED REVIEW:
- ECC agent fleet as a whole;
- ECC skill catalog as a whole;
- legacy command shims;
- ECC global rules replacing Engürü governance;
- autonomous memory/learning promotion;
- bulk hook activation;
- ECC as a new Engürü Core.

## Acceptance

- no new Core/framework;
- all seven capabilities map to existing Engürü layers;
- fail-closed behavior for unsupported capability, missing dry-run, security findings and incomplete skill evidence;
- Human Threshold preserved;
- deterministic regression tests PASS;
- exact-head CI PASS before merge;
- post-merge exact-main verification before PASS/FINISHED claims.
