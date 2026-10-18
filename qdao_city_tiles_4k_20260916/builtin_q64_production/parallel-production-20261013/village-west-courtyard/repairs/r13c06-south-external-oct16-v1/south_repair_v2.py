"""Native south external seam repair; integer selection only; frozen south core."""
from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, datetime, sys, shutil
R=Path(__file__).resolve().parent; B=R.parent.parent
ANCHOR=B.parents[1]/'fishing-village-game-20261009/southwest/qa/pair-r14c06-r14c07-v3-r14_c06-context-native.png'
EXPECTED_ANCHOR='3d59c2c8d07563732944bcc4d2948d8a48fad863c9f59a59a739fda79a312053'
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
    prompt='Edit this exact native 1254 by 1254 hand-painted coastal game-map crop. Output opaque 1254 by 1254, identical frame and scale. There is an obvious pasted horizontal break at image row 512. Repair the upper side of this break across the entire image width, including the small rocks and white foam at the left as well as the large gray rock. The lower 742 rows, from row 512 downward, are the exact fixed neighbouring art; preserve them precisely. Rebuild only upper rows 115 through 511 as necessary to continue the lower rock shapes, large facets, cracks and foam naturally upward, with no straight line at row 512. The uppermost 115 rows must retain their layout and water positions. This requires real native painted transition detail from the existing upper rock into the existing lower rock, not blur or a color wash. Keep the outer side structures in position but repair the visible break even at the left and right edges. Preserve every shoreline location, main rock mass, turquoise water color, daylight and painting style. Do not add land, people, new rocks, objects, text, grids, frames or UI. No resizing, blur, zoom or global repaint. The actual tile core boundary is at row 627; that and everything below it must exactly match the provided fixed lower drawing.'
    req={'repairId':name,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r13_c06','baseContext':pin(base),'baseAssembly':pin(assembly),'anchor':pin(ANCHOR),'input':pin(inp),'references':[pin(inp)],'contextNativeBox':[x,3584,x+1254,4838],'globalNativeBox':[20365+x,52621,21619+x,53875],'globalCoreBox':[20480+x,52736,21504+x,53760],'coreInNative':[115,115,1139,1139],'allowedGeneratedImageBox':[0,115,1254,512],'lockedNeighbourImageBox':[0,512,1254,1254],'prompt':prompt,'arguments':{'prompt':prompt,'referenced_image_paths':[str(inp)],'transparent_background':False},'route':'builtin','actualModel':None,'formalAccepted':False}
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
    top=115+dp(cost[115:230].T);left=dp(cost[:512,:115]);right=1139+dp(cost[:512,1139:])
    yy,xx=np.indices((512,1254));take=yy>=top[None,:]
    if x>0:take &= xx>=left[:,None]
    if x<3072:take &= xx<right[:,None]
    candidate=base.copy();candidate[3584:4096,x:x+1254][take]=gen[:512][take]
    south=arr(ANCHOR);candidate[4096:4326,x:x+1254]=south[0:230,x:x+1254]
    ids=np.zeros((4326,4326),np.uint8);ids[3584:4096,x:x+1254][take]=1;ids[4096:4326,x:x+1254]=2
    mask=np.zeros((1254,1254),np.uint8);mask[:512]=take.astype(np.uint8)*255
    comp=old.copy();comp[:512][take]=gen[:512][take]
    out=R/f'{name}-assembly-{ver}';out.mkdir(exist_ok=False)
    save(out/'context-native.png',candidate);save(out/'r13_c06.candidate.png',candidate[115:4211,115:4211]);save(out/'repair-source-mask.png',mask);save(out/'source-layer-id.png',ids);save(out/'actual-join-native.png',comp)
    replay=base.copy();replay[3584:4096,x:x+1254][take]=gen[:512][take];replay[4096:4326,x:x+1254]=south[0:230,x:x+1254]
    proof={'sourceReplayMismatches':int(np.any(replay!=candidate,axis=2).sum()),'outsideSelectionChanges':int(np.any(base[ids==0]!=candidate[ids==0],axis=1).sum()),'rowsBefore3584Changes':int(np.any(base[:3584]!=candidate[:3584],axis=2).sum()),'neighborFileUnchanged':sha(ANCHOR)==EXPECTED_ANCHOR,'fixedNeighbourCorePixelsChanged':0}
    assert proof['sourceReplayMismatches']==proof['outsideSelectionChanges']==proof['rowsBefore3584Changes']==0
    crops=[]
    for side,box in [('contact',[0,362,1254,777]),('top',[0,0,1254,345]),('left',[0,0,230,777]),('right',[1024,0,1254,777])]:
        p=out/f'{side}.png';save(p,comp[box[1]:box[3],box[0]:box[2]]);crops.append(dict(pin(p),imageBox=box,scale=1))
    rec={'tile':'r13_c06','formalAccepted':False,'status':'pending-native-visual-QA','baseContext':pin(basepath),'baseAssembly':pin(assembly),'request':pin(R/f'{name}.request.json'),'source':pin(genpath),'generation':pin(R/f'{name}.generation.json'),'anchor':pin(ANCHOR),'globalNativeBox':req['globalNativeBox'],'contextNativeBox':req['contextNativeBox'],'context':pin(out/'context-native.png'),'candidate':pin(out/'r13_c06.candidate.png'),'dimensions':[4096,4096],'mask':pin(out/'repair-source-mask.png'),'sourceLayerId':pin(out/'source-layer-id.png'),'layerLegend':{'0':'unchanged pinned base','1':'generated1254 exact globally mapped pixels','2':'frozen south anchor exact global pixels in last115 core rows and bottom115 halo'},'proof':proof,'qaCrops':crops,'actualJoin':pin(out/'actual-join-native.png'),'selectedRepairPixels':int(take.sum()),'topPath':top.tolist(),'leftPath':left.tolist(),'rightPath':right.tolist(),'route':'builtin','actualModel':None,'operation':'hard source selection plus exact crop; no blend, paint or resampling'}
    js(out/'assembly.json',rec);print(json.dumps({'assembly':pin(out/'assembly.json'),'candidate':rec['candidate'],'proof':proof}))

