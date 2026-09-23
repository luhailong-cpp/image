"""Select reviewed S/SW sources, retaining original provenance and replacement history."""
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('direction', choices=['S', 'SW'])
p.add_argument('slot', help='01..16 or idle')
p.add_argument('version', type=int)
p.add_argument('--reason', required=True)
a = p.parse_args()
idle = a.slot == 'idle'
n = None if idle else int(a.slot)
assert idle or 1 <= n <= 16
batch = f'{a.direction}-idle-v{a.version}' if idle else f'{a.direction}{n:02d}-walk-v{a.version}'
d = R / '15-generation' / batch
slot = f'idle/{a.direction}.png' if idle else f'walk/{a.direction}/{n:02d}.png'
t = R / '15-delivery-preview/runtime' / slot
side = t.with_name(t.name + '.generation.json')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path, obj): path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
cmd = [sys.executable, str(R/'15-tools/archive_frame.py'), '--generation-dir', str(d), '--source', str(d/'raw.png'), '--request-json', str(d/'request.json'), '--receipt-json', str(d/'receipt.json'), '--direction', a.direction, '--kind', 'idle' if idle else 'walk', '--process']
if n is not None: cmd.extend(['--frame', str(n)])
r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf8')
if r.returncode: raise RuntimeError(r.stderr)
raw_sha = sha(d/'raw.png')
for other in (R/'15-delivery-preview/runtime').rglob('*.png.generation.json'):
    if other != side and read(other).get('derivedFrom', {}).get('sha256') == raw_sha:
        raise RuntimeError(f'Source already selected elsewhere: {other}')
old = read(side) if side.exists() else None
if old and old.get('derivedFrom', {}).get('sha256') == raw_sha:
    assert sha(t) == old['sha256']
    print(slot + ' already selected')
    raise SystemExit(0)
if old:
    assert sha(t) == old['sha256'], 'Existing delivery changed unexpectedly'
    hist = d/'selection-history.json'
    if hist.exists(): raise RuntimeError('Replacement history already exists; inspect before repeating')
    write(hist, {'replacedAt': datetime.now(timezone.utc).isoformat(), 'reason': a.reason, 'priorSidecar': old})
operation = read(d/'processing-fixed088-v1/processing.json')
source = d/'processing-fixed088-v1/final.png'
new = {'schemaVersion':1,'character':'15_water_dragon_scholar_boy','slot':slot,'file':t.name,'sha256':sha(source),'selectedAt':datetime.now(timezone.utc).isoformat(),'selectionAuthorization':'role15 owner reviewed replacement','selectionNote':a.reason,'derivedFrom':{'path':str(d/'raw.png'),'sha256':raw_sha,'generationRecord':str(d/'raw.png.generation.json')},'operation':operation,'actualModel':None,'actualQuality':None,'artReview':'pending_final_loop_review','clientValidation':'not_performed'}
t.parent.mkdir(parents=True, exist_ok=True)
t.write_bytes(source.read_bytes())
write(side, new)
assert sha(t) == new['sha256']
print(slot + ' selected ' + batch)
