# P06 G2 v16 — Independent Trust Policy & Key Authority — Human Threshold Contract

STATE: HOLD_PENDING_INDEPENDENT_HUMAN_ACCEPTANCE
SCOPE: PR #184 review candidate. No official issuer, DoneCheck, or Verified Finish promotion.

## Existing evidence
- Synthetic OSi exact-head field: prior 17/17 PASS at 895a7536450dd3fcd669d2cc630f9bc2e437018e.
- Subsequent source changes require exact-new-head CI and OSi test receipts.
- DoneCheck v1.2 core: engurulabory/donecheck@8b90a8fc93453dd8a84994195d28d14b15e261cb.
- Historic source scope MAIN pinned in v15. Trust must not be silently expanded to a new main SHA.

## Human-controlled approval inputs
1. Human approver identity and authority basis, explicit timestamp and approved scope.
2. Independently authorized policy document SHA-256 obtained outside candidate-supplied data, plus authorized origin and storage protection evidence.
3. Producer ID, public key fingerprint, key ID and independently established proof of private key custody; private key stays outside repository.
4. Authorized task/source MAIN/DoneCheck commit, artifact scope, expiry, rotation and revocation procedure with human roles and emergency block.
5. Live signed producer evidence receipt provenance verified against raw artifact digests.
6. Ledger threat model: same-UID adversary/path substitution, root permissions and post-restart uncertainty; explicit risk owner and disposition.
7. Storage durability: observed fault-injection proof versus *unverified* physical power-loss guarantees; independent disk durability acceptance or expressly documented HOLD.
8. Independent code/security reviewer verdict, exact PR HEAD, CI receipts and native OSi field receipts.

## Decision gate
Human Threshold may explicitly ACCEPT limited trust policy, REJECT, or HOLD with evidence identifiers. Absent signed human-approved policy and independent signer attestation: G2 official=HOLD. Even G2 acceptance cannot create G3 DoneCheck verifyTask PASS or G4 Verified Finish automatically. PR merge is a separate human approval decision.

## Test hook boundary
Production entry: qualifyProducer(input), no environment-triggered fault injection.
Separate explicitly exported review-only helper: qualifyProducerWithFaults(input,testFaults), used only by test child process. Export remains a potential mis-use surface and MUST receive independent security review before live deployment. A production build can remove the test helper once approved; prior test results remain scoped to review candidate.

STATE=HOLD_HUMAN_POLICY_AND_KEY_AUTHORITY
NEXT_ACTION=EXACT_HEAD_CI_AND_OSI_FIELD_THEN_INDEPENDENT_HUMAN_REVIEW
