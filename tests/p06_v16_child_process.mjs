import {qualifyProducer} from '../tools/enguru_p06_producer_authority_candidate.mjs';
import {readFileSync} from 'node:fs';
const x=JSON.parse(readFileSync(0,'utf8'),(_k,v)=>v&&v.type==='Buffer'&&Array.isArray(v.data)?Buffer.from(v.data):v);
try{await qualifyProducer(x);console.log('STATE=QUALIFIED_CANDIDATE_ONLY')}catch(e){console.log('STATE=HOLD');process.exitCode=41}
