/**
 * ENGURU V6.9 WP-02+WP-03: bounded evidence and authority observation bridge.
 * Review-only engineering candidate. No writes to canonical ledger, key store or DoneCheck.
 * Canonical verified finish remains exclusively in engurulabory/donecheck
 * recordVerifiedFinish() with its authenticated reviewer and audit ledger.
 *
 * This module uses node:crypto to independently check scoped Ed25519 attestations
 * only against a caller-owned, provenance-validated TRUSTED registry. The public
 * production CLI has no configured trust root and therefore always holds.
 */
import { createHash, verify as cryptoVerify } from 'node:crypto';
import { readFile, lstat } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

export const SOURCE_PINS = Object.freeze({
  taskId: 'ENGURU-MGMT69-GH-FOUNDATION-01',
  repo: 'engurulabory/Engurulaboratuvari',
  ledgerPrHead: 'de63a9e34a9b05b6474c847019d8c682b5360d50',
  ledgerGitBlob: 'd54f48ce532a23e4e4b6eff1ef5f9c7c776e71fc',
  controlMainHead: '1f7dfd708d652764ac74df27dcbbd393779e2b3b',
  gh69BaseHead: '11b993bd4956c2838900b22fcd03c0c39aae5afc',
  donecheckMainHead: '4181f48df5ea0c060d9aa9f40a471c554b44b53d',
  originalTotal: 100,
  observationPass: 27,
});
const ROLES = ['source_owner', 'issuer', 'independent_verifier'];
const SHA256 = /^[a-f0-9]{64}$/;
const SHA1 = /^[a-f0-9]{40}$/;
const ID = /^B(?:0[1-9]|10)-(?:0[1-9]|10)$/;
const fail = (state, reason, extra={}) => ({state, reason, ...extra, officialPassAdded:0, donecheckAccepted:false, verifiedFinish:false});
const digest = (buffer) => createHash('sha256').update(buffer).digest('hex');
export const gitBlob = bytes => createHash('sha1').update(Buffer.from(`blob ${bytes.length}\0`)).update(bytes).digest('hex');
export function canonicalJson(v) { // JS same algorithm as DoneCheck src/runtime/node/canonical-json.ts
  function norm(x) {
    if (x === null || ['string','boolean'].includes(typeof x)) return x;
    if (typeof x === 'number' && Number.isFinite(x)) return x;
    if (Array.isArray(x)) return x.map(norm);
    if (x && typeof x === 'object') {
      const o={}; for (const k of Object.keys(x).sort()) {
        if (x[k] !== undefined) o[k]=norm(x[k]);
      } return o;
    }
    throw Error('INVALID_CANONICAL_JSON');
  }
  return JSON.stringify(norm(v));
}
function exactControls(rows) {
  if (!Array.isArray(rows) || rows.length !== 100) return false;
  const actual = new Set();
  for (const x of rows) {
    if (!x || typeof x !== 'object' || !ID.test(x.id)||actual.has(x.id)
      ||typeof x.name!=='string'||!x.name.trim()||!['PASS_EVIDENCE','HOLD'].includes(x.state)) return false;
    actual.add(x.id);
    if (x.state==='PASS_EVIDENCE' && (typeof x.evidence !== 'string' || !x.evidence.trim())) return false;
    if (x.state==='HOLD' && x.evidence !== null) return false;
  }
  for (let b=1;b<=10;b++) for (let c=1;c<=10;c++)
    if (!actual.has(`B${String(b).padStart(2,'0')}-${String(c).padStart(2,'0')}`)) return false;
  return true;
}
/** Immutable raw-byte verification of the exact PR191 ledger, not an acceptance write. */
export function auditObservedLedger(raw, opts={}) {
  if (!Buffer.isBuffer(raw) || raw.length<2000) return fail('HOLD_LEDGER_BYTES','EMPTY_OR_UNTRUSTED_LEDGER');
  const pin=opts.expectedGitBlob ?? SOURCE_PINS.ledgerGitBlob;
  if (typeof pin !== 'string'||!SHA1.test(pin)||gitBlob(raw)!==pin)
    return fail('HOLD_LEDGER_PROVENANCE','GIT_BLOB_MISMATCH',{observedGitBlob:gitBlob(raw)});
  let ledger;
  try { ledger=JSON.parse(raw.toString('utf8')); } catch {return fail('HOLD_LEDGER_SCHEMA','INVALID_JSON');}
  if(ledger?.schema!=='enguru.100-unit-verified-finish-tracker/v1'||!exactControls(ledger.checks))
    return fail('HOLD_LEDGER_SCHEMA','ORIGINAL_CATALOG_OR_EVIDENCE');
  const passed=ledger.checks.filter(x=>x.state==='PASS_EVIDENCE').length;
  if(ledger.total_units!==100||ledger.verified_units!==passed||ledger.remaining_units!==100-passed)
    return fail('HOLD_LEDGER_COUNTER','COUNTS_INCONSISTENT');
  if(ledger.checks.find(x=>x.id==='B01-09')?.state!=='HOLD'||
    ledger.official_h1_h2_h3?.passed!==0||ledger.official_h1_h2_h3?.total!==12||
    ledger.verified_finish!=='HOLD')return fail('HOLD_OFFICIAL_GATES','PREMATURE_ACCEPTANCE');
  if(passed!==SOURCE_PINS.observationPass)return fail('HOLD_LEDGER_FRESHNESS','PINNED_OBSERVATION_CHANGED');
  return fail('PASS_READ_ONLY_LEDGER_OBSERVATION','PINNED_LEDGER_INVARIANTS',{
    verifiedUnits:passed,remainingUnits:100-passed,ledgerBlobSha1:gitBlob(raw),rawSha256:digest(raw),
    eligibleControls:Object.fromEntries(ledger.checks.filter(x=>x.state==='HOLD').map(x=>[x.id,x.name]))
  });
}
function secureTime(value) {
  return typeof value==='string' && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(value)
    && Number.isFinite(Date.parse(value));
}
/** Structurally authenticate role grants, scoped and signed with Ed25519.
 * The trusted policy MUST be anchored by a separate externally authenticated
 * provider; a packet-carried policy cannot become a production trust root.
 */
