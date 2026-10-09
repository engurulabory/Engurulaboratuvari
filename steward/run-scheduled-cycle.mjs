import { execFileSync } from 'node:child_process';
import { readFileSync, statSync } from 'node:fs';
import {
  inspectWorkspaceHealth, STEWARD_SCOPES, STEWARD_VERSION,
  assessEvidenceFreshness, buildDailyScorecard, assessSelfHealth
} from './index.mjs';

const SCOPES = Object.values(STEWARD_SCOPES);
const aggregate = (states) => states.includes('BLOCKED') ? 'BLOCKED'
  : states.includes('HOLD') ? 'HOLD' : 'PASS';

export function classifyTrackedFile(path) {
  if (path.startsWith('governance/') || path.startsWith('.github/') ||
      path.startsWith('security/') || path.startsWith('evidence/')) return STEWARD_SCOPES.LABORY;
  if (path.startsWith('steward/') || path.startsWith('tools/') ||
      path.startsWith('core/') || path.startsWith('packages/')) return STEWARD_SCOPES.CORE;
  if (path.startsWith('site/') || path.startsWith('app/') ||
      path.startsWith('product/') || path.startsWith('products/')) return STEWARD_SCOPES.PRODUCT;
  return STEWARD_SCOPES.LABORY;
}

export function inspectTrackedScopes({ files=[], contents=[], nowEpochMs=Date.now(),
  observedAt=new Date(nowEpochMs).toISOString(), sourceCommit=null,
  eventName=null, runId=null } = {}) {
  const scoped = SCOPES.map((scope) => {
    const subset = files.filter(p=>classifyTrackedFile(p)===scope);
    const matching = contents.filter(x=>classifyTrackedFile(x.path || '')===scope);
    const inspection = inspectWorkspaceHealth({scope,files:subset,contents:matching,workItems:[]});
    // An empty scope is incomplete source coverage, never a healthy scan.
    const state = subset.length ? inspection.status : 'HOLD';
    return {scope,state,trackedFileCount:subset.length,
      findings:inspection.repository?.findings || [],
      coverage:subset.length ? 'OBSERVED' : 'MISSING'};
  });
  const genuineScheduledRun = eventName === 'schedule' && /^[0-9]+$/.test(String(runId || '')) && !!sourceCommit;
  // Event provenance is a native GitHub Actions context; PR fixtures stay observational.
  const freshness = assessEvidenceFreshness({records:[{id:'CURRENT_RUN',observedAt}],nowEpochMs});
  const evidenceState = sourceCommit ? freshness.state : 'HOLD';
  const health = assessSelfHealth({
    schedulerState:genuineScheduledRun?'PASS':'HOLD',
    discoveryState:scoped.every(x=>x.coverage==='OBSERVED')?'PASS':'HOLD',
    assessorState:aggregate(scoped.map(x=>x.state)),
    writeBoundaryState:'PASS',
    lastSuccessfulRunAt:genuineScheduledRun?observedAt:undefined,nowEpochMs
  });
  const scorecard = buildDailyScorecard({
    workerHealth:health,
    portfolioAssessments:scoped.map(x=>({state:x.state})),
    repairsApplied:0,humanThreshold:0,generatedAt:observedAt
  });
  return {
    schemaVersion:'1.2',stewardVersion:STEWARD_VERSION,
    mode:'READ_ONLY_SCHEDULED_CYCLE',sourceCommit,observedAt,
    runEvent:{eventName,runId,genuineScheduledRun},
    authority:'INSPECT_AND_PLAN',writeBoundary:'PRESERVED',
    scopeCoverage:scoped,trackedFileCount:files.length,
    evidenceFreshness:evidenceState,workerHealth:health,
    scorecard,
    state:aggregate([...scoped.map(x=>x.state),evidenceState,health.state]),
    verifiedFinish:'HOLD',
    nextAction:'VERIFY_REAL_SCHEDULED_RUN_AND_SCOPED_STEWARD_ACCEPTANCE'
  };
}

function trackedFiles() {
  return execFileSync('git',['ls-files','-z'],{encoding:'utf8'}).split('\0').filter(Boolean);
}
function textContents(files) {
  const out=[];
  for(const path of files) {
    try {
      const stat=statSync(path);
      if(!stat.isFile() || stat.size>1000000) continue;
      out.push({path,content:readFileSync(path,'utf8')});
    } catch { /* excluded files remain represented in tracked file counts */ }
  }
  return out;
}
if (process.argv[1] && import.meta.url === new URL('file://' + process.argv[1]).href) {
  const files=trackedFiles();
  const sourceCommit=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim();
  const receipt=inspectTrackedScopes({files,contents:textContents(files),sourceCommit,
    eventName:process.env.GITHUB_EVENT_NAME || null,
    runId:process.env.GITHUB_RUN_ID || null});
  console.log(JSON.stringify(receipt,null,2));
  if(receipt.state==='BLOCKED') process.exitCode=3;
  else if(receipt.state==='HOLD' && process.env.ENGURU_STEWARD_STRICT_FIELD==='1') process.exitCode=2;
}
