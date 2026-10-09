// Steward v1.2: read-only authenticated fleet discovery, no repository mutation.
export function reconcileFleet({records=[],expected=[],complete=false,source='UNVERIFIED'}={}){
 const seen=new Set(),found=[],duplicates=[];
 for(const record of records){
   const name=record?.full_name;
   if(typeof name!=='string'|| !/^[-.\w]+\/[-.\w]+$/.test(name)) continue;
   if(seen.has(name)){duplicates.push(name);continue;}
   seen.add(name);found.push({repository:name,visibility:record.private?'PRIVATE':'PUBLIC',archived:!!record.archived});
 }
 const missing=expected.filter(name=>!seen.has(name));
 const state=!complete || duplicates.length || missing.length?'HOLD':'PASS';
 return {schema:'enguru.steward.fleet-observation/v1',state,source,complete,
   visibleRepositoryCount:found.length,repositories:found,expectedCount:expected.length,
   missing,duplicates,authority:'OBSERVATION_ONLY',verifiedFinish:'HOLD'};
}
export async function discoverGithubFleet({fetchImpl=globalThis.fetch,token,owner='engurulabory',
 expected=[],maxPages=10}={}){
 if(!token || typeof fetchImpl!=='function')
   return reconcileFleet({records:[],expected,complete:false,source:'TOKEN_OR_FETCH_UNAVAILABLE'});
 const records=[];let complete=false;
 for(let page=1;page<=maxPages;page++){
   let response;
   try{
     response=await fetchImpl('https://api.github.com/user/repos?per_page=100&page='+page+
       '&affiliation=owner,collaborator,organization_member',
       {headers:{Authorization:'Bearer '+token,Accept:'application/vnd.github+json',
         'X-GitHub-Api-Version':'2022-11-28','User-Agent':'enguru-steward-v12'}});
   }catch{return reconcileFleet({records,expected,complete:false,source:'API_NETWORK_HOLD'});}
   if(!response.ok) return reconcileFleet({records,expected,complete:false,source:'API_HTTP_'+response.status});
   let pageData;
   try{pageData=await response.json()}catch{return reconcileFleet({records,expected,complete:false,source:'API_RESPONSE_HOLD'});}
   if(!Array.isArray(pageData)) return reconcileFleet({records,expected,complete:false,source:'API_SCHEMA_HOLD'});
   records.push(...pageData.filter(r=>r?.owner?.login===owner));
   if(pageData.length<100){complete=true;break;}
 }
 const result=reconcileFleet({records,expected,complete,source:'GITHUB_AUTHENTICATED_API'});
 return {...result,owner};
}
