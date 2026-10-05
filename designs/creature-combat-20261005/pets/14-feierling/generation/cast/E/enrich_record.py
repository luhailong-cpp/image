from pathlib import Path
import json,hashlib,sys
ROOT=Path("D:/work/image/designs/creature-combat-20261005/pets/14-feierling")
n=f"{int(sys.argv[1]):02}"
g=ROOT/"generation/cast/E"
p=g/(n+".generation.json")
data=json.loads(p.read_text(encoding="utf-8"))
receipt=json.loads((g/(n+".receipt.json")).read_text(encoding="utf-8"))
data["submittedParameters"]["referenced_image_paths"]=receipt["referenced_image_paths"]
data["generatedAt"]=receipt["returnedAt"]
data["generationStartedAt"]=receipt["startedAt"]
data["evidence"]["toolOutputHint"]=receipt["output_hint"]
if len(receipt["referenced_image_paths"])>3:
 r=Path(receipt["referenced_image_paths"][3])
 data["references"].append({"path":str(r),"role":"Cast E frame01 camera, scale, feet and identity continuity anchor", "sha256":hashlib.sha256(r.read_bytes()).hexdigest()})
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")

