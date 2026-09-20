from PIL import Image
from pathlib import Path
D=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/lanxian_spring/triple_r08_c06_c08')
im=Image.open(D/'output_v2/extended-context.png')
for name,box in [('upper-outer-context-return',(7780,15,8834,330)),('bottom-outer-context-return',(7780,4000,8834,4311))]:
 f=D/'qa_v2'/f'{name}.png';assert not f.exists();im.crop(box).save(f)
