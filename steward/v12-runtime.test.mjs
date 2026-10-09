import assert from 'node:assert/strict';
import { inspectTrackedScopes, classifyTrackedFile } from './run-scheduled-cycle.mjs';
import { STEWARD_SCOPES, STEWARD_VERSION } from './index.mjs';

assert.equal(STEWARD_VERSION,'1.2.0');
assert.equal(classifyTrackedFile('governance/truth.json'), STEWARD_SCOPES.LABORY);
assert.equal(classifyTrackedFile('steward/index.mjs'), STEWARD_SCOPES.CORE);
assert.equal(classifyTrackedFile('site/product-registry.json'), STEWARD_SCOPES.PRODUCT);
const files=['governance/truth.json','steward/index.mjs','site/product-registry.json'];
const contents=files.map(path=>({path,content:'intact source'}));
const base={files,contents,nowEpochMs:Date.parse('2026-10-09T06:00:00Z'),
  observedAt:'2026-10-09T06:00:00Z',sourceCommit:'a'.repeat(40)};
const r=inspectTrackedScopes(base);
assert.equal(r.scopeCoverage.length,3);
assert.deepEqual(r.scopeCoverage.map(x=>x.state),['PASS','PASS','PASS']);
assert.equal(r.state,'HOLD'); // Real scheduled continuity still unverified.
assert.equal(r.workerHealth.state,'HOLD');
assert.equal(r.verifiedFinish,'HOLD');
assert.equal(r.scorecard.state,'HOLD');
assert.equal(r.scorecard.portfolioHealthScore,100);
assert.equal(inspectTrackedScopes({...base,files:files.slice(0,2),
 contents:contents.slice(0,2)}).scopeCoverage[1].state,'HOLD');
const conflict=inspectTrackedScopes({...base,contents:[
 ...contents,{path:'steward/conflict.mjs',content:'<<<<<<< HEAD\n=======\n>>>>>>> branch'}]});
assert.equal(conflict.state,'BLOCKED');
assert.equal(inspectTrackedScopes({...base,sourceCommit:null}).evidenceFreshness,'HOLD');
console.log('STEWARD_V12_RUNTIME_SAFETY_TESTS=PASS');
