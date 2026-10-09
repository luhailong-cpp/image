"""Convert pinned DAY consolidated repairs using actual local festival windows.

prepare ID | record ID TOOL_RESULT_PATH. Creates own inputs and provenance only;
never integrates repairs, changes DAY, or publishes a candidate.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, shutil, sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
T = ROOT / 'r08_c15'
B = T / 'repairs/consolidated-sync'
STYLE = Path('D:/work/image/designs/gameplay-ui/04-guild.png')
IDS = ['wood-horizontal-s1','wood-horizontal-s2','wood-horizontal-s3','wood-horizontal-s4',
       'wood-right-w1','wood-right-w2','a-left-cross','b-right-cross','c-left-bottom',
       'd-right-bottom','e-hull-waterline','f-lantern-blueboard',
       'right-upper','right-lower','g-left-insertion','roof',
       'left-insertion','water-left-horizontal','right-halo-finish']

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def meta(p,role): return {'file':str(p),'sha256':sha(p),'role':role}
def write(p,d):
    p=Path(p).resolve(); assert p.is_relative_to(T.resolve()),p
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rgb(p,h,size):
    assert sha(p)==h,p
    with Image.open(p) as im:
        im.load(); assert im.size==size and im.mode in ('RGB','RGBA'),p
        if im.mode=='RGBA': assert im.getchannel('A').getextrema()==(255,255)
        return im.convert('RGB')

def top_two_rows():
    """Real source coverage only: 4326x2278. No missing-pixel placeholder."""
    p=B/'guides/top-two-rows-context.png'; rp=Path(str(p)+'.generation.json')
    if p.exists():
        r=read(rp); return rgb(p,r['sha256'],(4326,2278)),r
    sys.path.insert(0,str(T)); import assemble_c15_shared as a
    m=read(a.DAY_MANIFEST); masks,mask_records=a.load_day_masks(m)
    rows=[]; sources=[]; used=[]
    for row in (1,2):
        arr=[]
        for col in (1,2,3,4):
            n=T/f'native/r{row:02}_c{col:02}.png'; r=read(str(n)+'.generation.json')
            arr.append(np.asarray(rgb(n,r['sha256'],(1254,1254))))
            sources.append(meta(n,'actual existing festival native fragment'))
        acc=arr[0]
        for col in (2,3,4):
            key=f'vertical_r{row:02}_c{col-1:02}_c{col:02}'
            acc,_=a.append_with_mask(acc,arr[col-1],masks[key],key,'vertical'); used.append(key)
        rows.append(acc)
    key='horizontal_r01_r02'
    acc,_=a.append_with_mask(rows[0],rows[1],masks[key],key,'horizontal'); used.append(key)
    assert acc.shape==(2278,4326,3)
    p.parent.mkdir(parents=True,exist_ok=True); Image.fromarray(acc).save(p)
    r={**meta(p,'actual partial festival reference, never complete tile'),'pixels':[4326,2278],
       'operation':'exact DAY masks on first two complete festival native rows; no colour adjustment',
       'derivedFrom':sources,'dayMasks':[x for x in mask_records if x['id'] in used],
       'globalRectXYWH':[57229,28557,4326,2278],'resized':False,'finalArt':False,
       'completePixelCandidate':False,'createdAtUtc':now()}
    write(rp,r); return Image.fromarray(acc),r

def prepare(name):
    assert name in IDS,name
    out=B/'native'/f'{name}.png'; assert not out.exists(),'Never overwrite existing native repair'
    request_path=B/'prompts'/f'{name}.request.json'
    prepared_path=B/'prompts'/f'{name}.prepared.json'
    if request_path.exists() or prepared_path.exists():
        assert request_path.exists() and prepared_path.exists(),'Incomplete existing preparation; inspect instead of overwrite'
        prepared=read(prepared_path)
        assert sha(prepared['prompt'])==prepared['promptSha256'],'Existing prepared prompt changed'
        for item in prepared['references']:assert sha(item['file'])==item['sha256'],'Existing prepared reference changed'
        assert read(request_path)['referenced_image_paths']==[item['file'] for item in prepared['references']]
        return read(request_path)
    contract_path=T/'source-contract-v2/source-contract.json'
    locked=read(contract_path); catalog={item['id']:item for item in locked['nativeSources']}
    item=catalog[name];e=item['daySource'];snapshot=item['geometrySnapshot']['snapshot']
    variant={'manifest':locked['approvedManifest']}
    source=Path(e['file']); geometry=rgb(Path(snapshot['file']),snapshot['sha256'],(1254,1254))
    assert snapshot['sha256']==e['sha256'] and sha(source)==e['sha256']
    assert sha(e['record']['file'])==e['record']['sha256']
    rect=item['sourceRectTileAndHaloXYXY']; x,y,x1,y1=rect; assert [x1-x,y1-y]==[1254,1254]
    day=B/'guides'/f'{name}-day-source.png'; day.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,day); assert sha(day)==e['sha256']
    write(str(day)+'.generation.json',{'file':str(day),'sha256':sha(day),'operation':'original-byte frozen DAY repair geometry',
       'derivedFrom':[e],'sourceGenerationRecordSnapshot':read(e['record']['file']),'finalArt':False})
    fp=T/'tone-assembly/output/r08_c15.png'
    if fp.exists():
        f=read(str(fp)+'.generation.json'); base=rgb(fp,f['sha256'],(4096,4096)); crop=rect
        context=meta(fp,'same actual festival tile window; palette only, DAY repair is geometry authority')
        if name=='right-halo-finish':
            fm=T/'tone-assembly/output/tone-assembly-manifest.json'; manifest=read(fm);ext=manifest['extendedContext']
            base=rgb(Path(ext['file']),ext['sha256'],(4326,4326));crop=e['sourceRectInExtendedXYXY']
            assert crop==[v+115 for v in rect] and crop[2]<=4326 and crop[3]<=4326
            assert base.crop((115,115,4211,4211)).tobytes()==rgb(fp,f['sha256'],(4096,4096)).tobytes(),'Extended/core mismatch'
            context={**meta(Path(ext['file']),'actual 4326 native festival extended context; includes unchanged true 115px right halo'),'manifest':meta(fm,'festival tone manifest'),'sourceRectInExtendedXYXY':crop,'corePixelIdentical':True}
        else:assert min(crop)>=0 and crop[2]<=4096 and crop[3]<=4096,'Core crop exceeded coverage'
    else:
        assert name.startswith('wood-horizontal-'),'Only top wood repairs have complete source coverage before whole tone assembly'
        base,context=top_two_rows(); crop=[x+115,y+115,x1+115,y1+115]
        assert crop[2]<=base.width and crop[3]<=base.height,'Missing real festival source pixels'
    same=B/'guides'/f'{name}-festival-same-window.png'; base.crop(crop).save(same)
    write(str(same)+'.generation.json',{'file':str(same),'sha256':sha(same),'operation':'exact native unscaled same-window festival crop',
       'derivedFrom':[context],'sourceCropXYXY':crop,'finalArt':False,'resized':False})
    refs=[{**meta(day,'exact DAY repaired geometry'),'dayAuthorityFile':str(source),'dayAuthoritySha256':e['sha256'],
           'dayGenerationRecord':e['record'],'sourceRectXYXY':rect},
          meta(same,'same-window actual festival material and light reference; old seams may need joining'),
          meta(STYLE,'confirmed primary Q art rendering; no UI or text transfer')]
    prompt=f'''Use case: lighting-weather. Original 五行奇谈 fishing-village Lantern Festival map r08_c15, repair {name}.
Image1 is the exact repaired DAY geometry. Convert only its lighting and palette to match Image2, the actual FESTIVAL pixels at the identical map coordinates. Image3 is the confirmed primary rounded, clean, full Daoist Q art style.
Preserve Image1's exact crop, camera, scale and every object's footprint, contour, joint, fold, rope strand, cast-shadow silhouette, water ripple and edge crossing. Retain exact original material identity and hue. Blue painted wooden boat boards remain solid matte wood with lengthwise grain, never water, caustics, fish scales or wave-like highlights. Blue cloth remains cloth with the same folds and restrained soft light. Only actual water receives matching rippled reflections. Honey timber, cream rope, soft lavender shade and restrained warm festival light must match the actual same-window scene. Join any guide colour steps smoothly. Existing lanterns may glow; introduce no new lantern, prop, reflection pattern, building or vegetation. Do not copy old seams or change geometry from Image2. Avoid saturated orange flooding, added gloss, sparkling textures or excessive yellow light.
Return one opaque native 1254x1254 image, exactly same crop and layout as Image1, no resizing, border, labels, text, UI, watermark, blur, noise or sharpening. Highest visual completion. Configured gpt-image-2.5-sunburst/max is the batch target, not an exposed tool selector. Tile-local XYXY={rect}; these are metadata and must not appear in the art.'''
    pp=B/'prompts'/f'{name}.txt'; pp.parent.mkdir(parents=True,exist_ok=True); pp.write_text(prompt,encoding='utf-8')
    request={'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}
    write(B/'prompts'/f'{name}.request.json',request)
    write(B/'prompts'/f'{name}.prepared.json',{'name':name,'references':refs,'dayConsolidatedManifest':variant['manifest'],
       'dayNativeRepair':e,'festivalSource':context,'sourceRectXYXY':rect,'prompt':str(pp),'promptSha256':sha(pp),
       'preparedAtUtc':now(),'formalAccepted':False,'sourceContractV2':meta(contract_path,'explicit approved-chain contract'),'sourceCoordinateSpace':item['coordinateSpace'],'sourceRectInExtendedXYXY':e.get('sourceRectInExtendedXYXY')})
    return request

def record(name,raw):
    assert name in IDS,name
    raw=Path(raw); im=rgb(raw,sha(raw),(1254,1254)); p=B/'native'/f'{name}.png'; assert not p.exists(),p
    prepared=read(B/'prompts'/f'{name}.prepared.json'); requestp=B/'prompts'/f'{name}.request.json'; request=read(requestp)
    for r in prepared['references']: assert sha(r['file'])==r['sha256'],r['file']
    assert sha(prepared['prompt'])==prepared['promptSha256']
    p.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(raw,p)
    write(str(p)+'.generation.json',{'file':str(p),'sha256':sha(p),'width':1254,'height':1254,'generatedAt':now(),
       'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(ROOT/'batch-model-check.json')['configSnapshot'],
       'submittedParameters':{'model':None,'quality':None,**request},'actualModel':None,'actualQuality':None,
       'unverifiedReason':'Host-managed builtin exposes no model or quality selector or result metadata.',
       'evidence':{'toolResultSourcePath':str(raw),'toolResultSha256':sha(raw),'sha256':sha(raw)},
       'references':prepared['references'],'geometryMatchedTo':prepared['references'][0],
       'prompt':prepared['prompt'],'promptSha256':prepared['promptSha256'],'requestFile':str(requestp),'requestSha256':sha(requestp),
       'dayNativeRepair':prepared['dayNativeRepair'],'dayConsolidatedManifest':prepared['dayConsolidatedManifest'],
       'sourceRectXYXY':prepared['sourceRectXYXY'],'festivalSource':prepared['festivalSource'],
       'resizedAfterGeneration':False,'finalArtUpscaled':False,'sourceBytesPreserved':True,'visualQA':'pending','formalAccepted':False,'sourceContractV2':prepared.get('sourceContractV2'),'sourceCoordinateSpace':prepared.get('sourceCoordinateSpace','core'),'sourceRectInExtendedXYXY':prepared.get('sourceRectInExtendedXYXY')})
    return meta(p,'original builtin festival repair native, not integrated')

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1]=='prepare': result=prepare(sys.argv[2])
    elif sys.argv[1]=='record': result=record(sys.argv[2],sys.argv[3])
    else: raise SystemExit('prepare ID | record ID RAW_PATH')
    print(json.dumps(result,ensure_ascii=False))
