from pathlib import Path
from PIL import Image
import json,hashlib,datetime,numpy as np
T=Path(__file__).resolve().parent
R=T/'review/resumed-local-repairs-20261016'
R.mkdir(exist_ok=False)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def write(p,j):assert not p.exists();p.write_text(json.dumps(j,indent=2,ensure_ascii=False),encoding='utf-8')
def png(p,im):assert not p.exists();im.save(p)
def checked(r):assert sha(r['path'])==r['sha256'];return Path(r['path'])
S=read(T/'repairs/south-post-v2-20261013/composition.json')
W=read(T/'repairs/west-grout-v1-20261013/composition.json')
base=Image.open(checked(S['base'])).convert('RGB')
original=np.asarray(base).copy()
def operation(im,c):
 for k in ['native','receipt','preparation','alpha']:checked(c[k])
 rec=read(c['receipt']['path']);assert rec['actualSize']==[1254,1254] and rec['actualModel'] is None
 n=Image.open(c['native']['path']).convert('RGB');assert n.size==(1254,1254)
 x0,y0,x1,y1=c['tilePlacement'];old=np.asarray(im.crop((x0,y0,x1,y1))).astype(np.uint32)
 new=np.asarray(n.crop(c['nativeCrop'])).astype(np.uint32);a=np.asarray(Image.open(c['alpha']['path'])).astype(np.uint32)[:,:,None]
 assert old.shape==new.shape and a.shape[:2]==old.shape[:2]
 out=((new*a+old*(255-a)+127)//255).astype(np.uint8)
 im.paste(Image.fromarray(out),(x0,y0));return im
for c in [S,W]:
 replay=operation(Image.open(checked(c['base'])).convert('RGB'),c)
 assert np.array_equal(np.asarray(replay),np.asarray(Image.open(checked(c['candidate'])).convert('RGB')))
B=operation(operation(base.copy(),S),W)
out=np.asarray(B)
assert np.array_equal(original[:,3981:4096],out[:,3981:4096])
assert np.array_equal(original[:200],out[:200])
changed=np.any(out!=original,axis=2)
allowed=np.zeros((4096,4096),dtype=bool)
for c in [S,W]:
 x0,y0,x1,y1=c['tilePlacement'];allowed[y0:y1,x0:x1]=True
assert not np.any(changed&~allowed)
C=Image.open(checked(S['contextBase'])).convert('RGB');C.paste(B,(115,115))
dest=T/'candidate/r15_c15-4k-south-v2-west-v1-20261016.png'
ctx=T/'candidate/r15_c15-context-4326-south-v2-west-v1-20261016.png'
png(dest,B);png(ctx,C)
sources=[]
for edge,tile,strip in [('north','r14_c15',(0,3896,4096,4096)),('west','r15_c14',(3896,0,4096,4096))]:
 old=read(T/f'review/assembly-008f4b817c43676ebb32/native-segments/{edge}-neighbor-source.json')['candidate']
 cur=read(T.parent/tile/'candidate/latest-assembly.json')['candidate']
 oldi=Image.open(checked(old)).convert('RGB');curi=Image.open(checked(cur)).convert('RGB')
 same=np.array_equal(np.asarray(oldi.crop(strip)),np.asarray(curi.crop(strip)))
 sources.append({'edge':edge,'old':old,'current':cur,'actualUsedNeighborStrip':list(strip),'oldQaNeighborStripUnchanged':same})
 if edge=='west':west=curi
crops=[]
def crop(name,im,box):
 p=R/(name+'.png');png(p,im);crops.append({'name':name,'path':str(p),'sha256':sha(p),'box':box,'size':list(im.size),'scale':1})
crop('south-repair-after',B.crop((1880,3700,2500,4096)),[1880,3700,2500,4096])
crop('south-repair-before',base.crop((1880,3700,2500,4096)),[1880,3700,2500,4096])
crop('south-repair-original-target',Image.open(T/'repairs/south-post-v2-20261013/target-native-1254.png'),[1520,2842,2774,4096])
join=Image.new('RGB',(800,800));join.paste(west.crop((3696,2100,4096,2900)),(0,0));join.paste(B.crop((0,2100,400,2900)),(400,0))
crop('west-repair-real-join',join,[-400,2100,400,2900])
crop('west-mask-right-boundary',B.crop((120,2100,340,2900)),[120,2100,340,2900])
crop('west-mask-upper-boundary',B.crop((0,2140,360,2330)),[0,2140,360,2330])
crop('west-mask-lower-boundary',B.crop((0,2710,360,2910)),[0,2710,360,2910])
manifest={'tile':'r15_c15','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'pending_local_visual_qa','base':S['base'],'baseAssembly':ref(T/'candidate/r15_c15-assembly-008f4b817c43676ebb32.json'),'operations':[{'sourceComposition':ref(T/'repairs/south-post-v2-20261013/composition.json'),'order':1,**{k:S[k] for k in ['native','receipt','preparation','nativeCrop','tilePlacement','alpha','formula']}},{'sourceComposition':ref(T/'repairs/west-grout-v1-20261013/composition.json'),'order':2,**{k:W[k] for k in ['native','receipt','preparation','nativeCrop','tilePlacement','alpha','formula']}}],'candidate':ref(dest),'context':ref(ctx),'contextBase':S['contextBase'],'contextOperation':'paste 4096 core at115,115; original halo retained as nonauthoritative','nativeEditSources':2,'actualModel':None,'resize':False,'warp':False,'colorCorrection':False,'formalAccepted':False}
write(R/'selection-manifest.json',manifest)
write(R/'verification.json',{'candidate':ref(dest),'context':ref(ctx),'sourceCompositionsReplayed':True,'changeRestrictedToRecordedMasks':True,'eastLast115PixelIdenticalToBase':True,'northFirst200PixelIdenticalToBase':True,'neighborSourceComparison':sources,'pixelChanges':int(changed.sum()),'qaCrops':crops,'formalAccepted':False})
print(json.dumps({'candidate':ref(dest),'context':ref(ctx),'manifest':ref(R/'selection-manifest.json'),'verification':ref(R/'verification.json'),'neighborQaReuse':sources},ensure_ascii=False))
