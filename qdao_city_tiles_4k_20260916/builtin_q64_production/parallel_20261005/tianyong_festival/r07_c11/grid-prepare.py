from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
N=Path(__file__).parent;T=N.parent;ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def checked(v):
 assert sha(v['file'])==v['sha256'],v['file']
 return Image.open(v['file']).convert('RGBA')
r,c=map(int,sys.argv[1:3]);assert 1<=r<=4 and 1<=c<=4
D=N/f'r{r:02d}_c{c:02d}-v1';D.mkdir(exist_ok=False)
cp_path=N/'local-source-checkpoint.json';cp=read(cp_path)
(D/'local-source-checkpoint-input.json').write_bytes(cp_path.read_bytes())
first=read(N/'r04_c01-v1/preparation.json')
left=checked(first['sources']['r07_c10']);belowleft=checked(first['sources']['r08_c10'])
for p in cp['externalReturnDependencies']:
 asset=checked(p['asset']);target=left if p['destinationTile']=='r07_c10' else belowleft
 target.paste(asset,tuple(p['destinationTileLTRB'][:2]))
left.save(D/'left-coupled-input.png');belowleft.save(D/'below-left-coupled-input.png')
leftref={**ref(D/'left-coupled-input.png'),'tile':'r07_c10','pixels':[4096,4096],'tileLocalLTRB':[0,0,4096,4096],'nativeScale':1}
belowref={**ref(D/'below-left-coupled-input.png'),'tile':'r08_c10','pixels':[4096,4096],'tileLocalLTRB':[0,0,4096,4096],'nativeScale':1}
local=[(c-1)*1024-115,(r-1)*1024-115,(c-1)*1024+1139,(r-1)*1024+1139]
world=[40960+local[0],24576+local[1],40960+local[2],24576+local[3]]
context=Image.new('RGBA',(1254,1254),(0,0,0,0))
def paste_world(im,b):
 x1=max(local[0],b[0]);y1=max(local[1],b[1]);x2=min(local[2],b[2]);y2=min(local[3],b[3])
 if x1>=x2 or y1>=y2:return
 crop=im.crop((x1-b[0],y1-b[1],x2-b[0],y2-b[1]))
 context.alpha_composite(crop,(x1-local[0],y1-local[1]))
chain=cp.get('manifestChain',[cp['manifest']])
for mp in chain:
 m=read(mp['file']);assert sha(mp['file'])==mp['sha256']
 paste_world(checked(m['joined']),m['windowTileLocalLTRB'])
paste_world(left,[-4096,0,0,4096])
paste_world(belowleft,[-4096,4096,0,8192])
paste_world(checked(cp['fragment']),[0,0,4096,4096])
context.save(D/'context.png');a=np.array(context)
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as im:im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(D/'layout-reference-only.png')
refs=[D/'context.png',D/'layout-reference-only.png',ROOT/'designs/gameplay-ui/04-guild.png']
prompt="""Use case: precise-object-edit / outpainting. Fill only transparent missing native map pixels of image1; return the exact1254x1254 same-scale opaque square. Image1 is the exact edit target with real finished painted neighbor pixels. Preserve every existing stone outline, joint endpoint, round bevel thickness, relief edge, material color, lighting, shadow and camera at the visible context. Continue the SAME structures smoothly through the arbitrary transparency edge. Image2 is the canonical structure-only guide for this precise world crop: follow its actual object positions, paving layout, curved courses, shadows and ornaments, but never paste or upscale its blurry pixels. Image3 is the approved STYLE reference only: clean bright rounded DaoistQ game art, smooth ivory and warmgold stone, elegant clean handpainting. Do not import its UI. Native crisp coherent forms and true architectural joints, soft restrained painted texture. Missing area is part of one continuous map. No added cracks, crease, fold, missing chip, triangular surface gash, grime, excessive veining, grain, dense small engraving, sharpened halos, text, UI, frame, watermark, characters or new architecture. Do not create new straight joints at context boundaries. Do not zoom, rotate, change scale, crop or reframe. Keep the broad paving and relief visibly rounded and consistent with the supplied finished pixels."""
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
req={'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c11','patch':f'r{r:02d}_c{c:02d}','row':r,'col':c,'tileGlobalOrigin':[40960,24576],'tileLocalCropLTRB':local,'globalCropLTRB':world,'configSnapshot':read(ROOT/'config/image-generation.json'),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'knownPixels':int((a[:,:,3]==255).sum()),'missingPixels':int((a[:,:,3]==0).sum()),'submittedParameters':{'model':None,'quality':None,'size':None},'actualModel':None,'actualQuality':None}
write(D/'request.json',req)
prep={'sources':{'fragment':cp['fragment'],'left':leftref,'belowLeft':belowref},'sourceCheckpoint':ref(D/'local-source-checkpoint-input.json'),'manifestChain':chain,'references':[dict(ref(p),role=role) for p,role in zip(refs,['exact native neighbor context','canonical structure only','approved painting style only'])],'master':ref(master),'guidePixelsAllowedInFinal':False,'nativeScale':1}
write(D/'preparation.json',prep)
for p,sources,op,scale in [(D/'context.png',[cp['fragment'],leftref,belowref],'Exact native neighboring crop composition; no rescale',1),(D/'layout-reference-only.png',[ref(master)],'Resized geometry reference only; excluded from all final pixels',None)]:
 write(str(p)+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':sources,'operation':op,'nativeScale':scale,'actualModel':None,'actualQuality':None,'newModelCalls':0})
print(json.dumps({'dir':str(D),'request':str(D/'request.json'),'knownPixels':req['knownPixels'],'missingPixels':req['missingPixels']}))
