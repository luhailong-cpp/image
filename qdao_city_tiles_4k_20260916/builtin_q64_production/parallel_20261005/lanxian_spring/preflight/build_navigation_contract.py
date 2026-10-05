"""Read shared historical navigation; write only this task's preflight artifacts."""
from pathlib import Path
from datetime import datetime, timezone
from collections import deque
import hashlib, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = Path(__file__).resolve().parent
REPO = Path('D:/work/image')
NAV = REPO/'qdao_large_city_maps_20260912/runtime/lanxian-navigation.json'
BUILDER = NAV.parent/'build_navigation.py'
LAYOUT = REPO/'qdao_city_tiles_4k_20260916/builtin_q64_all_city_references/lanxian_day/map-native-layout-reference.png'
PLAN = REPO/'qdao_city_tiles_4k_20260916/q64_production_plans/lanxian_spring.json'
CLIENT = Path('D:/work/mmorpg-client/Assets/Scripts/World/Tianyong/FestivalRegionMap.cs')
SCALE = 65536/1254
TILE = (32768,28672,36864,32768)
SOURCE_BOX = tuple(v/SCALE for v in TILE)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p, role): return {'file':str(p),'sha256':sha(p),'role':role}
def savej(p, value): p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rounded(points): return [[round(v,6) for v in p] for p in points]
def clip(poly, rect):
    points=[tuple(p) for p in poly]
    for axis,edge,keep_less in [(0,rect[0],False),(0,rect[2],True),(1,rect[1],False),(1,rect[3],True)]:
        result=[]
        if not points: break
        for a,b in zip(points[-1:]+points[:-1],points):
            ina=a[axis]<=edge if keep_less else a[axis]>=edge
            inb=b[axis]<=edge if keep_less else b[axis]>=edge
            if ina!=inb:
                t=(edge-a[axis])/(b[axis]-a[axis])
                result.append(tuple(edge if j==axis else a[j]+t*(b[j]-a[j]) for j in range(2)))
            if inb: result.append(b)
        points=result
    return points
def transform_shape(shape, kind):
    verts=shape['vertices']; whole=[[x*SCALE,y*SCALE] for x,y in verts]
    local=[[x-TILE[0],y-TILE[1]] for x,y in whole]
    return {'name':shape['name'],'kind':kind,'source1254Vertices':verts,
            'whole65536Vertices':rounded(whole),'tileLocalVerticesUnclipped':rounded(local),
            'tileLocalClippedVertices':rounded(clip(local,(0,0,4096,4096))),
            'worldXZVertices':rounded([[50+x/1254*300,300-y/1254*300] for x,y in verts])}

nav=json.loads(NAV.read_text(encoding='utf-8-sig'))
plan=json.loads(PLAN.read_text(encoding='utf-8-sig'))
entry=next(t for t in plan['tiles'] if t['id']=='r08_c09')
assert entry['finalPixelRect']==[32768,28672,4096,4096]
with Image.open(LAYOUT) as im: layout=im.convert('RGB'); assert im.size==(1254,1254)
selected=[]
for field,kind in [('allowed_floor_polygons','allowed_floor'),('excluded_obstacle_polygons','blocked_obstacle')]:
    for s in nav[field]:
        if clip(s['vertices'],SOURCE_BOX): selected.append(transform_shape(s,kind))
assert [s['name'] for s in selected]==['Taiji central plaza','central plaza broad paved perimeter','plaza southern east planter']

# Reconstruct the historical mask in memory exactly as the saved builder specifies.
raster=Image.new('L',(1254,1254)); d=ImageDraw.Draw(raster)
for s in nav['allowed_floor_polygons']: d.polygon([tuple(v) for v in s['vertices']],fill=255)
for s in nav['manually_traced_route_strips']:
    pts=[tuple(v) for v in s['centerline']];w=s['width_pixels']
    d.line(pts,fill=255,width=w,joint='curve')
    for x,y in pts:d.ellipse((x-w/2,y-w/2,x+w/2,y+w/2),fill=255)
