from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/08_alchemy_prodigy_boy")
B=ROOT/"provenance/axis-20261004"
selection={}
for d,nums in {"NW":["06","07","14","15"],"SW":["13","14","15"]}.items():
    for n in nums:
        v=4 if (d,n)==("NW","14") else 1
        source=f"generation/axis-20261004/{d}/{n}-v{v}.png"
        reason="收回后蹬支撑鞋的侧向外撇，使踝与鞋掌保持西北运动平面；保留自然抬跟。" if d=="NW" else "前摆靴收回膝下运动平面，消除过大正面鞋底透视与相邻帧突转，保留抬脚。"
        if (d,n)==("NW","14"):reason+="第四版从原正式帧修鞋掌朝向，保留原膝位腿长，前掌底936接近原931。"
        selection[f"run/{d}/{n}"]={"source":source,"reason":reason,"staticReviewed":True}
        recp=Path(str(ROOT/source)+".generation.json")
        rec=json.loads(recp.read_text(encoding="utf-8"))
        rec["editInputSnapshot"]="provenance/axis-20261004/before-manifest.json"
        rec["evidence"]={"receipt":f"provenance/axis-20261004/west-{d}-{n}-v{v}.receipt.json","modelField":None,"qualityField":None}
        for ref in rec["references"]:ref["sha256"]=hashlib.sha256(Path(ref["path"]).read_bytes()).hexdigest()
        rec["visualStatus"]="static_sequence_reviewed"
        rec["staticReview"]={"yaw":"accepted","upperRegistration":"accepted","phase":"preserved","clientDynamicAccepted":False}
        if v==2:rec.pop("startedAt",None)
        recp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
p=B/"west-NW-14-v2.job.json";j=json.loads(p.read_text(encoding="utf-8"));j.pop("startedAt",None);p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding="utf-8")
(B/"west-selection.json").write_text(json.dumps(selection,ensure_ascii=False,indent=2),encoding="utf-8")
metrics=[]
for d in ["W","NW","SW"]:
    sheet=Image.new("RGBA",(2048,1120),(236,231,215,255));dr=ImageDraw.Draw(sheet)
    for i in range(16):
        n=f"{i+1:02}";slot=f"run/{d}/{n}"
        p=ROOT/selection[slot]["source"] if slot in selection else ROOT/f"runtime/run/{d}/{n}.png"
        im=Image.open(p).convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS)
        if slot in selection:
            before=Image.open(ROOT/f"runtime/run/{d}/{n}.png").convert("RGBA")
            a=np.asarray(before)[:,:,3]>128;b=np.asarray(im)[:,:,3]>128
            upper=float((a[:650]&b[:650]).sum()/(a[:650]|b[:650]).sum())
            # Bottom of support in selected rear-support phase. Crop restricts swing-foot / robe.
            x0,x1=(520,800) if d=="NW" and n in ("06","07") else ((300,520) if d=="NW" else (580,820))
            oldy=np.where(a[800:,x0:x1])[0];newy=np.where(b[800:,x0:x1])[0]
            metrics.append({"slot":slot,"upperAlphaIoU":round(upper,5),"supportBottomBefore":int(oldy.max()+800) if len(oldy) else None,"supportBottomAfter":int(newy.max()+800) if len(newy) else None})
        x=(i%8)*256;y=(i//8)*560
        dr.text((x+6,y+6),f"{slot} {'EDIT' if slot in selection else 'KEEP'}",fill="black")
        sheet.alpha_composite(im.resize((256,256),Image.Resampling.LANCZOS),(x,y+25))
        leg=im.crop((160,620,880,1000)).resize((256,135),Image.Resampling.LANCZOS)
        sheet.alpha_composite(leg,(x,y+295))
    sheet.convert("RGB").save(B/f"west-{d}-selected-sequence.jpg",quality=95)
(B/"west-final-metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
print(json.dumps(metrics))
