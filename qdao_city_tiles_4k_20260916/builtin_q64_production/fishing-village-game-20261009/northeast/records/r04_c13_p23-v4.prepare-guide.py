import json,hashlib
from pathlib import Path
from PIL import Image
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role): return {"path":str(p).replace("\\","/"),"sha256":sha(p),"role":role}
p="r04_c13_p23"
source=Z/"native"/(p+"-v1.png")
a=Image.open(source).convert("RGB")
g=Image.new("RGB",(1254,1254))
segments=[([0,0,230,1254],[0,0,230,1254]),([230,0,600,1254],[230,0,535,1254]),([600,0,890,1254],[535,0,850,1254]),([890,0,1254,1254],[850,0,1254,1254])]
for s,d in segments:
 cut=a.crop(s)
 if cut.size!=(d[2]-d[0],d[3]-d[1]): cut=cut.resize((d[2]-d[0],d[3]-d[1]),Image.Resampling.BICUBIC)
 g.paste(cut,d[:2])
plan=json.loads((Z/"records"/(p+".plan.json")).read_text())
for edge in plan["nativeEdgeSources"]:
 g.paste(Image.open(edge["path"]).convert("RGB").crop(edge["cropBox"]),edge["pasteAt"][:2])
out=Z/"guides"/(p+"-v4.geometry-corrected-guide.png")
assert not out.exists()
g.save(out)
d={"purpose":"NONFINAL generation geometry guide only. Horizontally remap target geometry then restore exact native edge anchors. Never final art; output must be freshly generated native1254.", "source":ref(source,"failed native target used as visual guide only"),"segments":segments,"operation":"piecewise horizontal BICUBIC guide remap only, then exact neighbor strips","nativeEdgeSources":plan["nativeEdgeSources"],"resampled":True,"finalArt":False}
Path(str(out)+".derived.json").write_text(json.dumps(d,indent=2)+"\n")
plan["references"]=plan["references"][:3]+[ref(out,"geometry-corrected guide only; never final pixels")]
plan["repairTarget"]=ref(source,"preserved failed target")
plan["repairGuide"]=ref(out,"corrected geometry guide")
plan["attemptContext"]="Concentrated repair after completing independent p44/p34; previous v2/v3 no improvement preserved."
assert not (Z/"records"/(p+"-v4.plan.json")).exists()
(Z/"records"/(p+"-v4.plan.json")).write_text(json.dumps(plan,indent=2)+"\n")
print(json.dumps({"guide":str(out),"sha256":sha(out)}))

