from pathlib import Path
import sys,json,hashlib
from PIL import Image
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast");sys.path.insert(0,str(Z));from review_external_seams import Sources
T=Z/"r13_c11";Q=T/"qa"/"rockfoot-joint-20261016";Q.mkdir(exist_ok=False)
box=[41473,50573,42727,51827];S=Sources();im,parts,missing=S.extract(box);assert im is not None and not missing and im.size==(1254,1254)
p=Q/"input-native.png";im.save(p)
(Q/"input-native.derivation.json").write_text(json.dumps({"file":str(p),"globalBox":box,"sources":parts,"resamplingApplied":False,"classification":"AI edit input and QA only","sha256":hashlib.sha256(p.read_bytes()).hexdigest()},indent=2))
print(p)

