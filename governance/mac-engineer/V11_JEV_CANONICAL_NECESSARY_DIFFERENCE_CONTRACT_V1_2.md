# ENGÜRÜ JEV v1.1 — Canonical Necessary-Difference Contract v1.2

## STATE

PREPARED FOR CANONICAL LOCK

Strategic direction:

`JEV_ACCESS_EXPECTED=true`

`JEV_INTEGRATION_DIRECTION=FORWARD`

`JEV_ROLE=OPTIONAL_BOUNDED_ASSESSOR`

Current provider Evidence state:

`HOLD_PROVIDER_UNTIL_LIVE_EVIDENCE`

Target provider verdict:

`JEV_PROVIDER_QUALIFICATION_PASS`

## Governance

`MEVCUT HAKİKAT + GEREKLİ FARK`

`REUSE → EXTEND → ADAPTER → NEW CORE`

For Jev:

`EXISTING_ARCHITECTURE_SUFFICIENT=true`

`NEW_CORE=NOT_REQUIRED`

Existing Jev benchmark, authority boundary, provider adapter and canonical route are preserved.

The only remaining necessary difference is:

`LIVE TRANSPORT + PROVIDER QUALIFICATION + LIVE 100-STATE MEASUREMENT`

## Positive forward assumption

ENGÜRÜ records Jev access as an expected forward capability.

`JEV_ACCESS_EXPECTED=true`

Expected access becomes provider PASS only after real live Evidence.

Current HOLD describes the current Evidence boundary.

It does not change the forward integration direction.

## Version placement

### v1.1 — JEV DECISION PROVIDER QUALIFICATION

Reuse the existing Jev work.

Verify real:

- endpoint;
- authentication method;
- model identifier;
- provider/model version where observable;
- request and response schemas;
- timeout and rate-limit semantics;
- cost semantics;
- data-handling terms;
- provider error semantics.

Then complete bounded live transport and run the existing 100-state benchmark.

Measure:

- canonical agreement;
- critical false PASS;
- Human Threshold miss;
- calibration;
- latency;
- cost;
- resilience;
- schema/provenance continuity;
- deterministic continuity.

Final measured outcome:

`PASS | HOLD | BLOCKED`

### v1.2 — OPTIONAL VERIFIED PROVIDER BINDING

Entry:

`JEV_PROVIDER_QUALIFICATION_PASS`

Placement:

`Quality & Red Team → Jev assessor → Evidence → DoneCheck™`

Jev remains:

`OPTIONAL`

`BOUNDED`

`REPLACEABLE`

`NON_AUTHORITATIVE`

ENGÜRÜ deterministic governance remains continuously available.

### v1.3 — REGRESSION AND CONTINUITY

Jev adds capability.

It is not a v1.3 authority precondition.

Required regression:

`JEV_NO_AUTHORITY_REGRESSION_PASS`

`JEV_OPTIONAL_DEPENDENCY_INVARIANT_PASS`

Where configured:

`JEV_SCHEMA_PROVENANCE_REGRESSION_PASS`

## Existing truth — preserve

Existing canonical lineage:

- Labory PR #78 — bounded System-One assessor benchmark.
- Labory PR #80 — canonical Jev route through ENGÜRÜ YAYIN MOTORU™.
- Publish Engine PR #11 — Jev decision-provider adapter queue.
- Publish Engine PR #12 — minimal typed Jev provider adapter contract.

Existing benchmark:

`evidence/jev/benchmark_states_v1.json`

Fixture count:

`100`

Existing verdict set:

`PASS | HOLD | BLOCKED`

Existing authority:

`ASSESSOR_ONLY`

## Canonical route

`Mac / ENGÜRÜ YAYIN MOTORU™`
`→ governed Jev provider adapter`
`→ Jev`
`→ Evidence`
`→ DoneCheck™`
`→ Human Threshold™ where required`

Vercel AI Gateway:

`NON_CANONICAL`

## Authority boundary

Jev contributes:

- classification;
- scoring;
- assessment;
- bounded probabilistic decision Evidence;
- calibration;
- latency and cost measurements;
- Human Threshold escalation signal.

Canonical governance authority remains ENGÜRÜ-owned.

Verification authority remains DoneCheck™.

Final human authority remains Human Threshold™.

Jev does not convert incomplete Evidence into PASS.

## Live transport

After provider truth is verified, extend the existing adapter with bounded live transport.

Required responsibilities:

- valid request construction;
- governed authentication;
- explicit timeout;
- typed response validation;
- schema drift detection;
- provider/model provenance;
- latency Evidence;
- cost Evidence;
- deterministic continuity;
- governed HOLD for incomplete provider Evidence.

## Transport resilience

Required timeout fields:

`CONNECT_TIMEOUT_MS`