export function assessSimulation({request,attestations,trustedPolicy,rawEvidence,ledgerAudit,now}) {
  if(ledgerAudit?.state!=='PASS_READ_ONLY_LEDGER_OBSERVATION')
    return fail('HOLD_LEDGER','EXACT_LEDGER_NOT_VERIFIED');
  if(!request||typeof request!=='object'||request.taskId!==SOURCE_PINS.taskId||
     request.repo!==SOURCE_PINS.repo||request.sourceHead!==SOURCE_PINS.ledgerPrHead||
     request.ledgerBlob!==ledgerAudit.ledgerBlobSha1||request.targetHead!==SOURCE_PINS.gh69BaseHead)
    return fail('HOLD_SOURCE_SCOPE','TASK_OR_SOURCE_BINDING');
  if(!Buffer.isBuffer(rawEvidence)||rawEvidence.length===0||!SHA256.test(request.evidenceSha256)||
     digest(rawEvidence)!==request.evidenceSha256)
    return fail('HOLD_EVIDENCE','RAW_EVIDENCE_DIGEST');
  if(!Array.isArray(request.controlIds)||request.controlIds.length<1||request.controlIds.length>10||
     new Set(request.controlIds).size!==request.controlIds.length||
     request.controlIds.some(id=>typeof id!=='string'||!ID.test(id)||!Object.hasOwn(ledgerAudit.eligibleControls??{},id)))
    return fail('HOLD_SCOPE','INVALID_OR_DUPLICATE_CONTROL_IDS');
  // Real canonical ledger set is checked separately in auditObservedLedger.
  if(!Array.isArray(attestations)||attestations.length!==ROLES.length||
     !trustedPolicy||typeof trustedPolicy!=='object'||trustedPolicy.trustProvenance!=='TEST_ONLY_VERIFIED_EXTERNALLY')
    return fail('HOLD_TRUST_ROOT','TRUST_REGISTRY_REQUIRES_EXTERNAL_PROVENANCE');
  if(!secureTime(now))return fail('HOLD_TIME','TIME_NOT_PROVEN');
  const seen=new Set(),seenActors=new Set();
  for(const role of ROLES) {
    const matches=attestations.filter(x=>x?.role===role);
    if(matches.length!==1)return fail('HOLD_AUTHORITY','ROLE_COUNT_OR_MISSING');
    const a=matches[0];
    const key=trustedPolicy.keys?.[a.keyId];
    if(!key||key.role!==role||key.actorId!==a.actorId||key.active!==true||
       !Array.isArray(key.allowedRepos)||!key.allowedRepos.includes(request.repo))
      return fail('HOLD_AUTHORITY','UNTRUSTED_KEY_OR_WRONG_ROLE');
    if(!secureTime(a.signedAt)||!secureTime(a.expiresAt)||
       Date.parse(a.expiresAt)<=Date.parse(now)||Date.parse(a.signedAt)>Date.parse(now)||
       Date.parse(a.expiresAt)<=Date.parse(a.signedAt))
      return fail('HOLD_AUTHORITY','EXPIRED_OR_FUTURE_ATTESTATION');
    if(typeof a.nonce!=='string'||a.nonce.length<16||seen.has(a.nonce)||seenActors.has(a.actorId))
      return fail('HOLD_AUTHORITY','REPLAY_OR_NO_ROLE_SEPARATION');
    seen.add(a.nonce);seenActors.add(a.actorId);
    if(a.taskId!==request.taskId||a.repo!==request.repo||
       a.sourceHead!==request.sourceHead||a.targetHead!==request.targetHead||
       a.ledgerBlob!==request.ledgerBlob||a.evidenceSha256!==request.evidenceSha256||
       JSON.stringify(a.controlIds)!==JSON.stringify(request.controlIds))
      return fail('HOLD_AUTHORITY','SIGNATURE_SCOPE_MISMATCH');
    if(typeof a.signatureBase64!=='string'||!a.signatureBase64||!key.publicKeyPem)
      return fail('HOLD_AUTHORITY','UNSIGNED_ATTESTATION');
    const {signatureBase64,...signedBody}=a;
    let valid=false;
    try {valid=cryptoVerify(null,Buffer.from(canonicalJson(signedBody)),key.publicKeyPem,
      Buffer.from(signatureBase64,'base64'));} catch {valid=false;}
    if(!valid)return fail('HOLD_AUTHORITY','INVALID_ED25519_SIGNATURE');
  }
  return fail('READY_FOR_EXTERNAL_DONECHECK_SIMULATION','THREE_SCOPED_CRYPTO_GRANTS_VALID_TEST_ONLY',{
    scopedControlIds:request.controlIds,verifiedRoles:ROLES.slice(),externalDoneCheckRequired:true
  });
}
export async function inspectProductionLedger(file) {
  try {
    if (typeof file!=='string'||!file||!(await lstat(file)).isFile() || (await lstat(file)).isSymbolicLink())
      return fail('HOLD_LEDGER_SOURCE','REGULAR_FILE_REQUIRED');
    const raw=await readFile(file);
    const observation=auditObservedLedger(raw);
    if(observation.state!=='PASS_READ_ONLY_LEDGER_OBSERVATION')return observation;
    // No external owner/issuer/verifier trust root exists in canonical GH69.
    return fail('HOLD_EXTERNAL_TRUST_ROOT','REQUIRES_CANONICAL_OWNER_ISSUER_VERIFIER_AND_DONECHECK',{
      ledgerBlobSha1:observation.ledgerBlobSha1,verifiedUnits:observation.verifiedUnits,
      donecheckSourceHead:SOURCE_PINS.donecheckMainHead
    });
  } catch { return fail('HOLD_LEDGER_SOURCE','READ_ACCESS_OR_PATH_FAILURE'); }
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href) {
  const f=process.argv[2];
  inspectProductionLedger(f).then(x=>{
    console.log(JSON.stringify(x));
    process.exitCode=x.state==='HOLD_EXTERNAL_TRUST_ROOT'?0:2;
  });
}