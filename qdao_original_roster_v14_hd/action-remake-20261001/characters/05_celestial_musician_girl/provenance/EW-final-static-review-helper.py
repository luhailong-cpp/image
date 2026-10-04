from pathlib import Path
import json, hashlib
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parents[1]
OUT = "provenance/EW-visible-anatomy-foot-heading-review-20261003.json"
def read(rel):
    return json.loads((BASE / rel).read_text(encoding="utf-8-sig"))
def write(rel, obj):
    (BASE / rel).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
def sha(rel):
    return hashlib.sha256((BASE / rel).read_bytes()).hexdigest()

selected = [r for r in read("candidate-selection.json") if r["direction"] in ("E","W") and r["action"] in ("run","attack","cast","hit")]
assert len(selected) == 100
assert next(r for r in selected if (r["action"],r["direction"],r["frame"])==("attack","W",9))["file"] == "staging/attack/W-09-v3.png"
assert next(r for r in selected if (r["action"],r["direction"],r["frame"])==("cast","W",8))["file"] == "staging/cast/W-08-v3.png"
assert next(r for r in selected if (r["action"],r["direction"],r["frame"])==("hit","E",3))["file"] == "staging/hit/E-03-v5.png"

native_views = {
    ("run","E"):set(range(1,17)), ("run","W"):set(range(1,17)),
    ("attack","W"):set(range(1,13)),
    ("attack","E"):{1,3,4,5,6,7,12},
    ("cast","E"):{1,7,8,9,10,16},
    ("cast","W"):{1,3,6,7,8,9,14,15,16},
    ("hit","E"):{1,2,3,4,6}, ("hit","W"):{1,3,6}
}
special = {
    ("run","E",12):"后腿鞋尖下压属于蹬离时踝跖屈；鞋底可见不是向外旋转，保留。",
    ("run","W",12):"后足蹬离时鞋尖向下/后跟抬起，仍沿W所在矢状面；不把鞋底显露判外八。",
    ("attack","W",9):"v3已把远解剖RIGHT靴由朝镜头的正面鞋头改为明确W侧面，鞋尖在踝左、鞋跟在右；近LEFT靴、站距和双臂不变。v2拒用。",
    ("cast","W",8):"v3近LEFT肩的大袖跨琴连上端握手；抬至胸前的小手来自后层独立袖口，可读作远RIGHT。远上臂遮挡，无明确第三手/错接。两鞋W向。v1/v2错误近臂低弦拒用。",
    ("cast","W",14):"v2最新原生图已看；回到中性身体量级与16近似，两鞋尖W向，近LEFT上握/远RIGHT下弦。",
    ("cast","W",15):"v2最新原生图已看；回到中性身体量级与16近似，双靴并拢但鞋头均在各自踝左侧，无外八。",
    ("hit","E",3):"v5最新原生图已看；较旧v4恢复头/身体/支持靴量级，后仰抬腿保留，两手归属和E向鞋尖正确。旧v4比例疑点已解决。",
    ("attack","W",4):"远靴有三分之四短缩，但鞋尖仍在踝左、后跟在右；不能仅因看到鞋头正面就等同原W09-v2的外撇。",
    ("attack","W",5):"扩步和远靴短缩保留，鞋头朝W左下、后跟在右侧；未见反向外撇。右指首次明确触下弦，身体前压为出力强调。",
    ("attack","W",6):"右手越过琴尾离弦，属于05后的下拨随势，宽站距不是脚掌偏航。",
    ("cast","W",6):"双膝下蹲、远手高腕蓄势，双鞋头都在踝左方；站距扩大仍沿W，非外八。",
    ("cast","W",7):"远右腕从高位向面前上弦下降，近左臂持上端保持；双鞋W向并承重。"
}
findings = {
    ("run","E"):("近RIGHT下弦、远LEFT上端持琴，在跑步中保持双手角色；未見第三手/额外腿。", "支撑/前摆鞋头向E；后摆跖屈和鞋底显露按动作解释，没有需重画的明确外撇。"),
    ("run","W"):("近LEFT肩肘腕跨琴连上端，远RIGHT低弦；选用W10v5等已排除错臂/相位拒稿。", "支持/前摆鞋头朝W；前后错脚与后腿屈曲不等同外八，暂无明确必须重画帧。"),
    ("attack","E"):("近RIGHT拨下弦、远LEFT稳上端，抬腕到下拨的两手归属连续。", "两靴的鞋尖均沿E，前压扩步时膝踝与鞋向连贯。"),
    ("attack","W"):("近LEFT跨琴上握、远RIGHT拨下弦，01–12可读；没有明确多肢。", "W09v3修复唯一明确朝镜头外撇；其余远鞋短缩仍保留W左向，近鞋沿W。"),
    ("cast","E"):("近RIGHT抬腕/下拨、远LEFT持上琴，两臂角色无交换。", "双鞋E向，09前压扩步保留；没有通过收窄双腿伪装修鞋。"),
    ("cast","W"):("近LEFT跨琴上握，远RIGHT抬胸/下拨；08v3后层小手可读，远上臂被遮挡，未声称全关节裸露。", "两鞋W向；06/07下蹲扩步、14/15收回并足均可读，未见需修外撇。"),
    ("hit","E"):("近RIGHT下弦/远LEFT上端，后仰和抬腿中持琴不换手；03v5替换比例偏小旧图。", "支持靴及抬起靴仍向E，后仰不是鞋尖反向。"),
    ("hit","W"):("近LEFT跨琴上握，远RIGHT低弦；抬腿及后仰阶段未见第三手/额外腿。", "可见鞋头均向W，远靴短缩保留；未见明确外撇。")
}
rows=[]
selection_sources={"candidate-selection.json"}
for r in selected:
    a,d,f=r["action"],r["direction"],r["frame"]
    actual=sha(r["file"])
    assert actual == r["sha256"], (a,d,f,"candidate image hash mismatch")
    rec_hash=sha(r["generationRecord"])
    rec=read(r["generationRecord"])
    advertised=rec.get("sha256")
    if advertised:
        assert advertised == actual, (a,d,f,"generation record hash mismatch")
    source=r.get("selectionSource") or "candidate-selection.json"
    selection_sources.add(source)
    rows.append({
        "action":a,"direction":d,"frame":f,"file":r["file"],
        "sha256":actual,"generationRecord":r["generationRecord"],
        "generationRecordSha256":rec_hash,"generationRecordDirectImageHashMatches":advertised==actual if advertised else None,
        "selectionSource":source,
        "inspection":"native_single_frame_and_sequence_contact_sheet" if f in native_views[a,d] else "sequence_contact_sheet",
        "visibleArmsReview":"no_obvious_topology_error_in_visible_regions",
        "feetReview":"no_definite_outward_splay",
        "recommendation":"preserve_current_selected_frame",
        "notes":special.get((a,d,f),findings[a,d][1]),
        "dynamicPassClaimed":False
    })
