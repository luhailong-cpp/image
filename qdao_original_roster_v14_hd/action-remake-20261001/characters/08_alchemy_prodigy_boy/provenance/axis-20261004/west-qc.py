from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/08_alchemy_prodigy_boy")
BATCH=ROOT/"provenance/axis-20261004"
slots=[("NW","06"),("NW","07"),("NW","14"),("NW","15"),("SW","13"),("SW","14"),("SW","15")]
metrics=[]
for d,n in slots:
    before=Image.open(ROOT/f"runtime/run/{d}/{n}.png").convert("RGBA")
    p=ROOT/f"generation/axis-20261004/{d}/{n}-v1.png"
    after=Image.open(p).convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS)
    a=np.asarray(before)[:,:,3]>128;b=np.asarray(after)[:,:,3]>128
    aa=a[:650];bb=b[:650]
    m={"slot":f"run/{d}/{n}","upperAlphaIoU":round(float((aa&bb).sum()/(aa|bb).sum()),5),
       "beforeBBox":before.getchannel("A").getbbox(),"candidateBBox":after.getchannel("A").getbbox()}
    metrics.append(m)
    sheet=Image.new("RGBA",(2048,1056),(238,234,217,255));sheet.alpha_composite(before,(0,32));sheet.alpha_composite(after,(1024,32))
    ImageDraw.Draw(sheet).text((5,8),f"{d}/{n} BEFORE -- AFTER whole canvas scale only; upper IoU {m['upperAlphaIoU']}",fill="black")
    sheet.convert("RGB").resize((1400,722),Image.Resampling.LANCZOS).save(BATCH/f"west-{d}-{n}-comparison.jpg",quality=92)
    recp=Path(str(p)+".generation.json")
    rec=json.loads(recp.read_text(encoding='utf-8'))
    rec["editInputSnapshot"]="provenance/axis-20261004/before-manifest.json"
    rec["evidence"]={"receipt":f"provenance/axis-20261004/west-{d}-{n}-v1.receipt.json","modelField":None,"qualityField":None}
    for ref in rec["references"]:
        ref["sha256"]=hashlib.sha256(Path(ref["path"]).read_bytes()).hexdigest()
    recp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
(BATCH/"west-registration-metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
print(json.dumps(metrics))
