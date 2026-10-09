from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/donghai_lantern")
D=ROOT/"r08_c15/repairs/hull-step-final"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {"file":str(p),"sha256":sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding="utf-8"))
c=read(D/"completion.json")
report={"reviewedAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"c14_shared_edge","completion":ref(D/"completion.json"),"base":c["base"],"native":c["native"],"nativeRecord":c["nativeRecord"],"mask":c["mask"],"patchedWindow":c["patchedWindow"],"status":"pass-local-repair","actualNativeViewed":True,"actualReferenceViews":[ref(D/"target.png"),ref(D/"day-geometry.png"),ref(Path("D:/work/image/designs/gameplay-ui/04-guild.png"))],"actualViews":[{**e,"actuallyViewed":True,"viewTool":"view_image","detail":"original"} for e in c["qa"]],"findings":["Frozen DAY 70ce623a has a continuous lower hull/waterline here; festival 908df2ad introduced the accidental short step.","The single generated native removes the notch and abrupt brown-to-blue splice while retaining boat direction, footprint, neighboring plank seams and warm reflection placement.","Final 48px local return shows smooth hull/water contact and continuous timber and water brushwork in full1254 and all four ROI returns.","All pixels outside nonzero mask are exactly unchanged from base; no full tile or DAY was edited."],"windowXYXY":c["windowXYXY"],"roisXYXY":c["roisXYXY"],"daySyncRequired":False,"geometryDisposition":"Restored existing DAY continuous tangent only within the small local defect; no scene relocation or overall footprint change.","formalAccepted":False}
rp=D/"qa/review.json";rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
Q=ROOT/"r08_c15/repairs/approved-sync/qa"
pink={"reviewedAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"c14_shared_edge","priorReview":ref(Q/"review-old16-repair-returns.json"),"candidate":c["base"],"issue":"lower-water-pink-sliver","classification":"non-structural local reflection color from insertion overlap","status":"classified-no-extra-repair","roiTileXYXY":[2140,3820,2340,4096],"actualViews":[{**ref(Q/(n+".png")),"actuallyViewed":True,"viewTool":"view_image","detail":"original"} for n in ("pink-sliver-final","pink-sliver-native","pink-sliver-day")],"findings":["Native d contains an ordinary gold reflection brushstroke; final overlap changes a narrow segment toward pink.","No object, shoreline, hull silhouette or connective map geometry is affected.","At the full1254 scale this remains a small reflection color variation; no additional generative edit is justified solely as a style preference."],"pixelEditsMade":False}
pp=Q/"lower-water-color-classification.json";pp.write_text(json.dumps(pink,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"completion":ref(D/"completion.json"),"review":ref(rp),"pinkClassification":ref(pp),"native":c["native"],"mask":c["mask"],"patchedWindow":c["patchedWindow"]}))

