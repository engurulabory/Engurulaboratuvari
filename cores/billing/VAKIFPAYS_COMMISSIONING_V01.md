# ENGÜRÜ Tahsilat Motoru™ — VakıfPayS Commissioning v0.1

STATE: HOLD — local/provider adapter preparation complete; merchant commissioning and live field proof are external.

## Locked architecture

ENGÜRÜ products
→ ENGÜRÜ Billing Core™ payment verification boundary
→ VakıfPayS Hosted Payment Page (HPP)
→ VakıfPayS QUERYTRANSACTION verification
→ verified PaymentProof
→ PARK / GİB invoice flow
→ evidence / DoneCheck™

## Why HPP first

- card PAN/CVV never enters ENGÜRÜ runtime
- 3D Secure and card-entry surface stay on VakıfPayS
- ENGÜRÜ creates the session, redirects the customer, receives the return, then independently queries the provider
- browser callback is evidence of message integrity only; it is never sufficient for VERIFIED PAYMENT

## Implemented preparation

- TEST / LIVE fail-closed mode
- merchant credentials only through environment variables
- SESSIONTOKEN / HPP session creation
- HTTPS return URL requirement
- current `sdSha512` callback integrity verification
- mandatory QUERYTRANSACTION before creating `PaymentProof(verified=True)`
- exact amount and currency reconciliation
- provider rejection / malformed response fail-closed behavior
- REFUND adapter surface
- no card PAN/CVV collection in ENGÜRÜ adapter
- unit tests for the provider boundary

## Runtime secrets

Never commit these values:

- `VAKIFPAYS_MERCHANT`
- `VAKIFPAYS_MERCHANT_USER`
- `VAKIFPAYS_MERCHANT_PASSWORD`
- `VAKIFPAYS_SECRET_KEY`
- `VAKIFPAYS_MODE=TEST|LIVE`

## External Human Threshold still required

Tunahan Bey / VakıfPayS must provide or confirm:

1. Engürü Maya merchant activation and test/live credentials.
2. Foreign-issued-card authority / limits for the merchant.
3. EUR, USD and GBP settlement behavior into VakıfBank currency accounts.
4. Engürü Maya commission and settlement timing.

## Commissioning sequence after credentials arrive

1. Store TEST credentials outside git.
2. Create a TEST HPP session.
3. Complete a provider test-card transaction.
4. Verify callback signature.
5. QUERYTRANSACTION and reconcile payment id + amount + currency.
6. Emit verified Billing Core `PaymentProof`.
7. Exercise reject, retry, duplicate and refund paths.
8. Record evidence.
9. Switch to LIVE only after Human Threshold approval.
10. Run one controlled low-value live transaction.
11. Reconcile VakıfPayS receipt → VakıfBank settlement → PARK invoice.
12. DoneCheck™.

## Verdict

LOCAL PREPARATION — PASS when repository CI passes.

PROVIDER COMMISSIONING — HOLD.

LIVE MONEY — HOLD / Human Threshold.
