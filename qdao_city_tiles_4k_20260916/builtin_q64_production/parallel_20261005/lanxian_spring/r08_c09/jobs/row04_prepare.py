"""Prepare/read/save only the assigned row04 c03/c04 artifacts."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
from PIL import Image

T=Path(__file__).resolve().parents[1]
R=T.parents[4]
D=T.parent.parent/'lanxian_day/r08_c09'
REPO=Path('D:/work/image')
STYLE=REPO/'designs/gameplay-ui/04-guild.png'
SPRING=REPO/'qdao_city_tiles_4k_20260916/builtin_q64_all_city_references/lanxian_spring/map-native-layout-reference.png'
C08=REPO/'qdao_city_tiles_4k_20260916/builtin_q64_production/lanxian_spring/triple_r08_c06_c08/output_v2/r08_c08.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()

def reference():
    assert sha(C08)=='7b68b30caedcede54610718bf93dca4d1bef4513d4423a58dbd82f24f7250de4'
    target=T/'guides/row04-spring-c08-native-detail.png'
    target.parent.mkdir(parents=True,exist_ok=True)
    Image.open(C08).crop((0,2842,1254,4096)).save(target)
    write(Path(str(target)+'.derivation.json'),{'file':str(target),'sha256':sha(target),'pixels':[1254,1254],
        'source':str(C08),'sourceSha256':sha(C08),'sourceCropLTRB':[0,2842,1254,4096],
        'operation':'native pixel crop without resizing','role':'nearby spring red-lacquer planter material only, not target geometry'})
    print(json.dumps({'reference':str(target)}))

def prepare(cell):
    assert cell in ['r04_c03','r04_c04']
    target=D/'native'/f'{cell}.png';rec=Path(str(target)+'.generation.json')
    assert target.is_file() and rec.is_file(), 'day native dependency missing'
    assert sha(target)==read(rec)['sha256'], 'day dependency SHA mismatch'
    with Image.open(target) as im:assert im.size==(1254,1254)
    refs=[{'path':str(target),'role':'EDIT TARGET: native day patch; sole authoritative geometry, unchanged paving/foliage/shadows'},
          {'path':str(T/'guides/row04-spring-c08-native-detail.png'),'role':'nearby spring planter red lacquer and warm gold material only; do not copy geometry'},
          {'path':str(STYLE),'role':'user-confirmed primary painting style only; no UI/text/objects'},
          {'path':str(SPRING),'role':'town Spring Festival accent restraint only; not geometry or production pixels'}]
    overlap=''
    if cell=='r04_c04':
        west=T/'native/r04_c03.png';assert west.is_file()
        context=T/'guides/row04-c04-west-overlap.png'
        Image.open(west).crop((1024,0,1254,1254)).save(context)
        write(Path(str(context)+'.derivation.json'),{'file':str(context),'sha256':sha(context),'source':str(west),'sourceSha256':sha(west),'sourceCropLTRB':[1024,0,1254,1254],'pixels':[230,1254],'operation':'native pixel overlap crop; no resizing','role':'matches target left230px; retain contour and restrained surface colors'})
        refs.append({'path':str(context),'role':'EXACT WEST OVERLAP: this230x1254 crop corresponds to target x0..230,y0..1254; coordinates/colors/contours must attach without doubled edges'})
        overlap=' Image5 is the exact230x1254 west overlap corresponding to target x=0..230 at unchanged y: continue the red/gold material choices consistently and keep shared foliage/rail contours at these same positions. Do not enlarge or reinterpret this narrow reference.'
    prompt='''Use case: precise-object-edit. EDIT IMAGE1 ONLY into a restrained Spring Festival appearance. This is a1254x1254 native game-map detail patch: return the same opaque square, identical framing, scale, camera and geometry. Preserve every ground pixel appearance, stone slab edge, grout, bevel, trunk contour, green leaf cluster, shrub, soil, shadow footprint, pole footprint and existing structural shape. Change ONLY the existing wooden planter rim/wooden railing surface to modest clean vermilion red lacquer, with very narrow warm-gold accents on existing cap/edge surfaces. Retain white stone posts as white; use gold only on existing small cap trim if present. Match Image2 nearby spring planter material while keeping Image1 geometry. Do not color the tree trunk red. Do not add any new lanterns, hanging ropes, ribbons, tassels, posts, flowers, coins, banners, ornaments, snow, confetti or petals. No new entity or occupied ground. Do not paint or decorate any paving, leaves or shadow. Unmodified stone and foliage must remain as close to Image1 as possible with no added texture, changed illumination or recolored ground. Image3 supplies the user-confirmed PRIMARY bright clean rounded Daoist Q-style hand-painted material finish ONLY: copy no UI, text, bunny, foliage, frame or object from it. Image4 is Spring Festival color restraint only, not geometry. Do not copy its structures. The image must remain a close edit of Image1 with minimal surface-color substitutions, no overall restyling or new scenery. Keep every clipped contour exiting the canvas in exactly the same place. No border, text, watermark, blur, rescaling, sharpening or extra shadows.'''+overlap
    jobs=T/'jobs';pf=jobs/f'{cell}.row04.prompt.txt';pf.write_text(prompt,encoding='utf-8')
    refsfile=jobs/f'{cell}.row04.references.json';write(refsfile,refs)
    req={'prompt':prompt,'referenced_image_paths':[r['path'] for r in refs],'transparent_background':False}
    write(jobs/f'{cell}.row04.request.json',req)
    write(jobs/f'{cell}.row04.source.json',{'cell':cell,'daySource':str(target),'daySourceSha256':sha(target),'dayGenerationRecord':str(rec),'dayGenerationRecordSha256':sha(rec),'verifiedAtUtc':now(),'crossAppearanceGeometryAccepted':False,'nativePixels':[1254,1254],'core':[115,115,1139,1139]})
    print(json.dumps({'cell':cell,'request':str(jobs/f'{cell}.row04.request.json'),'daySha':sha(target)},ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['reference','prepare']);ap.add_argument('cell',nargs='?');a=ap.parse_args()
    reference() if a.action=='reference' else prepare(a.cell)
