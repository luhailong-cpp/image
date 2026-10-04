from pathlib import Path
from PIL import Image
import json,hashlib,sys
from datetime import datetime,timezone
B=Path(sys.argv[1]).resolve();stem=sys.argv[2]
req=json.loads((B/(stem+".request.json")).read_text(encoding="utf-8"))
p=B/(stem+".native.png");im=Image.open(p).convert("RGBA")
cfg=json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
refs=[{"file":f,"sha256":sha(Path(f)),"role":"Explicit input role stated in saved prompt"} for f in req["referenced_image_paths"]]
record={"file":p.name,"sha256":sha(p),"generatedAt":datetime.now(timezone.utc).isoformat(),"width":im.width,"height":im.height,"mode":im.mode,"format":"PNG","route":"builtin","tool":"image_gen.imagegen","configSnapshot":cfg,"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":req["referenced_image_paths"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"Host-managed builtin tool does not expose model/quality parameters or confirmed response metadata.","prompt":stem+".prompt.txt","evidence":{"receipt":stem+".receipt.json"},"references":refs,"editedFrom":refs[0],"alphaExtrema":im.getchannel("A").getextrema(),"status":"generated-pending-visual-review","outputScalePolicy":"full-canvas-to1024-no-translation"}
(B/(p.name+".generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
out=B/(stem+".png")
assert min(im.size)>=1024 and im.width==im.height
im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
derived={"file":out.name,"sha256":sha(out),"width":1024,"height":1024,"mode":"RGBA","operation":"uniform full canvas resize to1024, no translation/crop/bbox fit/individual grounding","outputScalePolicy":"full-canvas-to1024-no-translation","derivedFrom":{"file":p.name,"sha256":sha(p),"generationRecord":p.name+".generation.json"},"actualModel":None,"actualQuality":None,"sourceConfigSnapshot":cfg,"unverifiedReason":record["unverifiedReason"],"status":"derived-pending-visual-review"}
(B/(out.name+".generation.json")).write_text(json.dumps(derived,ensure_ascii=False,indent=2),encoding="utf-8")
a=Image.open(out).getchannel("A");print(json.dumps({"file":out.name,"nativeSize":im.size,"sha256":sha(out),"bbox32":a.point(lambda v:255 if v>=32 else 0).getbbox(),"alpha":a.getextrema()}))

