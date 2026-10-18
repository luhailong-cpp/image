"""Native south external seam repair; integer selection only; frozen south core."""
from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, datetime, sys, shutil
R=Path(__file__).resolve().parent; B=R.parent.parent
ANCHOR=B.parents[1]/'fishing-village-game-20261009/southwest/qa/pair-r14c06-r14c07-v3-r14_c07-context-native.png'
EXPECTED_ANCHOR='f99ce424bb494d46b3d8fe89f32aac0b6037797a05bdd76b3429fba5e95b2d9c'
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
    x=int(sys.argv[3]);base=Path(sys.argv[4]);assembly=Path(sys.argv[5])
    north=arr(base);south=arr(ANCHOR)
    image=np.concatenate((north[3584:4096,x:x+1254],south[0:742,x:x+1254]),axis=0)
    assert image.shape==(1254,1254,3)
    inp=R/f'{name}.input-native.png'; save(inp,image)
    prompt='Precisely repair the horizontal map splice in this actual 1254 by 1254 native hand-painted game-map crop. Return opaque 1254 by 1254 with exactly the same frame, pixel scale and composition. The splice is exactly at image row 512. The bottom reference region, rows 512 through 1253, is a fixed neighbouring map tile: preserve it and all its rock, water, foam, lighting and brush marks exactly. Change only the upper half as needed to join naturally into that fixed lower half, especially rows 150 through 511. Continue the lower rock outlines, stone cracks, painted planes and water ripples into the upper half smoothly, keeping the large shoreline and rock mass positions. Remove the straight pasted line and abrupt texture scale/color changes with newly painted native detail. Preserve the upper 115 rows and outer left/right 115 pixel bands as closely as possible. The contact at row 512 must align to the exact existing bottom-side features; do not shift the fixed bottom half to match the upper half. Preserve daylight, rounded Q-style painted coastal rocks and turquoise sea. No new objects, landmass, people, text, UI, border, grid, global redesign, blur, resampling, zoom or smoothing filter.'
    req={'repairId':name,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r13_c07','baseContext':pin(base),'baseAssembly':pin(assembly),'anchor':pin(ANCHOR),'input':pin(inp),'references':[pin(inp)],'contextNativeBox':[x,3584,x+1254,4838],'globalNativeBox':[24461+x,52621,25715+x,53875],'globalCoreBox':[24576+x,52736,25600+x,53760],'coreInNative':[115,115,1139,1139],'allowedGeneratedImageBox':[0,115,1254,627],'lockedNeighbourImageBox':[0,627,1254,1254],'fixedNeighborNorthHaloImageBox':[0,512,1254,627],'prompt':prompt,'arguments':{'prompt':prompt,'referenced_image_paths':[str(inp)],'transparent_background':False},'route':'builtin','actualModel':None,'formalAccepted':False}
    js(R/f'{name}.request.json',req);print(json.dumps({'request':str(R/f'{name}.request.json'),'input':str(inp)}))
elif cmd=='archive':
    src=Path(sys.argv[3]);out=R/f'{name}.native.png';im=Image.open(src);assert im.size==(1254,1254)
    assert im.mode in ('RGB','RGBA')
    if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
    assert not out.exists();shutil.copy2(src,out)
    js(R/f'{name}.generation.json',{'repairId':name,'originalToolFile':pin(src),'saved':pin(out),'dimensions':[1254,1254],'mode':im.mode,'request':pin(R/f'{name}.request.json'),'route':'builtin','actualModel':None,'actualQuality':None,'nativePixelsResampled':False})
    print(json.dumps(pin(out)))
elif cmd=='compose':
    req=read(R/f'{name}.request.json'); basepath=Path(sys.argv[3]); assembly=Path(sys.argv[4]); ver=sys.argv[5]
    x=req['contextNativeBox'][0];base=arr(basepath);old=arr(req['input']['path']);genpath=R/f'{name}.native.png';gen=arr(genpath)
    assert sha(req['input']['path'])==req['input']['sha256']
    assert np.array_equal(base[3584:4096,x:x+1254],old[:512]),'Cannot rebase after this inspected source region changed'
    cost=np.mean((old.astype(float)-gen.astype(float))**2,axis=2)
    bottom=512+dp(cost[512:627].T)
    yy,xx=np.indices((627,1254));fromgen=yy<bottom[None,:]
    patch=old[:627].copy();patch[fromgen]=gen[:627][fromgen]
    current=base[3584:4211,x:x+1254].copy()
    outercost=np.mean((current.astype(float)-patch.astype(float))**2,axis=2)
    top=115+dp(outercost[115:230].T);left=dp(outercost[:,:230]);right=1024+dp(outercost[:,1024:])
    take=yy>=top[None,:]
    if x>0:take &= xx>=left[:,None]
    if x<3072:take &= xx<right[:,None]
    south=arr(ANCHOR);candidate=base.copy();candidate[4211:4326,x:x+1254]=south[115:230,x:x+1254]
    candidate[3584:4211,x:x+1254][take]=patch[take]
    ids=np.zeros((4326,4326),np.uint8);ids[4211:4326,x:x+1254]=2
    ids[3584:4211,x:x+1254][take & fromgen]=1;ids[3584:4211,x:x+1254][take & ~fromgen]=2
    mask=np.zeros((1254,1254),np.uint8);mask[:627]=take.astype(np.uint8)*255
    comp=old.copy();comp[:627]=current;comp[:627][take]=patch[take]
    out=R/f'{name}-assembly-{ver}';out.mkdir(exist_ok=False)
    save(out/'context-native.png',candidate);save(out/'r13_c07.candidate.png',candidate[115:4211,115:4211]);save(out/'repair-source-mask.png',mask);save(out/'source-layer-id.png',ids);save(out/'actual-join-native.png',comp)
    replay=base.copy();replay[4211:4326,x:x+1254]=south[115:230,x:x+1254];replay[3584:4211,x:x+1254][take & fromgen]=gen[:627][take & fromgen];replay[3584:4211,x:x+1254][take & ~fromgen]=old[:627][take & ~fromgen]
    proof={'sourceReplayMismatches':int(np.any(replay!=candidate,axis=2).sum()),'outsideSelectionChanges':int(np.any(base[ids==0]!=candidate[ids==0],axis=1).sum()),'rowsBefore3584Changes':int(np.any(base[:3584]!=candidate[:3584],axis=2).sum()),'neighborFileUnchanged':sha(ANCHOR)==EXPECTED_ANCHOR,'fixedNeighbourCorePixelsChanged':0}
    assert proof['sourceReplayMismatches']==proof['outsideSelectionChanges']==proof['rowsBefore3584Changes']==0
    crops=[]
    for side,box in [('contact',[0,477,1254,777]),('top',[0,0,1254,345]),('left',[0,0,230,777]),('right',[1024,0,1254,777])]:
        p=out/f'{side}.png';save(p,comp[box[1]:box[3],box[0]:box[2]]);crops.append(dict(pin(p),imageBox=box,scale=1))
    rec={'compositionVersion':2,'script':pin(Path(__file__)), 'tile':'r13_c07','formalAccepted':False,'status':'pending-native-visual-QA','baseContext':pin(basepath),'baseAssembly':pin(assembly),'request':pin(R/f'{name}.request.json'),'source':pin(genpath),'generation':pin(R/f'{name}.generation.json'),'anchor':pin(ANCHOR),'globalNativeBox':req['globalNativeBox'],'contextNativeBox':req['contextNativeBox'],'context':pin(out/'context-native.png'),'candidate':pin(out/'r13_c07.candidate.png'),'dimensions':[4096,4096],'mask':pin(out/'repair-source-mask.png'),'sourceLayerId':pin(out/'source-layer-id.png'),'layerLegend':{'0':'unchanged pinned base','1':'generated1254 exact globally mapped pixels','2':'frozen south anchor north halo exact global pixels in own final115 core strip and bottom halo'},'proof':proof,'qaCrops':crops,'actualJoin':pin(out/'actual-join-native.png'),'selectedRepairPixels':int(take.sum()),'topPath':top.tolist(),'bottomPath':bottom.tolist(),'leftPath':left.tolist(),'rightPath':right.tolist(),'route':'builtin','actualModel':None,'operation':'hard source selection plus exact crop; no blend, paint or resampling'}
    js(out/'assembly.json',rec);print(json.dumps({'assembly':pin(out/'assembly.json'),'candidate':rec['candidate'],'proof':proof}))

