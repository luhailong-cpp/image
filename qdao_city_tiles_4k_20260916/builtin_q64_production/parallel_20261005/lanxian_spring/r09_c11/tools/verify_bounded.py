"""Replay recorded original pixels, masks and bounded deltas; create native QA."""
import json
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
from common import TILE, NATIVE, HALO, EXTENDED, info, now, read, write, load_west

parser=argparse.ArgumentParser()
parser.add_argument('--candidate',default='assembly_bounded_v2')
args=parser.parse_args()
out=(TILE/args.candidate).resolve(strict=True)
assert out.is_relative_to(TILE)
m=read(out/'assembly.json')
base=read(TILE/'assembly_hardcut/assembly.json')
canvas=np.zeros((EXTENDED,EXTENDED,3),np.uint8)
canvas[:,:HALO]=np.asarray(load_west())[:,4096:4211]
source_map={s['patchId']:s for s in m['sources']}
replay_steps=[]
returns=[]
qa_dir=out/'qa-extra';qa_dir.mkdir(exist_ok=True)
actual=np.asarray(Image.open(out/'extended4326.png').convert('RGB'))
for s in m['steps']:
    cell=s['patchId'];x,y=s['nativeOriginXY']
    src=source_map[cell]
    raw=np.asarray(Image.open(src['file']).convert('RGB'))
    delta=np.load(s['rgbDelta']['file'])['rgbDelta'].astype(np.int16)
    a=np.asarray(Image.open(s['alpha']['file'])).astype(np.uint32)[...,None]
    corrected=np.clip(raw.astype(np.int16)+delta,0,255).astype(np.uint32)
    old=canvas[y:y+NATIVE,x:x+NATIVE].astype(np.uint32)
    canvas[y:y+NATIVE,x:x+NATIVE]=((old*(255-a)+corrected*a+127)//255).astype(np.uint8)
    mx=np.abs(delta).max(axis=(0,1)).tolist()
    assert max(mx)<=16
    replay_steps.append({'cell':cell,'maxPerChannelDelta':mx,'zeroTranslation':s['integerTranslationXY']==[0,0]})
    if np.any(delta):
        ys,xs=np.where(np.any(delta!=0,axis=2))
        rect=[max(0,x+int(xs.min())-64),max(0,y+int(ys.min())-64),min(4326,x+int(xs.max())+65),min(4326,y+int(ys.max())+65)]
        dest=qa_dir/f'{cell}_field_support_and_returns_1to1.png'
        Image.fromarray(actual).crop(rect).save(dest)
        returns.append({**info(dest),'extendedLTRB':rect,'nativeSize':list(Image.open(dest).size),'resized':False,'viewed':False})
assert np.array_equal(canvas,actual)
assert np.array_equal(actual[115:4211,115:4211],np.asarray(Image.open(out/'core4096.png').convert('RGB')))
qa=[]
for rec in m['qa']:
    name=Path(rec['file']).name
    prior=next(q for q in base['qa'] if Path(q['file']).name==name)
    qa.append({**rec,'unchangedFromHardcut':rec['sha256']==prior['sha256'],'prior':prior})
junctions=[q for q in qa if q['kind']=='internal_junction']
montage=Image.new('RGB',(960,960))
for i,j in enumerate(junctions):montage.paste(Image.open(j['file']),(i%3*320,i//3*320))
montage_path=qa_dir/'junctions_native_montage.png';montage.save(montage_path)
preview_path=out/'preview1254.png';Image.open(out/'core4096.png').resize((1254,1254),Image.Resampling.LANCZOS).save(preview_path)
write(out/'pixel-verification.json',{'createdAtUtc':now(),'assembly':info(out/'assembly.json'),'originalPixelMaskDeltaReplayExact':True,'coreEqualsHaloCrop':True,'maxAllowedDelta':16,'steps':replay_steps,'qaChangedCount':sum(not q['unchangedFromHardcut'] for q in qa),'qa':qa,'fieldReturnQA':returns,'junctionMontage':{**info(montage_path),'resized':False,'layout':'3 by 3 row major y=1024,2048,3072; x=1024,2048,3072'},'preview':{**info(preview_path),'presentationOnly':True,'downscaled':True},'formalAccepted':False})
print(json.dumps({'replayExact':True,'qaChanged':[Path(q['file']).name for q in qa if not q['unchangedFromHardcut']],'fieldReturnCount':len(returns),'preview':str(preview_path)},ensure_ascii=False))
