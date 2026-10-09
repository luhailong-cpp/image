from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent;T=B.parent.parent;OWN=T.parent
BASE=T/'repairs/approved-sync/output/r08_c16.png';WEST=OWN/'r08_c15/west-common-edge-v3/output/r08_c15.png'
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ref(p,role=None):return {'file':str(p),'sha256':sha(p),**({'role':role} if role else {})}
def now():return datetime.now(timezone.utc).isoformat()
def prepare(i):
    assert sha(BASE)=='7d821e83179cae126dd4e0f1be7f6b83f6a762bfe7b0f0caa4bfa3ec8de0bb22'
    assert sha(WEST)=='7c18bf09e962b458ee285c04067655d6198c426d2bb53cccbe13bc58f24c8a4f'
    assert sha(STYLE)=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
    y=[0,1024,2048,2842][i-1];name=f's{i}'
    d=B/'guides';d.mkdir(exist_ok=True)
    p=d/(name+'-actual-pair.png')
    pair=Image.new('RGB',(8192,4096));pair.paste(Image.open(WEST).convert('RGB'),(0,0));pair.paste(Image.open(BASE).convert('RGB'),(4096,0))
    rect=[3469,y,4723,y+1254];pair.crop(rect).save(p)
    write(Path(str(p)+'.generation.json'),{**ref(p),'operation':'exact actual immutable c15 plus fixed c16 pair crop','sourcePairRectXYXY':rect,'derivedFrom':[ref(WEST),ref(BASE)],'resized':False})
    day=T/'repairs/consolidated-sync/guides'/f'west-only-joint-s{i}-day-source.png'
    refs=[ref(p,'PRIMARY EDIT TARGET: actual current final pair; preserve its exact geometry and color outside narrow repair'),ref(day,'DAY geometry reference only, not palette or lighting'),ref(STYLE,'confirmed clean rounded Q painting completion/style, no objects or UI to import')]
    detail={
    1:'Repair the narrow straight tint seam through quiet top water, crossing golden crossbeam and blue folded cloth. Match the existing left-of-center water, wood and blue fabric color continuously immediately to the right, then blend naturally back before x=847. Preserve diagonal geometry and existing broad cloth strokes; no new fine texture.',
    2:'Repair the straight tint seam where the crossing diagonal golden rails, cabin wood and shadows pass through x=627. Preserve every slant, board edge and post. Continue the same wood grain and light across the seam without a vertical or horizontal strip.',
    3:'Repair the straight tint seam in the timber rail, matte blue exterior wooden panel and hull crossing x=627. Also remove the small jagged orange timber paint island at image XYXY [682,72,892,242], matching uninterrupted adjacent timber grain and shade. This extra island is color only, no structure. Keep the existing lantern, hanging rope and board borders fixed. Ignore and preserve all unrelated patch artifacts farther right.',
    4:'Repair the straight tint seam in the existing hull timber and blue panel crossing x=627. In the bottom water, the pre-existing gold/purple reflections from the left currently terminate at the center. Continue only those same reflected paint marks a short natural distance into x=627..800, letting them taper organically into the existing blue water before x=847. Do not add a new reflection cluster or any new light source. Preserve lantern, tassel, waterline and all hull contours exactly.'
    }[i]
    prompt=f'''Use case: precise-object-edit. One production micro-repair to an already approved Q illustrated Lantern Festival map.
Image1 is the PRIMARY EDIT TARGET: reproduce this exact 1254x1254 crop, camera, geometry and existing color palette. Image2 is geometry-only DAY evidence at the same world coordinates; NEVER use its daylight colors, change the existing lighting, or move anything. Image3 is only the confirmed style.
Only repair the narrow color/brushwork discontinuity at image x=627. The left 627 columns belong to an immutable finished neighbor: copy them faithfully; they will be discarded and replaced with their exact original pixels. The right side x>=847 is also fixed. Correct only x=627..846 so it meets the unchanged actual LEFT edge at x=627 naturally and returns smoothly to unchanged actual RIGHT color before x=847. No vertical or horizontal tint bands.
{detail}
Every plank outline, rope strand, fold silhouette, lantern position, cast-shadow boundary and waterline must stay at exactly the same pixel location. This is solely palette/brushstroke continuity. Do not redesign, relight, recolor the whole image, invent props, add decorations, introduce pink stripes, increase saturation or copy objects from the style image. Keep all existing matte wood grain and broad calm water planes sharp and natural; do not blur/smear. No noise, speckled mask edges or granular artifacts. Return one opaque native 1254x1254 PNG with identical composition, no crop, zoom, resize, lettering or watermark. Config target gpt-image-2.5-sunburst/max is host-managed and not an exposed selector.'''
    if i==3:prompt+='\nThe one additional permitted change is the small orange island explicitly described above; its surrounding board edges and everything outside that rectangle remain unchanged.'
    pp=B/'prompts'/(name+'.txt');pp.parent.mkdir(exist_ok=True);pp.write_text(prompt,encoding='utf8')
    rq={'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}
    write(B/'prompts'/(name+'.request.json'),rq)
    write(B/'prompts'/(name+'.prepared.json'),{'name':name,'references':refs,'base':ref(BASE),'immutableWest':ref(WEST),'rectTileXYXY':[-627,y,627,y+1254],'sourcePairRectXYXY':rect,'prompt':ref(pp),'request':ref(B/'prompts'/(name+'.request.json')),'allowedTileScope':'x<220 full height plus [0,2050,350,2350] wood patch; immutable c15 unchanged'})
    return rq
def record(i,raw):
    name=f's{i}';raw=Path(raw);p=B/'native'/(name+'.png');assert not p.exists()
    with Image.open(raw) as im:assert im.size==(1254,1254);im.load();assert im.mode in ('RGB','RGBA');assert im.mode=='RGB' or im.getchannel('A').getextrema()==(255,255)
    pre=read(B/'prompts'/(name+'.prepared.json'));rq=read(B/'prompts'/(name+'.request.json'))
    for e in pre['references']+[pre['base'],pre['immutableWest'],pre['prompt'],pre['request']]:assert sha(e['file'])==e['sha256']
    p.parent.mkdir(exist_ok=True);shutil.copyfile(raw,p)
    rec={**ref(p),'generatedAt':now(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(OWN/'batch-model-check.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**rq},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; tool has no model/quality selectors or disclosed returned model/quality.','evidence':{'toolResultSourcePath':str(raw),'toolResultSha256':sha(raw)},'references':pre['references'],'prompt':pre['prompt'],'request':pre['request'],'base':pre['base'],'immutableWest':pre['immutableWest'],'rectTileXYXY':pre['rectTileXYXY'],'resizedAfterGeneration':False,'sourceBytesPreserved':True,'visualReview':'pending actual native/pair returns'}
    write(Path(str(p)+'.generation.json'),rec);return ref(p)
if __name__=='__main__':
    if sys.argv[1]=='prepare':o=prepare(int(sys.argv[2]))
    elif sys.argv[1]=='record':o=record(int(sys.argv[2]),sys.argv[3])
    print(json.dumps(o,ensure_ascii=False))

