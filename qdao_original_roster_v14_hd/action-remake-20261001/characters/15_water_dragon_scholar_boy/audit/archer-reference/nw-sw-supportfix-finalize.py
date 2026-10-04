from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy")
A=B/"audit/archer-reference"
s=json.loads((A/"nw-sw-supportfix-selection.json").read_text(encoding="utf-8-sig"))
rows=s["rows"]
now=datetime.now(timezone.utc).isoformat()
checks=[]
errors=[]
for r in rows:
    p=Path(r["file"])
    with Image.open(p) as im:
        dims=list(im.size); mode=im.mode; alpha=list(im.getchannel("A").getextrema()) if mode=="RGBA" else None
    sha=hashlib.sha256(p.read_bytes()).hexdigest()
    record=B/r["generationRecord"]
    g=json.loads(record.read_text(encoding="utf-8-sig"))
    receipt=B/g["evidence"]["toolResult"]
    prompt=B/g["prompt"]
    result={"slot":r["slot"],"candidateKey":r["candidateKey"],"size":dims,"mode":mode,"alphaExtrema":alpha,"shaMatches":sha==r["sha256"],"generationExists":record.exists(),"receiptExists":receipt.exists(),"promptExists":prompt.exists(),"actualModel":g.get("actualModel"),"actualQuality":g.get("actualQuality")}
    checks.append(result)
    if dims!=[1254,1254] or mode!="RGBA" or alpha!=[0,255] or not all(result[k] for k in ("shaMatches","generationExists","receiptExists","promptExists")):
        errors.append(result)
