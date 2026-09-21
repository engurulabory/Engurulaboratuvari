# ENGÜRÜ Mac Engineer™ v0.6 — Persistent Working Memory v0.1

## STATE

IMPLEMENTED CANDIDATE — exact-head tests, regression, Evidence and Mandatory DoneCheck™ required.

## NIYET

Preserve one durable engineering-task truth across interruption, restart and later resume without creating a parallel memory daemon, authority system or agent framework.

Package 3 extends the existing **Task State + Evidence + Verified Learning** layers.

## Canonical placement

`Task Contract → Task State → Persistent Working Memory → Evidence → DoneCheck™ → Human Threshold™ → Verified Finish → Governed Learning Promotion`

This layer stores state. It does not manufacture authority or PASS.

## Durable Task Record

Every real task record binds:

- one immutable `task_id`;
- objective;
- authority snapshot;
- required capabilities;
- monotonic revision;
- state transitions;
- artifact references;
- evidence references;
- Human decisions with authority + evidence;
- one current resume checkpoint;
- final outcome.

Persistence is caller-owned file storage. The implementation does not introduce a service or daemon.

### Continuity rules

1. Writes are atomic: temporary file → fsync → replace.
2. Every mutation supplies `expected_revision`.
3. A stale revision cannot overwrite newer truth.
4. Resume requires the exact checkpoint identity.
5. A task already closed with Verified Finish / PASS cannot silently resume as active work.
6. PASS final outcome requires evidence.
7. Runtime path remains outside canonical repository truth unless an evidence artifact is intentionally committed.

## Governed Learning Promotion

Canonical chain:

`OBSERVED → LEARNING_CANDIDATE → EVIDENCE → FRESH_REVIEW → ACCEPT / REJECT → VERSIONED PROMOTION`

Rules:

- one observation remains `OBSERVED`;
- repeated observation is required before candidacy;
- evidence + benchmark are required before review;
- fresh review uses a different reviewer identity from the producer;
- ACCEPT preserves existing EvidenceGatedSkillLearning + Human Threshold behavior;
- REJECT cannot be promoted;
- promotion records an explicit version and target;
- promotion does not expand authority;
- accepted learning is recoverable as a versioned record rather than silently rewriting canonical policy.

## Truth boundary

Persistent memory is not “the model remembers everything.”

It is a bounded engineering record that preserves verified task state, evidence and governed learning across runtime interruption.

User/profile memory, private conversation memory and product-domain databases are outside this Package 3 contract.

## Acceptance

Package 3 may PASS only when:

1. task identity survives store restart;
2. stale writes fail closed;
3. checkpoint/resume survives restart;
4. Human decision + evidence binding is verified;
5. evidence-less PASS is rejected;
6. completed PASS cannot silently resume;
7. one observation cannot self-promote;
8. independent review is enforced;
9. Human Threshold is required for learning ACCEPT;
10. accepted learning is versioned and persists;
11. rejected learning cannot be promoted;
12. exact-head Labory regression is green;
13. Evidence is recorded;
14. Mandatory DoneCheck™ passes.

## NEXT ACTION

Run Package 3 unit tests and full Labory exact-head regression. If green, record Evidence, update the canonical WORKLIST, run Mandatory DoneCheck™, then move to Package 4.
