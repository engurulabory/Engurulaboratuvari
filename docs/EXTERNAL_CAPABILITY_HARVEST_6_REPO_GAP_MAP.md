# External Capability Harvest — 6 Repo Gap Map

Date: 2026-09-18  
Authority: ENGÜRÜ Labory Control Plane  
Mode: research/adaptation only — no parallel framework authority

## STATE

**HOLD FOR IMPLEMENTATION / PASS FOR GAP CLASSIFICATION**

This document records mechanism-level findings from six external GitHub sources and maps them into existing ENGÜRÜ layers.

Core rule:

`mevcut hakikat + gerekli fark`

Reuse rule:

`reuse → extend → adapter → new core`

No external repository becomes an ENGÜRÜ control plane.

## Source set

| Source | Upstream | Decision |
|---|---|---|
| Superpowers | https://github.com/obra/superpowers | **KESİN AL — selected mechanisms** |
| Anthropic frontend-design | https://github.com/anthropics/skills/tree/main/skills/frontend-design | **ALMAYALIM as parallel skill** |
| Anthropic Claude Code code-review | https://github.com/anthropics/claude-code/tree/main/plugins/code-review | **MUTLAKA AL — mechanism clean-room adaptation** |
| Anthropic security-review | https://github.com/anthropics/claude-code-security-review | **KESİN AL — selected mechanisms** |
| claude-mem | https://github.com/thedotmack/claude-mem | **ALSAK DA OLUR — principles only** |
| gstack | https://github.com/garrytan/gstack | **MUTLAKA AL — selected mechanisms** |

## What ENGÜRÜ already has

Current ENGÜRÜ layers already cover:

- state → claim → evidence → next action;
- DoneCheck™ and Human Threshold™;
- governed product/team routing;
- Quality & Red Team;
- Security & Authority;
- browser QA / VX1;
- Aesthetic / Human Visual Authority;
- context resume + deterministic compaction;
- deterministic independent verifier;
- contradiction and unsupported-claim checks;
- citation/provenance evidence;
- fail-closed provider/tool routing.

Therefore this harvest is not an operating-system replacement.

## Gap map

### 1. gstack — MUTLAKA AL

Adapt:

- bounded second-model / outside-voice review;
- runtime careful/freeze/guard semantics;
- diff → affected surface → browser QA;
- post-deploy canary;
- performance benchmark/regression trend;
- CSO-style threat modelling.

Place into:

- Shared AI Infrastructure™;
- Quality & Red Team;
- Security & Authority;
- Release & Reliability.

Do not import:

- parallel CEO/team hierarchy;
- framework-level authority over ENGÜRÜ;
- any command that bypasses Human Threshold or Repository Order.

### 2. Anthropic Claude Code code-review — MUTLAKA AL

Adapt:

- PR-diff semantic review;
- repository-history / blame-aware context;
- separate review lanes;
- confidence/high-signal filtering;
- exact SHA / line evidence;
- duplicate and low-confidence suppression.

Place into:

**Quality & Red Team**

Canonical ENGÜRÜ flow:

`PR DIFF → GOVERNANCE REVIEW → BUG REVIEW → HISTORY REVIEW → INDEPENDENT VERIFY → EVIDENCE FILTER → QA VERDICT → DoneCheck™`

License/provenance note:

Do not copy restricted upstream implementation into ENGÜRÜ. Reimplement the observed mechanism against ENGÜRÜ contracts.

### 3. Anthropic security-review — KESİN AL

Adapt:

- semantic diff security review;
- trusted-source / authority preflight;
- auth/trust-boundary/input/output review;
- prompt-injection-aware review boundary;
- OWASP/STRIDE coverage contract;
- false-positive suppression.

Place into:

**Security & Authority**

Canonical rule:

Provider-specific API dependence must not become governance authority. Local/provider-independent execution is preferred where it satisfies evidence requirements.

### 4. Superpowers — KESİN AL

Adapt:

- reproduce before repair;
- root-cause-first debugging;
- one hypothesis → smallest experiment;
- failing regression test before fix when applicable;
- verification-before-completion;
- isolated worktree execution for risky/parallel work;
- skill/agent behavior pressure tests.

Place into:

- Closed-Loop Production Core™ discipline;
- Verified Agent Operating behavior;
- Quality & Red Team;
- Repository Steward™ where repository isolation helps.

Do not import:

- a second orchestration constitution;
- mandatory skill authority above ENGÜRÜ Language Governance™.

### 5. claude-mem — ALSAK DA OLUR

Potentially adapt later:

- progressive retrieval;
- compact index → detail-on-demand;
- durable memory limited to verified project truth.

Current decision:

**Do not install a parallel memory daemon/runtime.**

Reason:

Shared AI v0.3 already has resume, deterministic context compaction, current-steering precedence and verified/transient state separation. A second memory runtime adds operational and privacy surface before a measured gap exists.

Re-open only if an evidence-backed long-running project-memory failure remains.

### 6. Anthropic frontend-design — ALMAYALIM as parallel skill

Current Builder audit already classifies Anthropic Frontend Design as:

`ALREADY_STRONGER / ADAPT creative-leap contract`

Existing ENGÜRÜ Aesthetic architecture already includes:

- research/art direction;
- three distinct directions;
- Artist / Professor authority separation;
- Design DNA;
- Signature Move / creative leap;
- VX1 browser verification;
- Human Visual Authority.

Keep upstream as a benchmark/reference only.

## Implementation lanes

### Quality & Red Team

- [ ] history-aware PR review;
- [ ] confidence/evidence filtering;
- [ ] diff-aware browser QA;
- [ ] post-deploy canary;
- [ ] performance regression benchmark.

### Security & Authority

- [ ] semantic security diff review;
- [ ] OWASP/STRIDE threat-model contract;
- [ ] trusted-source / prompt-injection preflight;
- [ ] fail-closed security finding evidence.

### Shared AI Infrastructure™

- [ ] bounded second-model outside voice;
- [ ] disagreement result = evidence for review, never automatic authority;
- [ ] cost/privacy/capability gates before second-model routing.

### Verified production discipline

- [ ] runtime careful/freeze/guard contract;
- [ ] systematic debugging contract;
- [ ] isolated worktree contract;
- [ ] skill/agent TDD pressure-test pattern.

### Memory / Context

- [ ] measure whether v0.3 context fails on real long-running projects;
- [ ] only if gap is proven, add progressive verified-memory retrieval;
- [ ] never allow stale memory to override current explicit instruction.

## DoneCheck input

PASS requires:

1. selected mechanisms mapped to existing owners;
2. no duplicate framework authority;
3. provenance/license recorded;
4. deterministic tests or reproducible evidence;
5. fail-closed behavior on uncertainty;
6. Human Threshold retained for consequential actions.

Until implementation evidence exists:

**JUDGMENT — HOLD**