new=[{"slot":r["slot"],"candidateKey":r["candidateKey"],"file":r["file"],"generationRecord":r["generationRecord"]} for r in rows if "supportfix" in r["candidateKey"]]
retained=[{"slot":r["slot"],"candidateKey":r["candidateKey"]} for r in rows if "supportfix" not in r["candidateKey"]]
newRecords=list((B/"provenance/generation").glob("run-NW-*-supportfix-v*.json"))+list((B/"provenance/generation").glob("run-SW-*-supportfix-v*.json"))
validation={"checkedAt":now,"scope":"选定 NW/SW 32 张候选的文件完整性；不是动态美术验收","selectedCount":len(rows),"uniqueShaCount":len({r["sha256"] for r in rows}),"newSelectedCount":len(new),"retainedCount":len(retained),"supportfixGenerationRecordCount":len(newRecords),"allSelected1254RGBA":not errors,"errors":errors,"rows":checks}
(A/"nw-sw-supportfix-validation.json").write_text(json.dumps(validation,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
issues=[
 {"id":"NW-position-09-10","slots":["run/NW/09","run/NW/10"],"detail":"右支撑足别已修正；09 到 10 的纵向相对足位仍有小幅前退，四段位置差异偏小。须父线程实际动态审核。"},
 {"id":"SW-pushoff-05-06","slots":["run/SW/05","run/SW/06"],"detail":"05/06 已从重复左支撑换为远右支撑，接地靴仍较接近身下，后侧推蹬幅度较弱。须动态审核是否达到身体经过支撑足的感觉。"},
 {"id":"NW-hand-11-12","slots":["run/NW/11","run/NW/12"],"detail":"沿用旧候选，11 到 12 扇手由后向前改变较大；本轮不宣称手部过渡已动态通过。"}
]
review={"updatedAt":now,"status":"candidate_ready_parent_dynamic_review","selection":"audit/archer-reference/nw-sw-supportfix-selection.json","selectedCount":32,"newSelectedCount":14,"retainedCount":18,"staticContactSheetsObserved":True,"dynamicPlaybackObserved":False,"clientIntegrated":False,"actualSupportIdentityObserved":{"NW":{"left":["15","16","01","02","03","04","05","06"],"right":["07","08","09","10","11","12","13","14"]},"SW":{"right":["15","16","01","02","03","04","05","06"],"left":["07","08","09","10","11","12","13","14"]}},"timing":{"frameMs":75,"cycleMs":1200,"interpretation":"同一支撑脚四个相对位置各两张独立图，另一足再接续；选定帧的支撑足别已复核，位置连续性仍须动态审核。"},"newSelections":new,"retainedSelections":retained,"openIssues":issues,"optionalNWPositionOrdering":{"applied":False,"warning":"位置更顺的备选顺序可能改变空手细节相位，须父线程动态决定，未静默套用。","mapping":{"run/NW/07":"run-NW-10-supportfix-v2","run/NW/08":"run-NW-08-supportfix-v4","run/NW/09":"run-NW-07-supportfix-v4","run/NW/10":"run-NW-09-supportfix-v1"}},"generation":{"route":"builtin image_gen.imagegen","configuredModel":"gpt-image-2.5-sunburst","configuredQuality":"max","actualModel":None,"actualQuality":None,"reason":"工具未提供型号/质量选择器，返回未披露；逐图请求、提示词与回执已记录。"},"writeBoundary":"仅候选 sources/new、逐图 provenance 与 audit/archer-reference；未写 runtime/master/共享 manifest/STATUS。"}
(A/"nw-sw-supportfix-review.json").write_text(json.dumps(review,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
md=["# NW / SW 支撑足修正最终候选交接","",f"更新：{now}","",
"本轮选定 32 张候选，其中 14 张新修、18 张沿用。已实际查看 2 张完整连图，支撑足别已核实；这是供父线程统一导出和动态审核的选帧，不是全角色完成声明。未在客户端接入，也未完成本子任务的浏览器动态验收。","",
"当前唯一选帧入口：nw-sw-supportfix-selection.json。旧 nw-sw-grounding-selection.json 仅保留为旧来源，旧 review 的通过结论不得继承。","",
"固定整张原图 1254×1254 缩为 940×940，放到 1024×1024 的 (42,49)；不得按每帧包围盒或最低像素重新对齐。16 帧 × 75ms = 1200ms。","",
"NW：左足支撑 15/16→01/02→03/04→05/06；右足支撑 07/08→09/10→11/12→13/14。SW：上述第一条为右足，第二条为左足。前/中/后仍是实际空间验收，不以标签充数。","",
"## 最终新候选","", "| 槽位 | 候选 |","|---|---|"]
md += [f'| {r["slot"]} | {r["candidateKey"]} |' for r in new]
md += ["","其余 18 张旧来源和 SHA 已原样带入 selection。32 张均有各自独立 SHA；完整文件检查见 nw-sw-supportfix-validation.json。","",
"## 必须如实保留的动态复审项",""]+[f'- {x["detail"]}' for x in issues]
md += ["","可选 NW 顺序（未应用）：07=NW10-supportfix-v2、08=NW08-supportfix-v4、09=NW07-supportfix-v4、10=NW09-supportfix-v1。这会使接地足相对位置更顺，但有手部相位代价；父线程须看动态后决定。","",
"## 预览与来源","",
"- nw-sw-supportfix-preview.html：两方向独立播放，默认 1×，75ms/帧；支持暂停与逐帧。",
"- nw-sw-NW-supportfix-contact.png、nw-sw-SW-supportfix-contact.png：最终 32 张静态连图。",
"- 新图走宿主内置 image_gen，目标 GPT Image 2.5 Sunburst / max。实际提交没有型号/质量选择器，实际返回值未披露，actualModel/actualQuality 保持 null。",
"- 28 张本轮 supportfix 生成候选均有逐图 request/prompt/receipt/generation 文字记录；入选 14 张。最终正式导出并确认引用完整后，由父线程统一清理不再需要的中间 PNG。",""]
(A/"nw-sw-supportfix-review.md").write_text("\n".join(md),encoding="utf-8")
old=A/"nw-sw-grounding-review.md"
content=old.read_text(encoding="utf-8-sig")
notice="> 已被 nw-sw-supportfix-review.md 与 nw-sw-supportfix-selection.json 取代；下文为旧候选审核记录，旧通过结论不可继承。\n\n"
if not content.startswith("> 已被"): old.write_text(notice+content,encoding="utf-8")
print(json.dumps({k:validation[k] for k in ("selectedCount","uniqueShaCount","newSelectedCount","retainedCount","supportfixGenerationRecordCount","allSelected1254RGBA","errors")},ensure_ascii=False))

