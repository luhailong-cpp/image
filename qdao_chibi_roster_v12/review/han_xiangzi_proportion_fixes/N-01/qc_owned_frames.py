from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, subprocess, sys
import numpy as np

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT))
from edge_despill import despill
PROCESSOR = Path.home() / ".agents/skills/generate2dsprite/scripts/generate2dsprite.py"
GENERATED = Path(r"C:\Users\luyua\.codex\generated_images\01a09f27-47ad-7342-9c26-85f9c1e456c1")
CASES = {
 "N-01": [("candidate", "exec-a36a442b-6038-4b93-a40f-80a88073ce8e.png", "prompt.txt", "rejected: head remains slightly small"), ("final", "exec-7d8effeb-5cd4-477b-8099-5a094a9f9a19.png", "prompt-revision02.txt", "selected")],
 "NE-01": [("final", "exec-40c19900-17bb-4a1c-8657-5339543526d7.png", "prompt.txt", "selected")],
 "SE-01": [("candidate", "exec-286c3262-4158-48d7-8760-7377cf275ca5.png", "prompt.txt", "rejected: head width unchanged"), ("final", "exec-5a1a90a6-561a-4a12-80be-a7d013ffe4bb.png", "prompt-revision02.txt", "selected")],
 "SE-03": [("candidate", "exec-d00c5e98-83d8-42c7-83c8-61341315f924.png", "prompt.txt", "rejected: head over-shrunk and body placement changed"), ("final", "exec-cb3333ba-99c4-473c-92d5-007b18de9d87.png", "prompt-revision02.txt", "selected")]
}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def masks(image):
 a=np.asarray(image.convert("RGB")).astype(int)
 r,g,b=a.transpose(2,0,1)
 fg=~((r>180)&(b>180)&(g<110))
 dark=(r<120)&(g<120)&(b<120)&fg
 return fg,dark

def measure(path):
 im=Image.open(path).convert("RGB")
 fg,dark=masks(im);ys,xs=np.where(fg);top=int(ys.min());widths=[];core=[]
 for y in range(top+35,min(im.height,top+140)):
  xx=np.where(dark[y])[0]
  if len(xx)>10:widths.append(int(xx[-1]-xx[0]+1))
  changes=np.diff(np.r_[False,dark[y],False].astype(int));starts=np.where(changes==1)[0];ends=np.where(changes==-1)[0]
  runs=[(s,e) for s,e in zip(starts,ends) if e-s>=4]
  if runs:core.append(int(runs[-1][1]-runs[0][0]))
 return {"size":list(im.size),"bbox_xyxy":[int(xs.min()),top,int(xs.max()+1),int(ys.max()+1)],"silhouette_height":int(ys.max()-ys.min()+1),"dark_row_span_p90":float(np.percentile(widths,90)),"dark_core_run4_span_p90":float(np.percentile(core,90))}

def body_translation(original,final):
 o,_=masks(original);n,_=masks(final);h,w=o.shape;o[:230]=False;best=(-1,0,0)
 for dy in range(-25,26):
  nn=n.copy();nn[:230+dy]=False
  for dx in range(-20,21):
   a=o[max(0,-dy):min(h,h-dy),max(0,-dx):min(w,w-dx)]
   b=nn[max(0,dy):min(h,h+dy),max(0,dx):min(w,w+dx)]
   inter=int((a&b).sum());union=int(o.sum()+nn.sum()-inter);iou=inter/union
   if iou>best[0]:best=(iou,dx,dy)
 return {"best_translation_original_to_final_xy":[best[1],best[2]],"lower_body_silhouette_iou":best[0],"roi":"original y>=230, same cut translated with body; diagnostic only, never applied to final artwork"}

