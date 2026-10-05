"""Prepare c10 layout-only references. Writes only beside this script; never generates art."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
BASE = OUT.parent.parent
REPO = Path('D:/work/image')
DATA = REPO/'qdao_city_tiles_4k_20260916'
DAY = BASE/'lanxian_day'
LAYOUT = DATA/'builtin_q64_all_city_references/lanxian_day/map-native-layout-reference.png'
SPRING = DATA/'builtin_q64_all_city_references/lanxian_spring/map-native-layout-reference.png'
STYLE = REPO/'designs/gameplay-ui/04-guild.png'
NAV = REPO/'qdao_large_city_maps_20260912/runtime/lanxian-navigation.json'
PRIOR_NAV = OUT.parent/'preflight/navigation-contract.json'
PLAN = DATA/'q64_production_plans/lanxian_spring.json'
ASM = OUT.parent/'r08_c09/assembly_v2/assembly.json'
CORE = (36864, 28672, 40960, 32768)
HALO = (36749, 28557, 41075, 32883)
SCALE = 65536/1254
NOW = datetime.now(timezone.utc).isoformat()

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def info(p,role): return {'file':str(p),'sha256':sha(p),'role':role}
def savej(p,data): Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rnd(vs): return [[round(v,6) for v in p] for p in vs]
def clip(poly, rect):
    points=[tuple(p) for p in poly]
    for axis,edge,less in [(0,rect[0],False),(0,rect[2],True),(1,rect[1],False),(1,rect[3],True)]:
        result=[]
        if not points: break
        for a,b in zip(points[-1:]+points[:-1],points):
            ina=a[axis]<=edge if less else a[axis]>=edge
            inb=b[axis]<=edge if less else b[axis]>=edge
            if ina!=inb:
                t=(edge-a[axis])/(b[axis]-a[axis])
                result.append(tuple(edge if j==axis else a[j]+t*(b[j]-a[j]) for j in range(2)))
            if inb: result.append(b)
        points=result
    return points
def saveimg(im,name,derivation):
    p=OUT/'guides'/name; im.save(p)
    rec={'createdAtUtc':NOW,'file':str(p),'sha256':sha(p),'pixels':list(im.size),
         'productionPixelsAllowed':False,'role':'layout/context guide only; not a finished tile',**derivation}
    savej(p.with_suffix('.derived.json'),rec)
    return rec

# A day c10 directory appearing is a hard stop, so a new common geometry is never silently duplicated.
assert not (DAY/'r08_c10').exists(), 'Day c10 is now present: inspect/reuse its common geometry before preparing.'
day_c10_matches=[str(p) for p in DAY.rglob('*') if 'r08_c10' in str(p)]
assert not day_c10_matches, day_c10_matches
(OUT/'guides').mkdir(parents=True,exist_ok=True)
(OUT/'qa').mkdir(exist_ok=True)
plan=read(PLAN); entry=next(x for x in plan['tiles'] if x['id']=='r08_c10')
assert entry['finalPixelRect']==[36864,28672,4096,4096]
assembly=read(ASM)
source=next(x for x in assembly['outputs'] if x['role']=='candidate_with_halo')
source_core=next(x for x in assembly['outputs'] if x['role']=='candidate')
assert sha(source['file'])==source['sha256']
assert sha(source_core['file'])==source_core['sha256']
with Image.open(source['file']) as im: padded=im.convert('RGB'); assert im.size==(4326,4326)
with Image.open(source_core['file']) as im: core=im.convert('RGB'); assert im.size==(4096,4096)
assert padded.crop((115,115,4211,4211)).tobytes()==core.tobytes()
with Image.open(LAYOUT) as im: layout=im.convert('RGB'); assert im.size==(1254,1254)
source_box=tuple(v/SCALE for v in HALO)
guide=layout.transform((4326,4326),Image.Transform.EXTENT,source_box,Image.Resampling.BICUBIC)
guide_rec=saveimg(guide,'day-layout-only-4326.png',{
    'sources':[info(LAYOUT,'whole-city common day layout, macrogeometry only')],
    'operation':'PIL EXTENT BICUBIC; enlarged reference pixels only',
    'source1254RectLTRB':list(source_box),'whole65536RectLTRB':list(HALO),
    'coreRectInGuideLTRB':[115,115,4211,4211],'alignmentAccepted':False})
strip=padded.crop((4096,0,4326,4326))
strip_rec=saveimg(strip,'spring-c09-east-overlap-230x4326.png',{
    'sources':[info(source['file'],'latest c09 native-pixel assembly candidate, not formally accepted'),info(ASM,'assembly provenance')],
    'operation':'exact crop, no resampling','cropInSourceLTRB':[4096,0,4326,4326],
    'whole65536RectLTRB':[36749,28557,36979,32883],
    'placementInC10PaddedGuideLTRB':[0,0,230,4326],
    'coreRegionInStripLTRB':[0,115,115,4211],
    'provisionalHaloRegionsInStripLTRB':[[115,0,230,4326],[0,0,115,115],[0,4211,115,4326]],
    'temporaryNativeMosaic':False,'assemblyQaAccepted':assembly['qaAccepted'],
    'notes':'First 115 columns inside y115..4211 are c09 core. Right 115 and top/bottom are c09 extrapolated halo; no c10 acceptance implied.'})
fixed=core.crop((3981,0,4096,4096))
assert fixed.tobytes()==strip.crop((0,115,115,4211)).tobytes()
fixed_rec=saveimg(fixed,'spring-c09-core-east-115x4096.png',{
    'sources':[info(source_core['file'],'c09 candidate core; exact neighboring pixels')],
    'operation':'exact crop, no resampling','cropInSourceLTRB':[3981,0,4096,4096],
    'whole65536RectLTRB':[36749,28672,36864,32768],
    'placementInC10PaddedGuideLTRB':[0,115,115,4211],
    'assemblyQaAccepted':assembly['qaAccepted']})
composite=guide.copy(); composite.paste(strip,(0,0))
composite_rec=saveimg(composite,'layout-only-with-west-native-context-4326.png',{
    'sources':[guide_rec,strip_rec],'operation':'paste exact 230x4326 c09 strip over enlarged day layout at (0,0); no blending',
    'visibleJoinIsNotASeamRepair':True,'alignmentAccepted':False,
    'notes':'Mixed-resolution planning guide. All pixels are forbidden as production output; exact context original remains separately available.'})
preview_rec=saveimg(composite.resize((1254,1254),Image.Resampling.LANCZOS),'regional-layout-only-preview-1254.png',{
    'sources':[info(OUT/'guides/layout-only-with-west-native-context-4326.png','mixed-resolution planning guide')],
    'operation':'4326 to 1254 LANCZOS for regional composition reference only','alignmentAccepted':False})

nav=read(NAV); previous=read(PRIOR_NAV)
shapes=[]
for field,kind in [('allowed_floor_polygons','allowed_floor'),('excluded_obstacle_polygons','blocked_obstacle')]:
    for s in nav[field]:
        whole=[[x*SCALE,y*SCALE] for x,y in s['vertices']]
        local=[[x-CORE[0],y-CORE[1]] for x,y in whole]
        halo_clipped=clip(local,(-115,-115,4211,4211))
        if not halo_clipped: continue
        clipped=clip(local,(0,0,4096,4096))
        xs=[p[0] for p in local]; ys=[p[1] for p in local]
        shapes.append({'name':s['name'],'kind':kind,'source1254Vertices':s['vertices'],
            'whole65536Vertices':rnd(whole),'tileLocalVerticesUnclipped':rnd(local),
            'tileLocalClippedVertices':rnd(clipped),'tileHaloLocalClippedVertices':rnd(halo_clipped),
            'tileLocalUnclippedBBoxLTRB':[round(v,6) for v in (min(xs),min(ys),max(xs),max(ys))],
            'intersectsCore':bool(clipped)})
contract={'schemaVersion':1,'createdAtUtc':NOW,'tile':'r08_c10',
    'status':'historical_navigation_constraints_only_not_new_art_acceptance',
    'sources':[info(NAV,'historical shared day/festival occupancy'),info(PRIOR_NAV,'verified historical mask reconstruction and shared runtime contract'),info(LAYOUT,'current common day layout; different artwork basis'),info(PLAN,'tile-coordinate plan')],
    'historicalNavigationArtworkSources':nav['source_maps'],
    'sourceCurrentLayoutIsDifferentFromHistoricalNavArtwork':True,
    'coordinates':{'wholePixelCoreLTRB':list(CORE),'wholePixelHaloLTRB':list(HALO),
        'source1254CoreLTRB':[v/SCALE for v in CORE],'source1254HaloLTRB':list(source_box),
        'tileLocalCoreLTRB':[0,0,4096,4096],'tileLocalHaloLTRB':[-115,-115,4211,4211],
        'paddedGuideCoreLTRB':[115,115,4211,4211],'scale1254To65536':SCALE,
        'origin':'top-left; x right; y down; rectangles endpoint-exclusive',
        'formulaWhole':['X = source_x * 65536 / 1254','Y = source_y * 65536 / 1254'],
        'formulaLocal':['x = source_x * 65536 / 1254 - 36864','y = source_y * 65536 / 1254 - 28672'],
        'formulaPaddedGuide':['u = x + 115','v = y + 115'],'worldRectXZ':entry['worldRect']},
    'intersectingPolygons':shapes,'historicalMaskEvidence':previous['historicalMask'],
    'constraints':['Preserve common day/spring ground routes, circle courses, planter footprints, bridge/stair/river coordinates.',
        'Do not add festival objects on allowed ground. Keep historical planter obstruction areas blocked; exact new-art alignment requires review.',
        'No new bridge, road, building, tree, or planter may be invented from styling. Navigation overlay may not be used as a production image.',
        'The c09 real edge constrains local continuation; 1254 whole-city crop is macro layout and may disagree with c09 regional geometry. Resolve continuity before native generation.'],
    'alignmentAccepted':False,'newArtworkNavigationAccepted':False,'formalAccepted':False}
savej(OUT/'navigation-contract.json',contract)

font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
thumb=guide.resize((1000,1000),Image.Resampling.LANCZOS).convert('RGBA')
layer=Image.new('RGBA',thumb.size); d=ImageDraw.Draw(layer)
for s in shapes:
    ps=[((x+115)/4326*1000,(y+115)/4326*1000) for x,y in s['tileHaloLocalClippedVertices']]
    color=(25,170,115,28) if s['kind']=='allowed_floor' else (235,30,55,100)
    d.polygon(ps,fill=color,outline=color[:3]+(230,))
thumb=Image.alpha_composite(thumb,layer).convert('RGB')
preview=Image.new('RGB',(1000,1100),'#fff7e5');preview.paste(thumb,(0,100));d=ImageDraw.Draw(preview)
d.text((18,10),'r08_c10 | OLD navigation coordinate constraints only',font=font,fill='#9d1324')
d.text((18,40),'Enlarged current day layout; new geometry alignment NOT verified',font=font,fill='#9d1324')
d.text((18,70),'Green: allowed floor. Red: historical planter obstruction. QA ONLY.',font=font,fill='#273331')
preview.save(OUT/'qa/historical-navigation-preview.png')
savej(OUT/'qa/historical-navigation-preview.derived.json',{
    'createdAtUtc':NOW,'file':str(OUT/'qa/historical-navigation-preview.png'),
    'sha256':sha(OUT/'qa/historical-navigation-preview.png'),'pixels':[1000,1100],
    'sources':[info(OUT/'navigation-contract.json','historical occupancy mapping'),info(LAYOUT,'current day macro layout')],
    'operation':'enlarge fractional day crop then overlay mapped legacy polygon constraints',
    'role':'QA only','productionPixelsAllowed':False,'alignmentAccepted':False})

prompt='''准备请求，尚未提交。只生成《问道》小镇春节地图 r08_c10 的区域结构引导图，1254×1254；该输出仍是布局引导，不计入4K成品原片。
覆盖全城65536坐标[36749,28557,41075,32883)，核心[36864,28672,40960,32768)。固定俯视等距视角、尺度、光照方向和地面坡度。
附图角色：regional-layout-only-preview-1254.png 是当前day全城布局的名义裁取加c09原生东侧边缘；day全城图只规定宏观拓扑，不规定高清像素；spring-c09-east-overlap-230x4326.png 是真实邻图完整高度230px边缘上下文，左115px且y115..4211来自c09核心，右115px与上下各115为候选外延；04-guild.png 只规定圆润饱满、明亮干净、细腻完整的道家Q版画法；春节全景只规定克制红金气氛。
由c09东边的暖米色铺地、灰米相间圆环铺装以及下部已有树坛叶片/木栏端部，按同一尺度连续向东延伸。保留day名义布局中的东南树坛、各树冠/树干/围栏占地与右下靠近河岸的既有绿植；只在已有木栏、已有柱帽材质上小量朱红暖金。不要新增实体占地，不移动道路、圆环、地砖缝、树木、建筑、桥梯、河岸、投影；不要将旧导航红色覆盖画进作品，不要遍地花瓣、不要给地砖涂红金。
现有day小图与c09区域原生边缘尚未证明几何对齐；边界相接时以c09真实上下文连续性为局部约束，同时保持day道路/树坛宏观布局。若需要改变树坛占地或道路才能衔接，应返回可检查的结构提案，不得宣称已经共享day高清几何。
历史导航约束：中央广场及外围铺地允许通行；plaza southeast planter 与 plaza southern east planter 为阻挡占地，按navigation-contract.json的坐标核对。旧导航源图与当前布局图不同，此处不构成新图导航验收。
输出干净单幅区域参考，不带文字标注、水印、网格、标尺、拼接面板。禁止把放大的参考像素或此区域引导当作正式4096成品；后续必须分16张1254原生细节图生产，再按1024核心+115halo拼接并验收。
'''
(OUT/'regional-prompt-pending.txt').write_text(prompt,encoding='utf-8')
request={'status':'prepared_not_submitted','generationAuthorizedInThisStep':False,'createdAtUtc':NOW,
    'tile':'r08_c10','purpose':'regional layout guide only; no production native image generated',
    'promptFile':str(OUT/'regional-prompt-pending.txt'),'promptSha256':sha(OUT/'regional-prompt-pending.txt'),
    'suggestedReferences':[info(OUT/'guides/regional-layout-only-preview-1254.png','nominal common layout plus c09 boundary composition'),
        info(OUT/'guides/spring-c09-east-overlap-230x4326.png','exact current west-neighbor edge context'),
        info(LAYOUT,'current day common macrogeometry'),info(STYLE,'locked rendering/material style only'),info(SPRING,'festival color restraint only')],
    'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,
    'toolCalled':False,'recheckBeforeGeneration':'Recheck parallel day r08_c10 and c09 assembly_v2 hashes; adopt any newly available common day guide instead of creating competing geometry.'}
savej(OUT/'regional-request-pending.json',request)
report={'schemaVersion':1,'createdAtUtc':NOW,'tile':'r08_c10','status':'layout_only_prepared_no_generation',
    'dayC10Present':False,'dayC10Matches':day_c10_matches,
    'dayCurrentWorkEvidence':info(DAY/'current-work.json','snapshot evidence of c09-only current day work'),
    'dayLayout':info(LAYOUT,'most reliable available shared whole-city layout'),
    'c09AssemblyEvidence':info(ASM,'latest finished assembly source; candidate not accepted'),
    'c09Candidate':source_core,'c09PaddedCandidate':source,
    'temporaryNativeMosaicUsed':False,'coreBoundaryByteEqualityVerified':True,
    'artifacts':[guide_rec,strip_rec,fixed_rec,composite_rec,preview_rec],
    'navigationContract':str(OUT/'navigation-contract.json'),'pendingRequest':str(OUT/'regional-request-pending.json'),
    'newGeneratedImages':0,'newComplete4KTiles':0,'geometryAlignmentAccepted':False,
    'warnings':['No shared day c10 regional/native geometry exists at preparation time.',
        'Whole-city source crop has only about 82.77 source pixels per side including halo; all enlarged versions are guide-only.',
        'c09 assembly is candidate pending visual review. Its outer halo is extrapolated, not accepted c10 art.',
        'Low-resolution nominal geometry and current c09 native regional geometry must be reconciled before production.']}
savej(OUT/'preparation.json',report)
print(json.dumps({'output':str(OUT),'nav':[(s['name'],s['kind'],s['tileLocalUnclippedBBoxLTRB']) for s in shapes],
    'c09CoreSHA':source_core['sha256'],'c09PaddedSHA':source['sha256'],'dayLayoutSHA':sha(LAYOUT)},ensure_ascii=False))
