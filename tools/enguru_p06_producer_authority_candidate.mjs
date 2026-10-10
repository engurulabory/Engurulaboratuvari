/** P06 G2 v16 integration candidate: fail-closed, no official issuer authority. */
import {createHash,createPublicKey,verify} from 'node:crypto';
import {mkdir,open} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {assessProducerAttestation,canonicalJson,HoldError} from './enguru_p06_authenticated_producer_adapter.mjs';
const need=(ok,why)=>{if(!ok)throw new HoldError(why)};
const sha=x=>createHash('sha256').update(x).digest('hex');
const isHex=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
/** Caller must obtain expected policy digest from independent approved source, not policy bytes. */
export async function qualifyProducer(input){
  need(input&&typeof input==='object'&&!Array.isArray(input),'INPUT_REQUIRED');
  const {assessment,authorization,authorizationSignatureBase64,independentPolicySha256,ledgerDirectory}=input;
  need(assessment&&typeof assessment==='object','ASSESSMENT_REQUIRED');
  need(isHex(independentPolicySha256)&&assessment.expectedPolicySha256===independentPolicySha256,'INDEPENDENT_TRUST_PIN_REQUIRED');
  const candidate=assessProducerAttestation(assessment);
  const policy=JSON.parse(assessment.policyBytes.toString('utf8'));
  need(authorization&&typeof authorization==='object'&&!Array.isArray(authorization),'AUTHORIZATION_REQUIRED');
  need(authorization.schema==='enguru.p06.producer-authority-binding/v16','AUTHORIZATION_SCHEMA');
  need(authorization.mainSha===candidate.mainSha && authorization.donecheckSha===candidate.donecheckSha,'SOURCE_SCOPE');
  need(authorization.producerId===candidate.producerId && authorization.keyId===policy.keyId,'IDENTITY_SCOPE');
  need(authorization.policySha256===independentPolicySha256,'POLICY_SCOPE');
  need(authorization.attestationSha256===sha(Buffer.from(canonicalJson(assessment.attestation))),'ATTESTATION_SCOPE');
  need(typeof authorization.executionId==='string'&&/^[A-Za-z0-9._:-]{8,128}$/.test(authorization.executionId),'EXECUTION_ID');
  need(typeof authorization.nonce==='string'&&/^[A-Za-z0-9_-]{16,128}$/.test(authorization.nonce),'NONCE');
  need(authorization.signedAt===assessment.attestation.signedAt,'TIMESTAMP_SCOPE');
  need(typeof authorizationSignatureBase64==='string' && /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(authorizationSignatureBase64),'SIGNATURE_FORMAT');
  const sig=Buffer.from(authorizationSignatureBase64,'base64');need(sig.length===64,'SIGNATURE_LENGTH');
  let ok=false;try{ok=verify(null,Buffer.from(canonicalJson(authorization)),createPublicKey(policy.publicKeyPem),sig)}catch{ok=false}
  need(ok,'AUTHORITY_BINDING_SIGNATURE_INVALID');
  need(typeof ledgerDirectory==='string'&&ledgerDirectory.length>0,'DURABLE_LEDGER_REQUIRED');
  const root=resolve(ledgerDirectory); const dir=join(root,'enguru-p06-g2-replay-v1');
  await mkdir(dir,{recursive:true,mode:0o700});
  const token=sha(Buffer.from(canonicalJson({producerId:authorization.producerId,keyId:authorization.keyId,nonce:authorization.nonce})));
  const slot=join(dir,token);
  try{await mkdir(slot,{mode:0o700});}catch(e){if(e?.code==='EEXIST')throw new HoldError('REPLAY_OR_UNCERTAIN_COMMIT');throw e}
  try{
    const f=await open(join(slot,'receipt.json'),'wx',0o600);
    try{await f.writeFile(canonicalJson({token,authorizationDigest:sha(Buffer.from(canonicalJson(authorization))),state:'RESERVED_CANDIDATE_ONLY'})+'\n');await f.sync()}finally{await f.close()}
    const d=await open(slot,'r');try{await d.sync()}finally{await d.close()}
    const parent=await open(dir,'r');try{await parent.sync()}finally{await parent.close()}
  }catch(e){throw new HoldError('LEDGER_COMMIT_UNCERTAIN_HOLD')}
  return {state:'QUALIFIED_PROVENANCE_CANDIDATE_ONLY',officialIssuer:'HOLD',officialDoneCheck:'HOLD',humanThreshold:'HOLD',verifiedFinish:'HOLD',replayToken:token,policySha256:independentPolicySha256,attestationVerified:candidate.attestationVerified,authorityBindingVerified:true,nextAction:'HUMAN_AUTHORIZED_LIVE_POLICY_AND_DONECHECK_SEPARATE_REVIEW'};
}
