"""Deterministic native crops of existing, once-generated clean skins; no AI calls."""
from pathlib import Path
from PIL import Image, ImageOps
import json, hashlib, uuid, datetime
from collections import deque

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'staged/Assets/Resources/UI/Ugui/GameplayFidelity20261016'
OUT.mkdir(parents=True, exist_ok=True)
sources = {name: Image.open(ROOT/'assets'/f'{name}-clean-skin.png').convert('RGB') for name in ('inventory', 'quests', 'activities')}
rows = []

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def sprite(name, image, source, rect=None, operation='native crop'):
    path = OUT/f'{name}.png'
    image.save(path)
    meta = f'''fileFormatVersion: 2
guid: {uuid.uuid5(uuid.NAMESPACE_URL, 'qdao-gameplay-fidelity-20261016/'+name).hex}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
  isReadable: 0
  streamingMipmaps: 0
  textureFormat: 1
  maxTextureSize: 4096
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  compressionQuality: 100
  spriteMode: 1
  spriteExtrude: 0
  spriteMeshType: 0
  alignment: 0
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: 100
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 0
  alphaUsage: 1
  alphaIsTransparency: 1
  textureType: 8
  textureShape: 1
  platformSettings:
  - serializedVersion: 4
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 4096
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 100
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID: {uuid.uuid5(uuid.NAMESPACE_DNS, 'qdao-'+name).hex}
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
  userData: Gameplay fidelity native crop 20261016
  assetBundleName:
  assetBundleVariant:
'''
    Path(str(path)+'.meta').write_text(meta, encoding='utf-8')
    rows.append(dict(name=name,source=f'assets/{source}-clean-skin.png',source_sha256=sha(ROOT/'assets'/f'{source}-clean-skin.png'),source_rect=rect,operation=operation,size=list(image.size),sha256=sha(path)))

def crop(name, source, rect): sprite(name,sources[source].crop(rect),source,list(rect))

def menu_icon(name, rect):
    image=sources['activities'].crop(rect).convert('RGBA')
    pixels=image.load(); w,h=image.size; queue=deque(); seen=set()
    # Remove only the paper/jade background connected to the crop boundary;
    # enclosed white areas of the taiji glyph remain part of the icon.
    def background(p):
        r,g,b,a=p
        return (r>170 and g>158 and b>130 and max(r,g,b)-min(r,g,b)<75) or (g>r*1.12 and g>b*1.05 and r<105 and g<150)
    for x in range(w): queue.extend(((x,0),(x,h-1)))
    for y in range(h): queue.extend(((0,y),(w-1,y)))
    while queue:
        x,y=queue.popleft()
        if (x,y) in seen or not (0<=x<w and 0<=y<h): continue
        seen.add((x,y))
        if not background(pixels[x,y]): continue
        pixels[x,y]=(0,0,0,0)
        queue.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
    sprite(name,image,'activities',list(rect),'native ornament crop with boundary-connected background alpha extraction')

