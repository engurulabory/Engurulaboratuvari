/** P06 G2 v16 integration candidate: fail-closed, no official issuer authority. */
import {createHash,createPublicKey,verify} from 'node:crypto';
import {mkdir,open,lstat,realpath} from 'node:fs/promises';
import {getuid} from 'node:process';
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
  const requestedRoot=resolve(ledgerDirectory);
  const root=await realpath(requestedRoot).catch(()=>{throw new HoldError('LEDGER_PATH_UNTRUSTED')});
  const dir=join(root,'enguru-p06-g2-replay-v1');
  // The root must already be provisioned by the authorized local operator.
  // Never recursively create or silently accept a caller-controlled symlink.
  const privateDirectory=async (path)=>{
    let st;try{st=await lstat(path)}catch{throw new HoldError('LEDGER_PATH_UNTRUSTED')}
    need(st.isDirectory()&&!st.isSymbolicLink(),'LEDGER_PATH_NOT_PRIVATE_DIRECTORY');
    need((st.mode&0o077)===0,'LEDGER_DIRECTORY_PERMISSIONS');
    if(typeof getuid==='function')need(st.uid===getuid(),'LEDGER_DIRECTORY_OWNER');
    need((await realpath(path))===path,'LEDGER_SYMLINK_ANCESTOR');
  };
  // Reject a symlink at the supplied ledger leaf, but allow canonical macOS
  // system ancestors such as /var -> /private/var; operate on canonical root.
  const requestedStat=await lstat(requestedRoot).catch(()=>{throw new HoldError('LEDGER_PATH_UNTRUSTED')});
  need(requestedStat.isDirectory()&&!requestedStat.isSymbolicLink(),'LEDGER_ROOT_SYMLINK');
  await privateDirectory(root);
  try{await mkdir(dir,{mode:0o700})}catch(e){if(e?.code!=='EEXIST')throw new HoldError('LEDGER_DIRECTORY_CREATE_FAILED')}
  await privateDirectory(dir);
  const token=sha(Buffer.from(canonicalJson({producerId:authorization.producerId,keyId:authorization.keyId,nonce:authorization.nonce})));
  const slot=join(dir,token);
  // Test-only fail-closed hooks. Never exposed as authorization results.
  const fault=process.env.ENGURU_P06_V16_TEST_FAULT;
  const testFault=(point)=>{if(fault===point)throw new HoldError('INJECTED_'+point+'_HOLD')};
  try{await mkdir(slot,{mode:0o700});}catch(e){if(e?.code==='EEXIST')throw new HoldError('REPLAY_OR_UNCERTAIN_COMMIT');throw new HoldError('LEDGER_RESERVATION_FAILED')}
  await privateDirectory(slot);
  testFault('AFTER_RESERVATION');
  if(fault==='SIGKILL_AFTER_RESERVATION')process.kill(process.pid,'SIGKILL');
  try{
    const f=await open(join(slot,'receipt.json'),'wx',0o600);
    try{testFault('EIO_BEFORE_WRITE');await f.writeFile(canonicalJson({token,authorizationDigest:sha(Buffer.from(canonicalJson(authorization))),state:'RESERVED_CANDIDATE_ONLY'})+'\n');testFault('ENOSPC_BEFORE_FSYNC');await f.sync();testFault('AFTER_FILE_FSYNC')}finally{await f.close()}
    const d=await open(slot,'r');try{await d.sync()}finally{await d.close()}
    const parent=await open(dir,'r');try{testFault('BEFORE_PARENT_FSYNC');await parent.sync()}finally{await parent.close()}
  }catch(e){throw new HoldError('LEDGER_COMMIT_UNCERTAIN_HOLD')}
  return {state:'QUALIFIED_PROVENANCE_CANDIDATE_ONLY',officialIssuer:'HOLD',officialDoneCheck:'HOLD',humanThreshold:'HOLD',verifiedFinish:'HOLD',replayToken:token,policySha256:independentPolicySha256,attestationVerified:candidate.attestationVerified,authorityBindingVerified:true,nextAction:'HUMAN_AUTHORIZED_LIVE_POLICY_AND_DONECHECK_SEPARATE_REVIEW'};
}
