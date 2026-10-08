"""Prepare/record second-pass south joins; never touches either 4K output."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,shutil
from PIL import Image
R=Path(__file__).resolve().parent
T=R/'r07_c15';D=T/'repairs/unified/south-finishing'
STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(name):
 f=D/name;target=f/'input.png';m=read(str(target)+'.generation.json')
 assert sha(target)==m['sha256'] and not (f/'edited-native.png').exists()
 detail={'s1':'The thick cream rope, diagonal boat rim, curved barrel lid and barrel-lid board grooves currently jump at y627. Make their UPPER ends meet the exact positions, angles, widths and grain directions already visible in the unchanged lower half. Repair the barrel lid grooves and local brightness above the join; keep the barrel silhouette and lower groove endpoints fixed.',
 's2':'The blue-painted horizontal roof fascia and its thin light timber lip currently change height/slope at y627. Repaint ONLY their UPPER continuation to meet the fixed lower-half blue fascia and plank junctions. Use the lower-half exact diagonal slope and edge endpoints; no duplicate lip or new plank.',
 's3':'The broad diagonal wooden roof beam and adjacent blue canopy have a geometric offset across y627. Continue the lower-half beam width, edge angle and blue canopy corners upward into the upper repair area; the LOWER half is authoritative.',
 's4':'The cream rope and blue canopy wooden frame meet incorrectly at y627. The bottom-half wooden joint and canopy are the true structure. Rebuild their UPPER continuation so the rope ends at its existing attachment above, and the exact wooden frame and blue cloth meet the lower-half endpoints. Do not prolong a rope into the area where the existing lower image contains a wooden frame.'}[name]
 prompt='Use case: precise-object-edit. IMAGE1 is the exact1254x1254 edit target; IMAGE2 is the approved bright clean rounded hand-painted Q-style material reference only. This is a SECOND narrow repair of the straight horizontal collage seam at local y627. '+detail+' Treat pixels y627..1254 as a FIXED neighboring image: preserve every lower-half object boundary, board line, rope twist, highlight, hue and pixel position. Use them as the immutable stencil. Repaint only upper y280..626 as needed to connect onto that fixed lower edge. Preserve upper y0..150 exactly and keep y150..280 close to the input. The visible straight color/structure cut at y627 must disappear. Keep the same isometric camera, crop, object count and scale. Existing geometry already represents one coherent boat; repair the local joint, do not redesign it. No new objects, extra wood grooves, new rope, boat parts, ripples, white grids, texture noise, text, blur or border. Output opaque1254 square with no resizing.'
 refs=[{'file':str(target),'sha256':sha(target),'role':'native joint input; immutable lower half with recorded registration of upper prior repair'},
       {'file':str(STYLE),'sha256':sha(STYLE),'role':'approved hand-painted Q-style material only'}]
 (f/'prompt.txt').write_text(prompt,encoding='utf-8');save(f/'references.json',refs)
 print(json.dumps({'name':name,'prompt':prompt,'references':[v['file'] for v in refs]},ensure_ascii=False))
def record(name,source):
 f=D/name;src=Path(source);out=f/'edited-native.png';assert not out.exists()
 with Image.open(src) as im:im.load();assert im.size==(1254,1254)
 refs=read(f/'references.json');p=f/'prompt.txt'
 for r in refs:assert sha(r['file'])==r['sha256']
 shutil.copyfile(src,out)
 record={'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'format':'PNG',
 'generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin',
 'configSnapshot':read(R.parents[3]/'config/image-generation.json'),
 'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[r['file'] for r in refs]},
 'actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in interface exposes no model/quality selectors or returned version metadata.',
 'evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},
 'prompt':str(p),'promptSha256':sha(p),'references':refs,'resizedAfterGeneration':False,'finalArtUpscaled':False,
 'sourceRectXYXY':read(str(f/'input.png')+'.generation.json')['sourceRectXYXY'],
 'inputDerivationRecord':{'file':str(f/'input.png.generation.json'),'sha256':sha(f/'input.png.generation.json')},
 'intendedDestination':'r07_c15 upper half only; immutable r08_c15 not modified',
 'lowerHalfPixelIdentityNotAssumed':True,'integrationVisualReviewRequired':True}
 save(str(out)+'.generation.json',record);print(json.dumps({'file':str(out),'sha256':sha(out)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(sys.argv[2])
 elif sys.argv[1]=='record':record(sys.argv[2],sys.argv[3])

