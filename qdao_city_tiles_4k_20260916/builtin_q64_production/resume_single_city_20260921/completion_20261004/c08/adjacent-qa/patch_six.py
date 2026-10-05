from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys,shutil,datetime
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=json.loads((R/"tone-v2-bindings.json").read_text())["sources"]
boxes={"gold-top":[7565,0,8819,1254],"corner-left":[3469,3469,4723,4723],"corner-right":[7565,3469,8819,4723]}
def offset(k):
 return (int(k[5:])-7)*4096,(int(k[1:3])-8)*4096
def crop(a,box):
 x0,y0,x1,y1=box;out=np.zeros((y1-y0,x1-x0,3),np.uint8);parts=[]
 for k,im in a.items():
  ox,oy=offset(k);ix0=max(x0,ox);iy0=max(y0,oy);ix1=min(x1,ox+4096);iy1=min(y1,oy+4096)
  if ix0<ix1 and iy0<iy1:
   out[iy0-y0:iy1-y0,ix0-x0:ix1-x0]=im[iy0-oy:iy1-oy,ix0-ox:ix1-ox]
   parts.append({"tile":k,"source":bind[k],"tileCropLTRB":[ix0-ox,iy0-oy,ix1-ox,iy1-oy],"destinationLTRB":[ix0-x0,iy0-y0,ix1-x0,iy1-y0]})
 return out,parts
a={k:np.array(Image.open(v["file"]).convert("RGB")) for k,v in bind.items()}
if sys.argv[1]=="prepare":
 for name,box in boxes.items():
  P=R/name;P.mkdir(exist_ok=True);out,parts=crop(a,box);Image.fromarray(out).save(P/"context.png")
  rec={"file":str(P/"context.png"),"sha256":sha(P/"context.png"),"globalWindowLTRB":box,"parts":parts,"operation":"Native crop/concat; no resize"}
  (P/"context.png.generation.json").write_text(json.dumps(rec,indent=2),encoding="utf-8")
 print("Prepared3 native1254windows")
else:
 O=R/"coupled-v1";O.mkdir(exist_ok=True);repairs=[]
 hosts=json.loads((R/"hosts.json").read_text())
 for name,box in boxes.items():
  P=R/name;host=Path(hosts[name]);shutil.copy2(host,P/"native.png")
  native=np.array(Image.open(P/"native.png").convert("RGB"));assert native.shape==(1254,1254,3)
  ctx,parts=crop(a,box);y,x=np.mgrid[:1254,:1254]
  edge=np.minimum.reduce([x,1253-x,1253-y]) if box[1]==0 else np.minimum.reduce([x,y,1253-x,1253-y])
  t=np.clip((edge-16)/112,0,1);alpha=np.rint(t*t*(3-2*t)*255).astype(np.uint8)
  joined=((ctx.astype(np.uint32)*(255-alpha[:,:,None])+native.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
  Image.fromarray(joined).save(P/"composite.png");Image.fromarray(alpha).save(P/"mask.png")
  for part in parts:
   tx0,ty0,tx1,ty1=part["tileCropLTRB"];dx0,dy0,dx1,dy1=part["destinationLTRB"]
   a[part["tile"]][ty0:ty1,tx0:tx1]=joined[dy0:dy1,dx0:dx1]
  pbox=[max(0,box[0]-160),max(0,box[1]-160),min(12288,box[2]+160),min(8192,box[3]+160)]
  per,_=crop(a,pbox);Image.fromarray(per).save(P/"perimeter.png")
  g={"file":str(P/"native.png"),"sha256":sha(P/"native.png"),"pixels":[1254,1254],"recordedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"tool":"image_gen.imagegen","route":"builtin","actualModel":None,"actualQuality":None,"generatedAt":None,"submittedParameters":{"model":None,"quality":None,"size":None,"transparent_background":False},"configSnapshot":json.loads((R.parent/"config.snapshot.json").read_text()),"prompt":str(P/"prompt.txt"),"references":[json.loads((P/"context.png.generation.json").read_text()),{"file":"D:/work/image/designs/gameplay-ui/04-guild.png","sha256":sha("D:/work/image/designs/gameplay-ui/04-guild.png"),"role":"approved style"}],"evidence":{"hostSavedOriginal":str(host),"copyByteIdentical":sha(host)==sha(P/"native.png"),"toolResponse":str(P/"tool-response.json")},"unverifiedReason":"Builtin host did not expose actual model/quality/generation time."}
  (P/"native.png.generation.json").write_text(json.dumps(g,indent=2),encoding="utf-8")
  repairs.append({"name":name,"globalWindowLTRB":box,"native":g["file"],"nativeSha256":g["sha256"],"generationRecord":str(P/"native.png.generation.json"),"mask":str(P/"mask.png"),"parts":parts})
 outputs={}
 for k,im in a.items():
  p=O/(k+".png");Image.fromarray(im).save(p);outputs[k]={"file":str(p),"sha256":sha(p),"pixels":[4096,4096]}
 rec={"sources":outputs,"derivedFrom":bind,"repairs":repairs,"operation":"3 disjoint native1254 repairs composited with16..128px context margins. No scale/warp/source blur. Top boundary lacks yfade for top-touching window.","formalAccepted":False}
 (R/"coupled-v1-bindings.json").write_text(json.dumps(rec,indent=2),encoding="utf-8")
 print(json.dumps(outputs,indent=2))
