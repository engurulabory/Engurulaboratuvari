import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {planSafeMaintenance,closeoutRepository} from '../../steward/index.mjs';
const fixture=JSON.parse(readFileSync(new URL('./pilot-fabric-source-snapshot.json',import.meta.url),'utf8'));
let pass=0;
function gate(id,fn){fn();console.log(id+'=PASS');pass++;}
const ids=['ZEKU','ATLAS','FORGE','ASTRA','NEURON','SENTINEL','FORMA'];
gate('H01_SEVEN_CANONICAL_PROFILES',()=>{assert.deepEqual(fixture.profiles.map(p=>p.id),ids);assert.equal(fixture.sourceBlobSha,'bba5d31d33b25bce9aba22758303fc629f00dba8');assert.equal(fixture.scope,'REFERENCE_ONLY_NOT_RUNTIME_EVIDENCE');});
gate('H02_ZERO_INVENTED_HANDLER_AUTHORITY',()=>{for(const p of fixture.profiles){assert.equal(p.binding,'HOLD_PENDING_HANDLER_RESOLUTION');assert.equal(p.evidenceRequired,true);assert.equal(p.authority,'INHERIT_CURRENT_CAPABILITY_AND_ACTION_AUTHORITY');}});
gate('H03_INTENT_ROUTE_FAIL_CLOSED',()=>{const selection=(id,cap)=>{const p=fixture.profiles.find(x=>x.id===id);return (!p||!p.capabilityIds.includes(cap)||p.binding!=='FIELD_VERIFIED')?{state:'HOLD',executed:false}:{state:'READY',executed:false};};assert.deepEqual(selection('ZEKU','OPERATOR_CONTINUE_DISPATCH'),{state:'HOLD',executed:false});assert.equal(selection('FORGE','ROOT_CAUSE_REPAIR').state,'HOLD');assert.equal(selection('ASTRA','DELETE_FILES').state,'HOLD');assert.equal(selection('UNKNOWN','BUILD').state,'HOLD');});
gate('H04_SEVEN_CAPABILITY_SPECS',()=>{const map=Object.fromEntries(fixture.profiles.map(x=>[x.id,x.capabilityIds]));assert.ok(map.ZEKU.includes('OPERATOR_CONTINUE_DISPATCH'));assert.ok(map.ATLAS.includes('ADVANCED_CODE_ENGINEERING'));assert.ok(map.FORGE.includes('ROOT_CAUSE_REPAIR'));assert.ok(map.ASTRA.includes('INTERNET_RESEARCH_HARVEST_ASTRA'));assert.ok(map.NEURON.includes('ADVANCED_CODE_ENGINEERING'));assert.ok(map.SENTINEL.includes('TEST_REGRESSION'));assert.ok(map.FORMA.includes('SOURCE_PRODUCT_CHANGE'));});
gate('H05_STEWARD_HUMAN_APPROVAL',()=>{let r=planSafeMaintenance({mergedBranches:['protected-branch'],staleWorkflows:['old.yml']});assert.equal(r.safeActions.length,0);assert.equal(r.humanThreshold.length,2);});
gate('H06_STEWARD_PROTECTED_EVIDENCE',()=>{const r=planSafeMaintenance({findings:[{code:'OBVIOUS_JUNK',file:'evidence/field.tmp'},{code:'OBVIOUS_JUNK',file:'sandbox/cache.tmp'}]});assert.deepEqual(r.safeActions.map(x=>x.target),['sandbox/cache.tmp']);assert.equal(r.humanThreshold.length,1);});
gate('H07_CLOSEOUT_HOLD_BOUNDARIES',()=>{assert.equal(closeoutRepository({mapPass:false}).status,'HOLD');assert.equal(closeoutRepository({evidencePreserved:false,mapPass:true}).status,'BLOCKED');});
assert.equal(pass,7);
console.log(JSON.stringify({state:'PASS_SCOPED',passed:pass,total:7,source:'EXACT_EXTERNAL_PILOT_PROFILE_FIXTURE_AND_REAL_STEWARD_METHODS',handlerExecution:'NOT_EXECUTED',fullE2E:'HOLD',verifiedFinish:'HOLD'}));
