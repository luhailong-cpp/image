from pathlib import Path
import sys
sys.dont_write_bytecode=True
from PIL import Image
import ai_helper as h
O=Path(__file__).resolve().parent
west=O.parents[2]/'tiles/current/region-v1/r09_c14-candidate.png'
right=O/'r09_c15-internal-candidate-v3.png'
joint=Image.new('RGB',(1254,4096));joint.paste(Image.open(west).convert('RGB').crop((3469,0,4096,4096)),(0,0));joint.paste(Image.open(right).convert('RGB').crop((0,0,627,4096)),(627,0))
p=O/'west-joint-source.png';joint.save(p);h.derived(p,[west,right],{'method':'integer native two-tile joint627each','jointSeamX':627,'globalOrigin':[56717,32768]})
for i,y in enumerate([0,1024,2048,2842],1):
 d=O/f'west-joint-source-{i}.png';joint.crop((0,y,1254,y+1254)).save(d);h.derived(d,[p],{'method':'native1254crop','origin':[0,y]})
