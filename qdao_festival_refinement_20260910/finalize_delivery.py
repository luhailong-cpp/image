"""Close the art delivery only after the final ledger verification passes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
B=Path(__file__).resolve().parent;R=B.parent
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):p.write_text(s,encoding="utf-8")
def save(p,j):write(p,json.dumps(j,ensure_ascii=False,indent=2)+"\n")
f=read(B/"final-verification.json");d=read(B/"decisions.json")
assert f["status"]=="passed" and not f["errors"] and d["pending_count"]==0
assert f["ledger_sha256"]==sha(B/"decisions.json") and f["inventory_sha256"]==sha(B/"inventory.json")
for sub in ["v9-edges","edge_exports"]:assert read(B/sub/"final-verification.json")["status"]=="passed"
audit=read(B/"decision-classification-audit.json")
assert len(audit.get("corrections",[]))>=19
assert audit["compatibility_27_verification"]["status"]=="passed"
assert read(B/"reviews/new-large-maps-review.json")["status"]=="passed"
now=datetime.now(timezone.utc).isoformat();old=read(B/"monitor-state.json")
H=B/"history";H.mkdir(exist_ok=True)
for name in ["README.md","monitor-state.json"]:
 out=H/("before-final-close-"+name)
 if not out.exists():shutil.copy2(B/name,out)
counts=d["decision_counts"];n=f["inventory_paths"];changed=counts.get("updated",0)
write(B/"README.md",f"""# 五行奇谈 · 全库节庆精修

