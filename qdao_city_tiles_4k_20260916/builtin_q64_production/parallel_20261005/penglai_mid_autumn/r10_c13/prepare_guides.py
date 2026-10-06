from pathlib import Path
from PIL import Image
import json,hashlib,shutil
from datetime import datetime,timezone
from io import BytesIO
R=Path(__file__).resolve().parent;REF=R/'references';G=R/'guides';G.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p,role):return dict(file=str(p),sha256=sha(p),role=role)
def deriv(p,ss,op):write(str(p)+'.generation.json',dict(file=str(p),sha256=sha(p),createdAt=now(),width=Image.open(p).width,height=Image.open(p).height,format='PNG',derivedFrom=ss,operation=op,actualModel=None,actualQuality=None,unverifiedReason='Planning-only crop/scale/composite, not a new generation.',productionPixels=False,nativeDetailCount=0,formalAccepted=False))
host=Path('C:/Users/luyua/.codex/generated_images/01a10bb7-4da4-7553-abb9-125e7fe01ccc/exec-b1bdb7f7-204b-4c76-a405-9b3f36e34cbf.png');native=REF/'halo-extension-native.png';shutil.copyfile(host,native)
params=json.loads((R/'halo-extension.call.json').read_text())['submittedParameters'];roles=['transparent thin right/bottom planning halo edit target','approved coarse whole-map extended layout','main approved style']
config=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
write(str(native)+'.generation.json',dict(file=str(native),sha256=sha(native),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',toolResultPath=str(host),toolResultSha256=sha(host),toolResultEvidence=str(R/'halo-extension.tool-result.txt'),configSnapshot=config,submittedParameters=params,actualModel=None,actualQuality=None,unverifiedReason='Host-managed builtin exposes no model/quality selectors or result identifiers.',prompt=str(R/'halo-extension.prompt.txt'),references=[ref(Path(p),role) for p,role in zip(params['referenced_image_paths'],roles)],role='planning outer halo only',selectedWholeImage=False,selectedScope='only source-transparent right and bottom margin',productionPixels=False,nativeDetailCount=0,formalAccepted=False))
context=Image.open(REF/'halo-extension-context.png').convert('RGBA');gen=Image.open(native).convert('RGB');opaque=context.getchannel('A');inv=Image.eval(opaque,lambda x:255-x);mask=REF/'halo-selection-mask.png';inv.save(mask)
combined=Image.composite(context.convert('RGB'),gen,opaque);selected=REF/'planning-extended1254.png';combined.save(selected)
deriv(selected,[ref(REF/'halo-extension-context.png','existing confirmed macro geometry'),ref(native,'new thin outside halo only')],dict(kind='planning halo selection',mask=str(mask),maskSha256=sha(mask),coreGeneratedRedesignExcluded=True,resampling=False,planningGlobalRectXYWH=[49037,36749,4326,4326]))
deriv(mask,[ref(REF/'halo-extension-context.png','source alpha')],dict(kind='inverse alpha selection mask',resampling=False))
a=4326*1164/(1254*4096);b=90-115*1164/4096
deriv(REF/'halo-extension-context.png',[ref(REF/'structure-aligned-extended.png','frozen confirmed macro planning geometry')],dict(kind='planning-only affine window to expanded halo frame',affineDestinationToSource=[a,0,b,0,a,b],resampling='bicubic',transparentOutsideSource=True,globalRectXYWH=[49037,36749,4326,4326]))
layout=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_all_city_references/penglai_day/map-native-layout-reference.png');box=[49037*1254/65536,36749*1254/65536,53363*1254/65536,41075*1254/65536]
deriv(REF/'halo-layout-guide.png',[ref(layout,'whole-map approved day layout')],dict(kind='coarse planning-only fractional crop enlargement',sourceBoxXYXY=box,resampling='bicubic',productionDetail=False))
full=combined.resize((4326,4326),Image.Resampling.LANCZOS)
coreSource=REF/'structure-aligned.png';fixedcore=Image.open(coreSource).convert('RGB').resize((4096,4096),Image.Resampling.LANCZOS)
full.paste(fixedcore,(115,115));fullp=REF/'planning-extended4326.png';full.save(fullp)
assert full.crop((115,115,4211,4211)).tobytes()==fixedcore.tobytes()
deriv(fullp,[ref(selected,'planning halo frame'),ref(coreSource,'immutable macro core')],dict(kind='planning-only enlargement and exact core override',outputPixels=[4326,4326],coreRectXYXY=[115,115,4211,4211],coreScale=4096/1164,haloScale=4326/1254,resampling='LANCZOS',coreUnchangedFromDeclaredResize=True,globalRectXYWH=[49037,36749,4326,4326],productionDetail=False))
records=[]
for row in range(1,5):
 for col in range(1,5):
  x=(col-1)*1024;y=(row-1)*1024;box=[x,y,x+1254,y+1254];p=G/f'p{row}{col}.png';full.crop(tuple(box)).save(p);op=dict(kind='planning guide exact crop',cropXYXY=box,scale=1,resampling=False,globalPatchXYWH=[49037+x,36749+y,1254,1254],globalCoreXYWH=[49152+x,36864+y,1024,1024],core=1024,halo=115,overlap=230,notProductionPixels=True)
  deriv(p,[ref(fullp,'planning-only4326 field')],op);records.append(dict(id=f'p{row}{col}',file=str(p),sha256=sha(p),pixels=[1254,1254],**op))
for row in range(1,5):
 for col in range(1,5):
  im=Image.open(G/f'p{row}{col}.png')
  if col<4:assert im.crop((1024,0,1254,1254)).tobytes()==Image.open(G/f'p{row}{col+1}.png').crop((0,0,230,1254)).tobytes()
  if row<4:assert im.crop((0,1024,1254,1254)).tobytes()==Image.open(G/f'p{row+1}{col}.png').crop((0,0,1254,230)).tobytes()
write(R/'guides/index.json',dict(createdAt=now(),tile='r10_c13',source=ref(fullp,'planning4326'),count=16,allPixelsPlanningOnly=True,productionNativeCount=0,grid=[4,4],patchPixels=[1254,1254],core=1024,halo=115,overlap=230,overlapsPixelIdentical=True,records=records))
plan=json.loads((R/'plan.json').read_text());handoff=json.loads((R.parent/'handoff.json').read_text());nw=Path(handoff['baselineCandidates'][2]['file']);plan['northWestCandidate']=str(nw)
freeze=json.loads((R/'frozen-neighbors.json').read_text());by={}
for d in freeze['neighbors']:
 key='north' if d['role'].startswith('north') else 'west';p=Path(d['source']);raw=p.read_bytes();img=Image.open(BytesIO(raw)).convert('RGB');pixel=hashlib.sha256(img.crop(tuple(d['cropXYXY'])).tobytes()).hexdigest();assert pixel==d['pixelSha256'];by[key]=dict(file=str(p),sha256=hashlib.sha256(raw).hexdigest(),pixels=[4096,4096],scopedPassed=True,scopedPassRegion=d['cropXYXY'],frozenCropFile=d['file'],frozenCropPixelSha256=pixel,checkedAt=now());plan[key+'Candidate']=str(p)
by['northWest']=dict(file=str(nw),sha256=sha(nw),pixels=[4096,4096],scopedPassRegion=[3981,3981,4096,4096],source='existing old r09_c12 final candidate from handoff')
plan.update(updatedAt=now(),candidateSourcesStillUnderScopedRepair=False,candidateStatusScope='Only frozen context scopes are asserted passed; no new whole-tile acceptance claims.',candidateSources=by,northCandidateSha256=by['north']['sha256'],westCandidateSha256=by['west']['sha256'],northWestCandidateSha256=by['northWest']['sha256'],sharedDayStructureAvailable=False,proposedSharedStructure=str(REF/'shared-structure-aligned.png'),sharedDayTaskAdopted=False,nightStructure=str(coreSource),planningExtended4326=str(fullp),guideIndex=str(R/'guides/index.json'),structurePreparationStatus='ready_for_root_review_with_native_boundary_precedence',nextRequirement='Root reviews proposed common structure, then validates p11 transparent-context native outpaint; no native patches generated here.')
plan['nativePatchConstraints']={
 'p21':'CRITICAL WESTERN BOUNDARY: Image1 actual r10_c12 native west context is authoritative over the soft planning guide. Keep the blue fabric-covered surface at its true native edge height, slope and footprint; do not shift it to match the guide. Continue both existing wooden rail/beam surfaces and their supporting posts from the native strip at their actual endpoints, widths and perspective. The planning west join around extended planning y450..650 contains residual differences; resolve them by extending real native geometry smoothly into the unchanged large stall footprint, never by cropping a beam at the mask edge or adding a post.',
 'p31':'CRITICAL WESTERN BOUNDARY: Preserve the real native r10_c12 wooden beam/rail and post-foot endpoints and their relative heights. The planning west join near extended planning y650..800 remains approximate. Native Image1 fixes the geometry: continue these existing supports coherently, without creating intersecting/doubled rails, extra posts or detached feet. Continue each paving grout endpoint from the actual native strip with its original width and slope; keep the open walking corridor and cargo footprints unchanged.',
 'p41':'CRITICAL WESTERN BOUNDARY: The entering blue canopy corner and rounded wooden tip must connect to actual r10_c12 native Image1 at exactly their existing positions and perspective. The planning lower-left corner is approximate and may not override these native contours. Keep canopy occupancy and frame count fixed; continue the actual paving line endpoints naturally. Do not add a second tip, bend the canopy merely to follow the soft guide, or invent a new pavement branch.'}
plan['generationSchedule']={'method':'strict north/left/diagonal dependencies; anti-diagonal wavefronts or row pipeline after required predecessors saved','helper':str(R.parent/'native_patch.py'),'nativeContextFirst':True,'guideSecondPlanningOnly':True,'styleThird':True,'doNotOverwriteNativeOutputs':True,'productionNativeCount':0}
write(R/'plan.json',plan)
print(json.dumps({'guides':16,'planning4326':str(fullp),'planningSha256':sha(fullp),'coreSource':str(coreSource),'coreSha256':sha(coreSource),'northWestCandidate':str(nw),'northSha256':by['north']['sha256'],'westSha256':by['west']['sha256']},ensure_ascii=False))
