export function governanceEnvelope({ state, claim, evidence = [], nextAction } = {}) {
  const validStates = new Set(['PASS', 'HOLD', 'BLOCKED', 'READY_AGAIN']);
  if (!validStates.has(state)) throw new Error('INVALID_GOVERNANCE_STATE');
  if (typeof claim !== 'string' || !claim.trim()) throw new Error('CLAIM_REQUIRED');
  if (!Array.isArray(evidence) || evidence.length === 0) throw new Error('EVIDENCE_REQUIRED');
  if (typeof nextAction !== 'string' || !nextAction.trim()) throw new Error('NEXT_ACTION_REQUIRED');
  return Object.freeze({ state, claim: claim.trim(), evidence, nextAction: nextAction.trim() });
}
