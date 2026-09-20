"""Use existing immutable-source pipeline for 04 only; no shared preview writes."""
import argparse, importlib.util, json, sys, shutil, hashlib
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
p=argparse.ArgumentParser();p.add_argument('batch');p.add_argument('direction');p.add_argument('frame',type=int);a=p.parse_args()
b=HERE/a.batch
receipt=json.loads((b/'generation-receipt.json').read_text(encoding='utf-8'))
(b/'prompt.txt').write_text(receipt['actual_request']['prompt'],encoding='utf-8',newline='')
original=Path(receipt['original_generated_file'])
if (b/'raw.png').exists():
    assert hashlib.sha256(original.read_bytes()).digest()==hashlib.sha256((b/'raw.png').read_bytes()).digest()
else: shutil.copy2(original,b/'raw.png')
pipe=module('guardian_pipeline',ROOT/'tools/pipeline.py')
pipe.preview=lambda: None
pipe.import_sheet(SimpleNamespace(command='import-walk',character='04_mountain_guardian_boy',direction=a.direction,source=b/'raw.png',prompt=b/'prompt.txt',receipt=b/'generation-receipt.json',batch_id=a.batch,common_scale=.84,chroma_profile='standard',rows=1,cols=1,source_cell_indices=None,idle_order=None,output_frames=str(a.frame),start_frame=1))
ver=module('guardian_verify',ROOT/'tools/verify.py')
report=ver.verify('04_mountain_guardian_boy',a.direction,False,a.frame)
dest=ROOT/'candidate/04_mountain_guardian_boy/review'/f'validation-{a.direction}-{a.frame:02d}.json'
dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
prov=module('guardian_provenance',ROOT/'tools/inspect_image_provenance.py')
(b/'provenance.json').write_text(json.dumps(prov.inspect_image(b/'raw.png'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
