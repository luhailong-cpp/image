"""Next tile exact-frame planning. All writes restricted to this tile."""
from pathlib import Path
import sys,shutil
from PIL import Image
F=Path(__file__).resolve().parent;ROOT=F.parent;sys.path.insert(0,str(ROOT))
from production import read,sha,now,REPO
from production import write as base_write
X,Y,S,H=53248,40960,4736,320
FRAME=[X-H,Y-H,S,S];R=F/'references'
N=ROOT/'r10_c14/output/r10_c14-candidate.png';W=ROOT/'r11_c13/output/r11_c13-candidate.png';NW=ROOT/'r10_c13/output/r10_c13-candidate.png'
DAY=ROOT.parent/'penglai_day/r11_c14/references/structure.png';STYLE=REPO/'designs/gameplay-ui/04-guild.png'
EXPECTED={N:'963d29bf2b73c9ff400d29689a43023135b7653e0cd0159b80f7fc0d6b6f70f3',W:'1aa087f96cf986582881560436fb3fba780cbcbe13f3b29a133e4eb9c0ece180',NW:'c6c7176ea72228aca772c78a17fe8e3b5fc699904f46205d62ae482f420d1a5b',DAY:'5adad2dfbf5d3a803d7cb511a74adc697ce726e6206454df6d5289e8ba3e422f'}
def write(p,v):
 p=Path(p);assert p.resolve().is_relative_to(F.resolve());base_write(p,v)
def ref(p,**kw):return dict(file=str(p),sha256=sha(p),**kw)
def saveim(im,p,sources,operation):
 p=Path(p);assert p.resolve().is_relative_to(F.resolve()) and not p.exists();p.parent.mkdir(parents=True,exist_ok=True);im.save(p);write(str(p)+'.generation.json',dict(**ref(p),width=im.width,height=im.height,createdAt=now(),derivedFrom=[ref(a) for a in sources],operation=operation,productionPixels=False))
