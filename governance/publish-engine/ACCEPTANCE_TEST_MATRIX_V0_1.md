# ENGÜRÜ YAYIN MOTORU™ v0.1 — Acceptance Test Matrix

## HÜKÜM KURALI

**100/100 = yalnız 10/10 gate PASS ve her gate için current evidence mevcutsa.**

Bir gate HOLD ise toplam sonuç **HOLD**.
Bir kritik security/authority gate FAIL ise toplam sonuç **FAIL**.

| Gate | Weight | Required proof | Positive test | Negative test | Verdict |
|---|---:|---|---|---|---|
| Architecture Simplicity | 10 | bounded module map | engine starts with minimal config | unknown module/config rejected | HOLD |
| Source Truth | 10 | exact repo/branch/SHA | correct source resolves | wrong repo/branch/stale SHA rejected | HOLD |
| Deterministic Build | 10 | repeatable artifact digest | same source → same digest where build permits | dirty tree/untracked mutation blocks | HOLD |
| Artifact / Provenance | 10 | source SHA ↔ artifact digest receipt | receipt binds correct artifact | forged/stale receipt rejected | HOLD |
| Cloud Publication | 10 | provider deployment receipt | preview + production deploy | wrong account/project/auth scope blocks | HOLD |
| Domain / DNS / TLS | 10 | domain bind + DNS + cert + HTTPS | expected domain returns expected status | wrong DNS/expired TLS/wrong host blocks VERIFIED_LIVE | HOLD |
| Rollback | 10 | previous verified release + rollback receipt | rollback → public re-verification | arbitrary/unverified target refused | HOLD |
| Multi-Site Isolation | 10 | isolated per-site state/evidence | site A publish leaves B unchanged | A failure cannot mutate B | HOLD |
| Zero-Cost Guard | 10 | free-capacity/cost decision receipt | no paid mutation occurs | paid-only requirement produces HOLD | HOLD |
| Evidence / DoneCheck / Cockpit | 10 | immutable receipt + terminal truth | operator sees true current state | UI cannot manufacture PASS | HOLD |

---

## REQUIRED FIELD SCENARIOS

### F01 — First publication
`manifest → preflight PASS → preview → Human Threshold → production → domain → DNS → TLS → HTTPS → parity → evidence → DoneCheck PASS → VERIFIED_LIVE`

### F02 — Safe rollback
`current VERIFIED_LIVE → previous verified release → Human Threshold → rollback → DNS/TLS/HTTPS/parity re-check → rollback receipt → VERIFIED_LIVE`

### F03 — DNS failure
Wrong/missing DNS must end in:
`HOLD`
and must never produce VERIFIED_LIVE.

### F04 — TLS failure
Invalid/not-ready TLS must end in:
`HOLD`.

### F05 — Dirty source
Uncommitted source drift must block publication:
`HOLD`.

### F06 — Stale approval
Approval from a previous source/artifact must not authorize a newer candidate.

### F07 — Cost escalation
Any operation requiring a paid plan or incremental mandatory platform spend must stop:
`HOLD — HUMAN THRESHOLD`.

### F08 — Cross-site isolation
Publishing Site A must not mutate Site B project/domain/state/evidence.

### F09 — Credential leakage
Logs and receipts are scanned for provider token/secret leakage.
Any leak:
`FAIL`.

### F10 — VERIFY ALL
Must be read-only.
No provider mutation permitted.

---

## REAL 100/100 EXIT

All of the following must be current and evidence-backed:

- 10 gates PASS,
- F01 PASS,
- F02 PASS,
- all negative tests PASS,
- zero secret leakage,
- zero unapproved paid mutation,
- DoneCheck™ PASS,
- Human Threshold™ publication and rollback records,
- exact source/artifact/deployment/domain chain preserved.

Until then:

**REAL FIELD SCORE — HOLD**
