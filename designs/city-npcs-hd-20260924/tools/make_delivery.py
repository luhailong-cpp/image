from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime,timezone
import json,hashlib,zipfile,sys,math
sys.stdout.reconfigure(encoding="utf-8")
root=Path(__file__).resolve().parents[1]
plan=json.loads((root/"batch-plan.json").read_text(encoding="utf-8"))
by_id={e["id"]:e for e in plan["entries"]}
files=sorted((root/"native").glob("*.png"))
entries=[];issues=[]
for file in files:
 ident=file.name[:2]
 if ident not in by_id:continue
 e=by_id[ident];record_path=file.with_name(file.name+".generation.json")
 if not record_path.is_file():issues.append(file.name+": missing generation record");continue
 record=json.loads(record_path.read_text(encoding="utf-8-sig"));im=Image.open(file)
 digest=hashlib.sha256(file.read_bytes()).hexdigest()
 if record.get("sha256")!=digest:issues.append(file.name+": SHA256 mismatch")
 if im.mode!="RGBA":issues.append(file.name+": not RGBA")
 rgba=im.convert("RGBA");a=rgba.getchannel("A");mask=a.point(lambda v:255 if v>=8 else 0);bbox=mask.getbbox()
 edge=[a.crop((0,0,1,im.height)).getextrema()[1],a.crop((im.width-1,0,im.width,im.height)).getextrema()[1],a.crop((0,0,im.width,1)).getextrema()[1],a.crop((0,im.height-1,im.width,im.height)).getextrema()[1]]
 if a.getextrema()[0]!=0:issues.append(file.name+": no transparent pixels")
 if any(x>=8 for x in edge):issues.append(file.name+": visible content touches border")
 if record.get("width")!=im.width or record.get("height")!=im.height:issues.append(file.name+": dimension metadata mismatch")
 entries.append({"id":ident,"name":e["name"],"file":file.relative_to(root).as_posix(),"sha256":digest,"nativeSize":[im.width,im.height],"mode":im.mode,"alphaExtrema":list(a.getextrema()),"edgeAlphaMax":edge,"visibleBBox":bbox,"generationRecord":record_path.relative_to(root).as_posix(),"actualModelFamily":record.get("actualModel"),"actualModelVersion":record.get("actualModelVersion"),"actualQuality":record.get("actualQuality"),"referenceCompleteness":e["referenceCompleteness"],"designInterpretation":e.get("designInterpretation")})
ids=[e["id"] for e in entries];missing=sorted(set(by_id)-set(ids))
if len(set(ids))!=len(ids):issues.append("duplicate character IDs")
validation={"checkedAt":datetime.now(timezone.utc).isoformat(),"count":len(entries),"missingIds":missing,"issues":issues,"allFilesNativeUnscaled":True,"apiUsed":False}
(root/"validation.json").write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding="utf-8")
if missing or issues:
 print(json.dumps(validation,ensure_ascii=False));sys.exit(1)
manifest={"schemaVersion":1,"createdAt":datetime.now(timezone.utc).isoformat(),"scope":"23 static main-city NPC festive redraws","style":"Original Q-version Taoist + approved designs + Spring Festival / Mid-Autumn costume details","route":"builtin","apiUsed":False,"resolutionNote":"Native files are preserved without upscaling; actual sizes are per entry. Not native 4K. Numerical GPT Image model version and quality were not disclosed by the built-in host.","npcCount":len(entries),"entries":entries}
(root/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",24);small=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",17);title=ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc",38)
cols=6;cw,ch=340,440;rows=math.ceil(len(entries)/cols)
for dark in [False,True]:
 bg=(246,241,230) if not dark else (30,43,45);fg=(45,63,57) if not dark else (234,228,208)
 sheet=Image.new("RGB",(cols*cw+48,rows*ch+160),bg);draw=ImageDraw.Draw(sheet)
 draw.text((26,20),"主城 NPC · 道家 Q 版 × 春节中秋",font=title,fill=fg)
 draw.text((27,75),"23 位静态角色｜原生透明 PNG｜内置生成，未使用付费 API｜总览仅作缩略预览",font=small,fill=fg)
 for i,e in enumerate(entries):
  im=Image.open(root/e["file"]).convert("RGBA");alpha=im.getchannel("A").point(lambda v:255 if v>=8 else 0);bb=alpha.getbbox();thumb=im.crop(bb);thumb.thumbnail((cw-32,ch-86),Image.Resampling.LANCZOS)
  x=24+(i%cols)*cw;y=130+(i//cols)*ch
  sheet.paste(thumb,(x+(cw-thumb.width)//2,y+(ch-86-thumb.height)//2),thumb)
  text=e["id"]+" "+e["name"];draw.text((x+12,y+ch-70),text,font=font,fill=fg)
  draw.text((x+12,y+ch-34),str(e["nativeSize"][0])+" × "+str(e["nativeSize"][1])+"  原生",font=small,fill=fg)
 name="qa-dark.jpg" if dark else "overview.jpg";sheet.save(root/name,quality=94)
 deriv={"operation":"QA contact sheet only: alpha-bbox crop and downscale thumbnails, composite onto inspection background; native PNG assets unchanged","derivedFrom":[{"file":e["file"],"sha256":e["sha256"],"generationRecord":e["generationRecord"]} for e in entries]}
 (root/(name+".derivation.json")).write_text(json.dumps(deriv,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"count":len(entries),"sizes":sorted(set(tuple(e["nativeSize"]) for e in entries)),"validation":"passed","manifest":"manifest.json","overview":"overview.jpg"},ensure_ascii=False))
