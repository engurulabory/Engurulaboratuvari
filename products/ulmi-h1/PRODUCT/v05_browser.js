'use strict';
/* ENGÜRÜ Mühendis OSi™ V0.5: same-tab, no browser interception, no bridge,
   real native window.fetch to current server; independent DoneCheck NOT implied. */
const $ = id => document.getElementById(id);
const token = document.querySelector('meta[name="enguru-token"]').content;
const STORE = 'enguru_muhendis_v05_real_browser_candidate';
const sessionId = (()=>{const v=sessionStorage.getItem(STORE+'_session')||crypto.randomUUID();sessionStorage.setItem(STORE+'_session',v);return v;})();
let evidence = null;
const now = ()=>new Date().toISOString();
function addStep(name,passed,details){
 const rec={step:name,state:passed?'PASS':'HOLD',utc:now(),details:String(details??'')};
 evidence.steps.push(rec);const li=document.createElement('li');li.className=passed?'pass':'hold';li.textContent=rec.state+' · '+name+' · '+rec.details;$('steps').append(li);
 if(!passed)throw Error(name+' · '+rec.details);
}
async function api(path,data,overrideToken){
 const method=data===undefined?'GET':'POST';const cfg={method,cache:'no-store'};
 if(method==='POST'){cfg.headers={'Content-Type':'application/json','X-Enguru-Token':overrideToken??token};cfg.body=JSON.stringify(data);}
 // This native fetch goes from the actual browser straight to localhost; no intermediary.
 const response=await fetch(path,cfg);
 evidence.network.push({utc:now(),method,path:path.split('?')[0],status:response.status});
 let body;try{body=await response.json();}catch(e){throw Error('HTTP '+response.status+' · JSON olmayan API yanıtı: '+path);}
 return {status:response.status,body};
}
async function sha256(text){
 const bytes=new TextEncoder().encode(text);const hash=await crypto.subtle.digest('SHA-256',bytes);
 return [...new Uint8Array(hash)].map(b=>b.toString(16).padStart(2,'0')).join('');
}
async function verifyTask(task,name,verifyBehavior){
 const t=await api('/api/task?task_id='+encodeURIComponent(task.task_id));
 addStep(name+' SQLite görev geri okuması',t.status===200&&t.body.task?.status==='PASS_SCOPED',task.task_id);
 const receipt=t.body.task.receipt;
 const f=await api('/api/file?name='+encodeURIComponent(receipt.path));
 addStep(name+' gerçek dosya geri okuması',f.status===200&&typeof f.body.content==='string',receipt.path);
 const hash=await sha256(f.body.content);
 addStep(name+' SHA-256 tarayıcı hesaplaması',hash===receipt.output_sha256,hash);
 const r=await api('/api/verify?task_id='+encodeURIComponent(task.task_id));
 addStep(name+' API SHA geri okuması',r.status===200&&r.body.match===true&&r.body.sha256===hash,r.body.status);
 evidence.outputs.push({label:name,task_id:task.task_id,filename:receipt.path,sha256:hash,behavior:receipt.functional_test.status});
 if(verifyBehavior==='python')addStep('Python ayrı süreç 3 gerçek test',receipt.functional_test.status==='PASS'&&receipt.functional_test.output.includes('Ran 3 tests'),receipt.functional_test.method);
 if(verifyBehavior==='diagnostic')addStep('Eklenebilir statik teşhis modülü',receipt.functional_test.capability_id==='PY_DIAGNOSTIC_V1'&&receipt.functional_test.status==='PASS'&&receipt.functional_test.diagnostic!==undefined,receipt.functional_test.method);
 if(verifyBehavior==='html'){
   // The only HTML executed here is the trusted, locally pinned scaffold fixture.
   addStep('Sabit HTML şablonu kaynağı',receipt.source_origin==='SCOPED_TEMPLATE_HTML',receipt.source_origin);
   const iframe=$('trusted-fixture');
   await new Promise((ok,fail)=>{const timer=setTimeout(()=>fail(Error('Güvenilir HTML iframe zaman aşımı')),5000);iframe.onload=()=>{clearTimeout(timer);ok();};iframe.src='/api/trusted-html?task_id='+encodeURIComponent(task.task_id);});
   const b=iframe.contentDocument.getElementById('tamamla');b.click();
   addStep('Gerçek tarayıcıda oluşturulmuş HTML butonu',iframe.contentDocument.getElementById('durum')?.textContent==='Görev tamamlandı','Görev tamamlandı');
   evidence.outputs[evidence.outputs.length-1].behavior='PASS_SCOPED_BROWSER_BUTTON';
   iframe.removeAttribute('src');
 }
}
function persist(){sessionStorage.setItem(STORE,JSON.stringify(evidence));}
// V0.5.6 real Safari worklist acceptance — user starts this batch explicitly.
// The client cannot independently approve its own browser proof; HTML remains VERIFYING.
async function verifyWorklistBrowser(){
  const catalog=await api('/api/worklist');
  addStep('İş listesi gerçek API bağlantısı',catalog.status===200&&catalog.body.status==='PASS_SCOPED_LOCAL_WORKLIST','GET /api/worklist');
  const demo=catalog.body.catalogs.find(x=>x.catalog_id==='H1_PILOT_WORKLIST');
  addStep('Örnek listenin Saray kabulünden ayrılması',!!demo&&demo.source_claim==='LOCAL_DEMO_NOT_SARAY_ACCEPTED','LOCAL_DEMO_NOT_SARAY_ACCEPTED');
  addStep('Seçilebilir üç mühendislik iş türü',
    ['PYTHON_TEST_EXAMPLE','HTML_EXAMPLE','PYTHON_STATIC_DIAG'].every(kind=>catalog.body.items.some(x=>x.kind===kind&&x.catalog_id==='H1_PILOT_WORKLIST')),
    'Python · HTML · AST');
  for(const kind of ['PYTHON_TEST_EXAMPLE','HTML_EXAMPLE','PYTHON_STATIC_DIAG']){
    const item=catalog.body.items.find(x=>x.kind===kind&&x.catalog_id==='H1_PILOT_WORKLIST');
    const p=await api('/api/worklist/plan',{work_id:item.work_id});
    const selectedId=p.body.plan?.task_id||p.body.task?.task_id;
    addStep('İş listesinden seç ve owner planını hazırla · '+kind,
      p.status===200&&['READY_OWNER','ALREADY_PLANNED'].includes(p.body.status)&&!!selectedId,
      item.work_id);
    const x=await api('/api/execute',{task_id:selectedId});
    addStep('Owner tarafından başlatılmış sınırlı gerçek icra · '+kind,
      x.status===200&&x.body.status==='PASS_SCOPED',x.body.status);
    const t=await api('/api/task?task_id='+encodeURIComponent(selectedId));
    addStep('İş listesi SQLite görev eşliği · '+kind,
      t.status===200&&t.body.task?.status==='PASS_SCOPED',selectedId);
    const f=await api('/api/file?name='+encodeURIComponent(t.body.task.path));
    const hash=await sha256(f.body.content);
    addStep('İş listesi çıktı SHA geri okuma · '+kind,
      f.status===200&&hash===t.body.task.receipt?.output_sha256,hash);
    if(kind==='HTML_EXAMPLE'){
      const frame=$('trusted-fixture');
      await new Promise((resolve,reject)=>{
        const timer=setTimeout(()=>reject(Error('HTML iş listesi iframe yüklenemedi')),7000);
        frame.onload=()=>{clearTimeout(timer);resolve();};
        frame.src='/api/trusted-html?task_id='+encodeURIComponent(selectedId);
      });
      const doc=frame.contentDocument;
      addStep('HTML iş listesi gerçek Safari düğme ön durumu',doc?.getElementById('durum')?.textContent==='Görev hazır',selectedId);
      doc.getElementById('tamamla').click();
      const value=doc.getElementById('durum').textContent;
      addStep('HTML iş listesi gerçek Safari düğme son durumu',value==='Görev tamamlandı',value);
      frame.removeAttribute('src');
      const proof=await api('/api/worklist/browser-accept',{work_id:item.work_id,task_id:selectedId,observed:value});
      addStep('İstemci kanıtı bağımsız PASS üretmez',proof.status===200&&proof.body.status==='CLIENT_OBSERVATION_RECORDED_VERIFYING'&&proof.body.final_done===false,'VERIFYING');
      evidence.worklist_html_task=selectedId;
    }
    if(kind==='PYTHON_TEST_EXAMPLE')addStep('İş listesi Python 3 gerçek test',
      t.body.task.receipt?.functional_test?.status==='PASS'&&t.body.task.receipt.functional_test.output.includes('Ran 3 tests'),selectedId);
    if(kind==='PYTHON_STATIC_DIAG')addStep('İş listesi AST teşhisi, kod çalıştırmadan',
      t.body.task.receipt?.functional_test?.status==='PASS'&&t.body.task.receipt.functional_test.capability_id==='PY_DIAGNOSTIC_V1',selectedId);
    evidence['worklist_'+kind]=selectedId;
    persist();
  }
  const bad=await api('/api/worklist/browser-accept',{
    work_id:'H1_DEMO_HTML_002',task_id:evidence.worklist_html_task,observed:'SAHTE_DONE'});
  addStep('Sahte DONE metni güvenle reddedilir',bad.status===422,bad.status);
  const state=await api('/api/worklist');
  const items=state.body.items.filter(i=>i.catalog_id==='H1_PILOT_WORKLIST');
  const py=items.find(i=>i.kind==='PYTHON_TEST_EXAMPLE');
  const dg=items.find(i=>i.kind==='PYTHON_STATIC_DIAG');
  const ht=items.find(i=>i.kind==='HTML_EXAMPLE');
  addStep('Kanıtlı Python ve AST Biten İşler\'e geçti',
    py?.state==='DONE_SCOPED'&&dg?.state==='DONE_SCOPED'&&state.body.work_done.some(i=>i.work_id===py.work_id),
    'Python + AST DONE_SCOPED');
  addStep('HTML istemci bildirimi yalnız Doğrulanıyor durumunda',
    ht?.state==='VERIFYING'&&state.body.work_in_progress.some(i=>i.work_id===ht.work_id)&&
    !state.body.work_done.some(i=>i.work_id===ht.work_id),'VERIFYING');
  evidence.worklist_source='LOCAL_DEMO_NOT_SARAY_ACCEPTED';
  evidence.worklist_html_final='VERIFYING';
}

