from pathlib import Path
from PIL import Image, ImageDraw
import hashlib,json,datetime,shutil,re
ROOT=Path(__file__).resolve().parent
ART=ROOT/"art"
OUT=ROOT/"client/Assets/Resources/UI/Ugui/MailV1Fidelity"
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):
 p=Path(p)
 if p.exists():return hashlib.sha256(p.read_bytes()).hexdigest()
 return json.loads(p.with_name(p.name+".generation.json").read_text(encoding="utf-8"))["sha256"]
config=json.loads((ROOT.parents[2]/"config/image-generation.json").read_text(encoding="utf-8-sig"))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
original=ROOT.parent/"01-mail-event.png"
system=ROOT.parent/"02-mail-system.png"
records=[
("mail-clean-skin.png","clean-mail-skin.txt",[original,system],r"C:\Users\luyua\.codex\generated_images\01a143db-6e50-7b01-86b3-e4d6e8d583a8\exec-9d0fb6de-234d-414d-84ec-df74d4bee886.png"),
("mail-empty-base.png","empty-mail-base.txt",[ART/"mail-clean-skin.png",system],r"C:\Users\luyua\.codex\generated_images\01a143db-6e50-7b01-86b3-e4d6e8d583a8\exec-022c0b59-da7b-4acb-8ae6-49aced00ab48.png"),
("mail-empty-frame.png","empty-mail-footer.txt",[ART/"mail-empty-base.png"],r"C:\Users\luyua\.codex\generated_images\01a143db-6e50-7b01-86b3-e4d6e8d583a8\exec-0a7e98b4-4b90-4f01-a5ff-01b529a924ae.png"),
("mail-controls-clean.png","clean-mail-controls.txt",[ART/"mail-clean-skin.png"],r"C:\Users\luyua\.codex\generated_images\01a143db-6e50-7b01-86b3-e4d6e8d583a8\exec-be94f0c8-b37a-454f-93b3-fbd80cb6cda8.png")]
for name,prompt,refs,cache in records:
 if not (ART/name).exists():continue
 im=Image.open(ART/name)
 rec={"file":name,"sha256":sha(ART/name),"generatedAt":now,"generatedAtBasis":"Recorded immediately after built-in call in current session; not a model metadata timestamp","width":im.width,"height":im.height,"format":"PNG","tool":"image_gen.imagegen","route":"builtin","configSnapshot":config,"submittedParameters":{"prompt":str(ROOT/"prompts"/prompt),"referenced_image_paths":[str(x) for x in refs],"transparent_background":False,"model":None,"quality":None},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理；工具没有model/quality选择器，结果只返回image_url和output_hint，未披露可核实具体版本或质量。","references":[{"path":str(x),"sha256":sha(x),"role":"edit-target" if i==0 else "same-approved-mail-support"} for i,x in enumerate(refs)],"evidence":{"resultKeys":["image_url","output_hint"],"toolOutputPath":cache},"review":{"status":"accepted-for-runtime-slicing" if name!="mail-empty-base.png" else "superseded-by-footer-cleanup","nativeClientParityVerified":False},"retention":"Only source required for current extraction is retained; intermediate base will be removed after source-chain record is complete."}
 stamp=re.search(rb'c2pa\.created.{0,32}?(20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)',(ART/name).read_bytes(),re.S)
 if stamp:
  rec["generatedAt"]=stamp.group(1).decode()
  rec["generatedAtBasis"]="PNG embedded c2pa.actions.v2 / c2pa.created.when; metadata declaration only, C2PA signature chain not validated."
 rec["evidence"]["embeddedSoftwareAgent"]={"name":"ChatGPT","version":"gpt-image","scope":"generic family label only, not 2.5/Sunburst snapshot or max quality"}
 (ART/(name+".generation.json")).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
master=Image.open(ART/"mail-clean-skin.png").convert("RGBA")
base=Image.open(ART/"mail-empty-frame.png").convert("RGBA")
items=[]
def save(name,im,source,rect,operation,border=(0,0,0,0)):
 path=OUT/(name+".png");im.save(path)
 meta={"key":name,"assetPath":"Assets/Resources/UI/Ugui/MailV1Fidelity/"+name+".png","source":str(source),"sourceRectXYWH":rect,"width":im.width,"height":im.height,"sha256":sha(path),"borderLeftBottomRightTop":list(border),"operation":operation}
 items.append(meta)
 rec={"file":path.name,"sha256":meta["sha256"],"width":im.width,"height":im.height,"format":"PNG","derivedAt":now,"operation":operation,"derivedFrom":[{"path":str(source),"sha256":sha(source),"generationRecord":str(source)+".generation.json"}],"actualModel":None,"actualQuality":None,"modelBasis":"Inherited from AI source record; actual version and quality not disclosed."}
 (path.with_name(path.name+".generation.json")).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 guid=hashlib.sha256(("wuxing-mail-fidelity-20261016/"+name).encode()).hexdigest()[:32]
 metaText=f"""fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
  isReadable: 0
  textureType: 8
  textureShape: 1
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  textureFormat: 1
  maxTextureSize: 4096
  textureCompression: 0
  compressionQuality: 100
  spriteMode: 1
  spritePixelsToUnits: 100
  spriteMeshType: 0
  spriteExtrude: 1
  spritePivot: {{x: 0.5, y: 0.5}}
  spriteBorder: {{x: {border[0]}, y: {border[1]}, z: {border[2]}, w: {border[3]}}}
  alphaIsTransparency: 1
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID: {guid}
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
  assetBundleName:
  assetBundleVariant:
"""
 (path.with_name(path.name+".meta")).write_text(metaText,encoding="utf-8")
def crop(name,rect,border=(0,0,0,0),mask=None):
 x,y,w,h=rect;im=master.crop((x,y,x+w,y+h))
 if mask is not None:
  a=Image.new("L",(w,h),0);ImageDraw.Draw(a).polygon(mask,fill=255);im.putalpha(a)
 save(name,im,ART/"mail-clean-skin.png",rect,"crop approved text-free skin; optional polygon alpha only; no resampling",border)
save("mail_empty_frame",base,ART/"mail-empty-frame.png",[0,0,1932,814],"Byte-pixel-preserving runtime full base; no resampling")
crop("mail_row_selected",(211,199,538,81),(24,12,16,12))
crop("mail_row_normal",(218,280,529,79),(13,10,13,10))
crop("mail_envelope_unread",(240,287,88,66))
crop("mail_envelope_read",(240,446,88,67))
crop("mail_envelope_selected",(240,207,88,66))
crop("mail_gift",(696,207,33,35))
crop("mail_reward_coin",(951,585,116,98))
crop("mail_reward_crystal",(1099,585,116,98))
crop("mail_reward_mooncake",(1244,585,116,98))
crop("mail_reward_gourd",(1386,585,116,98))
# The empty reward field is a clean paper center with the exact original gold perimeter.
slot=master.crop((951,585,1067,683))
paper=base.crop((1390,592,1490,672)).resize((94,76),Image.Resampling.LANCZOS)
slot.paste(paper,(11,11))
save("mail_reward_slot",slot,ART/"mail-clean-skin.png",[951,585,116,98],"Crop original gold reward slot; replace only inner reward artwork with clean empty-frame paper; deterministic skin extraction",(12,12,12,12))
crop("mail_banner",(783,203,933,267))
crop("mail_button_all",(231,696,298,70),(42,22,42,22))
crop("mail_button_clean",(542,698,191,66),(28,18,28,18))
crop("mail_button_event",(1156,716,168,56),(20,16,20,16))
crop("mail_button_claim",(1326,709,234,66),(32,20,32,20))
crop("mail_button_delete",(1560,716,154,56),(25,16,25,16))
crop("mail_tab_selected",(225,88,148,58),(18,14,18,14))
normal=base.crop((225,88,373,146));save("mail_tab_normal",normal,ART/"mail-empty-frame.png",[225,88,148,58],"Crop neutral original tab without dynamic selected check",(18,14,18,14))
crop("mail_close",(1690,48,80,69))
# Runtime list rows contain only their skin; all unread/envelope/attachment state is rendered from MailUiState.
for key,rect,selected in [("mail_row_selected",(211,199,538,81),True),("mail_row_normal",(218,280,529,79),False)]:
 x,y,w,h=rect;row=master.crop((x,y,x+w,y+h))
 if selected:
  row.paste(row.crop((122,8,214,76)),(27,8))
  row.paste(row.crop((439,7,479,43)),(484,7))
 else:
  row.paste(base.crop((x+20,y+5,x+122,y+76)),(20,5))
  row.paste(base.crop((x+478,y+5,x+528,y+43)),(478,5))
 save(key,row,ART/"mail-clean-skin.png",list(rect),"Crop original row border and fill; remove only baked envelope/unread/gift pictograms with matching clean local skin donor pixels; runtime state draws icons",(24,12,16,12) if selected else (13,10,13,10))
for key,rect in [("mail_envelope_unread",(240,287,88,66)),("mail_envelope_read",(240,446,88,67)),("mail_envelope_selected",(240,207,88,66))]:
 x,y,w,h=rect;icon=master.crop((x,y,x+w,y+h));alpha=Image.new("L",(w,h),0)
 ImageDraw.Draw(alpha).polygon([(2,18),(75,4),(87,53),(6,65)],fill=255)
 if key!="mail_envelope_read":ImageDraw.Draw(alpha).rectangle((68,0,87,18),fill=0)
 icon.putalpha(alpha)
 save(key,icon,ART/"mail-clean-skin.png",list(rect),"Crop original envelope; polygon alpha keeps envelope art and excludes baked unread dot; runtime draws unread dot from state")
# Selected category glyph is stateful and is supplied separately rather than baked into all tabs.
tab=master.crop((225,88,373,146));tab.paste(tab.crop((58,8,95,49)),(18,8))
save("mail_tab_selected",tab,ART/"mail-clean-skin.png",[225,88,148,58],"Crop selected jade tab; replace check glyph only with same-tab blank jade paper",(18,14,18,14))
for key,rect in [("mail_category_all",(241,98,37,37)),("mail_category_system",(392,101,30,34)),("mail_category_event",(520,101,30,34)),("mail_category_reward",(646,99,34,36))]:
 x,y,w,h=rect;icon=master.crop((x,y,x+w,y+h))
 if key!="mail_category_all":
  alpha=Image.new("L",(w,h),0);pix=icon.load();a=alpha.load()
  for yy in range(h):
   for xx in range(w):
    r,g,b,_=pix[xx,yy]
    if r<205 and g<165 and b<130:a[xx,yy]=255
  icon.putalpha(alpha)
 save(key,icon,ART/"mail-clean-skin.png",list(rect),"Crop approved category pictogram; preserve colored nontext mark and remove neutral paper only")
items=list({item["key"]:item for item in items}.values())
gift=master.crop((696,207,729,242));alpha=Image.new("L",gift.size,0);pix=gift.load();a=alpha.load()
for yy in range(gift.height):
 for xx in range(gift.width):
  r,g,b,_=pix[xx,yy]
  if r>g*1.10 and g>b*1.20 and b<170:a[xx,yy]=255
gift.putalpha(alpha)
save("mail_gift",gift,ART/"mail-clean-skin.png",[696,207,33,35],"Crop original gift pictogram; alpha removes the jade row background so attachment state can be drawn over either row skin")
items=list({item["key"]:item for item in items}.values())
controls=Image.open(ART/"mail-controls-clean.png").convert("RGBA")
for key,rect,border in [("mail_row_selected",(211,199,538,81),(24,12,16,12)),("mail_row_normal",(218,280,529,79),(13,10,13,10)),("mail_reward_slot",(951,585,116,98),(12,12,12,12))]:
 x,y,w,h=rect
 save(key,controls.crop((x,y,x+w,y+h)),ART/"mail-controls-clean.png",list(rect),"Direct crop of AI-cleaned same-original control skin; no donor patches, no resampling",border)
items=list({item["key"]:item for item in items}.values())
for key in ("mail_reward_slot","mail_row_normal"):
 path=OUT/(key+".png.generation.json");record=json.loads(path.read_text(encoding="utf-8"))
 # Final rows and slot are direct crops from the precise AI cleanup, with no second donor image.
 path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
( ROOT/"sprite-manifest.json").write_text(json.dumps({"schemaVersion":1,"sourceCanvas":[1932,814],"designCanvas":[2560,1080],"uniformScale":min(2560/1932,1080/814),"sprites":items,"nativeParityVerified":False},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"sprites":len(items),"sourceCanvas":list(base.size),"output":str(OUT)}))