for key,history in CASES.items():
 folder=BASE/key
 original=Image.open(folder/"original-cell.png").convert("RGB");final=Image.open(folder/"final-cell.png").convert("RGB");idle=Image.open(folder/"reference-idle-native.png").convert("RGB")
 entries=[]
 for name,source,prompt,status in history:
  raw=folder/(name+"-raw.png");assert sha(raw)==sha(GENERATED/source)
  cell=folder/(name+"-cell.png");assert np.array_equal(np.asarray(Image.open(raw).resize((443,443),Image.Resampling.LANCZOS)),np.asarray(Image.open(cell)))
  entries.append({"name":name,"built_in_imagegen_source":str(GENERATED/source),"raw_file":str(raw),"raw_sha256":sha(raw),"native_size":list(Image.open(raw).size),"prompt_file":prompt,"prompt_sha256":sha(folder/prompt),"status":status,"metrics_at443":measure(cell)})
 provenance={"character":"30_han_xiangzi","direction":key.split("-")[0],"phase":int(key.split("-")[1]),"generator":"built-in image_gen edit; native art references visible in conversation","original_reference_provenance":"reference-sources.json","generation_history":entries,"selected_raw":"final-raw.png","selected_raw_sha256":sha(folder/"final-raw.png"),"selected_cell":"final-cell.png","selected_cell_sha256":sha(folder/"final-cell.png"),"normalization":{"source_box":[0,0,1254,1254],"operation":"whole square Lanczos resize1254 to443","scale":443/1254,"body_bbox_fit":False,"part_scaling":False,"pasted_anatomy":False,"mirroring":False,"interpolation_between_poses":False},"production_modified":False}
 (folder/"final-provenance.json").write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 measurements={"method":"Native443 square color mask excludes bright solid magenta. Dark rows35..139 below first visible top, RGB each<120. Span P90 can include thin ribbon outlines; core variant retains runs>=4px to reduce ribbon-outline bias. Metrics only screen, never drive pixel scaling.","original":measure(folder/"original-cell.png"),"final":measure(folder/"final-cell.png"),"reference_idle":measure(folder/"reference-idle-native.png"),"reference_phase02":measure(folder/"reference-phase02-cell.png"),"reference_phase03":measure(folder/"reference-phase03-cell.png"),"body_translation":body_translation(original,final),"whole_cell_normalization_only":True}
 (folder/"measurements.json").write_text(json.dumps(measurements,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 board=Image.new("RGB",(1329,471),(26,38,38));draw=ImageDraw.Draw(board)
 for col,(label,img) in enumerate([("Original walk "+key,original),("New authored walk "+key,final),("Normal same-direction idle",idle)]):
  draw.text((col*443+10,7),label,fill="white");board.paste(img,(col*443,28))
 board.save(folder/"before-after-native.png")
 command=[sys.executable,str(PROCESSOR),"process","--input",str(folder/"final-cell.png"),"--target","player","--mode","walk","--rows","1","--cols","1","--cell-size","443","--fit-scale","1","--scale-strategy","preserve","--align","center","--component-mode","largest","--component-padding","0","--trim-border","0","--edge-clean-depth","0","--output-dir",str(folder/"qc-processing")]
 result=subprocess.run(command,capture_output=True,text=True,encoding="utf-8",errors="replace")
 (folder/"qc-processor.log").write_text(result.stdout+result.stderr,encoding="utf-8");assert result.returncode==0,result.stderr
 meta=json.loads((folder/"qc-processing/pipeline-meta.json").read_text(encoding="utf-8"));f=meta["frames"][0]
 for gate in ["source_edge_touch","output_edge_touch","paste_clamped","is_empty"]:assert not f.get(gate),(key,gate)
 cleaned=Image.open(folder/"qc-processing/raw-sheet-clean.png").convert("RGBA");cleaned,stats=despill(cleaned,4,12);cleaned.save(folder/"qc-despill4.png")
 darkbg=Image.new("RGBA",cleaned.size,(38,55,55,255));darkbg.alpha_composite(cleaned);darkbg.convert("RGB").save(folder/"qc-despill4-dark.png")
 (folder/"qc-despill4-stats.json").write_text(json.dumps(stats,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"key":key,"original":measurements["original"],"final":measurements["final"],"body_translation":measurements["body_translation"],"no_edge_touch_or_clamp":True},ensure_ascii=False),flush=True)
