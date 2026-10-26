import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash,generateKeyPairSync,sign} from 'node:crypto';
import {auditObservedLedger,assessSimulation,canonicalJson,gitBlob,inspectProductionLedger,SOURCE_PINS} from '../tools/enguru_management_v69_wp02_wp03_bridge.mjs';
const roles=['source_owner','issuer','independent_verifier'];
const rawEvidence=Buffer.from('evidence: GH69 bounded proof event: candidate only');
const sha= x=>createHash('sha256').update(x).digest('hex');
function ledger() {
  const checks=[];
  for(let b=1;b<=10;b++) for(let c=1;c<=10;c++) {
    const i=(b-1)*10+c;
    checks.push({id:`B${String(b).padStart(2,'0')}-${String(c).padStart(2,'0')}`,
      block:String(b).padStart(2,'0'),name:`Original condition ${i}`,
      state:(i<=29&&i!==9&&i!==10)?'PASS_EVIDENCE':'HOLD',evidence:(i<=29&&i!==9&&i!==10)?`historic-receipt-${i}`:null});
  }
  return {schema:'enguru.100-unit-verified-finish-tracker/v1',checks,total_units:100,verified_units:27,
    remaining_units:73,official_h1_h2_h3:{passed:0,total:12},verified_finish:'HOLD'};
}
function observe(ledgerValue=ledger()) {
  const raw=Buffer.from(JSON.stringify(ledgerValue));
  return auditObservedLedger(raw,{expectedGitBlob:gitBlob(raw)});
}
function fixture() {
  const observation=observe(), now='2026-10-22T16:30:00Z';
  const request={taskId:SOURCE_PINS.taskId,repo:SOURCE_PINS.repo,sourceHead:SOURCE_PINS.ledgerPrHead,
    targetHead:SOURCE_PINS.gh69BaseHead,ledgerBlob:observation.ledgerBlobSha1,
    evidenceSha256:sha(rawEvidence),controlIds:['B01-09','B01-10']};
  const privateKeys={};const keys={},attestations=[];
  for(let i=0;i<roles.length;i++) {
    const role=roles[i],actorId=`test-${role}`,keyId=`test-key-${role}`;
    const kp=generateKeyPairSync('ed25519');
    privateKeys[role]=kp.privateKey;
    keys[keyId]={role,actorId,active:true,allowedRepos:[SOURCE_PINS.repo],publicKeyPem:kp.publicKey.export({type:'spki',format:'pem'})};
    const a={role,actorId,keyId,nonce:`test-${role}-nonce-2026`,signedAt:'2026-10-22T16:29:00Z',
      expiresAt:'2026-10-22T16:45:00Z',...request,signatureBase64:''};
    attestations.push(a);
  }
  const f={request,attestations,trustedPolicy:{trustProvenance:'TEST_ONLY_VERIFIED_EXTERNALLY',keys},
    rawEvidence:Buffer.from(rawEvidence),ledgerAudit:observation,now};
  const resign=()=>{
    for(const a of f.attestations){const {signatureBase64,...body}=a;
      a.signatureBase64=sign(null,Buffer.from(canonicalJson(body)),privateKeys[a.role]).toString('base64');}
  };
  resign();return {f,resign};
}
function expectReady(f){assert.equal(assessSimulation(f).state,'READY_FOR_EXTERNAL_DONECHECK_SIMULATION');
  assert.equal(assessSimulation(f).officialPassAdded,0);
  assert.equal(assessSimulation(f).verifiedFinish,false);}
