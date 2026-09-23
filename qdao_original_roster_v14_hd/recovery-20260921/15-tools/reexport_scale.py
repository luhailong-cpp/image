"""Uniform native-source re-export for manually reviewed character scale.

No pose changes, no 1024-frame upsampling. --apply explicitly replaces only the
named character-15 slot after source and selected SHA verification.
"""
from pathlib import Path
import argparse, json, hashlib, importlib.util
from datetime import datetime, timezone
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--direction',choices=['N','NE','E','SE','S','SW','W','NW'],required=True);p.add_argument('--frame',type=int);p.add_argument('--idle',action='store_true');p.add_argument('--multiplier',type=float,required=True);p.add_argument('--reason',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
if a.idle==(a.frame is not None):raise SystemExit('Choose --idle or --frame')
if a.frame is not None and not 1<=a.frame<=16:raise SystemExit('Frame must be 1..16')
if not .85<=a.multiplier<=1.15:raise SystemExit('Manual multiplier must be small, 0.85..1.15')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
slot=f'idle/{a.direction}.png' if a.idle else f'walk/{a.direction}/{a.frame:02d}.png'
target=R/'15-delivery-preview/runtime'/slot;side=target.with_name(target.name+'.generation.json')
old=json.loads(side.read_text(encoding='utf-8'));assert old['character']=='15_water_dragon_scholar_boy' and old['sha256']==sha(target)
raw=Path(old['derivedFrom']['path']);assert raw.is_relative_to(R/'15-generation') and sha(raw)==old['derivedFrom']['sha256']
with Image.open(raw) as source:native=source.size
assert min(native)>=1024
keyed_path=raw.parent/'processing-fixed088-v1/keyed.png'
with Image.open(keyed_path) as source:keyed=source.convert('RGBA');assert keyed.size==native
spec=importlib.util.spec_from_file_location('edge_despill',R.parent/'tools/vendor/edge_despill.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
scale=1024/max(native)*.88*a.multiplier
assert scale<1
size=tuple(round(x*scale) for x in native);normalized=keyed.resize(size,Image.Resampling.LANCZOS);cleaned,despill=module.despill(normalized,radius=4,reference_radius=12)
y,x=np.where(np.asarray(cleaned)[:,:,3]>8);top=int(y.min());height=int(y.max())-top;anchor_x=float(np.median(x[y<top+max(1,int(height*.42))]));anchor_y=int(y.max());delta=[round(512-anchor_x),942-anchor_y]
b=cleaned.getchannel('A').getbbox();moved=[b[0]+delta[0],b[1]+delta[1],b[2]+delta[0],b[3]+delta[1]]
assert min(moved[:2])>=1 and max(moved[2:])<=1023,f'Would clip: {moved}'
final=Image.new('RGBA',(1024,1024));final.paste(cleaned,tuple(delta))
folder=raw.parent/f'processing-scale-v1-{a.multiplier:.4f}';folder.mkdir(exist_ok=True)
dest=folder/'final.png';final.save(dest)
now=datetime.now(timezone.utc).isoformat();new=dict(old)
new.update(sha256=sha(dest),selectedAt=now,selectionAuthorization='user requested proportion repair; explicit --apply required',selectionNote=a.reason,artReview='pending_after_scale_review')
new['operation']={'name':'native_uniform_downscale_manual_head_torso_scale_and_anchor','originalNativeSize':list(native),'sourceSha256':sha(raw),'keyedNativePath':str(keyed_path),'keyedNativeSha256':sha(keyed_path),'baseWholeCellScale':1024/max(native)*.88,'manualMultiplier':a.multiplier,'wholeCellScale':scale,'normalizedSize':list(size),'outputSize':[1024,1024],'rootPx':[512,942],'anchorAfterPx':[512,942],'translationPx':delta,'anchorAlgorithm':'upper_body_alpha_gt8_median_42_percent_x_lowest_alpha_gt8_y','upscaled':False,'perSubjectBboxFit':False,'poseModification':False,'reason':a.reason,'oldSelectedSha256':old['sha256'],'oldOperation':old['operation'],'despill':despill,'stages':{'keyed':{'path':str(keyed_path),'sha256':sha(keyed_path),'size':list(native)},'final':{'path':str(dest),'sha256':sha(dest),'size':[1024,1024]}}}
(folder/'final.png.generation.json').write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8')
for bg,name in [((240,234,220,255),'light'),((24,34,44,255),'dark')]:
    check=Image.new('RGBA',(1024,1024),bg);check.alpha_composite(final);check.convert('RGB').save(folder/f'check-{name}.png')
if a.apply:
    log=R/'15-review'/'scale-reexport-history.jsonl'
    with log.open('a',encoding='utf-8') as f:f.write(json.dumps({'time':now,'slot':slot,'oldSelection':old,'newSelection':new},ensure_ascii=False)+'\n')
    tmp=target.with_name(target.name+'.next');tmp.write_bytes(dest.read_bytes());tmp.replace(target)
    tmp=side.with_name(side.name+'.next');tmp.write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(side)
print(json.dumps({'slot':slot,'native':native,'scale':scale,'multiplier':a.multiplier,'sha256':sha(dest),'applied':a.apply}))
