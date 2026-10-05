from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,io,datetime
B=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
keys=["run-E-08-v6","run-E-09-v5","run-E-10-v5"]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def edges(im):
 a=im.getchannel("A");w,h=im.size
 return {k:sum(v>128 for v in a.crop(box).getdata()) for k,box in {"top":(0,0,w,1),"bottom":(0,h-1,w,h),"left":(0,0,1,h),"right":(w-1,0,w,h)}.items()}
def flat(im):
 bg=Image.new("RGBA",im.size,(216,222,214,255));bg.alpha_composite(im);return bg.convert("RGB")
report=[]
for key in keys:
 frame=key.split("-")[2];p=B/"staging"/(key+".png");old=B/"runtime/run/E"/(frame+".png")
 im=Image.open(p);im.load();assert im.mode=="RGBA" and im.width==im.height and im.width>=1024
 out=im.resize((1024,1024),Image.Resampling.LANCZOS);buf=io.BytesIO();out.save(buf,format="PNG")
 ok=not any(edges(im).values()) and not any(edges(out).values())
 sheet=Image.new("RGB",(640,350),(216,222,214));dr=ImageDraw.Draw(sheet)
 for col,(ip,label) in enumerate([(old,"BEFORE E"+frame),(p,key)]):
  pic=Image.open(ip);sheet.paste(flat(pic.resize((320,320),Image.Resampling.LANCZOS)),(col*320,0));dr.text((col*320+4,326),label,fill="black")
 sheet.save(D/(key+"-before-after.jpg"),quality=96)
 recpath=p.with_suffix(".png.generation.json");rec=json.loads(recpath.read_text(encoding="utf-8"))
 for ref in rec["references"]:ref["sha256AtEdit"]=sha(Path(ref["path"]))
 rec["evidence"]["toolResult"]="provenance/"+key+".tool-result.json"
 rec["editInput"]={"file":old.relative_to(B).as_posix(),"sha256":sha(old),"generationRecord":old.relative_to(B).as_posix()+".generation.json","generationRecordSha256":sha(Path(str(old)+".generation.json"))}
 rec["review"]={"status":"candidate" if ok else "rejected","reason":"Upper torso continuity edit, static review pending." if ok else "Brush touches right canvas boundary; technically invalid."}
 recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 report.append({"key":key,"file":p.relative_to(B).as_posix(),"sha256":sha(p),"beforeRuntimeSha256":sha(old),"nativeSize":list(im.size),"mode":im.mode,"nativeEdgesHighAlpha":edges(im),"exportTest":{"size":[1024,1024],"sha256":hashlib.sha256(buf.getvalue()).hexdigest(),"edgesHighAlpha":edges(out),"operation":"uniform_full_canvas_resize","crop":None,"translation":[0,0],"alphaCleanup":False,"written":False},"technicalPassed":ok,"actualModel":None,"actualQuality":None,"timing":{"frameMs":60,"frameCount":16,"cycleMs":960}})
(D/"technical.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,ensure_ascii=False))
