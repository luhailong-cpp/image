from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, shutil
from PIL import Image

REPAIR=Path(__file__).resolve().parent.parent
TILE=REPAIR.parent.parent
ROOT=TILE.parent
PROJECT=Path('D:/work/image')
DAY=ROOT.parent/'donghai_day/r08_c11/repairs/west-common-edge'
WEST=PROJECT/'qdao_city_tiles_4k_20260916/builtin_q64_production/donghai_lantern/r08_c08_c09_c10_joint/output_v2/r08_c10.png'
EAST=TILE/'tone-assembly/output/r08_c11.png'
STYLE=PROJECT/'designs/gameplay-ui/04-guild.png'
TONE=TILE/'guides/neighbor-tone-native.png'
STARTS=[0,1024,2048,2842]

def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def item(p,role):return {'file':str(p),'sha256':sha(p),'role':role}

def prepare(i):
 name=f's{i}';start=STARTS[i-1]
 for d in ['native','guides','prompts','qa']:(REPAIR/d).mkdir(parents=True,exist_ok=True)
 day=DAY/f'{name}.png';record=read(str(day)+'.generation.json');assert sha(day)==record['sha256']
 geometry=Image.open(day).convert('RGB');assert geometry.size==(1254,1254)
 guide=geometry.copy();dependencies=[item(day,'exact repaired day geometry')];overlap=0
 if i>1:
  prior=REPAIR/'native'/f's{i-1}.png';assert prior.exists();overlap=STARTS[i-2]+1254-start
  guide.paste(Image.open(prior).crop((0,1254-overlap,1254,1254)),(0,0))
  dependencies.append({**item(prior,'previous festival native overlap'),'sourceCropXYXY':[0,1254-overlap,1254,1254],'pasteXY':[0,0]})
 guidepath=REPAIR/'guides'/f'{name}-edit.png';guide.save(guidepath)
 write(str(guidepath)+'.generation.json',{'file':str(guidepath),'sha256':sha(guidepath),'operation':'exact day native copy with previous festival top overlap; no scaling','globalRectXYWH':[40333,28672+start,1254,1254],'derivedFrom':dependencies,'previousOverlapPixels':overlap,'resampled':False,'finalArt':False})
 tone=Image.new('RGB',(1254,1254));tone.paste(Image.open(WEST).crop((3469,start,4096,start+1254)),(0,0));tone.paste(Image.open(EAST).crop((0,start,627,start+1254)),(627,0))
 tonepath=REPAIR/'guides'/f'{name}-festival-same-window.png';tone.save(tonepath)
 write(str(tonepath)+'.generation.json',{'file':str(tonepath),'sha256':sha(tonepath),'operation':'unscaled same-coordinate festival tone-context joint crop; not geometry authority','globalRectXYWH':[40333,28672+start,1254,1254],'derivedFrom':[{**item(WEST,'pinned existing festival c10 palette'),'sourceCropXYXY':[3469,start,4096,start+1254],'pasteXY':[0,0]},{**item(EAST,'current tonal festival c11 palette'),'sourceCropXYXY':[0,start,627,start+1254],'pasteXY':[627,0]}],'resampled':False,'finalArt':False})
 refs=[item(day,'PRIMARY GEOMETRY: repaired native day window, preserve every contour and shadow silhouette'),item(guidepath,'edit target, identical day geometry with exact previous festival top overlap'),item(STYLE,'PRIMARY user-confirmed art style; ignore UI and text'),item(TONE,'festival palette and rendering sample only; no geometry transfer'),item(tonepath,'same-coordinate existing festival appearance/tone context only; its unrepaired join must NOT be copied')]
 prompt=f'''Use case: lighting-weather.
Asset: 五行奇谈 fishing-village Lantern Festival map; west shared c10/c11 repaired native window {name}, global XYWH [40333,{28672+start},1254,1254].
Image 1 is PRIMARY exact repaired DAY geometry. Image 2 is the edit target at the IDENTICAL crop; its top {overlap} pixels, if any, are the previous finished FESTIVAL repair overlap. Image 3 is PRIMARY confirmed hand-painted Daoist Q-style. Image 4 is a festival material/palette sample. Image 5 is SAME-COORDINATE festival tone context only: it still contains the old faulty geometric join, so NEVER transfer its contours, stone joints or shadow shapes.
Convert only the daylight appearance of image 2 into matching bright, clean Lantern Festival appearance. Precisely preserve all repaired geometry of image 1: every leaf outline, branch, post, red cloth, stone contour, paving joint, basket rim/weave, object scale and occlusion. Most importantly keep the repaired stone/paving lines and every cast-shadow SILHOUETTE exactly; recolor the existing shadow interiors without adding, moving or reshaping any shadow. Maintain all four crop boundaries, camera and field of view. Keep prior festival overlap visually consistent without inventing structure. The original tile boundary at image x627 is now repaired; do not recreate a stripe, chopped leaf or broken pavement there.
Rendering: rounded full clean hand-painted Daoist Q-style as image 3; warm cream paving, balanced green foliage, restrained honey/peach reflected light and soft lavender shadow tones. Match images 4 and 5 gently while retaining image 1 structure. Preserve blue roofs and red fabric. No new lanterns, props, characters, sparkle, glare, orange wash, fluorescent outlines, broad new light patches or new shadow shapes. No UI, text, logos, grid, border, watermark, blur, sharpening or noise.
One opaque 1254x1254 image, exact existing crop, crisp native detail. Highest available visual completion. Config target gpt-image-2.5-sunburst/max is a target only; no model or quality selector is implied by this prose.'''
 pp=REPAIR/'prompts'/f'{name}.txt';pp.write_text(prompt,encoding='utf-8')
 write(REPAIR/'prompts'/f'{name}.references.json',refs)
 req={'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False}
 write(REPAIR/'prompts'/f'{name}.request.json',req);print(json.dumps(req,ensure_ascii=False))

def record(i,src):
 name=f's{i}';src=Path(src);dst=REPAIR/'native'/f'{name}.png';assert not dst.exists()
 im=Image.open(src);im.load();assert im.size==(1254,1254);shutil.copyfile(src,dst)
 req=read(REPAIR/'prompts'/f'{name}.request.json');refs=read(REPAIR/'prompts'/f'{name}.references.json');assert all(sha(x['file'])==x['sha256'] for x in refs)
 receipt={'tool':'image_gen.imagegen','observedAtUtc':now(),'toolResultSourcePath':str(src),'toolResultSha256':sha(src),'actualPixels':list(im.size),'actualModel':None,'actualQuality':None}
 rp=REPAIR/'prompts'/f'{name}.receipt.json';write(rp,receipt)
 write(str(dst)+'.generation.json',{'file':str(dst),'sha256':sha(dst),'generatedAt':now(),'timestampMeaning':'locally observed completed tool result','width':im.width,'height':im.height,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(PROJECT/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,**req},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed built-in tool exposes neither model/quality selectors nor actual model/quality return evidence.','evidence':{**receipt,'receiptFile':str(rp)},'prompt':str(REPAIR/'prompts'/f'{name}.txt'),'references':refs,'globalRectXYWH':[40333,28672+STARTS[i-1],1254,1254],'resizedAfterGeneration':False,'finalArtUpscaled':False,'geometryMatchedTo':refs[0],'formalAccepted':False,'visualQA':'pending; native repair fragment only'})
 print(json.dumps({'file':str(dst),'sha256':sha(dst),'size':im.size}))

if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(int(sys.argv[2]))
 elif sys.argv[1]=='record':record(int(sys.argv[2]),sys.argv[3])