2026-09-12：**图片库精修与验收已全部完成，待处理项为 0。** 整体保持道家 Q 版，春节、元宵、中秋仅作适量点缀。长期制作依据是[节庆方案](../docs/QDAO_FESTIVAL_REFINEMENT.md)和[UI 规范第 2 节](../qdao_ui_redesign_v5/UI_SPEC.md#2-统一视觉与控件层级)。

## 完成范围

最终清单覆盖 **{n:,} 个视觉文件**，其中 **{changed} 个现行图片／视觉导出路径更新**；符合风格的素材逐项记录保留理由，历史参考、真实运行截图和制作证据保留原貌。不能把清单总数理解为重绘张数。

[逐文件决定](decisions.json)覆盖全部路径，待处理 0 项；[最终验证](final-verification.json)通过 {f['current_files_checked']:,} 个现行素材、来源、派生及当前验收证据的哈希／完整性／画布核验，另核对 {f['protected_records_checked']:,} 个受保护记录的存在性（有绑定哈希的同时核对哈希）。风格目视审查和各批次 Alpha、帧序、重采样、图集／九宫格检查见下列证据。

| 批次 | 最终结果与入口 |
|---|---|
| 登录、选角 | [4 张正式 PNG](prelogin/publication.json)已发布；去除登录前九尾狐，登录主角居中，保留原文字和控件布局 |
| v11 八人及动作 | [最终验收](edge_exports/final-verification.json)：408 项媒体中修复 303 项、原样保留 105 项；补清月兔发梢色边，PNG Alpha、GIF 原透明合同、帧序和锚点保留，整包与当前图片一致 |
| v9 静态人物、主角别名与准备副本 | [最终验收](v9-edges/final-verification.json)：44 张 PNG 发布并更新人物总览；24 张来源、22 张准备副本及保留文件通过核对 |
| 场景、选服链和准备主角 | [逐文件发布](scenes-sync/per-file-decisions.json)：34 个路径核验，32 个更新、2 个纯控件层保留；包含 18 个场景／合成导出 |
| UI／物件导入准备 | [198 张 PNG](prepared-sync/publication.json)与当前权威来源同步，保留既有目标尺寸与各自缩放／九宫格配方 |
| 当前控件总览 | [4 个 PNG／SVG](component-overviews/publication.json)从当前控件重新生成，原页面几何和标签保留 |
| 新增三个地点及节庆版 | [六张大地图](../qdao_large_city_maps_20260912/README.md)与26个视觉文件纳入最后补充审查，按各地自然配色保留；原图及导出哈希通过 |\n| 已合适的素材 | [UI、物件、旧动作审查](reviews/ui-items-old-hero-review.md)、[人物与四宠](reviews/v9-pets-style-review.md)、[零散文件](remaining-misc-review.json)逐项记录保留；高清主城、36 张地图切片与五类场景沿用已验收节庆画法 |

上述批次中的派生关系和重复路径以逐文件账本去重。新增复查拼图、备份、脚本和 JSON 不计入 {changed} 个现行视觉更新路径。

## 风格与保留约束

道家 Q 版始终是主体：玉绿、象牙米白、桃木和细暖金，高清手绘，圆润比例但人物脸型、年龄、直发／束发／辫发、职业与法器各有区别。春节使用少量红绳、流苏；元宵使用局部花灯暖光；中秋使用月纹、玉兔、桂花。按用途选择，无须每张图同时加入三节符号。新增大地图按其最新地域定调保留灰蓝瓦、木色、石路和自然海岸配色；UI 的玉绿米白规范继续适用。

登录／选服／创角／选角保持无九尾狐；独立宠物及游戏内用途保留。地图道路、地标、战斗留白、切片接缝和正式路径保持。透明人物 RGB 修复不改 Alpha；准备 UI 沿用已验收 v10 来源的新轮廓，不能说旧皮肤 Alpha 完全不变；v9 准备副本按当前 RGBA 重采样，完全透明处的隐藏 RGB 变化已如实写入批次报告。

## 当前验收入口

- [completion.json](completion.json)：最终完成状态、核心证据哈希及监测收尾。
- [inventory.json](inventory.json)、[decisions.json](decisions.json)、[final-verification.json](final-verification.json)：盘点、每文件用途与最终只读验证。
- [来源分类复核](decision-classification-audit.md)：保留正在引用的原始图、27号现行兼容组装、当前网页和动作证据；原始谱系声明哈希与当前文件哈希分别记录。
- [monitor-state.json](monitor-state.json)：最终状态；此前逐小时进度在 [history](history/before-final-close-monitor-state.json) 中保留。

最初约定为**等待一次 5 小时，然后每小时检查**。前置出图已全部完成，本轮接续执行完毕；监测结束状态记录在 completion.json，不重新启动等待。

复查当前库可依次运行 `build_inventory.py`、`build_decisions.py`、`verify_decisions.py`；这是核查流程，不会重新生图。批次脚本、提示词、真实生成输出、before 备份和视觉验收均在相应子目录。旧生成器已按各自发布流程阻止回写旧皮肤。

本次结论覆盖图片仓库及仓库内导入准备文件。实际客户端接入、寻路和运行验收由其独立任务记录，不能由图片库完成推断。
""")
p=R/"docs/QDAO_FESTIVAL_REFINEMENT.md";s=p.read_text(encoding="utf-8-sig")
s=s.replace("2026-09-12 前置交付已全部验收，现已进入实际精修与逐批发布。","2026-09-12 前置交付、全库精修与最终验收已全部完成，待处理项为 0；最终结果见[全库精修交付](../qdao_festival_refinement_20260910/README.md)。")
a=s.index("2026-09-10 已完成[全库精修接续准备]");z=s.index("\n\n用户要求：",a)
s=s[:a]+"2026-09-12 已完成全库精修接续与验收，详见[最终交付](../qdao_festival_refinement_20260910/README.md)。以下记录原始调度与开工约定，作为历史保留；当前无需重新等待或继续监测。"+s[z:]
s=s.replace("6. 完成全部文件的处理与验收后交付结果并暂停该监测。","6. 完成全部文件的处理与验收后交付结果并结束该监测。")
s=s.split("## 当前批次：2026-09-12")[0]+"""## 最终交付：2026-09-12

全库图片精修完成。登录前整屏、人物透明边缘、场景／选服同源路径、UI 与物件准备副本和当前总览已发布；符合目标的地图、宠物、UI 与物件保留并写明理由。最终逐文件待处理 0 项，所有现行素材及来源、派生文件的哈希、图像完整性和画布验证通过。

[完成记录](../qdao_festival_refinement_20260910/completion.json) · [逐批说明与风格落实](../qdao_festival_refinement_20260910/README.md) · [最终验证](../qdao_festival_refinement_20260910/final-verification.json)。本轮完成范围为图片库及仓库内准备副本，客户端任务状态单独记录。
"""
write(p,s)
p=R/"README.md";s=p.read_text(encoding="utf-8-sig");a=s.index("2026-09-09 后续美术：");z=s.index("\n\n",a)
s=s[:a]+"2026-09-12 全库节庆精修已完成：[最终交付与逐文件验收](qdao_festival_refinement_20260910/README.md)。整体保持道家 Q 版，春节／元宵／中秋适量点缀；登录前整屏、人物边缘、场景与准备副本已更新，待处理项为 0。长期风格继续遵守[节庆方案](docs/QDAO_FESTIVAL_REFINEMENT.md)。"+s[z:];write(p,s)
p=R/"docs/WUXING_QITAN_HANDOFF.md";s=p.read_text(encoding="utf-8-sig");first,rest=s.split("\n",1)
s=first+"\n\n2026-09-12 最新图片入口：[全库节庆精修已完成](../qdao_festival_refinement_20260910/README.md)，逐文件待处理为 0。人物 v9／v11、场景、登录前整屏及有效导出以本轮最终验收为准；下文各日期为历史交付与客户端专项范围。新素材继续保持道家 Q 版及少量春节／元宵／中秋点缀。\n"+rest;write(p,s)
p=R/"docs/QDAO_ART_DIRECTION.md";s=p.read_text(encoding="utf-8-sig");first,rest=s.split("\n",1)
s=first+"\n\n2026-09-12：本轮[全库节庆精修](../qdao_festival_refinement_20260910/README.md)已完成；当前来源、透明导出与同源副本以该最终验收入口为准。下文早期尺寸与来源描述保留其历史日期，长期画法约束继续沿用。\n"+rest;write(p,s)
p=R/"qdao_ui_style_recut_v10/README.md";s=p.read_text(encoding="utf-8-sig").replace("[全库节庆精修](../qdao_festival_refinement_20260910/README.md)正在接续","[全库节庆精修](../qdao_festival_refinement_20260910/README.md)已完成并通过最终验证");write(p,s)
state={"schema_version":3,"updated_at_utc":now,"phase":"complete","all_images_complete":True,"images_edited_by_this_task":changed,"style":old.get("style"),"latest_visual_constraints":old.get("latest_visual_constraints"),"generation_gate_open":True,"prerequisites_complete":True,"refinement_started_utc":old.get("refinement_started_utc"),"completed_at_utc":now,"last_check_kind":"user_requested_continuation","inventory_count":n,"pending_count":0,"refinement":{"status":"complete","all_images_complete":True,"quality_recheck_28_required":False,"decision_ledger":"decisions.json","final_verification":"final-verification.json"},"automation_id":"automation","automation_status":"awaiting_cleanup","original_schedule":"One initial five-hour wait, then hourly checks; no renewed delay.","history":"history/before-final-close-monitor-state.json","completion":"completion.json","client_accessed":False,"next_step":None}
save(B/"monitor-state.json",state)
core=["inventory.json","decisions.json","final-verification.json","v9-edges/final-verification.json","edge_exports/final-verification.json","decision-classification-audit.json","reviews/new-large-maps-review.json","prelogin/publication.json","prepared-sync/publication.json","scenes-sync/per-file-decisions.json","component-overviews/publication.json"]
completion={"schema":"qdao.festival.completion.v1","status":"complete","completed_utc":now,"all_images_complete":True,"inventory_paths":n,"updated_visual_paths":changed,"current_files_checked":f["current_files_checked"],"protected_records_checked":f["protected_records_checked"],"pending_count":0,"style":"Daoist chibi overall; restrained Spring Festival, Lantern Festival and Mid-Autumn accents.","automation":{"id":"automation","status":"awaiting_cleanup"},"core_evidence":[{"path":name,"sha256":sha(B/name)} for name in core],"client_accessed":False,"scope":"Repository art and in-repository import preparations; external client work remains independently tracked."}
save(B/"completion.json",completion)
print(json.dumps({"status":"complete","paths":n,"updated":changed,"pending":0,"automation":"awaiting_cleanup"}))
