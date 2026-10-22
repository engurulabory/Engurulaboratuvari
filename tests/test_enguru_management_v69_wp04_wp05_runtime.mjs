import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile,writeFile,symlink,rm,mkdir,open} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
import {DisposableJournal,executeObservedPilot,replayBytes} from '../tools/enguru_management_v69_wp04_wp05_runtime.mjs';
import {auditObservedLedger,gitBlob} from '../tools/enguru_management_v69_wp02_wp03_bridge.mjs';
const sha=x=>createHash('sha256').update(x).digest('hex');
const actors={manager:'g-manager-A',executor:'g-executor-B',verifier:'g-verifier-C'};
const temps=[];
async function root(){const p=await mkdtemp(join(tmpdir(),'gh69-runtime-test-'));temps.push(p);return p;}
async function fixture(){
 let checks=[];for(let i=1;i<=100;i++){
  let b=Math.ceil(i/10),c=i%10||10,pass=i<=29 && i!==9 && i!==10;
  checks.push({id:`B${String(b).padStart(2,'0')}-${String(c).padStart(2,'0')}`,name:`Original ${i}`,
    state:pass?'PASS_EVIDENCE':'HOLD',evidence:pass?`proof-${i}`:null});
 }
 const o={schema:'enguru.100-unit-verified-finish-tracker/v1',checks,total_units:100,verified_units:27,
  remaining_units:73,official_h1_h2_h3:{passed:0,total:12},verified_finish:'HOLD'};
 const raw=Buffer.from(JSON.stringify(o));return auditObservedLedger(raw,{expectedGitBlob:gitBlob(raw)});
}
async function pilot(){let p=await root(),observed=await fixture(),result=await executeObservedPilot({observed,root:p,actorIds:actors});
 return {p,result,j:new DisposableJournal(p),observed};}
const expectHold=async(promise,code)=>assert.rejects(promise,e=>e?.code===code);
const scopes={taskId:'ENGURU-MGMT69-GH-FOUNDATION-01',repo:'engurulabory/Engurulaboratuvari',
 ledgerPrHead:'de63a9e34a9b05b6474c847019d8c682b5360d50',ledgerBlob:'d54f48ce532a23e4e4b6eff1ef5f9c7c776e71fc',controlIds:['B01-09']};
const mkEvent=(type,role,id,payload,key)=>({type,actor:{role,id},payload,idempotencyKey:key});
const first=()=>mkEvent('TASK_CREATED','manager',actors.manager,scopes,'gh69-r-test-create');

