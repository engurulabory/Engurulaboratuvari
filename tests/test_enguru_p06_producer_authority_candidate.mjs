import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,rm,readFile,mkdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash,generateKeyPairSync,sign} from 'node:crypto';
import {qualifyProducer} from '../tools/enguru_p06_producer_authority_candidate.mjs';
import {MAIN,DONECHECK,TASK,canonicalJson,HoldError} from '../tools/enguru_p06_authenticated_producer_adapter.mjs';
const buf=v=>Buffer.from(JSON.stringify(v)+'\n');
const sha=x=>createHash('sha256').update(x).digest('hex');
const gates=Object.fromEntries(['HISTORICAL_BRIDGE_NEW_HEAD_FAIL_CLOSED','MERGED_MAIN_GITHUB_CI_3_OF_3','MERGED_MAIN_TWO_EXACT_SOURCE_BLOBS','OSi_BOUNDED_TARGETED_AND_FULL_REGRESSION','PR182_MERGED_EXACT_MAIN_PROVENANCE','PRIOR_V11_EVIDENCE_AND_DONECHECK_V12_ABI','PRODUCER_INPUT_CANDIDATE_UNAUTHORIZED'].map(x=>[x,'PASS']));
const ts=Object.fromEntries(Object.entries({BRIDGE_10:10,EVIDENCE_IO_11:11,P06_POLICY_8:8,FULL_REGRESSION:385}).map(([k,count])=>[k,{state:'PASS',returnCode:0,count,logSha256:'b'.repeat(64)}]));
function fixture(ledgerDirectory){
 const keys=generateKeyPairSync('ed25519'),now='2026-10-10T14:00:00Z';
 const v13={state:'PASS_V13_NEW_MAIN_OSI_RECONCILED_PRODUCER_CANDIDATE_OFFICIAL_HOLD',preservation:'PASS',issues:[],main:{sha:MAIN},officialDoneCheck:'HOLD',humanThreshold:'HOLD',verifiedFinish:'HOLD',gates,tests:ts};
 const artifactBytesById={},evidenceCandidates=Array.from({length:3},(_,i)=>{const id=`e-${i}`,raw=Buffer.from(id);artifactBytesById[id]=raw;return{id,taskId:TASK,kind:'test_report',source:'system',content:'UNAUTHORIZED_CANDIDATE_NO_ASSERTION',provenance:{schema:'donecheck.evidence-provenance/v1',producerKind:'mac_engineer',producerId:'enguru-p06-UNAUTHORIZED',artifactDigest:'sha256:'+sha(raw)}}});
 const candidate={canonicalMain:MAIN,donecheckV12Main:DONECHECK,producerAuthenticated:false,officialProducerAuthorized:false,trustedProducerAllowlistGranted:false,machineVerificationIssued:false,officialDoneCheck:'HOLD',humanThreshold:'HOLD',verifiedFinish:'HOLD',evidenceCandidates};
 const v13Bytes=buf(v13),candidateBytes=buf(candidate),v14Bytes=buf({state:'PASS_V14_G2_AUTHORITY_GAP_EXACTLY_CLASSIFIED_OFFICIAL_HOLD',preservation:'PASS',issues:[],v13Receipt:{sha256:sha(v13Bytes)},candidateValidation:{sha256:sha(candidateBytes)},authorityDecision:{G2_PRODUCER_AUTHENTICATION:'HOLD_NO_AUTHENTICATED_PRODUCER_RECEIPT',G3_DONECHECK_VERIFYTASK:'HOLD_NOT_INVOKED_NO_TRUSTED_PASS_EVIDENCE'}});
 const policy={schema:'enguru.p06.producer-authentication-policy/v1',state:'EXTERNALLY_AUTHORIZED_FOR_PROVENANCE_ONLY',scope:'PINNED_P06_G2_MAIN_ONLY',mainSha:MAIN,donecheckSha:DONECHECK,taskId:TASK,producerId:'enguru.p06.test-only',keyId:'TEST_ONLY',publicKeyPem:keys.publicKey.export({format:'pem',type:'spki'}),expiresAt:'2026-10-12T14:00:00Z',autoDoneCheckPass:false,autoHumanDecision:false,autoVerifiedFinish:false};
 const policyBytes=buf(policy),expectedPolicySha256=sha(policyBytes);
 const payload={schema:'enguru.p06.producer-binding/v1',mainSha:MAIN,donecheckSha:DONECHECK,taskId:TASK,producerId:policy.producerId,v13Sha256:sha(v13Bytes),v14Sha256:sha(v14Bytes),candidateSha256:sha(candidateBytes),artifacts:evidenceCandidates.map(e=>({id:e.id,artifactDigest:e.provenance.artifactDigest})).sort((a,b)=>a.id.localeCompare(b.id))};
 const attestation={schema:'enguru.p06.producer-ed25519-attestation/v1',producerId:policy.producerId,keyId:policy.keyId,signedAt:now,payload,signatureBase64:sign(null,Buffer.from(canonicalJson({schema:'enguru.p06.producer-ed25519-attestation/v1',signedAt:now,payload})),keys.privateKey).toString('base64')};
 const assessment={v13Bytes,v14Bytes,candidateBytes,policyBytes,expectedPolicySha256,attestation,artifactBytesById,now};
 const authorization={schema:'enguru.p06.producer-authority-binding/v16',mainSha:MAIN,donecheckSha:DONECHECK,producerId:policy.producerId,keyId:policy.keyId,policySha256:expectedPolicySha256,attestationSha256:sha(Buffer.from(canonicalJson(attestation))),executionId:'test-execution-123',nonce:'nonce-0123456789abcdef',signedAt:now};
 const authorizationSignatureBase64=sign(null,Buffer.from(canonicalJson(authorization)),keys.privateKey).toString('base64');
 return {assessment,authorization,authorizationSignatureBase64,independentPolicySha256:expectedPolicySha256,ledgerDirectory};
}
async function setup(){const dir=await mkdtemp(join(tmpdir(),'enguru-g2-v16-'));return{dir,x:fixture(dir)}}
const hold=async f=>assert.rejects(f,HoldError);
test('signed synthetic qualification candidate-only and durable replay rejection',async()=>{const {dir,x}=await setup();try{const r=await qualifyProducer(x);assert.equal(r.officialIssuer,'HOLD');assert.equal(r.officialDoneCheck,'HOLD');assert.equal(r.verifiedFinish,'HOLD');await hold(()=>qualifyProducer(x))}finally{await rm(dir,{recursive:true,force:true})}});
test('concurrent duplicate nonce only one reservation',async()=>{const {dir,x}=await setup();try{const results=await Promise.allSettled([qualifyProducer(x),qualifyProducer(x)]);assert.equal(results.filter(r=>r.status==='fulfilled').length,1)}finally{await rm(dir,{recursive:true,force:true})}});
test('incorrect external policy pin holds',async()=>{const {dir,x}=await setup();try{x.independentPolicySha256='0'.repeat(64);await hold(()=>qualifyProducer(x))}finally{await rm(dir,{recursive:true,force:true})}});
test('wrong source scope holds',async()=>{const {dir,x}=await setup();try{x.authorization.mainSha='0'.repeat(40);await hold(()=>qualifyProducer(x))}finally{await rm(dir,{recursive:true,force:true})}});
test('wrong signing key holds',async()=>{const {dir,x}=await setup();try{x.authorizationSignatureBase64=Buffer.alloc(64).toString('base64');await hold(()=>qualifyProducer(x))}finally{await rm(dir,{recursive:true,force:true})}});
test('missing durable ledger holds',async()=>{const {dir,x}=await setup();try{delete x.ledgerDirectory;await hold(()=>qualifyProducer(x))}finally{await rm(dir,{recursive:true,force:true})}});
test('changed nonce without re-signing holds',async()=>{const {dir,x}=await setup();try{x.authorization.nonce='nonce-9876543210abcdef';await hold(()=>qualifyProducer(x))}finally{await rm(dir,{recursive:true,force:true})}});
test('missing artifact holds before ledger reservation',async()=>{const {dir,x}=await setup();try{delete x.assessment.artifactBytesById['e-0'];await hold(()=>qualifyProducer(x))}finally{await rm(dir,{recursive:true,force:true})}});
test('restart/reinstantiation with same durable root rejects replay',async()=>{const {dir,x}=await setup();try{await qualifyProducer(x);const again=fixture(dir);again.assessment=x.assessment;again.authorization=x.authorization;again.authorizationSignatureBase64=x.authorizationSignatureBase64;again.independentPolicySha256=x.independentPolicySha256;await hold(()=>qualifyProducer(again))}finally{await rm(dir,{recursive:true,force:true})}});
test('pre-created replay reservation with missing receipt fails closed',async()=>{const {dir,x}=await setup();try{const token=sha(Buffer.from(canonicalJson({producerId:x.authorization.producerId,keyId:x.authorization.keyId,nonce:x.authorization.nonce})));await mkdir(join(dir,'enguru-p06-g2-replay-v1',token),{recursive:true});await hold(()=>qualifyProducer(x))}finally{await rm(dir,{recursive:true,force:true})}});