rows.sort(key=lambda r:({"run":0,"attack":1,"cast":2,"hit":3}[r["action"]],r["direction"],r["frame"]))
canonical=json.dumps([{k:r[k] for k in ("action","direction","frame","file","sha256")} for r in rows],ensure_ascii=False,separators=(",",":")).encode()
doc={
    "schemaVersion":1,"reviewer":"finish_ew","reviewedAt":datetime.now(timezone.utc).isoformat(),
    "scope":"E/W run16 each, attack12 each, cast16 each, hit6 each; static visible anatomy and foot heading, not final runtime acceptance",
    "reviewStatus":"completed_static_review_no_further_mandatory_source_redraw",
    "selectedImageCount":len(rows),
    "selectedEWImageSetSha256":hashlib.sha256(canonical).hexdigest(),
    "imageSetDigestDefinition":"SHA256 of UTF-8 compact JSON array ordered run/attack/cast/hit then E/W then frame, keys action,direction,frame,file,sha256, ensure_ascii=false separators comma/colon",
    "sourceSelectionFiles":[{"file":s,"sha256":sha(s)} for s in sorted(selection_sources)],
    "method":{
        "visualEvidence":"All frames reviewed on sequence contact sheets; owned run E/W and attack W single-frame native views during production; explicit latest/key native views identified per row. Only visible limb connections judged.",
        "headingCriteria":"由鞋头相对踝/鞋跟的朝向、膝踝连线和近远遮挡判断；不是按屏幕左右机械分腿，也不是把前后错脚、踝跖屈或露鞋底都判外八。",
        "proportionCriteria":"比较头、躯干和靴的共同量级，区分扩步/前压/后仰造成轮廓变化；不用bbox归一化。",
        "selectionBinding":"本审阅只对rows中的文件字节有效；后续任意源图替换需重新检查对应槽，不因文件名相同自动继承。",
        "mutations":"本次只写审阅JSON及私有helper，未改源图/选帧表。W09v3是此前授权AI修图并已进入选表。"
    },
    "clips":[{"action":a,"direction":d,"arms":findings[a,d][0],"feet":findings[a,d][1],"staticRecommendation":"preserve_current_selection"} for a in ("run","attack","cast","hit") for d in ("E","W")],
    "events":{
        "attackE":{"firstVisibleStringContact":4,"bodyForceAccent":5,"followThrough":[6,7]},
        "attackW":{"firstClearStringContact":5,"bodyForceAccent":5,"releaseOffStrings":6,"lateFollowThrough":7,"basis":"04远RIGHT指悬于弦上；05指落下段弦面并身体前压扩步；06手越琴尾离弦。依据原生图04v1/05v2/06v1，非照抄提示词。"},
        "castE":{"windupPeak":7,"stringApproach":8,"releaseAccent":9,"followThrough":10},
        "castW":{"windupPeak":6,"descendingPreparation":[7,8],"clearLowStringContactAccent":9,"followThrough":10}
    },
    "resolvedSourceIssues":[
        {"action":"attack","direction":"W","frame":9,"selected":"staging/attack/W-09-v3.png","rejected":"staging/attack/W-09-v2.png","resolution":"远RIGHT靴外撇改W侧向；正确近靴/手臂/站距保留。"},
        {"action":"cast","direction":"W","frame":8,"selected":"staging/cast/W-08-v3.png","resolution":"独立第二眼可读近LEFT上握、远RIGHT抬胸；上臂局部遮挡，未见明确错接。"},
        {"action":"hit","direction":"E","frame":3,"selected":"staging/hit/E-03-v5.png","rejected":"staging/hit/E-03-v4.png","resolution":"原生复看确认整体偏小问题已恢复。"}
    ],
    "unresolvedMandatoryStaticRedraws":[],
    "remainingOutsideThisStaticReview":[
        "由根代理在全段固定R与统一scale导出后检查正常倍速/真实合成，确认接触保持、相位节奏和片段衔接。",
        "客户端世界移动速度与脚步周期同步、攻击命中时刻属于运行整合，不以本静态检查冒充已通过。",
        "被琴/袖/头发遮住的远侧肩肘骨骼不可直接看见；结论只覆盖可见拓扑没有明确矛盾。"
    ],
    "rows":rows
}
write(OUT,doc)

