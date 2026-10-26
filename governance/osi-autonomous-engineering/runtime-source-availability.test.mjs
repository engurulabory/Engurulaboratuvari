import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const snap=JSON.parse(readFileSync(new URL('./pilot-fabric-source-snapshot.json',import.meta.url),'utf8'));
const contract=readFileSync(new URL('./OSI_AUTONOMOUS_ENGINEERING_CONTRACT_V01.md',import.meta.url),'utf8');
const roles=snap.profiles;
const outcomes=[];
function gate(name,fn){fn();outcomes.push({name,state:'PASS'});console.log(name+'=PASS');}
gate('R01_PINNED_PROFILE_PROVENANCE',()=>{assert.equal(snap.sourceBlobSha,'bba5d31d33b25bce9aba22758303fc629f00dba8');assert.equal(roles.length,7);});
gate('R02_NO_EXECUTOR_SUBSTITUTION',()=>{assert.equal(snap.scope,'REFERENCE_ONLY_NOT_RUNTIME_EVIDENCE');for(const p of roles)assert.equal(p.binding,'HOLD_PENDING_HANDLER_RESOLUTION');});
gate('R03_CONVERSATION_MUST_HOLD_WITHOUT_HANDLER',()=>{function dispatch(pilotId,requestedCapability,handler){const p=roles.find(x=>x.id===pilotId);if(!p||!p.capabilityIds.includes(requestedCapability)||p.binding!=='FIELD_VERIFIED'||typeof handler!=='function')return {state:'HOLD',executed:false,reason:'HANDLER_OR_AUTHORITY_UNVERIFIED'};return {state:'READY_FOR_BOUNDED_EXECUTION',executed:false};}for(const p of roles){const capability=p.capabilityIds[0];assert.deepEqual(dispatch(p.id,capability,null),{state:'HOLD',executed:false,reason:'HANDLER_OR_AUTHORITY_UNVERIFIED'});}assert.equal(dispatch('ZEKU','DELETE_USER_FILES',null).state,'HOLD');assert.equal(dispatch('UNKNOWN','BUILD',null).state,'HOLD');});
gate('R04_NATIVE_FIELD_NOT_SUBSTITUTED',()=>{assert.match(contract,/P06.*OSi/);assert.match(contract,/fieldProof.completed=0\/7/);assert.match(contract,/VERIFIED_FINISH_HOLD/);});
const receipt={schema:'enguru.osi.p05.runtime-availability-gate/v1',state:'HOLD',sourceAuthority:'OSI_LOCAL',remoteExecutorSource:'UNAVAILABLE_IN_CHECKED_GITHUB_REFS',sourceFixtureVerified:true,profileCount:roles.length,executablePilotHandlersVerified:0,realRuntimeImported:false,realE2EExecuted:false,guardTests:outcomes,verifiedFinish:'HOLD',nextAction:'P06_OSI_LOCAL_RUNTIME_HARVEST_AND_ISOLATED_EXECUTION'};
console.log('RUNTIME_AVAILABILITY_RECEIPT='+JSON.stringify(receipt));
assert.equal(receipt.state,'HOLD');
