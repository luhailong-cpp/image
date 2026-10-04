from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl")
merged={}
for rel in ["attack-work/selection.json","attack-W-grounding-work/selection.json","run-E-grounding-work/selection.json","run-NE-work/selection.json"]:
 merged.update(json.loads((R/rel).read_text(encoding="utf-8"))["slots"])
xf={"attack/E":(53,160),"attack/W":(0,174),"run/E":(32,143),"run/NE":(-30,150)}
rows=[]
for slot,rel in merged.items():
 p=R/rel;im=Image.open(p);a=im.getchannel("A");bb=a.point(lambda v:255 if v>=32 else 0).getbbox();tx,ty=xf[slot.rsplit("/",1)[0]]; ob=[bb[0]*860/1254+tx,bb[1]*860/1254+ty,bb[2]*860/1254+tx,bb[3]*860/1254+ty]
 recp=Path(str(p)+".generation.json");rec=json.loads(recp.read_text(encoding="utf-8"))
 rows.append({"slot":slot,"file":rel,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"nativeSize":im.size,"mode":im.mode,"alphaExtrema":a.getextrema(),"bboxAlpha32":bb,"fixedExportBBox":ob,"mainContourInsideNative":bb[0]>0 and bb[1]>0 and bb[2]<im.width and bb[3]<im.height,"mainContourInsideExport":min(ob[:2])>=0 and max(ob[2:])<=1024,"generationRecord":str(recp.relative_to(R)).replace(chr(92),"/"),"modelEvidencePresent":all(k in rec for k in ["actualModel","actualQuality","submittedParameters","configSnapshot"])})
sha=[r["sha256"] for r in rows]
report={"checkedAtUtc":datetime.now(timezone.utc).isoformat(),"scope":"Selected attack24 (W04-08 grounding override), runE16, ownNE9. Final full196 export/dynamic integration owned by ROOT.","count":len(rows),"allNative1254":all(r["nativeSize"]==(1254,1254) for r in rows),"allTrueRGBA":all(r["mode"]=="RGBA" and r["alphaExtrema"]==(0,255) for r in rows),"uniqueSha":len(set(sha)),"issues":[r["slot"] for r in rows if not(r["mainContourInsideNative"] and r["mainContourInsideExport"] and r["modelEvidencePresent"])],"timing":{"run":{"frameMs":75,"cycleMs":1200,"uniform":True},"attack":{"frameMs":30,"cycleMs":360}},"staticVisualReview":"Feet axes, two-hand same-spear grips, complete spear ends, alternating run support/flight inspected in native files and contact sheets. Geometry does not replace normal-speed review.","remaining":["Final root exported sequence review, including E02→03 attack compression and W11 recovery.","NE15/16 both are short flight (soles1103/1102), do not label16 clearly lower descent.","Minor actual native attack sole variation retained; no per-frame grounding translation."],"frames":rows}
(R/"attack-work/closeout-audit-20261004.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="frames"},ensure_ascii=True))

