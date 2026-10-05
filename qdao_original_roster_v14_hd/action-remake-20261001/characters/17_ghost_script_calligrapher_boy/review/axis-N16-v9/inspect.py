from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,io,datetime
B=Path(__file__).resolve().parents[2]; D=Path(__file__).resolve().parent
key="run-N-16-v9"
native=B/"staging"/(key+".png"); before=B/"runtime/run/N/16.png"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def edge(im):
    a=im.getchannel("A");w,h=im.size
    return {k:sum(x>128 for x in a.crop(v).getdata()) for k,v in {"top":(0,0,w,1),"bottom":(0,h-1,w,h),"left":(0,0,1,h),"right":(w-1,0,w,h)}.items()}
def flat(im):
    bg=Image.new("RGBA",im.size,(216,222,214,255));bg.alpha_composite(im);return bg.convert("RGB")
im=Image.open(native);im.load();old=Image.open(before);old.load()
assert im.width==im.height and im.width>=1024 and im.mode=="RGBA"
out=im.resize((1024,1024),Image.Resampling.LANCZOS);buf=io.BytesIO();out.save(buf,format="PNG")
whole=Image.new("RGB",(480,274),(236,235,227));draw=ImageDraw.Draw(whole)
feet=Image.new("RGB",(840,424),(236,235,227));fd=ImageDraw.Draw(feet)
for i,(pic,label) in enumerate([(old,"BEFORE runtime N16"),(out,"AFTER N16v9 REJECT")]):
    whole.paste(flat(pic.resize((240,240),Image.Resampling.LANCZOS)),(i*240,0));draw.text((i*240+4,245),label,fill="black")
    feet.paste(flat(pic.crop((365,675,755,1005)).resize((420,355),Image.Resampling.LANCZOS)),(i*420,0));fd.text((i*420+4,366),label,fill="black")
whole.save(D/"before-after-full240.jpg",quality=95);feet.save(D/"before-after-feet.jpg",quality=95)
recpath=native.with_suffix(".png.generation.json");rec=json.loads(recpath.read_text(encoding="utf-8"))
for ref in rec["references"]:ref["sha256AtEdit"]=sha(Path(ref["path"]))
rec["evidence"]["toolResult"]="provenance/"+key+".tool-result.json"
rec["editInput"]={"file":"runtime/run/N/16.png","sha256":sha(before),"generationRecord":"runtime/run/N/16.png.generation.json","generationRecordSha256":sha(Path(str(before)+".generation.json"))}
rec["review"]={"status":"rejected","reason":"Non-target right swing boot changed to whole sole facing camera."}
recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
report={"reviewedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"rejected_non_target_pose_drift","slot":"run-N-16","key":key,
"file":native.relative_to(B).as_posix(),"sourceSha256":sha(native),"beforeRuntimeSha256":sha(before),"nativeSize":list(im.size),"mode":im.mode,"nativeEdgesHighAlpha":edge(im),
"exportTest":{"size":[1024,1024],"sha256":hashlib.sha256(buf.getvalue()).hexdigest(),"edgesHighAlpha":edge(out),"operation":"uniform_full_canvas_resize","crop":None,"translation":[0,0],"alphaCleanup":False,"written":False},
"targetChange":"左支撑靴横扭收正，膝踝鞋掌轴向朝N。",
"nonTargetDrift":"右摆靴错误采用参考v6整底朝镜头视图，改变原runtime近落地后跟和窄底边；右踝/靴相位随之改变。这一副作用足以拒选。",
"bodyReview":"全画布240px对比，整体头身、笔卷、左支撑腿布局无明显大幅平移；右摆靴姿态不符合约束，不能因左靴变好而选用。",
"runtimeModified":False,"acceptanceModified":False,"additionalGenerationAllowedThisRound":False,
"generationRecord":recpath.relative_to(B).as_posix(),"toolRequest":"provenance/"+key+".request.json","toolResult":"provenance/"+key+".tool-result.json",
"actualModel":None,"actualQuality":None}
(D/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,ensure_ascii=False))

