from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from PIL import Image
Q=Path(__file__).resolve().parent
Z=Q.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'path':Path(p).as_posix(),'sha256':sha(p)}
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
    with Path(p).open('x',encoding='utf-8') as f: json.dump(d,f,ensure_ascii=False,indent=2)
idx=read(Z/'art-delivery-index.json')
orig=read(Q/'r11_c04-internal-native-art-audit-v1.json')
refs=read(Z/'native/r11_c04_riser_base_repair_v1.request.json')['references']
prompts=[(Z/'native/r11_c04_riser_base_repair_v1.prompt.txt').read_text(encoding='utf-8'), 'Use case: precise-object-edit. Image 1 is the exact local edit target, native 1254 by 1254 pixels. Repair the broken stone-to-sand bottom boundary of the UPPER broad stone stair riser. The lower-left stone face and its bottom edge are CORRECT; keep the entire left half, including its thickness and base position, absolutely unchanged. Near x620,y700 there is a sawtooth notch and a too-high stone base on the RIGHT. Extend the right-hand stone face DOWNWARD about 60 pixels into the sand so its lower edge continues the existing lower-left edge in one smooth straight diagonal, until it meets the right side wall/post. Remove the artificial horizontal stripe/double edge in this junction. Do not move the left bottom edge upward. Change only the right half of that first riser\'s lower edge and the immediately adjoining stone texture/shadow/sand, roughly x550-1000 y540-790. Keep its upper edge, step count, lower stairs, post, rope, original camera and every image outer edge unchanged. No other layout alteration. The other images are supporting style/layout references only. Same crisp hand-painted Daoist Q game-map stone and warm sand. No text, UI, people, watermark or grid. Opaque square, exact original framing.']
for v in [1,2]:
    p=Z/f'native/r11_c04_riser_base_repair_v{v}.png'
    with Image.open(p) as im: dims=list(im.size)
    assert dims==[1254,1254]
    write(Z/f'native/r11_c04_riser_base_repair_v{v}.generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tool':'image_gen__imagegen','model':None,'modelEvidence':'Actual model identifier not returned by built-in tool','paidApiUsed':False,'output':ref(p),'sha256':sha(p),'dimensions':dims,'references':[{**r,**ref(r['path'])} for r in refs],'prompt':prompts[v-1],'transparent_background':False,'selectionStatus':'not_selected_boundary_geometry_changed','review':'Central notch removed, but original lower-left edge raised about60px across left half; local replacement would transfer mismatch to patch boundary. Original 4096 candidate remains selected pending wider geometry repair.'})
for direction,other,first in [('west','r11_c03',True),('north','r10_c04',True),('east','r11_c05',False)]:
    n=next(t for t in idx['artAccepted'] if t['tile']==other)
    for r in [n['nativeContext'],n['sourceTrace'],n['artAudit'],orig['trace'],orig['context']]: assert sha(r['path'])==r['sha256']
    a={'tile':other,'context':n['nativeContext']}
    b={'tile':'r11_c04','context':orig['context']}
    write(Q/f'r11c04-{direction}-fresh-v1.manifest.json',{'outputPrefix':f'pair-r11c04-{direction}-fresh-v1','inputs':[a,b] if first else [b,a],'provenance':[orig['trace'],n['sourceTrace'],n['artAudit']]})
print('Created generation receipts and three neighbor pair manifests; original selected candidate remains unchanged.')