test('ledger fixture 100 exact rows 27 pass 73 hold',()=>{
 const s=observe();assert.equal(s.state,'PASS_READ_ONLY_LEDGER_OBSERVATION');
 assert.equal(s.verifiedUnits,27);assert.equal(Object.keys(s.eligibleControls).length,73);
});
test('synthetic three valid Ed25519 role grants never mint official finish',()=>expectReady(fixture().f));
test('production CLI holds without canonical trusted registry',async()=>{
 const result=await inspectProductionLedger('/path/that/is/not/the/trusted/ledger');
 assert.equal(result.verifiedFinish,false); assert.match(result.state,/^HOLD_/);
});
// External trust roots are intentionally never populated from signed producer payload.
const cases=[
 ['tampered evidence bytes', f=>f.rawEvidence=Buffer.from('modified'),'HOLD_EVIDENCE'],
 ['digest claim malformed',f=>f.request.evidenceSha256='bad','HOLD_EVIDENCE'],
 ['different task',f=>f.request.taskId='another-task','HOLD_SOURCE_SCOPE'],
 ['different source head',f=>f.request.sourceHead='0'.repeat(40),'HOLD_SOURCE_SCOPE'],
 ['different target head',f=>f.request.targetHead='1'.repeat(40),'HOLD_SOURCE_SCOPE'],
 ['different ledger digest',f=>f.request.ledgerBlob='1'.repeat(40),'HOLD_SOURCE_SCOPE'],
 ['different repo',f=>f.request.repo='attacker/repo','HOLD_SOURCE_SCOPE'],
 ['out of catalog ID',f=>f.request.controlIds=['FAKE-01'],'HOLD_SCOPE'],
 ['already accepted original ID',f=>f.request.controlIds=['B01-01'],'HOLD_SCOPE'],
 ['duplicate control',f=>f.request.controlIds=['B01-09','B01-09'],'HOLD_SCOPE'],
 ['more than ten',f=>f.request.controlIds=Array(11).fill('B01-09'),'HOLD_SCOPE'],
 ['empty controls',f=>f.request.controlIds=[],'HOLD_SCOPE'],
 ['missing issuer',f=>f.attestations=f.attestations.filter(a=>a.role!=='issuer'),'HOLD_TRUST_ROOT'],
 ['duplicate owner',f=>f.attestations[1].role='source_owner','HOLD_AUTHORITY'],
 ['key revoked',f=>f.trustedPolicy.keys['test-key-source_owner'].active=false,'HOLD_AUTHORITY'],
 ['wrong repo permitted',f=>f.trustedPolicy.keys['test-key-source_owner'].allowedRepos=['forged/repo'],'HOLD_AUTHORITY'],
 ['unknown key',f=>f.attestations[0].keyId='unlisted','HOLD_AUTHORITY'],
 ['role swapped',f=>f.attestations[0].role='issuer','HOLD_AUTHORITY'],
 ['expired owner grant',f=>f.attestations[0].expiresAt='2026-10-22T16:29:30Z','HOLD_AUTHORITY'],
 ['future signedAt',f=>f.attestations[0].signedAt='2026-10-22T18:00:00Z','HOLD_AUTHORITY'],
 ['duplicated nonce',f=>f.attestations[1].nonce=f.attestations[0].nonce,'HOLD_AUTHORITY'],
 ['same actor on two roles',f=>{const a=f.attestations[0];f.attestations[1].actorId=a.actorId;
   f.trustedPolicy.keys[f.attestations[1].keyId].actorId=a.actorId;},'HOLD_AUTHORITY'],
 ['signature tamper',f=>f.attestations[0].signatureBase64=Buffer.from('fake').toString('base64'),'HOLD_AUTHORITY'],
 ['signed different evidence digest',f=>f.attestations[0].evidenceSha256='0'.repeat(64),'HOLD_AUTHORITY'],
 ['missing role signing',f=>f.attestations[0].signatureBase64='', 'HOLD_AUTHORITY'],
 ['untrusted registry source',f=>f.trustedPolicy.trustProvenance='FROM_PRODUCER_PACKET','HOLD_TRUST_ROOT'],
 ['out of scope attestation',f=>f.attestations[1].controlIds=['B01-09'],'HOLD_AUTHORITY'],
 ['wrong pinned ledger',f=>f.ledgerAudit={state:'HOLD_LEDGER_PROVENANCE'},'HOLD_LEDGER'],
 ['invalid timestamp',f=>f.now='not-iso','HOLD_TIME'],
];
for(const [name,mutate,want] of cases){
 test(`adversarial ${name}`,()=>{let {f}=fixture();mutate(f);assert.equal(assessSimulation(f).state,want,name);
   assert.equal(assessSimulation(f).officialPassAdded,0);
 });
}
const ledgerCases=[
 ['wrong git blob', x=>{},'HOLD_LEDGER_PROVENANCE',true],
 ['duplicate original ID',x=>x.checks[99].id='B01-01','HOLD_LEDGER_SCHEMA'],
 ['fake pass without receipt',x=>x.checks[29].state='PASS_EVIDENCE','HOLD_LEDGER_SCHEMA'],
 ['false product count',x=>x.verified_units=28,'HOLD_LEDGER_COUNTER'],
 ['false official H1',x=>x.official_h1_h2_h3.passed=1,'HOLD_OFFICIAL_GATES'],
 ['fake Verified Finish',x=>x.verified_finish='PASS','HOLD_OFFICIAL_GATES'],
 ['premature B01-09',x=>{x.checks[8].state='PASS_EVIDENCE';x.checks[8].evidence='claim';x.verified_units=28;x.remaining_units=72},'HOLD_OFFICIAL_GATES'],
 ['hold with leaked approval',x=>x.checks[29].evidence='claim','HOLD_LEDGER_SCHEMA'],
 ['unknown state',x=>x.checks[29].state='PASS','HOLD_LEDGER_SCHEMA'],
 ['wrong total row count',x=>x.checks.pop(),'HOLD_LEDGER_SCHEMA'],
 ['malformed schema',x=>x.schema='candidate','HOLD_LEDGER_SCHEMA'],
 ['wrong remaining',x=>x.remaining_units=72,'HOLD_LEDGER_COUNTER'],
];
for(const [name,mutate,want,unpin] of ledgerCases){
 test(`ledger rejection ${name}`,()=>{
  let x=ledger();mutate(x);const bytes=Buffer.from(JSON.stringify(x));
  let actual=auditObservedLedger(bytes,unpin?undefined:{expectedGitBlob:gitBlob(bytes)});
  assert.equal(actual.state,want,name);assert.equal(actual.officialPassAdded,0);
 });
}