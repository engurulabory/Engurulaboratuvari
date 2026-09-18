# Jev System-One Benchmark Adapter — Experiment Contract v1

**STATE:** HOLD / EXPERIMENT  
**Authority:** assessor only; never authority.  
**Placement:** existing Quality & Red Team → DoneCheck™ lane.  
**Rule:** reuse → extend → adapter → new core.

## Purpose

Compare Jev decisions against ENGÜRÜ deterministic governance without changing canonical authority.

Input contract:
- Labory state
- canonical verdict: `PASS | HOLD | BLOCKED`
- Human Threshold™: `true | false`
- critical-authority flag
- evidence/source reference

Measured outputs:
- canonical agreement
- critical false PASS count
- Human Threshold miss count
- calibration assessment
- latency
- cost
- deterministic fallback

## JEV EXPERIMENT GATE

- Canonical agreement >= 95%
- Critical false PASS = 0
- Human Threshold miss = 0
- Calibration = acceptable under the declared evaluation method
- Latency = meaningfully lower than the comparison reasoning route
- Cost = meaningfully lower than the comparison reasoning route
- Deterministic fallback = PASS

Any missing live-provider metric keeps the experiment at HOLD.

## Authority boundary

Jev may classify, score or assess. It may not:
- grant Human Threshold approval;
- convert missing evidence into PASS;
- override Secret Zero™, DoneCheck™, Repository Order or Language Governance;
- expand provider/tool authority;
- mutate canonical truth by itself.

## Fixture truth

`evidence/jev/benchmark_states_v1.json` contains 100 canonical-derived governance fixtures. They are reproducible evaluation inputs, not claimed historical production events.

## Final outcomes

- PASS → adapter may be adopted inside the existing lane.
- HOLD → more evidence/provider commissioning required.
- BLOCKED → adapter is removed; deterministic governance remains canonical.


## Canonical execution route — locked

Primary route:
`Mac / ENGÜRÜ YAYIN MOTORU™ → governed provider adapter → Jev → Evidence → DoneCheck™`

Vercel AI Gateway is not part of the canonical Jev execution architecture. It may be used only as a non-canonical external reference path if explicitly authorized for a separate experiment.

The Jev adapter must inherit existing Publish Engine / Labory provider boundaries:
- local credential handling;
- no caller self-granted authority;
- explicit cost/accounting evidence;
- fail-closed HOLD on missing provider access;
- Human Threshold™ before any consequential external side effect.
