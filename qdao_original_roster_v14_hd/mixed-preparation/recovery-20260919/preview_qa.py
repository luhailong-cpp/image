"""Temporary preview fixture using three copied real PNGs; never artwork approval."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'tools'))
import serve_mixed_preview as preview

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
def encode(value): return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def sha(data): return hashlib.sha256(data).hexdigest()

with tempfile.TemporaryDirectory(prefix='preview-qa-',dir=HERE) as temporary:
    fixture=Path(temporary)
    character='04_mountain_guardian_boy'
    old=ROOT.parent/'qdao_original_roster_v13/candidate'/character
    new=ROOT/'candidate'/character
    selected={'walk/SW/01.png':old,'walk/SW/02.png':new,'idle/SW.png':old}
    files=[]
    mappings={}
    for relative in sorted(preview.SLOTS):
        if relative in selected:
            source=selected[relative]
            data=(source/relative).read_bytes()
            write(fixture/relative,data)
            size=512 if source==old else 1024
            record=json.loads((source/'processing/frame-sources.json').read_text(encoding='utf-8-sig'))[relative]
            files.append({'path':relative,'availability':'present','width':size,'height':size,
                'pixels_per_unit':52 if size==512 else 104,'sha256':sha(data),
                'source_kind':'preserved-v13' if size==512 else 'native-hd',
                'native_cell_size':record['source'].get('native_size')})
            mappings[relative]={'original_record':record}
        else:
            files.append({'path':relative,'availability':'missing','width':1024,'height':1024,'sha256':None,
                'source_kind':'native-hd','pixels_per_unit':104})
    sources=encode({'actions':mappings,'scope':'PREVIEW QA FIXTURE ONLY'})
    preserved=encode({'scope':'PREVIEW QA FIXTURE ONLY; NOT AN ACTUAL PRESERVATION RECORD'})
    qc=encode({'scope':'PREVIEW QA FIXTURE ONLY; NOT ARTWORK QC'})
    manifest=encode({'character_id':character+' (preview QA fixture)','resolution_mode':'mixed-preserved-v1',
        'frame_count':16,'frame_duration_ms':30,'status':'preview-qa-partial-fixture','visual_review':'pending',
        'files':files,'sources_sha256':sha(sources),'preserved_snapshot_sha256':sha(preserved)})
    report=encode({'scope':'PREVIEW QA FIXTURE ONLY','manifest_sha256':sha(manifest),'qc_sha256':sha(qc)})
    for path,data in {'manifest.json':manifest,'qc.json':qc,'assembly-report.json':report,
        'processing/mixed-sources.json':sources,'processing/preserved-output-snapshot.json':preserved}.items():
        write(fixture/path,data)
    snapshot=preview.snapshot(fixture)
    assert not snapshot['complete'] and not snapshot['problems']
    assert sum(row['valid'] for row in snapshot['files'])==3
    assert snapshot['draft_review']['status']=='pending' and snapshot['draft_review']['evidence']==[]
    assert not any(v for k,v in snapshot['draft_review'].items() if k.endswith('_review'))
    changed=fixture/'walk/SW/02.png'
    original=changed.read_bytes();changed.write_bytes(original+b'QA CHANGED BYTES')
    assert any('SHA differs' in p for p in preview.snapshot(fixture)['problems'])
    changed.write_bytes(original)
    try: preview.safe_path(fixture,'../outside.png')
    except ValueError: pass
    else: raise AssertionError('Traversal was not rejected')
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'Preview UI fixture checks only, no artwork approval',
        'partial_slots_and_pending_review':'passed','SHA_mutation_rejected':'passed','traversal_rejected':'passed',
        'copied_actual_pngs':list(selected),'fixture_directory':str(fixture)}
    write(HERE/'preview-server-qa.json',encode(result))
    stop=threading.Event()
    base=preview.handler(fixture)
    class Handler(base):
        def do_GET(self):
            if self.path=='/qa-stop':
                self.reply(200,b'QA stopped','text/plain');stop.set()
            else: super().do_GET()
    server=ThreadingHTTPServer(('127.0.0.1',8877),Handler)
    server.timeout=1
    print('PREVIEW_QA_READY http://127.0.0.1:8877/',flush=True)
    try:
        while not stop.is_set(): server.handle_request()
    finally: server.server_close()
print('PREVIEW_QA_FINISHED temporary fixture cleaned',flush=True)
