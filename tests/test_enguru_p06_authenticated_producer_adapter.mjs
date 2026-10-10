import test from 'node:test';
import assert from 'node:assert/strict';
import {generateKeyPairSync,sign,createHash} from 'node:crypto';
import {assessProducerAttestation,canonicalJson,HoldError,MAIN,DONECHECK,TASK} from '../tools/enguru_p06_authenticated_producer_adapter.mjs';
const buf=v=>Buffer.from(JSON.stringify(v)+'\n');
const sha=v=>createHash('sha256').update(v).digest('hex');
const now='2026-10-10T14:00:00Z';
const gates={};for(const g of ['HISTORICAL_BRIDGE_NEW_HEAD_FAIL_CLOSED','MERGED_MAIN_GITHUB_CI_3_OF_3','MERGED_MAIN_TWO_EXACT_SOURCE_BLOBS','OSi_BOUNDED_TARGETED_AND_FULL_REGRESSION','PR182_MERGED_EXACT_MAIN_PROVENANCE','PRIOR_V11_EVIDENCE_AND_DONECHECK_V12_ABI','PRODUCER_INPUT_CANDIDATE_UNAUTHORIZED'])gates[g]='PASS';
const tests={};for(const [name,n] of Object.entries({BRIDGE_10:10,EVIDENCE_IO_11:11,P06_POLICY_8:8,FULL_REGRESSION:385}))tests[name]={state:'PASS',returnCode:0,count:n,logSha256:'b'.repeat(64)};
function fixture(){
 const keys=generateKeyPairSync('ed25519');
 const v13={state:'PASS_V13_NEW_MAIN_OSI_RECONCILED_PRODUCER_CANDIDATE_OFFICIAL_HOLD',preservation:'PASS',issues:[],main:{sha:MAIN},officialDoneCheck:'HOLD',humanThreshold:'HOLD',verifiedFinish:'HOLD',gates,tests};
 const artifacts={};
 const evidenceCandidates=Array.from({length:3},(_,n)=>{
   const id=`e-${n}`;const data=Buffer.from('TEST_ARTIFACT_'+id);artifacts[id]=data;
   return {id,taskId:TASK,kind:'test_report',source:'system',content:'UNAUTHORIZED_CANDIDATE_NO_ASSERTION',
    provenance:{schema:'donecheck.evidence-provenance/v1',producerKind:'mac_engineer',producerId:'enguru-p06-UNAUTHORIZED',artifactDigest:'sha256:'+sha(data)}};
 });
 const candidate={canonicalMain:MAIN,donecheckV12Main:DONECHECK,producerAuthenticated:false,officialProducerAuthorized:false,trustedProducerAllowlistGranted:false,machineVerificationIssued:false,officialDoneCheck:'HOLD',humanThreshold:'HOLD',verifiedFinish:'HOLD',evidenceCandidates};
 const candidateBytes=buf(candidate),v13Bytes=buf(v13);
 const v14={state:'PASS_V14_G2_AUTHORITY_GAP_EXACTLY_CLASSIFIED_OFFICIAL_HOLD',preservation:'PASS',issues:[],v13Receipt:{sha256:sha(v13Bytes)},candidateValidation:{sha256:sha(candidateBytes)},authorityDecision:{G2_PRODUCER_AUTHENTICATION:'HOLD_NO_AUTHENTICATED_PRODUCER_RECEIPT',G3_DONECHECK_VERIFYTASK:'HOLD_NOT_INVOKED_NO_TRUSTED_PASS_EVIDENCE'}};
 const v14Bytes=buf(v14);
 const policy={schema:'enguru.p06.producer-authentication-policy/v1',state:'EXTERNALLY_AUTHORIZED_FOR_PROVENANCE_ONLY',scope:'PINNED_P06_G2_MAIN_ONLY',mainSha:MAIN,donecheckSha:DONECHECK,taskId:TASK,producerId:'enguru.p06.test-only',keyId:'TEST_ONLY',publicKeyPem:keys.publicKey.export({format:'pem',type:'spki'}),expiresAt:'2026-10-12T14:00:00Z',autoDoneCheckPass:false,autoHumanDecision:false,autoVerifiedFinish:false};
 const payload={schema:'enguru.p06.producer-binding/v1',mainSha:MAIN,donecheckSha:DONECHECK,taskId:TASK,producerId:policy.producerId,v13Sha256:sha(v13Bytes),v14Sha256:sha(v14Bytes),candidateSha256:sha(candidateBytes),artifacts:evidenceCandidates.map(e=>({id:e.id,artifactDigest:e.provenance.artifactDigest})).sort((a,b)=>a.id.localeCompare(b.id))};
 const attestation={schema:'enguru.p06.producer-ed25519-attestation/v1',producerId:policy.producerId,keyId:policy.keyId,signedAt:now,payload,signatureBase64:sign(null,Buffer.from(canonicalJson({schema:'enguru.p06.producer-ed25519-attestation/v1',signedAt:now,payload})),keys.privateKey).toString('base64')};
 const policyBytes=buf(policy);return {v13Bytes,v14Bytes,candidateBytes,policyBytes,expectedPolicySha256:sha(policyBytes),attestation,artifactBytesById:artifacts,now};
}
const reject=(name,mutate)=>test(name,()=>{const x=fixture();mutate(x);assert.throws(()=>assessProducerAttestation(x),HoldError);});
test('synthetic verified signature gives PROPOSAL only, no DoneCheck/Human/Verified Finish',()=>{const v=assessProducerAttestation(fixture());assert.equal(v.attestationVerified,true);assert.equal(v.state,'AUTHENTICATED_PROVENANCE_CANDIDATE_ONLY_OFFICIAL_HOLD');assert.equal(v.officialIssuer,'HOLD');assert.equal(v.officialDoneCheck,'HOLD');assert.equal(v.verifiedFinish,'HOLD');assert.equal(v.trustedProducerAllowlistGranted,false);assert.equal(v.assertionMinted,false);});
reject('reject absent independently pinned policy hash',x=>{x.expectedPolicySha256=undefined});
reject('reject modified policy',x=>{x.policyBytes=Buffer.concat([x.policyBytes,Buffer.from(' ')])});
reject('reject unauthorized policy',x=>{const p=JSON.parse(x.policyBytes);p.state='PENDING';x.policyBytes=buf(p);x.expectedPolicySha256=sha(x.policyBytes)});
reject('reject wrong MAIN',x=>{const p=JSON.parse(x.policyBytes);p.mainSha='0'.repeat(40);x.policyBytes=buf(p);x.expectedPolicySha256=sha(x.policyBytes)});
reject('reject signature tampering',x=>{x.attestation.signatureBase64=Buffer.alloc(64).toString('base64')});
reject('reject changed signed payload',x=>{x.attestation.payload.mainSha='0'.repeat(40)});
reject('reject wrong signer key identity',x=>{x.attestation.keyId='FORGED'});
reject('reject expired policy',x=>{x.now='2026-10-15T14:00:00Z'});
reject('reject missing artifact',x=>{delete x.artifactBytesById['e-0']});
reject('reject tampered artifact bytes',x=>{x.artifactBytesById['e-0']=Buffer.from('TAMPER')});
reject('reject forged DoneCheck assertion',x=>{const c=JSON.parse(x.candidateBytes);c.evidenceCandidates[0].content='[DONECHECK:PASS] fabricated';x.candidateBytes=buf(c)});
reject('reject forged pre-existing issuer PASS',x=>{const c=JSON.parse(x.candidateBytes);c.officialProducerAuthorized=true;x.candidateBytes=buf(c)});
reject('reject V13 false DoneCheck PASS',x=>{const v=JSON.parse(x.v13Bytes);v.officialDoneCheck='PASS';x.v13Bytes=buf(v)});
reject('reject V14 forged auth PASS',x=>{const v=JSON.parse(x.v14Bytes);v.authorityDecision.G2_PRODUCER_AUTHENTICATION='PASS';x.v14Bytes=buf(v)});
reject('reject policy privilege escalation',x=>{const p=JSON.parse(x.policyBytes);p.autoVerifiedFinish=true;x.policyBytes=buf(p);x.expectedPolicySha256=sha(x.policyBytes)});

reject('reject changed unsigned-looking attestation timestamp',x=>{x.attestation.signedAt='2026-10-10T13:59:59Z'});