# Full-canvas art remains one uniform-scale native image. Only areas that become
# real scrolling controls are cleared with small pieces of that same paper.
# Texture tiling never reintroduces the source's baked slots/selected highlight.
for source, areas in {
    'inventory': [(175,166,1160,697),(182,91,1165,163)],
    'quests': [(164,169,770,669),(190,90,721,164),(1101,124,1230,182),(841,316,1751,458),(843,475,1502,665),(854,684,1157,742)],
    'activities': [(519,155,1776,654),(163,94,486,529),(794,685,1451,734)]
}.items():
    base=sources[source].copy()
    # Same-source blank paper, clear of separators, badges, slot outlines and text.
    tile=sources[source].crop((1290,100,1354,164))
    for x0,y0,x1,y1 in areas:
        for y in range(y0,y1,64):
            for x in range(x0,x1,64):
                piece=tile
                if ((x-x0)//64)%2: piece=ImageOps.mirror(piece)
                if ((y-y0)//64)%2: piece=ImageOps.flip(piece)
                base.paste(piece.crop((0,0,min(64,x1-x),min(64,y1-y))),(x,y))
    sprite(source+'-frame',base,source,operation='native skin with baked dynamic cards cleared using same-source paper tile; no resize')

crop('bag-slot','inventory',(376,174,563,312))
crop('bag-slot-selected','inventory',(178,169,370,316))
crop('bag-tab-selected','inventory',(190,92,444,160))
crop('bag-tab-normal','inventory',(447,92,683,160))
crop('bag-button-normal','inventory',(1235,678,1445,746))
crop('bag-button-primary','inventory',(1459,673,1767,754))
crop('bag-sort','inventory',(1005,700,1163,754))
crop('mission-row-selected','quests',(166,171,769,267))
crop('mission-row','quests',(166,273,769,368))
crop('mission-tab-selected','quests',(191,91,458,160))
crop('mission-tab','quests',(456,91,720,161))
crop('mission-badge','quests',(1102,127,1228,179))
crop('mission-button-normal','quests',(1190,678,1454,749))
crop('mission-button-primary','quests',(1462,672,1778,754))
crop('activity-card','activities',(522,159,932,654))
for name,rect,fill_rect in [('activity-nav-selected',(166,95,485,201),(285,116,317,148)),('activity-nav',(166,207,485,309),(295,230,327,262))]:
    panel=sources['activities'].crop(rect)
    tile=sources['activities'].crop(fill_rect)
    for area in [(19,10,115,panel.height-10),(255,10,panel.width-9,panel.height-10)]:
        x0,y0,x1,y1=area
        for y in range(y0,y1,32):
            for x in range(x0,x1,32): panel.paste(tile.crop((0,0,min(32,x1-x),min(32,y1-y))),(x,y))
    sprite(name,panel,'activities',list(rect),'native nav skin with baked icon/check cleared for live selection')
menu_icon('activity-menu-scroll',(190,109,270,190))
menu_icon('activity-menu-taiji',(185,215,273,300))
menu_icon('activity-menu-hourglass',(189,322,271,405))
menu_icon('activity-menu-lantern',(189,432,271,520))
crop('activity-button','activities',(563,571,890,637))
crop('activity-icon-frame','activities',(540,175,710,352))
crop('activity-badge-green','activities',(723,235,836,280))
crop('activity-badge-blue','activities',(1140,235,1255,280))
crop('activity-badge-pink','activities',(1562,235,1674,280))

manifest=dict(schema='qdao.gameplay.fidelity.native-slices.v1',clean_canvas=[1932,814],original_design_canvas=[1931,814],sprites=rows,import_settings=dict(textureType='Sprite',spriteMode='Single',meshType='FullRect',textureCompression='Uncompressed',pixelsPerUnit=100,mipmaps=False,maxTextureSize=4096),asset_postprocessor=False)
(ROOT/'slice-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for stale in ('activity-nav-hourglass','activity-nav-lantern'):
    for suffix in ('.png','.png.meta'):
        candidate=(OUT/(stale+suffix)).resolve()
        if candidate.parent == OUT.resolve() and candidate.exists(): candidate.unlink()
originals={'inventory':'02-inventory.png','quests':'01-quests.png','activities':'03-activities.png'}
for name, original in originals.items():
    clean=ROOT/'assets'/f'{name}-clean-skin.png'
    record=dict(schema='qdao.image-generation-record.v1',asset=str(clean.relative_to(ROOT)),operation='one built-in image edit reported successful by previous agent before reboot',configuration_target=json.loads((ROOT.parents[2]/'config/image-generation.json').read_text(encoding='utf-8-sig')),submitted_model=None,submitted_quality=None,actual_model='unconfirmed: tool response not retained before reboot',actual_quality='unconfirmed: tool response not retained before reboot',time_evidence=dict(file_mtime_utc=datetime.datetime.fromtimestamp(clean.stat().st_mtime,datetime.timezone.utc).isoformat(),precision='filesystem evidence only, not exact generation time'),source=dict(path='../'+original,sha256=sha(ROOT.parent/original),native_size=list(Image.open(ROOT.parent/original).size)),output=dict(native_size=list(sources[name].size),sha256=sha(clean)),prompt=f'{name}-clean-skin.prompt.txt',evidence_limitations='Parent agent reports exactly one successful built-in cleaning edit per image. Tool returned model/quality/response and precise submission time were not persisted before reboot. Current config is target only, never evidence of actual parameters. No repeat generation performed in resume.')
    (ROOT/f'{name}-clean-skin.record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(rows)} native sprites and explicit import metadata written to {OUT}')
