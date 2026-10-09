from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
import numpy as np
from PIL import Image
import finish_r07_c15_south as rec
R=Path(__file__).resolve().parent;T=R/'r10_c16';D=T/'repairs/north-joint';STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(name):
 x={'n2':768,'n3':1792}[name];d=D/name;d.mkdir(parents=True,exist_ok=True);assert not (d/'edited-native.png').exists()
 north=R/'r09_c16/output/r09_c16.png';ext=R/'r09_c16/output/extended-context.png';base=T/'output/r10_c16.png'
 assert sha(north)=='75e40578e8c29233bd6b73fbf60a3ea0d7eec917769b93de51404ad34e99a5f9'
 assert sha(ext)=='ccf95c2bae623f71dc8d34a14a6cd7f23ad5000f0b8ad0c5499cb528ded279ed'
 assert sha(base)=='76171e89da5aa391e359c9c6095f3a09bf46912a8f876f0f4a059d6459b608e7'
 im=Image.new('RGB',(1254,1254));im.paste(Image.open(north).crop((x,3469,x+1254,4096)),(0,0));im.paste(Image.open(base).crop((x,0,x+1254,627)),(0,627));im.paste(Image.open(ext).crop((x+115,4211,x+1369,4326)),(0,627))
 im.save(d/'composition-reference.png');a=np.array(im.convert('RGBA'));a[742:1107]=0;Image.fromarray(a).save(d/'input.png')
 save(d/'input.png.generation.json',{'file':str(d/'input.png'),'sha256':sha(d/'input.png'),'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceRectXYXY':[x,-627,x+1254,627],'operation':'Exact north core627 plus true south halo115 and current lower tile; gap zeroes RGBA to remove false cut geometry. No resampling.','transparentRepairWindowXYXY':[0,742,1254,1107],'tileBoundaryLocalY':627,'sources':[{'file':str(p),'sha256':sha(p)} for p in [north,ext,base]],'resized':False})
 specific={'n2':'Continue the large existing vertical warm wooden pole and its attached pale hanging fabric/float from the authoritative upper context. The prior lower image incorrectly cut this broad upper object off and added a little false post top at the join. Do not create a second cap or a horizontal chopped end at the boundary. Connect each same object naturally to the matching existing lower timber or cloth, with unchanged endpoint positions and clean surfaces.', 'n3':'Continue the tall warm wooden upright from the upper anchor into the SAME lower upright. Its side edges and grain must be continuous and straight across the gap; no width jump, jog, ledge or horizontal cut. Preserve the smaller rounded post beside it as one separate existing post. Quiet cyan water continues around those exact silhouettes without tiny floating tan fragments.'}[name]
 prompt='Use case: precise-object-edit, fill missing native region. IMAGE1 is the edit target with a transparent horizontal gap y742..1106. IMAGE2 shows approximate object identities only in that gap, with a rejected old seam; IMAGE3 is the approved clean rounded bright Q-style materials. Fill the missing region to join the authoritative sharp UPPER anchor y0..741 to the fixed LOWER anchor y1107..1253. '+specific+' Upper pixels y0..741 include real accepted neighbor core and its actual continuation halo, so keep them unchanged in geometry, hue and dimensions. Preserve lower anchor and all object count, perspective, isometric camera and crop. Only repair the local connection. No new objects, rope, plank joints, decorations, ripples, foam, cells or grain. Do not add more detail to quiet water. Return one opaque native1254x1254 square, no zoom, blur, border or text.'
 (d/'prompt.txt').write_text(prompt,encoding='utf-8');refs=[{'file':str(p),'sha256':sha(p),'role':role} for p,role in [(d/'input.png','exact target with immutable north core and true halo'),(d/'composition-reference.png','approximate lower identities only; gap contains rejected joint geometry'),(STYLE,'approved materials only')]];save(d/'references.json',refs)
 print(json.dumps({'name':name,'prompt':prompt,'references':[x['file'] for x in refs]}))
def record(name,source):
 rec.D=D;rec.record(name,source);p=D/name/'edited-native.png.generation.json';j=rec.read(p);j['intendedDestination']='r10_c16 north core y0..627 only; r09_c16 immutable';j.pop('lowerHalfPixelIdentityNotAssumed',None);j['retainedAnchorPixelIdentityNotAssumed']=True;save(p,j)
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(sys.argv[2])
 elif sys.argv[1]=='record':record(sys.argv[2],sys.argv[3])
