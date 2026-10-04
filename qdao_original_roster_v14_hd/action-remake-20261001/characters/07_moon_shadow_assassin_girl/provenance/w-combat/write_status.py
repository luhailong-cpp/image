import json, hashlib
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
ROOT=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl")
slots=[]
counts={"hit":6,"attack":12,"cast":16}
for action,count in counts.items():
 for n in range(1,count+1):
  p=ROOT/"staging"/action/"W"/f"{n:02d}.png"
  record=Path(str(p)+".generation.json")
  s={"action":action,"direction":"W","frame":n,"status":"generated_pending_sequence" if p.exists() else "missing","file":str(p.relative_to(ROOT)) if p.exists() else None,"request":f"provenance/w-combat/{action}-W-{n:02d}.request.json","prompt":f"provenance/w-combat/{action}-W-{n:02d}.prompt.txt","durationMs":40 if action=="hit" else 30 if action=="attack" else 45,"event":"hit_recoil_peak" if action=="hit" and n==3 else "contact" if action=="attack" and n==6 else "release" if action=="cast" and n==9 else None}
  if p.exists():
   im=Image.open(p);im.load()
   a=im.getchannel("A")
   rec=json.loads(record.read_text(encoding="utf-8"))
   s["request"]=rec["prompt"]
   s["prompt"]=rec["prompt"]
   s["actualReferences"]=rec["references"]
   s.update({"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"nativeSize":list(im.size),"mode":im.mode,"alphaRange":a.getextrema(),"generationRecord":str(record.relative_to(ROOT)),"alphaBoundsByThreshold":{str(t):a.point(lambda v,t=t:255 if v>t else 0).getbbox() for t in [0,8,32,127,240]},"visualStatus":"initial_pose_review_only","sequenceAccepted":False,"exported1024":False,"clientIntegrated":False})
  slots.append(s)
o={"updatedAt":datetime.now(timezone.utc).isoformat(),"userTimezone":"America/New_York","expected":34,"generated":sum(s["status"]!="missing" for s in slots),"missing":sum(s["status"]=="missing" for s in slots),"modelTarget":"gpt-image-2.5-sunburst","qualityTarget":"max","actualModel":None,"actualQuality":None,"actualParametersReason":"宿主管理，工具未开放或披露model/quality；目标不代表实际确认。","inputReferences":["D:/work/image/q_daoist_character_pack_4096/07_moon_shadow_assassin_girl_transparent_4096.png","D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/07-tools/candidate/07_moon_shadow_assassin_girl/idle/W.png","D:/work/image/designs/jubaozhai-ui/02-characters.png"],"rootAnchor":{"intendedNormalized":[0.5,0.8984375],"intendedOn1024":[512,920],"status":"prompt target; measured uniform camera/root acceptance pending"},"blocker":{"frame":"hit W02","consecutiveFailures":3,"rawError":"image generation failed: network error: error sending request","switchedToAPI":False},"slots":slots}
o["blocker"]=None
o["networkHistory"]={"state":"recovered","failureEvidenceRetained":True,"routeChanged":False}
o["reviewNotes"]=["34 native independent frames complete, not 34 final game exports.","All current frames were actually viewed as generated; identity/hands/feet initial review passed.","Attack11 and Cast02/11 were redrawn to remove obvious phase reversal; replaced image records retained.","Full playback, uniform camera/root coherence, low-alpha fringe cleanup and formal 1024 export remain pending root review."]
(ROOT/"provenance"/"w-combat"/"STATUS.json").write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"generated":o["generated"],"missing":o["missing"],"existing":[{"file":s["file"],"bounds":s.get("alphaBoundsByThreshold")} for s in slots if s["file"]]},ensure_ascii=False,indent=2))

