"""Dry-run by default. Explicit --apply imports only audited 06 E04/E06/E13 raw."""
from pathlib import Path
from types import SimpleNamespace
import argparse, hashlib, importlib.util, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CHAR='06_thunder_caster_boy'
GEN=ROOT/'generation'/CHAR
OUT=ROOT/'candidate'/CHAR
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--apply',action='store_true')
args=parser.parse_args()
sources={r['batch']:r for r in read(HERE/'source-audit.json')['images']}
assert read(OUT/'processing/scale-profile.json')['common_scale']==.88
plan=[]
for frame in (4,6,13):
    batch=f'E{frame:02d}-single-v1'
    folder=GEN/batch
    row=sources[batch]
    for name,expected in [('raw.png',row['sha256']),('prompt.txt',row['prompt_sha256']),('generation-receipt.json',row['receipt_sha256'])]:
        if sha(folder/name)!=expected: raise RuntimeError(f'Audited source changed: {folder/name}')
    if (OUT/f'walk/E/{frame:02d}.png').exists(): raise RuntimeError(f'Target E{frame:02d} already exists; review it rather than overwrite.')
    plan.append(SimpleNamespace(command='import-walk',character=CHAR,direction='E',source=folder/'raw.png',prompt=folder/'prompt.txt',receipt=folder/'generation-receipt.json',batch_id=batch,common_scale=.88,chroma_profile='standard',rows=1,cols=1,source_cell_indices=None,idle_order=None,output_frames=str(frame),start_frame=1))
print(json.dumps({'mode':'apply' if args.apply else 'dry_run','frames':[4,6,13],'character':CHAR,'common_scale':.88,'native':[1254,1254],'output':[1024,1024],'shared_preview_updates':False,'visual_review':'pending'}),flush=True)
if args.apply:
    pipeline=load('import_pending06_pipeline',ROOT/'tools/pipeline.py')
    pipeline.preview=lambda:None
    verifier=load('import_pending06_verifier',ROOT/'tools/verify.py')
    for item in plan:
        pipeline.import_sheet(item)
    for frame in (4,6,13):
        result=verifier.verify(CHAR,'E',False,frame)
        (OUT/f'review/validation-E-{frame:02d}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result),flush=True)
