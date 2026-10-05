from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,io,datetime
B=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
key="cast-E-03-v3";p=B/"staging"/(key+".png");old=B/"runtime/cast/E/03.png"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def edges(im):
    a=im.getchannel("A");w,h=im.size
    return {k:sum(v>128 for v in a.crop(box).getdata()) for k,box in {"top":(0,0,w,1),"bottom":(0,h-1,w,h),"left":(0,0,1,h),"right":(w-1,0,w,h)}.items()}
def flat(im):
    bg=Image.new("RGBA",im.size,(216,222,214,255));bg.alpha_composite(im);return bg.convert("RGB")
im=Image.open(p);im.load();assert im.mode=="RGBA" and im.width==im.height and im.width>=1024
out=im.resize((1024,1024),Image.Resampling.LANCZOS);buf=io.BytesIO();out.save(buf,format="PNG")
for name,items in [("before-after-full320",[(old,"BEFORE E03"),(p,"AFTER "+key)]),("02-new03-04-full320",[(B/"runtime/cast/E/02.png","E02 unchanged"),(p,key),(B/"runtime/cast/E/04.png","E04 unchanged")])]:
    sheet=Image.new("RGB",(320*len(items),350),(216,222,214));dr=ImageDraw.Draw(sheet)
    for col,(ip,label) in enumerate(items):
        pic=Image.open(ip);sheet.paste(flat(pic.resize((320,320),Image.Resampling.LANCZOS)),(col*320,0));dr.text((col*320+4,326),label,fill="black")
    sheet.save(D/(name+".jpg"),quality=96)
recpath=p.with_suffix(".png.generation.json");rec=json.loads(recpath.read_text(encoding="utf-8"))
for ref in rec["references"]:ref["sha256AtEdit"]=sha(Path(ref["path"]))
rec["evidence"]["toolResult"]="provenance/"+key+".tool-result.json"
rec["editInput"]={"file":old.relative_to(B).as_posix(),"sha256":sha(old),"generationRecord":old.relative_to(B).as_posix()+".generation.json","generationRecordSha256":sha(Path(str(old)+".generation.json"))}
rec["review"]={"status":"candidate","reason":"Backtracking right arm path corrected; mouth overlap and small left scroll drift require root sequence comparison."}
recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
report={"reviewedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"candidate_path_improved_root_review_pending","file":p.relative_to(B).as_posix(),"slot":"cast-E-03","key":key,"sourceSha256":sha(p),"beforeRuntimeSha256":sha(old),
"nativeSize":list(im.size),"mode":im.mode,"nativeEdgesHighAlpha":edges(im),"exportTest":{"size":[1024,1024],"sha256":hashlib.sha256(buf.getvalue()).hexdigest(),"edgesHighAlpha":edges(out),"operation":"uniform_full_canvas_resize","crop":None,"translation":[0,0],"alphaCleanup":False,"written":False},
"targetChange":"右肩—肘—腕从原耳侧回撤路径改为脸前右上斜举；笔向介于02更竖直与04更斜举之间。旧耳后笔和旧穗无残留，唯一大青穗连握拳下方新笔尾，右笔左卷身份保留。",
"nonTargetDrift":"新右袖/前臂遮住部分嘴与下脸；这是右臂移动后的实际遮挡，需要root对照判断可读性。左卷及墨灵有轻微向右/下的位置重绘，双腿靴形与站位大体保留但非逐像素固定。没有整图平移、缩放或腿距明显扩大。",
"technicalPassed":not any(edges(im).values()) and not any(edges(out).values()),
"generationRecord":recpath.relative_to(B).as_posix(),"request":"provenance/"+key+".request.json","toolResult":"provenance/"+key+".tool-result.json","actualModel":None,"actualQuality":None,
"timing":{"frameMs":45,"frameCount":16,"releaseFrame":10},"runtimeModified":False,"acceptanceModified":False,
"comparisons":["before-after-full320.jpg","02-new03-04-full320.jpg"]}
(D/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,ensure_ascii=False))

