from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json
from datetime import datetime,timezone
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/village-west-courtyard')
R=Path(__file__).parent; Q=B/'qa/r12c07-resume2-north-hard-v1';Q.mkdir(parents=True,exist_ok=True)
P=B/'qa/r12c07-resume2-north-review-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
inp=load(P/'qa-inputs-v1.json');research=load(P/'source-research-v2.json')
basep=Path(inp['south']['path']);northp=Path(inp['north']['path']);assert sha(basep)==inp['south']['sha256'];assert sha(northp)==inp['north']['sha256']
base=np.asarray(Image.open(basep).convert('RGB'));north=np.asarray(Image.open(northp).convert('RGB'));donor=north[4096:4326].copy();assert base.shape==north.shape==(4326,4326,3)
donorp=R/'donor-native-same-global-4326x230.png';assert not donorp.exists();Image.fromarray(donor).save(donorp)
donorids=np.load(research['donorProvenanceProof']['sourceIdMap']['path']);np.save(R/'donor-native-source-ids.npy',donorids)
# A horizontal min-cost path chooses the last donor pixel per column. All RGB
# values in the output come directly from an input; costs do not alter pixels.
lo,hi=115,229
cost=np.mean(np.abs(donor[lo:hi+1].astype(np.float64)-base[lo:hi+1].astype(np.float64)),axis=2)
height,width=cost.shape;back=np.zeros((height,width),dtype=np.int8);score=cost[:,0].copy()
for x in range(1,width):
 choices=np.stack([np.r_[np.inf,score[:-1]]+0.25,score,np.r_[score[1:],np.inf]+0.25]);k=np.argmin(choices,axis=0);back[:,x]=k.astype(np.int8)-1;score=cost[:,x]+choices[k,np.arange(height)]
path=np.zeros(width,dtype=np.int32);row=int(np.argmin(score))
for x in range(width-1,-1,-1):
 path[x]=row+lo
 if x:row+=int(back[row,x])
assert np.all((path>=lo)&(path<=hi));assert np.max(np.abs(np.diff(path)))<=1
mask=np.zeros(base.shape[:2],dtype=np.uint8);mask[:230]=(np.arange(230)[:,None]<=path[None,:]).astype(np.uint8)
out=base.copy();m=mask[:230].astype(bool);out[:230][m]=donor[m]
np.save(R/'hard-mask-uint8.npy',mask);np.save(R/'cut-path-int32.npy',path);Image.fromarray(mask[:230]*255).save(R/'hard-mask-top230-bw.png')
sourceids=np.zeros(base.shape[:2],dtype=np.uint8);sourceids[:230][m]=donorids[m]+1;np.save(R/'source-ids-uint8.npy',sourceids)
contextp=Q/'context-native.png';corep=Q/'r12_c07.north-hard-native-4096.png';assert not contextp.exists();Image.fromarray(out).save(contextp);Image.fromarray(out[115:4211,115:4211]).save(corep)
replay=base.copy();loadedmask=np.load(R/'hard-mask-uint8.npy').astype(bool);loadeddonor=np.asarray(Image.open(donorp).convert('RGB'));replay[:230][loadedmask[:230]]=loadeddonor[loadedmask[:230]];saved=np.asarray(Image.open(contextp).convert('RGB'))
nativeReplay=np.zeros_like(donor)
allnative=list(research['nativeSources'])+[research['westernHaloSupplement']]
for i,v in enumerate(allnative):
 a=np.asarray(Image.open(v['path']).convert('RGB'));box=v['globalContextBox'];gx0,gy0,gx1,gy1=box;x0=max(24461,gx0);x1=min(28787,gx1);aa=a[44941-gy0:45171-gy0,x0-gx0:x1-gx0];where=donorids[:,x0-24461:x1-24461]==i;nativeReplay[:,x0-24461:x1-24461][where]=aa[where]
