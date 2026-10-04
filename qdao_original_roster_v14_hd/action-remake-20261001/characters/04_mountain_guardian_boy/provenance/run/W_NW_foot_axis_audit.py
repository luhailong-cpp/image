from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
from PIL import Image
R=Path("D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy")
now=datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
wnotes=[
"前脚鞋尖朝左，后脚抬跟俯仰随小腿，未见外旋反拧。",
"左向前掌平压，踝膝自然连接；后脚回收，不以露鞋面视作外撇。",
"保留主窗口新修平掌承重稿；趾左跟右，与小腿自然相接。",
"前脚收膝踝部下压，后脚趾向左下随蹬离方向；未见横向拧脚。",
"抬膝脚尖俯向左下，后侧蹬离，鞋轴随各自小腿。",
"前靴趾向左，后靴随屈膝俯仰；鞋底露出不代表外旋。",
"伸出靴趾向左，后脚回收俯向下；未见反向趾轴。",
"落地前脚跟领先、趾左向，另一脚回收。",
"接触脚趾左跟右，另一脚跟抬起，左右相位可辨。",
"左向平掌压低，后脚自然屈起，保留。",
"支撑鞋趾向左，后收脚随胫骨折叠，保留。",
"换步前脚趾左上、后脚趾左下，属于踝俯仰而非外旋。",
"收腿双靴趾左下随小腿，无脚踝横向反拧，保留。",
"前靴左向展开，后靴收起，保留。",
"前脚趾左向，后脚跟抬起；保持。",
"前靴趾左向预备接触，后脚自然屈收；循环脚向可接01。"
]
nnotes=[
"定点修复画面右靴：旧稿趾向右；本稿后跟在近处偏右、趾向左上纵深，保留初接触与原腿距。",
"定点修复右承重靴：旧稿平掌但鞋尖向右；本稿跟近趾远向左上，保留膝压缩和支撑。",
"右支撑靴后跟可见，趾端向左上缩短，小腿与踝自然相接，保留。",
"前腿收膝，后腿露底蹬离；鞋底展示是俯仰，不判为外旋。",
"抬膝与后踝伸展配合，双靴底方向随小腿，保留。",
"腾空双腿屈曲，两靴底朝后可见，未见与小腿横向拧转。",
"后腿伸展露底、前腿收起；趾跟纵轴随运动纵深，保留。",
"前靴向左上预摆，后靴露底回收；未见向右的错误鞋尖。",
"左平掌支撑趾朝左上、跟右下，右后脚露底；保留。",
"左脚压缩支撑，跟趾纵轴随左上运动；保留。",
"左支撑后跟近、趾向左上缩短，右脚屈收；保留。",
"左脚脚跟抬起、前掌趾向左上，另一腿通过；保留。",
"左后靴露底，右前靴后跟可见且未明显外撇；保留。",
"双腿腾空屈收，鞋底随胫骨方向展示；保留。",
"远侧靴被衣摆部分遮挡，无明确反向鞋尖；不根据不可见部位猜测修改。",
"定点修复右预接触靴：后跟朝近处，趾端向远处左上，不再侧向右撇；保留原腿距与准备接触相。"
]
fix={1:"NW_01_foot_axis_attempt02",2:"NW_02_foot_axis_attempt01",16:"NW_16_foot_axis_attempt01"}
for direction,notes in [("W",wnotes),("NW",nnotes)]:
    frames=[]
    for i,note in enumerate(notes,1):
        p=R/"frames/run"/direction/f"frame_{i:02d}.png"
        mp=p.with_suffix(".generation.json");m=read(mp);s=sha(p)
        assert m["sha256"]==s
        with Image.open(p) as im:assert im.size==(1024,1024) and im.mode=="RGBA"
        assert (R/m["nativeSource"]["path"]).exists()
        if direction=="NW" and i in fix:
            assert fix[i] in m["nativeSource"]["path"]
            # Preserve the slot's existing timing declaration, undo registrar default 30.
            older=m
            while "runTiming" not in older and older.get("replacement",{}).get("retiredRecord"):
                older=read(R/older["replacement"]["retiredRecord"])
            if "runTiming" in older:
                m["frameDurationMs"]=older.get("frameDurationMs")
                m["runTiming"]=older["runTiming"]
            m["review"]={"status":"visual_passed","scope":"static_single_frame_and_foot_axis_only","automaticallyApproved":False,"reviewedAt":now,"reviewedSha256":s,"observation":note,"dynamicAcceptance":"pending_parent_grounded720_and_quarter_speed_review","note":"真实查看生成返回及1024正式图；脚向修复未以缩腿距替代，动态/客户端未在此确认。"}
            m["nativeSource"]["fileRetained"]=True
            m["nativeSource"]["retentionNote"]="保留至主窗口动态审查，当前不清理。"
            write(mp,m)
        frames.append({"frame":i,"file":p.relative_to(R).as_posix(),"sha256":s,"decision":"ai_corrected" if direction=="NW" and i in fix else "retained","observation":note,"nativeSource":m["nativeSource"],"modelQualityEvidence":{"target":m.get("submissionConfigTarget"),"submittedModel":m.get("submittedParameters",{}).get("model"),"submittedQuality":m.get("submittedParameters",{}).get("quality"),"actualModel":m.get("actualModel"),"actualQuality":m.get("actualQuality")}})
    audit={"schemaVersion":1,"character":"04_mountain_guardian_boy","direction":direction,"reviewedAt":now,"scope":"static_foot_axis_review","criterion":"按运动朝向看足跟→趾尖轴与小腿自然对齐；区分回收露底/踝俯仰和横向外旋；不缩两腿间距代替脚向。","referencePolicy":"07仅只读透视对照，用户已撤回整套/垂直方向通过，无金标方向可照搬。","method":"实际查看当前逐帧全画布接触表、单帧全分辨率并结合本窗口上一轮已看的单帧；只修明确错误。","correctedFrames":[1,2,16] if direction=="NW" else [],"retainedCount":13 if direction=="NW" else 16,"staticVerdict":"本轮确定外撇已修；其余未发现明确脚踝反拧而保留。","dynamicAcceptance":"pending_parent_review_of_grounded720_and_grounded_slow","clientIntegration":"not_integrated","frames":frames}
    write(R/f"provenance/run/{direction}_foot_axis_review_20261003.json",audit)
    np=R/f"RUN_{direction}_NOTES.md";text=np.read_text(encoding="utf-8")
    old="已提供640/720/800ms三档试播；normal采用720ms候选，slow采用其0.25倍。480ms旧值已撤为旧基线，正式客户端时长未批准。GIF用40/50ms交替实现720ms，不复制或插值姿态。"
    new="已提供640/720/800ms三档试播；当前统一预览改用720ms承重加权候选，逐帧[40,70,60,40,40,30,30,50]×2，grounded_slow为其0.25倍。480ms仅旧基线，720ms仍待动态/客户端批准；不复制或插值姿态。"
    text=text.replace(old,new).replace("当前预览：","早期过程预览（本节旧来源在后续修图后不再用于最终验收）：")
    text+="\n## 2026-10-03 最新脚向复核\n\n"+("W16帧均保留。主窗口W03新承重稿已实际查看，趾左跟右；其余前掌顺左向，后摆靴的露底/下压是俯仰，未发现确定外旋反拧。\n" if direction=="W" else "仅NW01、02、16发现画面右靴鞋尖向右外撇，已通过真实内置AI定点转正为后跟近、鞋尖向左上纵深；膝位、腿距、步态、杖盾与握持保持。NW01首次编辑仍有右侧趾轮廓，第二次已去除，采用attempt02；02/16采用attempt01。其余13帧保留。\n")
    text+="\n07只作透视对照，不作为验收金标。修图实际传入目标帧、07同向正式帧、本角色identity、NW idle与designs风格共5张。目标2.5 Sunburst/max，提交与返回版本/质量仍为未确认null。\n" if direction=="NW" else "\n07只作透视对照，不作为验收金标；本方向本轮没有新增AI编辑。\n"
    text+=f"\n当前SHA审查：provenance/run/{direction}_foot_axis_review_20261003.json。统一预览：preview/run_{direction}_contact.png、run_{direction}_grounded720.gif、run_{direction}_grounded_slow.gif。正常步频、接地持续时间与相邻连续性由主窗口动态复核；未接入客户端。当前原生图保持，不在本轮清理。\n"
    np.write_text(text,encoding="utf-8")
