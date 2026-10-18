"""Native south external seam repair; integer selection only; frozen south core."""
from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, datetime, sys, shutil
R=Path(__file__).resolve().parent; B=R.parent.parent
ANCHOR=B/'qa/r12c07-resume2-r19-v1/context-native.png'
EXPECTED_ANCHOR='99f50735f137c049b46ad315c5ea11873f9a30f25014561dcee25aaaec3e6f72'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p): return dict(path=str(p),sha256=sha(p))
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def arr(p): return np.asarray(Image.open(p).convert('RGB')).copy()
def save(p,a):
    with Path(p).open('xb') as f: Image.fromarray(a).save(f,format='PNG')
def js(p,a):
    with Path(p).open('x',encoding='utf-8') as f: json.dump(a,f,ensure_ascii=False,indent=2)
def dp(cost):
    h,w=cost.shape; prev=cost[0].copy(); links=np.zeros((h,w),np.int8)
    for r in range(1,h):
        z=np.stack((prev,np.r_[np.inf,prev[:-1]],np.r_[prev[1:],np.inf]))
        q=np.argmin(z,axis=0); links[r]=np.array([0,-1,1],np.int8)[q]; prev=cost[r]+np.min(z,axis=0)
    path=np.empty(h,np.int32);path[-1]=np.argmin(prev)
    for r in range(h-1,0,-1): path[r-1]=path[r]+links[r,path[r]]
    return path
cmd,name=sys.argv[1:3]
assert sha(ANCHOR)==EXPECTED_ANCHOR
if cmd=='prepare':
    x=int(sys.argv[3]);base=Path(sys.argv[4]);assembly=Path(sys.argv[5]);own=arr(base);north=arr(ANCHOR)
    image=np.concatenate((north[3584:4326,x:x+1254],own[230:742,x:x+1254]),axis=0);assert image.shape==(1254,1254,3)
    inp=R/f'{name}.input-native.png';save(inp,image)
    prompt='Repair the horizontal pasted discontinuity at row742 in this exact native 1254 by 1254 coastal game-map image. Output opaque 1254 by 1254, identical frame and scale. Keep the entire upper742 rows in their exact existing positions: they are fixed northern neighboring artwork. Repaint the lower side of the break, rows742 through1138, to naturally continue the existing turquoise water strands, white foam, gray-gold rounded rock facets and cracks from above into the lower scene. Preserve the bottommost115 rows and both outer side layouts so this local repair fits the wider map. Remove the straight pasted line across the entire width, using native hand-painted details and irregular rock transitions, with consistent daylight colors and brush size. The actual tile boundary is at row627 and is fixed; do not change it. Preserve the shoreline silhouette, existing main rock masses and water directions. No additional objects, land, people, boats, text, UI or grid. No blur, wash, zoom, resizing or global redesign.'
    req={'repairId':name,'tile':'r13_c07','baseContext':pin(base),'baseAssembly':pin(assembly),'anchor':pin(ANCHOR),'input':pin(inp),'contextNativeBox':[x,-512,x+1254,742],'globalNativeBox':[24461+x,48525,25715+x,49779],'actualCoreSeamImageY':627,'initialSpliceImageY':742,'arguments':{'prompt':prompt,'referenced_image_paths':[str(inp)],'transparent_background':False},'route':'builtin','actualModel':None,'formalAccepted':False};js(R/f'{name}.request.json',req);print(json.dumps({'request':str(R/f'{name}.request.json'),'input':str(inp)}))
elif cmd=='archive':
    src=Path(sys.argv[3]);out=R/f'{name}.native.png';im=Image.open(src);assert im.size==(1254,1254);assert im.mode in ('RGB','RGBA')
    if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
    assert not out.exists();shutil.copy2(src,out);js(R/f'{name}.generation.json',{'repairId':name,'originalToolFile':pin(src),'saved':pin(out),'request':pin(R/f'{name}.request.json'),'dimensions':[1254,1254],'route':'builtin','actualModel':None,'resampled':False});print(json.dumps(pin(out)))
