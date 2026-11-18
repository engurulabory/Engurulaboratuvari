'use strict';
/* H1 V0.5.6: DOM textContent only; no dynamic code from work-list JSON. */
(()=>{
  const $=id=>document.getElementById(id);
  const token=document.querySelector('meta[name="enguru-token"]').content;
  let currentFilter='Tümü', workData={items:[]}, waiting=false;
  const doneStates=new Set(['DONE_SCOPED']);
  const labels={NOT_STARTED:'Başlamayı bekliyor',READY_OWNER:'Plan hazır · onay bekliyor',IN_PROGRESS:'Yapılmakta',
    VERIFYING:'İstemci gözlemi / bağımsız kanıt bekleniyor',DONE_SCOPED:'Kapsamlı testli iş bitti',
    HOLD:'HOLD · inceleme gerekli',HOLD_INTEGRITY:'HOLD · SHA eşliği'};
  const E=(tag,cl,txt)=>{const node=document.createElement(tag);if(cl)node.className=cl;if(txt!==undefined)node.textContent=String(txt);return node;};
  const put=(node,tag,cl,txt)=>{const x=E(tag,cl,txt);node.append(x);return x;};
  const statusText=(state)=>labels[state]||state;
  const renderState=(state)=>{const c=doneStates.has(state)?'done':state==='HOLD'||state==='VERIFYING'||state==='HOLD_INTEGRITY'?'wait':'';return E('span','work-state '+c,statusText(state));};
  async function req(url,data){const opts=data===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-Enguru-Token':token},body:JSON.stringify(data)};
    const r=await fetch(url,opts);let body;try{body=await r.json();}catch(_){throw Error('Yerel API JSON yanıtı okunamadı.');}
    if(!r.ok)throw Error(body.error||`HTTP ${r.status}`);return body;}
  function message(t,problem=false){const el=$('worklist-import-status');el.textContent=t;el.style.color=problem?'#924719':'#276451';}
  async function start(work){
    if(waiting)return;waiting=true;message('İş planı hazırlanıyor…');
    try{
      const o=await req('/api/worklist/plan',{work_id:work.work_id});
      if(o.plan){window.ENGURU_SHOW_PLAN(o.plan);message('Plan hazır. Dosya oluşturmak için owner onayı bekleniyor.');}
      else if(o.task){window.ENGURU_SHOW_TASK(o.task.task_id);message('Önceki görev yeniden açıldı; ikinci iş üretilmedi.');}
      await refresh();$('planbox').scrollIntoView({behavior:'smooth',block:'start'});
    }catch(e){message('HOLD · '+e.message,true);}finally{waiting=false;}
  }
  async function testHTML(work){
    if(waiting)return;waiting=true;message('Güvenilir HTML örneği gerçek tarayıcıda sınanıyor…');
    const root=$('work-browser-test'),area=$('work-browser-frame');root.hidden=false;area.replaceChildren();
    const iframe=put(area,'iframe','html-test-frame');iframe.title='Güvenilir HTML · gerçek tarayıcı işlevsel test';
    const timeout=window.setTimeout(()=>{message('HOLD · Tarayıcı yükleme süresi aşıldı.',true);waiting=false;},12000);
    try{
      const text=await new Promise((resolve,reject)=>{
        iframe.addEventListener('load',()=>{try{const doc=iframe.contentDocument;
          if(!doc)throw Error('Tarayıcı belge erişimi yok.');
          const before=doc.getElementById('durum')?.textContent;
          const button=doc.getElementById('tamamla');if(before!=='Görev hazır'||!button)throw Error('Güvenilir HTML test sözleşmesi eksik.');
          button.click();const after=doc.getElementById('durum')?.textContent;
          if(after!=='Görev tamamlandı')throw Error('Gerçek buton davranışı başarısız.');
          resolve(after);
        }catch(e){reject(e);}}, {once:true});
        iframe.addEventListener('error',()=>reject(Error('HTML yüklenemedi.')),{once:true});
        iframe.src='/api/trusted-html?task_id='+encodeURIComponent(work.task_id);
      });
      const proof=await req('/api/worklist/browser-accept',{work_id:work.work_id,task_id:work.task_id,observed:text});
      $('work-browser-note').textContent='İstemci düğme davranışını bildirdi. '+proof.status+' · Bağımsız kanıt ve owner kabulü bekleniyor.';
      message('Tarayıcı gözlemi kaydedildi. Doğrulama aşaması devam ediyor.');await refresh();
    }catch(e){message('HOLD · '+e.message,true);$('work-browser-note').textContent='Gerçek davranış kanıtı alınamadı.';}
    finally{window.clearTimeout(timeout);waiting=false;}
  }
  function renderCategories(items){const area=$('work-categories');area.replaceChildren();const cats=['Tümü',...new Set(items.map(x=>x.category))];
    for(const cat of cats){const b=put(area,'button',cat===currentFilter?'active':'',cat);b.type='button';b.setAttribute('aria-pressed',String(cat===currentFilter));
      b.addEventListener('click',()=>{currentFilter=cat;render();});}
  }
  function render(){const items=workData.items||[];
    $('work-count-all').textContent=String(items.length);
    $('work-count-waiting').textContent=String(items.filter(x=>x.state==='NOT_STARTED').length);
    $('work-count-active').textContent=String(workData.counts?.in_progress||0);
    $('work-count-done').textContent=String(workData.counts?.done_scoped||0);
    $('work-active-count').textContent=String(workData.counts?.in_progress||0);
    $('work-done-count').textContent=String(workData.counts?.done_scoped||0);
    const headline=$('ux-worklist-count');if(headline)headline.textContent=`${items.length} örnek iş · ${workData.counts?.done_scoped||0} kapsamlı testli · ${workData.counts?.in_progress||0} doğrulanıyor`;
    const cats=workData.catalogs||[];
    $('worklist-source').textContent=cats.some(x=>x.source_claim==='HFS_MANAGEMENT_OWNER_SUPPLIED')?'OWNER YÜKLEDİ · SARAY BAĞIMSIZ ONAYI AÇIK':'ÖRNEK LİSTE · SARAY KABULÜ DEĞİL';
    $('worklist-source').classList.add('hold');
    renderCategories(items);
    const area=$('work-catalog');area.replaceChildren();
    for(const item of items.filter(x=>currentFilter==='Tümü'||x.category===currentFilter)){
      const card=put(area,'article','work-card');put(card,'span','work-category',item.category+' · '+item.kind);
      put(card,'h3','',item.title);put(card,'p','',item.description);
      const bar=put(card,'div','work-actions');bar.append(renderState(item.state));
      const b=put(bar,'button','btn btn-small',item.state==='NOT_STARTED'?'İşi başlat':'İşi aç');
      b.type='button';b.addEventListener('click',()=>start(item));
    }
    if(!area.children.length)put(area,'p','placeholder','Bu türde iş bulunmuyor.');
    for(const [id,list] of [['work-active',workData.work_in_progress||[]],['work-done',workData.work_done||[]]]){
      const box=$(id);box.replaceChildren();
      if(!list.length)put(box,'p','placeholder',id==='work-active'?'Şu anda yürütülen veya onay bekleyen iş yok.':'Kanıtlı biten iş yok.');
      for(const item of list){const row=put(box,'article','work-board-item');put(row,'strong','',item.title);row.append(renderState(item.state));put(row,'small','small-note',item.next_action);
        if(item.task_id){const b=put(row,'button','btn btn-small','Görevi / makbuzu aç');b.addEventListener('click',()=>{window.ENGURU_SHOW_TASK(item.task_id);$('receipt').scrollIntoView({behavior:'smooth',block:'nearest'});});}
        if(item.state==='VERIFYING'&&item.kind==='HTML_EXAMPLE'){
          const b=put(row,'button','btn btn-small','HTML davranışını gerçek tarayıcıda sınayıp kaydet');b.addEventListener('click',()=>testHTML(item));
        }
      }
    }
  }
  async function refresh(){try{workData=await req('/api/worklist');render();}catch(e){message('HOLD · İş listesi alınamadı: '+e.message,true);}}
  async function importFile(){if(waiting)return;
    const file=$('worklist-file').files[0];if(!file){message('Önce yönetimden gelen JSON iş listesini seç.',true);return;}
    if(file.size>64000){message('HOLD · İş listesi 64 KB sınırını aşıyor.',true);return;}
    waiting=true;
    try{const catalog=JSON.parse(await file.text());const o=await req('/api/worklist/import',{catalog});
      message('Yerel liste kaydedildi: '+o.added+' yeni iş · revizyon '+o.revision+'. Saray kaynağının bağımsız kabulü ayrıdır.');
      currentFilter='Tümü';await refresh();
    }catch(e){message('HOLD · '+e.message,true);}finally{waiting=false;}
  }
  $('worklist-import').addEventListener('click',importFile);
  window.ENGURU_REFRESH_WORKLIST=refresh;
  refresh();window.setInterval(()=>{if(!document.hidden&&!waiting)refresh();},5000);
})();
