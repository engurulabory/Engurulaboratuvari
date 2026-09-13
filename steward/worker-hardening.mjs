import { governanceEnvelope } from './governance-envelope.mjs';

export const STEWARD_ASSESSOR_VERSION = '1.1.0';
export const DEFAULT_EVIDENCE_TTL_HOURS = 36;

const hasText = (value) => typeof value === 'string' && value.trim().length > 0;
const normalizeStatus = (status) => ['PASS','HOLD','BLOCKED'].includes(status) ? status : 'HOLD';

export function assessRepositoryBaseline({
  repository,
  assetType,
  readmePresent=false,
  manifestPresent=false,
  ciState='HOLD',
  testState='HOLD',
  evidenceState='HOLD',
  canonicalOwner,
  canonicalRole,
} = {}) {
  const findings = [];
  if (!hasText(repository)) findings.push({ code:'REPOSITORY_ID_MISSING', level:'BLOCKED' });
  if (!hasText(canonicalOwner)) findings.push({ code:'CANONICAL_OWNER_MISSING', level:'HOLD' });
  if (!hasText(canonicalRole)) findings.push({ code:'CANONICAL_ROLE_MISSING', level:'HOLD' });
  if (!readmePresent) findings.push({ code:'README_MISSING', level:'HOLD' });
  const manifestRequired = !['EXPERIMENT_EVIDENCE_RECORD','ARCHIVE','RELEASE_MIRROR'].includes(assetType);
  if (manifestRequired && !manifestPresent) findings.push({ code:'ENGURU_MANIFEST_MISSING', level:'HOLD' });
  for (const [code, state] of [['CI',ciState],['TEST',testState],['EVIDENCE',evidenceState]]) {
    const normalized = normalizeStatus(state);
    if (normalized !== 'PASS') findings.push({ code:`${code}_${normalized}`, level:normalized });
  }
  const state = findings.some((x)=>x.level==='BLOCKED') ? 'BLOCKED' : findings.length ? 'HOLD' : 'PASS';
  return { repository, assetType, state, findings, manifestRequired };
}

export function assessEvidenceFreshness({ records=[], nowEpochMs=Date.now(), ttlHours=DEFAULT_EVIDENCE_TTL_HOURS } = {}) {
  const ttlMs = ttlHours * 60 * 60 * 1000;
  const assessed = records.map((record)=>{
    const observed = Date.parse(record.observedAt || '');
    const validObservedAt = Number.isFinite(observed);
    const ageMs = validObservedAt ? Math.max(0, nowEpochMs - observed) : null;
    const stale = !validObservedAt || ageMs > ttlMs;
    return { ...record, stale, ageHours: ageMs === null ? null : Math.round((ageMs / 3600000) * 10) / 10 };
  });
  const stale = assessed.filter((x)=>x.stale);
  return governanceEnvelope({
    state: stale.length ? 'HOLD' : 'PASS',
    claim: 'Steward evaluated evidence freshness against the declared TTL.',
    evidence: [{ ttlHours, total:assessed.length, staleCount:stale.length, records:assessed }],
    nextAction: stale.length ? 'Refresh only stale evidence before relying on it for a consequential PASS.' : 'Preserve current evidence and continue daily Steward care.'
  });
}

export function buildDependencyProvenanceGraph({ nodes=[], edges=[] } = {}) {
  const ids = new Set(nodes.map((n)=>n.id).filter(Boolean));
  const invalidEdges = edges.filter((e)=>!ids.has(e.from) || !ids.has(e.to));
  const duplicateCanonicalOwners = [];
  const byCanonical = new Map();
  for (const node of nodes) {
    if (!node.canonicalCapability) continue;
    const list = byCanonical.get(node.canonicalCapability) || [];
    list.push(node.id);
    byCanonical.set(node.canonicalCapability, list);
  }
  for (const [capability, owners] of byCanonical.entries()) {
    if (owners.length > 1) duplicateCanonicalOwners.push({ capability, owners });
  }
  const staleProvenance = edges.filter((e)=>e.kind==='PROVENANCE' && e.sourceSha && e.currentSourceSha && e.sourceSha!==e.currentSourceSha);
  const state = invalidEdges.length || duplicateCanonicalOwners.length || staleProvenance.length ? 'HOLD' : 'PASS';
  return {
    state,
    nodes,
    edges,
    findings: {
      invalidEdges,
      duplicateCanonicalOwners,
      staleProvenance
    }
  };
}

export function verifyRepairLoop({ finding, repair, verification, evidence } = {}) {
  if (!finding) return { state:'BLOCKED', reason:'FINDING_REQUIRED' };
  if (!repair) return { state:'HOLD', reason:'REPAIR_NOT_APPLIED' };
  if (!verification) return { state:'HOLD', reason:'REVERIFY_REQUIRED' };
  if (!evidence) return { state:'HOLD', reason:'EVIDENCE_REQUIRED' };
  if (verification.state !== 'PASS') return { state:'HOLD', reason:'REVERIFY_NOT_PASS', verification };
  return { state:'PASS', finding, repair, verification, evidence };
}

export function assessSelfHealth({
  schedulerState='HOLD',
  discoveryState='HOLD',
  assessorState='HOLD',
  writeBoundaryState='PASS',
  lastSuccessfulRunAt,
  nowEpochMs=Date.now(),
  maxRunAgeHours=30,
} = {}) {
  const components = { schedulerState, discoveryState, assessorState, writeBoundaryState };
  const nonPass = Object.entries(components).filter(([,state])=>state!=='PASS');
  const lastRun = Date.parse(lastSuccessfulRunAt || '');
  const runFresh = Number.isFinite(lastRun) && (nowEpochMs - lastRun) <= maxRunAgeHours * 3600000;
  if (!runFresh) nonPass.push(['lastSuccessfulRunAt','STALE_OR_MISSING']);
  return {
    state: nonPass.some(([,state])=>state==='BLOCKED') ? 'BLOCKED' : nonPass.length ? 'HOLD' : 'PASS',
    components,
    runFresh,
    nonPass
  };
}

export function buildDailyScorecard({
  workerHealth,
  portfolioAssessments=[],
  repairsApplied=0,
  humanThreshold=0,
  generatedAt,
} = {}) {
  const states = portfolioAssessments.map((x)=>x.state);
  const blocked = states.filter((x)=>x==='BLOCKED').length;
  const hold = states.filter((x)=>x==='HOLD').length;
  const pass = states.filter((x)=>x==='PASS').length;
  const total = states.length;
  const portfolioHealthScore = total ? Math.round(((pass + hold * 0.5) / total) * 100) : 0;
  const workerHealthScore = workerHealth?.state === 'PASS' ? 100 : workerHealth?.state === 'HOLD' ? 85 : 60;
  return {
    schemaVersion:'1.1',
    generatedAt: generatedAt || new Date().toISOString(),
    workerHealthScore,
    portfolioHealthScore,
    scannedRepositories: total,
    repairsApplied,
    pass,
    hold,
    blocked,
    humanThreshold,
    state: blocked ? 'BLOCKED' : hold || workerHealth?.state!=='PASS' ? 'HOLD' : 'PASS'
  };
}
