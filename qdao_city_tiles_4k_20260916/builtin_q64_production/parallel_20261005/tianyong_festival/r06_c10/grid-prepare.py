from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,shutil
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent;T=B.parent;ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
row,col=map(int,sys.argv[1:3]);assert 1<=row<=4 and 1<=col<=4
P=B/f'r{row:02}_c{col:02}-v1';P.mkdir(exist_ok=True);assert not (P/'native.png').exists()
if not (B/'local-source-checkpoint.json').exists():
 rootcp=read(T/'source-checkpoint.json');s=rootcp['fragment'];assert s['tile']=='r07_c10' and sha(s['file'])==s['sha256'];write(B/'initial-root-source-checkpoint.json',rootcp)
 Image.new('RGBA',(4096,4096),(0,0,0,0)).save(B/'initial-empty-fragment.png')
 halo=np.zeros((115,4096,4),dtype=np.uint8);hsrc=[]
 for c in [1,2,3,4]:
  mp=T/f'r07_c10/r01_c{c:02}-v1/final-v1/manifest.json';m=read(mp);jp=Path(m['joined']['file']);assert sha(jp)==m['joined']['sha256'];j=np.array(Image.open(jp).convert('RGBA'));hsrc.append({'manifest':ref(mp),'joined':ref(jp)})
  for p in m['patches']:
   if p['name'] not in ['new-core','left-return']:continue
   a,_,z,_=p['cropFromJoinedLTRB'];dx,_,dz,_=p['destinationTileLTRB'];halo[:,dx:dz]=j[:115,a:z]
 assert np.all(halo[:,:,3]==255);Image.fromarray(halo).save(B/'r07-top-native-halo.png')
 write(B/'r07-top-native-halo.png.generation.json',{'operation':'Exact native top115 external halo composition using corresponding in-tile x ownership and sequential side returns','sources':hsrc,'output':ref(B/'r07-top-native-halo.png'),'nativeScale':1,'newModelCalls':0,'formalAccepted':False,'doesNotClaimAdjacentTileCoverage':True})
 write(B/'local-source-checkpoint.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r06_c10','fragment':ref(B/'initial-empty-fragment.png'),'nativeScale':1,'coveragePixels':0,'coupledBottom':s,'manifest':None,'contextJoined':None,'formalAccepted':False,'rootPublished':False})
cp=read(B/'local-source-checkpoint.json');source=cp['fragment'];assert sha(source['file'])==source['sha256'];current=np.array(Image.open(source['file']).convert('RGBA'))
x=(col-1)*1024-115;y=(row-1)*1024-115;origin=[36864,20480];window=[x,y,x+1254,y+1254];world=[origin[i%2]+window[i] for i in range(4)]
side=('right' if col<4 else None) if row in [4,2] else ('left' if col>1 else None)
C=np.zeros((1254,1254,4),dtype=np.uint8);nativeinputs=[source];regions=[]
if row==4:
 bottom=cp['coupledBottom'];assert sha(bottom['file'])==bottom['sha256'];a=np.array(Image.open(bottom['file']).convert('RGBA'));hp=B/'r07-top-native-halo.png';h=np.array(Image.open(hp).convert('RGBA'));l,r=max(x,0),min(x+1254,4096)
 C[1024:1139,l-x:r-x]=h[:,l:r];C[1139:,l-x:r-x]=a[:115,l:r];nativeinputs += [ref(hp),bottom]
 regions += [{'contextLTRB':[l-x,1024,r-x,1139],'source':ref(hp),'sourceLTRB':[l,0,r,115],'role':'Actual native r07 external top halo, not fabricated r06 coverage'},{'contextLTRB':[l-x,1139,r-x,1254],'source':bottom,'sourceLTRB':[l,0,r,115]}]
 mapref=T/f'r07_c10/r01_c{col:02}-v1/final-v1/joined.png'
else:
 below=sorted((B/f'r{row+1:02}_c{col:02}-v1').glob('final-*/manifest.json'),key=lambda p:p.stat().st_mtime)[-1];bm=read(below);bp=Path(bm['joined']['file']);assert sha(bp)==bm['joined']['sha256'];a=np.array(Image.open(bp).convert('RGBA'));C[1024:]=a[:230];nativeinputs.append(ref(bp));regions.append({'contextLTRB':[0,1024,1254,1254],'source':ref(bp),'sourceLTRB':[0,0,1254,230]});mapref=bp
