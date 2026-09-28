"""Verify retained 08 runtime assets; never claim deleted originals were re-read."""
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
import hashlib, json, re
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent / '08-delivery-preview' / 'revisions' / 'final-v1'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
errors = []
def check(ok, note):
    if not ok: errors.append(note)
def local(value):
    p = (ROOT / value).resolve()
    if not p.is_relative_to(ROOT.resolve()): raise ValueError('Path outside final package: '+value)
    return p

m = read(ROOT / 'manifest.json')
before = read(ROOT / 'file-audit-before-cleanup.json')
check(before['status']=='passed_file_checks_only' and not before['errors'], 'Pre-cleanup source audit did not pass')
check(before['manifest_sha256']==sha(ROOT/'manifest.json'), 'Manifest differs from pre-cleanup source audit')
expected = {f'walk/{d}/{i:02d}' for d in m['directions'] for i in range(1,17)} | {f'idle/{d}' for d in m['directions']}
check(len(expected)==136 and {r['slot'] for r in m['files']}==expected and len(m['files'])==136, 'Missing or duplicate slots')
check(len({r['sha256'] for r in m['files']})==136, 'Repeated output SHA')
baseline = {r['slot']:r for r in before['files']}
for row in m['files']:
    p = local(row['path'])
    check(p.is_file() and sha(p)==row['sha256']==baseline[row['slot']]['output_sha256'], row['slot']+': output SHA changed')
    with Image.open(p) as im:
        check(im.size==(1024,1024) and im.mode=='RGBA' and im.format=='PNG', row['slot']+': format')
        check(im.getchannel('A').getextrema()==(0,255), row['slot']+': transparency')
    source_path = local(row['source_record'])
    check(sha(source_path)==row['source_record_sha256'], row['slot']+': source record')
    source=read(source_path)
    for name in ('request','receipt'):
        check(sha(source_path.parent/(name+'.json'))==source[name]['sha256'], row['slot']+': '+name+' evidence')
    gen=read(source_path.parent/'raw.png.generation.json')
    check(sha(source_path.parent/'prompt.txt')==gen['prompt']['sha256'],row['slot']+': prompt evidence')
    check(gen['sha256']==baseline[row['slot']]['raw_sha256'],row['slot']+': recorded source SHA')
timings=[]
check(len(m['gifs'])==16,'Need sixteen light/dark GIFs')
for row in m['gifs']:
    p=local(row['path']); check(sha(p)==row['sha256'],row['path']+': GIF SHA')
    with Image.open(p) as im:
        durations=[]
        for i in range(im.n_frames): im.seek(i); durations.append(im.info.get('duration'))
        check(durations==[30]*16 and im.info.get('loop')==0,row['path']+': 16 x 30ms infinite timing')
        timings.append({'path':row['path'],'durations_ms':durations})
for row in m['contact_sheets']:
    check(sha(local(row['path']))==row['sha256'],row['path']+': design preview SHA')
check(sha(ROOT/'browser-review.json')==m['visual_acceptance_sha256'],'Visual acceptance record changed')
html=(ROOT/'index.html').read_text(encoding='utf-8')
embedded=re.search(r'const M=(.*?), \$=id=>',html,re.S)
check(bool(embedded) and json.loads(embedded.group(1).replace('<\\/','</'))==m,'Viewer manifest differs from final manifest')
class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key,value in attrs:
            if key in ('href','src') and value and not value.startswith(('http:','https:','data:','#')):
                check(local(value.split('#')[0]).is_file(),'Broken current HTML link: '+value)
for name in ('index.html','previews.html'): Links().feed((ROOT/name).read_text(encoding='utf-8'))
report={'schema':'qdao08-retained-runtime-audit-v1','checkedAt':datetime.now(timezone.utc).isoformat(),
        'status':'passed' if not errors else 'failed','manifest_sha256':sha(ROOT/'manifest.json'),
        'walk':128,'idle':8,'gifs':timings,'errors':errors,'original_images_rechecked':False,
        'source_audit_before_cleanup_sha256':sha(ROOT/'file-audit-before-cleanup.json'),
        'limitations':'Validates retained final files and textual evidence against the pre-cleanup audit. Original generation images were deliberately removed; this is not a new source-image or client-runtime test.',
        'unity_validation':False,'formal_client_validation':False}
(ROOT/'runtime-audit-after-cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'errors':errors,'runtime_png':136,'gifs':16}))
raise SystemExit(1 if errors else 0)
