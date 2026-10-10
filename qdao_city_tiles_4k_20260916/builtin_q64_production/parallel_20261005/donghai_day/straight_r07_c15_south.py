from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent;D=R/'r07_c15/repairs/unified';F=D/'south-straight';STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(name):
 x={'s2':1024,'s3':2048,'s4':2842}[name];f=F/name;f.mkdir(parents=True,exist_ok=True);assert not (f/'edited-native.png').exists()
 src=D/'refined/candidate.png';south=R/'r08_c15/output/r08_c15.png';ext=R/'r08_c15/output/extended-context.png'
 assert sha(src)=='965caba9070b2a41daa9b2c2b1e5ec1d292bfa3970965fe89d4f6ebb2ace3a40'
 assert sha(south)=='70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585'
 im=Image.new('RGB',(1254,1254));im.paste(Image.open(src).crop((x,3140,x+1254,4096)),(0,0));im.paste(Image.open(south).crop((x,0,x+1254,298)),(0,956));im.paste(Image.open(ext).crop((x+115,0,x+1369,115)),(0,841))
 im.save(f/'composition-reference.png');a=np.array(im.convert('RGBA'));a[230:841]=0;Image.fromarray(a).save(f/'input.png')
 save(f/'input.png.generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'file':str(f/'input.png'),'sha256':sha(f/'input.png'),'sourceRectXYXY':[x,3140,x+1254,4394],'operation':'Exact context crop, transparent broad gap removes rejected warped geometry; no painted guide lines.','transparentRepairWindowXYXY':[0,230,1254,841],'composition':{'file':str(f/'composition-reference.png'),'sha256':sha(f/'composition-reference.png')},'sources':[{'file':str(p),'sha256':sha(p)} for p in [src,south,ext]],'fixedContextStartsLocalY':841,'trueTileBoundaryLocalY':956,'resized':False})
 specific={
 's2':'The broad PALE GOLD front board immediately above the blue fascia is ONE SOLID WIDE WOODEN MEMBER already visible in the lower anchor. Continue it upward coherently. Do not add a narrow extra plank, dark gap or doubled board-tip border above the blue fascia. The central long roof plank terminates cleanly against this broad front member. All lower endpoints, slope and widths are authoritative. The preceding version had a blurred/double board tip: completely rebuild that tip inside the missing region with one crisp edge.',
 's3':'The broad diagonal roof beam is a STRAIGHT SOLID TIMBER with straight parallel long edges and straight long grain direction. Extrapolate its exact existing lower-anchor side planes UPWARD as straight lines. Reconstruct its upper rounded end cap at the same approximate location shown in the identity guide, but prioritize the straight beam continuing from the fixed lower anchor. NO wavy edge, curved beam, bending wood grain, S-shape, kink, skinny extra timber, or doubled outline. Preserve roof-board count and clear joins to this beam.',
 's4':'CRITICAL STRUCTURE: the lower blue-canopy WOOD FRAME is a STRAIGHT DIAGONAL TIMBER. Extend it UP-LEFT in a STRAIGHT LINE until it disappears BEHIND the broad main diagonal beam. It is NOT attached to the gray rope-anchor stone. Keep the cream rope and gray attachment as a separate existing rope fixture in their original approximate positions. There must be blue cloth between that rope fixture and the straight canopy frame. Delete the erroneous S-shaped dogleg wooden branch visible in IMAGE2; IMAGE2 is WRONG about that branch. The broad main beam must also stay STRAIGHT with straight grain, continuing the exact lower anchor. No bent/S-shaped frames, no new branch, no extra beam, no shifted lower joints.'}[name]
 prompt='Use case: precise-object-edit, fill missing region. IMAGE1 is the native1254 square target with a large transparent gap from y230 to840. IMAGE2 gives object identity and approximate upper placement but contains rejected bent geometry inside the gap; it is NOT a shape stencil there. IMAGE3 is approved rounded clean bright Q-style material only. Fill the transparent gap with a coherent continuation of the existing boat. The opaque LOWER context y841..1254 is the EXACT IMMUTABLE GEOMETRY STENCIL: preserve its pixels and extend its straight edges upward. '+specific+' Preserve the upper opaque anchor y0..230. Maintain same isometric camera, scale and crop. Keep every lower anchor at the same coordinate, color, width and angle. No new objects, extra fine grains, water ripples, grids, blur, lettering or border. Return opaque1254x1254. Do not resize or warp any retained context.'
 (f/'prompt.txt').write_text(prompt,encoding='utf-8');refs=[{'file':str(p),'sha256':sha(p),'role':role} for p,role in [(f/'input.png','native gap edit with immutable lower stencil'),(f/'composition-reference.png','approximate object identities only; rejected geometry inside gap'),(STYLE,'approved style')]];save(f/'references.json',refs)
 print(json.dumps({'name':name,'directory':str(f),'prompt':str(f/'prompt.txt'),'references':str(f/'references.json')}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(sys.argv[2])
 elif sys.argv[1]=='record':
  import finish_r07_c15_south as f
  f.D=F;f.record(sys.argv[2],sys.argv[3])