test('full pilot uses 7 durable management-execution-verifier events and production HOLD',async()=>{
 const {result,j}=await pilot(),state=await j.read();
 assert.equal(result.state,'PASS_SYNTHETIC_BOUNDED_HANDOFF_EXTERNAL_AUTHORITY_HOLD');
 assert.equal(state.sequence,7);assert.equal(state.state,'HOLD_EXTERNAL_AUTHORITY');
 assert.equal(result.donecheck,'HOLD');assert.equal(result.officialPassAdded,0);assert.equal(result.verifiedFinish,false);
 assert.equal(state.records[4].actor.id,actors.verifier);assert.equal(state.records[5].actor.id,actors.manager);
});
test('restart: journal reconstructs exact sequence/head',async()=>{
 const {p,j}=await pilot();const a=await j.read(),b=await new DisposableJournal(p).read();
 assert.equal(a.head,b.head);assert.equal(b.sequence,7);assert.equal(a.state,b.state);
});
test('repeat whole pilot produces no duplicate events',async()=>{
 const {p,j,observed}=await pilot();let a=await j.read();let b=await executeObservedPilot({observed,root:p,actorIds:actors});
 assert.equal((await j.read()).sequence,7);assert.equal(b.head,a.head);
});
test('CAS rejects stale version, accepts correct one',async()=>{
 const p=await root(),j=new DisposableJournal(p);await j.append(first(),0);
 await expectHold(j.append(mkEvent('WORK_ASSIGNED','manager',actors.manager,{taskId:scopes.taskId,assignedTo:actors.executor},'gh69-r-test-assign'),0),'HOLD_CAS_VERSION');
 assert.equal((await j.read()).sequence,1);
});
test('idempotency accepts exact retry even with old expected version',async()=>{
 const j=new DisposableJournal(await root()),e=first();await j.append(e,0);
 const r=await j.append(e,0);assert.equal(r.idempotent,true);assert.equal(r.sequence,1);
});
test('same idempotency token with mutated payload fails closed',async()=>{
 const j=new DisposableJournal(await root()),e=first();await j.append(e,0);
 await expectHold(j.append({...e,payload:{...scopes,controlIds:['B01-10']}},1),'HOLD_IDEMPOTENCY_CONFLICT');
});
test('double write rejected with existing lock',async()=>{
 const p=await root(),j=new DisposableJournal(p);let h=await open(join(p,'gh69-events.lock'),'wx');
 try{await expectHold(j.append(first(),0),'HOLD_CONCURRENT_WRITER');}finally{await h.close();}
});
test('tampering a recorded JSON field is detected',async()=>{
 const {p,j}=await pilot();const f=join(p,'gh69-events.jsonl');const content=await readFile(f,'utf8');
 await writeFile(f,content.replace('HOLD_EXTERNAL_TRUST_ROOT','PASS_EXTERNAL_TRUST_ROOT'));
 await expectHold(j.read(),'HOLD_JOURNAL_INTEGRITY');
});
test('tampering sequence detected',async()=>{
 const {p,j}=await pilot();const f=join(p,'gh69-events.jsonl'),c=await readFile(f,'utf8');
 await writeFile(f,c.replace('"sequence":1','"sequence":9'));
 await expectHold(j.read(),'HOLD_JOURNAL_INTEGRITY');
});
test('torn final JSON line stops replay',async()=>{
 const {p,j}=await pilot();let f=join(p,'gh69-events.jsonl'),c=await readFile(f);
 await writeFile(f,c.subarray(0,c.length-7));
 await expectHold(j.read(),'HOLD_INCOMPLETE_OR_OVERSIZED_JOURNAL');
});
test('untrusted output root rejected',async()=>{
 const j=new DisposableJournal('/mnt/data/gh69-malicious');
 await expectHold(j.append(first(),0),'HOLD_UNSCOPED_OUTPUT_ROOT');
});
test('symlinked journal rejected',async()=>{
 const p=await root(),j=new DisposableJournal(p),target=join(p,'target');await writeFile(target,'');
 await symlink(target,join(p,'gh69-events.jsonl'));
 await expectHold(j.read(),'HOLD_JOURNAL_SOURCE');
});
test('pilot refuses missing external ledger observation',async()=>{
 await expectHold(executeObservedPilot({observed:{state:'CLAIM'},root:await root(),actorIds:actors}),'HOLD_LEDGER_PROVENANCE');
});
test('pilot refuses producer and verifier identity collision',async()=>{
 await expectHold(executeObservedPilot({observed:await fixture(),root:await root(),actorIds:{...actors,verifier:actors.executor}}),'HOLD_ACTOR_SEPARATION');
});
test('unknown management role rejected',async()=>{
 await expectHold(new DisposableJournal(await root()).append(mkEvent('TASK_CREATED','issuer',actors.manager,scopes,'gh69-r-role'),0),'HOLD_ORDER_OR_ROLE');
});
test('invalid original source rejected',async()=>{
 await expectHold(new DisposableJournal(await root()).append(mkEvent('TASK_CREATED','manager',actors.manager,{...scopes,repo:'foreign/foreign'},'gh69-r-bad-scope'),0),'HOLD_SCOPE');
});
test('unbounded controls rejected',async()=>{
 await expectHold(new DisposableJournal(await root()).append(mkEvent('TASK_CREATED','manager',actors.manager,{...scopes,controlIds:Array(11).fill('B01-09')},'gh69-r-many'),0),'HOLD_SCOPE');
});
test('out-of-order executor event rejected',async()=>{
 await expectHold(new DisposableJournal(await root()).append(mkEvent('EXECUTION_RECORDED','executor',actors.executor,{taskId:scopes.taskId},'gh69-r-order'),0),'HOLD_ORDER_OR_ROLE');
});
test('invalid canonical JSON data rejected',async()=>{
 const e=first();e.payload={...scopes,missing:Infinity};
 await assert.rejects(new DisposableJournal(await root()).append(e,0),/INVALID_CANONICAL_JSON/);
});
test('partial journal resumes at same task without double-writing',async()=>{
 const p=await root(),observed=await fixture(),j=new DisposableJournal(p);
 await j.append(first(),0);
 await j.append(mkEvent('WORK_ASSIGNED','manager',actors.manager,{taskId:scopes.taskId,assignedTo:actors.executor},'gh69-wp0405-2'),1);
 // First idempotency key differs from pilot's key; resume must reject divergence.
 await expectHold(executeObservedPilot({observed,root:p,actorIds:actors}),'HOLD_ORDER_OR_ROLE');
});
test('resume after simulated interruption reuses exactly keyed first event',async()=>{
 const p=await root(),observed=await fixture(),j=new DisposableJournal(p);
 const e=mkEvent('TASK_CREATED','manager',actors.manager,scopes,'gh69-wp0405-1');
 await j.append(e,0);const old=(await j.read()).head;
 const r=await executeObservedPilot({observed,root:p,actorIds:actors});
 assert.equal(r.events,7);assert.equal((await j.read()).records[0].hash,old);
});
test('unverified manager external acceptance cannot be registered as state',async()=>{
 const {j}=await pilot(); const e=mkEvent('EXTERNAL_AUTHORITY_HOLD','manager',actors.manager,
 {taskId:scopes.taskId,state:'PASS_VERIFIED_FINISH',officialPassAdded:1},'gh69-finish-forgery');
 await expectHold(j.append(e,7),'HOLD_ORDER_OR_ROLE');
});
test('truncated event cannot be treated as completed after crash',async()=>{
 const p=await root(),j=new DisposableJournal(p);await j.append(first(),0);
 const f=join(p,'gh69-events.jsonl');let a=await readFile(f,'utf8');await writeFile(f,a+'{"partial":true');
 await expectHold(j.read(),'HOLD_INCOMPLETE_OR_OVERSIZED_JOURNAL');
});
test('duplicate original ID in management task is rejected',async()=>{
 const j=new DisposableJournal(await root());let e=first();e.payload={...scopes,controlIds:['B01-09','B01-09']};
 await expectHold(j.append(e,0),'HOLD_SCOPE');
});
test('forged issuer cannot serve as independent verifier',async()=>{
 const {j}=await pilot();const r=await j.read();assert.equal(r.records[4].actor.role,'verifier');
 assert.notEqual(r.records[4].actor.id,r.records[2].actor.id);
});
test('unknown task ID rejected at first durable event',async()=>{
 const j=new DisposableJournal(await root()),e=first();e.payload={...scopes,taskId:'FAKE'};
 await expectHold(j.append(e,0),'HOLD_SCOPE');
});
test('corrupted middle link rejected on restart',async()=>{
 const {p,j}=await pilot(),f=join(p,'gh69-events.jsonl');let c=await readFile(f,'utf8');
 await writeFile(f,c.replace(/"previousHash":"[a-f0-9]{64}"/, '"previousHash":"'+'0'.repeat(64)+'"'));
 await expectHold(j.read(),'HOLD_JOURNAL_INTEGRITY');
});
test('completed pilot has exactly one verified-candidate and zero official acceptance',async()=>{
 const {result,j}=await pilot(),r=await j.read();
 assert.equal(r.records.filter(x=>x.type==='INDEPENDENT_CHECKED').length,1);
 assert.equal(r.records.filter(x=>x.type==='EXTERNAL_AUTHORITY_HOLD').length,1);
 assert.equal(r.records.some(x=>x.type==='verified_finish'),false);
 assert.equal(result.officialPassAdded,0);assert.equal(result.verifiedFinish,false);
});
test.after(async()=>{await Promise.all(temps.map(p=>rm(p,{recursive:true,force:true})));});
