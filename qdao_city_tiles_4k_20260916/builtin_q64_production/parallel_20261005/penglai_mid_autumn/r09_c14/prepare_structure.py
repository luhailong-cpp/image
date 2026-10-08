from pathlib import Path
from PIL import Image
import sys,json,hashlib,datetime,shutil

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
REPO=Path('D:/work/image')
DAY=BASE.parent/'penglai_day/r09_c14/references/structure.png'
WEST=BASE/'output/r09_c13/r09_c13.png'
STYLE=REPO/'designs/gameplay-ui/04-guild.png'
TILE='r09_c14'

def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def source(p):
 p=Path(p);return {'file':p.as_posix(),'sha256':sha(p),'generationRecord':str(p)+'.generation.json' if Path(str(p)+'.generation.json').exists() else None}
def derived(dest,sources,operation):
 im=Image.open(dest)
 write(str(dest)+'.generation.json',{'file':dest.as_posix(),'sha256':sha(dest),'generatedAt':stamp(),'width':im.width,'height':im.height,'format':'PNG','derivedFrom':[source(p) for p in sources],'operation':operation,'productionPixels':False,'role':'planning_or_context_only','formalAccepted':False})

def init():
 for name in ['references','prompts','evidence','guides','qa']:(ROOT/name).mkdir(parents=True,exist_ok=True)
 assert sha(DAY)=='ac5429e91e9ae2542555e1e10fe03f63df8cd13d8fcd2a663d96446a4d530e2e'
 assert sha(WEST)=='9de5b3325de9ba147072aab2b5e7effbbd10a033894b928711e572b895429e4d'
 day=Image.open(DAY).convert('RGB');west=Image.open(WEST).convert('RGB')
 assert day.size==(1254,1254) and west.size==(4096,4096)
 for width in [115,320]:
  dest=ROOT/'references'/f'west-native{width}.png';west.crop((4096-width,0,4096,4096)).save(dest)
  derived(dest,[WEST],{'method':'native crop without resampling','sourceBoxLTRB':[4096-width,0,4096,4096]})
 dest=ROOT/'references/west-preview.png';west.resize((1254,1254),Image.Resampling.LANCZOS).save(dest)
 derived(dest,[WEST],{'method':'downscale to1254 for whole-neighbor appearance context only'})
 # Day reference already covers global [GX-115,GY-115,GX+4211,GY+4211].
 # Replace ONLY the western 115px context in this same framing, downsampled.
 guide=day.copy();guide.paste(west.crop((3981,0,4096,4096)).resize((33,1188),Image.Resampling.LANCZOS),(0,33))
 dest=ROOT/'references/day-geometry-with-night-west.png';guide.save(dest)
 derived(dest,[DAY,WEST],{'method':'unchanged shared-day1254 geometry with current night native west115 reduced to33x1188 at0,33; planning only','sameFrameGlobalXYWH':[53133,32653,4326,4326],'nightStripSourceBoxLTRB':[3981,0,4096,4096],'nightStripTargetBoxLTRB':[0,33,33,1221],'productionUseForbidden':True})
 prompt='''Use case: lighting-weather. Asset: the same-frame structural planning art for tile r09_c14 in the original 五行奇谈 Taoist Q fantasy town, Mid-Autumn night appearance. Image 1 is the exact edit target, shared daytime geometry with a narrow real NIGHT west-neighbor anchor at x0..32,y33..1220. Image 2 is the unaltered same-frame DAY structural reference: keep its geometry exactly. Image 3 is the actual western NIGHT neighboring tile, appearance/context only, do not render its whole scene. Image 4 is the approved PRIMARY PAINTING STYLE; match rounded full clean hand-painted materials, never copy UI. Image 5 is the real western native right320px strip, edge-position/material evidence only.
Change ONLY the daylight to clean luminous Mid-Autumn night: violet-blue moonlight in pale stone, jade/teal green foliage, warm amber from the existing upper-left cropped lantern. Keep it bright, legible, clean and warm enough for the approved Taoist Q style. Preserve every scene object, exact camera, crop, perspective, footprint, scale and count. Curving ivory garden wall and left-side staircase retain exact silhouettes and tread directions; rounded pale boulders, tree, flowering foliage, wooden produce stall, all vegetables, baskets, posts, round Taoist pictorial sign, small foreground cropped timber crate and lower-right post stay in exactly the same positions as Image 2. Do not add lanterns, festival props, moon discs, buildings, paving grout branches, text or characters.
The narrow western anchor from Image 1 is already final night art and is authoritative. Preserve its cropped lantern edge, foliage endpoints, rail profile and individual stair treads precisely, naturally continue their tangent directions into the same target scene. Remove no objects and move no wall/plant/stair/stall merely to relight it. The artificial vertical paste border x33 is not a scene edge: give the new light/material a coherent transition without drawing a line there. Do not expand or zoom the frame. The existing 1254 square frame already includes its outer planning halo; return exactly this square view. No border, labels, UI, watermark, photorealism, plastic glare, grain or gritty over-detail. Output an opaque square image.'''
 refs=[(ROOT/'references/day-geometry-with-night-west.png').as_posix(),DAY.as_posix(),(ROOT/'references/west-preview.png').as_posix(),STYLE.as_posix(),(ROOT/'references/west-native320.png').as_posix()]
 call={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False}
 (ROOT/'prompts/structure.prompt.txt').write_text(prompt,encoding='utf-8');write(ROOT/'prompts/structure.call.json',call)
 cfg=read(REPO/'config/image-generation.json');write(ROOT/'evidence/config-snapshot.json',cfg)
 write(ROOT/'evidence/structure-request.json',{'createdAt':stamp(),'configSnapshot':cfg,'submittedParameters':{'model':None,'quality':None,**call},'actualModel':None,'actualQuality':None,'references':[source(p) for p in refs],'planningOnly':True})
 tile=next(t for t in read(REPO/'qdao_city_tiles_4k_20260916/q64_production_plans/penglai_mid_autumn.json')['tiles'] if t['id']==TILE)
 write(ROOT/'plan.json',{'createdAt':stamp(),'tile':tile,'core':1024,'halo':115,'overlap':230,'nativePatchPixels':[1254,1254],'nativeGrid':[4,4],'sharedDayStructure':source(DAY),'sharedDayStructureAvailable':True,'dayStructureIsPlanningOnly':True,'westCandidate':WEST.as_posix(),'westCandidateSha256':sha(WEST),'referenceFrameGlobalXYWH':[53133,32653,4326,4326],'formalAccepted':False,'navigationVerified':False,'clientVerified':False,'stage':'shared_structure_night_edit_pending'})
 print(json.dumps(call,ensure_ascii=True))

