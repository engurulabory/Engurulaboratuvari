"""Read-only loopback HTTP API. No network source fetching at runtime."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from .core import Core, canonical

class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,address,core=None):
        if address[0]!='127.0.0.1': raise ValueError('loopback only')
        self.core=core or Core()
        super().__init__(address,Handler)

class Handler(BaseHTTPRequestHandler):
    server_version='FetihCore/0.1'
    def log_message(self,*args): pass
    def send_json(self,status,value):
        body=canonical(value)
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers();self.wfile.write(body)
    def do_GET(self):
        # Resist browser cross-origin/DNS-rebinding access; not a multi-user auth service.
        host=self.headers.get('Host','')
        if host!=f'127.0.0.1:{self.server.server_port}' or self.headers.get('Origin'):
            self.send_json(403,{'error':'local direct clients only'});return
        if len(self.path)>2048:
            self.send_json(414,{'error':'URI too long'});return
        p=urlsplit(self.path);q=parse_qs(p.query,keep_blank_values=True);c=self.server.core
        if set(q)-({'concept'} if p.path=='/graph' else {'id'} if p.path=='/verses' else set()) or any(len(v)!=1 for v in q.values()):
            self.send_json(400,{'error':'invalid query'});return
        routes={'/health':lambda:{'status':'ok','version':'0.1.0','source_integrity':'PASS','interpretation_acceptance':'HOLD'},
                '/verses':lambda:c.verses,'/sources':lambda:c.sources,'/concepts':lambda:c.records,
                '/graph':lambda:c.graph(q.get('concept',[None])[0]),'/models':c.models,
                '/hypotheses':c.hypotheses,'/review-queue':lambda:c.records,'/export':c.export}
        if p.path=='/verses' and 'id' in q:
            v=q['id'][0]
            if v not in c.by_verse:self.send_json(404,{'error':'verse outside scope'});return
            self.send_json(200,{'id':v,'text':c.by_verse[v]});return
        if p.path not in routes:self.send_json(404,{'error':'route not found'});return
        self.send_json(200,routes[p.path]())
    def do_POST(self): self.send_json(405,{'error':'read-only API'})
    do_PUT=do_POST
    do_DELETE=do_POST
    do_PATCH=do_POST
