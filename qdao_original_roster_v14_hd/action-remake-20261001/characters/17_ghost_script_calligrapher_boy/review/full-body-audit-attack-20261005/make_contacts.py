from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,datetime
B=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
def flatten(im):
    bg=Image.new("RGBA",im.size,(216,222,214,255));bg.alpha_composite(im);return bg.convert("RGB")
rows=[]
for direction in ["E","W"]:
    for start in [1,7]:
        sheet=Image.new("RGB",(3*400,2*432),(236,235,227)); dr=ImageDraw.Draw(sheet)
        feet=Image.new("RGB",(3*450,2*305),(236,235,227)); fd=ImageDraw.Draw(feet)
        arms=Image.new("RGB",(3*450,2*390),(236,235,227)); ad=ImageDraw.Draw(arms)
        for j,n in enumerate(range(start,start+6)):
            p=B/"runtime/attack"/direction/f"{n:02d}.png"; im=Image.open(p);im.load()
            assert im.size==(1024,1024) and im.mode=="RGBA"
            rows.append({"slot":f"attack-{direction}-{n:02d}","file":p.relative_to(B).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
            label=f"{direction}{n:02d}"+(" CONTACT" if n==6 else "")
            x,y=(j%3)*400,(j//3)*432
            sheet.paste(flatten(im.resize((400,400),Image.Resampling.LANCZOS)),(x,y));dr.text((x+6,y+405),label,fill="black")
            x,y=(j%3)*450,(j//3)*305
            feet.paste(flatten(im.crop((80,555,960,1010)).resize((450,233),Image.Resampling.LANCZOS)),(x,y));fd.text((x+6,y+242),label+" fixed feet crop",fill="black")
            x,y=(j%3)*450,(j//3)*390
            arms.paste(flatten(im.crop((20,300,1015,970)).resize((450,303),Image.Resampling.LANCZOS)),(x,y));ad.text((x+6,y+311),label+" fixed shoulder/hand crop",fill="black")
        stem=f"{direction}-{start:02d}-{start+5:02d}"
        sheet.save(D/(stem+"-whole400.jpg"),quality=95)
        feet.save(D/(stem+"-feet.jpg"),quality=95)
        arms.save(D/(stem+"-hands.jpg"),quality=95)
(D/"sources.json").write_text(json.dumps({"createdAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"diagnosticOnly":True,"frames":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("24 actual PNGs read; four whole / feet / hand sets written")

