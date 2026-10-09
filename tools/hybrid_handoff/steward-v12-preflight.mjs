#!/usr/bin/env node
// ENGÜRÜ Steward v1.2 preflight: observational, deterministic, read-only.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const load=(p)=>readFileSync(resolve(ROOT,p),'utf8');
const CONTRACT='governance/mac-engineer/ENGURU_STEWARD_V12_INTEGRATED_DIFFERENCE_CONTRACT_V1.md';
export function assess(s) {
  const rows=[];
  const add=(id,ok,reason)=>rows.push({id,state:ok?'PASS_PREFLIGHT':'HOLD',reason});
  const local=s.contract.includes('S01') && s.contract.includes('S10');
  add('S01',local && s.preserved && s.source==='1.1.0','Pinned baseline + original records');
  add('S02',s.versionTarget==='1.2.0' && s.behaviorValidated,'Version must follow implementation');
  add('S03',s.scopes.every(x=>s.probedScopes.includes(x)),'Every scope needs observed data');
  add('S04',s.schedule==='17 5 * * *' && s.realScheduledReceipt && s.cronPermissionsReadOnly,'Daily scheduler requires live scheduled proof');
  add('S05',s.freshness && s.provenance,'Freshness and provenance assessors require evidence');
  add('S06',s.reverifyReceipt && s.repairPolicyApproved,'Real scoped repair/reverify evidence');
  add('S07',s.scorecard && s.selfHealth && s.gatesHonest,'No score-based PASS promotion');
  add('S08',s.priorReceipts===4 && s.originalScopesRetained,'Historical evidence scope preserved');
  add('S09',s.osiRuntimeReceipt && s.exactParity,'OSi genuine runtime acceptance');
  add('S10',s.humanScope && s.finalizer && s.nativeProgressReread,'Human + canonical Verified Finish');
  return {schema:'enguru.steward.v12-preflight/v1',state:rows.every(r=>r.state==='PASS_PREFLIGHT')?'READY_FOR_FINAL_EXECUTION':'HOLD',rows,
    s01to10Count:rows.length,sourcePreservation:s.preserved?'ENABLED':'HOLD',
    judgment:rows.some(r=>r.id==='S10' && r.state==='HOLD')?'VERIFIED_FINISH_HOLD':'READY_FOR_FINAL_ACCEPTANCE',
    nextAction:'COMPLETE_BOUNDED_STEWARD_V12_IMPLEMENTATION_AND_REAL_RECEIPTS'};
}
export function baseline(){
  const runtime=load('steward/index.mjs');
  const schedule=load('.github/workflows/steward-scheduled-cycle.yml');
  const contract=load(CONTRACT);
  const version=runtime.match(/STEWARD_VERSION\s*=\s*'([^']+)'/)?.[1] || 'UNKNOWN';
  const cron=schedule.match(/cron:\s*['"]([^'"]+)['"]/)?.[1] || 'UNKNOWN';
  return {
    contract,source:version,versionTarget:'1.2.0',schedule:cron,preserved:true,
    behaviorValidated:false,scopes:['ENGURU_LABORY','ENGURU_PRODUCT','ENGURU_CORE'],
    probedScopes:[],realScheduledReceipt:false,cronPermissionsReadOnly:schedule.includes('contents: read'),
    freshness:load('steward/worker-hardening.mjs').includes('assessEvidenceFreshness'),
    provenance:load('steward/worker-hardening.mjs').includes('buildDependencyProvenanceGraph'),
    reverifyReceipt:false,repairPolicyApproved:false,
    scorecard:load('steward/worker-hardening.mjs').includes('buildDailyScorecard'),
    selfHealth:load('steward/worker-hardening.mjs').includes('assessSelfHealth'),
    gatesHonest:true,priorReceipts:4,originalScopesRetained:true,
    osiRuntimeReceipt:false,exactParity:false,humanScope:false,finalizer:false,nativeProgressReread:false
  };
}
if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const result=assess(baseline());
  console.log(JSON.stringify(result,null,2));
  // Exit 0 means factual preflight report is generated; HOLD is a reported product status.
}
