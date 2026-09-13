"""Read-only extraction of identity and an already accepted single gait pose for imagegen."""
import argparse,base64,hashlib,io,json
from pathlib import Path
from PIL import Image

a=argparse.ArgumentParser();a.add_argument('--character',required=True);a.add_argument('--direction',required=True);a.add_argument('--phase',type=int,required=True);v=a.parse_args()
root=Path(__file__).resolve().parent;c=root/v.character;src=c/'source';im=Image.open(src/'idle.png').convert('RGBA');cw,ch=im.width//4,im.height//2;i=['N','NE','E','SE','S','SW','W','NW'].index(v.direction);identity=im.crop(((i%4)*cw,(i//4)*ch,(i%4+1)*cw,(i//4+1)*ch))
phase=[5,6,7,8,1,2,3,4][v.phase-1];f=root/'30_han_xiangzi'/'walk'/v.direction/f'{phase:02}.png';pose=Image.open(f).convert('RGBA');guide=Image.new('RGBA',pose.size,(255,0,255,255));guide.alpha_composite(pose)
meta={'purpose':'Identity and one accepted exact pose as imagegen references, not output art.','identity_source':str(src/'idle.png'),'identity_sha256':hashlib.sha256((src/'idle.png').read_bytes()).hexdigest(),'pose_source':str(f),'pose_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'phase':v.phase,'source_phase':phase}
(src/f'{v.direction}{v.phase:02}-references.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
for ref in [identity,guide]:
 b=io.BytesIO();ref.convert('RGB').save(b,format='JPEG',quality=93);print(base64.b64encode(b.getvalue()).decode())
