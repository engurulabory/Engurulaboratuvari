/** ENGURU GH69: bind actual seven-event handoff to immutable DoneCheck v1.2 source.
 * Read-only. Source evidence cannot grant owner/issuer/reviewer authority.
 */
import {createHash} from 'node:crypto';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {lstat,readFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {auditObservedLedger,gitBlob,SOURCE_PINS} from './enguru_management_v69_wp02_wp03_bridge.mjs';
import {DisposableJournal} from './enguru_management_v69_wp04_wp05_runtime.mjs';
const exec=promisify(execFile);
const H='4181f48df5ea0c060d9aa9f40a471c554b44b53d';
const PINS={
 'src/runtime/node/reviewer-attestation.ts':'07a498195598daf4b5f7328593b3f5d9f4',
 'src/runtime/node/audit-ledger.ts':'3fcee6dfefa1d68cfdbb7ff3d3889603d87620f8',
 'src/runtime/node/verified-finish-runtime.ts':'4d43505a568caef023e7488d15c017355ce58f11',
 'src/donecheck-runtime-node.ts':'9325f76b2dd7c70d590a8fab41ad86a3d266e2e3'
};
const TYPES=['TASK_CREATED','WORK_ASSIGNED','EXECUTION_RECORDED','EVIDENCE_BOUND','INDEPENDENT_CHECKED','MANAGEMENT_DECISION','EXTERNAL_AUTHORITY_HOLD'];
const HOLD=reason=>({state:'HOLD',reason,officialPassAdded:0,verifiedFinish:false,donecheckRuntimeInvoked:false});
const sha=b=>createHash('sha256').update(b).digest('hex');
export function inspectHandoff(o,c){
 if(o?.state!=='PASS_READ_ONLY_LEDGER_OBSERVATION'||o.ledgerBlobSha1!==SOURCE_PINS.ledgerGitBlob||
    !/^[a-f0-9]{64}$/.test(o.rawSha256))return HOLD('HOLD_LEDGER_SCOPE');
 if(!c||c.sequence!==7||c.state!=='HOLD_EXTERNAL_AUTHORITY'||c.records?.length!==7)return HOLD('HOLD_JOURNAL_SCOPE');
 const r=c.records;
 for(let i=0;i<7;i++){
   if(r[i]?.type!==TYPES[i]||r[i].eventId!==SOURCE_PINS.taskId+':'+(i+1)||
      r[i].sequence!==i+1||r[i].payload?.taskId!==SOURCE_PINS.taskId)return HOLD('HOLD_JOURNAL_ORDER');
 }
 const manager=r[0].actor?.id,executor=r[2].actor?.id,verifier=r[4].actor?.id;
 if(!manager||!executor||!verifier||new Set([manager,executor,verifier]).size!==3||
   r[0].actor?.role!=='manager'||r[2].actor?.role!=='executor'||r[4].actor?.role!=='verifier'||
   r[1].actor?.id!==manager||r[3].actor?.id!==executor||r[5].actor?.id!==manager||r[6].actor?.id!==manager)
   return HOLD('HOLD_ACTOR_SEPARATION');
 const init=r[0].payload;
 if(init.repo!==SOURCE_PINS.repo||init.ledgerPrHead!==SOURCE_PINS.ledgerPrHead||
    init.ledgerBlob!==o.ledgerBlobSha1||init.controlIds?.length!==1||
    init.controlIds[0]!=='B01-09')return HOLD('HOLD_TASK_SOURCE_SCOPE');
 if(r[1].payload?.assignedTo!==executor||r[2].payload?.result!==o.state||
    r[2].payload?.digest!==o.rawSha256||r[3].payload?.digest!==o.rawSha256||
    r[4].payload?.evidenceDigest!==o.rawSha256||r[4].payload?.verdict!=='PASS_CANDIDATE_ONLY'||
    r[5].payload?.reviewedEvidence!==o.rawSha256||
    r[5].payload?.verdict!=='HOLD_EXTERNAL_AUTHORITY'||r[6].payload?.state!=='HOLD_EXTERNAL_TRUST_ROOT'||
    r[6].payload?.officialPassAdded!==0)return HOLD('HOLD_EVIDENCE_OR_FINAL_AUTHORITY');
 return {state:'PASS_BOUNDED_READONLY_HANDOFF',taskId:SOURCE_PINS.taskId,
   ledgerBlob:o.ledgerBlobSha1,ledgerSha256:o.rawSha256,journalHead:c.head,events:7,
   officialPassAdded:0,verifiedFinish:false,donecheckRuntimeInvoked:false};
}
export async function inspectDoneCheck(root){
 try{
   const dir=resolve(root);
   const stat=await lstat(dir);
   if(!stat.isDirectory()||stat.isSymbolicLink())return HOLD('HOLD_DONECHECK_ROOT');
   const {stdout}=await exec('git',['-C',dir,'rev-parse','HEAD'],{timeout:10000});
   if(stdout.trim()!==H)return HOLD('HOLD_DONECHECK_HEAD');
   const blobs={};
   for(const [p,pin] of Object.entries(PINS)){
     const st=await lstat(join(dir,p));
     if(!st.isFile()||st.isSymbolicLink()||st.nlink!==1)return HOLD('HOLD_DONECHECK_FILE_TYPE');
     const raw=await readFile(join(dir,p)),blob=gitBlob(raw);
     if(blob!==pin)return HOLD('HOLD_DONECHECK_BLOB');
     blobs[p]={gitBlob:blob,sha256:sha(raw)};
   }
   return {state:'PASS_PINNED_DONECHECK_SOURCE_ONLY',sourceHead:H,blobs,
     officialPassAdded:0,verifiedFinish:false,donecheckRuntimeInvoked:false};
 }catch{return HOLD('HOLD_DONECHECK_SOURCE_UNAVAILABLE');}
}
export async function inspectRealBinding({ledgerFile,journalRoot,donecheckRoot}){
 let ledger,chain;
 try{
   const stat=await lstat(ledgerFile);
   if(!stat.isFile()||stat.isSymbolicLink()||stat.nlink!==1)return HOLD('HOLD_LEDGER_SOURCE');
   ledger=await readFile(ledgerFile);
   chain=await new DisposableJournal(journalRoot).read();
 }catch{return HOLD('HOLD_LEDGER_OR_JOURNAL_MISSING');}
 const observed=auditObservedLedger(ledger);
 const h=inspectHandoff(observed,chain);
 if(h.state!=='PASS_BOUNDED_READONLY_HANDOFF')return h;
 const d=await inspectDoneCheck(donecheckRoot);
 if(d.state!=='PASS_PINNED_DONECHECK_SOURCE_ONLY')return d;
 return {schema:'enguru.gh69.wp0205.source-handoff/v1',
   state:'PASS_REAL_PINNED_SOURCE_AND_HANDOFF_EXTERNAL_AUTHORITY_HOLD',
   taskId:SOURCE_PINS.taskId,controls:['B01-09'],
   ledgerBlob:h.ledgerBlob,ledgerSha256:h.ledgerSha256,journalHead:h.journalHead,events:7,
   donecheckHead:d.sourceHead,donecheckBlobs:d.blobs,trustRoot:'HOLD_NO_AUTHORIZED_EXTERNAL_ISSUER',
   reviewer:'HOLD_NO_INDEPENDENT_SIGNED_REVIEW',writer:'HOLD_NO_CANONICAL_LEDGER_GRANT',
   nextAction:'AUTHENTICATE_EXTERNAL_OWNER_ISSUER_VERIFIER_THEN_INVOKE_EXISTING_DONECHECK_V12',
   officialPassAdded:0,verifiedFinish:false,donecheckRuntimeInvoked:false};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const [cmd,ledgerFile,journalRoot,donecheckRoot]=process.argv.slice(2);
 if(cmd!=='--readonly'||!ledgerFile||!journalRoot||!donecheckRoot){
   console.log(JSON.stringify(HOLD('HOLD_USAGE')));process.exitCode=2;
 }else{
   inspectRealBinding({ledgerFile,journalRoot,donecheckRoot}).then(result=>{
     console.log(JSON.stringify(result));process.exitCode=result.state.startsWith('PASS_')?0:2;
   }).catch(()=>{console.log(JSON.stringify(HOLD('HOLD_RUNTIME')));process.exitCode=2;});
 }
}
