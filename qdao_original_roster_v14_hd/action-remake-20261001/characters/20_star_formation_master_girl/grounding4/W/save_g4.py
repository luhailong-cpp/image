from pathlib import Path
from PIL import Image
import sys,json,hashlib,shutil,datetime
BASE=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/20_star_formation_master_girl")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,obj): Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
receipt=Path(sys.argv[1]); r=json.loads(receipt.read_text(encoding="utf-8")); stem=receipt.name.removesuffix(".receipt.json"); folder=receipt.parent
reqpath=folder/(stem+".request.json"); req=json.loads(reqpath.read_text(encoding="utf-8"))
native=folder/(stem+"-native.png"); final=folder/(stem+".png")
existing_record=folder/(stem+".png.generation.json")
if existing_record.exists() and native.exists() and final.exists():
    old=json.loads(existing_record.read_text(encoding="utf-8"))
    if old["native"]["sha256"]==sha(native) and old["export"]["sha256"]==sha(final):
        print(json.dumps({"file":str(final),"already_saved":True,"sha256":sha(final)})); sys.exit(0)
src=Path(r["host_png"]); shutil.copyfile(src,native)
im=Image.open(native)
if im.mode!="RGBA": raise RuntimeError("Host output is not RGBA")
if min(im.size)<1024 or im.width!=im.height: raise RuntimeError("Unexpected native canvas "+str(im.size))
if im.size==(1024,1024): shutil.copyfile(native,final); operation={"type":"copy","resizeCount":0}
else: im.resize((1024,1024),Image.Resampling.LANCZOS).save(final); operation={"type":"full_canvas_uniform_resize","from":list(im.size),"to":[1024,1024],"resample":"LANCZOS","resizeCount":1,"offset":[0,0],"usesBoundingBox":False,"alignsLowestPixel":False}
refs=[]
for i,p in enumerate(req["submitted"]["referenced_image_paths"]):
    fp=Path(p); ent={"path":p,"role":req["reference_roles"][i],"sha256":sha(fp)}
    sidecar=Path(str(fp)+".generation.json")
    if sidecar.exists(): ent["source_generation_record"]=str(sidecar).replace("\\","/"); ent["source_generation_record_sha256"]=sha(sidecar); ent["source_generation_record_snapshot"]=json.loads(sidecar.read_text(encoding="utf-8"))
    refs.append(ent)
record={"schema_version":1,"created_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"model":None,"quality":None,"actual_returned":{"model":None,"quality":None,"generation_id":None},"configuration_target":{"model":"gpt-image-2.5-sunburst","quality":"max","builtin_product":"ChatGPT Images 2.5"},"target_confirmation":"宿主管理入口无型号/质量选择器，返回未披露；不能将配置目标当作实测","submitted":req["submitted"],"references":refs,"prompt_file":str(folder/(stem+".prompt.txt")).replace("\\","/"),"prompt_sha256":sha(folder/(stem+".prompt.txt")),"receipt":str(receipt).replace("\\","/"),"receipt_sha256":sha(receipt),"native":{"file":str(native).replace("\\","/"),"sha256":sha(native),"size":list(im.size),"mode":im.mode},"export":{"file":str(final).replace("\\","/"),"sha256":sha(final),"size":[1024,1024],"mode":"RGBA","operation":operation},"phase_spec":req["phase_spec"],"status":"awaiting_static_visual_review","clientIntegration":"not_integrated"}
dump(folder/(stem+".png.generation.json"),record)
print(json.dumps({"file":str(final),"native_size":list(im.size),"sha256":sha(final)}))
