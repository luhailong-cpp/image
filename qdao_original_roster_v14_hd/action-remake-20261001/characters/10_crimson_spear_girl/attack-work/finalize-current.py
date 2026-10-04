from pathlib import Path
import json,hashlib,runpy
from datetime import datetime,timezone
from PIL import Image,ImageDraw
B=Path(__file__).parent
sel=json.loads((B/"selection.json").read_text())
sel["E"].update({"1":"attack-E-01-v2.png","12":"attack-E-12-v4.png"})
sel["W"]["6"]="attack-W-06-v2.png"
(B/"selection.json").write_text(json.dumps(sel,indent=2),encoding="utf-8")
for fn in ["audit.py","audit-current.py"]:
 p=B/fn;s=p.read_text(encoding="utf-8")
 s=s.replace("脸仍偏正面3/4，相对E02存在跳角，需修。","v2严格E侧起势，修正双眼正面相机；与E11/12固定头身尺度。")
 s=s.replace("v2已取消过头握位、收至胸腰、双脚收拢；站立高度比E11变化较大待复核。","v4沿E11相同头身尺寸与屈膝站距，仅闭口/收稳枪发；v2/v3站立高度过大弃用。")
 s=s.replace("接触关键帧，原生偏右、鞋底较高；禁止逐帧贴地。","v2侧面接触、双手握枪与两脚支撑明确；与W05同基线，W方向共同配准，不单帧下移。")
 s=s.replace("E02/E03/E06/E07/E12选v2，其余原版本。","E01/E02/E03/E06/E07/W06选v2，E12选v4，其余原版本。")
 s=s.replace("E01角度、E12站立高度变化和W06位置优先复核。","E01侧相机、E12尺寸突变、W06侧面握枪均已实际修订；仍须整段动态与共同方向配准。")
 p.write_text(s,encoding="utf-8")
runpy.run_path(str(B/"audit.py"),run_name="__main__")
html=(B/"preview.html").read_text(encoding="utf-8").replace("E02/E03/E06/E07/E12 用 v2","E01/E02/E03/E06/E07/W06 用 v2，E12 用 v4")
(B/"preview.html").write_text(html,encoding="utf-8")
for d in ["E","W"]:
 sheet=Image.new("RGB",(1600,1200),(45,55,65));dr=ImageDraw.Draw(sheet);sources=[]
 for i in range(12):
  p=B/sel[d][str(i+1)];im=Image.open(p).convert("RGBA").resize((380,380),Image.Resampling.LANCZOS);x=(i%4)*400+10;y=(i//4)*400+15;sheet.paste(im,(x,y),im);dr.text((x+8,y+5),f"{d} {i+1:02d}",fill="white")
  sources.append({"file":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"generationRecord":p.name+".generation.json"})
 out=B/f"contact-{d}.jpg";sheet.save(out,quality=94)
 (B/(out.name+".generation.json")).write_text(json.dumps({"file":out.name,"route":"mechanical-preview-only","sourceFiles":sources,"operation":"Full1254canvas resized380px into labeled contact sheet; no formal sprite exported","actualModel":None,"actualQuality":None},ensure_ascii=False,indent=2),encoding="utf-8")
obsolete=["attack-E-01.png","attack-E-02.png","attack-E-03.png","attack-E-07.png","attack-E-12.png","attack-E-12-v2.png","attack-E-12-v3.png","attack-W-06.png"]
clean=[]
selected={f for d in sel.values() for f in d.values()}
for fn in obsolete:
 p=(B/fn).resolve()
 if p.parent != B.resolve() or fn in selected:raise RuntimeError("Deletion boundary or current selection")
 if not p.exists():continue
 sha=hashlib.sha256(p.read_bytes()).hexdigest();rp=Path(str(p)+".generation.json");rec=json.loads(rp.read_text(encoding="utf-8"));rec.update(selection="superseded-or-rejected",imageRetained=False,cleanupReason="User keeps only current images; selected replacement persisted with complete provenance.");rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
 p.unlink();clean.append({"file":fn,"sha256":sha,"imageDeleted":True,"textProvenanceRetained":True})
for rp in B.glob("*.png.generation.json"):
 rec=json.loads(rp.read_text(encoding="utf-8"))
 for ref in rec.get("references",[]):ref["imageRetained"]=Path(ref["file"]).exists()
 if rec.get("editedFrom"):rec["editedFrom"]["sourceImageRetained"]=Path(rec["editedFrom"]["file"]).exists()
 rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
(B/"cleanup-20261003.json").write_text(json.dumps({"at":datetime.now(timezone.utc).isoformat(),"selectedImages":24,"deleted":clean},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"selected":24,"remainingPng":len(list(B.glob("*.png"))),"removed":len(clean)}))

