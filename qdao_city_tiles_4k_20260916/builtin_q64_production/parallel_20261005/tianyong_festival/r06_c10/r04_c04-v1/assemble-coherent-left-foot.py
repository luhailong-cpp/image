from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
D=Path(__file__).parent;T=D.parents[1];F=D/'final-v7';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True);read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()};save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
base=read(D/'final-v6/assembly.json');s=base['latestBottom'];s11=base['rightNeighbor'];src=np.array(Image.open(s['file']).convert('RGBA'));src11=np.array(Image.open(s11['file']).convert('RGBA'));j=np.array(Image.open(D/'final-v6/joined.png').convert('RGB'))[:,80:];n=np.array(Image.open(D/'repair-left-boundary-v1/native.png').convert('RGB'))
full=np.zeros((1954,1754,3),dtype='uint8');full[:,500:]=j;full[1139:,:500]=src[:815,2457:2957,:3]
y,x=np.indices((1254,1254));sm=lambda v:np.clip(v,0,1)**2*(3-2*np.clip(v,0,1))
w=sm(x/60)*sm((1253-x)/100)*sm((y-40)/40)*(1-sm((y-920)/160))
# At y<439, x<500 is unclaimed r06 context; fill for a coherent displayed union, never included in new-core.
full[700:1139,:500]=n[:439,:500]
region=full[700:1954,:1254];full[700:1954,:1254]=np.rint(region*(1-w[:,:,None])+n*w[:,:,None]).astype('uint8')
Image.fromarray(full).save(F/'joined.png');Image.fromarray(full[:1254,500:1754]).save(F/'context-main1254.png')
candidate=Image.fromarray(src);candidate.paste(Image.fromarray(full[1139:1780,:1639]).convert('RGBA'),(2457,0));ca=np.array(candidate)
candidate.crop((2297,0,2957,750)).save(Q/'left-return-boundary.png')
Image.fromarray(np.concatenate([ca[:750,3896:4096],src11[:750,:200]],axis=1)).save(Q/'right-return-boundary.png')
Image.fromarray(full).crop((0,1100,1754,1800)).save(Q/'full-return.png');Image.fromarray(full).crop((500,650,1754,1454)).save(Q/'body.png')
assert np.array_equal(ca[:641,4035:4096],src[:641,4035:4096])
rec={**base,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'output':ref(F/'joined.png'),'windowGlobalLTRB':[39321,23437,41075,25391],'compositeDimension':[1754,1954],'leftBoundaryRepair':ref(D/'repair-left-boundary-v1/native.png'),'leftBoundaryNativeWindowGlobalLTRB':[39321,24137,40575,25391],'leftBoundarySelectedFootSubject':True,'leftSelectionFeatherX':[0,60,1153,1253],'leftSelectionFeatherY':[40,80,920,1080],'registrationApplied':False,'maxDx':0,'maxDy':0,'notes':['Entire coherent left gray rim and carved plinth chosen from native repair, with source fade outside its left silhouette.','All changed source ROI coordinates are explicit; root right61 untouched exactly.','Extra500 columns above committed new core are unclaimed context only.'],'bottomReturnLTRB':[2457,0,4096,641]};save(F/'assembly.json',rec)
q=read(D/'request.json');q.update({'selectedFinalDirectory':'final-v7','manifestWindowTileLocalLTRB':[2457,2957,4211,4911],'manifestWindowGlobalLTRB':[39321,23437,41075,25391],'joinedMainOffsetX':500,'bottomReturnXStart':-500,'bottomReturnMainYEnd':1780,'contextForContinuation':str(F/'context-main1254.png')});save(D/'request.json',q)
print(json.dumps(ref(F/'joined.png')))