cp=R/"provenance/audit/combat_phase_review.json";c=read(cp)
changed=[f["file"] for f in c["frames"] if sha(R/f["file"])!=f["sha256"]]
assert not changed,changed
c["footAxisReview"]={"reviewedAt":now,"scope":"read_only_static_contact_sheets_and_key_frames","method":"重新实看hit/attack/cast E/W六组接触表；全尺寸复看hit E/W03、attack E/W06、cast E10/W08/W10，结合先前phase原尺寸帧。","frameBindings":"本报告frames中68张当前SHA经再次校验未改变。","decision":"retain_combat_frames_no_confirmed_pathological_ankle_yaw","reason":"前掌顺出手/受击朝向，后脚适度外开与宽弓步或马步对应的膝向一致，未确认脚踝相对胫骨反拧。战斗稳定站距不按跑步收窄，也不强行让双靴平行。","qualification":"这是一轮静态脚向判断，不冒称68张都在本次重新全尺寸逐张查看；全组以当前contact覆盖，关键与可疑脚掌另用全尺寸确认。动态和客户端仍由主窗口处理。","pngChanged":False}
write(cp,c)
mp=cp.with_suffix(".md");tx=mp.read_text(encoding="utf-8")
tx+="\n## 最新脚向只读复核\n\n六组当前接触表重新查看，重点全尺寸核对hit E/W03、attack E/W06、cast E10/W08/W10，并结合此前phase全尺寸查看。68张原绑定SHA再次检查未变。前掌顺出手/受击方向，后脚适度外开与膝向及宽弓步/马步相符，未确认脚踝相对小腿反拧，全部保留。不能用缩战斗腿距或强制双脚平行代替脚向判断。覆盖方式为全组contact加重点全尺寸，不冒称本次68张全尺寸重新查看；不修改PNG/source/sidecar。\n"
mp.write_text(tx,encoding="utf-8")
print(json.dumps({"runAuditCount":32,"nwCorrected":list(fix),"combatUnchanged":len(c["frames"]),"timing":"preserved prior slot metadata; weighted preview defined by root"},ensure_ascii=False))

