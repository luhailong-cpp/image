from pathlib import Path
from PIL import Image
import json,hashlib,shutil,importlib.util
import numpy as np
from datetime import datetime,timezone
p=Path(__file__).resolve().parent;r=p/"seam_repair_v2"
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
records=[]
for e in json.loads((r/"sources.json").read_text(encoding="utf-8")):
 ident=e["id"];src=Path(e["source"]);assert Image.open(src).size==(1254,1254)
 out=r/"native"/f"{ident}.png";shutil.copyfile(src,out)
 record={"id":ident,"route":"builtin_image_gen","backendModelVerified":False,"sourceOutputPath":str(src),"sourceOutputSha256":sha(src),"outputSha256":sha(out),"actualNativePixels":[1254,1254],"finalArtUpscaled":False,"promptFile":f"prompts/{ident}.prompt.txt","promptSha256":sha(r/"prompts"/f"{ident}.prompt.txt"),"guideSha256":sha(r/"guides"/f"{ident}.png")}
 (r/"native"/f"{ident}.record.json").write_text(json.dumps(record,indent=2),encoding="utf-8");records.append(record)
basefile=p/"output/extended-context.png";base=np.asarray(Image.open(basefile).convert("RGB")).copy()
# r02 is an unchanged crop of already generated native-source assembly, not a new generation or a resampled guide.
keep=base[1024:2278,3584:4838].copy();Image.fromarray(keep).save(r/"native/r02-preserved.png")
preserved={"id":"r02","route":"mechanical_preserve_native_assembly_pixels","source":str(basefile),"sourceSha256":sha(basefile),"sourceBox":[3584,1024,4838,2278],"pixels":[1254,1254],"outputSha256":sha(r/"native/r02-preserved.png"),"newGeneration":False}
(r/"native/r02-preserved.record.json").write_text(json.dumps(preserved,indent=2),encoding="utf-8")
spec=importlib.util.spec_from_file_location("mechanical_seam",p.parent/"r10_c08/assemble_builtin.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);seam=m.load_seam_helper()
pieces=[np.asarray(Image.open(r/"native"/f"{i}.png").convert("RGB")) if i!="r02" else keep for i in ["r01","r02","r03","r04"]]
strip=np.transpose(pieces[0],(1,0,2));metrics=[]
for i,im in enumerate(pieces[1:],2):
 strip,metric=m.append_patch(strip,np.transpose(im,(1,0,2)),seam,f"repair_vertical_{i}");metrics.append(metric)
strip=np.transpose(strip,(1,0,2));assert strip.shape==(4326,1254,3)
combined,metric=m.append_patch(base[:,:3814],strip,seam,"insert_repair_left");metrics.append(metric)
combined,metric=m.append_patch(combined,base[:,4608:],seam,"insert_repair_right");metrics.append(metric)
assert combined.shape==base.shape
assert np.array_equal(combined[:,:3584],base[:,:3584])
assert np.array_equal(combined[:,4838:],base[:,4838:])
out=p/"output_v2";qa=p/"qa_v2";out.mkdir(exist_ok=True);qa.mkdir(exist_ok=True)
Image.fromarray(combined).save(out/"extended-context.png")
canvas=Image.fromarray(combined[115:4211,115:8307].copy());canvas.save(out/"pair_8192x4096_candidate.png")
a=canvas.crop((0,0,4096,4096));b=canvas.crop((4096,0,8192,4096));a.save(out/"r10_c07.png");b.save(out/"r10_c08.png")
assert np.array_equal(np.concatenate([np.asarray(a),np.asarray(b)],axis=1),np.asarray(canvas))
canvas.resize((1600,800),Image.Resampling.LANCZOS).save(qa/"overview-preview.jpg",quality=70)
items=[]
for i,y in enumerate([0,799,1598,2397,3196],1):
 box=[3446,y,4746,y+900];im=canvas.crop(box);f=qa/f"cross_4k_seam_{i:02}_100pct.png";im.save(f);im.save(f.with_suffix(".jpg"),quality=85);items.append({"file":f.name,"sourceBox":box,"pixels":[1300,900],"scale":1,"sha256":sha(f)})
files=[{"file":str(f.relative_to(p)).replace("\\","/"),"pixels":list(Image.open(f).size),"sha256":sha(f)} for f in out.glob("*.png")]
manifest={"schemaVersion":1,"createdAtUtc":datetime.now(timezone.utc).isoformat(),"status":"repaired_candidate_pending_visual_review","parentAssembly":"assembly.json","parentAssemblySha256":sha(p/"assembly.json"),"baseExtendedSourceSha256":sha(basefile),"newNativeRepairCount":3,"preservedAssemblyCrop":preserved,"repairSources":records,"method":"native1254 edits, minimum-error overlap seams and2px seam-mask feather, then exact4K slices","sourceResampling":False,"globalBlur":False,"colorMatching":False,"unchangedOutsideRepairBandPixels":True,"repairBandInExtended":[3584,0,4838,4326],"scriptSha256":sha(Path(__file__)),"files":files,"qa":items,"seamMetrics":metrics,"tilesRejoinExactly":True,"runtimePublished":False,"wholeCityComplete":False,"visualQaPassed":False}
(p/"assembly_v2.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print(json.dumps({"newNativeRepairs":3,"files":files,"rejoinedPixelsMatch":True},indent=2))
