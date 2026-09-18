# ENGÜRÜ Shared AI Infrastructure™ v0.1

## STATE
FOUNDATION — theoretical/technical architecture only. Runtime/provider commissioning is not claimed.

## ROLE
A shared AI service layer inside ENGÜRÜ Labory. It is not a standalone product, repository or authority domain.

## LOCKED PRINCIPLE
**The system may optimize itself; it may not expand its own authority.**

## PURPOSE
Provide one governed interface for Builder, Steward, Publish Engine, ZEKÜ and future Labory products without binding any product directly to OpenAI, Groq, Cerebras, Cloudflare, Gemini, OpenRouter or another model vendor.

## FLOW
```
PRODUCT / AGENT
  -> Unified LLM Interface
  -> Identity + Authority
  -> Data Classification
  -> Policy Gate
  -> Capability Match
  -> Zero-Cost Gate
  -> Context Preflight
  -> Health + Quota Gate
  -> Smart Router
  -> Provider Adapter / Local Runtime
  -> Result Verifier
  -> Evidence Ledger
  -> Learning Signals
  -> Model Intelligence
  -> Proposal
  -> Human Threshold when authority/policy/production changes
```

## REQUIRED COMPONENTS
1. Unified LLM Interface
2. Policy Engine
3. Provider Registry
4. Capability Registry
5. Smart Router
6. Circuit Breaker + bounded retry/failover
7. Zero-Cost Guard
8. Local fallback
9. Result Verifier
10. Evidence Ledger
11. Offline test harness
12. Security/red-team gate
13. Model Intelligence + lifecycle management

## AUTHORITY BOUNDARIES
The system MAY automatically:
- collect non-secret model/provider metadata;
- observe health, latency, quota and availability;
- record benchmark/eval results;
- lower routing preference after verified degradation;
- propose a better route or candidate model.

The system MUST NOT automatically:
- relax privacy policy;
- expand commercial-use authority;
- enable paid use;
- transmit SECRET data to an external provider;
- change production default authority;
- approve a new provider/model for production;
- alter Human Threshold rules.

## DEPENDENCY STRATEGY
Preferred reusable open-source layers:
- LiteLLM: provider normalization/routing adapter layer;
- Open Policy Agent: declarative policy evaluation;
- OpenTelemetry: traces/metrics/log transport;
- Promptfoo: eval/red-team/regression;
- OpenAI Agents SDK: optional orchestration/testing layer with non-OpenAI providers;
- local OpenAI-compatible runtime: final fallback.

No dependency is canonical policy authority. ENGÜRÜ policy, registry and evidence contracts remain authoritative.

## FAIL-CLOSED RULES
- Unknown privacy -> BLOCKED
- Unknown commercial-use status -> BLOCKED
- Unknown cost when paid use is not authorized -> BLOCKED
- Capability mismatch -> BLOCKED
- Context overflow risk -> reroute or BLOCKED
- All providers unavailable -> local fallback; if incapable -> HOLD
- Evidence failure does not convert to PASS

## PRODUCT CONNECTION MAP
- Builder: code generation, code review, reasoning, structured output, repo analysis.
- Steward: audit, simplification, governance checks, drift detection, repair proposals.
- Publish Engine: generation, translation, summarization, metadata and governed publishing assistance.
- ZEKÜ: research assistance, classification, reasoning, document analysis and policy-permitted financial-support tasks.

Products call only the Labory service contract. Direct provider coupling is prohibited by architecture.

## MODEL LIFECYCLE
DISCOVERED -> UNVERIFIED -> BENCHMARKING -> CANDIDATE -> APPROVED -> ACTIVE -> DEGRADED -> DEPRECATED -> REMOVED

Production promotion requires evidence and Human Threshold where the change affects authority, privacy, cost or external consequence.

## COMPLETION BOUNDARY
This package can be structurally PASS before provider commissioning.
Runtime Verified Finish remains HOLD until offline tests, live provider commissioning, failover, quota exhaustion, privacy, local fallback, recovery and evidence are observed.
