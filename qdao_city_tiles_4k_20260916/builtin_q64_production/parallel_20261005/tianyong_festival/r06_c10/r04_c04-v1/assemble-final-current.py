from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
D=Path(__file__).parent;T=D.parents[1];F=D/'final-v6';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True);read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()};save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
root=read(T/'source-checkpoint.json');cs=read(root['candidateSetRecord']['file']);s=next(z for z in cs['candidates'] if z['tile']=='r07_c10');s11=next(z for z in cs['candidates'] if z['tile']=='r07_c11');assert ref(s['file'])['sha256']==s['sha256'] and ref(s11['file'])['sha256']==s11['sha256'];src=np.array(Image.open(s['file']).convert('RGBA'));src11=np.array(Image.open(s11['file']).convert('RGBA'))
j=np.array(Image.open(D/'final-v4/joined.png').convert('RGB'));bridge=np.array(Image.open(D/'repair-left-boundary-v1/native.png').convert('RGB'));c11p=T/'r07_c11/r01_c01-v1/join-v1/joined.png';c11=np.array(Image.open(c11p).convert('RGBA'))
assert np.array_equal(src[:115,4035:4096],c11[115:230,54:115]),'latest right corner lineage differs'
anchor=np.zeros((1954,1254,4),dtype='uint8');anchor[1024:1139,1024:]=c11[:115,:230];anchor[1139:,:1139]=src[:815,2957:4096];anchor[1139:,1139:]=src11[:815,:115]
y,x=np.indices((1954,1254));sm=lambda v:np.clip(v,0,1)**2*(3-2*np.clip(v,0,1))
rightw=sm((x-984)/94)*sm((y-1024)/56)*(anchor[:,:,3]==255)
j=np.rint(j*(1-rightw[:,:,None])+anchor[:,:,:3]*rightw[:,:,None]).astype('uint8')
full=np.zeros((1954,1334,3),dtype='uint8');full[:,80:]=j;full[1139:,:80]=src[:815,2877:2957,:3]
yy,xx=np.indices((550,165));w=sm(xx/10)*sm((164-xx)/10)*sm(yy/10)*sm((549-yy)/10)
region=full[1120:1670,:165];native=bridge[420:970,420:585];full[1120:1670,:165]=np.rint(region*(1-w[:,:,None])+native*w[:,:,None]).astype('uint8')
Image.fromarray(full).save(F/'joined.png');Image.fromarray(full[:1254,80:1334]).save(F/'context-main1254.png')
# Exact source outside the whole-ROI manifest remains untouched. Right61 are deliberately source-exact.
assert np.array_equal(full[1139:1780,80+1078:80+1139],src[:641,4035:4096,:3])
candidate=Image.fromarray(src,'RGBA');candidate.paste(Image.fromarray(full[1139:1780,:1219]).convert('RGBA'),(2877,0));ca=np.array(candidate)
candidate.crop((2717,0,3357,750)).save(Q/'left-return-boundary.png')
right=np.concatenate([ca[:750,3896:4096],src11[:750,:200]],axis=1);Image.fromarray(right).save(Q/'right-return-boundary.png')
Image.fromarray(full).crop((80,650,1334,1454)).save(Q/'body.png');Image.fromarray(full).crop((0,1520,1219,1850)).save(Q/'return-tail.png')
save(F/'assembly.json',{'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'output':ref(F/'joined.png'),'sources':[ref(D/'native.png'),ref(D/'repair-v3/native.png'),ref(D/'repair-left-boundary-v1/native.png'),s,s11,ref(c11p)],'baseAssembly':ref(D/'final-v4/assembly.json'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'toneCorrectionApplied':False,'windowGlobalLTRB':[39741,23437,41075,25391],'mainNativeWindowGlobalLTRB':[39821,23437,41075,24691],'repairWindowGlobalLTRB':[39821,24137,41075,25391],'leftBridgeWindowGlobalLTRB':[39321,24137,40575,25391],'compositeDimension':[1334,1954],'exactWorldCropOffsets':True,'bridgeSelectedNativeCropLTRB':[420,420,585,970],'bridgeDestinationJoinedLTRB':[0,1120,165,1670],'bridgeBoundaryFeatherPixels':10,'rootCheckpoint':ref(T/'source-checkpoint.json'),'latestBottom':s,'rightNeighbor':s11,'right61PixelsPreservedExact':True,'actualModel':None,'actualQuality':None,'formalAccepted':False,'limitations':['Top-left80 columns above y1139 lie outside new-core and are not coverage claims.','Joined is a coordinate-exact union of native AI windows; generated detail was not upscaled.']})
q=read(D/'request.json');q.update({'selectedFinalDirectory':'final-v6','manifestWindowTileLocalLTRB':[2877,2957,4211,4911],'manifestWindowGlobalLTRB':[39741,23437,41075,25391],'joinedMainOffsetX':80,'bottomReturnXStart':-80,'bottomReturnMainYEnd':1780,'contextForContinuation':str(F/'context-main1254.png')});save(D/'request.json',q)
prep=read(D/'preparation.json');save(D/'preparation-before-current-rebase.json',prep);cp=read(D/'source-checkpoint-input.json');cp['coupledBottom']=s;cp['rootRebaseEvidence']={'rootCheckpoint':ref(T/'source-checkpoint.json'),'rootCandidates':ref(root['candidateSetRecord']['file'])};save(D/'source-checkpoint-rebased-input.json',cp);prep['coupledBottom']=s;prep['savedCheckpoint']=ref(D/'source-checkpoint-rebased-input.json');prep['rebase']={'reason':'Live root07c10 right61 edge changed after generation; final preserves latest exact pixels there','latestSource':s,'rightSource':s11,'originalContextSourceRetainedInGenerationRecords':True};save(D/'preparation.json',prep)
print(json.dumps({'joined':ref(F/'joined.png'),'bottomSource':s,'returnTileLTRB':[2877,0,4096,641]}))