if side:
 sp=Path(cp['contextJoined']['file']);assert f'r{row:02}_c{col+(1 if side=="right" else -1):02}-v1' in str(sp);sa=np.array(Image.open(sp).convert('RGBA'));nativeinputs.append(ref(sp))
 if side=='right':C[:,1024:]=sa[:,:230];regions.append({'contextLTRB':[1024,0,1254,1254],'source':ref(sp),'sourceLTRB':[0,0,230,1254]})
 else:C[:,:230]=sa[:,1024:];regions.append({'contextLTRB':[0,0,230,1254],'source':ref(sp),'sourceLTRB':[1024,0,1254,1254]})
l,t,r,b=max(x,0),max(y,0),min(x+1254,4096),min(y+1254,4096);piece=current[t:b,l:r];known=piece[:,:,3]==255;C[t-y:b-y,l-x:r-x][known]=piece[known]
if row==4:
 l,r=max(x,0),min(x+1254,4096);C[1139:,l-x:r-x]=a[:115,l:r]
C[C[:,:,3]==0,:3]=0;Image.fromarray(C).save(P/'context.png')
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
Image.open(master).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(P/'layout-reference-only.png')
refs=[P/'context.png',P/'layout-reference-only.png',ROOT/'designs/gameplay-ui/04-guild.png',mapref]
prompt='''Use case: precise-object-edit / outpainting. Return one opaque native-detail1254 by1254 square image, with exactly the same world crop, camera and object scale as image1. Image1 is the EDIT TARGET: visible pixels are authentic native map continuation constraints. Fill only the black transparent missing region. Preserve every visible contour, endpoint, junction, roof and stone bevel, hue and lighting. Never interpret transparency as a physical seam.
Image2 is the exact same-world canonical LAYOUT reference, not final pixels. Newly paint its visible architecture, vegetation, pedestal, path, paving and cast-shadow footprints precisely in place. Do not cover structures or plants with blank paving, remove them, invent extra objects, recenter, zoom, rotate or change footprints. Known real edges in image1 are exact boundary constraints.
Image3 is approved primary STYLE: bright clean rounded full Daoist Q fantasy polished handpainting. Image4 is a nearby native MAP STYLE and continuity reference only: preserve its material language and detail scale without transplanting its composition. Render broad clean stone bevels, lush rounded foliage and polished dark-jade roof tiles wherever actually shown in image2. Quiet clean surfaces, no cracks, chipped stone, scratches, triangular fractures, grunge, photo texture, polygon noise, new lettering, UI frames, figures or watermark. Only reproduce cropped existing map features from the canonical layout. No resizing or geometric warp. Highest host finish.'''
(P/'prompt.txt').write_text(prompt,encoding='utf8');write(P/'source-checkpoint-input.json',cp)
req={'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r06_c10','patch':f'r{row:02}_c{col:02}','row':row,'col':col,'knownSide':side,'tileGlobalOrigin':origin,'globalCropLTRB':world,'tileLocalCropLTRB':window,'knownPixels':int((C[:,:,3]==255).sum()),'missingPixels':int((C[:,:,3]==0).sum()),'payload':{'prompt':prompt,'referenced_image_paths':[str(z) for z in refs],'transparent_background':False},'configSnapshot':read(ROOT/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'size':None},'formalAccepted':False};write(P/'request.json',req)
write(P/'preparation.json',{'references':[ref(z) for z in refs],'savedCheckpoint':ref(P/'source-checkpoint-input.json'),'sourceTile':{**source,'tile':'r06_c10','tileLocalLTRB':[0,0,4096,4096],'nativeScale':1},'coupledBottom':cp['coupledBottom'],'nativeInputs':nativeinputs,'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'requiresPriorManifest':cp['manifest'],'consistencyProof':{'currentFragmentOverlayExact':True,'allContextPixelsNative':True,'unknownNeighborPixelsNotInvented':True},'knownRegions':regions})
for name,ss,op in [('context.png',nativeinputs,'Exact native context composition, zeros where alpha0'),('layout-reference-only.png',[ref(master)],'Enlarged guide only; final pixels forbidden')]:write(P/(name+'.generation.json'),{'output':ref(P/name),'sources':ss,'operation':op,'newModelCalls':0,'actualModel':None,'actualQuality':None,'formalAccepted':False,'nativeScale':1})
print(json.dumps({'request':ref(P/'request.json'),'missingPixels':req['missingPixels'],'world':world}))
