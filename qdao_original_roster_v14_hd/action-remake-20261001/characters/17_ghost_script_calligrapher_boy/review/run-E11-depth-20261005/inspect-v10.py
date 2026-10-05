from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,io,datetime
B=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
key="run-E-11-v10";p=B/"staging"/(key+".png");old=B/"runtime/run/E/11.png"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def edges(im):
 a=im.getchannel("A");w,h=im.size
 return {k:sum(v>128 for v in a.crop(box).getdata()) for k,box in {"top":(0,0,w,1),"bottom":(0,h-1,w,h),"left":(0,0,1,h),"right":(w-1,0,w,h)}.items()}
def flat(im):
 bg=Image.new("RGBA",im.size,(216,222,214,255));bg.alpha_composite(im);return bg.convert("RGB")
im=Image.open(p);im.load();assert im.mode=="RGBA" and im.width==im.height and im.width>=1024
out=im.resize((1024,1024),Image.Resampling.LANCZOS);buf=io.BytesIO();out.save(buf,format="PNG")
groups=[("v10-before-after-full320",[(old,"BEFORE E11"),(p,"AFTER "+key)]),("v10-10-11-12-full320",[(B/"runtime/run/E/10.png","E10 current"),(p,key),(B/"runtime/run/E/12.png","E12 current")])]
for name,items in groups:
 sheet=Image.new("RGB",(320*len(items),350),(216,222,214));dr=ImageDraw.Draw(sheet)
 for col,(ip,label) in enumerate(items):
  pic=Image.open(ip);sheet.paste(flat(pic.resize((320,320),Image.Resampling.LANCZOS)),(col*320,0));dr.text((col*320+4,326),label,fill="black")
 sheet.save(D/(name+".jpg"),quality=96)
sheet=Image.new("RGB",(520*2,550),(216,222,214));dr=ImageDraw.Draw(sheet)
for col,(ip,label) in enumerate([(old,"BEFORE E11 torso"),(p,"AFTER v10 torso")]):
 pic=Image.open(ip).resize((1024,1024),Image.Resampling.LANCZOS).crop((260,380,780,900))
 sheet.paste(flat(pic),(col*520,0));dr.text((col*520+4,526),label,fill="black")
sheet.save(D/"v10-before-after-torso.jpg",quality=96)
recpath=p.with_suffix(".png.generation.json");rec=json.loads(recpath.read_text(encoding="utf-8"))
for ref in rec["references"]:ref["sha256AtEdit"]=sha(Path(ref["path"]))
rec["evidence"]["toolResult"]="provenance/"+key+".tool-result.json"
rec["editInput"]={"file":old.relative_to(B).as_posix(),"sha256":sha(old),"generationRecord":old.relative_to(B).as_posix()+".generation.json","generationRecordSha256":sha(Path(str(old)+".generation.json"))}
rec["review"]={"status":"candidate","reason":"Raised scroll-side shoulder hump reduced and lowered into short rear cuff; visual root review pending."}
recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
report={"reviewedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"candidate_local_depth_improved_root_review_pending","file":p.relative_to(B).as_posix(),"slot":"run-E-11","key":key,"sourceSha256":sha(p),"beforeRuntimeSha256":sha(old),"nativeSize":list(im.size),"mode":im.mode,"nativeEdgesHighAlpha":edges(im),"exportTest":{"size":[1024,1024],"sha256":hashlib.sha256(buf.getvalue()).hexdigest(),"edgesHighAlpha":edges(out),"operation":"uniform_full_canvas_resize","crop":None,"translation":[0,0],"alphaCleanup":False,"written":False},
"targetObservation":"卷手上方原本高于近肩的大隆起袖肩已缩小并下移到发尾以下，外露更像从躯干后方伸出的短袖；右笔近肩和低位握笔仍可读。没有完全藏掉所有卷袖，保留的短袖需主审判断是否足以消除错误近肩观感。",
"nonTargetDrift":"整体头身、两腿靴形、两手持物与两只墨灵保留；新图有少量重画/布局漂移，尤其卷轴边宽与附近衣纹，不能称逐像素固定。无新明显鞋轴外翻、换手或边缘裁断。","technicalPassed":not any(edges(im).values()) and not any(edges(out).values()),"generationRecord":recpath.relative_to(B).as_posix(),"request":"provenance/"+key+".request.json","toolResult":"provenance/"+key+".tool-result.json","actualModel":None,"actualQuality":None,"timing":{"frameMs":60,"frameCount":16,"cycleMs":960},"runtimeModified":False,"acceptanceModified":False,"comparisons":["v10-before-after-full320.jpg","v10-before-after-torso.jpg","v10-10-11-12-full320.jpg"]}
(D/"report-v10.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(report,ensure_ascii=False))
