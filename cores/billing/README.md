# ENGÜRÜ Billing Core™ v0.1

STATE: HOLD — foundation only. Production activation requires live external evidence.

## Purpose
One provider-neutral contract for every ENGÜRÜ product:

verified sale -> invoice decision -> PARK/GİB -> document evidence -> customer delivery -> DoneCheck™

Products do not integrate PARK directly.

## Production adapters
- payment verification adapter
- PARK taxpayer registry adapter
- PARK invoice/status/download adapter
- current UBL-TR document factory
- transactional mail adapter
- persistent idempotency/evidence store

## Fail-closed rules
- no verified payment, no invoice
- amount/currency mismatch blocks
- taxpayer lookup determines e-Fatura vs e-Arşiv
- internet e-Arşiv uses a separate series
- provider acceptance and final document identity are required before delivery
- duplicate order/idempotency keys cannot issue a second invoice
- secrets are stored only in deployment secret storage

## Verified Finish
Production PASS requires PARK authentication, authorized series, UBL-TR validation, payment-webhook verification, document issue/status/download proof, mail-delivery proof, duplicate/retry tests, cancellation/refund tests, evidence persistence, and Human Threshold approval for live fiscal issuance.
