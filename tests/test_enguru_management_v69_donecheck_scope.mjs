import assert from 'node:assert/strict';
import fs from 'node:fs';
import {deriveCandidateTask, runContract, scopedDiff} from '../tools/enguru_management_v69_donecheck_ci.mjs';
const doc=JSON.parse(fs.readFileSync('governance/management-v69/DONECHECK_TASK_REGISTRATION_PREP_V1.json'));
const original=JSON.stringify(doc), head='a'.repeat(40);
const event={pull_request:{number:248,state:'open',merged:false,
 head:{sha:head,ref:'review/management-s02-adoption-20261026',repo:{full_name:'engurulabory/Engurulaboratuvari'}},
 base:{ref:'main',sha:'28db999ba676e4764ae1b644950865674661d0b8',repo:{full_name:'engurulabory/Engurulaboratuvari'}}}};
const scope=deriveCandidateTask(doc,event,head);
assert.equal(scope.doc.donecheck_task.id,'ENGURU_MANAGEMENT_V69_PR_248');
assert.ok(scope.doc.success_criteria.every(c=>c.taskId===scope.doc.donecheck_task.id&&!c.statement.includes('#203')));
assert.equal(scope.doc.official_finish,'HOLD');assert.equal(scope.doc.authorization.cryptographic_human_review,'NOT_GRANTED');
assert.equal(JSON.stringify(doc),original);
let negative=0;
for(const mutate of [e=>e.pull_request.number=203,e=>e.pull_request.head.sha='b'.repeat(40),
 e=>e.pull_request.head.repo.full_name='other/repo',e=>e.pull_request.head.ref='main',
 e=>e.pull_request.base.sha='c'.repeat(40),e=>e.pull_request.merged=true]){
 const e=structuredClone(event);mutate(e);assert.throws(()=>deriveCandidateTask(doc,e,head));negative++;
}
const run={id:10,head_sha:head,event:'pull_request'};
const jobs={jobs:[{id:20,name:'verify',run_id:10,status:'completed',conclusion:'success'}]};
assert.equal(runContract(event.pull_request,run,jobs,head,scope),20);
assert.throws(()=>runContract({...event.pull_request,number:203},run,jobs,head,scope));negative++;
assert.throws(()=>runContract(event.pull_request,{...run,head_sha:'b'.repeat(40)},jobs,head,scope));negative++;
assert.throws(()=>scopedDiff([{filename:'governance/management-v69/DONECHECK_TASK_REGISTRATION_PREP_V1.json'}]));negative++;
assert.throws(()=>scopedDiff([{filename:'tools/enguru_management_v69_donecheck_ci.mjs',status:'renamed',previous_filename:'governance/controller/TASKS.json'}]));negative++;
scopedDiff([{filename:'tests/test_enguru_management_v69_donecheck_scope.mjs',status:'added'}]);
scopedDiff([{filename:'governance/management-v69/OPERATION_OBSERVATION.json',status:'modified'}]);
console.log(JSON.stringify({state:'PASS_CANDIDATE_SCOPE_CONTRACT',negativeControls:negative,originalTaskUnchanged:true,independentAcceptance:'HOLD'}));
