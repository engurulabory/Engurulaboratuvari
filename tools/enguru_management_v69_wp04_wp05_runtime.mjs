/**
 * ENGURU V6.9 WP04 + WP05 — disposable durable Management/Execution handoff pilot.
 * Requires read-only observed PR191 ledger. Writes only to an explicit disposable root;
 * never writes canonical ledger, DoneCheck, source repo, or production authority.
 * Hash chain detects accidental/unauthorized modifications relative to observed
 * content; it is NOT a cryptographic external trust anchor.
 */
import {open, readFile, mkdir, lstat, readdir} from 'node:fs/promises';
import {join,resolve,dirname} from 'node:path';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {auditObservedLedger,canonicalJson,SOURCE_PINS} from './enguru_management_v69_wp02_wp03_bridge.mjs';

const sha = raw => createHash('sha256').update(raw).digest('hex');
const EVENT_ACTORS={TASK_CREATED:'manager',WORK_ASSIGNED:'manager',EXECUTION_RECORDED:'executor',
  EVIDENCE_BOUND:'executor',INDEPENDENT_CHECKED:'verifier',MANAGEMENT_DECISION:'manager',
  EXTERNAL_AUTHORITY_HOLD:'manager'};
const SEQUENCE=Object.keys(EVENT_ACTORS);
const STATES={TASK_CREATED:'REGISTERED',WORK_ASSIGNED:'ASSIGNED',EXECUTION_RECORDED:'EXECUTED',
 EVIDENCE_BOUND:'EVIDENCE_BOUND',INDEPENDENT_CHECKED:'VERIFICATION_CANDIDATE',
 MANAGEMENT_DECISION:'MANAGEMENT_REVIEWED',EXTERNAL_AUTHORITY_HOLD:'HOLD_EXTERNAL_AUTHORITY'};
