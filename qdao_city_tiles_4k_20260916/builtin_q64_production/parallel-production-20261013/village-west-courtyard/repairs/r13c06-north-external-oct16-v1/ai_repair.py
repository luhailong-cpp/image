from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime,sys,shutil
R=Path(__file__).resolve().parent;B=R.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
anchor=B/'repairs/r12c06-resume-20261016-v1/north-hard-v1/context-native.png'
def save(p,a):
    with Path(p).open('xb') as f:Image.fromarray(a).save(f,format='PNG')
def js(p,o):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
def dp(cost):
    rows,cols=cost.shape;prev=cost[0].copy();links=np.zeros((rows,cols),np.int8)
    for r in range(1,rows):
        c=np.stack((prev,np.r_[np.inf,prev[:-1]],np.r_[prev[1:],np.inf]));q=np.argmin(c,axis=0);links[r]=np.array([0,-1,1],np.int8)[q];prev=cost[r]+np.min(c,axis=0)
    p=np.empty(rows,np.int32);p[-1]=np.argmin(prev)
    for r in range(rows-1,0,-1):p[r-1]=p[r]+links[r,p[r]]
    return p
cmd,name=sys.argv[1:3]
if cmd=='prepare':
    x=int(sys.argv[3]);base=Path(sys.argv[4]);north=np.asarray(Image.open(anchor).convert('RGB'));a=np.asarray(Image.open(base).convert('RGB'))
    im=np.concatenate([north[3840:4096,x:x+1254],a[:998,x:x+1254]],axis=0);assert im.shape==(1254,1254,3)
    dst=R/f'{name}.input.png';save(dst,im)
    prompt='Edit this exact 1254 by 1254 native game-map crop. Output exactly 1254 by 1254. Repair only the unnatural jagged splice and color/texture step in the shallow turquoise water around image rows 371 through 486, with a natural hand-painted transition extending at most to row 800. The top 371 rows are a locked upstream anchor: preserve their geometry, ripple positions, white foam and colors precisely. Preserve all water forms, rocks, foam channels, scale, daylight and palette. Continue the same ripple paths across the broken transition; replace the angular cut edges with coherent natural painted water. Match the existing lower water smoothly through actual new painted detail, not blur. Keep the outer left and right edges and the lower 350 rows unchanged so neighboring map pieces connect. No sharpening, resizing, smoothing filter, blur, new objects, text, UI, grid, border, or global redesign. This is a precise local seam repair, not a new scene.'
    if name=='N04bridge':prompt += ' The remaining defect is a very fine nearly-horizontal stepped color edge across blue pools directly below the rock, at image row371. Make the colors immediately below this row match the unchanged colors immediately above it, then develop natural water texture southward. Do not retain any ruler-straight or sawtooth line across a blue pool. Preserve the rock and white foam geometry exactly.'
    js(R/f'{name}.request.json',{'id':name,'atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input':str(dst),'inputSha256':sha(dst),'baseContext':str(base),'baseSha256':sha(base),'baseAssembly':str(base.parent/'assembly.json'),'baseAssemblySha256':sha(base.parent/'assembly.json'),'anchor':str(anchor),'anchorSha256':sha(anchor),'contextNativeBox':[x,-256,x+1254,998],'globalNativeBox':[20365+x,48781,21619+x,50035],'allowedRepairImageBox':[0,371,1254,906],'prompt':prompt,'route':'builtin-image_gen','actualModel':'not returned','status':'prepared','formalAccepted':False})
    print(json.dumps({'input':str(dst),'prompt':prompt}))
