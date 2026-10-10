/**
 * ENGÜRÜ P06 G2 — PROPOSAL-ONLY authenticated producer adapter (v15).
 * No credential creation, policy enrollment, filesystem writes, verifyTask,
 * DoneCheck authority, Human Threshold, or Verified Finish.
 * The policy hash must be pinned by an INDEPENDENT authorized integration.
 */
import {createHash, createPublicKey, verify as verifySignature} from 'node:crypto';

export const MAIN = '20762d0b22278250e4085b14d969c7da6bd86a9d';
export const DONECHECK = '8b90a8fc93453dd8a84994195d28d14b15e261cb';
export const TASK = 'ENGURU_P06_G2_MERGED_MAIN';
const EXPECTED_GATES = [
  'HISTORICAL_BRIDGE_NEW_HEAD_FAIL_CLOSED',
  'MERGED_MAIN_GITHUB_CI_3_OF_3',
  'MERGED_MAIN_TWO_EXACT_SOURCE_BLOBS',
  'OSi_BOUNDED_TARGETED_AND_FULL_REGRESSION',
  'PR182_MERGED_EXACT_MAIN_PROVENANCE',
  'PRIOR_V11_EVIDENCE_AND_DONECHECK_V12_ABI',
  'PRODUCER_INPUT_CANDIDATE_UNAUTHORIZED',
];
const EXPECTED_TESTS = {BRIDGE_10:10, EVIDENCE_IO_11:11, P06_POLICY_8:8, FULL_REGRESSION:385};
export class HoldError extends Error {constructor(reason){super(reason);this.name='HoldError';}}
function need(ok,reason){if(!ok)throw new HoldError(reason);}
function sha(raw){return createHash('sha256').update(raw).digest('hex');}
function parseRaw(raw,desc){
  need(Buffer.isBuffer(raw), desc+'_RAW_BYTES_REQUIRED');
  try {const a=JSON.parse(raw.toString('utf8'));need(a&&typeof a==='object'&&!Array.isArray(a),desc+'_JSON_OBJECT_REQUIRED');return a;}
  catch(e){if(e instanceof HoldError)throw e;throw new HoldError(desc+'_INVALID_JSON');}
}
function normalize(v){
  if(v===null||typeof v==='string'||typeof v==='boolean')return v;
  if(typeof v==='number'){need(Number.isFinite(v),'NONFINITE_NUMBER');return v;}
  if(Array.isArray(v))return v.map(normalize);
  need(v&&typeof v==='object','UNSUPPORTED_CANONICAL_VALUE');
  return Object.fromEntries(Object.keys(v).sort().filter(k=>v[k]!==undefined).map(k=>[k,normalize(v[k])]));
}
export function canonicalJson(v){return JSON.stringify(normalize(v));}
const iso=/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/;
function utcTime(v){return typeof v==='string'&&iso.test(v)&&Number.isFinite(Date.parse(v));}
function validateMachine(v13,v14,candidate,candidateSha,v13Sha){
  need(v13.state==='PASS_V13_NEW_MAIN_OSI_RECONCILED_PRODUCER_CANDIDATE_OFFICIAL_HOLD' && v13.preservation==='PASS' && Array.isArray(v13.issues)&&v13.issues.length===0,'V13_NOT_MACHINE_PASS');
  need(v13.main?.sha===MAIN && v13.officialDoneCheck==='HOLD' && v13.humanThreshold==='HOLD' && v13.verifiedFinish==='HOLD','V13_AUTHORITY_OR_HEAD_DRIFT');
  for(const gate of EXPECTED_GATES)need(v13.gates?.[gate]==='PASS','V13_GATE_MISSING_'+gate);
  const tests=v13.tests||{};
  need(Object.keys(tests).length===4,'V13_TEST_COUNT_MISMATCH');
  for(const [n,count] of Object.entries(EXPECTED_TESTS)){
    const t=tests[n];need(t?.state==='PASS' && t.returnCode===0 && t.count>=count && /^[a-f0-9]{64}$/.test(t.logSha256||''),'V13_TEST_PROOF_MISSING_'+n);
  }
  need(v14.state==='PASS_V14_G2_AUTHORITY_GAP_EXACTLY_CLASSIFIED_OFFICIAL_HOLD' && v14.preservation==='PASS' && Array.isArray(v14.issues)&&v14.issues.length===0,'V14_NOT_AUTHORITY_DIAGNOSIS_PASS');
  need(v14.v13Receipt?.sha256===v13Sha && v14.candidateValidation?.sha256===candidateSha,'V14_RECEIPT_SHA_MISMATCH');
  need(v14.authorityDecision?.G2_PRODUCER_AUTHENTICATION==='HOLD_NO_AUTHENTICATED_PRODUCER_RECEIPT' && v14.authorityDecision?.G3_DONECHECK_VERIFYTASK==='HOLD_NOT_INVOKED_NO_TRUSTED_PASS_EVIDENCE','V14_AUTHORITY_HOLD_DRIFT');
  need(candidate.canonicalMain===MAIN && candidate.donecheckV12Main===DONECHECK && candidate.producerAuthenticated===false && candidate.officialProducerAuthorized===false && candidate.trustedProducerAllowlistGranted===false && candidate.machineVerificationIssued===false && candidate.officialDoneCheck==='HOLD' && candidate.humanThreshold==='HOLD' && candidate.verifiedFinish==='HOLD','UNAUTHORIZED_CANDIDATE_ALTERED');
  need(Array.isArray(candidate.evidenceCandidates) && candidate.evidenceCandidates.length===3,'EXACT_THREE_EVIDENCE_ARTIFACTS_REQUIRED');
}

