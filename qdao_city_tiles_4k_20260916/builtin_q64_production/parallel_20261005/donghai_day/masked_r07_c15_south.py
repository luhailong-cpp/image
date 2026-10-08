from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent;D=R/'r07_c15/repairs/unified';F=D/'south-masked';STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(name):
 x={'s1':0,'s2':1024,'s3':2048}[name];f=F/name;f.mkdir(parents=True,exist_ok=True)
 assert not (f/'edited-native.png').exists()
 source=D/'candidate.png';south=R/'r08_c15/output/r08_c15.png';ext=R/'r08_c15/output/extended-context.png'
 assert sha(source)=='0a677ad6deb2347659789f3c45a5055b1611ea0cffeff0d5a6e64c40e7df6a52'
 assert sha(south)=='70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585'
 im=Image.new('RGB',(1254,1254));im.paste(Image.open(source).crop((x,3300,x+1254,4096)),(0,0));im.paste(Image.open(south).crop((x,0,x+1254,458)),(0,796))
 im.paste(Image.open(ext).crop((x+115,0,x+115+1254,115)),(0,681));im.save(f/'composition-reference.png')
 a=np.array(im.convert('RGBA'));a[380:681,:,:]=0;Image.fromarray(a).save(f/'input.png')
 save(f/'input.png.generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'file':str(f/'input.png'),'sha256':sha(f/'input.png'),'sourceRectXYXY':[x,3300,x+1254,4554],'operation':'Exact native context crop with transparent rectangular AI repair window; no final art drawn procedurally.','transparentRepairWindowXYXY':[0,380,1254,681],'composition':{'file':str(f/'composition-reference.png'),'sha256':sha(f/'composition-reference.png')},'sources':[{'file':str(p),'sha256':sha(p)} for p in [source,south,ext]],'fixedContextStartsLocalY':681,'trueTileBoundaryLocalY':796,'resized':False})
 detail={'s1':'Continue the barrel lid curved edge and lid plank grooves upward from their EXACT lower-context positions. The diagonal boat rim and cream rope must meet the lower existing segments with equal width and slope. Do not simplify or add barrel lid boards.','s2':'Continue the exact blue-painted roof fascia and its thin pale wooden lip upward from the fixed bottom-context edges. The fascia slope, thickness and pale lip must align precisely at y681. Preserve existing board join and rope.','s3':'Continue the broad diagonal roof beam and canopy cloth upward from the authoritative lower context at y681. Preserve the exact beam width, straight angle, side-plane thickness, wood highlights and blue cloth edge endpoints.'}[name]
 prompt='Use case: precise-object-edit / fill missing region. IMAGE1 is the1254 square edit target with a transparent missing horizontal window at local y380..680. Fill ONLY that missing window to reconstruct a continuous existing boat. IMAGE2 is an approximate composition reference, with a faulty seam in that same band; use only for object identity. IMAGE3 is approved rounded bright clean Q-style material reference. All opaque pixels above y380 and below y681 are fixed anchors. '+detail+' The LOWER opaque context beginning at y681 is the authoritative geometry. Extend its boundaries into the missing band and join upper anchors. Do not move, repaint, rescale or warp any opaque context. Keep exact crop and camera. Add no objects, boards, rope, wood grains, fine ripples, white grids, text or frame. Output full opaque1254x1254, no resizing.'
 (f/'prompt.txt').write_text(prompt,encoding='utf-8')
 refs=[{'file':str(p),'sha256':sha(p),'role':role} for p,role in [(f/'input.png','masked native target; missing pixels only'),(f/'composition-reference.png','approximate identity guide; lower context authoritative'),(STYLE,'approved material style')]]
 save(f/'references.json',refs)
 print(json.dumps({'name':name,'prompt':prompt,'references':[r['file'] for r in refs]},ensure_ascii=False))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(sys.argv[2])
 elif sys.argv[1]=='record':
  import finish_r07_c15_south as f
  f.D=F;f.record(sys.argv[2],sys.argv[3])

