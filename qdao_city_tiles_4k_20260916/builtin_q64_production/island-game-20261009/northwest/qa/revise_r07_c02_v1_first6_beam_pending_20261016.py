from pathlib import Path
import json,hashlib,datetime
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
p=Z/"qa/r07_c02_v1_first6_independent_connected_20261016.json"
d=json.loads(p.read_text(encoding="utf-8"))
d["supersedes"]={"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
d["createdAtUtc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
for c in d["crops"]:
 if c["review"]["i"] in (2,5):
  c["review"]["geometry"]="PENDING_REPAIR"
  c["review"]["note"]="Short step/join visible on the lower edge of the red wall beam near tile (3072,1040). Initially read as a timber joint, but owner independently identified the same localized stair-step and is repairing it. Keep pending until the repaired pixels and full mask boundary are reviewed."
d["geometryPassedCount"]=4
d["geometryPendingCount"]=2
d["reviewedCount"]=6
d["coordinationEvidence"]={"sender":"/root/west_continuation","note":"Owner viewed 24/33 and identified this exact same red beam lower edge step as the only geometry repair point so far."}
out=Z/"qa/r07_c02_v1_first6_independent_connected_20261016_v2.json"
assert not out.exists()
out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"path":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest()}))

