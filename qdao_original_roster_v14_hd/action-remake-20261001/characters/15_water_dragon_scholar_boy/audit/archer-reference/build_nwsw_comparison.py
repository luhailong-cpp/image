from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
A=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl")
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy")
O=B/"audit/archer-reference"; O.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",20)
allrows=[]
for d in ["NW","SW"]:
 for start in [1,5,9,13]:
  sheet=Image.new("RGB",(1024,1136),(228,231,226));draw=ImageDraw.Draw(sheet)
  for k,i in enumerate(range(start,start+4)):
   for col,(char,base) in enumerate([("09",A),("15",B)]):
    p=base/"runtime/run"/d/f"{i:02}.png";im=Image.open(p).convert("RGBA")
    # whole canvas 256; no per-character box normalization or geometry edits
    thumb=im.resize((256,256),Image.Resampling.LANCZOS)
    x=(k%2)*512+col*256;y=(k//2)*568
    # 512 high enlarged view, preserving whole square source ratio
    s=im.resize((256,256),Image.Resampling.LANCZOS)
    sheet.paste(s,(x,y+32),s)
    draw.text((x+6,y+5),f"{char} {d} {i:02}",font=font,fill=(20,45,38))
    lower=im.crop((256,512,1024,1024))
    lower.thumbnail((256,256),Image.Resampling.LANCZOS)
    sheet.paste(lower,(x,y+300),lower)
    draw.text((x+6,y+480),"腿脚区域（只裁看）",font=font,fill=(20,45,38))
    allrows.append({"character":char,"direction":d,"slot":i,"file":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size":list(im.size)})
  sheet.save(O/f"compare-{d}-{start:02}-{start+3:02}.png")
(O/"comparison-inputs.json").write_text(json.dumps({"operation":"只读正式runtime；全画布等比缩略+下半身查看裁切，不改变任何成品或选表","files":allrows},ensure_ascii=False,indent=2),encoding="utf8")
print("8 comparison sheets written; 64 runtime frames captured")

