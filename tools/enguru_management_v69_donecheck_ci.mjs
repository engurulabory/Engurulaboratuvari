#!/usr/bin/env node
/** Real DoneCheck verifyTask on GitHub-authenticated Management v6.9 machine evidence only. */
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

const REPO='engurulabory/Engurulaboratuvari';
const TASK='ENGURU_MANAGEMENT_V69_PR_203';
const IDS=['MGMT69-A-CI','MGMT69-B-SOURCE','MGMT69-C-OPERATIONS','MGMT69-BOUNDARY'];
const V3='11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc';
const TASK_PATH='governance/management-v69/DONECHECK_TASK_REGISTRATION_PREP_V1.json';
const hash=v=>crypto.createHash('sha256').update(v).digest('hex');
const check=(ok,why)=>{if(!ok)throw Error(why)};
const ishex=(x,n=40)=>typeof x==='string'&&new RegExp('^[0-9a-f]{'+n+'}$').test(x);

function taskContract(d) {
  check(d?.schema==='enguru.management-v69.donecheck-registration-preparation/v1','TASK_SCHEMA');
  check(d?.authorization?.decision==='APPROVED_SCOPE_PREPARATION_ONLY','SCOPE_AUTHORITY');
  check(d?.authorization?.cryptographic_human_review==='NOT_GRANTED','PREMATURE_HUMAN_GRANT');
  check(d?.donecheck_task?.id===TASK&&d?.donecheck_task?.status==='in_progress','TASK_ID_OR_STATUS');
  check(d?.existing_reviewer_candidate?.canonical_trust==='HOLD','FALSE_REVIEWER_GRANT');
  check(d?.official_finish==='HOLD','FALSE_ACCEPTANCE');
  check(d?.success_criteria?.length===4,'CRITERIA_SIZE');
  check(new Set(d.success_criteria.map(c=>c.id)).size===4,'CRITERIA_DUPLICATE');
  check(IDS.every(id=>d.success_criteria.some(c=>c.id===id&&c.taskId===TASK&&c.kind==='objective'&&c.required===true)),'CRITERIA_BINDING');
}
function scopedDiff(files) {
  check(Array.isArray(files)&&files.length>0&&files.length<100,'PR_DIFF_SIZE');
  for(const f of files) {
    const p=f?.filename;
    check(typeof p==='string'&&(p==='.github/workflows/enguru-management-v69.yml'
      ||p.startsWith('governance/management-v69/')
      ||/^tools\/enguru_management_v69[\w.\-]*\.(py|mjs)$/.test(p)
      ||/^tests\/test_enguru_management_v69[\w.\-]*\.py$/.test(p)),'PR_FOREIGN_FILE');
  }
}
function runContract(pr,run,jobs,head) {
  check(pr?.number===203&&pr?.state==='open'&&pr?.merged===false,'PR_SCOPE_OR_MERGED');
  check(pr?.head?.sha===head&&pr?.base?.ref==='main','PR_HEAD_DRIFT');
  check(run?.head_sha===head&&run?.event==='pull_request','RUN_HEAD_MISMATCH');
  check(Array.isArray(jobs?.jobs),'JOBS_SHAPE');
  const m=jobs.jobs.filter(j=>j.name==='verify'&&j.run_id===run.id);
  check(m.length===1&&m[0].status==='completed'&&m[0].conclusion==='success','VERIFY_JOB_NOT_PASS');
  return m[0].id;
}
function operationContract(o,main) {
  check(o?.state==='PASS_GITHUB_PROVENANCE_OFFICIAL_HOLD','OPERATION_NOT_PROVEN');
  check(o?.task_id==='LABORY_SAFE_REPAIR'&&o?.source_commit===main,'CONTROLLER_SOURCE_DRIFT');
  check(o?.github_bot_identity==='PASS_GITHUB_API_ACCOUNT'&&o?.worker_observation==='PASS','WORKER_NOT_PROVEN');
  check(o?.receipt_public_integrity==='PASS'&&ishex(o?.verified_public_receipt_sha256,64),'RECEIPT_UNPROVEN');
  check(o?.official_finish==='HOLD'&&o?.independent_donecheck==='HOLD','FOREIGN_ACCEPTANCE');
}
function selfTest(d) {
  const tests=[
    ()=>taskContract(d),
    ()=>taskContract({...d,authorization:{...d.authorization,cryptographic_human_review:'FAKE'}}),
    ()=>taskContract({...d,donecheck_task:{...d.donecheck_task,id:'FOREIGN'}}),
    ()=>taskContract({...d,success_criteria:[...d.success_criteria.slice(0,3),d.success_criteria[0]]}),
    ()=>scopedDiff([{filename:'tools/enguru_management_v69_donecheck_ci.mjs'}]),
    ()=>scopedDiff([{filename:'governance/controller/TASKS.json'}]),
    ()=>runContract({number:203,state:'open',merged:false,head:{sha:'a'.repeat(40)},base:{ref:'main'}},{id:1,head_sha:'a'.repeat(40),event:'pull_request'},{jobs:[{name:'verify',run_id:1,status:'completed',conclusion:'failure'}]},'a'.repeat(40))
  ];
  for(let i=0;i<tests.length;i++){let passed=true;try{tests[i]();}catch{passed=false}check(passed===(i===0||i===4),'SELF_TEST_'+i)}
  console.log('STATE=PASS_DONECHECK_CI_SELF_TEST;TESTS=7/7');
}
async function api(s,token) {
  const r=await fetch('https://api.github.com/repos/'+REPO+'/'+s,{
    headers:{Authorization:'Bearer '+token,Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'enguru-v69-independent-machine'},
    signal:AbortSignal.timeout(20000)});
  check(r.ok,'GITHUB_API_STATUS_'+r.status);
  return r.json();
}
async function source(p,ref,token) {
  const x=await api('contents/'+p+'?ref='+encodeURIComponent(ref),token);
  check(x.encoding==='base64'&&typeof x.content==='string','SOURCE_ENCODING');
  return Buffer.from(x.content.replace(/\s/g,''),'base64');
}
async function main() {
  const doc=JSON.parse(fs.readFileSync(TASK_PATH,'utf8'));
  taskContract(doc);
  if(process.argv.includes('--self-test'))return selfTest(doc);
  check(process.argv.includes('--live'),'EXPLICIT_LIVE_REQUIRED');
  const token=process.env.GITHUB_TOKEN,head=process.env.EXPECTED_PR_HEAD;
  const runid=Number(process.env.GITHUB_RUN_ID);
  check(token?.length>10&&process.env.GITHUB_REPOSITORY===REPO,'GITHUB_AUTHENTICATION');
  check(process.env.GITHUB_EVENT_NAME==='pull_request'&&ishex(head),'PR_HEAD_CONTEXT');
  check(Number.isSafeInteger(runid)&&runid>0,'RUN_ID');
  const [pr,run,jobs,m,files]=await Promise.all([
    api('pulls/203',token),api('actions/runs/'+runid,token),
    api('actions/runs/'+runid+'/jobs?per_page=100',token),
    api('git/ref/heads/main',token),api('pulls/203/files?per_page=100',token)]);
  const jobid=runContract(pr,run,jobs,head);
  const mainsha=m?.object?.sha;
  check(ishex(mainsha)&&pr?.base?.sha===mainsha,'MAIN_REF_DRIFT');
  scopedDiff(files);
  const [v3,agents]=await Promise.all([
    source('governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md',mainsha,token),
    source('AGENTS.md',mainsha,token)]);
  check(hash(v3)===V3,'CANONICAL_V3_SHA256');
  check(agents.toString('utf8').includes('ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md'),'AGENT_V3_ROUTE');
  const actual=JSON.parse(execFileSync('python3',['tools/enguru_management_v69_operation.py','--live'],{
    encoding:'utf8',timeout:120000,maxBuffer:500000,env:process.env}));
  operationContract(actual,mainsha);
  const proof=[
    'head='+head+' run='+runid+' successful verify-job='+jobid,
    'main='+mainsha+' V3='+V3+' PR-diff-count='+files.length,
    'worker='+actual.worker_job_id+' public-receipt='+actual.verified_public_receipt_sha256,
    'scope=management-v69 files='+files.length+' owner-authority=RESERVED'];
  const now=new Date().toISOString();
  const evidence=IDS.map((id,i)=>({
    id:'V69_'+id,taskId:TASK,criterionId:id,kind:'test_report',source:'system',
    content:'[DONECHECK:PASS] Independently authenticated GitHub API observations: '+proof[i],
    collectedAt:now,
    provenance:{schema:'donecheck.evidence-provenance/v1',producerKind:'github_ci',
      producerId:'enguru.github.management-v69-independent-api-observer',
      executionId:'run:'+runid+':verify-job:'+jobid,
      artifactDigest:'sha256:'+hash(JSON.stringify({id,proof:proof[i],head,runid,jobid})),
      observedAt:now,verificationRef:'https://github.com/'+REPO+'/actions/runs/'+runid}
  }));
  const bundle=process.env.DONECHECK_CORE_BUNDLE;
  check(bundle&&fs.existsSync(bundle),'DONECHECK_REAL_MODULE_REQUIRED');
  const core=await import(pathToFileURL(path.resolve(bundle)).href);
  check(typeof core.verifyTask==='function','DONECHECK_VERIFYTASK_REQUIRED');
  const verification=core.verifyTask({
    task:doc.donecheck_task,criteria:doc.success_criteria,evidence,
    aiOutput:'Independent machine verification of PR #203 technical A/B/C and preserved authority boundaries.',
    resultId:'MGMT69_VR_GITHUB_RUN_'+runid,verifiedAt:now,
    policy:{requireEvidenceProvenance:true,trustedProducerIds:['enguru.github.management-v69-independent-api-observer']}
  });
  check(verification.taskId===TASK&&verification.outcome==='pass'&&verification.criteria.length===4,'DONECHECK_VERIFICATION_HOLD');
  const report={schema:'enguru.management-v69.donecheck-machine-verification/v1',
    state:'PASS_REAL_DONECHECK_VERIFYTASK_TECHNICAL_ONLY',taskId:TASK,source_head:head,
    source_main:mainsha,github_run_id:runid,github_verify_job_id:jobid,
    donecheck_commit:'4181f48df5ea0c060d9aa9f40a471c554b44b53d',
    verificationResult:verification,
    criterionEvidence:evidence.map(e=>({id:e.id,criterionId:e.criterionId,provenance:e.provenance})),
    producerAuthority:'GITHUB_READ_API_IN_THIS_WORKFLOW_NOT_CRYPTOGRAPHIC_REVIEWER_ATTESTATION',
    canonicalOSiEnrollment:'HOLD_UNVERIFIED',reviewerTrust:'HOLD_UNVERIFIED',
    humanReview:'NOT_SIGNED',auditLedger:'NOT_WRITTEN',verifiedFinish:'HOLD',officialFinish:'HOLD'};
  const output=process.env.DONECHECK_VERIFICATION_OUTPUT;
  check(output&&output.startsWith(process.env.RUNNER_TEMP+'/'),'RUNNER_TEMP_OUTPUT_ONLY');
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx',mode:0o600});
  console.log(JSON.stringify({state:report.state,taskId:TASK,verificationResultId:verification.id,
    outcome:verification.outcome,criteria:verification.criteria.length,
    evidenceSha256:hash(fs.readFileSync(output)),officialFinish:'HOLD'},null,2));
}
main().catch(e=>{console.error('STATE=HOLD_DONECHECK_MACHINE_VERIFICATION');console.error('REASON='+String(e.message).slice(0,180));process.exitCode=50});
