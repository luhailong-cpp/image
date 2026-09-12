from pathlib import Path
import sys,json,hashlib,shutil
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
from processor_rgb import clean
from stage_v9_edges import evidence
j=json.loads((HERE/'stage.json').read_text());r=next(r for r in j['records'] if r['character_id']=='16')
src=ROOT/r['before_path'];dst=ROOT/r['staged_path'];old=Image.open(src).convert('RGBA')
archive=HERE/'first-pass';archive.mkdir(exist_ok=True);shutil.copy2(dst,archive/'16.png')
(archive/'16-record.json').write_text(json.dumps(r,indent=2)+'\n')
for e in r['evidence']:shutil.copy2(ROOT/e,archive/Path(e).name)
a=np.array(old);extra=np.zeros(a.shape[:2],dtype=bool);roi=[2840,2780,2930,2900];x0,y0,x1,y1=roi;extra[y0:y1,x0:x1]=True
new,stats=clean(old,extra_mask=extra);b=np.array(new);assert np.array_equal(a[:,:,3],b[:,:,3]);assert stats['unresolved']==0
new.save(dst,optimize=True);ev,pts=evidence(old,new,'16',np.any(a[:,:,:3]!=b[:,:,:3],axis=2))
first=np.array(Image.open(archive/'16.png'));delta=np.any(first[:,:,:3]!=b[:,:,:3],axis=2);assert not delta[~extra].any()
r.update(output_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),evidence=ev,detail_points=pts,rgb_changed_fraction=float(np.any(a[:,:,:3]!=b[:,:,:3],axis=2).mean()),extra_mask_roi=roi,extra_mask_reason='Actual light/dark QA found a strongly pink remnant in black braid gap; local same-image neutral donor fitting only inside this ROI; gold clothing outside protected.',extra_mask_processor='qdao_festival_refinement_20260910/v9-edges/refine_16_gap.py',extra_mask_processor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),additional_pixels_changed=int(delta.sum()),**stats)
(HERE/'stage.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'id':'16','extra_roi':roi,'additional_rgb_pixels':int(delta.sum()),'alpha_changed':0,'output_sha256':r['output_sha256']}))
