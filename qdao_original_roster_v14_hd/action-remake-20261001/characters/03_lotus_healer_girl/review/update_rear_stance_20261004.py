from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/03_lotus_healer_girl")
now=datetime.now(ZoneInfo("America/New_York")).isoformat()
edits=[
("SE",4,"04-v4","04-v3",1191,[530,1143],["近右后支撑鞋跟降低，完整鞋底平放，膝踝有压缩；远左腿保持折起","鞋长轴指向SE，与小腿走向一致，未见明确外翻","当前近右肩→前景袖→灯、远左臂→后瓶保持"],["鞋底从1209上移至1191（18px），是本次实际生成变化，未作贴地","头顶45保持，肩袖/持物链保留；03→04支撑位置推进仍偏大"]),
("SE",12,"12-v3","12-v2",1183,[470,1131],["远左后脚由斜翘脚跟改为较完整的平鞋底，膝部回收产生承重压缩","近右前膝/鞋保持抬起；足尖沿SE，未见明确外翻","头脸、右灯左瓶上身链保留"],["鞋底1209→1183（26px），鞋中心约向右收70px；后侧支撑仍清楚","11→12头和摆臂原有跨度保留，本次不改正确上身"]),
("SW",4,"04-v3","04-v2",1197,[714,1141],["近左后鞋降低脚跟，前后底面更完整，膝屈支撑；远右脚保持抬起","鞋尖沿SW，与支撑小腿方向一致，未见明确外翻","近左袖→瓶、远右臂→灯保持"],["头脸较目标略向左移约30px、头顶43→39；非程序平移","支撑鞋底1207→1197（10px），上身比例和完整人物保持"]),
("SW",12,"12-v3","12-v2",1198,[860,1141],["远右后脚鞋跟降低、底面更平，屈膝踝承重；近左抬脚保留","鞋尖沿SW，未见明确膝踝外翻","右灯左瓶及完整白裤保持"],["鞋底1201→1198（3px），头顶71→68；原帧边缘余量小仍保留","11→12后支撑推进较大；本次仅改支撑腿"])
]
for d,slot,name,old,bottom,center,obs,issues in edits:
 p=B/"generation"/d/(name+".png")
 rec=json.loads(p.with_name(p.name+".generation.json").read_text(encoding="utf-8"))
 r={"reviewedAt":now,"source":str(p).replace("\\","/"),"sourceSha256":rec["sha256"],"actualView":True,"selection":"selected_for_clearer_rear_flat_support","previousSelected":old+".png","observations":obs,"issues":issues,"measured":{"canvas":[1254,1254],"alphaGt8Bounds":rec["alphaGt8Bounds"],"supportShoeBottomY":bottom,"supportShoeCenterApprox":center},"supportPosition":"rear","supportContact":"heel_and_ball_flat_loaded_pose","visualAccepted":False,"validationScope":"static native image plus same-canvas consecutive sequence; does not claim perfect registration"}
 p.with_suffix(".review.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
 rec["status"]="selected_candidate";rec["review"]=r
 p.with_name(p.name+".generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
 inp=B/"review"/("run-"+d+"-sequence-input.json")
 dat=json.loads(inp.read_text(encoding="utf-8-sig"))
 f=next(x for x in dat["frames"] if x["slot"]==slot)
 assert Path(f["source"]).stem==old,(d,slot,f["source"])
 f.update(source=str(p).replace("\\","/"),sourceSha256=rec["sha256"],observedPhase=obs[0],contactType="rear_flat_loaded_support",isFlight=False,issues=issues,nativeCanvas=[1254,1254],alphaGt8Bounds=rec["alphaGt8Bounds"],durationMs=75,visualAccepted=False,footAxisObservation=obs[1],supportPosition="rear",supportReview=str(p.with_suffix(".review.json")).replace("\\","/"))
 dat["updatedAt"]=now
 dat["durationMs"]=1200
 dat["stanceAudit"]={"reviewedAt":now,"interpretation":"current provisional reading: front 01/09; middle 02/03/10/11; rear04/12; four consecutive stance images per foot","stanceRuns":[{"slots":[1,2,3,4],"durationMs":300,"foot":"right" if d=="SE" else "left"},{"slots":[9,10,11,12],"durationMs":300,"foot":"left" if d=="SE" else "right"}],"actualGroundedPoseRuns":[[1,2,3,4],[9,10,11,12]],"basis":"visible low planted outsole, knee/ankle load chain and opposite folded leg; no relabeling of flight as support","rearSupportEdits":[4,12],"exactlyEightGroundedFramesAccepted":False,"spatialDistributionAccepted":False,"remaining":["02/03/10 early-middle spatial progression is modest and needs full sequence comparison","SW15/16 retain actual early contact and cannot be counted as flight" if d=="SW" else "SE13 is already early flight; SE05 forefoot push remains a pose with depth registration uncertainty"],"visualAccepted":False}
 inp.write_text(json.dumps(dat,ensure_ascii=False,indent=2),encoding="utf-8")
# Regenerate only direction-specific review previews from current input; no frame translation/rescaling within its canvas.
for d in ("SE","SW"):
 dat=json.loads((B/"review"/("run-"+d+"-sequence-input.json")).read_text(encoding="utf-8"))
 assert dat["frames"][10]["source"].endswith("11-v3.png" if d=="SE" else "11-v4.png")
 if d=="SW": assert dat["frames"][2]["source"].endswith("03-v3.png")
 sheet=Image.new("RGB",(1024,1144),(239,238,229));draw=ImageDraw.Draw(sheet);anim=[]
 for i,f in enumerate(dat["frames"]):
  im=Image.open(f["source"]).convert("RGBA");assert im.size==(1254,1254)
  small=im.resize((256,256),Image.Resampling.LANCZOS)
  x=(i%4)*256;y=(i//4)*286
  sheet.paste(small,(x,y+30),small)
  draw.text((x+6,y+6),f'{d}{i+1:02d} 75ms',(35,60,55))
  # fixed diagnostic root line, not a claim all depth positions share this y
  ry=y+30+round(dat["nativeRoot"][1]*256/1254)
  draw.line((x,ry,x+255,ry),fill=(150,98,92))
  bg=Image.new("RGBA",(256,256),(239,238,229,255));bg.alpha_composite(small);anim.append(bg)
 sheet.save(B/"review"/("run-"+d+"-contact.jpg"),quality=95)
 anim[0].save(B/"review"/("run-"+d+"-trial.apng"),save_all=True,append_images=anim[1:],duration=[75]*16,loop=0,disposal=0,blend=0)
 print(d,[(f["slot"],Path(f["source"]).name) for f in dat["frames"] if f["slot"] in [3,4,11,12]])

