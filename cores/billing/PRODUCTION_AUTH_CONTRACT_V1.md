# ENGÜRÜ Billing Core™ — Production Authentication Contract v1.0

## STATE
HOLD — no live fiscal action is authorized until authentication and account identity proofs pass.

## Required secrets
- PARK_API_USERNAME
- PARK_API_PASSWORD

Secrets must exist only in the deployment/runtime secret store.
They must never be committed to Git, printed to logs, or copied into evidence.

## Required configuration
- PARK_API_BASE_URL
- PARK_API_VERSION
- PARK_EINVOICE_SERIES=ENG
- PARK_EARCHIVE_NORMAL_SERIES=EGR
- PARK_EARCHIVE_INTERNET_SERIES=INT

## Live proof sequence

1. Authenticate against the PARK production API.
2. Receive the PARK SESSION_ID documented by the provider integration protocol.
3. Keep the session only in runtime memory/cache for its validity period.
4. Call a read-only account/customer identity endpoint.
5. Verify that the returned legal account belongs to ENGÜRÜ Maya.
6. Run a read-only taxpayer lookup.
7. Record only redacted evidence:
   - timestamp
   - endpoint class
   - HTTP/result status
   - account-match PASS/HOLD
   - taxpayer-query PASS/HOLD
   - no credentials or session identifiers

## PASS criteria
- Authentication succeeds.
- A valid SESSION_ID is returned.
- Account/customer identity matches ENGÜRÜ Maya.
- Read-only taxpayer lookup succeeds.
- No secret or session identifier leakage is observed.

## HOLD
- Endpoint mismatch.
- Credential mismatch.
- Account identity cannot be verified.
- Taxpayer lookup is unavailable.

## BLOCKED
- Production authentication cannot be completed.
- Required production access is not provisioned.

## NEXT ACTION after PASS
Controlled first fiscal proof:

verified payment
→ taxpayer decision
→ one controlled INTERNET e-Arşiv invoice using INT
→ PARK/GİB status verification
→ official PDF/XML retrieval
→ customer delivery evidence
→ accounting delivery evidence
→ Evidence
→ DoneCheck™
→ Human Threshold™
