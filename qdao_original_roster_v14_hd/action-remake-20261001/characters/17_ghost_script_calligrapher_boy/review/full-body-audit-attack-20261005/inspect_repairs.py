from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,io,datetime
B=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
keys=["attack-E-09-v3","attack-E-09-v4","attack-W-09-v4"]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def edge(im):
    a=im.getchannel("A");w,h=im.size
    return {k:sum(v>128 for v in a.crop(box).getdata()) for k,box in {"top":(0,0,w,1),"bottom":(0,h-1,w,h),"left":(0,0,1,h),"right":(w-1,0,w,h)}.items()}
def flat(im):
    bg=Image.new("RGBA",im.size,(216,222,214,255));bg.alpha_composite(im);return bg.convert("RGB")
rows=[]
for key in keys:
    direction=key.split("-")[1];p=B/"staging"/(key+".png");im=Image.open(p);im.load()
    assert im.width==im.height and im.width>=1024 and im.mode=="RGBA"
    out=im.resize((1024,1024),Image.Resampling.LANCZOS);buf=io.BytesIO();out.save(buf,format="PNG")
    recpath=p.with_suffix(".png.generation.json");rec=json.loads(recpath.read_text(encoding="utf-8"))
    assert rec["sha256"]==sha(p)
    for ref in rec["references"]:ref["sha256AtEdit"]=sha(Path(ref["path"]))
    primary=Path(rec["references"][0]["path"])
    rec["evidence"]["toolResult"]="provenance/"+key+".tool-result.json"
    rec["editInput"]={"file":primary.relative_to(B).as_posix(),"sha256":sha(primary),"generationRecord":primary.relative_to(B).as_posix()+".generation.json","generationRecordSha256":sha(Path(str(primary)+".generation.json"))}
    rec["review"]={"status":"rejected" if key.endswith("v3") else "candidate","reason":"Old brush tassel remains below left sleeve." if key.endswith("v3") else "Local recovery fix; root sequence review pending."}
    recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    row={"slot":"attack-"+direction+"-09","key":key,"file":p.relative_to(B).as_posix(),"sourceSha256":sha(p),"nativeSize":list(im.size),"mode":im.mode,"nativeEdgesHighAlpha":edge(im),"beforeRuntimeSha256":sha(B/"runtime/attack"/direction/"09.png"),
    "exportTest":{"size":[1024,1024],"sha256":hashlib.sha256(buf.getvalue()).hexdigest(),"edgesHighAlpha":edge(out),"operation":"uniform_full_canvas_resize","crop":None,"translation":[0,0],"alphaCleanup":False,"written":False},
    "generationRecord":recpath.relative_to(B).as_posix(),"recommendation":"reject_old_tassel_remnant" if key.endswith("v3") else "recommend_for_root_review"}
    rows.append(row)
    if key.endswith("v4"):
        images=[(B/"runtime/attack"/direction/"08.png","08 unchanged"),(p,key),(B/"runtime/attack"/direction/"10.png","10 unchanged")]
        sheet=Image.new("RGB",(960,350),(216,222,214));draw=ImageDraw.Draw(sheet)
        for col,(ip,label) in enumerate(images):
            pic=Image.open(ip);sheet.paste(flat(pic.resize((320,320),Image.Resampling.LANCZOS)),(col*320,0));draw.text((col*320+4,326),label,fill="black")
        sheet.save(D/(direction+"-08-new09-10-full320.jpg"),quality=96)
        pair=Image.new("RGB",(640,350),(216,222,214));dr=ImageDraw.Draw(pair)
        for col,(ip,label) in enumerate([(B/"runtime/attack"/direction/"09.png","BEFORE 09"),(p,"AFTER "+key)]):
            pair.paste(flat(Image.open(ip).resize((320,320),Image.Resampling.LANCZOS)),(col*320,0));dr.text((col*320+4,326),label,fill="black")
        pair.save(D/(direction+"-09-before-after-full320.jpg"),quality=96)
report={"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"technical_passed" if all(not any(r["nativeEdgesHighAlpha"].values()) and not any(r["exportTest"]["edgesHighAlpha"].values()) for r in rows) else "technical_failed","runtimeModified":False,"frames":rows}
(D/"repair-technical.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,ensure_ascii=False))

