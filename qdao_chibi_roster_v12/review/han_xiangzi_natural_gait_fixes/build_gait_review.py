from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np,json,hashlib,shutil
B=Path(r'E:\work\image\qdao_chibi_roster_v12\review\han_xiangzi_natural_gait_fixes')
DIRS=['N','NE','E','SE','S','SW','W','NW']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def metrics(p):
 a=np.asarray(Image.open(p).convert('RGB'));r,g,b=a[:,:,0].astype(int),a[:,:,1].astype(int),a[:,:,2].astype(int)
 mask=~((r>160)&(b>140)&(g<150)&((r-g)>65)&((b-g)>65))
 ys,xs=np.where(mask);dark=(np.max(a,axis=2)<112);widths=[]
 for y in range(65,200):
  xx=np.where(dark[y])[0]
  if len(xx)>20:widths.append(int(xx[-1]-xx[0]+1))
 return {'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'height':int(ys.max()-ys.min()+1),'dark_head_span_p90':float(np.percentile(widths,90))}
def matte(p,size=256):
 im=Image.open(p).convert('RGB');a=np.array(im);r,g,b=a[:,:,0].astype(int),a[:,:,1].astype(int),a[:,:,2].astype(int)
 a[(r>160)&(b>140)&(g<150)&((r-g)>65)&((b-g)>65)]=(45,50,57)
 return Image.fromarray(a).resize((size,size),Image.Resampling.LANCZOS)
records=[];contacts=Image.new('RGB',(4*256,4*284),(45,50,57));ct=ImageDraw.Draw(contacts)
for i,d in enumerate(DIRS):
 folder=B/'directions'/d;sel=json.loads((folder/'selection-pending.json').read_text(encoding='utf-8-sig'))
 out=B/'resolved-cells'/d;out.mkdir(parents=True,exist_ok=True)
 board=Image.new('RGB',(4*256,2*284),(45,50,57));draw=ImageDraw.Draw(board)
 for ph in range(1,9):
  p=f'{ph:02d}';orig=folder/'original'/(p+'.png');src=folder/sel[p]['cell'] if p in sel else orig
  assert Image.open(src).size==(443,443)
  dest=out/(p+'.png');shutil.copyfile(src,dest)
  m0,m1=metrics(orig),metrics(src)
  records.append({'direction':d,'source_phase':ph,'is_leg_edit':p in sel,'source':str(src),'sha256':sha(src),'before':m0,'after':m1,'head_span_change':m1['dark_head_span_p90']-m0['dark_head_span_p90'],'height_change':m1['height']-m0['height']})
  x=(ph-1)%4*256;y=(ph-1)//4*284;board.paste(matte(src),(x,y+28));draw.text((x+8,y+6),f'{d} src{p}'+(' EDIT' if p in sel else ' kept'),fill='white')
 board.save(folder/'selected-eight-before-phase-rotation.jpg',quality=91)
 for j,ph in enumerate((1,5)):
  x=(i%2*2+j)*256;y=i//2*284;contacts.paste(matte(out/f'{ph:02d}.png'),(x,y+28));ct.text((x+8,y+6),f'{d} original {ph:02d}',fill='white')
(B/'review').mkdir(exist_ok=True)
contacts.save(B/'review/contacts-01-05-before-rotation.jpg',quality=92)
(B/'review/selected-measurements.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(json.dumps({'selected':sum(r['is_leg_edit'] for r in records),'max_abs_head_span_delta':max(abs(r['head_span_change']) for r in records),'notable':[r for r in records if r['is_leg_edit'] and (abs(r['head_span_change'])>8 or abs(r['height_change'])>10)]},indent=2))

