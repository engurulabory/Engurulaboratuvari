/** Existing DoneCheck core client for the engine's own final task, not an issuer. */
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';

const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const base='tools/zulfikar-performance-v141/';
const scope=read(base+'ENGINE_FINAL_SCOPE.json');
assert.equal(scope.kind,'USER_GOAL_SCOPE_RECONCILIATION_NOT_A_NEW_ACCEPTANCE_AUTHORITY');
assert.equal(scope.officialVerifiedFinish,'HOLD');
const head=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim();
assert.match(head,/^[a-f0-9]{40}$/);
assert.equal(head,process.env.EXPECTED_ENGINE_HEAD);
assert.equal(process.env.GITHUB_REPOSITORY,'engurulabory/Engurulaboratuvari');
const root='evidence/engine-final';
const logs=['round-1-source.log','round-2-resilience.log','round-3-finish.log'];
for(const f of logs)assert.match(fs.readFileSync(root+'/'+f,'utf8'),/\nOK\s*$/);
const second=read('evidence/second-exam/summary.json');
assert.equal(second.tasksPassed,3);
assert.equal(second.finalMet,12);
assert.equal(second.totalCriteria,12);
assert.equal(second.officialVerifiedFinish,'HOLD');
for(let n=1;n<=3;n++){
 const s=read('evidence/performance/round-'+n+'/summary.json');
 assert.equal(s.tasks,5);assert.equal(s.passed,5);assert.equal(s.verifiedFinish,'HOLD');
 for(const t of s.results)assert.equal(t.pass,true);
}
const seal=read('governance/enguru-suzgeci/zulfikar-v12/v141/GITHUB_SOURCE_SHA_SEAL_V2.json');
assert.equal(seal.stageFiles.length,18);
for(const row of seal.stageFiles)assert.equal(sha(fs.readFileSync(row.path)),row.sha256);
const core=await import(pathToFileURL(path.resolve(process.env.DONECHECK_CORE_BUNDLE)).href);
assert.equal(typeof core.verifyTask,'function');
const now=new Date().toISOString(), run=process.env.GITHUB_RUN_ID;
assert.match(run,/^[0-9]+$/);
const task={id:scope.taskId,title:'Zulfikar V1.4.1 engineering engine final',
 requestText:scope.goal,description:'Engine-only acceptance; separate product adoption/field tasks excluded by explicit owner decision.',
 status:'awaiting_review',createdAt:now};
const criteria=[...scope.technicalCriteria.map(c=>({...c,kind:'objective'})),
 ...scope.requiredHumanCriteria.map(c=>({...c,kind:'subjective'}))].map(c=>({...c,taskId:task.id,required:true,
 verificationInstruction:'Review exact engine HEAD '+head+' and source-pinned real evidence; human authority is separate.'}));
const files=[base+'ENGINE_FINAL_SCOPE.json',base+'verify_engine_donecheck.mjs',
 ...logs.map(f=>root+'/'+f),'evidence/second-exam/summary.json',
 ...[1,2,3].map(n=>'evidence/performance/round-'+n+'/summary.json')];
const filePins=Object.fromEntries(files.map(p=>[p,sha(fs.readFileSync(p))]));
const producerId='enguru.github.zulfikar-engine-ci';
const evidence=scope.technicalCriteria.map(c=>({id:'ENGINE_E_'+c.id,taskId:task.id,criterionId:c.id,
 kind:'test_report',source:'system',collectedAt:now,
 content:'[DONECHECK:PASS] Source-pinned real engine task outputs and successful existing verifiers; head='+head+' criterion='+c.id,
 provenance:{schema:'donecheck.evidence-provenance/v1',producerKind:'github_ci',producerId,
 executionId:'run:'+run+':engine-final',artifactDigest:'sha256:'+sha(JSON.stringify({head,criterion:c.id,filePins})),
 observedAt:now,verificationRef:'https://github.com/engurulabory/Engurulaboratuvari/actions/runs/'+run}}));
const input={task,criteria,aiOutput:'Engine technical acceptance candidate; independent review and final human authority remain unverified.',
 evidence,verifiedAt:now,policy:{requireEvidenceProvenance:true,trustedProducerIds:[producerId]}};
const machine=core.verifyTask({...input,criteria:criteria.filter(c=>c.kind==='objective'),resultId:'ZF_ENGINE_TECH_'+run});
const full=core.verifyTask({...input,resultId:'ZF_ENGINE_FULL_'+run});
assert.equal(machine.outcome,'pass');assert.equal(machine.criteria.length,4);
assert.equal(full.outcome,'inconclusive');assert.equal(full.criteria.length,6);
assert.equal(full.criteria.filter(c=>c.outcome==='inconclusive').length,2);
// Real negative use of the existing core: an untrusted assertion cannot close a criterion.
const refused=core.verifyTask({...input,criteria:criteria.filter(c=>c.kind==='objective'),
 evidence:evidence.map(e=>({...e,provenance:{...e.provenance,producerId:'untrusted-producer'}})),resultId:'ZF_ENGINE_NEGATIVE_'+run});
assert.equal(refused.outcome,'inconclusive');
const missing=core.verifyTask({...input,criteria:criteria.filter(c=>c.kind==='objective'),evidence:evidence.slice(1),resultId:'ZF_ENGINE_MISSING_'+run});
assert.equal(missing.outcome,'inconclusive');
const report={schema:'enguru.zulfikar.engine-final-existing-donecheck/v1',task,criteria,sourceHead:head,
 donecheckSource:'4181f48df5ea0c060d9aa9f40a471c554b44b53d',githubRunId:Number(run),filePins,
 machineVerification:machine,fullVerification:full,evidence,
 negativeControls:{untrustedProducer:refused.outcome,missingCriterionEvidence:missing.outcome},
 authorityClass:'SAME_GITHUB_EXECUTION_MACHINE_EVIDENCE_NOT_AUTHENTICATED_INDEPENDENT_REVIEW',
 canonicalTaskEnrollment:'HOLD_UNVERIFIED',reviewerAuthority:'HOLD_UNVERIFIED',humanReview:'NOT_SIGNED',
 auditLedger:'NOT_WRITTEN',recordVerifiedFinishInvoked:false,officialVerifiedFinish:'HOLD',
 productAdoptionOrFieldAcceptanceClaimed:false};
fs.writeFileSync(root+'/engine-donecheck.json',JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({taskId:task.id,head,machine:machine.outcome,full:full.outcome,
 machineCriteria:machine.criteria.length,humanCriteriaPending:2,officialVerifiedFinish:'HOLD'}));
