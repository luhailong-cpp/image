"""Local receipt/crop bookkeeping. Never calls models or grants visual QA."""
from pathlib import Path
import datetime, hashlib, importlib.util, json, sys
from PIL import Image

T=Path(__file__).resolve().parent
Z=T.parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj,exclusive=False):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x' if exclusive else 'w',encoding='utf-8') as f: json.dump(obj,f,ensure_ascii=False,indent=2)
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def start():
    p=read(T/'progress.json');v=p['currentVersion']
    previous=read(T/'current-execution.json') if (T/'current-execution.json').exists() else {}
    assert not previous.get('inFlight'), 'Existing in-flight call must be resolved first'
    data={'tile':'r15_c12','patch':p['currentPatch'],'version':v,'status':'submitting_builtin_imagegen','startedAt':now(),
          'tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,
          'request':str(T/'records'/f'{v}.request.json'),'owner':'/root/seam_resume','inFlight':True}
    write(T/'records'/f'{v}.execution-current.json',data,True);write(T/'current-execution.json',data)
    print(json.dumps({'version':v,'inFlight':True}))

def prepare(patch,extra=None):
    spec=importlib.util.spec_from_file_location('west',Z/'production_workflow_west_extension_20261016_v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    r=m.prepare('r15_c12',patch,extra)
    print(json.dumps({k:r[k] for k in ['version','request','target']}))

def unselect_failed(version):
    prep=read(T/'records'/f'{version}.preparation.json');patch=prep['logicalPatch']
    assert read(T/'review'/'quick-qa-20261016'/version/'visual-qa.json')['status']=='failed'
    mapping=read(T/'active-native-map.json');assert mapping[patch]==version
    write(T/'records'/f'{version}.selection-before-unselect.json',mapping,True)
    mapping.pop(patch);write(T/'active-native-map.json',mapping)
    p=read(T/'progress.json');p.update(activeNativeCount=len(mapping),status='failed_patch_preserved_pending_retry_or_independent_work',formalAccepted=False);write(T/'progress.json',p)
    print(json.dumps({'removedFromActiveOnly':version,'allImagesPreserved':True,'activeCount':len(mapping)}))

def receive(version,source):
    source=Path(source);prep=read(T/'records'/f'{version}.preparation.json')
    with Image.open(source) as im:
        assert im.size==(1254,1254) and im.format=='PNG'
        assert im.mode=='RGB' or (im.mode=='RGBA' and im.getextrema()[3]==(255,255))
        image=im.convert('RGB')
    receipt=T/'records'/f'{version}.receipt.json'
    write(receipt,{'schemaVersion':1,'status':'succeeded_pending_quick_visual_qa','tool':'image_gen.imagegen','route':'builtin',
        'createdAt':now(),'actualModel':None,'actualQuality':None,'sourcePath':str(source),'sourceSha256':sha(source),
        'observedSize':[1254,1254],'resizedAfterGeneration':False,'finalArtUpscaled':False,
        'request':prep['request'],'requestSha256':prep['requestSha256'],
        'modelEvidence':'Builtin response returned image_url and local output_hint only; no actual model or quality returned.'},True)
    helper=Z/'production_workflow_west_extension_20261016_v2.py'
    spec=importlib.util.spec_from_file_location('west',helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    result=m.ingest('r15_c12',version,str(source),str(receipt))
    review=T/'review'/'quick-qa-20261016'/version;review.mkdir(parents=True,exist_ok=True)
    crops=[]
    # Exact side-by-side source pixels, no rescale; inspect continuity at the core boundary.
    co=prep['coordinates']['contextBox']
    for anchor in prep['anchors']:
        direction=anchor['direction'];box=anchor['target'];src=Image.open(anchor['path']).convert('RGB')
        if anchor['sourceKind']=='actual4096_core' and direction=='right':
            y0,y1=box[1],box[3];sy0,sy1=anchor['sourceCrop'][1],anchor['sourceCrop'][3]
            paired=Image.new('RGB',(512,y1-y0));paired.paste(image.crop((883,y0,1139,y1)),(0,0));paired.paste(src.crop((0,sy0,256,sy1)),(256,0))
            out=review/'east-real-core-pair.png';paired.save(out);crops.append({'path':str(out),'sha256':sha(out),'kind':'unscaled adjacent true core pair','seamX':256,'generatedCrop':[883,y0,1139,y1],'sourceCrop':[0,sy0,256,sy1],'sourceSha256':anchor['sha256']})
        else:
            if direction=='right': b=(974,0,1254,1254)
            elif direction=='left': b=(0,0,280,1254)
            elif direction=='top': b=(0,0,1254,280)
            else: b=(0,974,1254,1254)
            out=review/f'{direction}-generated-overlap.png';image.crop(b).save(out)
            crops.append({'path':str(out),'sha256':sha(out),'kind':'unscaled generated overlap','crop':list(b),'anchor':anchor})
            if anchor['sourceKind']=='active_native_context':
                if direction in ['top','bottom']:
                    paired=Image.new('RGB',(1254,512))
                    before,after=(src,image) if direction=='top' else (image,src)
                    paired.paste(before.crop((0,883,1254,1139)),(0,0));paired.paste(after.crop((0,115,1254,371)),(0,256))
                else:
                    paired=Image.new('RGB',(512,1254))
                    before,after=(src,image) if direction=='left' else (image,src)
                    paired.paste(before.crop((883,0,1139,1254)),(0,0));paired.paste(after.crop((115,0,371,1254)),(256,0))
                out=review/f'{direction}-core-pair.png';paired.save(out)
                crops.append({'path':str(out),'sha256':sha(out),'kind':'unscaled adjacent core pair','sourceSha256':anchor['sha256'],'seamPosition':256})
    write(review/'evidence.json',{'version':version,'sourceSha256':sha(source),'native':result['file'],'crops':crops,'visualQA':'pending'},True)
    current={'tile':'r15_c12','patch':prep['logicalPatch'],'version':version,'status':'native_saved_pending_quick_qa','inFlight':False,'completedAt':now(),'source':str(source),'sourceSha256':sha(source),'native':result['file'],'actualModel':None,'actualQuality':None}
    write(T/'current-execution.json',current);write(T/'records'/f'{version}.execution-current.json',current)
    print(json.dumps({'ingest':result,'review':str(review),'crops':[c['path'] for c in crops]}))

def qa(version,status,note):
    assert status in ['local_pass','failed']
    review=T/'review'/'quick-qa-20261016'/version
    evidence=read(review/'evidence.json')
    write(review/'visual-qa.json',{'version':version,'reviewedAt':now(),'status':status,'scope':'Quick native layout/anchor continuity only; complete tile internal/external QA remains pending','native':evidence['native'],'sha256':evidence['sourceSha256'],'evidence':str(review/'evidence.json'),'notes':note,'formalAccepted':False,'mayPropagate':status=='local_pass'},True)
    current=read(T/'current-execution.json');current.update(status='quick_qa_'+status,inFlight=False,quickQA=str(review/'visual-qa.json'));write(T/'current-execution.json',current);write(T/'records'/f'{version}.execution-current.json',current)
    print(json.dumps({'qa':str(review/'visual-qa.json'),'sha256':sha(review/'visual-qa.json'),'status':status}))

if __name__=='__main__': globals()[sys.argv[1]](*sys.argv[2:])
