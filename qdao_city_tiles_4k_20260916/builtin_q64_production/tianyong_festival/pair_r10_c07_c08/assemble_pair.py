from pathlib import Path
import importlib.util,hashlib,json
from datetime import datetime,timezone
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
BASE=Path(r"E:/work/image/qdao_city_tiles_4k_20260916")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
old=module("tian_left",BASE/"builtin_q64_r10_c07/assemble_builtin.py")
new=module("tian_right",ROOT.parent/"r10_c08/assemble_builtin.py")
left,le=old.load_sources();right,re=new.load_sources()
seam=new.load_seam_helper();metrics=[];strips=[]
for row in range(4):
 pieces=left[row]+right[row];strip=pieces[0]
 for col,piece in enumerate(pieces[1:],2):
  strip,metric=new.append_patch(strip,piece,seam,f"r{row+1:02}_c{col-1:02}_c{col:02}");metrics.append(metric)
 assert strip.shape==(1254,8422,3);strips.append(strip)
combined=np.transpose(strips[0],(1,0,2))
for row,strip in enumerate(strips[1:],2):
 combined,metric=new.append_patch(combined,np.transpose(strip,(1,0,2)),seam,f"rows{row-1}_{row}");metrics.append(metric)
combined=np.transpose(combined,(1,0,2));assert combined.shape==(4326,8422,3)
final=combined[115:4211,115:8307].copy();assert final.shape==(4096,8192,3)
out=ROOT/"output";qa=ROOT/"qa";out.mkdir(exist_ok=True);qa.mkdir(exist_ok=True)
files=[]
def save(im,path,role):
 im.save(path,format="PNG",compress_level=6);files.append({"file":str(path.relative_to(ROOT)).replace("\\","/"),"pixels":list(im.size),"sha256":sha(path),"role":role})
save(Image.fromarray(combined),out/"extended-context.png","native_sources_joined_before_outer_crop")
canvas=Image.fromarray(final);save(canvas,out/"pair_8192x4096_candidate.png","two_adjacent_tiles_not_whole_city")
a=canvas.crop((0,0,4096,4096));b=canvas.crop((4096,0,8192,4096))
save(a,out/"r10_c07.png","local_candidate_not_runtime_accepted")
save(b,out/"r10_c08.png","local_candidate_not_runtime_accepted")
assert np.array_equal(np.concatenate([np.asarray(a),np.asarray(b)],axis=1),final)
overview=canvas.resize((1600,800),Image.Resampling.LANCZOS);overview.save(qa/"overview-preview.jpg",quality=70)
items=[]
for index,y in enumerate([0,799,1598,2397,3196],1):
 box=[3646,y,4546,y+900];im=canvas.crop(box);p=qa/f"cross_4k_seam_{index:02}_100pct.png";im.save(p);im.save(p.with_suffix(".jpg"),quality=85);items.append({"file":p.name,"sourceBox":box,"pixels":[900,900],"scale":1,"sha256":sha(p)})
manifest={"schemaVersion":1,"createdAtUtc":datetime.now(timezone.utc).isoformat(),"scope":"Two neighboring Tianyong festival Q64 tiles r10_c07 and r10_c08","status":"candidate_pending_visual_review","wholeCityPixels":[65536,65536],"worldRect":{"x":162.5,"z":112.5,"width":37.5,"height":18.75},"wholeCityPixelRectXYWH":[24576,36864,8192,4096],"nativePatchCount":32,"nativePixels":[1254,1254],"core":1024,"halo":115,"overlap":230,"sourceResampling":False,"guidePixelsInFinal":False,"globalBlur":False,"colorMatching":False,"joinBeforeFinal4kSlice":True,"seamAlgorithm":"existing minimum-error seam, radius2 mask only","leftSourcePackage":str(old.ROOT),"rightSourcePackage":str(new.ROOT),"leftNativeEvidence":le,"rightNativeEvidence":re,"leftPlanSha256":sha(old.ROOT/"plan.json"),"rightPlanSha256":sha(new.ROOT/"plan.json"),"scriptSha256":sha(Path(__file__)),"seamHelperSha256":sha(new.HELPERS),"files":files,"seamMetrics":metrics,"qa":items,"mechanicalValidation":{"nativeSources":32,"rejoinedCropsMatchCanvasExactly":True,"outputSize":[8192,4096],"deliveryTileSizes":[[4096,4096],[4096,4096]]},"runtimePublished":False,"visualQaPassed":False,"otherNeighborsQaPassed":False}
(ROOT/"assembly.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print(json.dumps({"files":files,"mechanicalValidation":manifest["mechanicalValidation"]},indent=2))
