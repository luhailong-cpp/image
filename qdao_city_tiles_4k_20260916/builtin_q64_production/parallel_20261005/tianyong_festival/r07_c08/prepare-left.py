from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
import numpy as np
from PIL import Image
N=Path(__file__).parent;T=N.parent;ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists());col=int(sys.argv[1]);D=N/(sys.argv[3] if len(sys.argv)>3 else f'r04_c{col:02d}-v1');D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def load(v):assert sha(v['file'])==v['sha256'];return Image.open(v['file']).convert('RGBA')
cp=read(N/'local-source-checkpoint.json');active=load(cp['fragment']);bottom=load(cp['prospectiveBottom']);x0=int(sys.argv[2]) if len(sys.argv)>2 else (col-1)*1024-115;local=[x0,2957,x0+1254,4211];origin=[28672,24576];world=[origin[i%2]+local[i] for i in range(4)]
C=active.crop(tuple(local));C.paste(bottom.crop((x0,0,x0+1254,115)),(0,1139))
assert C.size==(1254,1254);A=np.array(C)
known_start=int(np.flatnonzero(A[0,:,3]==255)[0])
assert np.all(A[:1139,known_start:,3]==255) and np.all(A[1139:,:,3]==255)
assert not A[:1139,:known_start,3].any()
C.save(D/'context.png');master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as m:m.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(D/'layout-reference-only.png')
refs=[D/'context.png',D/'layout-reference-only.png',ROOT/'designs/gameplay-ui/04-guild.png']
prompt='''Use case: precise-object-edit / outpainting. Paint the missing native map area of image1. Return one opaque1254x1254 image in the exact same crop, scale, lighting and camera. Image1 is the edit target: rightmost230 columns and bottom115 rows are authentic finished stone paving, transparent upper-left1024x1139 area is missing. Precisely preserve existing contour positions, rail width, bevel thickness, stone seams, shading and color along the RIGHT230 and BOTTOM115. Continue those exact shapes into the missing area; the straight transparency boundaries are not stone seams. Image2 supplies only the canonical same-world broad layout; never use its enlarged soft pixels in the output. Existing authentic image1 colors and endpoints take priority over image2. Image3 is the approved primary STYLE reference: bright clean rounded Daoist Q handpainting; ivory/warm golden stone and cool muted slate, without importing any UI or object.
Continue the existing plaza paving only. Any gray inset touching the bottom MUST continue upward as the same SINGLE GRAY stone surface until its real diagonal ivory frame; do not change it to beige or invent a horizontal cut along y1139. The existing bright ivory framing determines where the gray surface ends. Preserve true stone joints and smooth broad profiles. Keep plain surfaces quiet, gently painted and clean, without extra engravings, cracks, grime, dense veins, speckles, photographic grain or sharpening halos. Do not add a boundary at x1024 or y1139. No text, people, vegetation, objects, border, camera shift, rotation, crop, zoom or resizing. Highest visual finish through the host.'''
prompt=prompt.replace('rightmost230 columns',f'rightmost{1254-known_start} columns').replace('RIGHT230',f'RIGHT{1254-known_start}').replace('upper-left1024x1139',f'upper-left{known_start}x1139').replace('x1024',f'x{known_start}')
(D/'prompt.txt').write_text(prompt,encoding='utf-8');payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
save(D/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c08','patch':f'r04_c{col:02d}','tileGlobalOrigin':origin,'tileLocalCropLTRB':local,'globalCropLTRB':world,'configSnapshot':read(ROOT/'config/image-generation.json'),'payload':payload,'knownPixels':int((A[:,:,3]==255).sum()),'missingPixels':int((A[:,:,3]==0).sum()),'submittedParameters':{'model':None,'quality':None,'size':None}})
save(D/'source-checkpoint-input.json',cp)
prep={'sources':{'r07_c08':dict(cp['fragment'],tile='r07_c08',tileLocalLTRB=[0,0,4096,4096],nativeScale=1),'r08_c08':dict(cp['prospectiveBottom'],tileLocalLTRB=[0,0,4096,4096],nativeScale=1)},'references':[dict(ref(p),role=role) for p,role in zip(refs,['exact native local current right and prospective bottom, requiring prior manifest first','canonical structural layout only','approved primary painting style'])],'sourceCheckpoint':ref(D/'source-checkpoint-input.json'),'previousManifest':cp['manifest'],'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'knownStartX':known_start,'knownRegions':[{'source':cp['fragment'],'sourceLTRB':[x0+known_start,2957,x0+1254,4096],'contextXY':[known_start,0]},{'source':cp['prospectiveBottom'],'sourceLTRB':[x0,0,x0+1254,115],'contextXY':[0,1139],'prospectiveExternal':True}],'externalReturnDependencies':cp['externalReturnDependencies']}
save(D/'preparation.json',prep)
for name,inputs,op in [('context.png',list(prep['sources'].values()),'Exact native crops; prospective bottom is actual frozen source plus earlier manifest ROI, not a published external tile'),('layout-reference-only.png',[ref(master)],'Enlarged layout guide only; never used in output pixels')]:save(D/(name+'.generation.json'),{'file':str(D/name),'sha256':sha(D/name),'operation':op,'derivedFrom':inputs,'newModelCalls':0,'nativeScale':1,'actualModel':None,'actualQuality':None})
print(json.dumps({'request':str(D/'request.json'),'window':local,'world':world}))
