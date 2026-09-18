# ENGÜRÜ Shared AI Infrastructure™ — Local Runtime Commissioning Evidence

Date: 2026-09-18
Canonical main at commissioning proof: `102b50b80fad64220e9825c41950e7c9250281c7`

## State
IN_PROGRESS — Evidence complete; final Verify and registry activation pending.

## Runtime
- Ollama installed and service available on macOS.
- Local model: `qwen3:14b`.
- Direct local inference observed: `ENGURU_LOCAL_PASS`.
- Shared AI health observed:
  - `state=PASS`
  - `service=ENGURU_SHARED_AI_INFRASTRUCTURE`
  - `runtime=UP`
  - `active_providers=1`

## Real Shared AI Route
Observed through `/v1/enguru/respond`:
- `state=PASS`
- provider: `local_runtime`
- model: `qwen3:14b`
- attempts: `1`
- fallback path: `local_runtime:PASS`
- reason: `verified_execution`
- route cost evidence: `estimated_cost=0.0`

Earlier canonical route proof returned exact output:
- `ENGURU_SHARED_AI_PASS`

Recovery proof returned exact output:
- `ENGURU_RECOVERY_PASS`

## Fail-Closed Verification
Observed:
- SECRET request stayed local and PASSed via `local_runtime`.
- Paid route deterministic gate: PASS / blocked.
- Unverified privacy route deterministic gate: PASS / blocked.
- Unverified commercial-use route deterministic gate: PASS / blocked.
- Capability mismatch:
  - HTTP `503`
  - `state=HOLD`
  - `local_runtime:SKIP:capability`
  - `reason=no_safe_provider`
- Ollama unavailable while Shared AI remained UP:
  - HTTP `503`
  - `state=HOLD`
  - `local_runtime:ERROR:URLError`
  - `reason=no_safe_provider`
- Ollama restart recovery:
  - `state=PASS`
  - output `ENGURU_RECOVERY_PASS`
  - provider `local_runtime`
  - model `qwen3:14b`

## Security / Leakage
Captured commissioning outputs contained no API token, provider secret, credential, or external secret material.

## Evidence Verdict
Evidence set: COMPLETE for local runtime commissioning.
Final ACTIVE/PASS remains gated on:
1. canonical-config reproducibility rerun,
2. registry synchronization,
3. no Labory truth conflict,
4. DoneCheck final record.