/**
 * @param {object} args
 * @param {Buffer} args.v13Bytes - original unmodified V13 final-receipt.json
 * @param {Buffer} args.v14Bytes - original unmodified V14 final-receipt.json
 * @param {Buffer} args.candidateBytes - V13 UNAUTHORIZED producer candidate JSON
 * @param {Buffer} args.policyBytes - externally authorized producer policy, JSON bytes
 * @param {string} args.expectedPolicySha256 - independently pinned policy digest (not read from policy)
 * @param {object} args.attestation - Ed25519 producer attestation from external authorized signer
 * @param {Object<string,Buffer>} args.artifactBytesById - exact 3 raw V13 artifact contents
 * @param {string} args.now - caller's trusted UTC observation time
 */
export function assessProducerAttestation(args){
  need(args!==null && typeof args==='object' && !Array.isArray(args),'ASSESSMENT_ARGS_OBJECT_REQUIRED');
  const {v13Bytes,v14Bytes,candidateBytes,policyBytes,expectedPolicySha256,attestation,artifactBytesById,now}=args;
  need(typeof expectedPolicySha256==='string'&&/^[a-f0-9]{64}$/.test(expectedPolicySha256),'INDEPENDENT_POLICY_PIN_REQUIRED');
  need(utcTime(now),'TRUSTED_UTC_NOW_REQUIRED');
  need(Buffer.isBuffer(policyBytes)&&sha(policyBytes)===expectedPolicySha256,'POLICY_SHA_PIN_MISMATCH');
  const v13=parseRaw(v13Bytes,'V13'),v14=parseRaw(v14Bytes,'V14');
  const candidate=parseRaw(candidateBytes,'CANDIDATE'),policy=parseRaw(policyBytes,'POLICY');
  const v13Sha=sha(v13Bytes),v14Sha=sha(v14Bytes),candidateSha=sha(candidateBytes);
  validateMachine(v13,v14,candidate,candidateSha,v13Sha);
  need(policy.schema==='enguru.p06.producer-authentication-policy/v1' && policy.state==='EXTERNALLY_AUTHORIZED_FOR_PROVENANCE_ONLY' && policy.scope==='PINNED_P06_G2_MAIN_ONLY' && policy.mainSha===MAIN && policy.donecheckSha===DONECHECK,'PRODUCER_POLICY_NOT_AUTHORIZED_OR_WRONG_SCOPE');
  need(policy.autoDoneCheckPass===false && policy.autoHumanDecision===false && policy.autoVerifiedFinish===false,'PRODUCER_POLICY_PRIVILEGE_ESCALATION');
  need(policy.taskId===TASK && typeof policy.producerId==='string'&&policy.producerId.length>0&&!policy.producerId.includes('UNAUTHORIZED') && typeof policy.keyId==='string'&&policy.keyId.length>0 && typeof policy.publicKeyPem==='string','PRODUCER_KEY_OR_ID_MISSING');
  need(utcTime(policy.expiresAt) && Date.parse(now)<Date.parse(policy.expiresAt),'PRODUCER_POLICY_EXPIRED');
  need(attestation?.schema==='enguru.p06.producer-ed25519-attestation/v1' && attestation.producerId===policy.producerId && attestation.keyId===policy.keyId && utcTime(attestation.signedAt),'PRODUCER_ATTESTATION_IDENTITY_MISMATCH');
  const skew=Date.parse(now)-Date.parse(attestation.signedAt);
  need(skew>=-300_000 && skew<=86_400_000,'PRODUCER_ATTESTATION_NOT_FRESH');
  const items=candidate.evidenceCandidates;
  need(artifactBytesById!==null && typeof artifactBytesById==='object' && !Array.isArray(artifactBytesById),'ARTIFACT_MAP_OBJECT_REQUIRED');
  need(Object.keys(artifactBytesById).length===3,'EXACT_THREE_RAW_ARTIFACTS_REQUIRED');
  const artifacts=[];
  const seen=new Set();
  for(const item of items){
    need(item!==null && typeof item==='object' && !Array.isArray(item),'EVIDENCE_ITEM_OBJECT_REQUIRED');
    need(typeof item.id==='string'&&!seen.has(item.id),'EVIDENCE_ID_DUPLICATE');seen.add(item.id);
    need(item.taskId===TASK && item.kind==='test_report' && item.source==='system' && typeof item.content==='string'&&!item.content.trim().toUpperCase().startsWith('[DONECHECK:'),'CANDIDATE_ASSERTION_OR_SCOPE_FORGERY');
    need(item.provenance?.schema==='donecheck.evidence-provenance/v1' && item.provenance.producerKind==='mac_engineer' && typeof item.provenance.producerId==='string' && item.provenance.producerId.includes('UNAUTHORIZED'),'SOURCE_CANDIDATE_NOT_UNAUTHORIZED');
    const raw=artifactBytesById[item.id];
    need(Buffer.isBuffer(raw),'ARTIFACT_BYTES_MISSING_'+item.id);
    need(item.provenance.artifactDigest==='sha256:'+sha(raw),'ARTIFACT_BYTES_SHA_MISMATCH_'+item.id);
    artifacts.push({id:item.id,artifactDigest:item.provenance.artifactDigest});
  }
  const payload={schema:'enguru.p06.producer-binding/v1',mainSha:MAIN,donecheckSha:DONECHECK,
    taskId:TASK,producerId:policy.producerId,v13Sha256:v13Sha,v14Sha256:v14Sha,
    candidateSha256:candidateSha,artifacts:artifacts.sort((a,b)=>a.id.localeCompare(b.id))};
  need(attestation.payload!==null && typeof attestation.payload==='object' && !Array.isArray(attestation.payload),'ATTESTATION_PAYLOAD_OBJECT_REQUIRED');
  need(canonicalJson(attestation.payload)===canonicalJson(payload),'SIGNED_PAYLOAD_DOES_NOT_BIND_PROOFS');
  need(typeof attestation.signatureBase64==='string'&&/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(attestation.signatureBase64),'SIGNATURE_ENCODING_INVALID');
  const signature=Buffer.from(attestation.signatureBase64,'base64');
  need(signature.length===64,'ED25519_SIGNATURE_LENGTH_INVALID');
  let signed=false;
  try{signed=verifySignature(null,Buffer.from(canonicalJson({schema:attestation.schema,signedAt:attestation.signedAt,payload}),'utf8'),createPublicKey(policy.publicKeyPem),signature);}catch{signed=false;}
  need(signed,'AUTHENTICATED_PRODUCER_SIGNATURE_NOT_VERIFIED');
  return {
    schema:'enguru.p06.authenticated-producer-integration-candidate/v15',
    state:'AUTHENTICATED_PROVENANCE_CANDIDATE_ONLY_OFFICIAL_HOLD',
    mainSha:MAIN,donecheckSha:DONECHECK,producerId:policy.producerId,
    policySha256:expectedPolicySha256,attestationVerified:true,
    signedArtifactSha256:artifacts,
    canSubmitForSeparateIssuerReview:true,
    trustedProducerAllowlistGranted:false,donecheckVerifyTaskInvoked:false,
    officialIssuer:'HOLD',officialDoneCheck:'HOLD',humanThreshold:'HOLD',verifiedFinish:'HOLD',
    assertionMinted:false,canonSourceMutation:false,
    nextAction:'REVIEW_AUTHORIZED_POLICY_AND_REAL_DONECHECK_V12_VERIFICATION',
  };
}
