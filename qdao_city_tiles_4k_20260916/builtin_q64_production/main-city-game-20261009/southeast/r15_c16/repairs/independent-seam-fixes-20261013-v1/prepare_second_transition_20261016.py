from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent
O=D/'W01-second-bottom-transition-20261016';O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def js(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=D/'trial-v1/W01-west-capstone/composed-local-1254.png'
im=Image.open(src);im.save(O/'target-1254.png')
mark=im.copy();ImageDraw.Draw(mark).rectangle((627,750,780,869),outline=(255,0,255),width=3);mark.save(O/'target-marked.png')
prompt="Use case: precise-object-edit. Return a 1254 x 1254 opaque PNG at exactly this native framing and scale. Image 1 is the edit target, an actual assembled native game-map crop. Image 2 only marks the allowed repair rectangle; do not draw its magenta lines. Repair ONLY the tiny jagged double-step/notch on the lower diagonal shadow edge of the stone cap, around x646..690,y825..868 within the marked area x627..780,y750..870. Make that lower bevel/shadow contour a single clean continuous up-right diagonal connecting exactly to the unchanged existing edge immediately below y870 and to its upper-right continuation. Preserve the smooth cap top silhouette above it, the stone wall, and all existing legitimate grout. Do not introduce a new vertical block joint or protruding ledge. Keep rows y870..1253 and columns x0..626 exactly as the target: these are fixed neighboring artwork. Preserve native hand-painted stone detail and daylight shading without blur. No new object, ornament, plant, text, border, camera shift or resizing. Return the complete same image with this one very small contour repair only."
(O/'prompt.txt').write_text(prompt,encoding='utf-8')
request=dict(prompt=prompt,referenced_image_paths=[str(O/'target-1254.png'),str(O/'target-marked.png')],transparent_background=False)
js(O/'request.json',request)
js(O/'preparation.json',dict(schemaVersion=1,id='W01-second-bottom-transition',attempt=2,preparedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),route='builtin',actualModel=None,expectedNativeSize=[1254,1254],base=ev(D/'trial-v1/I01-blind-stone-grout/candidate-4096.png'),baseContext=ev(D/'trial-v1/I01-blind-stone-grout/context-4326.png'),target=ev(O/'target-1254.png'),targetParent=ev(src),references=[ev(O/'target-1254.png'),ev(O/'target-marked.png')],nativeCrop=[627,750,780,870],destinationCoreBox=[0,3592,153,3712],protectedCoreBox=[0,3712,4096,4096],request=ev(O/'request.json'),prompt=ev(O/'prompt.txt'),formalAccepted=False))
print(json.dumps(dict(request=str(O/'request.json'),target=str(O/'target-1254.png'))))

