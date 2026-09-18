# External Capability Harvest — Technical DoneCheck™

Date: 2026-09-18  
Authority: ENGÜRÜ Labory Control Plane  
Scope: six-repository mechanism harvest  
Judgment: **PASS — TECHNICAL HARVEST / HOLD — LIVE SECOND-PROVIDER COMMISSIONING**

## STATE

Four implementation packages are merged on canonical main:

| Package | Scope | Merge SHA | Labory Final Gate |
|---|---|---|---|
| P1 | Quality & Red Team — history-aware PR review, confidence/evidence filtering, Outside Voice contract | `1882a2ea76178e50fe676ae682ca98ffafa05f95` | `35332401621` SUCCESS |
| P2 | Security & Authority — semantic security review, STRIDE, OWASP, trusted-source gate | `de2f83c1a1446cef295ed34625b2eeb7b3f68d9d` | `35332732587` SUCCESS |
| P3 | Production Discipline — runtime guard, systematic debugging, worktree isolation, verification-before-completion, skill TDD | `17cdfe8e6a9e0b07ec3a7430b61e9573aa3f21dc` | `35332898620` SUCCESS |
| P4 | QA/Release Evidence Adapter — diff impact, browser evidence, canary, benchmark budget | `2c92d22a4ca4f7729046f322e3581e5d0e677cde` | `35333069263` SUCCESS |

Each package also passed IP Model Trust Gate, IP Model Trust Fleet and PARK Adapter CI on its PR head.

## CLAIM

The selected external mechanisms are now represented through existing ENGÜRÜ layers without installing a parallel operating system, team hierarchy, memory daemon, browser engine or design authority.

## EVIDENCE

### Quality & Red Team

- `shared_ai/quality_review.py`
- `tests/test_quality_review.py`
- `governance/quality/PR_REVIEW_CONTRACT_V1.md`

Verified behaviors:
- evidence-free and low-confidence finding suppression;
- duplicate finding collapse;
- history-sensitive regression/authority review;
- High/Critical accepted finding -> HOLD;
- Outside Voice identity independence;
- disagreement -> HOLD.

### Security & Authority

- `shared_ai/security_review.py`
- `tests/test_security_review.py`
- `governance/security/SECURITY_REVIEW_CONTRACT_V1.md`

Verified behaviors:
- untrusted review source -> HOLD;
- explicit trust-boundary requirement;
- STRIDE coverage;
- OWASP-oriented control coverage;
- evidence/confidence filtered semantic findings;
- unresolved High/Critical finding -> HOLD.

### Verified Production Discipline

- `shared_ai/production_discipline.py`
- `tests/test_production_discipline.py`
- `governance/production/VERIFIED_PRODUCTION_DISCIPLINE_V1.md`

Verified behaviors:
- path scope and frozen-path guard;
- destructive operation -> Human Threshold™;
- risky/parallel work -> isolated worktree;
- root-cause-first debugging order;
- failing regression test before fix;
- reverify after fix;
- completion claim requires verification evidence;
- skill/agent golden + negative + regression fixtures.

### QA / Release

- `shared_ai/release_quality.py`
- `tests/test_release_quality.py`
- `governance/quality/RELEASE_QUALITY_ADAPTER_V1.md`

Verified behaviors:
- diff -> affected route map;
- affected route -> browser evidence;
- production release -> canary evidence;
- benchmark baseline/candidate evidence;
- regression budget breach -> HOLD;
- evidence adapter reuses Builder/VX1 and Publish Engine surfaces.

## Provenance / License Boundary

| Upstream | License observed | ENGÜRÜ handling |
|---|---|---|
| `garrytan/gstack` | MIT | selected mechanism adaptation; no upstream authority |
| `obra/superpowers` | MIT | selected production-discipline mechanisms |
| `anthropics/claude-code-security-review` | MIT | semantic/security mechanisms adapted provider-independently |
| `anthropics/skills/skills/frontend-design` | Apache-2.0 | benchmark/reference only; no parallel skill installed |
| `thedotmack/claude-mem` | Apache-2.0 | principles only; no parallel daemon/runtime installed |
| `anthropics/claude-code` | Anthropic Commercial Terms / all rights reserved notice | mechanism observation only; no restricted upstream implementation copied |

License files were read from the upstream GitHub repositories during this reconciliation. This record is an engineering provenance boundary, not legal advice.

## No-Duplicate-Authority Check

PASS:
- ENGÜRÜ Language Governance™ remains canonical.
- DoneCheck™ remains verification authority.
- Human Threshold™ remains consequential-action authority.
- Secret Zero™ and IP & Model Trust remain intact.
- Existing Quality & Red Team, Security & Authority, Shared AI, Builder/VX1 and Publish Engine surfaces are extended/reused.
- No new Core or parallel framework was introduced.

## Outside Voice Boundary

Technical contract: **PASS**.

Live independent second-provider/model commissioning: **HOLD_PROVIDER**.

Reason:
- current evidence proves the identity/evidence/disagreement contract;
- it does not prove a second independently governed provider/model is commissioned in the Shared AI runtime;
- live independence must not be manufactured from the deterministic verifier or the same provider identity.

This HOLD does not invalidate the technical harvest. It is a future provider commissioning gate.

## claude-mem Decision

**CLOSED — NO PARALLEL RUNTIME.**

Shared AI already provides resume, compaction, current-instruction priority and verified/transient context separation. Progressive verified-memory retrieval may be reconsidered only after a measured long-running project-memory gap.

## frontend-design Decision

**CLOSED — NO PARALLEL SKILL.**

Builder Aesthetic / VX1 / Human Visual Authority remains canonical. Anthropic frontend-design stays a benchmark/reference source.

## DoneCheck™

- selected mechanisms mapped to existing owners: PASS;
- no duplicate framework authority: PASS;
- provenance/license boundary recorded: PASS;
- deterministic tests: PASS;
- fail-closed uncertainty behavior: PASS;
- Human Threshold retained: PASS;
- live second-provider Outside Voice commissioning: HOLD_PROVIDER, separate from technical implementation.

## FINAL JUDGMENT

**PASS — EXTERNAL CAPABILITY HARVEST TECHNICAL IMPLEMENTATION**

**HOLD_PROVIDER — LIVE SECOND-MODEL OUTSIDE VOICE COMMISSIONING**

No additional harvest Core/framework is required.
