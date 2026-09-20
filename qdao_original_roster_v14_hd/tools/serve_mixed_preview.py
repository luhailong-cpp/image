"""Read-only loopback preview of one immutable mixed assembly; never approves it."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import struct
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
PAGE = Path(__file__).with_name('mixed-preview.html')
DIRECTIONS = ('N','NE','E','SE','S','SW','W','NW')
SLOTS = {f'walk/{d}/{i:02d}.png' for d in DIRECTIONS for i in range(1,17)} | {f'idle/{d}.png' for d in DIRECTIONS} | {'portrait.png'}
BINDINGS = {'reviewed_input_manifest_sha256':'manifest.json','reviewed_input_qc_sha256':'qc.json',
    'reviewed_input_assembly_report_sha256':'assembly-report.json','reviewed_input_sources_sha256':'processing/mixed-sources.json',
    'reviewed_preserved_snapshot_sha256':'processing/preserved-output-snapshot.json'}
CHECKS = ('normal_size','enlarged','seam_15_16_01','anatomical_contacts_01_09','native_resolution','closeup_1080p','mixed_resolution_transition','preserved_identity')

def safe_path(root, relative):
    if not isinstance(relative,str) or not relative or '\\' in relative:
        raise ValueError('Invalid relative path')
    path = root / relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path escapes selected assembly')
    for node in (path,*path.parents):
        if node.is_symlink() or (hasattr(node,'is_junction') and node.is_junction()):
            raise ValueError('Linked paths are unsupported')
        if node == root:
            break
    return path

def assembly_path(value):
    path = Path(value).absolute()
    base = ROOT / 'mixed-candidates'
    if path == base or not path.is_relative_to(base) or not path.is_dir():
        raise ValueError('Use an existing immutable mixed-candidates/run/character directory')
    safe_path(ROOT, path.relative_to(ROOT).as_posix())
    return path.resolve()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def snapshot(directory):
    documents, hashes, original_bytes = {}, {}, {}
    for field, relative in BINDINGS.items():
        data = safe_path(directory,relative).read_bytes()
        documents[relative] = json.loads(data.decode('utf-8-sig'))
        hashes[field] = digest(data)
        original_bytes[relative] = data
    manifest = documents['manifest.json']
    if manifest.get('resolution_mode') != 'mixed-preserved-v1' or manifest.get('frame_count') != 16 or manifest.get('frame_duration_ms') != 30:
        raise ValueError('Expected the mixed-preserved-v1 16 × 30 ms contract')
    rows = manifest.get('files',[])
    if len(rows) != 137 or {r.get('path') for r in rows} != SLOTS:
        raise ValueError('Manifest must declare the exact 137 distinct PNG slots')
    source_actions = documents['processing/mixed-sources.json'].get('actions',{})
    files, problems, actual_hashes = [], [], {}
    for row in rows:
        relative = row['path']
        path = safe_path(directory,relative)
        info = {**row,'actual_sha256':None,'actual_width':None,'actual_height':None,'valid':False}
        if row.get('availability') != 'present':
            if path.exists(): problems.append(relative+': undeclared file exists')
            info['error'] = '尚未生成'
        else:
            try:
                before = path.stat()
                data = path.read_bytes()
                after = path.stat()
                if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns): raise ValueError('file changed while reading')
                if data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR': raise ValueError('not a PNG')
                width,height = struct.unpack('>II',data[16:24])
                actual = digest(data)
                actual_hashes[relative] = actual
                info.update(actual_sha256=actual,actual_width=width,actual_height=height)
                if actual != row.get('sha256'): raise ValueError('SHA differs from manifest')
                if [width,height] != [row.get('width'),row.get('height')]: raise ValueError('dimensions differ from manifest')
                if relative != 'portrait.png' and (width not in (512,1024) or width!=height or row.get('pixels_per_unit')!=width/512*52):
                    raise ValueError('invalid mixed resolution/PPU geometry')
                info['valid'] = True
            except (OSError,ValueError,struct.error) as error:
                info['error'] = str(error)
                problems.append(relative+': '+str(error))
        record = source_actions.get(relative,{}).get('original_record',{})
        info['provenance'] = {'source_kind':row.get('source_kind'),'native_cell_size':row.get('native_cell_size'),
            'raw_sha256':record.get('source',{}).get('sha256'),'raw_path':record.get('source',{}).get('path'),
            'receipt_sha256':record.get('generation',{}).get('receipt',{}).get('sha256'),
            'model_actual':record.get('generation',{}).get('model_actual','未披露')}
        files.append(info)
    report = documents['assembly-report.json']
    if report.get('manifest_sha256') != hashes['reviewed_input_manifest_sha256']: problems.append('assembly report manifest SHA differs')
    if report.get('qc_sha256') != hashes['reviewed_input_qc_sha256']: problems.append('assembly report QC SHA differs')
    if manifest.get('sources_sha256') != hashes['reviewed_input_sources_sha256']: problems.append('source map SHA differs')
    if manifest.get('preserved_snapshot_sha256') != hashes['reviewed_preserved_snapshot_sha256']: problems.append('preserved snapshot SHA differs')
    for relative,data in original_bytes.items():
        if safe_path(directory,relative).read_bytes()!=data: problems.append(relative+': metadata changed during capture')
    draft = {'schema':'qdao-original-v14-mixed/visual-review-input-v1','character_id':manifest['character_id'],
        'status':'pending','reviewer':'','reviewed_at_utc':None,**hashes,'reviewed_artifacts':actual_hashes,
        'reviewed_directions':[],'notes_by_direction':{d:'' for d in DIRECTIONS},'evidence':[],
        **{name+'_review':False for name in CHECKS},**{name+'_notes':'' for name in CHECKS[4:]}}
    return {'schema':'qdao-mixed-preview-snapshot-v1','captured_utc':datetime.now(timezone.utc).isoformat(),
        'assembly':str(directory),'character_id':manifest['character_id'],'status':manifest.get('status'),
        'visual_review':manifest.get('visual_review'),'files':files,'bindings':hashes,'problems':problems,
        'complete':len(actual_hashes)==137 and not problems,'draft_review':draft,
        'scope':'Current file hashes and PNG geometry only; independent reconstruction and actual visual approval remain separate.'}

def handler(directory):
    class Handler(BaseHTTPRequestHandler):
        def reply(self,status,data,mime):
            self.send_response(status)
            self.send_header('Content-Type',mime)
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' blob:; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)
        def do_GET(self):
            try:
                if self.headers.get('Host','').split(':')[0] not in ('127.0.0.1','localhost'):
                    self.reply(403,b'Loopback only','text/plain'); return
                path = unquote(urlparse(self.path).path)
                if path == '/':
                    self.reply(200,PAGE.read_bytes(),'text/html; charset=utf-8')
                elif path == '/api/review':
                    if directory is None: raise ValueError('启动时传入 --assembly 指向 mixed-candidates/run/角色目录。')
                    self.reply(200,json.dumps(snapshot(directory),ensure_ascii=False).encode(),'application/json; charset=utf-8')
                elif path.startswith('/asset/') and directory is not None:
                    relative = path[len('/asset/'):]
                    if relative not in SLOTS: raise ValueError('Only declared action/portrait PNGs can be served')
                    self.reply(200,safe_path(directory,relative).read_bytes(),'image/png')
                else:
                    self.reply(404,b'Not found','text/plain')
            except (OSError,ValueError,KeyError) as error:
                self.reply(400,json.dumps({'error':str(error)},ensure_ascii=False).encode(),'application/json; charset=utf-8')
        def log_message(self,format,*args):
            if args and str(args[1] if len(args)>1 else '') not in ('200','304'):
                super().log_message(format,*args)
    return Handler

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assembly',type=assembly_path)
    parser.add_argument('--port',type=int,default=8876)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1',args.port),handler(args.assembly))
    print(f'Mixed preview http://127.0.0.1:{args.port}/ assembly={args.assembly or "none"}; read-only',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__': main()
