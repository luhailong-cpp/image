from pathlib import Path
from PIL import Image
import json, hashlib
from datetime import datetime, timezone, timedelta
ROOT=Path(__file__).parent
CONFIG=json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig"))
def register(stem):
 p=ROOT/(stem+".png"); im=Image.open(p); req=json.loads((ROOT/(stem+".request.json")).read_text(encoding="utf-8"))
 alpha=im.getchannel("A") if im.mode=="RGBA" else None
 record={"file":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"generatedAt":datetime.fromtimestamp(p.stat().st_mtime,timezone(timedelta(hours=-4))).isoformat(),"generatedAtEvidence":"PNG file mtime preserved from builtin output; timezone America/New_York UTC-04:00","width":im.width,"height":im.height,"format":im.format,"mode":im.mode,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":CONFIG,"submittedParameters":{"model":None,"quality":None,"transparent_background":req["transparent_background"],"referenced_image_paths":req["referenced_image_paths"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露／无可核实元数据","evidence":{"receipt":stem+".receipt.json"},"prompt":stem+".prompt.txt","references":[{"file":r,"role":"Identity and approved pose/style reference, explicit roles in prompt"} for r in req["referenced_image_paths"]],"alphaExtrema":alpha.getextrema() if alpha else None,"visibleBBox":alpha.getbbox() if alpha else None,"nativeResolutionValidated":im.width>=1024 and im.height>=1024,"status":"generated-pending-visual-and-sequence-review"}
 for reference in record["references"]:
  reference["sha256"]=hashlib.sha256(Path(reference["file"]).read_bytes()).hexdigest()
 source=Path(req["referenced_image_paths"][0])
 source_record=Path(str(source)+".generation.json")
 if source_record.exists():
  record["editedFrom"]={"file":str(source),"sha256":record["references"][0]["sha256"],"generationRecord":str(source_record)}
 (ROOT/(stem+".png.generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({k:record[k] for k in ["file","sha256","width","height","mode","alphaExtrema","visibleBBox"]}))
if __name__=="__main__":
 import sys
 for stem in sys.argv[1:]: register(stem)
