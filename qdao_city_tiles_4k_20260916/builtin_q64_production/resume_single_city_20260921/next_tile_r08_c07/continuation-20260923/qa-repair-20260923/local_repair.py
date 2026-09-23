"""Bounded c07 repair. New files only; no shared state or source overwrites."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, re, shutil, sys
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
C07=HERE.parents[1]
SESSION=C07.parent
REPO=next(p for p in HERE.parents if (p/'config/image-generation.json').is_file())
V=C07/'continuation-20260923/versions/hard-core-20260923T075129893416Z'
SOURCE=V/'r08_c07.png'
SOURCE_SHA='e39ff9aedaab71c42501c14f7a99f7d50e7a2858bc001521464355f7c94ce156'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,obj):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f: json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec)
    old=sys.dont_write_bytecode;sys.dont_write_bytecode=True
    try: spec.loader.exec_module(mod)
    finally: sys.dont_write_bytecode=old
    return mod
city_path=SESSION/'tools/city_repair.py'
city=load_module('c07_city_repair_functions',city_path)

def prepare():
    assert sha(SOURCE)==SOURCE_SHA
    out=HERE/'prepared';out.mkdir(exist_ok=False)
    pixels=city.png(SOURCE,[4096,4096]);box=[0,2386,1254,3640]
    context=out/'context-native-1254.png';Image.fromarray(pixels[2386:3640,0:1254]).save(context)
    # Same smoothstep band as city_repair; left fade omitted because the defect
    # reaches the source tile left edge. Right/top/bottom fade remain 80px.
    yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
    a=np.clip((112+32-np.abs(yy-627))/(64),0,1);a=a*a*(3-2*a)
    edge=np.clip(np.minimum.reduce([yy,1253-xx,1253-yy])/80,0,1);edge=edge*edge*(3-2*edge)
    alpha=np.rint(a*edge*255).astype(np.uint8)
    mask=out/'mask.png';Image.fromarray(alpha).save(mask)
    prep={'source':str(SOURCE),'sourceSha256':sha(SOURCE),'sourceRecord':str(V/'assembly.json'),'sourceRecordSha256':sha(V/'assembly.json'),
          'context':str(context),'contextSha256':sha(context),'mask':str(mask),'maskSha256':sha(mask),'canvasBoxLTRB':box,
          'maskShape':'horizontal','bandWidthPixels':224,'bandFeatherPixels':32,'outerContextFadePixels':80,
          'leftEdgeFadeDisabledReason':'Observed artificial horizontal line reaches x=0; fix only the masked y-band at that edge.',
          'globalMaskNonzeroBoundsLTRB':[0,2869,1253,3158],'maximumAllowedShiftPixels':8.0,'upscaled':False,'formalAccepted':False}
    write(out/'prepared.json',prep)
    refs=[str(context),str(C07/'native/r04_c01.v2.png'),str(REPO/'designs/gameplay-ui/04-guild.png')]
    prompt='''Use case: precise-object-edit. Edit image 1 ONLY. Return exactly one opaque native 1254x1254 PNG with the identical crop, pixel scale, camera and exact stone-joint geometry. Image 2 is ONLY the already approved clean stone material. Image 3 is ONLY the approved Daoist Q/chibi painting style; do not import UI, text, objects or details.\nThis is a microscopic local cleanup, not a redesign. In image 1 there is an artificial ruler-straight horizontal pasted-image boundary at local y=570 (global y=2956), crossing ivory stone faces and two existing vertical stone grooves. There is also a weaker pasted rectangular tonal step at local y=686 (global y=3072). Remove only those artificial pasted-image boundaries, by continuing the same extremely smooth quiet ivory stone shading and continuously joining the existing vertical grooves without changing their width, location, bevel silhouette or gold geometry. They are not real tile divisions. Keep the real horizontal stone joints, rounded beveled outlines and gold border intact.\nEdit only the narrow horizontal band local y=483..772. Keep all pixels outside that band as unchanged as possible and maintain identical content through every image edge. Maintain the exact existing brick sizes, the vertical grooves at approximately x=244 and x=640, and gold strip near x=1200. No objects, no extra seams, no mottled texture, cracks, veins, flakes, cloud patches, grain, noise, frosting or glow. Retain clean bright warm ivory, subtly rounded full volumes, broad sparse quiet smooth shading. Output the exact image-1 crop at native resolution, no rescale, no whole map, no border, no labels.'''
    request={'prompt':prompt,'referenced_image_paths':refs}
    write(out/'actual-request.json',request)
    config=REPO/'config/image-generation.json';(out/'config.snapshot.json').write_bytes(config.read_bytes())
    capability=SESSION/'continuation-20260923/model-capability.json'
    write(out/'preflight.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'sourceSha256':sha(SOURCE),'assemblySha256':sha(V/'assembly.json'),
        'actualRequest':{'file':str(out/'actual-request.json'),'sha256':sha(out/'actual-request.json')},'references':[{'file':p,'sha256':sha(p)} for p in refs],
        'configuration':{'file':str(config),'sha256':sha(config),'snapshotSha256':sha(out/'config.snapshot.json')},
        'capability':{'file':str(capability),'sha256':sha(capability)},'tool':'image_gen.imagegen','exposedArguments':['prompt','referenced_image_paths','num_last_images_to_include'],
        'actualModel':None,'actualQuality':None,'generatedAt':None,'backendModelVerified':False})
    print(json.dumps({'prepared':str(out/'prepared.json'),'actualRequest':str(out/'actual-request.json')}))

def apply():
    out=HERE/'prepared';prep=read(out/'prepared.json');receipt=read(out/'receipt.json');req=read(out/'actual-request.json')
    assert receipt['request']==req
    for k in ['source','sourceRecord','context','mask']:assert sha(prep[k])==prep[k+'Sha256'],k
    for ref in read(out/'preflight.json')['references']:assert sha(ref['file'])==ref['sha256']
    native=Path(re.search(r' as (.+?\.png) by default\.',receipt['response']['output_hint'],re.DOTALL).group(1))
    before=city.png(SOURCE,[4096,4096]);context=city.png(prep['context'],[1254,1254]);repair=city.png(native,[1254,1254])
    alpha=np.asarray(Image.open(prep['mask'])).copy();assert alpha.shape==(1254,1254)
    sys.path.insert(0,str(SESSION/'tools/vendor'))
    helper_path=SESSION.parents[0]/'tools/mechanical_join.py'
    helper=load_module('c07_mechanical_repair',helper_path)
    result,flow,correction,registration=helper.registered_join(context,repair,alpha,max_shift=8.0,match_tone=True)
    assert np.array_equal(result[alpha==0],context[alpha==0])
    after=before.copy();after[2386:3640,0:1254]=result
    changed=np.any(after!=before,axis=2);allowed=np.zeros((4096,4096),bool);allowed[2386:3640,0:1254]=alpha>0
    assert not np.any(changed&~allowed)
    assert np.array_equal(after[3640:],before[3640:])
    directory=HERE/'repaired-v1';directory.mkdir(exist_ok=False)
    for original,name in [(native,'repair-native-1254.png'),(out/'receipt.json','request-receipt.json'),(Path(prep['mask']),'mask.png')]:
        with original.open('rb') as a,(directory/name).open('xb') as b:shutil.copyfileobj(a,b)
        assert sha(original)==sha(directory/name)
    Image.fromarray(result).save(directory/'context-after.png');Image.fromarray(after).save(directory/'r08_c07.png')
    np.save(directory/'flow.npy',flow,allow_pickle=False);np.save(directory/'correction.npy',correction,allow_pickle=False)
    for name,box in [('repair-focus-after',(0,2670,1254,3297)),('repair-line-after',(0,2880,1254,3158))]:Image.fromarray(after).crop(box).save(directory/(name+'.png'))
    prev=Image.fromarray(after);prev.thumbnail((1024,1024));prev.save(directory/'overview-preview-only.png')
    record={'schemaVersion':1,'tileId':'r08_c07','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'repaired_candidate_pending_visual_QA_not_published',
        'prepared':{'file':str(out/'prepared.json'),'sha256':sha(out/'prepared.json')},'sourceCandidate':{'file':str(SOURCE),'sha256':sha(SOURCE)},
        'sourceRecord':{'file':prep['sourceRecord'],'sha256':prep['sourceRecordSha256']},'originalNativeOutput':{'file':str(native),'sha256':sha(native),'actualNativePixels':[1254,1254]},
        'preflight':{'file':str(out/'preflight.json'),'sha256':sha(out/'preflight.json')},'actualRequest':{'file':str(out/'actual-request.json'),'sha256':sha(out/'actual-request.json')},
        'actualModel':None,'actualQuality':None,'generatedAt':None,'completedAtUtcObserved':receipt['completedAtUtcObserved'],'backendModelVerified':False,
        'helper':{'file':str(helper_path),'sha256':sha(helper_path)},'cityRepairReference':{'file':str(city_path),'sha256':sha(city_path)},
        'script':{'file':str(Path(__file__)),'sha256':sha(__file__)},'canvasBoxLTRB':prep['canvasBoxLTRB'],'registration':registration,
        'maskNonzeroBoundsLTRB':prep['globalMaskNonzeroBoundsLTRB'],'changedCanvasPixelCount':int(changed.sum()),'outsideMaskPixelsUnchanged':True,
        'bottom456RowsUnchanged':True,'originalNativeBytesPreserved':True,'finalArtUpscaled':False,'resampling':'Bounded <=8px optical alignment of repair plus local tone matching only; no enlargement',
        'formalAccepted':False,'visualAcceptancePassed':False,'runtimePublished':False,'files':{p.name:{'file':str(p),'sha256':sha(p)} for p in directory.iterdir() if p.is_file()}}
    write(directory/'repair.json',record);assert sha(SOURCE)==SOURCE_SHA
    print(json.dumps({'candidate':str(directory/'r08_c07.png'),'sha256':sha(directory/'r08_c07.png'),'record':str(directory/'repair.json'),'registration':registration}))

if __name__=='__main__':
    {'prepare':prepare,'apply':apply}[sys.argv[1]]()