elif cmd=='archive':
    src=Path(sys.argv[3]);dst=R/f'{name}.generated-v1.png';assert not dst.exists();shutil.copy2(src,dst)
    with Image.open(dst) as im:assert im.size==(1254,1254);mode=im.mode
    js(R/f'{name}.receipt-v1.json',{'id':name,'source':str(src),'saved':str(dst),'sha256':sha(dst),'dimensions':[1254,1254],'mode':mode,'route':'builtin-image_gen','actualModel':'not returned','operation':'unaltered original copy','atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
elif cmd=='compose':
    req=json.loads((R/f'{name}.request.json').read_text());basepath=Path(req['baseContext']);assert sha(basepath)==req['baseSha256'];assert sha(anchor)==req['anchorSha256'];x=req['contextNativeBox'][0]
    base=np.asarray(Image.open(basepath).convert('RGB'));old=np.asarray(Image.open(req['input']).convert('RGB'));src=R/f'{name}.generated-v1.png';gen=np.asarray(Image.open(src).convert('RGB'));cost=np.mean((old.astype(float)-gen.astype(float))**2,axis=2)
    topband=int(sys.argv[3]) if len(sys.argv)>3 else 115
    version=sys.argv[4] if len(sys.argv)>4 else 'v1'
    rightband=int(sys.argv[5]) if len(sys.argv)>5 else 115
    t,b=371,906;h=b-t;w=1254;top=dp(cost[t:t+topband].T);bottom=h-100+dp(cost[b-100:b].T);left=dp(cost[t:b,:115]);right=w-rightband+dp(cost[t:b,w-rightband:]);yy,xx=np.indices((h,w));inside=(yy>=top[None,:])&(yy<=bottom[None,:])&(xx<=right[:,None])
    if x>0:inside &= xx>=left[:,None]
    mask=np.zeros((1254,1254),bool);mask[t:b]=inside
    comp=old.copy();comp[mask]=gen[mask];cand=base.copy();cand[:998,x:x+1254][mask[256:]]=gen[256:][mask[256:]]
    out=R/(name+'-assembly-'+version);out.mkdir(exist_ok=False);save(out/'context-native.png',cand);save(out/'r13_c06.candidate-native-4096.png',cand[115:4211,115:4211]);save(out/'patch-composite.png',comp);save(out/'mask.png',(mask*255).astype(np.uint8))
    ids=np.zeros(base.shape[:2],np.uint8);ids[:998,x:x+1254][mask[256:]]=1;save(out/'source-layer-id.png',ids)
    crops=[]
    for side,box in [('top',[0,291,1254,566]),('bottom',[0,726,1254,986]),('left',[0,291,195,986]),('right',[1059,291,1254,986])]:
        p=out/f'{side}.png';save(p,comp[box[1]:box[3],box[0]:box[2]]);crops.append({'side':side,'path':str(p),'sha256':sha(p),'imageBox':box,'scale':1})
    replay=base.copy();replay[:998,x:x+1254][mask[256:]]=gen[256:][mask[256:]]
    proof={'replayMismatch':int(np.any(replay!=cand,axis=2).sum()),'northHaloChanges':int(np.any(cand[:115]!=base[:115],axis=2).sum()),'outsideSelectionChanges':int(np.any(cand[ids==0]!=base[ids==0],axis=1).sum()),'rows650AndBelowChanges':int(np.any(cand[650:]!=base[650:],axis=2).sum()),'anchorUnchanged':sha(anchor)==req['anchorSha256']}
    rec={'tile':'r13_c06','formalAccepted':False,'status':'pending-visual-QA','base':{'path':str(basepath),'sha256':sha(basepath),'assembly':req['baseAssembly'],'assemblySha256':req['baseAssemblySha256']},'source':{'path':str(src),'sha256':sha(src),'dimensions':[1254,1254],'globalNativeBox':req['globalNativeBox']},'request':{'path':str(R/f'{name}.request.json'),'sha256':sha(R/f'{name}.request.json')},'contextNativeBox':req['contextNativeBox'],'selectedPixels':int(mask.sum()),'mask':{'path':str(out/'mask.png'),'sha256':sha(out/'mask.png'),'values':[0,255]},'sourceLayerIdMap':{'path':str(out/'source-layer-id.png'),'sha256':sha(out/'source-layer-id.png')},'context':{'path':str(out/'context-native.png'),'sha256':sha(out/'context-native.png')},'tile4096':{'path':str(out/'r13_c06.candidate-native-4096.png'),'sha256':sha(out/'r13_c06.candidate-native-4096.png')},'proof':proof,'qaCrops':crops,'operation':'native AI1254 local repair followed by integer crop and binary hard source selection; no blending, resampling, blur or drawing','route':'builtin-image_gen','actualModel':'not returned'}
    rec['selectionBands']={'top':topband,'right':rightband,'left':115,'bottom':100,'maskImageAllowedBox':[0,371,1254,906]}
    js(out/'assembly.json',rec);print(json.dumps({'out':str(out),'proof':proof,'contextSha256':rec['context']['sha256']}))