for s in nav['excluded_obstacle_polygons']:d.polygon([tuple(v) for v in s['vertices']],fill=0)
pixels=np.asarray(raster.filter(ImageFilter.MinFilter(3)))==255
grid=np.zeros((150,150),dtype=bool)
for y in range(150):
    for x in range(150):
        grid[y,x]=pixels[math.floor(y*1254/150):math.ceil((y+1)*1254/150),math.floor(x*1254/150):math.ceil((x+1)*1254/150)].all()
spawn=tuple(nav['spawn_cell']); seen={spawn};q=deque([spawn])
while q:
    x,y=q.popleft()
    for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
        if 0<=xx<150 and 0<=yy<150 and grid[yy,xx] and (xx,yy) not in seen:seen.add((xx,yy));q.append((xx,yy))
connected=np.zeros_like(grid)
for x,y in seen:connected[y,x]=True
mask_sha=hashlib.sha256(np.packbits(connected.flatten(),bitorder='big').tobytes()).hexdigest()
mask_matches=mask_sha==nav['decoded_mask_sha256']
assert mask_matches, 'Historical navigation reconstruction mismatch'

sources=[info(NAV,'historical shared day/festival polygons and navigation contract; original artwork basis'),
         info(BUILDER,'historical mask construction algorithm, read only'),
         info(LAYOUT,'current day layout reference shown for QA only; alignment to historical navigation not accepted'),
         info(PLAN,'65536 grid coordinate plan only'),info(CLIENT,'same-region shared navigation runtime contract')]
contract={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'lanxian_spring',
    'tile':'r08_c09','status':'historical_navigation_constraints_only_not_new_art_acceptance','sources':sources,
    'historicalNavigationArtworkSources':nav['source_maps'],
    'sourceCurrentLayoutIsDifferentFromHistoricalNavArtwork':True,
    'coordinates':{'wholePixelRectLTRB':list(TILE),'wholePixelRectXYWH':[32768,28672,4096,4096],
        'source1254RectLTRB':list(SOURCE_BOX),'tileLocalRectLTRB':[0,0,4096,4096],
        'origin':'top-left; x right; y down; pixel rectangles endpoint-exclusive','scale1254To65536':SCALE,
        'formulaWhole':['X = source_x * 65536 / 1254','Y = source_y * 65536 / 1254'],
        'formulaTileLocal':['x = source_x * 65536 / 1254 - 32768','y = source_y * 65536 / 1254 - 28672'],
        'formulaWorld':['world_x = 50 + source_x / 1254 * 300','world_z = 300 - source_y / 1254 * 300'],
        'worldRectXZ':entry['worldRect']},
    'intersectingPolygons':selected,
    'historicalMask':{'grid':[150,150],'cellWorldUnits':2,'packing':nav['packing'],
        'expectedDecodedSha256':nav['decoded_mask_sha256'],'reconstructedDecodedSha256':mask_sha,
        'shaMatches':mask_matches,'walkableCells':int(connected.sum()),'reconstructionScope':'in memory only; no runtime resource written',
        'algorithm':'Union allowed floor and route strips; subtract obstacles; MinFilter(3) one-source-pixel safety erosion; accept only wholly allowed 150x150 cells; retain spawn four-neighbor component.'},
    'constraints':['Preserve common day/spring road, building footprint, bridge, stair and entrance coordinates.',
        'Keep the southern east planter as a navigation obstruction; no added festival prop may block established walkable ground.',
        'Polygon overlays are nominal coordinate transfers from old artwork, not proof of new geometry alignment.'],
    'alignmentAccepted':False,'newArtworkNavigationAccepted':False,'clientAcceptance':False,'formalAccepted':False,
    'newGeneratedImages':0,'newComplete4KTiles':0,
    'limitations':['The current 1254-square day layout differs from the old artwork named by the navigation source.',
        'Source polygons are historical constraints; a new shared structural reference and native-detail artwork still require visual/navigation checks.',
        'The local client runtime walkmask resource is absent; this reconstructs and verifies only the saved historical data.',
        'Preview enlarges reference pixels for diagnosis only; it is never production art.']}
