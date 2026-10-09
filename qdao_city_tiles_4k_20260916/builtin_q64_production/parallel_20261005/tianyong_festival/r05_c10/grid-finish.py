from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
import numpy as np
from PIL import Image
D=Path(sys.argv[1]);B=D.parent;read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()};save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
req=read(D/'request.json');prep=read(D/'preparation.json');cp=read(D/'source-checkpoint-input.json');F=D/req.get('selectedFinalDirectory','final-v1');J=Image.open(F/'joined.png').convert('RGB');assert (D/'qa-accepted.txt').exists()
tile='r05_c10';x,y,_,_=req['tileLocalCropLTRB'];row=req['row'];side=req['knownSide'];prior=prep['sourceTile'];bottom=prep['coupledBottom'];fragment=Image.open(prior['file']).convert('RGBA');before=np.array(fragment);coupled=Image.open(bottom['file']).convert('RGBA');beforebottom=np.array(coupled);changes=np.zeros((4096,4096),bool);bottomchanges=np.zeros((4096,4096),bool)
xl=max(0,-x);yt=max(0,-y);xr=min(1254,4096-x);newl=230 if side=='left' else xl;newr=1024 if side=='right' else xr;coreb=1139 if row==4 else 1024;patches=[]
rects=[('new-core',[newl,yt,newr,coreb],tile,None)]
if side=='left':rects.append(('left-return',[max(54,xl),yt,230,coreb],tile,prior))
if side=='right':rects.append(('right-return',[1024,yt,min(req.get('rightReturnMainXEnd',1200),xr),coreb],tile,prior))
bl=req.get('bottomReturnXStart',max(54,xl) if side=='left' else xl);br=min(req.get('rightReturnMainXEnd',1200),xr) if side=='right' else xr
if row==4:rects.append(('bottom-return',[bl,1139,br,req.get('bottomReturnMainYEnd',1200)],'r06_c10',bottom))
else:rects.append(('bottom-return',[bl,1024,br,min(req.get('bottomReturnMainYEnd',1200),4096-y)],tile,prior))
for name,crop,desttile,src in rects:
 l,t,r,b=crop;dest=[x+l,y+t-(4096 if desttile=='r06_c10' else 0),x+r,y+b-(4096 if desttile=='r06_c10' else 0)];dl,dt,dr,db=dest;assert 0<=dl<dr<=4096 and 0<=dt<db<=4096
 off=req.get('joinedMainOffsetX',0);crop=[l+off,t,r+off,b];p=F/(name+'.png');J.crop(crop).save(p)
 if desttile==tile:
  if src is None:assert not np.any(before[dt:db,dl:dr,3])
  fragment.paste(J.crop(crop).convert('RGBA'),(dl,dt));changes[dt:db,dl:dr]=True
 else:coupled.paste(J.crop(crop).convert('RGBA'),(dl,dt));bottomchanges[dt:db,dl:dr]=True
 patches.append({'name':name,'asset':ref(p),'cropFromJoinedLTRB':crop,'destinationTile':desttile,'destinationTileLTRB':dest,'requiredPriorSource':src,'nativeScale':1,'mustApplyTogether':True})
save(F/'visual-review.json',{'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'image':ref(F/'joined.png'),'reviewMethod':'Whole native output and coupled boundary strips reviewed at native scale.','inspectedImages':[ref(z) for z in (F/'qa').glob('*.png')],'localVisualAccepted':True,'formalAccepted':False,'wholeTileAccepted':False,'findings':[(D/'qa-accepted.txt').read_text(encoding='utf8')],'actualModel':None,'actualQuality':None})
m={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'tianyong_festival','tile':tile,'tileGlobalOrigin':[36864,16384],'nativeScale':1,'windowTileLocalLTRB':req.get('manifestWindowTileLocalLTRB',req['tileLocalCropLTRB']),'windowGlobalLTRB':req.get('manifestWindowGlobalLTRB',req['globalCropLTRB']),'joined':ref(F/'joined.png'),'visualReview':ref(F/'visual-review.json'),'assembly':ref(F/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':prep['savedCheckpoint'],'requiresPriorManifest':prep['requiresPriorManifest'],'note':'Apply every rectangle atomically with exact live prior ROI checks. Root state not modified by local preparation.'};save(F/'manifest.json',m)
after=np.array(fragment);afterbottom=np.array(coupled);assert np.array_equal(after[~changes],before[~changes]);assert np.array_equal(afterbottom[~bottomchanges],beforebottom[~bottomchanges]);coverage=int(np.count_nonzero(after[:,:,3]==255));assert coverage==int(np.count_nonzero(before[:,:,3]==255))+(newr-newl)*(coreb-yt)
fragment.save(F/(tile+'-fragment.png'))
if row==4:
 coupled.save(F/'r06_c10-coupled.png');bottom={**ref(F/'r06_c10-coupled.png'),'tile':'r06_c10','tileLocalLTRB':[0,0,4096,4096],'nativeScale':1}
 save(F/'r06_c10-coupled.png.generation.json',{'operation':'Exact native mandatory coupled return','sources':[prep['coupledBottom'],ref(F/'joined.png')],'manifest':ref(F/'manifest.json'),'output':bottom,'actualModel':None,'actualQuality':None,'nativeScale':1,'noUpscale':True,'pixelsOutsideManifestExact':True,'formalAccepted':False})
save(F/(tile+'-fragment.png.generation.json'),{'operation':'Exact native patch composition','sources':[prior,ref(F/'joined.png')],'manifest':ref(F/'manifest.json'),'output':ref(F/(tile+'-fragment.png')),'actualModel':None,'actualQuality':None,'nativeScale':1,'noUpscale':True,'coveragePixels':coverage,'pixelsOutsideManifestExact':True,'formalAccepted':False})
save(F/'joined.png.generation.json',{'operation':'Native assembly; see assembly for actual AI source windows and ownership','output':ref(F/'joined.png'),'assembly':ref(F/'assembly.json'),'sources':[ref(D/'native.png'),ref(D/'context.png')],'nativeScale':1,'noUpscale':True,'actualModel':None,'actualQuality':None,'formalAccepted':False})
save(B/'local-source-checkpoint.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':tile,'fragment':ref(F/(tile+'-fragment.png')),'nativeScale':1,'coveragePixels':coverage,'coupledBottom':bottom,'bottomNativeHalo':cp.get('bottomNativeHalo'),'manifest':ref(F/'manifest.json'),'previousManifest':prep['requiresPriorManifest'],'contextJoined':ref(Path(req.get('contextForContinuation',str(F/'joined.png')))),'formalAccepted':False,'rootPublished':False})
print(json.dumps({'manifest':ref(F/'manifest.json'),'coveragePixels':coverage,'fragment':ref(F/(tile+'-fragment.png')),'coupledBottom':bottom}))


