from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime
from zoneinfo import ZoneInfo
import json
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/03_lotus_healer_girl")
now=datetime.now(ZoneInfo("America/New_York")).isoformat()
E=[
("SE",15,"15-v3","15-v2","远左支撑腿向后下伸、支撑鞋移至髋后，低跟向前掌滚动；近右脚继续前伸离地",["支撑鞋约向viewer-left后移110px，底1181→1156，上身保持；后侧深度及接触注册仍有25px变化","较13/14实际后伸已可辨；膝踝仍有屈曲，未见明确外翻"],[393,1156]),
("SE",16,"16-v6","16-v5","远左腿进一步后下伸，支撑鞋后移且脚跟抬起、前掌保持低位承重；近右前脚保持抬起",["支撑鞋约向viewer-left后移170px，底1198→1167；是实际生成变化，未程序贴地","比15再向后约40px，末段伸腿推地更清楚；仍为单帧姿态接触判读"],[361,1167]),
("SW",7,"07-v6","07-v5","近左支撑腿从身下伸向髋后，鞋向viewer-right后移、低跟前掌承重；远右前脚仍抬起",["支撑鞋约后移190px，底1208→1175；后侧透视深度改变，非整图平移","05/06→07原向身下回收问题已改善，鞋轴仍沿SW"],[911,1175]),
("SW",8,"08-v3","08-v2","近左腿继续伸向后下方，抬跟以前掌作末支撑；远右前脚维持前伸准备换脚",["支撑鞋约向viewer-right后移240px，底1170→1162；略高8px不单独认定腾空","比07再向后约30px、踝伸展更明显，头脸约左移20px；正确持物链保持"],[950,1162])
]
for d,s,n,old,obs,issues,point in E:
 p=B/"generation"/d/(n+".png");rec=json.loads(p.with_name(p.name+".generation.json").read_text(encoding="utf-8"))
 r={"reviewedAt":now,"actualView":True,"source":str(p).replace("\\","/"),"sourceSha256":rec["sha256"],"selection":"selected_after_actual_rear_progression_improvement","observations":[obs,"完整白裤、长波浪发、右灯左瓶肩袖链保留","后足纵轴随方向；单独露底不当作外八"],"issues":issues,"measured":{"alphaGt8Bounds":rec["alphaGt8Bounds"],"rearContactPointApprox":point},"visualAccepted":False}
 p.with_suffix(".review.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8");rec.update(status="selected_candidate",review=r);p.with_name(p.name+".generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
 inp=B/"review"/("run-"+d+"-sequence-input.json");dat=json.loads(inp.read_text(encoding="utf-8-sig"));f=next(f for f in dat["frames"] if f["slot"]==s)
 assert Path(f["source"]).stem==old
 f.update(source=str(p).replace("\\","/"),sourceSha256=rec["sha256"],observedPhase=obs,contactType="rear_forefoot_loaded_pose",isFlight=False,issues=issues,nativeCanvas=[1254,1254],alphaGt8Bounds=rec["alphaGt8Bounds"],supportPosition="rear_terminal",supportReview=str(p.with_suffix(".review.json")).replace("\\","/"),durationMs=75)
 dat["updatedAt"]=now;inp.write_text(json.dumps(dat,ensure_ascii=False,indent=2),encoding="utf-8")
 oldp=B/"generation"/d/(old+".png.generation.json");oldrec=json.loads(oldp.read_text(encoding="utf-8"));oldrec["status"]="superseded_by_clearer_rear_progression";oldrec["supersededBy"]=str(p.relative_to(B)).replace("\\","/");oldp.write_text(json.dumps(oldrec,ensure_ascii=False,indent=2),encoding="utf-8")
md=["# SE/SW 连续支撑最终实际矩阵","",f"更新：{now}。本轮input稳定，不再改图；总导出由root统一处理。","",
"最新要求：每半圈同一支撑脚连续8张，前/身下/稍后/末后四位置各两张独立姿态，再换脚。SE右1–8/左9–16；SW左1–8/右9–16。16×75ms=1200ms。",
"已完成每向8个必要槽局部修改，加4个末段针对性改善；此前04/12平底承重修正保留。当前是16张独立来源，不做整图平移、复制补帧或插值。",
"实图可读同侧连续支撑；四位置之间的距离不按数学等距验收。SE03仍偏前，04/12已进入较后位置；SE05/06及13/14组内推进有限。末段新SE15/16、SW07/08已明确后伸，比前稿改善。末段鞋底随生成及后侧透视有所上移（最多33px）；保留较大接触注册变化，未仅凭8–15px变化认定腾空。","",
"|向/槽|当前图|计划位置|实际支撑/动作|实际不足|","|---|---|---|---|---|"]
for d in ("SE","SW"):
 inp=B/"review"/("run-"+d+"-sequence-input.json");dat=json.loads(inp.read_text(encoding="utf-8-sig"))
 dat["stanceAudit"].update(reviewedAt=now,revisionStatus="stable_for_root_rebuild",fourPositionSpatialProgressionAccepted=False,terminalProgressionImproved=True,remaining=["SE03相对02推进小；04/12较早进入后侧，各位置跨度不均","SE15/16、SW07/08末段后伸已实际改善；后鞋深度/注册上移8–33px保留记录","SW16前鞋接近后鞋高度，可能双支撑交接；单帧髋遮挡使全圈腿归属仍需动态核对"],visualAccepted=False)
 dat["issues"]=["独立原生1254 RGBA完整；每槽75ms，总1200ms","最新连续8张同脚支撑图已齐，四位置跨度不完全均匀","头身/道具注册仍有少量变动，已知手交换图均排除","离线像素和来源完整，不以技术检查替代动态验收"]
 dat["updatedAt"]=now;inp.write_text(json.dumps(dat,ensure_ascii=False,indent=2),encoding="utf-8")
 sheet=Image.new("RGB",(1024,1144),(239,238,229));draw=ImageDraw.Draw(sheet);anim=[]
 for i,f in enumerate(dat["frames"]):
  p=Path(f["source"]);im=Image.open(p).convert("RGBA");sm=im.resize((256,256),Image.Resampling.LANCZOS);x=(i%4)*256;y=(i//4)*286
  sheet.paste(sm,(x,y+30),sm);draw.text((x+6,y+6),f'{d}{i+1:02d} {p.stem} 75ms',(35,60,55))
  ry=y+30+round(dat["nativeRoot"][1]*256/1254);draw.line((x,ry,x+255,ry),fill=(150,98,92))
  bg=Image.new("RGBA",(256,256),(239,238,229,255));bg.alpha_composite(sm);anim.append(bg)
  md.append(f'|{d}{i+1:02d}|{p.name}|{f["plannedSupportPosition"]}|{f["observedPhase"]}|{"；".join(f["issues"])}|')
 sheet.save(B/"review"/("run-"+d+"-contact.jpg"),quality=95)
 anim[0].save(B/"review"/("run-"+d+"-trial.apng"),save_all=True,append_images=anim[1:],duration=[75]*16,loop=0,disposal=0,blend=0)
 print(d,",".join(Path(f["source"]).stem for f in dat["frames"]))
(B/"review"/"run-SE-SW-continuous-support-matrix.md").write_text("\n".join(md),encoding="utf-8")