const ID=/^[a-zA-Z0-9][a-zA-Z0-9._:-]{4,127}$/;
function fail(reason){const e=new Error(reason);e.code=reason;throw e;}
function validateScope(v){
 if(!v||typeof v!=='object'||v.taskId!==SOURCE_PINS.taskId||v.repo!==SOURCE_PINS.repo||
    v.ledgerPrHead!==SOURCE_PINS.ledgerPrHead||v.ledgerBlob!==SOURCE_PINS.ledgerGitBlob||
    !Array.isArray(v.controlIds)||v.controlIds.length<1||v.controlIds.length>10||
    new Set(v.controlIds).size!==v.controlIds.length||
    v.controlIds.some(x=>!/^B(?:0[1-9]|10)-(?:0[1-9]|10)$/.test(x)))fail('HOLD_SCOPE');
 return v;
}
function nextState(replayed,type,actor,payload){
 const i=replayed.length;
 if(i>=SEQUENCE.length||SEQUENCE[i]!==type||EVENT_ACTORS[type]!==actor.role)fail('HOLD_ORDER_OR_ROLE');
 if(typeof actor.id!=='string'||!ID.test(actor.id)||typeof payload!=='object'||payload===null||Array.isArray(payload))fail('HOLD_ACTOR_OR_PAYLOAD');
 const p=replayed.length?replayed[0].payload:null;
 const actors=Object.fromEntries(replayed.filter(x=>x.type==='WORK_ASSIGNED'||x.type==='INDEPENDENT_CHECKED'||x.type==='TASK_CREATED').map(x=>[x.type,x.actor.id]));
 if(type==='TASK_CREATED'){
   validateScope(payload);
 }else{
   if(!p||payload.taskId!==p.taskId)fail('HOLD_TASK_BOUNDARY');
   if(type==='WORK_ASSIGNED'&&(!ID.test(payload.assignedTo)||payload.assignedTo===actor.id))fail('HOLD_ASSIGNMENT');
   if(type==='EXECUTION_RECORDED'&&(actor.id!==replayed[1].payload.assignedTo||
     payload.operation!=='AUDIT_PINNED_LEDGER'||payload.result!=='PASS_READ_ONLY_LEDGER_OBSERVATION'))fail('HOLD_UNVERIFIED_EXECUTION');
   if(type==='EVIDENCE_BOUND' && (payload.digest!==replayed[2].payload.digest ||
      !/^[a-f0-9]{64}$/.test(payload.digest)))fail('HOLD_EVIDENCE_DIGEST');
   if(type==='INDEPENDENT_CHECKED' && (actor.id===replayed[2].actor.id ||
      actor.id===actors.TASK_CREATED || payload.evidenceDigest!==replayed[3].payload.digest ||
      payload.verdict!=='PASS_CANDIDATE_ONLY'))fail('HOLD_VERIFIER_SEPARATION');
   if(type==='MANAGEMENT_DECISION' && (actor.id!==actors.TASK_CREATED ||
      payload.verdict!=='HOLD_EXTERNAL_AUTHORITY'||payload.reviewedEvidence!==replayed[4].payload.evidenceDigest))fail('HOLD_MANAGER_DECISION');
   if(type==='EXTERNAL_AUTHORITY_HOLD' && (actor.id!==actors.TASK_CREATED ||
      payload.state!=='HOLD_EXTERNAL_TRUST_ROOT'||payload.officialPassAdded!==0))fail('HOLD_OFFICIAL_BOUNDARY');
 }
 return STATES[type];
}
function validateRecordShape(r,n,prev){
 if(!r||typeof r!=='object'||r.sequence!==n+1||r.previousHash!==prev||
    !ID.test(r.idempotencyKey)||typeof r.eventId!=='string'||
    r.eventId!==`${SOURCE_PINS.taskId}:${n+1}`||!r.actor||!Object.hasOwn(EVENT_ACTORS,r.type)||
    typeof r.hash!=='string'||r.hash!==sha(canonicalJson({sequence:r.sequence,previousHash:r.previousHash,eventId:r.eventId,
     type:r.type,actor:r.actor,payload:r.payload,idempotencyKey:r.idempotencyKey})))fail('HOLD_JOURNAL_INTEGRITY');
}
export function replayBytes(bytes){
 if(!Buffer.isBuffer(bytes))fail('HOLD_JOURNAL_INPUT');
 if(bytes.length===0)return {sequence:0,state:'EMPTY',head:null,records:[]};
 if(bytes.length>3_000_000||bytes.at(-1)!==10)fail('HOLD_INCOMPLETE_OR_OVERSIZED_JOURNAL');
 const lines=bytes.toString('utf8').trimEnd().split('\n');
 if(lines.length>SEQUENCE.length)fail('HOLD_EXCESS_JOURNAL');
 const records=[];let prev=null;
 for(let i=0;i<lines.length;i++){
   let v;try{v=JSON.parse(lines[i]);}catch{fail('HOLD_JOURNAL_PARSE');}
   validateRecordShape(v,i,prev);
   const state=nextState(records,v.type,v.actor,v.payload);
   if(v.state!==state)fail('HOLD_JOURNAL_STATE');
   if(records.some(x=>x.idempotencyKey===v.idempotencyKey))fail('HOLD_JOURNAL_DUPLICATE');
   records.push(v);prev=v.hash;
 }
 return {sequence:records.length,state:records.length?records.at(-1).state:'EMPTY',head:prev,records};
}
function makeRecord(chain,event){
 const state=nextState(chain.records,event.type,event.actor,event.payload);
 if(!ID.test(event.idempotencyKey))fail('HOLD_IDEMPOTENCY_KEY');
 const next=chain.sequence+1, material={sequence:next,previousHash:chain.head,
    eventId:`${SOURCE_PINS.taskId}:${next}`,type:event.type,actor:event.actor,
    payload:event.payload,idempotencyKey:event.idempotencyKey};
 return {...material,state,hash:sha(canonicalJson(material))};
}
async function safeDirectory(root){
 if(typeof root!=='string'||!root.startsWith(resolve(tmpdir())+'/gh69-')||root.includes('..'))fail('HOLD_UNSCOPED_OUTPUT_ROOT');
 const abs=resolve(root);if(abs!==root||abs===resolve(tmpdir()))fail('HOLD_UNSCOPED_OUTPUT_ROOT');
 const parent=dirname(abs);const s=await lstat(parent).catch(()=>null);
 if(!s||!s.isDirectory()||s.isSymbolicLink())fail('HOLD_OUTPUT_PARENT');
 const x=await lstat(abs).catch(()=>null);
 if(!x)await mkdir(abs,{mode:0o700});
 const y=await lstat(abs);
 if(!y.isDirectory()||y.isSymbolicLink())fail('HOLD_OUTPUT_SYMLINK');
 return abs;
}
export class DisposableJournal{
 constructor(root){this.root=root;this.file=join(root,'gh69-events.jsonl');this.lock=join(root,'gh69-events.lock');}
 async read(){
   await safeDirectory(this.root);
   const st=await lstat(this.file).catch(()=>null);
   if(st&&(!st.isFile()||st.isSymbolicLink()||st.nlink!==1))fail('HOLD_JOURNAL_SOURCE');
   const raw=st?await readFile(this.file):Buffer.alloc(0);
   return replayBytes(raw);
 }
 async append(event,expectedSequence){
   await safeDirectory(this.root);
   let lock;try{lock=await open(this.lock,'wx',0o600);}catch{fail('HOLD_CONCURRENT_WRITER');}
   try{
     const chain=await this.read();
     const prior=chain.records.find(x=>x.idempotencyKey===event.idempotencyKey);
     if(prior){
       const wanted={type:event.type,actor:event.actor,payload:event.payload,idempotencyKey:event.idempotencyKey};
       const actual={type:prior.type,actor:prior.actor,payload:prior.payload,idempotencyKey:prior.idempotencyKey};
       if(canonicalJson(wanted)!==canonicalJson(actual))fail('HOLD_IDEMPOTENCY_CONFLICT');
       return {state:chain.state,sequence:chain.sequence,head:chain.head,idempotent:true};
     }
     if(!Number.isSafeInteger(expectedSequence)||expectedSequence!==chain.sequence)fail('HOLD_CAS_VERSION');
     const record=makeRecord(chain,event);
     const h=await open(this.file,'a',0o600);
     try{await h.writeFile(canonicalJson(record)+'\n','utf8');await h.sync();}finally{await h.close();}
     const now=await this.read();
     if(now.sequence!==chain.sequence+1||now.head!==record.hash)fail('HOLD_WRITE_VERIFICATION');
     return {sequence:now.sequence,state:now.state,head:now.head,idempotent:false};
   }finally{await lock.close();await import('node:fs/promises').then(m=>m.unlink(this.lock)).catch(()=>undefined);}
 }
}
/** Live read-only operation under explicit disposable root: actual source audit,
 * typed task transitions and evidence digest; no human grants synthesized. */
