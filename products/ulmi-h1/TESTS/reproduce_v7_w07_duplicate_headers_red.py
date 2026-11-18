from pathlib import Path
import json, sys, tempfile, os, threading, socket, re
from urllib.request import urlopen
p=Path(__file__).parent/'base/PRODUCT'
sys.path.insert(0,str(p))
with tempfile.TemporaryDirectory(prefix='ulmi-w07-headers-red-') as d:
 os.environ['ENGURU_H1_STATE_HOME']=d
 import server as s
 srv=s.make_server(0); t=threading.Thread(target=srv.serve_forever,daemon=True);t.start();port=srv.server_port
 try:
  import urllib.request
  page=urlopen(f'http://127.0.0.1:{port}/uat-final').read().decode();tok=re.search(r'content="([a-f0-9]{48})"',page).group(1)
  payload=b'{"kind":"python"}'
  cases={
   'DUP_ORIGIN': [f'Origin: http://127.0.0.1:{port}','Origin: https://evil.test',f'X-Enguru-Token: {tok}'],
   'DUP_TOKEN': [f'Origin: http://127.0.0.1:{port}',f'X-Enguru-Token: {tok}','X-Enguru-Token: attacker'],
   'DUP_HOST': [f'Origin: http://127.0.0.1:{port}',f'X-Enguru-Token: {tok}','Host: evil.test']
  }
  for name,extras in cases.items():
   hdr=['POST /api/scaffold HTTP/1.1',f'Host: 127.0.0.1:{port}',*extras,f'Content-Length: {len(payload)}','Content-Type: application/json','Connection: close','','']
   with socket.create_connection(('127.0.0.1',port),timeout=3) as sock:
    sock.settimeout(3);sock.sendall('\r\n'.join(hdr).encode()+payload);b=b''
    while 1:
     try:chunk=sock.recv(4096)
     except socket.timeout:break
     if not chunk:break
     b+=chunk
   code=int(re.match(rb'HTTP/1\.1 (\d+)',b).group(1))
   print(name,'STATUS',code,'TASK_ROWS',len(s.list_tasks()),flush=True)
 finally:
  srv.shutdown();srv.server_close();t.join()
