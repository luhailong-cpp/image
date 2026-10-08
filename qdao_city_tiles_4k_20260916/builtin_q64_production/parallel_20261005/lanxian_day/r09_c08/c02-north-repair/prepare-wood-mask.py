from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08/c02-north-repair')
im=Image.new('RGB',(1254,1254),(0,0,0));d=ImageDraw.Draw(im)
poly=[(700,627),(872,627),(872,857),(846,886),(818,873),(818,812),(793,790),(755,774),(755,677),(700,662)]
d.polygon(poly,fill=(255,255,255));p=R/'wood03-edit-mask1254.png';assert not p.exists();im.save(p)
(R/'wood03-mask.manifest.json').write_text(json.dumps({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'operation':'Technical edit selection mask only; white editable wood cap/upright, black protected. No artwork pixels.','polygonBoardXY':poly,'boardBoundaryY':627,'fixedNorthRows':[0,627],'nativeOffsetY':512,'originalSeatAndSupportProtected':True},indent=2))

