import assert from 'node:assert/strict';
import {
  STEWARD_VERSION, STEWARD_CYCLE, STEWARD_SCOPES, classifyWorkItem, inspectRepositoryOrder,
  inspectWorkspaceHealth, planSafeMaintenance, closeoutRepository,
  assessRepositoryBaseline, assessEvidenceFreshness, buildDependencyProvenanceGraph,
  verifyRepairLoop, assessSelfHealth, buildDailyScorecard
} from './index.mjs';
import { governanceEnvelope } from './governance-envelope.mjs';
import { assessSimplification } from './simplification-assessor.mjs';

assert.equal(STEWARD_VERSION, '1.1.0');
assert.deepEqual(STEWARD_CYCLE, ['YOKLAMA','TERTIP','DUZEN','TEMIZLIK','SADELESTIRME','BAKIM','ONARIM','KAPANIS','YENIDEN_HAZIR']);
assert.equal(STEWARD_SCOPES.LABORY, 'ENGURU_LABORY');
assert.equal(STEWARD_SCOPES.PRODUCT, 'ENGURU_PRODUCT');
assert.equal(STEWARD_SCOPES.CORE, 'ENGURU_CORE');
assert.equal(classifyWorkItem({ active:true }), 'ACTIVE');
assert.equal(classifyWorkItem({ mergeReady:true }), 'MERGE_CANDIDATE');
assert.equal(classifyWorkItem({ dependencyOpen:true }), 'HOLD');
assert.equal(classifyWorkItem({ protectedReference:true }), 'PROTECTED_REFERENCE');
assert.equal(inspectRepositoryOrder({ files:['README.md'] }).status, 'PASS');
const junk = inspectRepositoryOrder({ files:['tmp/cache.tmp'] });
assert.equal(junk.status, 'HOLD');
assert.equal(inspectRepositoryOrder({ contents:[{path:'x',content:'<<<<<<< HEAD\na\n=======\nb\n>>>>>>> branch'}] }).status, 'BLOCKED');
const coreHealth = inspectWorkspaceHealth({ scope:STEWARD_SCOPES.CORE, files:['README.md'], workItems:[{active:true},{protectedReference:true}] });
assert.equal(coreHealth.status, 'PASS');
assert.equal(inspectWorkspaceHealth({ scope:'INVALID' }).status, 'BLOCKED');
const maintenance = planSafeMaintenance({ findings:junk.findings });
assert.equal(maintenance.status, 'PASS');
assert.equal(maintenance.safeActions[0].action, 'DELETE_OBVIOUS_JUNK');
assert.equal(planSafeMaintenance({ mergedBranches:['feature/old'] }).status, 'HOLD');
assert.equal(closeoutRepository({ mapPass:false }).status, 'HOLD');
assert.equal(closeoutRepository({ mapPass:true }).status, 'READY_AGAIN');
assert.equal(closeoutRepository({ mapPass:true, evidencePreserved:false }).status, 'BLOCKED');

const envelope = governanceEnvelope({ state:'PASS', claim:'Steward decision is evidenced.', evidence:[{source:'unit-test'}], nextAction:'Preserve verified state.' });
assert.equal(envelope.state, 'PASS');
assert.throws(() => governanceEnvelope({ state:'PASS', claim:'x', evidence:[], nextAction:'y' }), /EVIDENCE_REQUIRED/);

const simplificationHold = assessSimplification({ candidates:[{id:'duplicate-a'},{id:'protected-a'}], protectedReferences:['protected-a'] });
assert.equal(simplificationHold.state, 'HOLD');
assert.equal(simplificationHold.evidence[0].projectedAfterCount, 1);
assert.equal(assessSimplification({ candidates:[{id:'protected-a'}], protectedReferences:['protected-a'] }).state, 'PASS');

const baselinePass = assessRepositoryBaseline({
  repository:'engurulabory/example-core', assetType:'CORE', readmePresent:true, manifestPresent:true,
  ciState:'PASS', testState:'PASS', evidenceState:'PASS', canonicalOwner:'ENGÜRÜ Labory', canonicalRole:'CORE'
});
assert.equal(baselinePass.state, 'PASS');
assert.equal(assessRepositoryBaseline({ repository:'x', assetType:'CORE', readmePresent:true, ciState:'PASS', testState:'PASS', evidenceState:'PASS', canonicalOwner:'o', canonicalRole:'CORE' }).state, 'HOLD');
assert.equal(assessRepositoryBaseline({ repository:'x', assetType:'EXPERIMENT_EVIDENCE_RECORD', readmePresent:true, ciState:'PASS', testState:'PASS', evidenceState:'PASS', canonicalOwner:'o', canonicalRole:'EXPERIMENT' }).state, 'PASS');

const now = Date.parse('2026-09-13T08:00:00Z');
const freshnessPass = assessEvidenceFreshness({ nowEpochMs:now, ttlHours:36, records:[{id:'a', observedAt:'2026-09-12T08:00:00Z'}] });
assert.equal(freshnessPass.state, 'PASS');
assert.equal(assessEvidenceFreshness({ nowEpochMs:now, ttlHours:12, records:[{id:'a', observedAt:'2026-09-12T08:00:00Z'}] }).state, 'HOLD');

const graphPass = buildDependencyProvenanceGraph({
  nodes:[{id:'source'},{id:'mirror'}],
  edges:[{from:'source',to:'mirror',kind:'PROVENANCE',sourceSha:'abc',currentSourceSha:'abc'}]
});
assert.equal(graphPass.state, 'PASS');
assert.equal(buildDependencyProvenanceGraph({
  nodes:[{id:'source'},{id:'mirror'}],
  edges:[{from:'source',to:'mirror',kind:'PROVENANCE',sourceSha:'abc',currentSourceSha:'def'}]
}).state, 'HOLD');

assert.equal(verifyRepairLoop({ finding:{id:'f'}, repair:{id:'r'}, verification:{state:'PASS'}, evidence:{id:'e'} }).state, 'PASS');
assert.equal(verifyRepairLoop({ finding:{id:'f'}, repair:{id:'r'} }).state, 'HOLD');

const workerPass = assessSelfHealth({
  schedulerState:'PASS', discoveryState:'PASS', assessorState:'PASS', writeBoundaryState:'PASS',
  lastSuccessfulRunAt:'2026-09-13T07:00:00Z', nowEpochMs:now
});
assert.equal(workerPass.state, 'PASS');
assert.equal(assessSelfHealth({ schedulerState:'BLOCKED', lastSuccessfulRunAt:'2026-09-13T07:00:00Z', nowEpochMs:now }).state, 'BLOCKED');

const score = buildDailyScorecard({
  workerHealth:workerPass,
  portfolioAssessments:[{state:'PASS'},{state:'PASS'},{state:'HOLD'}],
  repairsApplied:1,
  humanThreshold:1,
  generatedAt:'2026-09-13T08:00:00Z'
});
assert.equal(score.workerHealthScore, 100);
assert.equal(score.portfolioHealthScore, 83);
assert.equal(score.state, 'HOLD');

console.log('repository-steward: PASS');
