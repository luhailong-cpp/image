from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,sys
import numpy as np
from PIL import Image
H=Path(__file__).resolve().parent
B=H/'cross-boundary-plan-20260923T120626884718Z'
S=H.parent.parent
A=S.parent.parent
P=A.parent
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
def check(x):assert sha(x['file'])==x['sha256'],x
plan=read(B/'plan.json')
def stable():
    for k in ['sourceR08','sourceR09','sourceR08Record','sourceR09Record','style','material']:check(plan[k])
def preflight(pid):
    stable();q=B/pid;prep=read(q/'prepared.json')
    for k in ['request','prompt','context','mask']:check(prep[k])
    for r in prep['references']:check(r)
    req=read(q/'planned-request.json');assert req['prompt']==Path(prep['prompt']['file']).read_text(encoding='utf-8')
    assert read(P/'config/image-generation.json')==plan['configSnapshot'],'Config changed'
    with (q/'submitted-request.json').open('xb') as f:f.write((q/'planned-request.json').read_bytes())
    write(q/'execution-preflight.json',{'verifiedAtUtc':now(),'plan':info(B/'plan.json'),'prepared':info(q/'prepared.json'),'request':info(q/'submitted-request.json'),'configSnapshot':plan['configSnapshot'],'references':prep['references'],'sourceR08':plan['sourceR08'],'sourceR09':plan['sourceR09'],'capability':{'tool':'image_gen.imagegen','exposedParameters':['prompt','referenced_image_paths','num_last_images_to_include'],'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'actualModel':None,'actualQuality':None,'route':'builtin','evidence':'Current tool metadata inspected before execution; config is target only'},'inputImagesViewedAtOriginalPixelScale':True,'plannedMaskViewed':True,'maximumBatchCalls':3})
    print(json.dumps({'directory':str(q),'request':req}))
def ingest(pid):
    stable();q=B/pid;receipt=read(q/'receipt.json');pre=read(q/'execution-preflight.json');check(pre['request'])
    assert receipt['request']==read(q/'submitted-request.json')
    source=Path(re.search(r' as (.+?\.png) by default\.',receipt['response']['output_hint']).group(1))
    assert source.is_file() and Image.open(source).size==(1254,1254)
    target=q/'native-1254.png'
    with target.open('xb') as f:f.write(source.read_bytes())
    gen={'schemaVersion':1,'file':str(target),'sha256':sha(target),'width':1254,'height':1254,'format':'PNG','generatedAt':None,'observedCompletionAt':receipt['completedAtUtc'],'timestampSemantics':'clock tool UTC immediately after return; backend generation time undisclosed','tool':'image_gen.imagegen','route':'builtin','configSnapshot':plan['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'backendModelVerified':False,'unverifiedReason':'Host-managed builtin has no model/quality parameters and response disclosed neither value','prompt':info(q/'planned-prompt.txt'),'request':info(q/'submitted-request.json'),'references':pre['references'],'evidence':info(q/'receipt.json'),'preflight':info(q/'execution-preflight.json'),'editBefore':info(q/'context-native-1254.png'),'originalNativeOutput':info(source),'resized':False,'upscaled':False,'rawBytesPreserved':True,'formalAccepted':False}
    write(q/'native-1254.png.generation.json',gen);print(json.dumps({'native':info(target),'record':info(q/'native-1254.png.generation.json')}))
def apply():
    stable();before=[np.asarray(Image.open(plan[k]['file']).convert('RGB')) for k in ['sourceR08','sourceR09']];after=[x.copy() for x in before];masks=[np.zeros((4096,4096),np.uint8) for _ in range(2)];sources=[]
    for ent in plan['patches']:
        q=B/ent['id'];prep=read(q/'prepared.json');gen=read(q/'native-1254.png.generation.json');native=np.asarray(Image.open(q/'native-1254.png').convert('RGB'));context=np.asarray(Image.open(q/'context-native-1254.png').convert('RGB'));m=np.asarray(Image.open(q/'planned-allowed-mask.png'))
        assert sha(q/'native-1254.png')==gen['sha256'];check(prep['context']);check(prep['mask']);check(gen['evidence']);check(gen['request'])
        alpha=m[:,:,None].astype(np.float32)/255
        patched=np.rint(context*(1-alpha)+native*alpha).astype(np.uint8)
        assert np.array_equal(patched[m==0],context[m==0])
        x=prep['originalCombinedContextLTRB'][0];left,right=prep['ownedXRange'];l=left-x;r=right-x
        assert np.array_equal(context[:627,l:r],before[0][3469:,left:right]);assert np.array_equal(context[627:,l:r],before[1][:627,left:right])
        after[0][3469:,left:right]=patched[:627,l:r];after[1][:627,left:right]=patched[627:,l:r];masks[0][3469:,left:right]=m[:627,l:r];masks[1][:627,left:right]=m[627:,l:r]
        sources.append({'prepared':info(q/'prepared.json'),'native':info(q/'native-1254.png'),'generation':info(q/'native-1254.png.generation.json'),'mask':info(q/'planned-allowed-mask.png')})
    O=H/'versions'/('cross-boundary-pair-v1-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));O.mkdir();entries=[]
    for i,name in enumerate(['r08_c09','r09_c09']):
        changed=np.any(after[i]!=before[i],axis=2);assert not np.any(changed&(masks[i]==0))
        Image.fromarray(after[i]).save(O/(name+'.png'));Image.fromarray(masks[i]).save(O/(name+'-allowed-mask.png'))
        ys,xs=np.where(changed)
        entries.append({'tile':name,'candidate':info(O/(name+'.png')),'source':plan['sourceR08' if i==0 else 'sourceR09'],'mask':info(O/(name+'-allowed-mask.png')),'changedPixels':int(changed.sum()),'changedBoundsLTRB':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'outsideAllowedMaskPixelsUnchanged':True,'allNineInternalJunctionCrops512Unchanged':all(np.array_equal(before[i][y-256:y+256,x-256:x+256],after[i][y-256:y+256,x-256:x+256]) for y in [1024,2048,3072] for x in [1024,2048,3072]),'horizontalInternalSeams512Unchanged':all(np.array_equal(before[i][y-256:y+256],after[i][y-256:y+256]) for y in [1024,2048,3072])})
    stable();record={'schemaVersion':1,'createdAtUtc':now(),'status':'new_pair_candidate_pending_visual_review','plan':info(B/'plan.json'),'candidates':entries,'sources':sources,'sourceFilesUnchanged':True,'registration':'none','resampling':'none','nativeArtEnlarged':False,'returnFeatherPixels':32,'newModelCalls':3,'actualModel':None,'actualQuality':None,'accepted':False,'formalAccepted':False,'clientRuntimeAccepted':False,'selectionChanged':False,'script':info(Path(__file__))};write(O/'assembly.json',record)
    Q=O/'qa';Q.mkdir();items=[]
    def save(name,im,scope):
        f=Q/(name+'.png');im.save(f);items.append({'id':name,**info(f),'scope':scope,'pixelScale':'1:1','reviewed':False})
    joined=np.concatenate([after[0][-627:],after[1][:627]],axis=0)
    for n in range(4):save(f'shared-wide-{n+1:02}',Image.fromarray(joined[:,n*1024:(n+1)*1024]),{'xRange':[n*1024,(n+1)*1024],'boundaryY':627,'upperReturnY':435,'lowerReturnY':1075})
    for ti,name in enumerate(['r08_c09','r09_c09']):
        im=Image.fromarray(after[ti])
        for axis in ['v','h']:
            for n in [1,2,3]:
                p=1024*n;board=Image.new('RGB',(1024,2048));parts=[]
                for j in range(4):
                    box=[p-256,1024*j,p+256,1024*(j+1)] if axis=='v' else [1024*j,p-256,1024*(j+1),p+256]
                    c=im.crop(box)
                    if axis=='v':c=c.transpose(Image.Transpose.ROTATE_90)
                    board.paste(c,(0,j*512));parts.append(box)
                save(f'{name}-full-{axis}-{n:02}',board,{'segmentsLTRB':parts,'rotation90ForVertical':axis=='v'})
        jb=Image.new('RGB',(1536,1536))
        for yi,y in enumerate([1024,2048,3072]):
            for xi,x in enumerate([1024,2048,3072]):jb.paste(im.crop((x-256,y-256,x+256,y+256)),(512*xi,512*yi))
        save(f'{name}-nine-junctions',jb,{'centersXY':[[x,y] for y in [1024,2048,3072] for x in [1024,2048,3072]]})
    ledger=read(S/'current-coverage-ledger.json');tiles={t['tile']:t for t in ledger['tiles']}
    neighborEntries=[]
    for side,name in [('left','r09_c08'),('right','r09_c10'),('bottom','r10_c09')]:
        t=tiles[name]['candidate'];f=A/t['file'];assert sha(f)==t['sha256'];arr=np.asarray(Image.open(f).convert('RGB'));neighborEntries.append(info(f))
        if side=='left':edge=np.concatenate([arr[:,-256:],after[1][:,:256]],axis=1)
        elif side=='right':edge=np.concatenate([after[1][:,-256:],arr[:,:256]],axis=1)
        else:edge=np.concatenate([after[1][-256:],arr[:256]],axis=0)
        board=Image.new('RGB',(1024,2048))
        for j in range(4):
            seg=Image.fromarray(edge[j*1024:(j+1)*1024]) if side!='bottom' else Image.fromarray(edge[:,j*1024:(j+1)*1024])
            if side!='bottom':seg=seg.transpose(Image.Transpose.ROTATE_90)
            board.paste(seg,(0,j*512))
        save(f'r09-{side}-external-full',board,{'neighbor':info(f),'side':side,'fullSpan':4096})
    write(Q/'index.json',{'assembly':info(O/'assembly.json'),'evidence':items,'neighbors':neighborEntries,'fourTileJunctions':'not yet prepared/reviewed; no pass implied','formalAccepted':False})
    print(json.dumps({'version':str(O),'assembly':info(O/'assembly.json'),'candidates':entries,'qa':info(Q/'index.json')}))
if __name__=='__main__':
    if sys.argv[1]=='preflight':preflight(sys.argv[2])
    elif sys.argv[1]=='ingest':ingest(sys.argv[2])
    elif sys.argv[1]=='apply':apply()
