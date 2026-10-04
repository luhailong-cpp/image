from pathlib import Path
import argparse,hashlib,json,re,shutil
from datetime import datetime,timezone
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
PROV=ROOT/"provenance"/"hit"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return Path(p).relative_to(ROOT).as_posix()
p=argparse.ArgumentParser()
p.add_argument("--source",required=True)
p.add_argument("--stem",required=True)
p.add_argument("--review",default="candidate_pending_visual")
p.add_argument("--old-edit-target")
a=p.parse_args()
submission_path=PROV/(a.stem+".submission.json")
sub=json.loads(submission_path.read_text(encoding="utf-8-sig"))
receipt_path=PROV/(a.stem+".receipt.json")
receipt=json.loads(receipt_path.read_text(encoding="utf-8-sig"))
source=Path(a.source)
raw=source.read_bytes()
source_sha=sha(source)
with Image.open(source) as im:
 im.load()
 if im.format!="PNG" or im.mode!="RGBA" or im.width!=im.height or min(im.size)<1024: raise ValueError("invalid native frame")
 size=list(im.size)
 alpha=list(im.getchannel("A").getextrema())
 if alpha[0]!=0 or alpha[1]!=255: raise ValueError("invalid transparency")
 exported=im.copy() if im.size==(1024,1024) else im.resize((1024,1024),Image.Resampling.LANCZOS)
native=PROV/(a.stem+".native.png")
if native.exists() and sha(native)!=source_sha: raise ValueError("native path collision")
if not native.exists(): shutil.copy2(source,native)
refs=[]
for idx,path in enumerate(sub["submittedParameters"]["referenced_image_paths"],1):
 q=Path(path)
 original=q
 relocated=False
 if not q.exists() and idx==1 and a.old_edit_target:
  q=Path(a.old_edit_target); relocated=True
 if not q.exists(): raise ValueError("missing reference "+str(original))
 with Image.open(q) as im: dimensions=list(im.size)
 refs.append({"inputIndex":idx,"path":original.as_posix(),"sha256":sha(q),"pixelDimensions":dimensions,"readableEvidencePath":q.as_posix(),"relocatedAfterSubmission":relocated,"roleEvidence":"见实际prompt"})
out=ROOT/"frames"/"hit"/sub["direction"]/("frame_%02d.png"%sub["frame"])
if out.exists(): raise ValueError("refuse overwrite "+str(out))
out.parent.mkdir(parents=True,exist_ok=True)
exported.save(out)
times=re.findall(rb"20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z",raw)
generated_at=times[0].decode() if times else None
rec={"schemaVersion":1,"character":ROOT.name,"action":"hit","direction":sub["direction"],"frame":sub["frame"],"file":rel(out),"sha256":sha(out),"generatedAt":generated_at,"generationTimeEvidence":{"startedAt":sub.get("startedAt"),"completedAt":receipt.get("completedAt"),"c2paTextTimeCandidates":[x.decode() for x in times[:4]],"note":"PNG C2PA time文本摘录未独立验签；调用边界不是精确生成时刻。"},"exportedAt":datetime.now(timezone.utc).isoformat(),"width":1024,"height":1024,"format":"PNG","mode":"RGBA","alphaExtrema":list(exported.getchannel("A").getextrema()),"tool":"image_gen.imagegen","route":"builtin","configSnapshot":sub["configTarget"],"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":sub["submittedParameters"]["referenced_image_paths"],"prompt":rel(PROV/(a.stem+".prompt.txt"))},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露具体版本或质量；PNG泛称gpt-image不确认Sunburst/max。","references":refs,"evidence":{"submission":{"path":rel(submission_path),"sha256":sha(submission_path)},"receipt":{"path":rel(receipt_path),"sha256":sha(receipt_path)},"originalHostSource":source.as_posix()},"nativeSource":{"path":rel(native),"sha256":source_sha,"width":size[0],"height":size[1],"format":"PNG","mode":"RGBA","alphaExtrema":alpha},"derivedFrom":[{"path":rel(native),"sha256":source_sha}],"operation":{"type":"whole_canvas_uniform_resize","sourceSize":size,"targetSize":[1024,1024],"scaleX":1024/size[0],"scaleY":1024/size[1],"translation":[0,0],"crop":None,"bboxAlignment":False,"footAlignment":False,"mirroring":False,"poseInterpolation":False},"rootAnchor":{"x":512,"y":928,"units":"export_canvas_pixels","status":"declared_layout_target_not_pixel_verified"},"frameDurationMs":40,"review":{"status":a.review,"automaticallyApproved":False},"clientIntegration":"not_integrated"}
out.with_suffix(".generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"file":str(out),"sha256":sha(out),"nativeSha256":source_sha,"nativeSize":size,"generatedAt":generated_at,"review":a.review},ensure_ascii=False))

