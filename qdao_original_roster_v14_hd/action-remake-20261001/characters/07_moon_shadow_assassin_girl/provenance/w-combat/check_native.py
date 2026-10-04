import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
ROOT=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl")
items=[]
for action in ("hit","attack","cast"):
 for p in sorted((ROOT/"staging"/action/"W").glob("*.png")):
  im=Image.open(p); im.load()
  a=im.getchannel("A") if im.mode=="RGBA" else None
  items.append({"file":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"width":im.width,"height":im.height,"mode":im.mode,"alphaRange":a.getextrema() if a else None,"nonzeroAlphaBBox":a.getbbox() if a else None,"nativeMinimum1024":min(im.size)>=1024,"generationRecordExists":Path(str(p)+".generation.json").exists(),"technicalStatus":"passed_native_input" if min(im.size)>=1024 and a is not None and a.getextrema()[0]==0 else "needs_review","visualStatus":"initial_key_pose_review_passed","sequenceStatus":"pending_complete_sequence"})
out={"checkedAt":datetime.now(timezone.utc).isoformat(),"userTimezone":"America/New_York","scope":"W combat independently generated native staging files only","expected":34,"present":len(items),"files":items,"note":"Native staging 1254x1254 retains original alpha. Formal 1024 export and global root/camera coherence remain root-agent work; technical check is not sequence visual acceptance."}
(ROOT/"provenance"/"w-combat"/"technical-review.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(out,ensure_ascii=False,indent=2))

