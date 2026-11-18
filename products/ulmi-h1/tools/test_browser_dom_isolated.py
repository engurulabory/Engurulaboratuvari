#!/usr/bin/env python3
"""Real Chromium DOM test of the original ULMi HTML/CSS/JS with synthetic APIs.

This is an offline UI/JS test. It does NOT prove live HTTP, SQLite,
Qwen, owner UAT, or a browser navigating to a blocked loopback URL.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRODUCT = ROOT / 'PRODUCT'

MOCK = r'''
window.__ULMI_MOCK = { projects:[], chats:{}, tasks:{}, requests:[], activeTask:null, executions:0, violations:[] };
// about:blank is not a secure context; loopback HTTP is. This mock supplies only test IDs.
if(typeof crypto.randomUUID !== 'function') Object.defineProperty(crypto, 'randomUUID', {value:()=> 'mock-uuid-'+String(Math.floor(Math.random()*1e9))});
const SHA = 'a'.repeat(64);
const response = (body,status=200)=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json'}});
window.fetch = async function(path,opts={}){
 const u=new URL(path,'http://ulmi.test');
 const method=opts.method||'GET';
 const data=opts.body?JSON.parse(opts.body):{};
 const st=window.__ULMI_MOCK;
 st.requests.push({path:u.pathname,method,data});
 if(opts.headers?.['X-Enguru-Token']!=='TEST_RENDER_ONLY')st.violations.push('missing token');
 if(u.pathname==='/api/status')return response({network:'LOOPBACK_ONLY',version:'UI_MOCK_ONLY'});
 if(u.pathname==='/api/tasks')return response({tasks:Object.values(st.tasks)});
 if(u.pathname==='/api/maps')return response({maps:[]});
 if(u.pathname==='/api/desk/projects' && method==='GET')return response({projects:st.projects});
 if(u.pathname==='/api/desk/projects/save' && method==='POST'){
   const project={id:'p'+(st.projects.length+1),title:data.title,goal:data.goal,sha256:SHA};
   st.projects.unshift(project);st.chats[project.id]=[];
   return response({project});
 }
 if(u.pathname==='/api/desk/history'){
   const id=u.searchParams.get('project_id');
   return response({source:'H1_SQLITE',project_id:id,messages:st.chats[id]||[]});
 }
 if(u.pathname==='/api/desk/project-chat' && method==='POST'){
   const p=st.projects.find(p=>p.id===data.project_id);
   if(!p || data.project_sha256!==p.sha256 || data.requested_action!=='ADVISE_ONLY')
     return response({reason:'HOLD_CHAT_SOURCE_OR_ACTION'},409);
   const reply={state:'HOLD_REAL_QWEN',execution_state:'NOT_EXECUTED',
     model_output:'<img src=x onerror="window.__XSS__=true">',
     route_receipt:{provider:'MOCK_ONLY',model:'NO_REAL_MODEL'},source_receipts:[]};
   st.chats[p.id].push({user_text:data.text,saved_at:'2026-11-18T00:00:00Z',response:reply});
   return response({state:reply.state,execution_state:reply.execution_state,project_id:p.id,project_sha256:p.sha256});
 }
 if(u.pathname==='/api/scaffold' && method==='POST'){
   const id='t'+(Object.keys(st.tasks).length+1);
   const task={task_id:id,status:'READY',path:'mock-'+data.kind+'.html',origin:'SCOPED_TEMPLATE_HTML',
     plan_sha256:SHA,content:'<button>Gerçek test ayrı</button>'};
   st.tasks[id]=task;st.activeTask=id;return response(task);
 }
 if(u.pathname==='/api/execute' && method==='POST'){
   const t=st.tasks[data.task_id];if(!t)return response({reason:'missing task'},404);
   st.executions++;
   t.status='PASS_SCOPED';
   t.receipt={path:t.path,output_sha256:SHA,readback_sha256:SHA,readback:'PASS',source_origin:'SCOPED_TEMPLATE_HTML',
     functional_test:{method:'MOCK_ONLY',status:'NOT_TESTED'}};
   return response({status:'PASS_SCOPED',receipt:t.receipt});
 }
 if(u.pathname==='/api/task')return response({task:st.tasks[u.searchParams.get('task_id')]||null});
 if(u.pathname==='/api/verify')return response({match:true,sha256:SHA,verifier:'MOCK_ONLY'});
 if(u.pathname==='/api/file')return response({content:'Mock source only'});
 return response({error:'UNEXPECTED_STUB_URL '+u.pathname},404);
};
'''

def render_html():
    h=(PRODUCT/'index.html').read_text(encoding='utf-8')
    css=(PRODUCT/'style.css').read_text(encoding='utf-8')
    js=(PRODUCT/'app.js').read_text(encoding='utf-8')
    assert h.count('<script defer src="/app.js"></script>')==1
    assert h.count('<link rel="stylesheet" href="/style.css">')==1
    assert h.count('__ENGURU_CSRF__')==1
    h=h.replace('<script defer src="/app.js"></script>','')
    h=h.replace('<link rel="stylesheet" href="/style.css">','<style>'+css+'</style>')
    h=h.replace('__ENGURU_CSRF__','TEST_RENDER_ONLY')
    assert '</script>' not in js.lower()
    return h.replace('</body>', '<script>'+MOCK+'</script><script>'+js+'</script></body>'),[h,css,js]

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument('--output',required=True)
    pa.add_argument('--screenshot',required=True)
    pa.add_argument('--browser', default=os.environ.get('ULMI_CHROMIUM_EXECUTABLE','/usr/bin/chromium'))
    args=pa.parse_args()
    b=pathlib.Path(args.browser)
    if not b.is_absolute() or not b.is_file() or b.is_symlink():
        raise SystemExit('HOLD_BROWSER_BINARY_INVALID')
    out=pathlib.Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    shot=pathlib.Path(args.screenshot);shot.parent.mkdir(parents=True,exist_ok=True)
    html,parts=render_html()
    tests=[]
    def test(name, action):
        action();tests.append({'id':name,'state':'PASS_SCOPED_RENDERED_DOM_MOCK_API'})
        print('PASS_SCOPED',name,flush=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path=str(b),args=['--no-sandbox'])
        try:
            page=browser.new_page(viewport={'width':1440,'height':980},device_scale_factor=1)
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.set_content(html,wait_until='domcontentloaded')
            test('UI_RENDER', lambda: (page.get_by_role('heading',name='Emin · Maya | Proje sohbeti').wait_for(),
                  page.get_by_text('İyi fikirleri,').first.wait_for()))
            test('INITIAL_MOCK_API',lambda: page.locator('#metric-server').get_by_text('Canlı · Yerel HTTP').wait_for())
            test('PROJECT_REQUIRED',lambda: (page.locator('#chat-message').fill('Soru'),page.locator('#chat-send').click(),
                  page.locator('#chat-result').get_by_text('Önce SQLite').wait_for()))
            bad_name='<img src=x onerror="window.__XSS__=true">'
            def savefirst():
                page.locator('#project-title').fill(bad_name)
                page.locator('#project-goal').fill('İzole güvenlik denemesi')
                page.locator('#save-project').click()
                page.locator('#project-feedback').get_by_text('SQLite kaydı oluşturuldu').wait_for()
                assert page.locator('#project-list option:checked').inner_text().startswith(bad_name)
            test('PROJECT_CREATE_DISPLAY_AS_TEXT',savefirst)
            def chatfirst():
                page.locator('#chat-message').fill('Kaynaklı öneri ve model sınırı nedir?')
                page.locator('#chat-send').click()
                page.locator('#chat-result').get_by_text('İcra: NOT_EXECUTED').wait_for()
                page.locator('#chat-history').get_by_text('Kaynaklı öneri ve model sınırı nedir?').wait_for()
            test('CHAT_ADVISE_ONLY_WITH_MODEL_HOLD',chatfirst)
            def xss():
                assert page.evaluate('window.__XSS__ === undefined')
                assert page.locator('#chat-history img').count()==0
                assert page.locator('#project-list img').count()==0
                assert page.locator('#chat-history').get_by_text('<img src=x onerror=',exact=False).count()>0
            test('USER_AND_MODEL_XSS_TEXT_ONLY',xss)
            def second():
                page.locator('#project-title').fill('Proje 2')
                page.locator('#project-goal').fill('İkinci projenin özel görevi')
                page.locator('#save-project').click()
                page.locator('#project-feedback').get_by_text('SQLite kaydı oluşturuldu').wait_for()
                page.locator('#chat-history').get_by_text('Bu projede kayıtlı sohbet mesajı bulunmuyor.').wait_for()
                page.locator('#project-list').select_option('p1')
                page.locator('#chat-history').get_by_text('Kaynaklı öneri ve model sınırı nedir?').wait_for()
            test('CROSS_PROJECT_HISTORY_ISOLATION',second)
            def plan():
                page.locator('#choice-html').click()
                page.locator('#plan-button').click()
                page.locator('#plan-status').get_by_text('READY').wait_for()
                assert not page.locator('#execute-button').is_disabled()
            test('PLAN_REQUIRES_SEPARATE_EXECUTE',plan)
            def execution():
                assert page.evaluate('window.__ULMI_MOCK.executions')==0
                page.locator('#execute-button').click()
                page.locator('#receipt-panel').wait_for(state='visible')
                page.locator('#receipt-summary').get_by_text('SHA geri okuması PASS').wait_for()
                assert page.evaluate('window.__ULMI_MOCK.executions')==1
            test('EXPLICIT_EXECUTE_AND_RECEIPT_UI',execution)
            def assertions():
                assert not errors,errors
                x=page.evaluate('window.__ULMI_MOCK')
                assert x['violations']==[],x['violations']
                messages=[y for y in x['requests'] if y['path']=='/api/desk/project-chat']
                assert len(messages)==1 and messages[0]['data']['requested_action']=='ADVISE_ONLY'
                assert x['executions']==1
            test('NO_JAVASCRIPT_ERRORS_AND_EXPECTED_CALLS',assertions)
            # Persistent, visible provenance: screenshot must never resemble a live model/DB PASS.
            page.evaluate("""() => {
              const tag=document.createElement('div');tag.id='ulmi-mock-provenance';
              tag.textContent='TARAYICI DOM TESTİ · API MOCK · GERÇEK QWEN / SQLITE DEĞİL';
              Object.assign(tag.style,{position:'fixed',top:'0',left:'0',right:'0',zIndex:'100000',
                padding:'8px',fontFamily:'monospace',fontSize:'13px',fontWeight:'bold',
                background:'#231f20',color:'white',textAlign:'center'});
              document.body.append(tag);
            }""")
            page.screenshot(path=str(shot),full_page=True)
        finally:
            browser.close()
    import hashlib
    report={
      'schema':'ulmi.h1.rendered-dom-mock-api/v1',
      'source':'REAL_PRODUCT_INDEX_CSS_AND_JS',
      'source_sha256':{n:hashlib.sha256(s.encode('utf8')).hexdigest() for n,s in zip(['HTML','CSS','JS'],parts)},
      'model':'NO_REAL_QWEN', 'backend':'MOCK_ONLY_NO_REAL_HTTP_SQLITE',
      'full_http_e2e':'HOLD_BROWSER_ADMIN_POLICY',
      'owner_uat':'NOT_TESTED',
      'tests':tests, 'count':len(tests), 'status':'PASS_SCOPED_RENDERED_DOM_MOCK_API',
      'screenshot_sha256':hashlib.sha256(shot.read_bytes()).hexdigest()
    }
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':report['status'],'tests':len(tests),'screenshot':str(shot)},ensure_ascii=False))

if __name__=='__main__': main()
