"""Prepare existing art as identity and gait references. Does not generate poses."""
import argparse,base64,hashlib,io,json
from pathlib import Path
from PIL import Image

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--character',required=True);a.add_argument('--direction',required=True,choices=['N','NE','E','SE','S','SW','W','NW']);v=a.parse_args()
 root=Path(__file__).resolve().parent;c=root/v.character;source=c/'source';idle=source/'idle.png';im=Image.open(idle).convert('RGBA');cw,ch=im.width//4,im.height//2;idx=['N','NE','E','SE','S','SW','W','NW'].index(v.direction);box=((idx%4)*cw,(idx//4)*ch,(idx%4+1)*cw,(idx//4+1)*ch);identity=im.crop(box);identity_file=source/f'identity-{v.direction}.png';identity.save(identity_file)
 size=443;guide=Image.new('RGBA',(4*size,2*size),(255,0,255,255));records=[]
 for j,n in enumerate([5,6,7,8,1,2,3,4]):
  f=root/'30_han_xiangzi'/'walk'/v.direction/f'{n:02}.png';frame=Image.open(f).convert('RGBA');guide.alpha_composite(frame.resize((size,size),Image.Resampling.LANCZOS),((j%4)*size,(j//4)*size));records.append({'output_phase':j+1,'source':str(f),'source_sha256':sha(f),'source_phase':n,'uniform_canvas_scale':size/512})
 guide_file=source/f'pose-guide-{v.direction}.png';guide.save(guide_file);meta={'purpose':'Two imagegen references; first identity, second pose only. Output character must be creatively redrawn by imagegen.','identity':{'source':str(idle),'source_sha256':sha(idle),'cell_box':box,'output':str(identity_file)},'gait':{'source_character':'30_han_xiangzi','phase_order':[5,6,7,8,1,2,3,4],'grid':[4,2],'file':str(guide_file),'sha256':sha(guide_file),'frames':records}};guide_file.with_suffix('.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
 for ref in [identity,guide]:
  b=io.BytesIO();ref.convert('RGB').save(b,format='JPEG',quality=92);print(base64.b64encode(b.getvalue()).decode())
if __name__=='__main__':main()