import {spawn,spawnSync} from 'node:child_process';
import {symlink,chmod} from 'node:fs/promises';
const CHILD=new URL('./p06_v16_child_process.mjs',import.meta.url);
function child(x){return new Promise(resolve=>{const p=spawn(process.execPath,[CHILD.pathname],{stdio:['pipe','pipe','pipe']});let out='';p.stdout.on('data',d=>out+=d);p.on('close',code=>resolve({code,out}));p.stdin.end(JSON.stringify(x))})}
test('true OS process restart rejects persisted replay',async()=>{const {dir,x}=await setup();try{const first=await child(x);assert.equal(first.code,0);const restart=await child(x);assert.equal(restart.code,41)}finally{await rm(dir,{recursive:true,force:true})}});
test('two independent OS processes race, exactly one qualifies',async()=>{const {dir,x}=await setup();try{const a=await Promise.all([child(x),child(x)]);assert.deepEqual(a.map(r=>r.code).sort((a,b)=>a-b),[0,41])}finally{await rm(dir,{recursive:true,force:true})}});
test('symlink ledger root holds',async()=>{const {dir,x}=await setup();try{const link=dir+'-link';await symlink(dir,link);x.ledgerDirectory=link;await hold(()=>qualifyProducer(x));await rm(link,{force:true})}finally{await rm(dir,{recursive:true,force:true})}});
test('world-readable existing ledger root holds',async()=>{const {dir,x}=await setup();try{await chmod(dir,0o755);await hold(()=>qualifyProducer(x))}finally{await chmod(dir,0o700);await rm(dir,{recursive:true,force:true})}});
test('injected unavailable root holds without granting authority',async()=>{const {dir,x}=await setup();try{x.ledgerDirectory=join(dir,'missing-private-ledger');await hold(()=>qualifyProducer(x))}finally{await rm(dir,{recursive:true,force:true})}});