elif cmd=='compose':
    req=read(R/f'{name}.request.json');basepath=Path(sys.argv[3]);assembly=Path(sys.argv[4]);ver=sys.argv[5];x=req['contextNativeBox'][0];base=arr(basepath);genpath=R/f'{name}.native.png';gen=arr(genpath);north=arr(ANCHOR);old=arr(req['input']['path']);prior=base[:742,x:x+1254].copy()
    assert np.array_equal(prior[230:,230:1024],old[742:,230:1024]),'central reference changed'
    src=gen[512:].copy();anc=north[4096:4326,x:x+1254];cost=np.mean((src[:230].astype(float)-anc.astype(float))**2,axis=2);top=135+dp(cost[135:230].T);yy,xx=np.indices((742,1254));usegen=yy>=top[None,:];patch=src.copy();patch[:230][~usegen[:230]]=anc[~usegen[:230]]
    cost=np.mean((patch.astype(float)-prior.astype(float))**2,axis=2);bottom=627+dp(cost[627:].T);left=dp(cost[:,:230]);right=1024+dp(cost[:,1024:]);take=yy<bottom[None,:]
    if x>0:take &= xx>=left[:,None]
    if x<3072:take &= xx<right[:,None]
    candidate=base.copy();candidate[:742,x:x+1254][take]=patch[take];ids=np.zeros((4326,4326),np.uint8);sub=ids[:742,x:x+1254];sub[take & usegen]=1;sub[take & ~usegen]=2
    comp=old.copy();comp[512:]=candidate[:742,x:x+1254]
    out=R/f'{name}-assembly-{ver}';out.mkdir();save(out/'context-native.png',candidate);save(out/'r13_c07.candidate.png',candidate[115:4211,115:4211]);save(out/'source-layer-id.png',ids);save(out/'actual-join-native.png',comp)
    replay=base.copy();gm=sub==1;am=sub[:230]==2;replay[:742,x:x+1254][gm]=src[gm];replay[:230,x:x+1254][am]=anc[am];proof={'sourceReplayMismatches':int(np.any(replay!=candidate,axis=2).sum()),'outsideSelectionChanges':int(np.any(base[ids==0]!=candidate[ids==0],axis=1).sum()),'rows742AndBelowChanges':int(np.any(base[742:]!=candidate[742:],axis=2).sum()),'northAnchorUnchanged':sha(ANCHOR)==EXPECTED_ANCHOR}
    assert proof['sourceReplayMismatches']==proof['outsideSelectionChanges']==proof['rows742AndBelowChanges']==0
    crops=[]
    for side,box in [('contact',[0,480,1254,930]),('bottom',[0,909,1254,1254]),('left',[0,480,345,1254]),('right',[909,480,1254,1254])]:
        p=out/f'{side}.png';save(p,comp[box[1]:box[3],box[0]:box[2]]);crops.append(dict(pin(p),imageBox=box,scale=1))
    rec={'tile':'r13_c07','status':'pending-native-visual-QA','formalAccepted':False,'baseContext':pin(basepath),'baseAssembly':pin(assembly),'request':pin(R/f'{name}.request.json'),'source':pin(genpath),'generation':pin(R/f'{name}.generation.json'),'anchor':pin(ANCHOR),'context':pin(out/'context-native.png'),'candidate':pin(out/'r13_c07.candidate.png'),'contextNativeBox':req['contextNativeBox'],'sourceLayerId':pin(out/'source-layer-id.png'),'layerLegend':{'0':'pinned base unchanged','1':'generated input [512:] mapped to own context [0:742]','2':'same-global north anchor [4096:4326] mapped to own [0:230]'},'proof':proof,'qaCrops':crops,'actualJoin':pin(out/'actual-join-native.png'),'topPath':top.tolist(),'bottomPath':bottom.tolist(),'leftPath':left.tolist(),'rightPath':right.tolist(),'operation':'exact source selection; shared side masks for generation and anchor; no blend/resample/painting','route':'builtin','actualModel':None};js(out/'assembly.json',rec);print(json.dumps({'assembly':pin(out/'assembly.json'),'candidate':rec['candidate'],'proof':proof}))
