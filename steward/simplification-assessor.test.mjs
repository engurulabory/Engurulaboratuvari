import assert from 'node:assert/strict';
import { assessSimplification } from './simplification-assessor.mjs';

const hold = assessSimplification({
  candidates:[{id:'duplicate-a'},{id:'protected-a'}],
  protectedReferences:['protected-a']
});
assert.equal(hold.state,'HOLD');
assert.equal(hold.evidence[0].beforeCount,2);
assert.equal(hold.evidence[0].projectedAfterCount,1);
assert.equal(hold.evidence[0].protectedCount,1);
assert.equal(hold.evidence[0].reviewableCount,1);

const pass = assessSimplification({
  candidates:[{id:'protected-a'}],
  protectedReferences:['protected-a']
});
assert.equal(pass.state,'PASS');
assert.equal(pass.evidence[0].reviewableCount,0);
console.log('steward-simplification-assessor: PASS');
