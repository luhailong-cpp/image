from pathlib import Path
from PIL import Image
import sys,json
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest');sys.path.insert(0,str(Z));import production_v2 as p
T=Z/'r04_c06';f=Z/'r05_c06/candidate/r05_c06-candidate-minimum-error-03d4dd9f7332.png'
out=T/'layout-only/actual-south-context-s04_01.png';p.save_png(out,Image.open(f).convert('RGB').crop((0,0,1254,1254)))
p.write_json(out.with_suffix('.png.derivation.json'),{'source':str(f),'sourceSha256':p.sha(f),'sourceCrop':[0,0,1254,1254],'worldBox':[20480,16384,21734,17638],'resampled':False,'role':'actual neighbor context only'})
print(str(out))