def ingest(src):
 src=Path(src);dest=ROOT/'references/structure.png';assert not dest.exists()
 with Image.open(src) as im:assert im.size==(1254,1254)
 shutil.copyfile(src,dest);call=read(ROOT/'prompts/structure.call.json')
 write(str(dest)+'.generation.json',{'file':dest.as_posix(),'sha256':sha(dest),'generatedAt':datetime.datetime.fromtimestamp(src.stat().st_mtime,datetime.timezone.utc).isoformat(),'generatedAtEvidence':'Local tool output file modification time; service timestamp not exposed','width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(ROOT/'evidence/config-snapshot.json'),'submittedParameters':{'model':None,'quality':None,**call},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed: tool exposes no model or quality selectors and returns no confirmable model/quality values.','prompt':(ROOT/'prompts/structure.prompt.txt').as_posix(),'references':[source(p) for p in call['referenced_image_paths']],'evidence':{'sourceOutputPath':src.as_posix(),'sourceOutputSha256':sha(src),'toolResultFile':(ROOT/'evidence/structure-tool-result.json').as_posix()},'role':'shared_geometry_mid_autumn_appearance_planning_only','productionPixels':False,'formalAccepted':False})
 print(dest.as_posix(),sha(dest))

def guides():
 src=ROOT/'references/structure.png';im=Image.open(src).convert('RGB').resize((4326,4326),Image.Resampling.LANCZOS)
 dest=ROOT/'references/planning-extended4326.png';im.save(dest)
 derived(dest,[src],{'method':'uniform layout-only 1254->4326 reference enlargement; original frame includes115halo; no code-drawn exterior, no composite boundary','productionUseForbidden':True,'sourcePixelSize':[1254,1254],'referencePixelSize':[4326,4326],'coreBoxLTRB':[115,115,4211,4211]})
 rows=[]
 for r in range(1,5):
  for c in range(1,5):
   box=[(c-1)*1024,(r-1)*1024,(c-1)*1024+1254,(r-1)*1024+1254]
   target=ROOT/'guides'/f'p{r}{c}.png';im.crop(box).save(target)
   derived(target,[dest],{'method':'integer crop from planning canvas only','sourceBoxLTRB':box,'productionUseForbidden':True})
   rows.append({'id':f'p{r}{c}',**source(target),'sourceBoxLTRB':box,'globalCoreXYWH':[53248+(c-1)*1024,32768+(r-1)*1024,1024,1024]})
 write(ROOT/'guides/index.json',{'createdAt':stamp(),'tile':TILE,'guideCount':16,'productionPixels':False,'finalUseForbidden':True,'nativeContextMustOverridePlanningEdges':True,'source':source(dest),'guides':rows})
 plan=read(ROOT/'plan.json');plan.update({'stage':'structure_and_guides_ready_for_root_review','nightStructure':source(src),'planningExtended4326':source(dest),'guideIndex':(ROOT/'guides/index.json').as_posix(),'nativePatchCount':0});write(ROOT/'plan.json',plan)
 write(ROOT/'progress.json',{'updatedAt':stamp(),'tile':TILE,'appearance':'mid_autumn','stage':'structure_and_16_guides_waiting_root_review','nativeDetailPatches':0,'planningGuides':16,'completePixelCandidateTiles':0,'formalAccepted':0,'wholeCityComplete':False,'clientAccepted':False})
 print('16 planning-only guides saved; no native patches generated')

if __name__=='__main__':
 if sys.argv[1]=='init':init()
 elif sys.argv[1]=='ingest':ingest(sys.argv[2])
 elif sys.argv[1]=='guides':guides()
