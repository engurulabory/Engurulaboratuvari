#!/usr/bin/env python3
"""Real Chromium H1 browser smoke: project creation, SQLite readback, chat boundary.

No real Qwen and no owner UAT. Runs only on permitted GitHub runner.
"""
import os, re, socket, subprocess, sys, tempfile, time, uuid
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1',0));return s.getsockname()[1]
with tempfile.TemporaryDirectory(prefix='ulmi-h1-browser-') as d:
    port=free_port();base=f'http://127.0.0.1:{port}'
    env={**os.environ,'ENGURU_H1_STATE_HOME':d,'ENGURU_USTA_PORT':str(port)}
    process=subprocess.Popen([sys.executable,'-B',str(ROOT/'PRODUCT/server.py')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page()
            page.goto(base,wait_until='domcontentloaded',timeout=30000)
            assert 'ULMi' in page.title(),page.title()
            unique='ULMI H1 CI '+uuid.uuid4().hex[:8]
            page.locator('#project-title').fill(unique)
            page.locator('#project-goal').fill('Çalışan bir HTML uygulamasının gerçek mühendislik doğrulaması')
            page.locator('#save-project').click()
            page.locator('#project-feedback').get_by_text('SQLite kaydı oluşturuldu',exact=False).wait_for(timeout=20000)
            page.wait_for_function("document.querySelector('#project-list')?.selectedOptions?.[0]?.textContent?.includes('ULMI H1 CI')",timeout=10000)
            assert unique in page.locator('#project-list option:checked').inner_text()
            page.locator('#chat-message').fill('Bu proje için yetkili kaynaklı teknik öneri ver')
            page.locator('#chat-send').click()
            # No genuine model attached; fail-closed HOLD is the correct, non-executing behavior.
            page.locator('#chat-result').get_by_text('HOLD',exact=False).wait_for(timeout=20000)
            print('BROWSER_H1_PROJECT_SQLITE_AND_CHAT_HOLD=PASS_SCOPED')
            browser.close()
    finally:
        process.terminate()
        try:process.communicate(timeout=8)
        except subprocess.TimeoutExpired:process.kill();process.communicate()
