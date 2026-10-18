from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
base=Z/'tiles/connected-r05-r06-cross-v5/r06_c04_rail-ground-v1_4096.png'
d=Z/'qa/r06_c04_southmid_grout_a02_upper_reuse_mask_20261016_v1'
current=np.array(Image.open(base).convert('RGB'))[2842:4096,1421:2675]
target=np.array(Image.open(Z/'guides/r06_c04_southmid_grout_a02.native-crop.png').convert('RGB'))
repair=np.array(Image.open(Z/'native/r06_c04_southmid_grout_a02.png').convert('RGB'))
mask=np.array(Image.open(d/'source_selection_mask.png'))==255
assert np.array_equal(current[mask],target[mask]),'Selected pixels overlap newer repair'
result=current.copy();result[mask]=repair[mask]
p=d/'combined_current_v5_native_crop.png';assert not p.exists();Image.fromarray(result).save(p)
print(json.dumps({'currentCombined':str(p),'selectedPixels':int(mask.sum()),'selectedPixelsUnchangedVsOriginalEditTarget':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))

