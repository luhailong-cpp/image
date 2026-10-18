from pathlib import Path
import json,hashlib,shutil,sys,re,datetime
from PIL import Image
Z=Path(__file__).resolve().parent
stem=sys.argv[1];src=Path(sys.argv[2])
assert re.fullmatch(r"r02_c01_s0[1-4]_0[1-4]_a[0-9]+",stem)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dst=Z/"native"/(stem+".png");gp=Path(str(dst)+".generation.json");rp=Z/"receipts"/(stem+".receipt.json")
assert not dst.exists() and not gp.exists() and not rp.exists()
shutil.copyfile(src,dst)
im=Image.open(dst);w,h=im.size
inp=json.loads((Z/"guides"/(stem+".input.json")).read_text(encoding="utf-8"))
refs=json.loads((Z/"guides"/(stem+".references.json")).read_text(encoding="utf-8"))
pp=Z/"prompts"/(stem+".txt");when=datetime.datetime.now(datetime.timezone.utc).isoformat()
for e in refs: assert sha(e["path"])==e["sha256"]
receipt={"tool":"image_gen.imagegen","route":"builtin","generatedFile":src.as_posix(),"archivedAtUtc":when,"submitted":{"promptText":pp.read_text(encoding="utf-8"),"promptFile":pp.as_posix(),"referenced_image_paths":[e["path"] for e in refs],"transparent_background":False},"actualModel":None,"actualQuality":None,"outputSha256":sha(src)}
generation={"file":dst.as_posix(),"sha256":sha(dst),"generatedAt":when,"nativeWidth":w,"nativeHeight":h,"format":im.format,"sourceOutputPath":src.as_posix(),"sourceOutputSha256":sha(src),"tool":"image_gen.imagegen","route":"builtin","configSnapshot":None,"submittedParameters":{"model":None,"quality":None,"transparent_background":False},"actualModel":None,"actualQuality":None,"unverifiedReason":"Builtin tool returned no actual model or quality; included route only.","prompt":pp.as_posix(),"promptSha256":sha(pp),"references":refs,"evidence":{"receipt":rp.as_posix()},"globalBox":inp["globalBox"],"coreBox":inp["coreBox"],"resizedAfterGeneration":False,"finalArtUpscaled":False,"status":"candidate_pending_native_visual_and_seam_QA" if (w,h)==(1254,1254) else "unexpected_native_size_not_selected"}
for p,v in ((rp,receipt),(gp,generation)):
 with p.open("x",encoding="utf-8") as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write("\n")
sp=Z/"connected-coast-current-selection-20261016.json";s=json.loads(sp.read_text(encoding="utf-8"));s["updatedAtUtc"]=when
s.setdefault("archivedSources",[]).append({"stem":stem,"path":dst.as_posix(),"sha256":sha(dst),"generationRecord":gp.as_posix(),"generationSha256":sha(gp),"receipt":rp.as_posix(),"status":generation["status"]})
s["inflight"]=[e for e in s.get("inflight",[]) if e["stem"]!=stem]
sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"file":dst.as_posix(),"sha256":sha(dst),"dimensions":[w,h],"record":gp.as_posix(),"receipt":rp.as_posix()}))