# Update private earlier reviews so they no longer describe superseded files as current.
seqrel="provenance/attack/W-sequence-review-20261003.json"
seq=read(seqrel)
seq["reviewedAt"]=doc["reviewedAt"]
seq["staticFindings"][1]="逐图和整段连图已目视。采用W01v2,W02v3,W03v1,W04v1,W05v2,W06v1,W07v1,W08v1,W09v3,W10v2,W11v1,W12v1。"
seq["staticFindings"].append("W09v3已修复远RIGHT靴朝镜头外撇；原生图复看，鞋尖改向W，正确近靴/手臂保留。")
seq["forceAccentMarker"]={"frame":5,"basis":"明确触下弦并扩步前压；06已离弦随势。"}
seq["shaBoundStaticReview"]=OUT
seq["unresolved"]=["整段固定根1024导出后的正常360ms/段动态及真实合成由根代理复核。","未在本审阅中验证客户端命中时刻和世界移动同步。"]
write(seqrel,seq)

regrel="provenance/registration-landmarks-review.json"
reg=read(regrel)
if not any(x["id"]=="cast/W/16" for x in reg["landmarks"]):
    lm=dict(next(x for x in reg["landmarks"] if x["id"]=="cast/W/1"))
    lm.update({"id":"cast/W/16","frame":16,"file":"staging/cast/W-16-v1.png","observation":"末尾中性原生图已看；颈约585,590、髋约610,945，与01同量级同轴，支持cast W整段固定根。"})
    reg["landmarks"].append(lm)
reg["scope"]["landmarkedImages"]=len(reg["landmarks"])
for root in reg["clipRoots"]:
    if root["action"]=="cast" and root["direction"]=="W":
        root["status"]="provisional_reviewed"
        root["evidenceLandmarkIds"]=["cast/W/1","cast/W/3","cast/W/16"]
        root["basis"]="首尾中性01/16颈/髋轴相近，03蓄势轴相近；支持整段R(610,1185)，释放期真实前压保留。"
for lm in reg["landmarks"]:
    if lm["id"]=="hit/E/3":
        lm["status"]="historical_rejected_version_not_current_root_evidence"
        lm["supersededBy"]="staging/hit/E-03-v5.png"
        lm["observation"] += " 当前v5已另外实看恢复量级；旧v4坐标仅保留审阅历史，不用于当前配准。"
reg["sequenceStaticReview"]["hitEW"]["scaleIssue"]={
    "fileReviewed":"staging/hit/E-03-v5.png","previousFile":"staging/hit/E-03-v4.png",
    "finding":"最新v5已原生实看，头/身体/支持靴共同量级恢复，后仰姿态与正确手脚保留。",
    "status":"resolved_in_selected_v5"
}
reg["sequenceStaticReview"]["overall"]="可见手臂/肢体未见明确多肢或换手；最新静态脚向和比例结论以SHA绑定审阅为准。"
reg["sequenceStaticReview"]["shaBoundFinalStaticReview"]=OUT
reg["footDirectionReview"]={"status":"completed_static_review","file":OUT,"finding":"E/W已选100图无剩余明确必须重画的外撇；attack W09已选修复v3。动态/客户端另验。"}
reg["implementationProposal"]["rules"][-1]="cast W首尾01/16已复核同一中性轴；释放前压和扩步严格保留，全段固定R不变。"
reg["implementationProposal"]["uniformScaleSafety"] += " 根代理已报告按0.65完成固定R复核导出；最终全图容纳审计由其导出清单记录，本标注文档不改动其结果。"
reg["latestStaticReviewAt"]=doc["reviewedAt"]
write(regrel,reg)
print(json.dumps({"review":OUT,"reviewSha256":sha(OUT),"selectedEWImageSetSha256":doc["selectedEWImageSetSha256"],"rows":len(rows),"registrationSha256":sha(regrel),"attackWSelectionSha256":sha("provenance/attack/selection-W.json"),"runEWSelectionSha256":sha("provenance/run/selection-EW.json")},ensure_ascii=False))

