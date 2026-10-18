from pathlib import Path
import json, hashlib, datetime
import numpy as np
from PIL import Image
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p): return {"path":str(p).replace(chr(92),"/"),"sha256":sha(p)}
lower=Z/"qa/r03_c01_lower_cliff_edge_20261016_a01_mask_v2/mask_selection.json"
water=Z/"qa/r03_c01_upper_water_pair_masks_20261016_v1/derivation.json"
a=json.loads(lower.read_text(encoding="utf-8")); b=json.loads(water.read_text(encoding="utf-8"))
for k in ("target","repair","mask","combinedCrop"):
    assert sha(a[k]["path"])==a[k]["sha256"],k
for item in b["outputMasks"]+[b["reviewCrop"]]:
    assert sha(item["path"])==item["sha256"], item["path"]
t=np.array(Image.open(a["target"]["path"]).convert("RGB")); r=np.array(Image.open(a["repair"]["path"]).convert("RGB")); m=np.array(Image.open(a["mask"]["path"]).convert("L")); c=np.array(Image.open(a["combinedCrop"]["path"]).convert("RGB"))
assert set(np.unique(m)).issubset({0,255})
assert np.array_equal(np.where((m==255)[:,:,None],r,t),c)
q={
"schemaVersion":1,"reviewer":"/root/connected_continuation","createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
"reviewMethod":"Actual original-resolution view_image inspection; no resizing, no montage-based inference.",
"scope":"Two precisely pinned existing QA images only; not a 33-crop or whole-tile closure.",
"items":[
{"id":"lower_cliff_edge_a01_mask_v2","viewed":a["combinedCrop"],"size":list(Image.open(a["combinedCrop"]["path"]).size),"mask":a["mask"],"maskRecord":pin(lower),"raw":a["repair"],"target":a["target"],"nativeSameCoordinateReplayPassed":True,"geometryStatus":"PASS","note":"Complete 1254 crop viewed. Central channel rock edges and white water remain continuous from upper to lower crop; no new obvious geometric notch or split along the selected-region boundaries. This independently accepts the scoped lower cliff repair."},
{"id":"upper_water_pair_overlap","viewed":b["reviewCrop"],"size":list(Image.open(b["reviewCrop"]["path"]).size),"masks":b["outputMasks"],"derivation":pin(water),"geometryStatus":"PASS","note":"Actual 550 x 700 overlap review crop viewed. Water ripple network joins without an obvious straight cut, doubled edge, or geometric discontinuity in this inspected join. Scope is this overlap crop, not the entire two repaired 1254 regions."}
],
"materialStatus":"NOT_FULLY_ASSESSED","internalGeometryClosurePassed":False,"internalClosurePassed":False,"formalPassed":False
}
out=Z/"qa/r03_c01_second_batch_two_crops_independent_connected_20261016.json"
assert not out.exists()
out.write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(pin(out)))

