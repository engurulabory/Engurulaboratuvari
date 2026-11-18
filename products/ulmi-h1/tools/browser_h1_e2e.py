#!/usr/bin/env python3
"""Real browser E2E on a permitted runner, separated from real Qwen and owner UAT."""
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def server_ready(base, process, seconds=15):
    """Wait for the real HTTP server; avoid a race against browser navigation."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError('HOLD_BROWSER_SERVER_EXITED_BEFORE_READY')
        try:
            with urllib.request.urlopen(base + '/api/status', timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError, TimeoutError):
            pass
        time.sleep(0.1)
    raise RuntimeError('HOLD_BROWSER_SERVER_START_TIMEOUT')


def browser_options():
    options = {'headless': True, 'args': ['--no-sandbox']}
    # Explicit local executable is useful on isolated machines with system Chromium.
    # Managed-browser policy remains authoritative; setting this does not bypass it.
    binary = os.getenv('ULMI_CHROMIUM_EXECUTABLE', '')
    if binary:
        path = Path(binary)
        if not path.is_absolute() or not path.is_file() or path.is_symlink():
            raise RuntimeError('HOLD_BROWSER_EXECUTABLE_PATH')
        options['executable_path'] = str(path)
    return options


def main():
    with tempfile.TemporaryDirectory(prefix='ulmi-h1-browser-') as d:
        port = free_port()
        base = f'http://127.0.0.1:{port}'
        env = {**os.environ, 'ENGURU_H1_STATE_HOME': d, 'ENGURU_USTA_PORT': str(port)}
        process = subprocess.Popen(
            [sys.executable, '-B', str(ROOT/'PRODUCT/server.py')],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
        )
        try:
            server_ready(base, process)
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(**browser_options())
                try:
                    page = browser.new_page()
                    page.goto(base, wait_until='domcontentloaded', timeout=30000)
                    assert 'ULMi' in page.title(), page.title()
                    unique = 'ULMI H1 CI ' + uuid.uuid4().hex[:8]
                    page.locator('#project-title').fill(unique)
                    page.locator('#project-goal').fill('Çalışan HTML ürününün tarayıcı üzerinden doğrulanması')
                    page.locator('#save-project').click()
                    page.locator('#project-feedback').get_by_text('SQLite kaydı oluşturuldu', exact=False).wait_for(timeout=20000)
                    page.wait_for_function(
                        "document.querySelector('#project-list')?.selectedOptions?.[0]?.textContent?.includes('ULMI H1 CI')",
                        timeout=10000,
                    )
                    assert unique in page.locator('#project-list option:checked').inner_text()
                    page.locator('#chat-message').fill('Bu proje için yetkili kaynaklı teknik öneri ver')
                    page.locator('#chat-send').click()
                    # No genuine Qwen attached: the correct UI response is a visible HOLD.
                    page.locator('#chat-result').get_by_text('HOLD', exact=False).wait_for(timeout=20000)
                    print('BROWSER_H1_PROJECT_SQLITE_AND_CHAT_HOLD=PASS_SCOPED')
                finally:
                    browser.close()
        finally:
            process.terminate()
            try:
                process.communicate(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()


if __name__ == '__main__':
    main()