strips=[]
for i in range(4):
 x=115+1024*i;a=north[3866:4211,x:x+1024];b=out[115:745,x:x+1024];c=np.concatenate([a,b]);p=Q/f'N{i+1:02d}-actual-core-plus-lower-native.png';Image.fromarray(c).save(p);read=np.asarray(Image.open(p));segment=path[x:x+1024]
 strips.append({'id':f'N{i+1:02d}',**record(p),'size':[1024,975],'northContextBox':[x,3866,x+1024,4211],'candidateContextBox':[x,115,x+1024,745],'globalBox':[24461+x,44711,24461+x+1024,45686],'trueCoreJoinYInStrip':345,'newCutPathSouthContextYRangeInclusive':[int(segment.min()),int(segment.max())],'atLeastPixelsBelowNewCut':int(744-segment.max()),'cropIdentityDifferentPixels':int(np.any(read[:345]!=a,axis=2).sum()+np.any(read[345:]!=b,axis=2).sum())})
trace={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_actual_native_visual_review','formalAccepted':False,'tile':'r12_c07','globalContextBox':[24461,44941,28787,49267],'coreContextBox':[115,115,4211,4211],'base':record(basep),'baseAssembly':record(basep.parent/'assembly.json'),'northAnchor':record(northp),'sourceResearch':record(P/'source-research-v2.json'),'previousNorthQA':record(P/'review-v1.json'),'donor':{**record(donorp),'size':[4326,230],'northContextCropBox':[0,4096,4326,4326],'sameGlobalBox':[24461,44941,28787,45171],'destinationContextBox':[0,0,4326,230],'nativeSources':allnative,'sourceIds':record(R/'donor-native-source-ids.npy')},'method':'Binary hard selection: use donor for every y <= cutPath[x], original R18 elsewhere. Integer same-global pixels only.','pathSearch':{'loInclusive':lo,'hiInclusive':hi,'stepPerColumn':[-1,0,1],'cost':'mean RGB absolute donor/base difference at the same global pixel + 0.25 for each diagonal DP step','cutPath':record(R/'cut-path-int32.npy'),'selectedYRangeInclusive':[int(path.min()),int(path.max())]},'mask':{**record(R/'hard-mask-uint8.npy'),'shape':[4326,4326],'dtype':'uint8','values':[0,1],'zeroMeans':'R18','oneMeans':'donor'},'sourceIds':{**record(R/'source-ids-uint8.npy'),'dtype':'uint8','legend':{'0':'R18 complete historical trace referenced by baseAssembly',**{str(i+1):v['path'] for i,v in enumerate(allnative)}}},'context':{**record(contextp),'size':[4326,4326]},'candidate':{**record(corep),'size':[4096,4096]},'proof':{'hierarchicalFullContextReplayDifferentPixels':int(np.any(replay!=saved,axis=2).sum()),'nativeDonorReplayDifferentPixels':int(np.any(nativeReplay!=donor,axis=2).sum()),'uncoveredPixels':int((donorids==255).sum()),'differentPixelsOutsideAllowedY0To230':int(np.any(out[230:]!=base[230:],axis=2).sum()),'changedPixelsInY512AndBelow':int(np.any(out[512:]!=base[512:],axis=2).sum()),'coreCropIdentityDifferentPixels':int(np.any(np.asarray(Image.open(corep))!=out[115:4211,115:4211],axis=2).sum()),'anchorHashUnchanged':sha(northp)==inp['north']['sha256'],'baseHashUnchanged':sha(basep)==inp['south']['sha256'],'changedPixels':int(np.any(out!=base,axis=2).sum()),'noResize':True,'noBlend':True,'noBlur':True,'noColourChange':True,'noAI':True},'qaStrips':strips,'reuseRule':'Apply saved donor and saved mask only after verifying a new internal baseline has the same R18 top 230 RGB pixels; require a new full context replay, new trace and new output path. Old QA may be reused only for byte-identical affected crops. Never overwrite the input baseline.','scripts':[record(Path(__file__)),record(R/'replay.py')]}
(Q/'assembly.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'context':trace['context'],'candidate':trace['candidate'],'assembly':record(Q/'assembly.json'),'proof':trace['proof'],'pathRanges':[{'id':a['id'],'y':a['newCutPathSouthContextYRangeInclusive']} for a in strips]},ensure_ascii=False))
