#!/usr/bin/env python3
"""Real Chromium + original UI code + synthetic API: project selection race test.

This test is NOT real HTTP/SQLite/Qwen E2E; the purpose is a reliable RED/GREEN
regression for stale in-flight chat replies appearing under a different project.
"""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_browser_dom_isolated import render_html


def run(browser_path: str):
    html, _ = render_html()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'], **({'executable_path': browser_path} if browser_path else {}))
        try:
            page = browser.new_page()
            page_errors = []
            page.on('pageerror', lambda e: page_errors.append(str(e)))
            page.set_content(html, wait_until='domcontentloaded')
            def save(title):
                page.locator('#project-title').fill(title)
                page.locator('#project-goal').fill('Bu projeye ait ayrı geçmişin kontrolü')
                page.locator('#save-project').click()
                page.locator('#project-feedback').get_by_text('SQLite kaydı oluşturuldu').wait_for()
            save('Proje A')
            page.locator('#chat-message').fill('A için kaynak önerisi')
            page.locator('#chat-send').click()
            page.locator('#chat-result').get_by_text('Kaynaklı öneri').wait_for()
            save('Proje B')
            page.locator('#chat-history').get_by_text('Bu projede kayıtlı sohbet mesajı bulunmuyor.').wait_for()
            # Switching to B must reset A's previous completion marker.
            first = page.locator('#chat-result').inner_text()
            assert 'Kaynaklı öneri' not in first, f'STALE_PRIOR_PROJECT_RESULT_VISIBLE: {first}'

            # Defer an actual synthetic response and change project before it returns.
            page.evaluate('''() => {
              const original = window.fetch;
              window.__DELAYED_CHAT = {pending:0};
              window.fetch = (path,opts) => {
                if (path==='/api/desk/project-chat') {
                  window.__DELAYED_CHAT.pending++;
                  return new Promise((resolve,reject) => {
                    window.__DELAYED_CHAT.resolve=() => original(path,opts).then(resolve,reject);
                    window.__DELAYED_CHAT.reject=() => reject(new Error('SIMULATED_TIMEOUT'));
                  });
                }
                return original(path,opts);
              };
            }''')
            page.locator('#chat-message').fill('Yalnızca B için gecikmiş öneri')
            page.locator('#chat-send').click()
            page.wait_for_function('window.__DELAYED_CHAT.pending===1')
            page.locator('#project-list').select_option('p1')
            page.locator('#chat-history').get_by_text('A için kaynak önerisi').wait_for()
            text_before = page.locator('#chat-result').inner_text()
            page.evaluate('window.__DELAYED_CHAT.resolve()')
            page.wait_for_function("document.querySelector('#chat-send').disabled===false")
            page.wait_for_timeout(150)
            text_after = page.locator('#chat-result').inner_text()
            assert text_after == text_before, f'INFLIGHT_OTHER_PROJECT_COMPLETION_LEAK: {text_before} => {text_after}'
            assert page.locator('#chat-message').input_value() == 'Yalnızca B için gecikmiş öneri', 'MESSAGE_DRAFT_LOST_AFTER_PROJECT_SWITCH'
            assert 'Yalnızca B için gecikmiş öneri' not in page.locator('#chat-history').inner_text(), 'B_CHAT_SHOWN_IN_A'
            # Error response from another project's in-flight request must also
            # remain scoped to that original project, not the newly chosen one.
            page.locator('#chat-message').fill('A için geciken hatalı istek')
            page.locator('#chat-send').click()
            page.wait_for_function('window.__DELAYED_CHAT.pending===2')
            page.locator('#project-list').select_option('p2')
            page.locator('#chat-history').get_by_text('Yalnızca B için gecikmiş öneri').wait_for()
            error_before = page.locator('#chat-result').inner_text()
            page.evaluate('window.__DELAYED_CHAT.reject()')
            page.wait_for_function("document.querySelector('#chat-send').disabled===false")
            page.wait_for_timeout(150)
            assert page.locator('#chat-result').inner_text()==error_before, 'STALE_OTHER_PROJECT_ERROR_VISIBLE'
            assert 'SIMULATED_TIMEOUT' not in page.locator('#chat-result').inner_text()
            assert page.locator('#chat-message').input_value()=='A için geciken hatalı istek', 'ERROR_WIP_DRAFT_LOST'
            assert not page_errors, page_errors
            return {'status':'PASS_SCOPED_CHROMIUM_MOCK_API','checks':[
              'SWITCH_CLEARS_PREVIOUS_PROJECT_RESULT',
              'INFLIGHT_OTHER_PROJECT_SUCCESS_CANNOT_UPDATE_SELECTED_PROJECT',
              'CHAT_INPUT_PRESERVED_AFTER_SWITCH',
              'NEW_PROJECT_HISTORY_ISOLATED',
              'INFLIGHT_OTHER_PROJECT_FAILURE_CANNOT_UPDATE_SELECTED_PROJECT',
              'ERROR_DRAFT_PRESERVED_AFTER_PROJECT_SWITCH',
              'NO_SCRIPT_ERRORS'], 'source_js_sha256':hashlib.sha256((Path(__file__).resolve().parents[1]/'PRODUCT'/'app.js').read_bytes()).hexdigest(), 'real_http_sqlite':'NOT_TESTED_BY_THIS_TEST', 'real_qwen':'NOT_TESTED_BY_THIS_TEST'}
        finally:
            browser.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output');parser.add_argument('--browser',default='')
    arg=parser.parse_args()
    result=run(arg.browser)
    if arg.output:Path(arg.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False))
