from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/03_lotus_healer_girl")
now=datetime.now(ZoneInfo("America/New_York")).isoformat()
C={"SE":{5:"05-v2",6:"06-v2",7:"07-v3",8:"08-v2",13:"13-v2",14:"14-v4",15:"15-v2",16:"16-v5"},"SW":{5:"05-v3",6:"06-v2",7:"07-v5",8:"08-v2",13:"13-v2",14:"14-v4",15:"15-v2",16:"16-v2"}}
special={
("SE",5):["支撑脚比04稍后，膝压缩；平足承重，非旧前掌飞离"],
("SE",6):["支撑鞋稍回身下，05→06水平推进不严格；接地姿可读"],
("SE",7):["后脚已落下但主要仍平足，末段前掌滚动不足"],
("SE",8):["后脚已伸后支撑，白裤覆盖前脚踝；最后蹬地的踝伸展不足"],
("SE",13):["后左脚已落下，右脚前摆；较12支撑位置变化小"],
("SE",14):["后左腿伸下，前右腿折起；同侧承重但与13后移差别小"],
("SE",15):["后左脚接地，但13→15支撑水平递后不足，待针对性编辑"],
("SE",16):["后左脚已真实伸下至1198，右前鞋抬起；较15未明显递后，待针对性编辑"],
("SW",5):["后近左脚全掌落下，底1220低于04约23px；无程序贴地"],
("SW",6):["后近左脚落下，前右脚抬高；支撑底1222，注册不同"],
("SW",7):["后近左脚已下伸至1208；05→07支撑反向向身下收，待针对性编辑"],
("SW",8):["近左后脚落下、前右脚抬起；较07又向身下收，末段推地不足，待针对性编辑"],
("SW",13):["远右后脚降跟承重，近左脚前摆；与12较接近"],
("SW",14):["远右后腿伸下、近左前膝折起；同脚承重"],
("SW",15):["远右后腿伸下，近左前脚离地；支撑底1165略高，透视注册仍有变化"],
("SW",16):["远右后腿伸下；前左鞋已接近后鞋高度，可能双支撑交接，不能宣称纯单脚"]
}
md=["# SE/SW 连续支撑实际矩阵（2026-10-04）","最新要求：同脚连续8张，四位置各两张；SE右1–8/左9–16，SW左1–8/右9–16。16张独立来源，每张75ms。","此矩阵记录当前实际像素；空间位置未全部验收，关键末段继续局部修。","","|向/槽|当前图|实际支撑|实际不足|","|---|---|---|---|"]
for d,choices in C.items():
 inp=B/"review"/("run-"+d+"-sequence-input.json");dat=json.loads(inp.read_text(encoding="utf-8-sig"))
 for slot,name in choices.items():
  p=B/"generation"/d/(name+".png");rec=json.loads(p.with_name(p.name+".generation.json").read_text(encoding="utf-8"))
  support=("right" if d=="SE" else "left") if slot<=8 else ("left" if d=="SE" else "right")
  pos="slightly_rear" if slot in (5,6,13,14) else "rear_terminal"
  obs=("近" if slot<=8 else "远")+("右" if support=="right" else "左")+"后腿实际伸下承重；另一腿前摆抬起；双腿完整白裤"
  issues=special[(d,slot)]
  r={"reviewedAt":now,"actualView":True,"source":str(p).replace("\\","/"),"sourceSha256":rec["sha256"],"selection":"selected_support_candidate_pending_spatial_review","observedSupportFoot":support,"observedPhase":obs,"contactEvidence":"low broad coherent outsole; extended loaded hip-knee-ankle chain; other leg elevated","footAxisObservation":"鞋纵轴随"+d+"行进方向，未见明确膝踝外翻；未以露底等同外八","upperBodyObservation":"当前上身/右灯左瓶及完整人物保留，未程序平移缩放","measured":{"alphaGt8Bounds":rec["alphaGt8Bounds"]},"issues":issues,"visualAccepted":False}
  p.with_suffix(".review.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
  rec.update(status="selected_candidate",review=r);p.with_name(p.name+".generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
  f=next(x for x in dat["frames"] if x["slot"]==slot)
  f.update(source=str(p).replace("\\","/"),sourceSha256=rec["sha256"],observedPhase=obs,observedSupportFoot=support,contactType="loaded_rear_support",isFlight=False,durationMs=75,startMs=(slot-1)*75,issues=issues,nativeCanvas=[1254,1254],alphaGt8Bounds=rec["alphaGt8Bounds"],supportPosition=pos,visualAccepted=False,supportReview=str(p.with_suffix(".review.json")).replace("\\","/"),footAxisObservation=r["footAxisObservation"])
 for f in dat["frames"]:
  s=f["slot"];idx=(s-1)%8;f["plannedSupportPosition"]=["front","front","under_body","under_body","slightly_rear","slightly_rear","rear_terminal","rear_terminal"][idx]
  md.append(f'|{d}{s:02d}|{Path(f["source"]).name}|{f.get("observedPhase","")}|{"；".join(f["issues"])}|')
 dat["updatedAt"]=now;dat["durationMs"]=1200
 dat["stanceAudit"]={"reviewedAt":now,"requirement":"same support foot continuously grounded eight independent frames, four positions each two poses, then alternate","stanceRuns":[{"slots":list(range(1,9)),"foot":"right" if d=="SE" else "left","durationMs":600},{"slots":list(range(9,17)),"foot":"left" if d=="SE" else "right","durationMs":600}],"continuousLoadedPoseReading":True,"fourPositionSpatialProgressionAccepted":False,"remaining":["SE15/16 terminal progression insufficient; SW07/08 reverse movement toward body; targeted edits ongoing"],"visualAccepted":False}
 dat["contactEvents"]=[{"slot":s,"atMs":(s-1)*75,"event":event,"basis":"current actual planted pose; exact four-position spacing under review"} for s,event in [(1,"first_foot_front_contact"),(3,"first_foot_underbody_support"),(5,"first_foot_rear_load"),(7,"first_foot_terminal_load"),(9,"opposite_foot_front_contact"),(11,"opposite_foot_underbody_support"),(13,"opposite_foot_rear_load"),(15,"opposite_foot_terminal_load"),(17,"next_cycle_contact")]]
 dat["events"]=[dict(e,frame=e["slot"],type=e["event"],timeMs=e["atMs"]) for e in dat["contactEvents"]]
 inp.write_text(json.dumps(dat,ensure_ascii=False,indent=2),encoding="utf-8")
 # exactly same canvas for comparison
 sheet=Image.new("RGB",(1024,1144),(239,238,229));draw=ImageDraw.Draw(sheet);anim=[]
 for i,f in enumerate(dat["frames"]):
  im=Image.open(f["source"]).convert("RGBA");sm=im.resize((256,256),Image.Resampling.LANCZOS);x=(i%4)*256;y=(i//4)*286
  sheet.paste(sm,(x,y+30),sm);draw.text((x+6,y+6),f'{d}{i+1:02d} {Path(f["source"]).stem} 75ms',(35,60,55))
  ry=y+30+round(dat["nativeRoot"][1]*256/1254);draw.line((x,ry,x+255,ry),fill=(150,98,92))
  bg=Image.new("RGBA",(256,256),(239,238,229,255));bg.alpha_composite(sm);anim.append(bg)
 sheet.save(B/"review"/("run-"+d+"-contact.jpg"),quality=95)
 anim[0].save(B/"review"/("run-"+d+"-trial.apng"),save_all=True,append_images=anim[1:],duration=[75]*16,loop=0,disposal=0,blend=0)
for d,n,reason in [("SE","16-v3","后脚仍折起偏高，不能作为连续支撑"),("SE","16-v4","后脚底仍偏高于前鞋，连续后足承重不足"),("SW","07-v4","后脚底约1149，较同腿承重位置高约60px")]:
 p=B/"generation"/d/(n+".png");rec=json.loads(p.with_name(p.name+".generation.json").read_text(encoding="utf-8"))
 r={"reviewedAt":now,"actualView":True,"source":str(p),"sourceSha256":rec["sha256"],"selection":"not_selected","issues":[reason],"visualAccepted":False}
 p.with_suffix(".review.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8");rec.update(status="not_selected",review=r);p.with_name(p.name+".generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
(B/"review"/"run-SE-SW-continuous-support-matrix.md").write_text("\n".join(md),encoding="utf-8")
print("Input stable snapshot and matrix saved. Four targeted terminal edits remain.")

