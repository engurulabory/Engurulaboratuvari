import contextlib
import hashlib
import http.server
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from enguru_core import roles
from enguru_core.contracts import Rejected
from enguru_core.kernel import Kernel
from test_core import FixtureRoles


class Integrations(unittest.TestCase):
    def test_two_real_http_stub_role_requests_digest_and_separation(self):
        observed=[]; plan_sha=[None]
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self,*a):pass
            def do_GET(self):
                observed.append(('GET',self.path))
                self.send_response(200);self.end_headers()
                self.wfile.write(json.dumps({'models':[{'name':roles.MODEL,'digest':roles.DIGEST}]}).encode())
            def do_POST(self):
                obj=json.loads(self.rfile.read(int(self.headers['Content-Length'])));observed.append(('POST',obj))
                operation='plan_unique_jobs_repair' if 'manager rolüsün' in obj['system'] else 'apply_reviewed_unique_jobs_patch'
                self.send_response(200);self.end_headers()
                self.wfile.write(json.dumps({'model':roles.MODEL,'done':True,'done_reason':'stop',
                   'response':json.dumps({'operation':operation,'plan_sha256':plan_sha[0]})}).encode())
        server=http.server.HTTPServer(('127.0.0.1',0),Handler)
        t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
        try:
            with tempfile.TemporaryDirectory() as d,patch.object(roles,'BASE','http://127.0.0.1:'+str(server.server_port)):
                k=Kernel(Path(d)/'profile',roles.LocalRoles())
                try:
                    plan_sha[0]=k.plan('http-stub').sha
                    self.assertEqual(k.execute('http-stub','unique_jobs sıra onarımı')['state'],'DONE')
                    posts=[x[1] for x in observed if x[0]=='POST'];self.assertEqual(len(posts),2)
                    self.assertNotEqual(posts[0]['system'],posts[1]['system'])
                    self.assertTrue(all(x['model']==roles.MODEL for x in posts))
                finally:k.close()
        finally:server.shutdown();server.server_close();t.join(2)

    def test_wrong_model_and_malformed_reply_hold(self):
        with tempfile.TemporaryDirectory() as d:
            k=Kernel(Path(d)/'profile',roles.LocalRoles())
            try:
                with patch.object(roles,'local_http',return_value={'models':[{'name':roles.MODEL,'digest':'wrong'}]}):
                    with self.assertRaisesRegex(Rejected,'MODEL_DIGEST'):k.roles.identity()
                with patch.object(k.roles,'identity',return_value=roles.DIGEST),patch.object(roles,'local_http',return_value={
                    'model':roles.MODEL,'done':True,'done_reason':'stop','response':'{"operation":"shell"}'}):
                    with self.assertRaises(Rejected):k.execute('bad-model','unique_jobs sıra onarımı')
                    self.assertEqual(k.snapshot()['state'],'HOLD')
            finally:k.close()

    def test_pause_at_pre_action_boundary_and_live_recovery_denied(self):
        with tempfile.TemporaryDirectory() as d:
            k=Kernel(Path(d)/'profile',FixtureRoles())
            try:
                original=k.roles.propose
                def pause(role,text,plan):
                    if role=='executor':
                        with self.assertRaises(Rejected):k.recover()
                        k.ledger.control(True)
                    return original(role,text,plan)
                k.roles.propose=pause
                with self.assertRaisesRegex(Rejected,'PAUSED_AT_SAFE_BOUNDARY'):k.execute('paused','unique_jobs sıra onarımı')
                self.assertFalse((k.root/'jobs').exists())
                self.assertEqual(k.snapshot()['state'],'HOLD')
            finally:k.close()

    def test_canonical_sources_and_75_criterion_text(self):
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
        from validate import validate
        self.assertEqual(validate()['criteria_text_exact'],75)