export async function executeBoundedPilot({ledgerFile,root,actorIds}){
 const {manager,executor,verifier}=actorIds||{};
 if([manager,executor,verifier].some(x=>!ID.test(x))||new Set([manager,executor,verifier]).size!==3)fail('HOLD_ACTOR_SEPARATION');
 if(typeof ledgerFile!=='string'||!ledgerFile)fail('HOLD_LEDGER_LOCATION');
 const st=await lstat(ledgerFile).catch(()=>null);
 if(!st||!st.isFile()||st.isSymbolicLink())fail('HOLD_LEDGER_SOURCE');
 const raw=await readFile(ledgerFile),observed=auditObservedLedger(raw);
 if(observed.state!=='PASS_READ_ONLY_LEDGER_OBSERVATION')fail('HOLD_SOURCE_PROVENANCE');
 return executeObservedPilot({observed,root,actorIds});
}
/** Explicit read-only observation candidate for deterministic tests; never authority. */
export async function executeObservedPilot({observed,root,actorIds}){
 if(observed?.state!=='PASS_READ_ONLY_LEDGER_OBSERVATION'|| !/^[0-9a-f]{40}$/.test(observed.ledgerBlobSha1)||
   !/^[0-9a-f]{64}$/.test(observed.rawSha256))fail('HOLD_LEDGER_PROVENANCE');
 // TEST-ONLY callable. The real CLI always verifies SOURCE_PINS.ledgerGitBlob itself.
 if([actorIds?.manager,actorIds?.executor,actorIds?.verifier].some(x=>!ID.test(x))||
    new Set([actorIds.manager,actorIds.executor,actorIds.verifier]).size!==3)fail('HOLD_ACTOR_SEPARATION');
 const {manager,executor,verifier}=actorIds;
 const j=new DisposableJournal(root);const events=[
  ['TASK_CREATED','manager',{taskId:SOURCE_PINS.taskId,repo:SOURCE_PINS.repo,
   ledgerPrHead:SOURCE_PINS.ledgerPrHead,ledgerBlob:SOURCE_PINS.ledgerGitBlob,controlIds:['B01-09']}],
  ['WORK_ASSIGNED','manager',{taskId:SOURCE_PINS.taskId,assignedTo:executor}],
  ['EXECUTION_RECORDED','executor',{taskId:SOURCE_PINS.taskId,operation:'AUDIT_PINNED_LEDGER',
    result:observed.state,digest:observed.rawSha256}],
  ['EVIDENCE_BOUND','executor',{taskId:SOURCE_PINS.taskId,digest:observed.rawSha256}],
  ['INDEPENDENT_CHECKED','verifier',{taskId:SOURCE_PINS.taskId,verdict:'PASS_CANDIDATE_ONLY',
    evidenceDigest:observed.rawSha256}],
  ['MANAGEMENT_DECISION','manager',{taskId:SOURCE_PINS.taskId,verdict:'HOLD_EXTERNAL_AUTHORITY',
    reviewedEvidence:observed.rawSha256}],
  ['EXTERNAL_AUTHORITY_HOLD','manager',{taskId:SOURCE_PINS.taskId,
    state:'HOLD_EXTERNAL_TRUST_ROOT',officialPassAdded:0}]
 ];
 for(let i=0;i<events.length;i++){
   const [type,role,payload]=events[i];let chain=await j.read();
   const event={type,actor:{role,id:actorIds[role]},payload,idempotencyKey:`gh69-wp0405-${i+1}`};
   await j.append(event,chain.sequence);
 }
 const completed=await j.read();
 return {state:observed.ledgerBlobSha1===SOURCE_PINS.ledgerGitBlob ?
   'PASS_REAL_BOUNDED_HANDOFF_EXTERNAL_AUTHORITY_HOLD' : 'PASS_SYNTHETIC_BOUNDED_HANDOFF_EXTERNAL_AUTHORITY_HOLD',
   taskId:SOURCE_PINS.taskId,
   events:completed.sequence,finalState:completed.state,head:completed.head,
   sourceLedgerBlob:observed.ledgerBlobSha1,sourceLedgerSha256:observed.rawSha256,
   officialPassAdded:0,verifiedFinish:false,donecheck:'HOLD',humanThreshold:'PRESERVED',
   durable:true,recovered:completed.records.length===SEQUENCE.length};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const args=process.argv.slice(2);
 if(args.length!==3||args[0]!=='--pilot')fail('USAGE: --pilot <ledger_file> <disposable_root>');
 executeBoundedPilot({ledgerFile:args[1],root:args[2],actorIds:{manager:'gh69-test-manager',executor:'gh69-test-executor',verifier:'gh69-test-independent-verifier'}})
   .then(x=>{console.log(JSON.stringify(x));process.exitCode=0;})
   .catch(e=>{console.log(JSON.stringify({state:'HOLD',reason:e.code||e.message,officialPassAdded:0,verifiedFinish:false}));process.exitCode=2;});
}