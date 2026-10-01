import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
CLIENT=Path("D:/luyuan/wuxingqitan/mmorpg-client/Assets/Resources/World/Characters/QdaoOriginalRosterV13/03_lotus_healer_girl")
rows=[]
for d in ["N","NE","E","SE","S","SW","W","NW"]:
    for f in range(1,17):
        p=CLIENT/"walk"/d/f"{f:02}.png"
        with Image.open(p) as im: dims=list(im.size); mode=im.mode
        rows.append({"path":str(p),"direction":d,"frame":f,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size":dims,"mode":mode})
result={"characterId":"03_lotus_healer_girl","capturedAt":datetime.now(timezone.utc).isoformat(),"clientRoot":str(CLIENT),"readOnly":True,"frames":rows,"notes":["Old byte-distinct walk is not current run acceptance.","S/W and original identity prompt govern anatomical RIGHT lantern, LEFT bottle, LEFT lotus hair ornament.","Old E arm/ornament depth is inconsistent and must be corrected.","Old per-frame lowest alpha grounding must not be used for run export."]}
(ROOT/"baseline-audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"frames":len(rows),"sizes":sorted(set(tuple(x["size"]) for x in rows))}))

