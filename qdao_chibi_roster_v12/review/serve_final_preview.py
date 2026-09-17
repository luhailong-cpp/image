from pathlib import Path
import http.server, functools
SITE=Path(r'E:\work\image\qdao_chibi_roster_v12\review\site').resolve()
assert SITE.is_dir() and SITE.name=='site' and SITE.parent.name=='review'
class PreviewServer(http.server.ThreadingHTTPServer):
 request_queue_size=128
 daemon_threads=True
class Handler(http.server.SimpleHTTPRequestHandler):
 protocol_version='HTTP/1.1'
 def log_message(self,format,*args):
  pass
PreviewServer(('127.0.0.1',8871),functools.partial(Handler,directory=str(SITE))).serve_forever()
