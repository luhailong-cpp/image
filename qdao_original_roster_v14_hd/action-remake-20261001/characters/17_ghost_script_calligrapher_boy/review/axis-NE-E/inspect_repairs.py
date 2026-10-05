from pathlib import Path
import json,hashlib,datetime,io
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[2]
D=Path(__file__).resolve().parent
choices=[("07","run-NE-07-v7"),("08","run-NE-08-v7"),("15","run-NE-15-v4")]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def edges(im):
    a=im.getchannel("A");w,h=im.size
    return {k:sum(v>128 for v in a.crop(box).getdata()) for k,box in
      {"top":(0,0,w,1),"bottom":(0,h-1,w,h),"left":(0,0,1,h),"right":(w-1,0,w,h)}.items()}
def flatten(im):
    bg=Image.new("RGBA",im.size,(216,222,214,255));bg.alpha_composite(im);return bg.convert("RGB")
whole=Image.new("RGB",(6*240,274),(236,235,227));wd=ImageDraw.Draw(whole)
feet=Image.new("RGB",(2*590,3*338),(236,235,227));fd=ImageDraw.Draw(feet)
out=[]
for row,(n,key) in enumerate(choices):
    native=B/"staging"/(key+".png"); im=Image.open(native);im.load()
    assert im.width==im.height and im.width>=1024 and im.mode=="RGBA"
    review=im.resize((1024,1024),Image.Resampling.LANCZOS)
    stream=io.BytesIO();review.save(stream,format="PNG")
    oldpath=B/"runtime/run/NE"/(n+".png");old=Image.open(oldpath);old.load()
    recpath=native.with_suffix(".png.generation.json")
    rec=json.loads(recpath.read_text(encoding="utf-8"))
    assert rec["sha256"]==sha(native)
    refs=rec["references"]
    for ref in refs:
        p=Path(ref["path"]);ref["sha256AtEdit"]=sha(p)
    rec["evidence"]["toolResult"]=f"provenance/{key}.tool-result.json"
    rec["editInput"]={"file":oldpath.relative_to(B).as_posix(),"sha256":sha(oldpath),
        "generationRecord":oldpath.relative_to(B).as_posix()+".generation.json",
        "generationRecordSha256":sha(Path(str(oldpath)+".generation.json"))}
    recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for col,(pic,label) in enumerate([(old,"BEFORE runtime NE"+n),(review,"AFTER "+key)]):
        whole.paste(flatten(pic.resize((240,240),Image.Resampling.LANCZOS)),((row*2+col)*240,0))
        wd.text(((row*2+col)*240+4,244),label,fill=(20,30,20))
        crop=pic.crop((200,650,1000,1010)).resize((590,266),Image.Resampling.LANCZOS)
        feet.paste(flatten(crop),(col*590,row*338))
        fd.text((col*590+5,row*338+274),label+" fixed crop (200,650,1000,1010)",fill=(20,30,20))
    outputSha=hashlib.sha256(stream.getvalue()).hexdigest()
    out.append({"slot":"run-NE-"+n,"key":key,"file":native.relative_to(B).as_posix(),"sourceSha256":sha(native),
      "nativeSize":list(im.size),"mode":im.mode,"nativeEdgesHighAlpha":edges(im),
      "exportTest":{"size":[1024,1024],"sha256":outputSha,"edgesHighAlpha":edges(review),"operation":"uniform_full_canvas_resize","crop":None,"translation":[0,0],"alphaCleanup":False,"written":False},
      "beforeRuntimeSha256":sha(oldpath),"generationRecord":recpath.relative_to(B).as_posix()})
whole.save(D/"repair-before-after-240.jpg",quality=95)
feet.save(D/"repair-before-after-feet.jpg",quality=96)
assert all(not any(r["nativeEdgesHighAlpha"].values()) and not any(r["exportTest"]["edgesHighAlpha"].values()) for r in out)
(D/"repair-technical.json").write_text(json.dumps({"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"technical_passed","runtimeModified":False,"frames":out},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,ensure_ascii=False))

