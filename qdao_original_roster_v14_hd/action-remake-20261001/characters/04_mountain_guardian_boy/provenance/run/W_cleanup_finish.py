from pathlib import Path
import json,re,hashlib
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[2].resolve()
NOW=datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
owned=[ROOT/"provenance"/"hit",ROOT/"provenance"/"run"]
formal=list((ROOT/"frames"/"hit").glob("*/*.png"))+list((ROOT/"frames"/"run"/"W").glob("*.png"))+list((ROOT/"frames"/"run"/"NW").glob("*.png"))
assert len(formal)==44
formal_evidence=[]
for p in formal:
 j=json.loads(p.with_suffix(".generation.json").read_text(encoding="utf-8-sig"));assert j["sha256"]==sha(p)
 assert Image.open(p).size==(1024,1024)
 formal_evidence.append({"path":str(p.relative_to(ROOT)),"sha256":sha(p)})
candidates=[]
for p in owned[0].glob("*.png"):
 if re.match(r"^[EW]_",p.name):candidates.append(p)
for p in owned[1].glob("*.png"):
 if re.match(r"^(W|NW)_\d{2}_.*\.png$",p.name):candidates.append(p)
deleted=[]
# Recover the already-recorded deletions from the first pass, which stopped
# at the last file because its Pillow image handle was still open.
recovery_records=list(owned[0].glob('*.generation.json'))+[p for p in owned[1].glob('*.generation.json') if p.name.startswith(('W_','NW_'))]+[p.with_suffix('.generation.json') for p in formal]
recovered={}
def recover(obj):
 if isinstance(obj,dict):
  v=obj.get('file') or obj.get('path')
  if v and obj.get('deletedAt')=='2026-10-03T11:49:35.386713+00:00':
   p=Path(v)
   if not p.is_absolute():p=ROOT/p
   p=p.resolve()
   if p.parent in owned and p.suffix=='.png':
    recovered[str(p).casefold()]={'path':str(p.relative_to(ROOT)),'absolutePath':str(p),'sha256':obj.get('sha256'),'pixelSize':([obj['width'],obj['height']] if 'width' in obj else obj.get('pixelDimensions') or obj.get('dimensions')),'mode':obj.get('mode','RGBA'),'reason':'正式导出确认后删除原生/拒稿；本记录从删除前已保存的逐图来源文字恢复。','deletedAt':obj['deletedAt']}
  for v in obj.values():
   if isinstance(v,(dict,list)):recover(v)
 elif isinstance(obj,list):
  for v in obj:recover(v)
for p in recovery_records:recover(json.loads(p.read_text(encoding='utf-8-sig')))
deleted=list(recovered.values())
for p in candidates:
 p=p.resolve();assert p.is_relative_to(ROOT/"provenance")
 assert p.parent in owned
 im=Image.open(p)
 deleted.append({"path":str(p.relative_to(ROOT)),"absolutePath":str(p),"sha256":sha(p),"pixelSize":list(im.size),"mode":im.mode,"reason":"已正式导出且本轮生成均完成；原图/拒稿/中间图删除，逐图文字模型、提交、回执及来源SHA保留。","deletedAt":NOW})
 im.close()
deleted=list({x['absolutePath'].casefold():x for x in deleted}.values())
save(ROOT/'provenance/run/W_NW_cleanup_plan_20261003.json',{'createdAt':NOW,'planned':deleted,'firstPassNote':'首轮最后一张被本脚本Pillow句柄占用；已关闭句柄，已删除项由删除前写入的来源标记恢复。'})
lookup={str(Path(x["absolutePath"]).resolve()).casefold():x for x in deleted}
def resolve_ref(v):
 try:
  p=Path(v)
  if not p.is_absolute():p=ROOT/p
  return str(p.resolve()).casefold()
 except Exception:return ""
def walk(obj):
 changed=False
 if isinstance(obj,dict):
  if "path" in obj and resolve_ref(obj["path"]) in lookup:
   obj["fileRetained"]=False;obj["retentionNote"]="用户2026-09-23素材保留要求：正式导出确认后删除原生/拒稿像素，来源SHA与调用文字证据保留。";obj["deletedAt"]=NOW;changed=True
  if "file" in obj and resolve_ref(obj["file"]) in lookup:
   obj["fileRetained"]=False;obj["artifactState"]="native_or_intermediate_pixels_deleted_after_export";obj["deletedAt"]=NOW;changed=True
  for v in list(obj.values()):
   if isinstance(v,(dict,list)):changed=walk(v) or changed
 elif isinstance(obj,list):
  for v in obj:changed=walk(v) or changed
 return changed
records=list(owned[0].glob("*.generation.json"))+[p for p in owned[1].glob("*.generation.json") if p.name.startswith(("W_","NW_"))]+[p.with_suffix(".generation.json") for p in formal]
for p in records:
 j=json.loads(p.read_text(encoding="utf-8-sig"))
 if walk(j):save(p,j)
# Each exact PNG was resolved and checked against owned directory before deletion.
for x in deleted:
 p=Path(x["absolutePath"]);assert p.resolve().parent in owned
 if p.exists():
  assert sha(p)==x["sha256"];p.unlink()
for action in ("hit","run"):
 items=[x for x in deleted if f"provenance/{action}/" in x["path"].replace("\\","/")]
 out=ROOT/"provenance"/action/("cleanup_hit_finish_20261003.json" if action=="hit" else "W_NW_cleanup_finish_20261003.json")
 save(out,{"createdAt":NOW,"scope":"hit12" if action=="hit" else "run W16/NW16","reason":"成品已落盘且逐图来源文字完整；当前正式帧与动态预览保留，不保留原图、拒稿和中间图。","finalExportsVerified": [x for x in formal_evidence if f"frames/{action}/" in x["path"].replace("\\","/")],"deleted":items,"dynamicReview":"pending_parent_review; 后续编辑直接使用当前正式帧，未伪报动态通过"})
print(json.dumps({"verifiedFinalFrames":len(formal),"deletedNativeOrIntermediate":len(deleted),"remainingOwnedNative":sum(p.exists() for p in candidates)},ensure_ascii=False))