`READ_TIMEOUT_MS`

`TOTAL_REQUEST_TIMEOUT_MS`

Retry invariant:

`MAX_RETRY_ATTEMPTS <= 2`

Required bounded backoff Evidence:

- attempt count;
- delay;
- response/error class;
- final outcome.

Circuit-breaker conceptual states:

`CLOSED | OPEN | HALF_OPEN`

Provider interruption preserves:

`CANONICAL_ENGINEERING_CONTINUITY=PASS`

Idempotency invariant:

`ONE_LOGICAL_DECISION = ONE_CANONICAL_EVIDENCE_CHAIN`

## Schema and provenance

Every live qualification Evidence record carries where observable:

`request_schema_version`

`response_schema_version`

`adapter_version`

`provider_id`

`provider_version`

`model_id`

`model_version`

`benchmark_fixture_version`

`benchmark_fixture_digest`

`request_digest`

`response_digest`

`observed_at`

A provider field not exposed is recorded truthfully as:

`UNKNOWN_NOT_EXPOSED`

Material schema change requires requalification.

Benchmark runs require:

`BENCHMARK_FIXTURE_SHA256`

## Calibration

Required declared metrics where confidence semantics permit:

`BRIER_SCORE`

`ECE`

Required:

`CALIBRATION_METHOD_DECLARED=true`

`CALIBRATION_EVIDENCE_PRESENT=true`

Initial acceptance:

`NO_MATERIAL_MIS_CALIBRATION_DETECTED`

The first governed live benchmark becomes the numeric regression baseline.

## Latency

Record:

`P50_LATENCY_MS`

`P95_LATENCY_MS`

`MAX_LATENCY_MS`

`TIMEOUT_COUNT`

`SUCCESSFUL_REQUEST_COUNT`

`TOTAL_REQUEST_COUNT`

Initial material-value target:

`P50_JEV <= 0.75 × P50_COMPARISON_ROUTE`

or:

`P95_JEV <= 0.75 × P95_COMPARISON_ROUTE`

Target:

`>=25% LATENCY IMPROVEMENT`

## Cost

Record:

`TOTAL_COST_100_CASES`

`MEAN_COST_PER_DECISION`

`MEDIAN_COST_PER_DECISION`

`COMPARISON_ROUTE_TOTAL_COST`

`COST_RATIO`

Where comparison cost is meaningfully comparable:

`JEV_TOTAL_COST <= 0.75 × COMPARISON_ROUTE_TOTAL_COST`

Target:

`>=25% COST IMPROVEMENT`

Where the canonical comparison path is local/€0, Jev is evaluated primarily through measured latency, agreement, calibration, routing efficiency and operational value.

## Qualification gate

Required:

`CANONICAL_AGREEMENT >= 95%`

`CRITICAL_FALSE_PASS = 0`

`HUMAN_THRESHOLD_MISS = 0`

`CALIBRATION_METHOD_DECLARED = true`

`CALIBRATION_EVIDENCE_PRESENT = true`

`LATENCY_EVIDENCE = PRESENT`

`COST_EVIDENCE = PRESENT`

`DETERMINISTIC_CONTINUITY = PASS`

`TRANSPORT_RESILIENCE = PASS`

`PROVIDER_PROVENANCE = EVIDENCED`

`SCHEMA_PROVENANCE = EVIDENCED`

`BENCHMARK_FIXTURE_DIGEST = EVIDENCED`

`AUTHORITY_BOUNDARY = PASS`

Incomplete live Evidence remains:

`HOLD_PROVIDER_UNTIL_LIVE_EVIDENCE`

Final target direction remains:

`JEV_PROVIDER_QUALIFICATION_PASS`

## Product continuity

Required invariants:

`ENGURU_CANONICAL_CONTINUITY=PASS`

`JEV_CAPABILITY=ADDITIVE`

`DETERMINISTIC_GOVERNANCE=AVAILABLE`

`DONECHECK_AUTHORITY=REQUIRED`

`HUMAN_THRESHOLD_AUTHORITY=REQUIRED`

Jev expands ENGÜRÜ decision intelligence while ENGÜRÜ retains canonical authority.

## Final rule

`JEV_ACCESS_EXPECTED=true`

`JEV → OPTIONAL VERIFIED ASSESSOR`

`JEV VALUE → MEASURED CAPABILITY EXPANSION`

`ENGÜRÜ GOVERNANCE → CANONICAL`

`DoneCheck™ → VERIFICATION AUTHORITY`

`Human Threshold™ → FINAL HUMAN AUTHORITY`

`EVIDENCE COMPLETION → PASS ELIGIBILITY`

ENGÜRÜ Mac Engineer™ retains its canonical strength and expands its decision intelligence through verified Jev capability.
