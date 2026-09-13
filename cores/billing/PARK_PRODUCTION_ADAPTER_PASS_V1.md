# PARK Production Adapter Pass™ v1.0

## STATE
HOLD — technical adapter can PASS before live fiscal proof.

## Provider truth
PARK e-Fatura / e-Arşiv uses SOAP services.

Documented methods used by this adapter:
- Login / Logout
- CheckUser
- SendInvoice
- GetInvoiceStatus
- GetInvoiceWithType
- WriteToArchiveExtended
- ReadFromArchive
- GetEArchiveInvoiceStatus

Login returns a SESSION_ID for following service calls.

Production service addresses and account-identity method are provider-confirmed configuration and are not guessed in source code.

## Repository implementation
- provider-neutral Billing Core
- PARK mock adapter
- PARK service adapter
- endpoint configuration contract
- authenticated transport boundary
- taxpayer lookup routing
- e-Fatura / e-Arşiv issue routing
- status lookup
- document download contract
- idempotency propagation
- ENG / EGR / INT series preservation
- fail-closed response checks
- dedicated PARK Adapter CI

## Live acceptance sequence
provider endpoint truth
→ Login / SESSION_ID
→ legal account identity
→ CheckUser
→ controlled INT e-Arşiv
→ PARK/GİB status
→ official PDF/XML
→ customer delivery evidence
→ accounting delivery evidence
→ duplicate/retry proof
→ Evidence
→ DoneCheck™
→ Human Threshold™

## PASS rule
Technical PASS requires adapter tests and CI.

Production Verified Finish requires live acceptance evidence for every applicable item above.

Mock-only evidence does not satisfy the production gate.