savej(OUT/'navigation-contract.json',contract)

# Two identical layout crops make the nominal legacy-overlay comparison clear.
fontpath=Path('C:/Windows/Fonts/msyh.ttc')
font=lambda size:ImageFont.truetype(str(fontpath),size)
canvas=Image.new('RGB',(1240,850),'#f7f7f4');draw=ImageDraw.Draw(canvas)
draw.text((30,18),'r08_c09 | Historical navigation constraint review',font=font(25),fill='#172c37')
draw.text((30,58),'OLD NAVIGATION ONLY - NEW ART ALIGNMENT / ACCEPTANCE NOT VERIFIED',font=font(18),fill='#b12630')
draw.text((30,96),'Current day layout reference (enlarged QA crop)',font=font(18),fill='#172c37')
draw.text((650,96),'Same crop + old allowed / blocked polygons',font=font(18),fill='#172c37')
size=560; crop=layout.transform((size,size),Image.Transform.EXTENT,SOURCE_BOX,Image.Resampling.BICUBIC)
overlay=Image.new('RGBA',(size,size));od=ImageDraw.Draw(overlay)
for s in selected:
    pts=[(x/4096*size,y/4096*size) for x,y in s['tileLocalClippedVertices']]
    if len(pts)<3:continue
    allowed=s['kind']=='allowed_floor'; color=(29,176,131,28) if allowed else (228,47,61,120)
    od.polygon(pts,fill=color,outline=(15,138,107,230) if allowed else (204,28,45,255),width=3)
annotated=Image.alpha_composite(crop.convert('RGBA'),overlay).convert('RGB')
canvas.paste(crop,(30,135));canvas.paste(annotated,(650,135))
draw.rectangle((29,134,590,695),outline='#b2b8bb',width=1);draw.rectangle((649,134,1210,695),outline='#b2b8bb',width=1)
draw.text((30,710),'Source box: x 627..705.375, y 548.625..627 / 1254',font=font(17),fill='#263c47')
draw.text((30,742),'Whole map: [32768,28672,36864,32768) / 65536',font=font(17),fill='#263c47')
draw.text((650,710),'Green: legacy allowed floor; red: southern east planter',font=font(17),fill='#263c47')
draw.text((650,742),'Obstacle crosses this tile south/east boundary.',font=font(17),fill='#263c47')
draw.text((30,793),'QA visualization only. No production pixels, new map acceptance, or runtime asset changes.',font=font(18),fill='#b12630')
preview=OUT/'navigation-r08_c09-preview-only.png';canvas.save(preview)
derived={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),**info(preview,'derived QA visualization only'),
    'pixels':list(canvas.size),'operation':'Bicubic enlarge exact nominal 1254 layout crop, duplicate into comparison panels, render clipped historical polygons and labels.',
    'sourceLayout':sources[2],'navigationSource':sources[0],'sourceCropLTRB':list(SOURCE_BOX),
    'contract':info(OUT/'navigation-contract.json','coordinate and constraint evidence'),'script':info(Path(__file__),'reproducible QA derivation'),
    'aiGenerated':False,'model':None,'quality':None,'layoutUpscaledForPreviewOnly':True,'productionArtwork':False,
    'newArtworkAlignmentAccepted':False,'clientAcceptance':False,'visualInspection':'pending'}
savej(OUT/'navigation-r08_c09-preview-only.derived.json',derived)
print(json.dumps({'contract':str(OUT/'navigation-contract.json'),'preview':str(preview),'historicalMaskShaMatches':mask_matches,'polygons':[s['name'] for s in selected]},ensure_ascii=False))
