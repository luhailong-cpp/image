"""Prepare/record 13 frozen c16 repairs using real same-window festival pixels.

prepare ID | record ID RAW | pin-west CORE_PATH CORE_SHA [EXTENDED_PATH]
Core tasks need completed tone only. West tasks additionally need explicit final
c15 lock. Optional preceding sources contribute ONLY their actual overlap crop.
No integration, DAY write, source substitution, resampling, or automatic QA pass.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, sys
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent;T=ROOT/'r08_c16';B=T/'repairs/consolidated-sync'
CONTRACT=T/'source-contract-v2/source-contract.json'
CONTRACT_SHA='e60640e0b49db49ecd7f932c4c99b41146ed2b2fc3fcbbedaaccf7c4d2afb289'
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
STYLE_SHA='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
IDS=[f'west-only-joint-s{i}' for i in range(1,5)]+['mast-1024','mast-2048','mast-3072','hull-upper','hull-lower','water-upper','water-lower','west-insertion-finish','west-rail-second']
PREVIOUS={'west-only-joint-s2':'west-only-joint-s1','west-only-joint-s3':'west-only-joint-s2','west-only-joint-s4':'west-only-joint-s3','mast-2048':'mast-1024','mast-3072':'mast-2048','hull-lower':'hull-upper','water-lower':'water-upper'}

def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p,role=None):return {'file':str(p),'sha256':sha(p),**({'role':role} if role else {})}
def verify(e):assert Path(e['file']).is_file() and sha(e['file'])==e['sha256'],e['file']
def write(p,d):
    p=Path(p).resolve();assert p.is_relative_to(T.resolve()),p
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rgb(p,h,size):
    assert sha(p)==h,p
    with Image.open(p) as im:
        im.load();assert im.size==size and im.mode in ('RGB','RGBA'),p
        if im.mode=='RGBA':assert im.getchannel('A').getextrema()==(255,255)
        return im.convert('RGB')
def save_crop(p,im,metadata):
    p=Path(p);assert not p.exists(),'Refuse overwriting input crop'
    p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
    record={**ref(p),'createdAtUtc':now(),'pixels':list(im.size),'operation':'exact original-pixel crop','resized':False,'generatedByAI':False,'finalArt':False,**metadata}
    write(str(p)+'.generation.json',record);return ref(p)
def contract():
    assert sha(CONTRACT)==CONTRACT_SHA,'Frozen c16 DAY contract changed'
    c=read(CONTRACT);assert [e['id'] for e in c['nativeSources']]==IDS
    return c,{e['id']:e for e in c['nativeSources']}

def tone_input():
    p=T/'tone-assembly/output/tone-assembly-manifest.json';assert p.exists(),'Need completed real c16 tone'
    m=read(p);a,b=m['candidate'],m['extendedContext'];verify(a);verify(b)
    core=rgb(a['file'],a['sha256'],(4096,4096));ext=rgb(b['file'],b['sha256'],(4326,4326))
    assert ext.crop((115,115,4211,4211)).tobytes()==core.tobytes(),'True tone core/extended mismatch'
    lock={'manifest':ref(p),'candidate':a,'extendedContext':b,'sourceContract':ref(CONTRACT)};lp=B/'tone-input-lock.json'
    if lp.exists():assert read(lp)==lock,'Immutable tone changed'
    else:write(lp,lock)
    return core,lock

def pin_west(path,digest,extended_path=None):
    path=Path(path).resolve();assert path.is_relative_to(ROOT.resolve()) and sha(path)==digest,'Final c15 path/SHA mismatch'
    ep=Path(extended_path).resolve() if extended_path else path.parent/'extended-context.png'
    assert ep.is_relative_to(ROOT.resolve()),ep
    core=rgb(path,digest,(4096,4096));ext=rgb(ep,sha(ep),(4326,4326))
    assert core.tobytes()==ext.crop((115,115,4211,4211)).tobytes()
    value={'immutableWest':ref(path),'immutableWestExtended':ref(ep),'corePixelIdenticalToExtendedCrop':True,'c15PixelsNeverWritten':True};p=B/'west-input-lock.json'
    if p.exists():assert read(p)==value,'Refuse replacing pinned final c15'
    else:write(p,value)
    return ref(p)

def prepare(name):
    assert name in IDS;out=B/'native'/(name+'.png');assert not out.exists(),'Native already exists'
    rp=B/'prompts'/(name+'.request.json');pp=B/'prompts'/(name+'.prepared.json')
    c,catalog=contract();item=catalog[name];day=item['daySource'];snap=item['geometrySnapshot']['snapshot']
    if rp.exists() or pp.exists():
        assert rp.exists() and pp.exists(),'Incomplete previous preparation'
        prior=read(pp);verify(prior['sourceContractV2']);verify({'file':prior['prompt'],'sha256':prior['promptSha256']})
        for e in prior['references']:verify(e)
        assert read(rp)['referenced_image_paths']==[x['file'] for x in prior['references']]
        return read(rp)
    verify(day);verify(day['record']);verify(snap);assert snap['sha256']==day['sha256']
    rgb(snap['file'],snap['sha256'],(1254,1254));assert sha(STYLE)==STYLE_SHA
    festival,tone=tone_input();rect=item['sourceRectTileAndHaloXYXY'];x,y,x1,y1=rect;assert [x1-x,y1-y]==[1254,1254]
    pair_source=name.startswith('west-only-joint-');west=None
    if pair_source:
        wp=B/'west-input-lock.json';assert wp.exists(),'West repairs require explicit final c15 path/SHA via pin-west'
        west=read(wp)
        for e in (west['immutableWest'],west['immutableWestExtended']):verify(e)
        westim=rgb(west['immutableWest']['file'],west['immutableWest']['sha256'],(4096,4096))
        pair=Image.new('RGB',(8192,4096));pair.paste(westim,(0,0));pair.paste(festival,(4096,0))
        crop=item['sourceRectInPairXYXY'];assert crop==[x+4096,y,x1+4096,y1]
        same_image=pair.crop(crop);context={'coordinateSpace':'c15-c16-pair','derivedFrom':[west['immutableWest'],tone['candidate']],'sourceCropXYXY':crop,'toneManifest':tone['manifest'],'westInputLock':ref(wp)}
    else:
        assert min(rect)>=0 and max(rect)<=4096,'Core source exceeds true coverage'
        same_image=festival.crop(rect);context={'coordinateSpace':'c16-core','derivedFrom':[tone['candidate']],'sourceCropXYXY':rect,'toneManifest':tone['manifest']}
    d=B/'guides'/(name+'-day-source.png');d.parent.mkdir(parents=True,exist_ok=True);assert not d.exists()
    shutil.copyfile(snap['file'],d);assert sha(d)==day['sha256']
    write(str(d)+'.generation.json',{**ref(d),'operation':'byte-identical frozen DAY native repair reference','derivedFrom':[snap],'dayAuthority':day,'sourceGenerationRecord':item['generationRecordSnapshot']['snapshot'],'generatedByAI':False,'resized':False,'finalArt':False})
    same=B/'guides'/(name+'-festival-same-window.png');save_crop(same,same_image,context)
    refs=[{**ref(d,'exact DAY repaired geometry; sole object-placement authority'),'dayAuthority':day,'sourceRectXYXY':rect},ref(same,'real festival pixels at exactly the same world coordinates; material and illumination context'),ref(STYLE,'confirmed primary rounded clean Q art style; no UI/text transfer')]
    previous_meta=None
    prev=PREVIOUS.get(name)
    if prev and (B/'native'/(prev+'.png')).exists():
        prev_path=B/'native'/(prev+'.png');prev_record=read(str(prev_path)+'.generation.json');assert sha(prev_path)==prev_record['sha256']
        pr=catalog[prev]['sourceRectTileAndHaloXYXY'];over=[max(x,pr[0]),max(y,pr[1]),min(x1,pr[2]),min(y1,pr[3])]
        assert over[0]<over[2] and over[1]<over[3] and over!=pr,'Previous must have a real proper overlap'
        local=[over[0]-pr[0],over[1]-pr[1],over[2]-pr[0],over[3]-pr[1]]
        prev_image=rgb(prev_path,prev_record['sha256'],(1254,1254));op=B/'guides'/(name+'-previous-actual-overlap.png')
        previous_meta={'previousNative':ref(prev_path),'previousRecord':ref(str(prev_path)+'.generation.json'),'sourceCropXYXY':local,'overlapTileAndHaloXYXY':over,'positionInsideCurrentXYXY':[over[0]-x,over[1]-y,over[2]-x,over[3]-y],'fullPreviousImageAttached':False}
        save_crop(op,prev_image.crop(local),previous_meta);refs.append(ref(op,'ONLY actual preceding native overlap crop, mapped to specified current coordinates; no pixels outside overlap attached'))
    extra=f" Image4 is only a narrow/cropped real overlap from the preceding converted source, not a new scene: map it only to current-image XYXY {previous_meta['positionInsideCurrentXYXY']}; use it to continue existing materials and illumination across that overlap. Never enlarge, relocate or duplicate any feature from this strip elsewhere." if previous_meta else ''
    if pair_source:
        extra+=' This source crosses the final c15/c16 tile boundary at native x=627. The left 627 columns of Image2 are the approved immutable c15 image. Match the right half to its existing materials and illumination continuously across x=627; preserve all DAY geometry at that boundary. Do not introduce a vertical color border or duplicate/reposition any neighboring object. The final integration uses only the right 627 columns of this output.'
        extra+=' All water panes stay calm with broad subdued paint planes like the actual references: no invented orange or pink highlight cluster, new reflection streak, point light, sunset mark, or off-window lantern reflection. Continue the true c15 left-of-627 water color into the right at the center line, with no vertical color stripe or step. Keep only the restrained original brushwork; no added fine sparkle texture.'
    prompt=f'''Use case: lighting-weather. Original 五行奇谈 fishing-village Lantern Festival map r08_c16, native repair {name}.
Image1 is the exact repaired DAY geometry and sole authority for placement. Convert only its lighting and palette to match Image2, the actual FESTIVAL pixels at identical map coordinates. Image3 is the confirmed rounded, clean, full Daoist Q illustration style.{extra}
Keep Image1's exact crop, camera, scale and every object's footprint, contours, joint geometry, folds, rope strands, waterline, ripple placement and border crossings. Preserve material identity and local hue: honey timber and cream rope stay timber/rope; blue painted wooden boat boards remain matte solid wood with lengthwise grain, never water/caustics/fish scales; blue cloth remains cloth with the same folds. Only actual water receives soft corresponding reflections. Match restrained warm festival light, cool lavender-blue shade and surrounding water tone shown in the identical window. Existing lanterns may glow. Do not introduce lanterns, ropes, props, lights, silhouettes, bright decorative patterns, vegetation or any object from outside the geometry reference. Do not import Image3's UI or scene objects. Do not copy old seams or geometry errors from Image2. No saturated orange flooding, glossy blue boards, scattered sparkling textures or excessive yellow light.
Return one opaque native 1254x1254 image with exactly Image1's composition. No resize, zoom, distortion, border, labels, text, UI, watermark, blur, noise or sharpening. Highest visual completion. Configured gpt-image-2.5-sunburst/max is this batch's target, not an exposed tool selector. Tile-local/halo XYXY={rect}, metadata only, never draw it.'''
    prompt_path=B/'prompts'/(name+'.txt');prompt_path.parent.mkdir(parents=True,exist_ok=True);prompt_path.write_text(prompt,encoding='utf8')
    request={'prompt':prompt,'referenced_image_paths':[e['file'] for e in refs],'transparent_background':False};write(rp,request)
    write(pp,{'name':name,'preparedAtUtc':now(),'references':refs,'dayNativeRepair':day,'dayConsolidatedManifest':c['approvedManifest'],'sourceContractV2':ref(CONTRACT),'sourceRectXYXY':rect,'sourceCoordinateSpace':item['coordinateSpace'],'sourceRectInPairXYXY':item['sourceRectInPairXYXY'],'festivalSource':context,'toneInputLock':ref(B/'tone-input-lock.json'),'westInputLock':ref(B/'west-input-lock.json') if pair_source else None,'previousOverlap':previous_meta,'prompt':str(prompt_path),'promptSha256':sha(prompt_path),'formalAccepted':False})
    return request

def record(name,rawpath):
    assert name in IDS;rawpath=Path(rawpath);im=rgb(rawpath,sha(rawpath),(1254,1254));out=B/'native'/(name+'.png');assert not out.exists()
    pp=B/'prompts'/(name+'.prepared.json');rp=B/'prompts'/(name+'.request.json');prepared=read(pp);request=read(rp)
    verify(prepared['sourceContractV2']);verify(prepared['toneInputLock']);verify({'file':prepared['prompt'],'sha256':prepared['promptSha256']})
    if prepared['westInputLock']:verify(prepared['westInputLock'])
    for e in prepared['references']:verify(e)
    assert request['prompt']==Path(prepared['prompt']).read_text(encoding='utf8') and request['referenced_image_paths']==[e['file'] for e in prepared['references']]
    out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(rawpath,out);assert sha(out)==sha(rawpath)
    value={**ref(out),'generatedAt':now(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(ROOT/'batch-model-check.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**request},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin exposes no model or quality selector and no actual model/quality result metadata.','evidence':{'toolResultSourcePath':str(rawpath),'toolResultSha256':sha(rawpath)},'references':prepared['references'],'geometryMatchedTo':prepared['references'][0],'prompt':prepared['prompt'],'promptSha256':prepared['promptSha256'],'requestFile':str(rp),'requestSha256':sha(rp),'preparedFile':ref(pp),'dayNativeRepair':prepared['dayNativeRepair'],'dayConsolidatedManifest':prepared['dayConsolidatedManifest'],'sourceContractV2':prepared['sourceContractV2'],'sourceRectXYXY':prepared['sourceRectXYXY'],'sourceRectInPairXYXY':prepared['sourceRectInPairXYXY'],'sourceCoordinateSpace':prepared['sourceCoordinateSpace'],'festivalSource':prepared['festivalSource'],'toneInputLock':prepared['toneInputLock'],'westInputLock':prepared['westInputLock'],'previousOverlap':prepared['previousOverlap'],'resizedAfterGeneration':False,'finalArtUpscaled':False,'sourceBytesPreserved':True,'visualQA':'pending actual original-size inspection','formalAccepted':False}
    write(str(out)+'.generation.json',value)
    qa=[]
    for label,box in [('top',[0,0,1254,224]),('bottom',[0,1030,1254,1254]),('left',[0,0,224,1254]),('right',[1030,0,1254,1254])]:
        p=B/'qa'/name/(label+'.png');qa.append({**save_crop(p,im.crop(box),{'derivedFrom':[ref(out)],'sourceCropXYXY':box,'visualReview':'pending'}),'sourceCropXYXY':box})
    write(B/'qa'/name/'manifest.json',{'native':ref(out),'record':ref(str(out)+'.generation.json'),'qa':qa,'pixelScale':1,'visualReview':'pending','formalSeamAccepted':False})
    return ref(out,'original builtin native repair; not yet integrated')

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8')
    if sys.argv[1]=='prepare':result=prepare(sys.argv[2])
    elif sys.argv[1]=='record':result=record(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=='pin-west':result=pin_west(sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else None)
    else:raise SystemExit('prepare ID | record ID RAW_PATH | pin-west CORE_PATH SHA [EXT_PATH]')
    print(json.dumps(result,ensure_ascii=False))
