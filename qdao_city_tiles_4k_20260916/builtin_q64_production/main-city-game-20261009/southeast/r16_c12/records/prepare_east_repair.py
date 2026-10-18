from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent.parent;R=T/'repairs/east-ledge-20261016-v1';R.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
man=read(T/'repairs/blind-grout-20261016-v1/manifest.json');bp=Path(man['candidate']['path']);east=T.parent/'r16_c13/candidate/r16_c13-4k-orphan-repair-v2-20261013.png'
assert sha(east)=='b9310da8e5fe812e96bf5e9307dce0bab032e242d1641cae56ffaa646da04788'
im=Image.new('RGB',(1254,1254));im.paste(Image.open(bp).convert('RGB').crop((3034,0,4096,1254)),(0,0));im.paste(Image.open(east).convert('RGB').crop((0,0,192,1254)),(1062,0));target=R/'E01-target.png';im.save(target)
refs=read(T/'records/p04_01_v20261016T220807_7dc2fcba.request.json')['referenced_image_paths'][:3]
req={'prompt':'Use case: precise-object-edit. Native Taoist chibi daylight city-wall seam repair. Images 1/2/3 are approved reference only. Image4 LAST is the actual edit target, exactly1254x1254. It is a native seam pair: x0..1062 is THIS tile; x1062..1254 is the LOCKED actual east neighbor. Fix only the small top/rear-edge height mismatch of the horizontal stone cornice near y340..350 at the border x1062. The right locked top profile sits about 7 pixels lower than the left. In x650..1062,y320..395 gently continue the exact right profile leftwards to join the unchanged cornice on the far left. Preserve a single straight level ledge at the join; no abrupt step. Keep the existing vertical stone joint near x1055, the broad lower cornice face from y395..460 and its shadow below y460. All x1062..1254 must remain unchanged; all y0..192 must remain unchanged; every other stone joint, color, lighting, texture and object stays. No new joints, grout stubs, double edges, blur, text, UI or decoration. Output exactly1254x1254 opaque with original framing; do not reconstruct the full scene.','referenced_image_paths':refs+[str(target)],'transparent_background':False}
(R/'E01.request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
prep={'target':str(target),'targetSha256':sha(target),'base':man['candidate'],'baseContext':man['context'],'east':{'path':str(east),'sha256':sha(east)},'origin':[3034,0],'status':'prepared_not_generated'}
(R/'preparation.json').write_text(json.dumps(prep,indent=2),encoding='utf-8');print(json.dumps(req))

