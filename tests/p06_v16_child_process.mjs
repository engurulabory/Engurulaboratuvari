import {qualifyProducer} from '../tools/enguru_p06_producer_authority_candidate.mjs';
import {readFileSync} from 'node:fs';
import {readFile,writeFile,mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const x=JSON.parse(readFileSync(0,'utf8'),(_k,v)=>v&&v.type==='Buffer'&&Array.isArray(v.data)?Buffer.from(v.data):v);
const point=process.env.ENGURU_P06_V16_TEST_FAULT;
let scratch;
try{
 let evaluate=qualifyProducer;
 if(point){
   const allowed=new Set(['AFTER_RESERVATION','SIGKILL_AFTER_RESERVATION','EIO_BEFORE_WRITE','ENOSPC_BEFORE_FSYNC','AFTER_FILE_FSYNC','BEFORE_PARENT_FSYNC']);
   if(!allowed.has(point))throw new Error('UNRECOGNIZED_TEST_POINT');
   scratch=await mkdtemp(join(tmpdir(),'enguru-p06-fault-only-'));
   const toolDir=new URL('../tools/',import.meta.url);
   const original=await readFile(new URL('enguru_p06_producer_authority_candidate.mjs',toolDir),'utf8');
   const dependency=await readFile(new URL('enguru_p06_authenticated_producer_adapter.mjs',toolDir),'utf8');
   await writeFile(join(scratch,'enguru_p06_authenticated_producer_adapter.mjs'),dependency);
   const marker={
    AFTER_RESERVATION:"  await privateDirectory(slot);",
    SIGKILL_AFTER_RESERVATION:"  await privateDirectory(slot);",
    EIO_BEFORE_WRITE:"    try{await f.writeFile(",
    ENOSPC_BEFORE_FSYNC:"await f.sync()",
    AFTER_FILE_FSYNC:"await f.sync()",
    BEFORE_PARENT_FSYNC:"await parent.sync()"
   }[point];
   const injection=point==='SIGKILL_AFTER_RESERVATION'?"process.kill(process.pid,'SIGKILL');":"throw new HoldError('INJECTED_"+point+"_HOLD');";
   if(!original.includes(marker))throw new Error('FAULT_MARKER_UNAVAILABLE');
   const patched=original.replace(marker,point==='AFTER_RESERVATION'||point==='SIGKILL_AFTER_RESERVATION'?marker+'\n  '+injection:point==='EIO_BEFORE_WRITE'?"    try{"+injection+"await f.writeFile(":marker+';'+injection);
   await writeFile(join(scratch,'enguru_p06_producer_authority_candidate.mjs'),patched);
   evaluate=(await import('file://'+join(scratch,'enguru_p06_producer_authority_candidate.mjs'))).qualifyProducer;
 }
 await evaluate(x);console.log('STATE=QUALIFIED_CANDIDATE_ONLY');
}catch(e){console.log('STATE=HOLD');process.exitCode=41}
finally{if(scratch)await rm(scratch,{recursive:true,force:true})}
