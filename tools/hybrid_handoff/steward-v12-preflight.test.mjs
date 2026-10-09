import assert from 'node:assert/strict';
import { assess, baseline } from './steward-v12-preflight.mjs';
const s=baseline(), r=assess(s);
assert.equal(r.rows.length,10);
assert.equal(r.state,'HOLD');
assert.equal(r.judgment,'VERIFIED_FINISH_HOLD');
assert.equal(s.source,'1.2.0');
assert.equal(s.schedule,'17 5 * * *');
assert.deepEqual(r.rows.filter(x=>x.state==='PASS_PREFLIGHT').map(x=>x.id),['S05','S07','S08']);
const full={...s,source:'1.1.0',versionTarget:'1.2.0',behaviorValidated:true,
 probedScopes:s.scopes,schedule:'17 5 * * *',realScheduledReceipt:true,cronPermissionsReadOnly:true,
 reverifyReceipt:true,repairPolicyApproved:true,osiRuntimeReceipt:true,exactParity:true,
 humanScope:true,finalizer:true,nativeProgressReread:true};
assert.equal(assess(full).state,'READY_FOR_FINAL_EXECUTION');
for(const [key,value] of Object.entries({preserved:false,behaviorValidated:false,realScheduledReceipt:false,
 repairPolicyApproved:false,reverifyReceipt:false,osiRuntimeReceipt:false,
 humanScope:false,finalizer:false,nativeProgressReread:false,gatesHonest:false,
 exactParity:false,priorReceipts:0,originalScopesRetained:false})){
  assert.equal(assess({...full,[key]:value}).state,'HOLD',key);
}
assert.equal(assess({...full,probedScopes:['ENGURU_LABORY']}).state,'HOLD');
assert.equal(assess({...full,schedule:'23 6 */3 * *'}).state,'HOLD');
assert.equal(assess({...full,freshness:false}).state,'HOLD');
assert.equal(assess({...full,provenance:false}).state,'HOLD');
assert.equal(assess({...full,selfHealth:false}).state,'HOLD');
assert.equal(assess({...full,scorecard:false}).state,'HOLD');
console.log('STEWARD_V12_PREFLIGHT_ADVERSARIAL=PASS; BASELINE=HOLD; FULL_FIXTURE=READY');
