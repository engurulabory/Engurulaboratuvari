# P06 G2 v16 — Independent Human Authority Decision Record v1

STATE=HOLD_AWAITING_INDEPENDENT_AUTHORITY_EVIDENCE
TYPE=REVIEW_RECORD_NOT_APPROVAL
PR=184
REVIEW_HEAD=99cce83845f037ba31a8ff6fb6138d359e7ff7b2
DATE=2026-10-10
SOURCE=governance/mac-engineer/P06_G2_V16_HUMAN_TRUST_POLICY_ACCEPTANCE.md

## Verified engineering evidence
- Operator-submitted isolated OSi exact-head run: 17/17 tests PASS, TEST_RC=0, STATE=PASS_V16_FINAL_AUTHORITY_PREFLIGHT_FIELD.
- Independent GitHub exact-head CI: 5/5 completed success.
- Production fault hook isolation source reviewed in PR; hardware-level durability and independent authority are outside the test claim.

## Human evidence gates — decisions based on supplied records
| Gate | Required verified evidence | Current finding |
| --- | --- | --- |
| A01 | Human approver identity, authority, explicit scope and dated approval | HOLD: no independently authenticated human authorization record |
| A02 | Canonical trust policy source, independent SHA-256 pin, signed approval and protected location | HOLD: authoritative accepted policy not supplied |
| A03 | Live producer ID, key ID, public key SHA-256 fingerprint and independently verified key custody | HOLD: live key custody and enrolled fingerprint not established |
| A04 | Revocation, rotation, expiry, incident response and responsible authority | HOLD: approved operational lifecycle not evidenced |
| A05 | Real signed producer receipt and raw source artifact digest binding | HOLD: synthetic tests only |
| A06 | Storage model: power-loss guarantees, ledger ownership, recovery and same-UID attacker assumption | HOLD: no independent risk owner acceptance or physical durability receipt |
| A07 | Independent security reviewer and scoped acceptance signature | HOLD: absent |
| A08 | Separate explicit PR merge authorization | HOLD: absent |

## Explicit risk dispositions
PHYSICAL_POWER_LOSS=HOLD_UNVERIFIED
SAME_UID_LEDGER_SUBSTITUTION=HOLD_UNVERIFIED
POWER_LOSS_OR_UNCERTAIN_LEDGER_SLOT=FAIL_CLOSED_HOLD_REQUIRES_REVIEW
TRUST_ROOT_AUTHORITY=HOLD
LIVE_SIGNER_AUTHORITY=HOLD
PRODUCTION_PROMOTION=HOLD

## Decision boundaries
CANDIDATE_SYNTHETIC_SECURITY=PASS
HUMAN_THRESHOLD_G2=HOLD
OFFICIAL_PRODUCER_ISSUER_G2=HOLD
DONECHECK_VERIFYTASK_G3=HOLD
VERIFIED_FINISH_G4=HOLD
PR184_MERGE=HOLD

A later human approval requires an authenticated reviewer to identify exact evidence hashes and approve the exact scope. A ChatGPT-authored decision record does not constitute signature or approval. Real key material must stay out of GitHub source, comments, and conversation.

NEXT_ACTION=HUMAN_REVIEW_AUTHORITATIVE_POLICY_KEY_CUSTODY_REVOCATION_AND_RISK_EVIDENCE
