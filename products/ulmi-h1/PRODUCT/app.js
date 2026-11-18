/* ENGÜRÜ ULMi H1: real same-origin API client, not a simulator.
   Reuses unchanged server.py / SQLite / fixed-template executor. */
'use strict';
const $ = id => document.getElementById(id);
const sessionToken = document.querySelector('meta[name="enguru-token"]').content;
let selectedKind = 'python';
let activeTask = null;
let pending = false;
const descriptions = {
 python: 'Mevcut motorun güvenilir Python örneğini planlar; yalnız bu sabit kaynak alt süreçte 3 gerçek testle çalıştırılır.',
 html: 'İşlevli HTML belgesi oluşturur. Gerçek tarayıcı buton testi ayrıca değerlendirilir.',
 taskboard: 'Gerçek Python HTTP + HTML + SQLite görev panosu üretir; alt süreçte 6 test yürütür. Üretilen uygulama ayrı başlatılabilir.',
 projectboard: 'Kayıtlı projenin gerçek kimliği/SHA’sı ile hedefe özel görev panosu üretir; özgün proje ve test kanıtını eşleştirir.',
 diagnostic: 'Python kaynağını yürütmeden analiz eder ve kaynaklı teşhis raporu yazar.',
 repair: 'Gerçek Python sözdizimi RED → tek satırlık güvenli onarım → AST GREEN. Kullanıcı kodu çalıştırılmaz.',
 qwen_plan: 'Yerel Qwen3 14B üzerinden özgün dosya planı önerir; model kimliği bağımsız doğrulanmadan PASS verilmez, kod otomatik çalıştırılmaz.'
};
const setText = (id,value) => {$(id).textContent = value == null ? '—' : String(value);};
function toast(message){const el=$('toast');el.hidden=false;el.textContent=message;clearTimeout(toast.timer);toast.timer=setTimeout(()=>el.hidden=true,8500);}
async function api(path,body){
 const options={headers:{'X-Enguru-Token':sessionToken}};
 if(body!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
 const resp=await fetch(path,options);
 const ct=resp.headers.get('Content-Type')||'';
 if(!ct.includes('application/json'))throw Error('HOLD: Beklenen JSON API yanıtı alınamadı.');
 const obj=await resp.json();
 if(!resp.ok)throw Error(obj.reason||obj.error||`HOLD HTTP ${resp.status}`);
 return obj;
}
function busy(value){pending=value;for(const id of ['plan-button','execute-button','refresh-button'])$(id).disabled=value;
 if(!value && activeTask)$('execute-button').disabled=activeTask.status!=='READY';}
function kindChanged(kind){if(pending)return;selectedKind=kind;
 for(const card of document.querySelectorAll('.action-card')){const yes=card.dataset.kind===kind;card.classList.toggle('is-selected',yes);card.setAttribute('aria-pressed',String(yes));card.querySelector('.action-arrow').textContent=yes?'Seçili ↗':'Seç ↗';}
 $('diagnostic-box').hidden=!['diagnostic','repair'].includes(kind);$('qwen-box').hidden=kind!=='qwen_plan';setText('kind-description',descriptions[kind]);
 setText('plan-button',kind==='diagnostic'?'Kod teşhis planını oluştur →':kind==='repair'?'Güvenli onarım planını oluştur →':'Gerçek planı oluştur →');
}
function showPlan(t){activeTask=t;
 $('plan-panel').hidden=false;$('plan-placeholder').hidden=true;
 setText('plan-task-id',t.task_id);setText('plan-filename',t.path);
 setText('plan-sha',t.plan_sha256||t.plan_sha||'SHA bekleniyor');
 setText('plan-source',t.content||'İçerik görevde okunamadı');setText('plan-status',t.status||'HOLD');
 const evidence=t.model_route_receipt;const el=$('model-route-evidence');
 el.hidden=!evidence;el.textContent=evidence?'MODEL ROTASI: '+evidence.model+' · '+evidence.provenance_level+' · '+evidence.response_sha256:'—';
 $('execute-button').disabled=t.status!=='READY';
}
function showReceipt(r,task,liveVerify){$('receipt-panel').hidden=false;$('receipt-placeholder').hidden=true;
 const result=$('receipt-summary');
 const state=task.status||'HOLD';
 const fn=r?.functional_test||{};const verified=liveVerify?.match===true && r?.readback==='PASS' && !!r?.output_sha256 && r.output_sha256===r.readback_sha256;
 result.classList.toggle('hold',!verified);
 result.textContent=verified?`Gerçek dosya oluşturuldu; güncel SHA geri okuması PASS. İşlevsel test: ${fn.status||'NOT_TESTED'}. Resmî DoneCheck ayrı.`:`HOLD: Görev ${state}. Güncel dosya bütünlüğü doğrulanmadı.`;
 setText('receipt-task',task.task_id);setText('receipt-sha',r?.output_sha256||'—');
 setText('receipt-test',fn.method||'—');setText('receipt-file',r?.path||task.path||'—');
 $('trusted-html-link').hidden=!(r?.source_origin==='SCOPED_TEMPLATE_HTML' && verified);
 if(!$('trusted-html-link').hidden)$('trusted-html-link').href='/api/trusted-html?task_id='+encodeURIComponent(task.task_id);
 $('file-preview').hidden=true;setText('readback-result','Gerçek dosya geri okuması için düğmeye bas.');
}
async function saveProject(){try{const title=$('project-title').value.trim();const goal=$('project-goal').value.trim();
 if(title.length<1||goal.length<5)throw Error('Proje adı ve en az 5 karakterli hedef gerekli.');
 $('save-project').disabled=true;
 const result=await api('/api/desk/projects/save',{title,goal});
 setText('project-feedback','SQLite kaydı oluşturuldu · '+result.project.id+' · kaynak SHA '+result.project.sha256.slice(0,16)+'…');
 await refreshProjects();$('project-list').value=result.project.id;await refreshChatHistory();
 }catch(e){setText('project-feedback','HOLD · '+e.message);}finally{$('save-project').disabled=false;}}
async function refreshProjects(){const data=await api('/api/desk/projects');
 const sel=$('project-list');const previous=sel.value;sel.replaceChildren();
 if(!data.projects.length){const o=document.createElement('option');o.textContent='Henüz kayıtlı proje yok';o.value='';sel.append(o);return;}
 for(const p of data.projects){const o=document.createElement('option');o.value=p.id;o.dataset.sha=p.sha256;o.textContent=p.title+' · '+p.id.slice(0,8);sel.append(o);}
 if(data.projects.some(p=>p.id===previous))sel.value=previous;
 await refreshChatHistory();
}
// H1 İş 05: the pre-existing project-SHA conversation API is now visible on the
// same engineering desk. All model/user text is displayed via textContent.
let chatPending=false;
function activeChatProject(){
 const opt=$('project-list').selectedOptions[0];
 return opt?.value && opt.dataset.sha ? {id:opt.value,sha:opt.dataset.sha}:null;
}
function chatEntry(label,text,details=''){
 const row=document.createElement('article');row.className='h1-chat-entry';
 const title=document.createElement('strong');title.textContent=label;
 const content=document.createElement('p');content.textContent=String(text||'');
 row.append(title,content);
 if(details){const note=document.createElement('small');note.textContent=details;row.append(note);}
 $('chat-history').append(row);
}
function showChatHistory(messages){
 $('chat-history').replaceChildren();
 if(!messages.length){chatEntry('Proje defteri','Bu projede kayıtlı sohbet mesajı bulunmuyor.');return;}
 for(const item of messages){
  chatEntry('Soru · '+(item.saved_at||''),item.user_text||'');
  const proposal=item.response||{};
  const route=proposal.route_receipt||{};
  const hashes=Array.isArray(proposal.source_receipts)?proposal.source_receipts.map(x=>x.role+':'+String(x.sha256||'').slice(0,12)).join(' · '):'Kaynak makbuzu bekleniyor';
  chatEntry('Maya · '+(proposal.state||'ÖNERİ'),proposal.model_output||'',
   'Rota: '+String(route.provider||'DOĞRULANMADI')+' / '+String(route.model||'BELİRSİZ')+' · '+hashes+' · İcra: '+String(proposal.execution_state||'NOT_EXECUTED'));
 }
}
async function refreshChatHistory(){
 const project=activeChatProject();
 if(!project){setText('chat-project-status','Önce bir proje seç.');$('chat-history').replaceChildren();return;}
 setText('chat-project-status','Proje: '+project.id+' · SHA '+project.sha.slice(0,16)+'…');
 try{
  const res=await api('/api/desk/history?project_id='+encodeURIComponent(project.id));
  // An in-flight older project's response must not overwrite the new selection.
  if(activeChatProject()?.id!==project.id)return;
  if(res.project_id!==project.id||res.source!=='H1_SQLITE')throw Error('HOLD_HISTORY_PROJECT_SCOPE');
  showChatHistory(res.messages||[]);
 }catch(e){setText('chat-result','HOLD · Geçmiş: '+e.message);}
}
async function sendProjectChat(){
 if(chatPending)return;
 const project=activeChatProject();const content=$('chat-message').value.trim();
 if(!project){setText('chat-result','Önce SQLite proje kaydı seç.');return;}
 if(!content||content.length>2000){setText('chat-result','1–2000 karakter arasında bir mühendislik sorusu yaz.');return;}
 chatPending=true;$('chat-send').disabled=true;
 try{
  // One unique durable id per explicit human click, without automatic replay.
  const response=await api('/api/desk/project-chat',{project_id:project.id,project_sha256:project.sha,
    message_id:crypto.randomUUID(),text:content,requested_action:'ADVISE_ONLY'});
  if(response.project_id!==project.id||response.project_sha256!==project.sha)throw Error('HOLD_CHAT_SCOPE');
  setText('chat-result','Kaynaklı öneri SQLite içinde kaydedildi · '+response.state+' · İcra: '+response.execution_state);
  $('chat-message').value='';
  await refreshChatHistory();
 }catch(e){setText('chat-result','HOLD · '+e.message+' · Aynı isteği otomatik tekrarlamıyoruz.');}
 finally{chatPending=false;$('chat-send').disabled=false;}
}
async function refresh(){
 const query=new URLSearchParams();
 const search=$('task-search').value.trim();const state=$('task-status-filter').value;
 if(search)query.set('search',search);if(state)query.set('status',state);
 const [status, tasks]=await Promise.all([api('/api/status'),api('/api/tasks'+(query.size?'?'+query:''))]);
 setText('metric-server',status?.network==='LOOPBACK_ONLY'?'Canlı · Yerel HTTP':'HOLD');
 setText('metric-source',`${status.version||'Sürüm belirsiz'} · ${status.network||'kaynak belirsiz'}`);
 setText('metric-tasks',tasks.tasks.length);
 setText('backend-label','H1 motoruna bağlı');
 setText('connection-status','● Gerçek HTTP / SQLite');
 $('sidebar-dot').classList.add('connected');$('connection-status').classList.add('connected');
 const list=$('task-list');list.replaceChildren();
 if(!tasks.tasks.length){const p=document.createElement('p');p.className='muted-hint';p.textContent='Henüz gerçek görev kaydı yok.';list.append(p);}
 for(const t of tasks.tasks.slice(0,20)){
  const row=document.createElement('button');row.type='button';row.className='task-row';
  const meta=document.createElement('span');const name=document.createElement('b');name.textContent=t.path;const date=document.createElement('small');date.textContent=`${t.origin} · ${t.task_id.slice(0,8)}`;meta.append(name,date);
  const badge=document.createElement('em');badge.textContent=t.integrity==='HOLD_INTEGRITY'?'HOLD_INTEGRITY':t.status;row.append(meta,badge);
  row.addEventListener('click',()=>loadTask(t.task_id));list.append(row);
 }
}
async function loadTask(id){try{busy(true);const obj=await api('/api/task?task_id='+encodeURIComponent(id));const task=obj.task;
 if(!task)throw Error('Görev bulunamadı');
 if(task.origin==='LOCAL_OLLAMA'){const proof=await api('/api/model/receipt?task_id='+encodeURIComponent(id));task.model_route_receipt=proof.route_receipt;}
 showPlan(task);
 if(task.receipt){const live=await api('/api/verify?task_id='+encodeURIComponent(id));showReceipt(task.receipt,task,live);}else{$('receipt-panel').hidden=true;$('receipt-placeholder').hidden=false;}
 document.querySelector('#uretim').scrollIntoView({behavior:'smooth',block:'start'});
 }catch(e){toast('Görev geri okuması: '+e.message);}finally{busy(false);}}
async function createPlan(){try{busy(true);let data;
 if(selectedKind==='qwen_plan')data=await api('/api/plan',{prompt:$('qwen-prompt').value.trim()});
 else if(selectedKind==='diagnostic')data=await api('/api/capability/plan',{id:'PY_DIAGNOSTIC_V1',source:$('source-input').value});
 else if(selectedKind==='repair')data=await api('/api/capability/repair-plan',{source:$('source-input').value});
 else if(selectedKind==='projectboard'){const s=$('project-list');const o=s.selectedOptions[0];
  if(!o||!o.value||!o.dataset.sha)throw Error('Önce bir proje kaydet ve seç.');
  data=await api('/api/desk/project-board/plan',{project_id:o.value,project_sha256:o.dataset.sha});}
 else data=await api('/api/scaffold',{kind:selectedKind});
 if(data.status!=='READY'||!data.task_id)throw Error('HOLD: Plan READY değil.');
 showPlan(data);$('receipt-panel').hidden=true;$('receipt-placeholder').hidden=false;
 await refresh();
 }catch(e){toast('Güvenli plan durduruldu: '+e.message);}finally{busy(false);}}
async function execute(){if(!activeTask||activeTask.status!=='READY'||pending)return;
 const id=activeTask.task_id;
 try{busy(true);const obj=await api('/api/execute',{task_id:id});
 const current=await api('/api/task?task_id='+encodeURIComponent(id));
 if(!current.task)throw Error('HOLD: Gerçek görev SQLite geri okuması yok.');
 showPlan(current.task);const live=await api('/api/verify?task_id='+encodeURIComponent(id));showReceipt(current.task.receipt||obj.receipt,current.task,live);
 if(obj.status!=='PASS_SCOPED'||current.task.status!=='PASS_SCOPED')throw Error('HOLD: İcra başarılı olarak doğrulanmadı.');
 await refresh();
 }catch(e){toast('İcra sonucu/kanıt: '+e.message);await refresh().catch(()=>{});}finally{busy(false);}}
async function verify(){if(!activeTask)return;
 try{const v=await api('/api/verify?task_id='+encodeURIComponent(activeTask.task_id));
 setText('readback-result',v.match?`SHA geri okuma PASS_SCOPED · ${v.sha256} · ${v.verifier}`:`HOLD · ${v.reason||v.status}`);
 }catch(e){toast('SHA geri okuma: '+e.message);}}
async function readFile(){if(!activeTask)return;
 try{const name=activeTask.path;const d=await api('/api/file?name='+encodeURIComponent(name));
 $('file-preview').hidden=false;setText('file-preview',d.content||'Boş kaynak');
 }catch(e){toast('Dosya erişimi: '+e.message);}}
async function refreshMaps(){
 const body=$('maps-list');const result=await api('/api/maps');
 const maps=result.maps||[];body.replaceChildren();
 for(const m of maps){
  const article=document.createElement('article');article.className='map-entry';
  const header=document.createElement('strong');header.textContent=m.id+' · '+m.name;
  const desc=document.createElement('small');desc.textContent=m.purpose||'Kaynak tanımı yok';
  const stage=document.createElement('em');stage.textContent='Kaynak projeksiyonu · Canlı kabul ayrı';
  article.append(header,desc,stage);body.append(article);
 }
 setText('maps-count',String(maps.length));
}
function connectEvents(){for(const card of document.querySelectorAll('[data-kind]')){card.addEventListener('click',()=>kindChanged(card.dataset.kind));card.setAttribute('aria-pressed',String(card.dataset.kind===selectedKind));}
 $('plan-button').addEventListener('click',createPlan);$('execute-button').addEventListener('click',execute);
 $('verify-button').addEventListener('click',verify);$('read-button').addEventListener('click',readFile);
 $('refresh-button').addEventListener('click',()=>refresh().catch(e=>toast(e.message)));
 $('task-search-button').addEventListener('click',()=>refresh().catch(e=>toast(e.message)));
 $('task-status-filter').addEventListener('change',()=>refresh().catch(e=>toast(e.message)));
 $('task-search').addEventListener('keydown',e=>{if(e.key==='Enter')refresh().catch(err=>toast(err.message));});
 $('save-project').addEventListener('click',saveProject);
 $('project-list').addEventListener('change',refreshChatHistory);
 $('chat-send').addEventListener('click',sendProjectChat);
 $('chat-refresh').addEventListener('click',refreshChatHistory);
}
connectEvents();
refreshMaps().catch(e=>setText('maps-list','HOLD · Harita kaynağı: '+e.message));
refreshProjects().catch(e=>setText('project-feedback','HOLD · '+e.message));
refresh().catch(e=>{setText('metric-server','Bağlantı yok');setText('connection-status','● H1 API erişilemiyor');
 setText('backend-label','H1 servisi bulunamadı');toast('Bu HTML gerçek H1 HTTP sunucusuyla çalışır. Bağlantı: '+e.message);});
