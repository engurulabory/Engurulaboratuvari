import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,rm} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {auditObservedLedger,gitBlob,SOURCE_PINS} from '../tools/enguru_management_v69_wp02_wp03_bridge.mjs';
import {DisposableJournal,executeObservedPilot} from '../tools/enguru_management_v69_wp04_wp05_runtime.mjs';
import {inspectHandoff,inspectDoneCheck,inspectRealBinding} from '../tools/enguru_management_v69_wp02_wp05_source_binding.mjs';
const roots=[],actorIds={manager:'manager-fixture-1',executor:'executor-fixture-2',verifier:'verifier-fixture-3'};
async function setup(){
 const root=await mkdtemp(join(tmpdir(),'gh69-binding-test-'));roots.push(root);
 const rows=[];for(let b=1;b<=10;b++)for(let c=1;c<=10;c++){
  const n=(b-1)*10+c,pass=n<=29&&n!==9&&n!==10;
  rows.push({id:'B'+String(b).padStart(2,'0')+'-'+String(c).padStart(2,'0'),
    name:'fixture',state:pass?'PASS_EVIDENCE':'HOLD',evidence:pass?'fixture':null});
 }
 const raw=Buffer.from(JSON.stringify({schema:'enguru.100-unit-verified-finish-tracker/v1',
  checks:rows,total_units:100,verified_units:27,remaining_units:73,
  official_h1_h2_h3:{passed:0,total:12},verified_finish:'HOLD'}));
 const observation=auditObservedLedger(raw,{expectedGitBlob:gitBlob(raw)});
 await executeObservedPilot({observed:observation,root,actorIds});
 const journal=await new DisposableJournal(root).read();
 return {root,journal,observation:{...observation,ledgerBlobSha1:SOURCE_PINS.ledgerGitBlob}};
}
test('candidate observation is real structure but cannot mint accepted finish',async()=>{
 const f=await setup();const r=inspectHandoff(f.observation,f.journal);
 assert.equal(r.state,'PASS_BOUNDED_READONLY_HANDOFF');assert.equal(r.officialPassAdded,0);
 assert.equal(r.verifiedFinish,false);assert.equal(r.donecheckRuntimeInvoked,false);
});
const mutations={
 absent_observation:x=>x.observation=null,
 false_observation:x=>x.observation.state='PASS_OFFICIAL',
 wrong_source:x=>x.observation.ledgerBlobSha1='0'.repeat(40),
 missing_chain:x=>x.journal.records=[],
 partial_chain:x=>x.journal.sequence=6,
 fake_end:x=>x.journal.state='VERIFIED_FINISH',
 wrong_type:x=>x.journal.records[2].type='verified_finish',
 wrong_event_id:x=>x.journal.records[1].eventId='unrelated',
 wrong_task:x=>x.journal.records[6].payload.taskId='foreign',
 duplicate_actor:x=>x.journal.records[4].actor.id=x.journal.records[2].actor.id,
 manager_mismatch:x=>x.journal.records[5].actor.id='foreign',
 forged_role:x=>x.journal.records[4].actor.role='issuer',
 wrong_repo:x=>x.journal.records[0].payload.repo='foreign/repo',
 wrong_head:x=>x.journal.records[0].payload.ledgerPrHead='0'.repeat(40),
 wrong_blob:x=>x.journal.records[0].payload.ledgerBlob='0'.repeat(40),
 duplicate_controls:x=>x.journal.records[0].payload.controlIds=['B01-09','B01-09'],
 unknown_control:x=>x.journal.records[0].payload.controlIds=['B01-10'],
 wrong_executor:x=>x.journal.records[1].payload.assignedTo='elsewhere',
 wrong_digest:x=>x.journal.records[2].payload.digest='0'.repeat(64),
 wrong_evidence:x=>x.journal.records[3].payload.digest='0'.repeat(64),
 verifier_false_pass:x=>x.journal.records[4].payload.verdict='PASS_OFFICIAL',
 verifier_wrong_evidence:x=>x.journal.records[4].payload.evidenceDigest='0'.repeat(64),
 manager_false_pass:x=>x.journal.records[5].payload.verdict='PASS_OFFICIAL',
 manager_wrong_evidence:x=>x.journal.records[5].payload.reviewedEvidence='0'.repeat(64),
 final_false_pass:x=>x.journal.records[6].payload.state='VERIFIED_FINISH',
 official_count_forged:x=>x.journal.records[6].payload.officialPassAdded=1
};
for(const [name,mutate] of Object.entries(mutations)){
 test('fail-closed: '+name,async()=>{
  const f=await setup(),x={observation:structuredClone(f.observation),journal:structuredClone(f.journal)};
  mutate(x);const r=inspectHandoff(x.observation,x.journal);
  assert.equal(r.state,'HOLD');assert.equal(r.verifiedFinish,false);assert.equal(r.officialPassAdded,0);
 });
}
test('untrusted directory cannot serve as DoneCheck source root',async()=>{
 const f=await setup();const r=await inspectDoneCheck(f.root);
 assert.equal(r.state,'HOLD');assert.equal(r.verifiedFinish,false);
});
test('missing real ledger yields HOLD without side effects',async()=>{
 const f=await setup();const r=await inspectRealBinding({
  ledgerFile:'/tmp/missing-gh69-pr191-ledger-file',journalRoot:f.root,donecheckRoot:f.root});
 assert.equal(r.state,'HOLD');assert.equal(r.officialPassAdded,0);
});
test.after(async()=>{await Promise.all(roots.map(r=>rm(r,{recursive:true,force:true})));});
