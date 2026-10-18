import sys
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
import west_sol as w
from PIL import Image
q=w.Z/'qa/west_sol/r07_c11_p34-v4';src=w.Z/'native/r07_c11_p34-v4-west_sol.png';im=Image.open(src).convert('RGB')
for side,pid in [('left','r07_c11_p33'),('bottom','r07_c11_p44')]:
 other=w.own_selection('r07_c11')[pid];ni=Image.open(other['path']).convert('RGB');out=Image.new('RGB',(256,1254) if side=='left' else (1254,256))
 if side=='left':out.paste(ni.crop((1011,0,1139,1254)),(0,0));out.paste(im.crop((115,0,243,1254)),(128,0))
 else:out.paste(im.crop((0,1011,1254,1139)),(0,0));out.paste(ni.crop((0,115,1254,243)),(0,128))
 f=q/(side+'.native-1to1.png');out.save(f);w.write(q/(side+'.check.json'),dict(sources=[w.ref(src),other],output=w.ref(f),seam=128,operation='Exact integer native crop/paste QA'))

