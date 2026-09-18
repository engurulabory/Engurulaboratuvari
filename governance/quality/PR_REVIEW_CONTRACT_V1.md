# ENGÜRÜ Quality & Red Team — History-Aware PR Review Contract

State: IMPLEMENTED CANDIDATE — exact-head CI required.

This extends the existing Quality & Red Team. It does not create a new core or review authority.

## Flow

`PR DIFF → HISTORY/BLAME CONTEXT → FINDINGS → EVIDENCE + CONFIDENCE FILTER → OUTSIDE VOICE WHEN REQUIRED → VERDICT → DoneCheck™`

## Rules

1. A finding without evidence is suppressed.
2. A finding below the configured confidence threshold is suppressed.
3. Regression, behavior-change and authority-change findings require history context.
4. Duplicate findings collapse to the strongest supported instance.
5. High/Critical accepted findings produce HOLD until resolved.
6. Outside Voice is independent only when reviewer identity differs from producer identity.
7. Outside Voice disagreement produces HOLD; it never self-decides the change.
8. Outside Voice requires evidence and remains subject to cost, privacy, capability and Human Threshold routing before any real provider call.
9. Exact diff/history evidence is preferred over prose recollection.
10. ENGÜRÜ Language Governance™, DoneCheck™ and Human Threshold™ remain canonical.

## External mechanism provenance

Mechanisms were informed by public patterns observed in Anthropic Claude Code code-review and gstack. No upstream framework becomes canonical authority; restricted implementation is not copied as ENGÜRÜ source.

## Acceptance

- deterministic confidence filtering;
- evidence-free noise suppression;
- history-sensitive regression handling;
- duplicate suppression;
- independent-identity outside voice;
- disagreement → HOLD;
- CI regression coverage.
