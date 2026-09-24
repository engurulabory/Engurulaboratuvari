# ENGÜRÜ Mac Engineer™ v0.8 — Full Product Engineering Chain Binding v1

## STATE

**CANONICAL / ACTIVE — GATE 4**

## INTENT

Bind the complete Product Engineering Operator chain to existing verified ENGÜRÜ
surfaces before product mutation expands.

No new core is introduced by this contract.

Canonical chain:

`INTAKE → DISCOVER → ARCHITECT → DESIGN → BUILD → TEST → REPAIR → PACKAGE → DEPLOY → LIVE VERIFY → LIFECYCLE → EVIDENCE → DoneCheck™ v1.2 → Human Threshold™`

## AUTHORITY

Execution authority:

> **ENGÜRÜ Mac-Native Engineering Authority™**

Machine verification authority:

> **DoneCheck™ v1.2 / 1.2.0 / exact-main `8b90a8fc93453dd8a84994195d28d14b15e261cb`**

Final human authority:

> **Human Threshold™**

Aesthetic judgment authority where applicable:

> **Human Artistic Authority™**

## PRODUCT SOURCE BASELINE

Canonical product:

`engurulabory/enguru-mac-engineer`

Exact main baseline:

`5432b9b135499cea18273c0e003877b864af92c6`

v0.7 reliability remains VERIFIED / LOCKED and is reused.

## BINDING MATRIX

| Stage | Existing owner / surface | Gate 4 binding | Execution proof |
|---|---|---|---|
| INTAKE | `runtime/app.py` + governed task context | REUSE | Gate 6 / 8 |
| DISCOVER | `runtime/repo_manager.py` + `runtime/research_capability.py` | REUSE | Gate 6 / 8 |
| ARCHITECT | `runtime/governance.py` + `runtime/repo_control.py` + current-truth contract | REUSE + bounded adapter | Gate 6 / 8 |
| DESIGN | Gate 3 UX/Aesthetic contract + Aesthetic Motor™ + Human Artistic Authority™ | REUSE | Gate 5 / 8 |
| BUILD | `runtime/local_ci.py` + native preparation/build path | REUSE | Gate 5 / 6 / 8 |
| TEST | `runtime/local_ci.py` + product regression suites | REUSE | Gate 5–11 |
| REPAIR | `runtime/repair.py` + `runtime/support_repair_loop.py` | REUSE | Gate 7 |
| PACKAGE | `execution_prep/native_app/prepare_native_app.command` | REUSE + provenance binding | Gate 5 |
| DEPLOY | governed release/install adapter boundary; existing Publish/installation authority when target requires it | ADAPTER_BOUND | Gate 9 |
| LIVE VERIFY | `runtime/app.py` + `runtime/doctor.py` + real user flow | REUSE + user-flow verifier | Gate 9 |
| LIFECYCLE | `runtime/reliability.py` + `runtime/backup_manager.py` + GitVault recovery | REUSE | Gate 9 |
| EVIDENCE | `runtime/governance.py` + reliability journals/checkpoints + local Evidence roots | REUSE | Gate 5–11 |
| DONECHECK | canonical DoneCheck™ v1.2 product | EXTERNAL_VERIFICATION_AUTHORITY | Gate 12 |
| HUMAN THRESHOLD | explicit human decision | FINAL_AUTHORITY | Gate 12 |

## BINDING RULES

1. Existing verified mechanisms are reused before extension.
2. A bounded adapter is allowed only where the target lifecycle requires a transport or product-specific interface.
3. An adapter does not become a new core.
4. Deployment authority is target-dependent and remains separated from build authority.
5. Health status alone does not satisfy LIVE VERIFY.
6. PACKAGE requires exact-source provenance.
7. REPAIR requires observed failure → root cause → bounded correction → regression → Evidence.
8. EVIDENCE is criterion-scoped and must survive restart/recovery where relevant.
9. DoneCheck™ v1.2 verifies Evidence; it does not manufacture missing Evidence.
10. Human Threshold™ remains final product authority.

## CURRENT REQUIRED DIFFERENCE

Gate 4 defines binding only.

The following execution differences remain for later gates:

- Gate 5: native productization, version/provenance, real package/install/run.
- Gate 6: existing-product change scenario.
- Gate 7: migration/repair scenario.
- Gate 8: new product from brief.
- Gate 9: deploy/live verify/rollback/lifecycle.
- Gate 10: finished-product delivery acceptance.
- Gate 11: consolidated real-Mac commissioning.
- Gate 12: DoneCheck™ v1.2 + Human Threshold™ + version lock.

## MUTATION BOUNDARY

Gate 4 does not modify ENGÜRÜ Mac Engineer™ product source.

Gate 4 verifies:

- exact product baseline;
- all chain stages have explicit ownership;
- existing verified mechanisms are reused;
- adapter boundaries are explicit;
- no duplicate core is introduced;
- later execution-proof gates remain explicit.

## EXIT

Gate 4 PASS:

`V08_FULL_PRODUCT_ENGINEERING_CHAIN_BOUND`

Next:

`V08_NATIVE_APP_PRODUCTIZATION_AND_PROVENANCE`
