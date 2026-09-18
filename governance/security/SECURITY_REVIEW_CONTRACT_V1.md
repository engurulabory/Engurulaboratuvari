# ENGÜRÜ Security & Authority — Semantic Review + Threat Model Contract

State: IMPLEMENTED CANDIDATE — exact-head CI required.

This extends the existing Security & Authority layer. It is not a new core.

## Flow

`TRUSTED SOURCE → DIFF SCOPE → TRUST BOUNDARIES → STRIDE → OWASP CONTROLS → SEMANTIC FINDINGS → EVIDENCE/CONFIDENCE FILTER → VERDICT → DoneCheck™`

## STRIDE coverage

- S — Spoofing / identity substitution
- T — Tampering / unauthorized mutation
- R — Repudiation / missing accountable evidence
- I — Information disclosure
- D — Denial of service / availability degradation
- E — Elevation of privilege / authority expansion

Missing required category evidence produces HOLD.

## OWASP-oriented controls

The baseline contract requires evidence for:

- authentication;
- authorization;
- input validation;
- injection resistance;
- secret handling;
- data exposure boundaries;
- logging / accountable evidence.

Missing required control evidence produces HOLD.

## Semantic review rules

1. Untrusted review source -> HOLD.
2. Missing diff scope -> HOLD.
3. Security-sensitive work without an explicit trust boundary -> HOLD.
4. Threat-model coverage is evidence-bound; labels alone do not count.
5. Evidence-free or low-confidence semantic findings are suppressed as noise.
6. High/Critical unmitigated findings -> HOLD.
7. Provider-specific scanners may contribute evidence but never become canonical authority.
8. Prompt-injection/untrusted-PR execution must not be treated as trusted evidence.
9. Secret Zero™, Human Threshold™, IP & Model Trust and DoneCheck™ remain canonical.
10. A machine security PASS cannot authorize an irreversible external action.

## Provenance

Mechanisms were informed by public patterns in Anthropic security-review and gstack CSO/threat-model workflows. ENGÜRÜ implements its own provider-independent contract.