async function start(){
 $('start').disabled=true;$('download').disabled=true;$('steps').replaceChildren();
 evidence={schema:'enguru.muhendis-osi.h1-v05-native-browser-acceptance/v1',started_at:now(),session_id:sessionId,location_origin:location.origin,
   user_agent:navigator.userAgent,bridge_used:false,interception_used:false,network:[],steps:[],outputs:[],phase:'RUNNING',goal_1:'ACTIVE',goal_2:'PARKED',html_prototype:'HOLD',daily_zero_procedure:'NOT_TESTED',official_donecheck:'NOT_TESTED'};
 try{
  addStep('Gerçek HTTP URL',location.protocol==='http:'&&location.hostname==='127.0.0.1'&&!location.port.startsWith('0'),location.origin);
  const st=await api('/api/status');addStep('Yerel mühendis API',st.status===200&&st.body.app.startsWith('ENGÜRÜ Mühendis'),st.status);
  const maps=await api('/api/maps');addStep('Dokuz harita',maps.status===200&&maps.body.maps.length===9,'9/9');
  const caps=await api('/api/capabilities');addStep('Yetenek modülü etkin',caps.status===200&&caps.body.capabilities.some(x=>x.id==='PY_DIAGNOSTIC_V1'&&x.enabled),'PY_DIAGNOSTIC_V1');
  const jobs=[{name:'HTML',route:'/api/scaffold',payload:{kind:'html'},behavior:'html'},
              {name:'Python',route:'/api/scaffold',payload:{kind:'python'},behavior:'python'},
              {name:'Teşhis',route:'/api/capability/plan',payload:{id:'PY_DIAGNOSTIC_V1',source:'def hesapla(a, b)\n    return a + b'},behavior:'diagnostic'}];
  for(const job of jobs){
   const p=await api(job.route,job.payload);addStep(job.name+' görev planı',p.status===200&&p.body.status==='READY',p.body.task_id);
   const x=await api('/api/execute',{task_id:p.body.task_id});addStep(job.name+' owner onaylı gerçek icra',x.status===200&&x.body.status==='PASS_SCOPED',x.body.status);
   await verifyTask(p.body,job.name,job.behavior);
   evidence['task_'+job.name]=p.body.task_id;persist();
  }
  await verifyWorklistBrowser();
  const invalid=await api('/api/scaffold',{kind:'python'},'BILEREK_YANLIS_TOKEN');addStep('Yetkisiz POST güvenle reddedilir',invalid.status===403,invalid.status);
  const retry=await api('/api/execute',{task_id:evidence.task_HTML});addStep('Aynı görev ikinci dosya oluşturmaz',retry.status===200&&retry.body.already_executed===true,retry.body.already_executed);
  const tasks=await api('/api/tasks');addStep('Görev defteri 3 işi koruyor',jobs.every(j=>tasks.body.tasks.some(t=>t.task_id===evidence['task_'+j.name])),tasks.body.tasks.length);
  evidence.phase='BEFORE_RELOAD';persist();$('state').textContent='Görevler tamamlandı · aynı sekmede yenilenerek makbuzlar doğrulanıyor…';
  location.reload();
 }catch(e){evidence.phase='HOLD';evidence.error=String(e);persist();render();}
}
async function resume(){
 evidence=JSON.parse(sessionStorage.getItem(STORE)||'null');
 if(!evidence||evidence.session_id!==sessionId||evidence.phase!=='BEFORE_RELOAD')return;
 $('start').disabled=true;$('steps').replaceChildren();
 for(const t of evidence.steps){const li=document.createElement('li');li.className=t.state==='PASS'?'pass':'hold';li.textContent=t.state+' · '+t.step+' · '+t.details;$('steps').append(li);}
 try{
  for(const name of ['HTML','Python','Teşhis']){
   const t=await api('/api/task?task_id='+evidence['task_'+name]);
   addStep('Yeniden açma · '+name,t.status===200&&t.body.task.receipt?.output_sha256===evidence.outputs.find(x=>x.label===name)?.sha256,name);
  }
  const wl=await api('/api/worklist');
  const htmlWork=wl.body.items.find(i=>i.work_id==='H1_DEMO_HTML_002');
  const pythonWork=wl.body.items.find(i=>i.work_id==='H1_DEMO_PYTHON_001');
  addStep('Yeniden açma sonrası HTML bağımsız kanıt bekliyor',
    htmlWork?.state==='VERIFYING'&&!wl.body.work_done.some(i=>i.work_id===htmlWork.work_id),'VERIFYING');
  addStep('Yeniden açma sonrası kanıtlı Python bitti',
    pythonWork?.state==='DONE_SCOPED', 'DONE_SCOPED');
  const required=['/api/status' ,'/api/maps','/api/capabilities','/api/scaffold','/api/execute','/api/task','/api/file','/api/verify'];
  addStep('Gerçek tarayıcı API istek zinciri',required.every(path=>evidence.network.some(x=>x.path===path&&x.status===200)),required.join(' → '));
  evidence.phase='PASS_SCOPED_DIRECT_BROWSER';evidence.completed_at=now();persist();render();
 }catch(e){evidence.phase='HOLD';evidence.error=String(e);persist();render();}
}
function render(){
 $('start').disabled=false;$('download').disabled=false;
 $('browser-state').textContent=evidence.phase==='PASS_SCOPED_DIRECT_BROWSER'?'PASS_SCOPED_DIRECT_BROWSER':'HOLD';
 $('browser-state').className=evidence.phase==='PASS_SCOPED_DIRECT_BROWSER'?'pass':'hold';
 $('state').textContent=evidence.phase==='PASS_SCOPED_DIRECT_BROWSER'?'Gerçek tarayıcıda tüm kapsamlı kontroller geçti.':'HOLD · '+(evidence.error||'Kanıt henüz tamamlanmadı');
 $('summary').textContent=JSON.stringify({phase:evidence.phase,session_id:evidence.session_id,steps:evidence.steps.length,outputs:evidence.outputs.length,network_request_count:evidence.network.length,html_prototype:evidence.html_prototype,goal_2:evidence.goal_2},null,2);
}
$('start').addEventListener('click',start);
$('download').addEventListener('click',()=>{
 if(!evidence)return;
 const a=document.createElement('a');const blob=new Blob([JSON.stringify(evidence,null,2)+'\n'],{type:'application/json'});
 a.href=URL.createObjectURL(blob);a.download='ENGURU_MUHENDIS_V05_DOGRUDAN_TARAYICI_KANITI.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),2000);
});
if(sessionStorage.getItem(STORE)){
 const old=JSON.parse(sessionStorage.getItem(STORE));
 if(old?.phase==='BEFORE_RELOAD')resume();else{evidence=old;for(const t of old.steps||[]){const li=document.createElement('li');li.className=t.state==='PASS'?'pass':'hold';li.textContent=t.state+' · '+t.step+' · '+t.details;$('steps').append(li);}render();}
}
