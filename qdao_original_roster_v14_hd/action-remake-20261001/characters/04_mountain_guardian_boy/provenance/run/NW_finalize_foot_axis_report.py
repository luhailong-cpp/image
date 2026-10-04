from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
R=Path("D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy")
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=R/"provenance/run/NW_foot_axis_review_20261003.json";a=load(p)
m=load(R/"frames/run/NW/frame_02.generation.json")
f=a["frames"][1];f.update({"sha256":m["sha256"],"nativeSource":m["nativeSource"],"observation":"脚向先转正为跟近趾远向左上，再局部延展承重小腿；当前鞋底y964，03鞋底y955，差9px。髋/躯干没有整图下移，长杖与另一回收腿保持。"})
assert sha(R/f["file"])==f["sha256"]
def sole(im):
    aa=im.convert("RGBA").getchannel("A").crop((510,800,645,995)).point(lambda x:255 if x>=128 else 0)
    return aa.getbbox()[3]+800-1
with Image.open(R/"provenance/run/NW_02_foot_axis_attempt01.png") as old:
    old_y=sole(old.resize((1024,1024),Image.Resampling.LANCZOS))
with Image.open(R/"frames/run/NW/frame_02.png") as im: y2=sole(im)
with Image.open(R/"frames/run/NW/frame_03.png") as im: y3=sole(im)
a["reviewedAt"]=datetime.now(timezone.utc).isoformat()
a["supportContinuity"]={"frames":[2,3],"before02SoleY":old_y,"after02SoleY":y2,"03SoleY":y3,"beforeAbsoluteDelta":abs(old_y-y3),"afterAbsoluteDelta":abs(y2-y3),"method":"仅分析预先确认支撑靴区域[x510,y800,x645,y995]内alpha>=128鞋底下沿；没有修改像素或按最低像素移动角色。","decision":"局部小腿延展后同脚承重高度衔接可接受；正常/慢速终审由根完成。"}
dump(p,a)
np=R/"RUN_NW_NOTES.md";tx=np.read_text(encoding="utf-8")
tx=tx.replace("02/16采用attempt01。","02最终采用NW_02_grounded_axis_attempt01；16采用foot_axis_attempt01。")
tx=tx.replace("修图实际传入目标帧、07同向正式帧、本角色identity、NW idle与designs风格共5张。","脚向修图实际传入目标帧、07同向正式帧、本角色identity、NW idle与designs风格共5张；02接地末修以本角色NW03代替07作同侧鞋底高度参考，其余4张仍实传。")
tx+=f"\n最后NW02接地连续修复：只延展支撑小腿，固定髋/躯干与另一回收腿；鞋底从y{old_y}改为y{y2}，相邻03为y{y3}，同侧鞋底差从{abs(old_y-y3)}px降至{abs(y2-y3)}px。PNG SHA：{m['sha256']}。脚尖仍向左上纵深，手/盾/完整长杖保留。\n"
np.write_text(tx,encoding="utf-8")
print(json.dumps(a["supportContinuity"],ensure_ascii=False))

