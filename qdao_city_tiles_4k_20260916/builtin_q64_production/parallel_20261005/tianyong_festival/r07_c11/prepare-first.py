from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image

N=Path(__file__).resolve().parent;T=N.parent;ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists())
D=N/'r04_c01-v1';D.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(v):assert sha(v['file'])==v['sha256'];return Image.open(v['file']).convert('RGBA')
cp=read(T/'source-checkpoint.json');sources={v['tile']:v for v in cp['candidateSet']}
left=sources['r07_c10'];lower=sources['r08_c10'];C=Image.new('RGBA',(1254,1254),(0,0,0,0))
C.paste(load(left).crop((3981,2957,4096,4096)),(0,0));C.paste(load(lower).crop((3981,0,4096,115)),(0,1139))
A=np.asarray(C);assert np.all(A[:,:115,3]==255) and not A[:,115:,3].any()
C.save(D/'context.png');local=[-115,2957,1139,4211];origin=[40960,24576];world=[origin[i%2]+local[i] for i in range(4)]
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as m:m.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(D/'layout-reference-only.png')
refs=[D/'context.png',D/'layout-reference-only.png',ROOT/'designs/gameplay-ui/04-guild.png']
prompt='''Use case: precise-object-edit / outpainting. Complete the missing native map area in image1. Return one opaque1254x1254 image with the exact same crop, scale, lighting and camera. Image1 is the edit target: its LEFT115 columns are authentic finished paving with a curved ivory ornamental border, and the remaining1139 columns are transparent missing map. Exactly preserve contour endpoints, carved scroll shapes, stone joints, bevel thickness, shading and color at the left edge. Continue the correct shapes into the missing right area. Image2 provides only the canonical same-world layout and object positions; do not paste or upscale its soft pixels. Image3 is the approved primary painting STYLE reference: bright clean rounded Daoist Q game art, smooth ivory and warmgold stone, clean attractive handpainting; do not import any UI or unrelated object. Follow image2 for what belongs in this crop and image1 for exact matching edge geometry and colors. Treat the straight transparency boundary x115 as an arbitrary crop line, never as a stone seam. Smooth broad clean stone surfaces, restrained subtle painted variation, continuous true joints. No invented cracks, grime, excessive veining, grain, dense engraving, sharpened halos, text, characters, watermark, border, camera shift, rotation, crop or zoom. Highest visual finish through the host.'''
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
save(D/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c11','patch':'r04_c01','tileGlobalOrigin':origin,'tileLocalCropLTRB':local,'globalCropLTRB':world,'configSnapshot':read(ROOT/'config/image-generation.json'),'payload':payload,'knownPixels':int((A[:,:,3]==255).sum()),'missingPixels':int((A[:,:,3]==0).sum()),'submittedParameters':{'model':None,'quality':None,'size':None},'actualModel':None,'actualQuality':None})
save(D/'source-checkpoint-input.json',cp)
prep={'sources':{'r07_c10':left,'r08_c10':lower},'references':[dict(ref(p),role=role) for p,role in zip(refs,['exact native known left strip','canonical structural layout only','approved primary painting style'])],'sourceCheckpoint':ref(D/'source-checkpoint-input.json'),'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'knownRegions':[{'source':left,'sourceLTRB':[3981,2957,4096,4096],'contextXY':[0,0]},{'source':lower,'sourceLTRB':[3981,0,4096,115],'contextXY':[0,1139]}]}
save(D/'preparation.json',prep)
for name,inputs,op in [('context.png',[left,lower],'Exact native crop composition; no generated or scaled pixels'),('layout-reference-only.png',[ref(master)],'Enlarged structural guide only; never used in output pixels')]:save(D/(name+'.generation.json'),{'file':str(D/name),'sha256':sha(D/name),'operation':op,'derivedFrom':inputs,'newModelCalls':0,'nativeScale':1 if name=='context.png' else None,'actualModel':None,'actualQuality':None})
print(json.dumps({'request':str(D/'request.json'),'world':world,'knownPixels':int((A[:,:,3]==255).sum())}))
