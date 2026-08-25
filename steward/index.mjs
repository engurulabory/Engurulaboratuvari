export const STEWARD_VERSION = '1.0.0';
export const STEWARD_SCOPES = Object.freeze({ LABORY: 'ENGURU_LABORY', PRODUCT: 'ENGURU_PRODUCT' });
export const STEWARD_CYCLE = Object.freeze(['YOKLAMA','TERTIP','DUZEN','TEMIZLIK','SADELESTIRME','BAKIM','ONARIM','KAPANIS','YENIDEN_HAZIR']);

const JUNK_PATTERNS = [/(^|\/)\.DS_Store$/,/(^|\/)Thumbs\.db$/,/(^|\/).*\.tmp$/,/(^|\/).*\.swp$/,/(^|\/)npm-debug\.log$/];
const PROTECTED_PATH = /^(?:evidence|\.github\/workflows|security|governance)\//;
const isJunk = (file = '') => JUNK_PATTERNS.some((pattern) => pattern.test(file));

export function classifyWorkItem({ active=false, mergeReady=false, dependencyOpen=false, superseded=false, protectedReference=false } = {}) {
  if (protectedReference) return 'PROTECTED_REFERENCE';
  if (active) return 'ACTIVE';
  if (mergeReady) return 'MERGE_CANDIDATE';
  if (dependencyOpen) return 'HOLD';
  if (superseded) return 'OBSOLETE_SUPERSEDED';
  return 'HOLD';
}

export function inspectRepositoryOrder({ files=[], contents=[] } = {}) {
  const findings = [];
  for (const file of files) if (isJunk(file)) findings.push({ level:'HOLD', code:'OBVIOUS_JUNK', file });
  for (const item of contents) {
    if (typeof item?.content === 'string' && /^(<<<<<<<|=======|>>>>>>>)/m.test(item.content)) {
      findings.push({ level:'BLOCKED', code:'MERGE_CONFLICT_MARKER', file:item.path || 'unknown' });
    }
  }
  return { status: findings.some((x)=>x.level==='BLOCKED') ? 'BLOCKED' : findings.length ? 'HOLD' : 'PASS', findings };
}

export function inspectWorkspaceHealth({ scope=STEWARD_SCOPES.PRODUCT, files=[], contents=[], workItems=[] } = {}) {
  const repository = inspectRepositoryOrder({ files, contents });
  const classified = workItems.map((item)=>({ ...item, stewardState: classifyWorkItem(item) }));
  const unresolved = classified.filter((item)=>['HOLD','OBSOLETE_SUPERSEDED'].includes(item.stewardState));
  return {
    scope,
    cycle: STEWARD_CYCLE,
    status: repository.status === 'BLOCKED' ? 'BLOCKED' : repository.status === 'HOLD' || unresolved.length ? 'HOLD' : 'PASS',
    repository,
    workItems: classified,
    order: { status: repository.status },
    organization: { status: unresolved.length ? 'HOLD' : 'PASS', unresolved: unresolved.length },
    hygiene: { status: repository.findings.some((x)=>x.code==='OBVIOUS_JUNK') ? 'HOLD' : 'PASS' },
  };
}

export function planSafeMaintenance({ findings=[], mergedBranches=[], staleWorkflows=[] } = {}) {
  const safeActions=[]; const humanThreshold=[]; const blocked=[];
  for (const finding of findings) {
    if (finding.code === 'OBVIOUS_JUNK' && isJunk(finding.file) && !PROTECTED_PATH.test(finding.file)) safeActions.push({ action:'DELETE_OBVIOUS_JUNK', target:finding.file });
    else if (finding.level === 'BLOCKED') blocked.push(finding);
    else humanThreshold.push({ action:'REVIEW_FINDING', target:finding.file || finding.code });
  }
  for (const branch of mergedBranches) if (branch && branch !== 'main') humanThreshold.push({ action:'DELETE_BRANCH', target:branch });
  for (const workflow of staleWorkflows) if (workflow) humanThreshold.push({ action:'DELETE_WORKFLOW', target:workflow });
  return { status: blocked.length ? 'BLOCKED' : humanThreshold.length ? 'HOLD' : 'PASS', safeActions, humanThreshold, blocked };
}

export function closeoutRepository({ clean=true, maintenanceVerified=true, evidencePreserved=true, protectedRefsUntouched=true, orderVerified=true, organizationVerified=true, hygieneVerified=true, mapPass=false } = {}) {
  if (!evidencePreserved) return { status:'BLOCKED', reason:'EVIDENCE_AT_RISK' };
  if (!protectedRefsUntouched) return { status:'BLOCKED', reason:'PROTECTED_REFERENCE_CHANGED' };
  if (!mapPass) return { status:'HOLD', reason:'PRODUCT_CORE_MAP_PASS_REQUIRED' };
  if (!orderVerified) return { status:'HOLD', reason:'ORDER_VERIFICATION_REQUIRED' };
  if (!organizationVerified) return { status:'HOLD', reason:'ORGANIZATION_VERIFICATION_REQUIRED' };
  if (!hygieneVerified) return { status:'HOLD', reason:'HYGIENE_VERIFICATION_REQUIRED' };
  if (!clean || !maintenanceVerified) return { status:'HOLD', reason: !clean ? 'REPOSITORY_NOT_CLEAN' : 'MAINTENANCE_NOT_VERIFIED' };
  return { status:'READY_AGAIN', cycle:STEWARD_CYCLE };
}
