"""Real socket/HTTP failure tests; these are not hosted-provider acceptance."""
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from nexus_integrations import _json_request,IntegrationError
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        if self.path=='/timeout': time.sleep(.2)
        code={'/auth':401,'/permission':403,'/duplicate':409}.get(self.path,200)
        self.send_response(code);self.end_headers()
        try:self.wfile.write(b'{}')
        except (BrokenPipeError,ConnectionResetError):pass
class HttpFailureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def test_real_http_failures_redacted(self):
        for path,message in [('/auth','authentication_failed'),('/permission','permission_denied'),('/duplicate','duplicate_conflict'),('/timeout','remote_request_failed')]:
            with self.subTest(path=path),self.assertRaisesRegex(IntegrationError,'^'+message+'$'):
                _json_request(self.base+path,timeout=.05)
