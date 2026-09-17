"""Serve the independent V13 directory on loopback only."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        super().end_headers()
    def translate_path(self,path):
        candidate=Path(super().translate_path(path)).resolve()
        if not candidate.is_relative_to(ROOT): return str(ROOT/'__not_found__')
        return str(candidate)
if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8874); args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT)))
    print(f'V13 preview: http://127.0.0.1:{args.port}/; root={ROOT}',flush=True)
    server.serve_forever()

