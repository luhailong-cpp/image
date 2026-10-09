from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent;T=N.parent;ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists());D=N/'r01_c01-v1';D.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(v):assert sha(v['file'])==v['sha256'];return Image.open(v['file']).convert('RGBA')
cp=read(T/'source-checkpoint.json');S={v['tile']:v for v in cp['candidateSet']};C=Image.new('RGBA',(1254,1254),(0,0,0,0));regions=[('r07_c10',[3981,3981,4096,4096],[0,0]),('r07_c11',[0,3981,1139,4096],[115,0]),('r08_c10',[3981,0,4096,1139],[0,115])]
for tile,box,xy in regions:
 crop=load(S[tile]).crop(box);assert np.all(np.asarray(crop)[:,:,3]==255);C.paste(crop,tuple(xy))
A=np.asarray(C);assert np.all(A[:115,:,3]==255) and np.all(A[:,:115,3]==255) and not A[115:,115:,3].any();C.save(D/'context.png')
origin=[40960,28672];local=[-115,-115,1139,1139];world=[origin[i%2]+local[i] for i in range(4)];master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as m:m.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(D/'layout-reference-only.png')
refs=[D/'context.png',D/'layout-reference-only.png',ROOT/'designs/gameplay-ui/04-guild.png']
prompt='''Use case: precise-object-edit / outpainting. Fill only the missing map area in image1, returning one opaque1254x1254 image at identical crop, scale, camera and lighting. Image1 is the actual native edit target. Its TOP115rows and LEFT115columns are authentic finished ivory/warmgold ornamental stone, with the rest of the square transparent. Precisely preserve each contour position and color in these authentic borders, including every scroll rim, joint, bevel, shadow and bright highlight. Extend them naturally into the missing lower-right square. Image2 is only the same-world canonical layout: follow its broad composition and object positions, but never paste or upscale its soft pixels. The sharp authentic image1 borders control exact continuation endpoints. Image3 is the approved primary STYLE only: bright clean rounded Daoist Q handpainting, ivory warmgold materials, clean confident edges and quiet broad surfaces. Do not import its UI. Follow image2 for which paving, ornament and materials actually belong here. Preserve large smooth scroll silhouettes and widths. Do not add any line at the arbitrary x115/y115 crop boundaries. No invented cracks, clutter, dense engravings, excessive veins, grime, grain, sharpening halos, unrelated objects, characters, text, watermark, border, camera move, zoom, rotation, crop or resizing. Highest visual finish through the host.'''
(D/'prompt.txt').write_text(prompt,encoding='utf-8');payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
save(D/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c11','patch':'r01_c01','tileGlobalOrigin':origin,'tileLocalCropLTRB':local,'globalCropLTRB':world,'configSnapshot':read(ROOT/'config/image-generation.json'),'payload':payload,'knownPixels':int((A[:,:,3]==255).sum()),'missingPixels':int((A[:,:,3]==0).sum()),'submittedParameters':{'model':None,'quality':None,'size':None},'actualModel':None,'actualQuality':None})
save(D/'source-checkpoint-input.json',cp)
prep={'sources':{tile:S[tile] for tile,_,_ in regions},'references':[dict(ref(p),role=role) for p,role in zip(refs,['exact native current top and left context','canonical structural layout only','approved primary painting style'])],'sourceCheckpoint':ref(D/'source-checkpoint-input.json'),'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'knownRegions':[{'source':S[tile],'sourceLTRB':box,'contextXY':xy} for tile,box,xy in regions]};save(D/'preparation.json',prep)
for name,inputs,op in [('context.png',list(prep['sources'].values()),'Exact native crops; all known ROI pixels opaque, although r07_c11 is incomplete elsewhere'),('layout-reference-only.png',[ref(master)],'Enlarged layout-only guide, never used as output pixels')]:save(D/(name+'.generation.json'),{'file':str(D/name),'sha256':sha(D/name),'operation':op,'derivedFrom':inputs,'newModelCalls':0,'nativeScale':1 if name=='context.png' else None,'actualModel':None,'actualQuality':None})
print(json.dumps({'request':str(D/'request.json'),'world':world,'knownPixels':int((A[:,:,3]==255).sum())}))