def setup():
 for p,h in EXPECTED.items():assert sha(p)==h
 for d in [R,F/'evidence',F/'qa',F/'guides']:d.mkdir(parents=True,exist_ok=True)
 write(F/'evidence/day-source-history.json',read(str(DAY)+'.generation.json'))
 write(F/'evidence/day-frame-evidence.json',dict(daySource=ref(DAY),frameGlobalXYWH=[X-115,Y-115,4326,4326],evidence=ref(DAY.parents[1]/'helper.py'),observed='Read-only helper.prepare uses global crop GX-115,GY-115,GX+4211,GY+4211 and1254 output. Structure prompt preserves that exact guide framing.',dayUnmodified=True))
 dc=R/'day-structure-snapshot.png';assert not dc.exists();shutil.copy2(DAY,dc);write(str(dc)+'.generation.json',dict(**ref(dc),copiedAt=now(),derivedFrom=[ref(DAY)],operation=dict(kind='read-only unchanged day planning snapshot',globalFrameXYWH=[X-115,Y-115,4326,4326]),productionPixels=False))
 ni,wi,nwi=[Image.open(p).convert('RGB') for p in [N,W,NW]]
 for role,im,p in [('north',ni,N),('west',wi,W)]:
  saveim(im.resize((1254,1254),Image.Resampling.LANCZOS),R/(role+'-context-preview.png'),[p],dict(kind='downsample native neighbor context only',sourceUpscaled=False))
  for depth in [115,320]:
   box=[0,4096-depth,4096,4096] if role=='north' else [4096-depth,0,4096,4096]
   saveim(im.crop(box),R/f'{role}-native{depth}.png',[p],dict(kind='exact native context crop',cropLTRB=box,scale=1))
 saveim(nwi.crop((3776,3776,4096,4096)),R/'northwest-native320.png',[NW],dict(kind='exact true NW native corner',cropLTRB=[3776,3776,4096,4096],scale=1))
 layout=REPO/'qdao_city_tiles_4k_20260916/builtin_q64_all_city_references/penglai_day/map-native-layout-reference.png';li=Image.open(layout).convert('RGB');k=li.width/65536
 canvas=li.transform((S,S),Image.Transform.EXTENT,[(X-H)*k,(Y-H)*k,(X+4096+H)*k,(Y+4096+H)*k],Image.Resampling.BICUBIC)
 canvas.paste(Image.open(dc).convert('RGB').resize((4326,4326),Image.Resampling.LANCZOS),(205,205));canvas.paste(ni.crop((0,3776,4096,4096)),(320,0));canvas.paste(wi.crop((3776,0,4096,4096)),(0,320));canvas.paste(nwi.crop((3776,3776,4096,4096)),(0,0))
 target=R/'night-edit-target.png';saveim(canvas.resize((1254,1254),Image.Resampling.LANCZOS),target,[layout,dc,N,W,NW],dict(kind='exact-frame day planning target with real N W NW night anchors',globalFrameXYWH=FRAME,dayPasteXY=[205,205],dayPlanningPixels=[4326,4326],northPasteXY=[320,0],westPasteXY=[0,320],northwestPasteXY=[0,0],outputPixels=[1254,1254],allResamplingPlanningOnly=True))
 tile=next(t for t in read(REPO/'qdao_city_tiles_4k_20260916/q64_production_plans/penglai_mid_autumn.json')['tiles'] if t['id']=='r11_c14')
 plan=dict(createdAt=now(),tile=tile,core=1024,halo=115,overlap=230,nativePatchPixels=[1254,1254],nativeGrid=[4,4],referenceFrameGlobalXYWH=FRAME,structureSourceFramePixels=[1254,1254],structureCoreLTRB=[H*1254/S,H*1254/S,(H+4096)*1254/S,(H+4096)*1254/S],sharedDayStructureSource=ref(dc),sharedDayTaskAdopted=False,dayTaskModified=False,stage='night_structure_pending_generation',rootReviewPending=True,nativePatchCount=0,formalAccepted=False,navigationVerified=False,clientVerified=False)
 for key,p in [('northCandidate',N),('westCandidate',W),('northWestCandidate',NW)]:plan[key]=str(p);plan[key+'Sha256']=sha(p)
 write(F/'plan.json',plan)
 prompt='''Use case: lighting-weather with exact composition preservation. Edit Image1 ONLY into a clean Mid-Autumn EVENING game-map fragment, matching the authoritative night anchors already inside Image1. Output one opaque1254x1254 square. Image1 is the ONLY target composition: fixed4736-global-pixel frame including320 margin on every side; the4096 core is inset84.73px on each edge. Preserve the ENTIRE frame and all object positions. Do not zoom, crop the margins, recenter, rotate, complete clipped objects, or turn it into a standalone scene.
Image1 already has real NIGHT neighbor strips across TOP84.73px and LEFT84.73px, with true night northwest corner. These are authoritative existing objects, colors and exact contour endpoints. The straight collage cuts at x84.73 and y84.73 are NOT object edges. Paint continuous real shapes from these endpoints into the daytime interior. NATIVE boundary silhouettes take precedence over small conflicting day-guide geometry. Image2 is the NORTH neighbor full context, located above the core. Image3 is the WEST neighbor full context, located left of the core. Never replace Image1 framing with either context image. Image4 is approved STYLE ONLY, never UI content.
Keep this exact existing boat composition: broad cream sail cropped at the top, its thin horizontal battens, one tall honey-brown mast, the diagonal spar and existing ropes, curved boat hull entering from lower-left, existing few deck planks and bench, existing jetty cropped across the upper-right. Preserve the rope connections, sail outline, hull footprint, object counts and current empty water areas. Continue the WEST neighbor clipped wooden hull at precisely its entry height and angle; continue NORTH jetty and water fender endpoints. No additional boat, extra mast, new quay, posts, buildings, lanterns, sail emblem, flag, people or decorations. NO SKY, horizon, moon, stars, scenic border, lettering, UI or watermark.
Use the adjacent night artwork's bright rounded Daoist chibi hand-painted finish: saturated cobalt water, broad organized blue water cells with restrained warm gold reflections continuing the real W side, ivory sail in warm amber light and cool blue-violet soft shadows, honey wood with clean golden edge highlights. The scene stays bright and readable. No photographic grain, texture noise, murky darkness, blur or sharpening halos. Repaint lighting while retaining exact fixed geometry and crop; this is a planning image, later native patches supply final detail.'''
 pp=F/'night-structure.prompt.txt';pp.write_text(prompt,encoding='utf-8');refs=[target,R/'north-context-preview.png',R/'west-context-preview.png',STYLE];call=dict(prompt=prompt,referenced_image_paths=[str(p) for p in refs],transparent_background=False)
 write(F/'night-structure.call.json',call);write(F/'night-structure.request.json',dict(preparedAt=now(),batch='continuation of builtin_q64 parallel20261005; same config target retained',configSnapshot=read(REPO/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,**call),prompt=str(pp),promptSha256=sha(pp),references=[ref(p) for p in refs],sourceVersions=[ref(p) for p in EXPECTED],planningFrameGlobalXYWH=FRAME,productionPixels=False))
 print(F/'night-structure.call.json')
def save(source):
 src=Path(source);dst=R/'structure.png';req=read(F/'night-structure.request.json');assert not dst.exists() and Image.open(src).size==(1254,1254)
 for a in req['references']+req['sourceVersions']:assert sha(a['file'])==a['sha256']
 shutil.copy2(src,dst);write(str(dst)+'.generation.json',dict(**ref(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Builtin host-managed; actual selectors and version/quality metadata not exposed.',prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),planningFrameGlobalXYWH=FRAME,sourceUpscaled=False,resizedAfterGeneration=False,productionPixels=False,nativeDetailCount=0,formalAccepted=False));print(dst);print(sha(dst))
if __name__=='__main__':
 if sys.argv[1]=='setup':setup()
 elif sys.argv[1]=='save':save(sys.argv[2])
