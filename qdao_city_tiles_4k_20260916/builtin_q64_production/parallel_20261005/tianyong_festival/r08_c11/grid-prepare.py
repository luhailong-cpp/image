"""Prepare a top-to-bottom, left-to-right native window from current actual sources."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent;T=N.parent;ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def origin(tile):return [(int(tile[5:7])-1)*4096,(int(tile[1:3])-1)*4096]
r,c=map(int,sys.argv[1:3]);assert 1<=r<=4 and 1<=c<=4;tile=N.name;xy=origin(tile);local=[(c-1)*1024-115,(r-1)*1024-115,(c-1)*1024+1139,(r-1)*1024+1139];world=[xy[i%2]+local[i] for i in range(4)]
tag=sys.argv[3] if len(sys.argv)>3 else 'v1'
assert tag.startswith('v') and tag[1:].isdigit()
D=N/f'r{r:02d}_c{c:02d}-{tag}';D.mkdir(exist_ok=False);cp=read(T/'source-checkpoint.json');save(D/'source-checkpoint-input.json',cp)
C=Image.new('RGBA',(1254,1254),(0,0,0,0));sources={};regions=[]
for v in cp['candidateSet']:
 ox,oy=origin(v['tile']);l,t,rr,b=max(world[0],ox),max(world[1],oy),min(world[2],ox+4096),min(world[3],oy+4096)
 if l>=rr or t>=b:continue
 assert sha(v['file'])==v['sha256'];im=Image.open(v['file']).convert('RGBA');assert im.size==(4096,4096);crop=im.crop((l-ox,t-oy,rr-ox,b-oy));C.alpha_composite(crop,(l-world[0],t-world[1]));sources[v['tile']]=v
 regions.append({'source':v,'sourceLTRB':[l-ox,t-oy,rr-ox,b-oy],'contextXY':[l-world[0],t-world[1]]})
A=np.asarray(C);assert np.any(A[:,:,3]==255);lx=115 if c==1 else 230;ty=115 if r==1 else 230;right=1139 if c==4 else 1254;bottom=1139 if r==4 else 1254
assert not np.any(A[ty:bottom,lx:right,3]),'New core already has pixels; choose a different grid window or explicit repair'
C.save(D/'context.png');master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as m:m.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(D/'layout-reference-only.png')
refs=[D/'context.png',D/'layout-reference-only.png',ROOT/'designs/gameplay-ui/04-guild.png']
prompt='''Use case: precise-object-edit / outpainting. Fill only transparent missing map pixels in image1, returning the exact1254x1254 opaque square at identical scale, crop, camera and lighting. Image1 contains authentic native finished artwork in the top and left context. Precisely preserve all existing contour endpoints, scroll rim thickness, bevels, stone joints, shadows and material colors. Continue the exact same structures into the missing lower-right region; the straight transparency edges are arbitrary crop boundaries, never stone joints. Image2 is only the canonical broad layout for this exact world crop: follow its real forms and object positions, but do not paste or upscale its soft pixels. Crisp authentic image1 contours take priority for exact boundary continuation. Image3 is approved primary STYLE only: bright, clean, rounded Daoist Q game art; ivory and warmgold handpainted stone, attractive confident edges, gentle sparse texture. Do not import its UI. Preserve the broad flowing ornament and its true architectural joints. No invented crack, crease, fold, chip, extra engraving, grime, grain, excessive veins, sharpening halos, text, UI, watermark, frame, characters, new architecture, camera shift, zoom, rotation, crop or resize. Highest visual finish through the host.'''
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
save(D/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':tile,'patch':f'r{r:02d}_c{c:02d}','row':r,'col':c,'tileGlobalOrigin':xy,'tileLocalCropLTRB':local,'globalCropLTRB':world,'configSnapshot':read(ROOT/'config/image-generation.json'),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'knownPixels':int((A[:,:,3]==255).sum()),'missingPixels':int((A[:,:,3]==0).sum()),'submittedParameters':{'model':None,'quality':None,'size':None},'actualModel':None,'actualQuality':None})
prep={'sources':sources,'knownRegions':regions,'sourceCheckpoint':ref(D/'source-checkpoint-input.json'),'references':[dict(ref(p),role=role) for p,role in zip(refs,['exact native current known context','canonical structure only','approved primary style'])],'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False};save(D/'preparation.json',prep)
for name,inputs,op,scale in [('context.png',list(sources.values()),'Exact current native crop composition',1),('layout-reference-only.png',[ref(master)],'Resized structure-only reference, never final pixels',None)]:save(D/(name+'.generation.json'),{'file':str(D/name),'sha256':sha(D/name),'operation':op,'derivedFrom':inputs,'newModelCalls':0,'nativeScale':scale,'actualModel':None,'actualQuality':None})
print(json.dumps({'request':str(D/'request.json'),'world':world,'knownPixels':int((A[:,:,3]==255).sum())}))
