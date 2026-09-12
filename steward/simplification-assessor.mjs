import { governanceEnvelope } from './governance-envelope.mjs';

export function assessSimplification({ candidates = [], protectedReferences = [] } = {}) {
  const protectedSet = new Set(protectedReferences);
  const protectedItems = candidates.filter((item) => protectedSet.has(item.id));
  const reviewableItems = candidates.filter((item) => !protectedSet.has(item.id));
  const beforeCount = candidates.length;
  const projectedAfterCount = protectedItems.length;
  const state = reviewableItems.length === 0 ? 'PASS' : 'HOLD';

  return governanceEnvelope({
    state,
    claim: 'Steward measured simplification opportunities while preserving protected references.',
    evidence: [{ beforeCount, projectedAfterCount, protectedCount: protectedItems.length, reviewableCount: reviewableItems.length, protectedItems, reviewableItems }],
    nextAction: state === 'PASS'
      ? 'Preserve the current simplified state and continue scheduled Steward care.'
      : 'Classify each reviewable item through the existing SAFE_AUTO, REVIEW, or HUMAN_THRESHOLD authority class before any structural change.'
  });
}
