from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
B=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
tech=json.loads((D/"technical.json").read_text(encoding="utf-8"))
notes={
"run-E-08-v6":{"target":"近笔肩仍起于颈下屏幕左侧；上臂和右袖在胸前延续到握笔手，白襟边更明确，后卷臂保持后缘穿出。不是强制全露胸饰。","drift":"头、双腿靴形及分腿相位稳定，主要变化为近肩/领边/袖纹和腰前饰细节。卷袖与青穗有轻微重绘；未见换手或新脚轴外翻。"},
"run-E-09-v5":{"target":"近笔肩与袖上臂重画成更连续的金边，窄白胸襟保留在近袖后的可见区域；左卷臂后摆并从身后接手。","drift":"保留原左屏后摆靴弯膝、右屏前靴落点方向。头/卷/墨灵有少量重绘和位置漂移，没有明显整体换相位。实际局部改动，不能声称逐像素固定。"},
"run-E-10-v5":{"target":"近笔肩颈下连接与跨胸袖遮挡保持，白领窄边和前腰饰方向更清楚；卷臂从后缘伸出，未为了露胸换肩。","drift":"前支撑靴和后弯膝靴相位保留；头、毛笔与卷边有少量重绘。笔尖接近右边，原生与1024高alpha触边均0，未见实质裁断。"}
}
items=[]
for t in tech:
 key=t["key"];p=B/t["file"];rp=p.with_suffix(".png.generation.json");rec=json.loads(rp.read_text(encoding="utf-8"))
 rec["review"]={"status":"candidate","reason":"Near brush shoulder/forward sleeve and front lapel revised against approved E05v5. Original leg phase preserved; root full sequence review pending."}
 rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 items.append({**t,"decision":"candidate_for_root_sequence_review","targetObservation":notes[key]["target"],"nonTargetDrift":notes[key]["drift"],"request":"provenance/"+key+".request.json","toolResult":"provenance/"+key+".tool-result.json","generationRecord":rp.relative_to(B).as_posix(),"generationRecordSha256":hashlib.sha256(rp.read_bytes()).hexdigest(),"comparison":key+"-before-after.jpg"})
def flat(im):
 bg=Image.new("RGBA",im.size,(216,222,214,255));bg.alpha_composite(im);return bg.convert("RGB")
keys=["run-E-05-v5","run-E-08-v6","run-E-09-v5","run-E-10-v5","run-E-11-v10"]
sheet=Image.new("RGB",(240*len(keys),270),(216,222,214));dr=ImageDraw.Draw(sheet)
for col,key in enumerate(keys):
 pic=Image.open(B/"staging"/(key+".png"));sheet.paste(flat(pic.resize((240,240),Image.Resampling.LANCZOS)),(col*240,0));dr.text((col*240+3,245),key,fill="black")
sheet.save(D/"05-08-09-10-11-candidates240.jpg",quality=96)
report={"reviewedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"candidates_static_reviewed_dynamic_pending","route":"builtin_image_gen","actualModel":None,"actualQuality":None,"styleReference":"D:/work/image/designs/jubaozhai-ui/02-characters.png","shoulderReference":"staging/run-E-05-v5.png","scope":"Only run E08 E09 E10 upper torso candidates. E11v10 already frozen separately. Runtime and acceptance untouched.","timing":{"frameCount":16,"frameMs":60,"cycleMs":960},"frames":items,"comparisonSet":"05-08-09-10-11-candidates240.jpg","runtimeModified":False,"acceptanceModified":False}
(D/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":report["status"],"frames":[{"key":x["key"],"sha256":x["sha256"],"generationRecordSha256":x["generationRecordSha256"]} for x in items]},ensure_ascii=False))
