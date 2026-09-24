from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json, hashlib, importlib.util, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
job=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
root=Path(__file__).resolve().parents[1]
src=Path(job["source"]); dst=root/job["destination"];dst.parent.mkdir(parents=True,exist_ok=True)
if not dst.exists(): shutil.copy2(src,dst)
parser=Path("E:/work/image/designs/city-npcs-20260924/tools/inspect_image_provenance.py")
spec=importlib.util.spec_from_file_location("provenance",parser);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
prov=mod.inspect_image(dst);provfile=dst.with_name(dst.name+".provenance.json");provfile.write_text(json.dumps(prov,ensure_ascii=False,indent=2),encoding="utf-8")
when=(prov.get("created_actions") or [{}])[0].get("when")
if isinstance(when,dict):when=when.get("value")
im=Image.open(dst).convert("RGBA");a=im.getchannel("A");bbox=a.point(lambda v:255 if v>=8 else 0).getbbox()
promptfile=dst.with_name(dst.stem+".prompt.txt");promptfile.write_text(job["prompt"],encoding="utf-8")
rec={"file":dst.name,"sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),"generatedAt":when,"recordedAt":datetime.now(timezone.utc).isoformat(),"width":im.width,"height":im.height,"format":"PNG","mode":"RGBA","tool":"image_gen.imagegen","route":"builtin","status":job["status"],"configSnapshot":json.loads(Path("E:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"size":None,"num_last_images_to_include":job.get("numRefs",2)},"actualModel":"gpt-image" if prov.get("created_actions") else None,"actualModelVersion":None,"actualQuality":None,"unverifiedReason":"Host-managed builtin only. Numerical model version, quality and size selectors are not exposed; actual output dimensions are recorded above.","prompt":promptfile.name,"references":job["references"],"evidence":{"toolOutputHint":job["toolOutputHint"],"embeddedProvenance":provfile.name},"visualReview":job.get("visualReview",{}),"alphaExtrema":a.getextrema(),"visibleBBoxAlphaThreshold8":bbox,"referenceCompleteness":job.get("referenceCompleteness","complete_or_mostly_complete")}
rec["visualReview"]["edgeAlphaMax"]=[a.crop((0,0,1,im.height)).getextrema()[1],a.crop((im.width-1,0,im.width,im.height)).getextrema()[1],a.crop((0,0,im.width,1)).getextrema()[1],a.crop((0,im.height-1,im.width,im.height)).getextrema()[1]]
record=dst.with_name(dst.name+".generation.json");record.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"file":str(dst),"size":im.size,"status":job["status"],"bbox":bbox},ensure_ascii=False))
