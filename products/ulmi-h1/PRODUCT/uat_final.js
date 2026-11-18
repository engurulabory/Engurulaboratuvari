/* ULMi H1 same-origin browser UAT; explicit user click, no mock, no fetch interceptor. */
'use strict';
const byId=id=>document.getElementById(id);
const csrf=document.querySelector('meta[name="enguru-token"]').content;
const STORAGE_KEY='enguru_ulmi_h1_uat_last_real_run_v1';
const now=()=>new Date().toISOString();
let proof=null;
function persist(){if(proof)sessionStorage.setItem(STORAGE_KEY,JSON.stringify(proof));}
function step(id,ok,note){
 const item={id,status:ok?'PASS':'HOLD',time:now(),note:String(note??'')};
 proof.checks.push(item);
 const li=document.createElement('li');li.textContent=item.status+' · '+id+' · '+item.note;
 li.className=ok?'pass':'hold';byId('steps').append(li);
 persist();if(!ok)throw Error(id+' · '+item.note);
}
async function req(path,body,auth=csrf){
 const opts={method:body===undefined?'GET':'POST',headers:{'X-Enguru-Token':auth},cache:'no-store'};
 if(body!==undefined){opts.headers['Content-Type']='application/json';opts.body=JSON.stringify(body);}
 const response=await fetch(path,opts);
 const data=await response.json();
 if(proof)proof.http.push({method:opts.method,path:path.split('?')[0],status:response.status});
 return {status:response.status,data};
}
function requireHttp(res,what){step(what,res.status===200,res.status);return res.data;}
async function digest(text){
 const raw=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text));
 return Array.from(new Uint8Array(raw),x=>x.toString(16).padStart(2,'0')).join('');
}
async function verifyProduced(taskId,kind){
 const obj=requireHttp(await req('/api/task?task_id='+encodeURIComponent(taskId)),kind+' SQLite row');
 step(kind+' task state',obj.task?.status==='PASS_SCOPED',obj.task?.status);
 const receipt=obj.task.receipt;
 const file=requireHttp(await req('/api/file?name='+encodeURIComponent(obj.task.path)),kind+' read actual source');
 const hash=await digest(file.content);
 step(kind+' browser SHA-256',hash===receipt.output_sha256 && hash===receipt.readback_sha256,hash);
 const checked=requireHttp(await req('/api/verify?task_id='+encodeURIComponent(taskId)),kind+' server readback');
 step(kind+' independent browser-vs-server digest',checked.match===true&&checked.sha256===hash,checked.status);
 step(kind+' functional test',kind==='HTML' ? receipt.functional_test?.status==='NOT_TESTED_BROWSER' : receipt.functional_test?.status==='PASS',receipt.functional_test?.method);
 proof.tasks.push({task_id:taskId,kind,path:obj.task.path,sha256:hash,method:receipt.functional_test.method});
 persist();return {task:obj.task,content:file.content};
}
async function planApproveExecute(route,input,kind){
 const plan=requireHttp(await req(route,input),kind+' plan HTTP');
 step(kind+' READY before execute',plan.status==='READY'&&!!plan.task_id,plan.status);
 const list=requireHttp(await req('/api/files'),kind+' pre-write file list');
 step(kind+' pre-write file absent',!list.files.some(x=>x.name===plan.path),plan.path);
 const exec=requireHttp(await req('/api/execute',{task_id:plan.task_id}),kind+' approved execute HTTP');
 step(kind+' real scoped execution',exec.status==='PASS_SCOPED',exec.status);
 const verified=await verifyProduced(plan.task_id,kind);
 const repeated=requireHttp(await req('/api/execute',{task_id:plan.task_id}),kind+' idempotent replay');
 step(kind+' replay no second effect',repeated.already_executed===true && repeated.receipt?.output_sha256===verified.task.receipt.output_sha256,repeated.already_executed);
 return verified;
}
async function trustedHtmlButton(taskId){
 const frame=byId('trusted-fixture');
 await new Promise((resolve,reject)=>{
  const clock=setTimeout(()=>reject(Error('HTML iframe timeout')),7000);
  frame.onload=()=>{clearTimeout(clock);resolve();};
  frame.onerror=()=>{clearTimeout(clock);reject(Error('Trusted HTML iframe blocked'));};
  frame.src='/api/trusted-html?task_id='+encodeURIComponent(taskId);
 });
 const doc=frame.contentDocument;
 step('Trusted HTML DOM initial',doc?.getElementById('durum')?.textContent==='Görev hazır',doc?.getElementById('durum')?.textContent);
 doc.getElementById('tamamla').click();
 step('Trusted HTML real button interaction',doc.getElementById('durum').textContent==='Görev tamamlandı',doc.getElementById('durum').textContent);
 frame.removeAttribute('src');
}
function updateView(){
 byId('summary').textContent=proof?JSON.stringify({phase:proof.phase,started:proof.started_at,finished:proof.finished_at,checks:proof.checks.length,holds:proof.checks.filter(x=>x.status==='HOLD').length,tasks:proof.tasks.length,browser:proof.user_agent,origin:proof.origin},null,2):'Henüz görev icra edilmedi.';
 if(proof)byId('download').disabled=false;
}
async function run(){
 byId('run').disabled=true;byId('reload').disabled=true;byId('download').disabled=true;byId('steps').replaceChildren();
 proof={schema:'enguru.ulmi.h1.real-browser-user-observation-v1',started_at:now(),phase:'RUNNING',origin:location.origin,user_agent:navigator.userAgent,bridge_used:false,mock_used:false,http:[],checks:[],tasks:[],owner_final:'NOT_ISSUED',independent_donecheck:'NOT_EXECUTED',h2:'PARKED'};
 persist();
 try{
  step('Real browser loopback origin',location.protocol==='http:'&&location.hostname==='127.0.0.1',location.origin);
  const status=requireHttp(await req('/api/status'),'H1 live HTTP status');
  step('Correct H1 network',status.network==='LOOPBACK_ONLY'&&String(status.app).includes('Mühendis'),status.version);
  const build=status.runtime_build;
  step('Source-bound running H1 identity',
       /^ULMI-H1-V7-/.test(status.version)&&/^[0-9a-f]{64}$/.test(build?.aggregate_sha256||'')&&
       /^[0-9a-f]{64}$/.test(build?.source_sha256?.['server.py']||'')&&
       /^[0-9a-f]{64}$/.test(build?.source_sha256?.['uat_final.js']||''),
       String(build?.aggregate_sha256||'MISSING'));
  proof.runtime_build_sha256=build.aggregate_sha256;
  proof.runtime_sources=build.source_sha256;
  persist();
  const denied=await req('/api/scaffold',{kind:'python'},'FAKE_UAT_TOKEN');
  step('Bad CSRF token denied; no task',denied.status===403,denied.status);
  const wrong=await req('/api/file?name='+encodeURIComponent('../outside.py'));
  step('Path traversal denied',wrong.status===400,wrong.status);
  const python=await planApproveExecute('/api/scaffold',{kind:'python'},'PYTHON');
  step('Real Python subprocess 3 tests',String(python.task.receipt.functional_test?.output).includes('Ran 3 tests'),'3 unittest');
  const html=await planApproveExecute('/api/scaffold',{kind:'html'},'HTML');
  // The trusted HTML template legitimately returns NOT_TESTED_BROWSER before this DOM test.
  await trustedHtmlButton(html.task.task_id);
  const saved=requireHttp(await req('/api/desk/projects/save',{
    title:'H1 UAT '+new Date().toISOString().slice(0,16),
    goal:'Gerçek kullanıcı tarayıcısından proje bağlı HTML HTTP SQLite görev panosu üretmek ve doğrulamak.'
  }),'Project SQLite write');
  const projects=requireHttp(await req('/api/desk/projects'),'Project SQLite readback');
  step('Project SHA and row persisted',projects.projects.some(x=>x.id===saved.project.id&&x.sha256===saved.project.sha256),saved.project.id);
  const board=await planApproveExecute('/api/desk/project-board/plan',{
    project_id:saved.project.id,project_sha256:saved.project.sha256
  },'PROJECT_BOARD');
  step('Generated app six real subprocess tests',String(board.task.receipt.functional_test?.output).includes('Ran 6 tests'),'6 unittest');
  const tasks=requireHttp(await req('/api/tasks'),'Task list after execution');
  step('Three real tasks in SQLite',proof.tasks.every(x=>tasks.tasks.some(t=>t.task_id===x.task_id&&t.status==='PASS_SCOPED')),String(tasks.tasks.length));
  proof.phase='AWAITING_RELOAD_READBACK';byId('state').textContent='Tek koşu tamam. Şimdi «Sayfayı yenile» düğmesi ile gerçek kalıcılığı doğrula.';
  byId('reload').disabled=false;
 }catch(err){proof.phase='HOLD';proof.error=String(err.message);byId('state').textContent='HOLD · '+err.message;}
 finally{proof.finished_at=now();persist();updateView();byId('run').disabled=false;}
}
async function afterReload(){
 try{const v=sessionStorage.getItem(STORAGE_KEY);if(!v)return;proof=JSON.parse(v);updateView();
 if(proof.phase==='AWAITING_RELOAD_READBACK'){
  byId('reload').disabled=false;
  byId('state').textContent='Önceki görevler var; yeniden başlatma sonrası SHA kontrolüne hazır.';
 }
 if(proof.phase==='RELOAD_READBACK'){
  const ids=proof.tasks.map(x=>x.task_id);let ok=ids.length===3;
  const live=await req('/api/status');
  ok=ok&&live.status===200&&live.data.runtime_build?.aggregate_sha256===proof.runtime_build_sha256;
  step('Browser reload unchanged exact H1 source SHA',ok,live.data.runtime_build?.aggregate_sha256||'MISSING');
  for(const x of proof.tasks){
   const task=await req('/api/task?task_id='+encodeURIComponent(x.task_id));
   const verify=await req('/api/verify?task_id='+encodeURIComponent(x.task_id));
   ok=ok&&task.status===200&&task.data.task?.status==='PASS_SCOPED'&&verify.status===200&&verify.data.sha256===x.sha256&&verify.data.match===true;
  }
  step('Browser reload; three SQLite receipts and SHA verified',ok,ids.join(','));
  proof.phase=ok?'BROWSER_OBSERVATION_PASS_SCOPED':'HOLD';
  proof.reloaded_at=now();byId('state').textContent=ok?'Tarayıcı gözlemi PASS_SCOPED · owner kabulü ayrıca gerekir.':'HOLD · Kalıcılık doğrulanamadı.';
  persist();updateView();
 }
 }catch(err){if(proof){proof.phase='HOLD';proof.error=String(err);persist();updateView();}byId('state').textContent='HOLD · '+String(err.message||err);}
}
byId('run').addEventListener('click',run);
byId('reload').addEventListener('click',()=>{if(proof&&proof.phase==='AWAITING_RELOAD_READBACK'){proof.phase='RELOAD_READBACK';persist();location.reload();}});
byId('download').addEventListener('click',()=>{
 if(!proof)return;const b=new Blob([JSON.stringify(proof,null,2)],{type:'application/json'});
 const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='ULMI_H1_GERCEK_TARAYICI_UAT_'+new Date().toISOString().replaceAll(':','-')+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
});
afterReload();
