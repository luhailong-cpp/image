"""Prepare/record four native c13-c14 festival joint appearance conversions.

Commands: prepare 1..4 | record 1..4 ACTUAL_RAW_PATH. No integration/state writes.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import sys
from PIL import Image

ROOT=Path(__file__).resolve().parent
PROJECT=Path('D:/work/image')
REPAIR=ROOT/'r08_c14/repairs/west-common-edge'
DAY_MANIFEST=ROOT.parent/'donghai_day/tiles/west-integration-r08_c14-manifest.json'
DAY_SHA=(json.loads((REPAIR/'source-contract.json').read_text(encoding='utf-8-sig'))['dayManifest']['sha256'] if (REPAIR/'source-contract.json').exists() else hashlib.sha256(DAY_MANIFEST.read_bytes()).hexdigest())
WEST=ROOT/'r08_c13/completed-candidate-v2/output/r08_c13.png'
WEST_SHA='bd2ccf25c06f3e22797cd153c26df45247ee9d099adb8d191a72d282cb78b1c6'
EAST=ROOT/'r08_c14/tone-assembly/output/r08_c14.png'
EAST_SHA=hashlib.sha256(EAST.read_bytes()).hexdigest() if EAST.exists() else None
STYLE=PROJECT/'designs/gameplay-ui/04-guild.png'
TONE=ROOT/'r08_c12/guides/neighbor-tone-native.png'
STARTS=[0,1024,2048,2842]


def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def item(path,role):return {'file':str(path),'sha256':sha(path),'role':role}
def check(path,digest):assert sha(path)==digest,f'SHA changed: {path}'
def write(path,data):
    path=Path(path).resolve();assert path.is_relative_to(REPAIR.resolve()),path
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def image(path,size):
    im=Image.open(path);im.load();assert im.format=='PNG' and im.size==size,(path,im.size)
    assert im.mode in ('RGB','RGBA'),path
    if im.mode=='RGBA':assert im.getchannel('A').getextrema()==(255,255),path
    return im.convert('RGB')


def contract():
    check(DAY_MANIFEST,DAY_SHA);day=read(DAY_MANIFEST)
    preflight=read(REPAIR/'day-source-preflight.json')
    assert preflight['dayManifest']['sha256']==DAY_SHA,'DAY manifest changed after preflight'
    assert day['tile']=='r08_c14' and day['parameters']['patchYStarts']==STARTS
    assert day['parameters']['stripPairRectXYXY']==[3469,0,4723,4096]
    assert len(day['nativeRepairSources'])==4 and len(day['seams'])==5
    for source in day['nativeRepairSources']:
        check(source['file'],source['sha256']);check(source['recordFile'],source['recordSha256'])
        record=read(source['recordFile']);assert record['sha256']==source['sha256']
        image(source['file'],(1254,1254))
    for seam in day['seams']:
        for key in ('maskPng','maskNpz'):check(seam[key]['file'],seam[key]['sha256'])
    check(WEST,WEST_SHA);check(EAST,EAST_SHA)
    image(WEST,(4096,4096));image(EAST,(4096,4096))
    evidence={'createdAtUtc':now(),'dayManifest':item(DAY_MANIFEST,'pinned c13-c14 joint geometry and exact future ownership masks'),
        'nativeDaySources':day['nativeRepairSources'],'daySeams':day['seams'],
        'festivalBaselines':[item(WEST,'pinned festival c13 completed-candidate-v2; all current repairs preserved outside eastern 627 pixels'),item(EAST,'pinned festival c14 tone candidate')],
        'globalPairOriginXY':[49152,28672],'repairPairRectXYXY':[3469,0,4723,4096],
        'nativePixels':[1254,1254],'patchYStarts':STARTS,'longitudinalOverlaps':[230,230,460],
        'formalAccepted':False,'integrationPerformed':False,'globalStateModified':False}
    path=REPAIR/'source-contract.json'
    if not path.exists():write(path,evidence)
    else:
        existing=read(path)
        assert existing['dayManifest']['sha256']==DAY_SHA
        assert [v['sha256'] for v in existing['festivalBaselines']]==[WEST_SHA,EAST_SHA]
    return day


def prepare(i):
    assert 1<=i<=4
    name=f's{i}';start=STARTS[i-1]
    assert not (REPAIR/'native'/f'{name}.png').exists(),'Never overwrite existing native'
    day=contract();source=day['nativeRepairSources'][i-1];assert source['id']==name
    for folder in ('native','guides','prompts','qa'):(REPAIR/folder).mkdir(parents=True,exist_ok=True)
    geometry=image(source['file'],(1254,1254));guide=geometry.copy();overlap=0
    dependencies=[{**item(source['file'],'exact repaired DAY geometry'),'generationRecord':source['recordFile'],'generationRecordSha256':source['recordSha256']}]
    if i>1:
        prior=REPAIR/'native'/f's{i-1}.png';rec=read(str(prior)+'.generation.json');check(prior,rec['sha256'])
        overlap=STARTS[i-2]+1254-start
        guide.paste(image(prior,(1254,1254)).crop((0,1254-overlap,1254,1254)),(0,0))
        dependencies.append({**item(prior,'exact previous festival native at shared world coordinates'),'sourceCropXYXY':[0,1254-overlap,1254,1254],'pasteXY':[0,0]})
    target=REPAIR/'guides'/f'{name}-edit.png';guide.save(target)
    write(str(target)+'.generation.json',{'file':str(target),'sha256':sha(target),'operation':'same day native geometry plus actual previous festival native top overlap','derivedFrom':dependencies,'globalRectXYWH':[52621,28672+start,1254,1254],'previousOverlapPixels':overlap,'resized':False,'finalArt':False})
    tone=Image.new('RGB',(1254,1254))
    tone.paste(image(WEST,(4096,4096)).crop((3469,start,4096,start+1254)),(0,0))
    tone.paste(image(EAST,(4096,4096)).crop((0,start,627,start+1254)),(627,0))
    tonepath=REPAIR/'guides'/f'{name}-festival-same-window.png';tone.save(tonepath)
    write(str(tonepath)+'.generation.json',{'file':str(tonepath),'sha256':sha(tonepath),'operation':'exact unscaled current festival same-coordinate joint context; geometry is superseded by repaired day','globalRectXYWH':[52621,28672+start,1254,1254],
        'derivedFrom':[{**item(WEST,'festival c13'),'sourceCropXYXY':[3469,start,4096,start+1254],'pasteXY':[0,0]},{**item(EAST,'festival c14'),'sourceCropXYXY':[0,start,627,start+1254],'pasteXY':[627,0]}],'resized':False,'finalArt':False})
    refs=[dependencies[0],item(target,'EDIT target: exact repaired day geometry plus prior festival overlap'),
          item(STYLE,'PRIMARY confirmed Daoist Q rendering/material/finish style; ignore all UI, text and layout'),
          item(TONE,'festival material/light sample only, never geometry or roof-color authority'),
          item(tonepath,'same-coordinate festival tone context only; never transfer old faulty joint geometry')]
    prompt=f'''Use case: lighting-weather.
Asset: 五行奇谈 fishing-village Lantern Festival map, repaired c13/c14 west common-edge native {name}, global XYWH [52621,{28672+start},1254,1254].
Image1 is the PRIMARY exact repaired DAY geometry and material-hue authority. Image2 is the edit target at the same crop; its top {overlap}px, when present, are genuine previous FESTIVAL repair pixels. Image3 is the PRIMARY confirmed rounded hand-painted Daoist Q style. Image4 is only a festival light/material sample. Image5 is SAME-COORDINATE festival tone context: its old faulty common-edge contours have been superseded and MUST NOT be copied.
Convert only image2 daylight appearance to the matching clean bright festival appearance. Precisely retain image1 repaired geometry: every roof tile, roof ridge, wall edge, wooden joint, paving joint, leaf outline, branch, post, object silhouette, occlusion and all true cast-shadow silhouettes. Keep all dimensions, scale, framing and four crop boundaries unchanged. The former tile boundary at x627 is repaired; do not recreate a join stripe or broken object there. Match the actual previous festival overlap without inventing shapes.
STRICT material-hue preservation: every roof retains its ORIGINAL hue from image1. Orange-red terracotta stays orange-red; blue or slate tiles stay their own blue or slate shade. Never convert an orange-red roof to blue, even if image4 contains blue roofing. Preserve cream plaster, honey timber, green foliage and all other original material identities. Only add the same restrained warm festival illumination as the same-window image5, with soft peach highlights and lavender shaded planes; do not intensify yellow/orange brightness beyond the neighboring context. Preserve existing true leaf dapples and shadow silhouettes. Rounded full clean finish as image3. No new lanterns, props, characters, vegetation, glitter, glow outlines, broad light blobs, new shadow shapes, blur, sharpening, noise, text, UI, watermark or border.
Water material stays clean clear blue: match the actual festival water body and restrained existing peach/gold reflections of image5, while retaining the exact wave shapes and piling silhouettes of image1. Do not copy its center seam, invent extra reflections or turn the whole water amber, purple, milky, metallic or neon; no sparks or floating decorations.
Return one opaque 1254x1254 image at the exact native crop with crisp native detail, no enlargement. Highest available completion. Config target gpt-image-2.5-sunburst/max is a target only; no exposed model/quality selector is claimed.'''
    pp=REPAIR/'prompts'/f'{name}.txt';pp.write_text(prompt,encoding='utf-8')
    request={'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}
    write(REPAIR/'prompts'/f'{name}.references.json',refs);write(REPAIR/'prompts'/f'{name}.request.json',request)
    return request


def record(i,raw):
    assert 1<=i<=4
    name=f's{i}';raw=Path(raw);dst=REPAIR/'native'/f'{name}.png';assert not dst.exists()
    im=image(raw,(1254,1254));request_path=REPAIR/'prompts'/f'{name}.request.json';request=read(request_path)
    refs=read(REPAIR/'prompts'/f'{name}.references.json')
    for ref in refs:check(ref['file'],ref['sha256'])
    assert request['referenced_image_paths']==[r['file'] for r in refs]
    shutil.copyfile(raw,dst)
    receipt={'tool':'image_gen.imagegen','observedAtUtc':now(),'toolResultSourcePath':str(raw),'toolResultSha256':sha(raw),'actualPixels':[1254,1254],'actualModel':None,'actualQuality':None}
    rp=REPAIR/'prompts'/f'{name}.receipt.json';write(rp,receipt)
    prompt_path=REPAIR/'prompts'/f'{name}.txt'
    write(str(dst)+'.generation.json',{'file':str(dst),'sha256':sha(dst),'generatedAt':now(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(ROOT/'batch-model-check.json')['configSnapshot'],
        'submittedParameters':{'model':None,'quality':None,**request},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed builtin exposes no model/quality selectors or actual return metadata.',
        'evidence':{**receipt,'receiptFile':str(rp)},'prompt':str(prompt_path),'promptSha256':sha(prompt_path),'requestFile':str(request_path),'requestSha256':sha(request_path),'references':refs,'geometryMatchedTo':refs[0],
        'globalRectXYWH':[52621,28672+STARTS[i-1],1254,1254],'pairRectXYXY':[3469,STARTS[i-1],4723,STARTS[i-1]+1254],
        'resizedAfterGeneration':False,'finalArtUpscaled':False,'sourceBytesPreserved':True,'formalAccepted':False,'visualQA':'pending native inspection; not integrated'})
    return {'file':str(dst),'sha256':sha(dst),'pixels':list(im.size)}


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1]=='prepare':result=prepare(int(sys.argv[2]))
    elif sys.argv[1]=='record':result=record(int(sys.argv[2]),sys.argv[3])
    else:raise SystemExit('Unknown command')
    print(json.dumps(result,ensure_ascii=False))

