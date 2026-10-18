"""Exact native pixels only: own west repair against frozen west context."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime,sys,shutil
R=Path(__file__).resolve().parent;B=R.parent.parent
ANCHOR=B/'repairs/r13c06-south-external-oct16-v1/S04-assembly-v4/context-native.png'
EXPECTED_ANCHOR='cf01cf3f67be4ee0ce7a5c6296edcc306c3a030bab9ffbe3b8d96def36fba047'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def arr(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def save(p,a):
    with Path(p).open('xb') as f:Image.fromarray(a).save(f,format='PNG')
def js(p,a):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(a,f,ensure_ascii=False,indent=2)
def dp(cost):
    h,w=cost.shape;prev=cost[0].copy();links=np.zeros((h,w),np.int8)
    for r in range(1,h):
        z=np.stack((prev,np.r_[np.inf,prev[:-1]],np.r_[prev[1:],np.inf]));q=np.argmin(z,axis=0)
        links[r]=np.array([0,-1,1],np.int8)[q];prev=cost[r]+np.min(z,axis=0)
    path=np.empty(h,np.int32);path[-1]=np.argmin(prev)
    for r in range(h-1,0,-1):path[r-1]=path[r]+links[r,path[r]]
    return path
cmd,name=sys.argv[1:3];assert sha(ANCHOR)==EXPECTED_ANCHOR
if cmd=='prepare':
    y=int(sys.argv[3]);base=Path(sys.argv[4]);assembly=Path(sys.argv[5]);own=arr(base);west=arr(ANCHOR)
    assert sha(base)==read(assembly)['context']['sha256']
    image=np.concatenate((west[y:y+1254,3584:4326],own[y:y+1254,230:742]),axis=1)
    assert image.shape==(1254,1254,3);inp=R/f'{name}.input-native.png';save(inp,image)
    prompt='Use case: compositing. Precisely repair this vertical map splice in the attached actual 1254 by 1254 native hand-painted game map. Return opaque 1254 by 1254, identical pixel scale and framing. The splice is at image column 742. The fixed LEFT reference region, columns 0 through 741, belongs to the neighboring tile: preserve its exact water ripple paths, white foam, turquoise colors, lighting, brush marks and positions. Repaint only the RIGHT-side transition, mainly columns 742 through 1103, to continue those exact left-side features naturally into the existing right-side sea. Preserve the rightmost 115 columns and outer top/bottom 115 rows as closely as possible. The seam at column 742 must follow the existing LEFT features; do not shift the left side to fit the right. Remove the straight pasted line and interrupted wave/foam contours with crisp native painted detail. Keep the daylight, rounded Q-style hand-painted coastal map, the same large-scale layout and turquoise sea. Do not add land, rocks, objects, people, symbols, text, borders or UI. No global redesign, zoom, resampling, blur, feathering or smoothing filter.'
    req={'repairId':name,'tile':'r13_c07','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseContext':pin(base),'baseAssembly':pin(assembly),'anchor':pin(ANCHOR),'input':pin(inp),'contextNativeBox':[-512,y,742,y+1254],'globalNativeBox':[23949,49037+y,25203,50291+y],'globalCoreBox':[24064,49152+y,25088,50176+y],'coreInNative':[115,115,1139,1139],'allowedGeneratedImageBox':[627,0,1139,1254],'lockedNeighbourImageBox':[0,0,627,1254],'fixedNeighborEastHaloImageBox':[627,0,742,1254],'prompt':prompt,'arguments':{'prompt':prompt,'referenced_image_paths':[str(inp)],'transparent_background':False},'route':'builtin','actualModel':None,'formalAccepted':False}
    js(R/f'{name}.request.json',req);print(json.dumps({'input':str(inp),'request':str(R/f'{name}.request.json')}))
elif cmd=='archive':
    src=Path(sys.argv[3]);out=R/f'{name}.native.png';im=Image.open(src);assert im.size==(1254,1254)
    assert im.mode in ('RGB','RGBA')
    if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
    assert not out.exists();shutil.copy2(src,out)
    js(R/f'{name}.generation.json',{'repairId':name,'originalToolFile':pin(src),'saved':pin(out),'dimensions':[1254,1254],'mode':im.mode,'request':pin(R/f'{name}.request.json'),'route':'builtin','actualModel':None,'actualQuality':None,'nativePixelsResampled':False});print(json.dumps(pin(out)))
elif cmd=='compose':
    req=read(R/f'{name}.request.json');basepath=Path(sys.argv[3]);assembly=Path(sys.argv[4]);ver=sys.argv[5];y=req['contextNativeBox'][1]
    base=arr(basepath);old=arr(req['input']['path']);genpath=R/f'{name}.native.png';gen=arr(genpath);west=arr(ANCHOR)
    assert sha(req['input']['path'])==req['input']['sha256'] and sha(basepath)==read(assembly)['context']['sha256']
    rebase=np.any(base[y:y+1254,230:742]!=old[:,742:],axis=2)
    assert not rebase[230:].any(),'Rebase outside prior upper overlap forbidden'
    g=read(R/f'{name}.generation.json');assert sha(genpath)==g['saved']['sha256'] and sha(R/f'{name}.request.json')==g['request']['sha256']
    cost=np.mean((old.astype(float)-gen.astype(float))**2,axis=2);left=627+dp(cost[:,627:742])
    yy,xx=np.indices((1254,627));fromgen=(xx+627)>=left[:,None];patch=old[:,627:].copy();patch[fromgen]=gen[:,627:][fromgen]
    current=base[y:y+1254,115:742].copy();outercost=np.mean((current.astype(float)-patch.astype(float))**2,axis=2)
    right=397+dp(outercost[:,397:512]);top=dp(outercost[:230].T);bottom=1024+dp(outercost[1024:].T)
    if y==2048:bottom=1139+dp(outercost[1139:].T)
    if y==3072:top=dp(outercost[:115].T)
    take=xx<right[:,None]
    if y>0:take &= yy>=top[None,:]
    if y<3072:take &= yy<bottom[None,:]
    candidate=base.copy();candidate[y:y+1254,0:115]=west[y:y+1254,4096:4211];candidate[y:y+1254,115:742][take]=patch[take]
    ids=np.zeros((4326,4326),np.uint8);ids[y:y+1254,:115]=2;ids[y:y+1254,115:742][take & fromgen]=1;ids[y:y+1254,115:742][take & ~fromgen]=2
    mask=np.zeros((1254,1254),np.uint8);mask[:,627:]=take.astype(np.uint8)*255;comp=old.copy();comp[:,627:]=current;comp[:,627:][take]=patch[take]
    out=R/f'{name}-assembly-{ver}';out.mkdir(exist_ok=False)
    save(out/'context-native.png',candidate);save(out/'r13_c07.candidate.png',candidate[115:4211,115:4211]);save(out/'repair-source-mask.png',mask);save(out/'source-layer-id.png',ids);save(out/'actual-join-native.png',comp)
    replay=base.copy();replay[y:y+1254,:115]=west[y:y+1254,4096:4211];replay[y:y+1254,115:742][take & fromgen]=gen[:,627:][take & fromgen];replay[y:y+1254,115:742][take & ~fromgen]=old[:,627:][take & ~fromgen]
    proof={'sourceReplayMismatches':int(np.any(replay!=candidate,axis=2).sum()),'outsideSelectionChanges':int(np.any(base[ids==0]!=candidate[ids==0],axis=1).sum()),'columnsAfter742Changes':int(np.any(base[:,742:]!=candidate[:,742:],axis=2).sum()),'neighborFileUnchanged':sha(ANCHOR)==EXPECTED_ANCHOR,'fixedNeighbourCorePixelsChanged':0}
    assert proof['sourceReplayMismatches']==proof['outsideSelectionChanges']==proof['columnsAfter742Changes']==0
    rec={'compositionVersion':'2-upper-lower-overlap-coverage','rebaseChangedPixelsInPriorUpperOverlap':int(rebase.sum()),'tile':'r13_c07','formalAccepted':False,'status':'pending-native-visual-QA','script':pin(Path(__file__)),'baseContext':pin(basepath),'baseAssembly':pin(assembly),'request':pin(R/f'{name}.request.json'),'source':pin(genpath),'generation':pin(R/f'{name}.generation.json'),'anchor':pin(ANCHOR),'globalNativeBox':req['globalNativeBox'],'contextNativeBox':req['contextNativeBox'],'context':pin(out/'context-native.png'),'candidate':pin(out/'r13_c07.candidate.png'),'dimensions':[4096,4096],'mask':pin(out/'repair-source-mask.png'),'sourceLayerId':pin(out/'source-layer-id.png'),'layerLegend':{'0':'unchanged pinned base','1':'generated1254 exact globally mapped pixels','2':'frozen west anchor east halo in own first115 core strip and left halo'},'proof':proof,'actualJoin':pin(out/'actual-join-native.png'),'selectedRepairPixels':int(take.sum()),'topPath':top.tolist(),'bottomPath':bottom.tolist(),'leftPath':left.tolist(),'rightPath':right.tolist(),'route':'builtin','actualModel':None,'operation':'hard source selection plus exact crop; no blend, paint or resampling'}
    js(out/'assembly.json',rec);print(json.dumps({'assembly':pin(out/'assembly.json'),'candidate':rec['candidate'],'context':rec['context'],'proof':proof}))
