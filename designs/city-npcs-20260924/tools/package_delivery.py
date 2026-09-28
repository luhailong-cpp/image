from pathlib import Path
import json,zipfile,datetime,hashlib
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
rows=[]
for e in m["entries"]:
    ex={r["size"]:r for r in e["export"]}
    rec=json.loads((ROOT/e["generationRecord"]).read_text(encoding="utf-8-sig"))
    pr=Path(e["generationRecord"]).parent/rec["prompt"]
    rows.append(f'| {e["id"]} | {e["name"]} | [2048]({ex[2048]["file"]}) · [1024]({ex[1024]["file"]}) | [原生]({e["raw"]}) | [生成记录]({e["generationRecord"]}) · [提示词]({pr.as_posix()}) |')
md="""# 五行奇谈 · 主城 NPC

按 designs 已确认的道家 Q 版手绘风格完成 **20 位截图主体 NPC + 3 位职业补全 NPC**。人物均为独立全身透明 PNG，适合主城摆放，也可复用于静态属性展示。本批交付静态素材，尚未接入客户端。

[查看总览](overview.jpg) · [深底验收](qa-dark.jpg) · [下载完整素材包](city-npcs-transparent-23.zip) · [机器可读清单](manifest.json) · [验收记录](validation.json)

![NPC 总览](overview.jpg)

## 取用

- `transparent-1024/`：1024×1024 RGBA，适合运行时导入。
- `transparent-2048/`：2048×2048 RGBA，供较大的展示画布使用。
- `characters/`：01—20 的原生图、实际提示词和逐图生成记录。
- `supplemental/`：21—23 的原生图、提示词和记录，明确标记为职业补全设计。

全部原生图片均为 **1254×1254**。2048 导出采用等比重采样和透明留边，不代表原生 2K 细节。导出只去除 Alpha≤3 的近乎不可见像素，再等比放入统一画布；完整服装和道具保留，原生文件不变。画布底部锚点为 `(0.5, 0.12)`（左下为原点），依据可见轮廓底部定位；主城接入时仍按实际脚底位置确认枢轴。

主参考为 [结伴同游](references/style-team-ui-v2.png)。身份参考为用户8张截图，已保存在 `references/`。少量朱红结绳、流苏、羽饰和金玉装饰统一在明亮、圆润、温润手绘的画法中。

## 逐图索引

| 编号 | NPC | 透明导出 | 原生图 | 来源与提示词 |
|---|---|---|---|---|
"""+"\n".join(rows)+"""

## 3 张职业补全稿

21 段铁心、22 云游大仙在截图中只露出名字和少量腿脚；根据锻造、云游职业语义补全了脸、服装和道具。23 店铺掌柜保留可见的红棕衣帽与圆胖体态，其正式 NPC 名称在截图中被截断，未补写未知姓名。这三张单独标为补全稿；不可见细节属于原创设计。

无想僧与无意僧按两位独立 NPC 制作，外形近似来自原参考设定。玩家、坐骑、称号与场景均未混入素材。

## 模型与生成记录

本批使用宿主内置 `image_gen`。官方已宣布 Images 2.5 向 Codex 开放；配置目标为 `gpt-image-2.5-sunburst / max`。工具未提供模型、质量或尺寸选择参数。PNG 的 C2PA 来源声明只报告 `softwareAgent = ChatGPT / gpt-image`，没有披露具体 2.5／2.0 版本或质量；记录中的 `actualModel` 仅保存这个系列名，`actualModelVersion`、`actualQuality` 为 `null`。未将配置、提示词或公告当作实际参数证明。

每张原生图有独立 `.generation.json` 和 `.provenance.json`，记录配置快照、实际提示词、输入参考、生成时间、哈希、返回字段与内嵌声明。C2PA 已解析，未验证数字签名。每张导出与总览有 `.derivation.json`，可追溯对应原生图。[官方核对与调用说明](model-check.md)。

两张未采用候选（屠娇娇长腿初稿、无意僧不透明初稿）连同独立记录保留在原生目录的 `candidates/`、`attempts/`，不在交付 PNG 或素材包内。

## 验收与复现

已核对全身完整性、角色辨识、浅深背景边缘、真实 Alpha、透明边距、逐图哈希和派生来源链。静态文件校验不代表已经完成战斗动画或主城引擎接入。

```powershell
python designs/city-npcs-20260924/tools/record_provenance.py
python designs/city-npcs-20260924/tools/build_delivery.py
python designs/city-npcs-20260924/tools/package_delivery.py
```

复现脚本只读取既有图片并整理导出，不调用图像模型。
"""
(ROOT/"README.md").write_text(md,encoding="utf-8")
bp=ROOT/"brief.md"
b=bp.read_text(encoding="utf-8")
b=b.replace("名单建立不表示图像已经完成。","当前成品和验收见 [交付说明](README.md)。")
b=b.replace("## deferred：信息不全，未列入本批完成名单","## 局部参考：另附职业补全设计")
b=b.replace("以上三位只标记 deferred，不计入 01—20 正式名单，不声称已经画完。","以上三位另按21—23制作职业补全稿，保留参考缺口说明；不可见细节为原创设计。")
b=b.replace("当前简报状态：20 名计划制作，3 名 deferred；完成数量以实际交付记录为准。","当前状态：20位主体NPC与3位职业补全NPC已交付；完成与来源索引见 README、manifest。")
bp.write_text(b,encoding="utf-8")
files={ROOT/n for n in ["README.md","manifest.json","roster.json","validation.json","brief.md","model-check.md","model-check.json","overview.jpg","overview.jpg.derivation.json","qa-dark.jpg","qa-dark.jpg.derivation.json"]}
for e in m["entries"]:
    rp=ROOT/e["raw"]; gp=ROOT/e["generationRecord"]
    files.update([rp,gp,rp.with_name(rp.name+".provenance.json")])
    rec=json.loads(gp.read_text(encoding="utf-8-sig"))
    files.add(gp.parent/rec["prompt"])
    for x in e["export"]:files.update([ROOT/x["file"],ROOT/x["derivation"]])
for p in (ROOT/"tools").glob("*.py"): files.add(p)
for p in (ROOT/"references").glob("*"): files.add(p)
archive=ROOT/"city-npcs-transparent-23.zip"
with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in sorted(files):
        if not p.exists():raise RuntimeError("Missing package source "+str(p))
        z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
    broken=z.testzip()
    if broken:raise RuntimeError("ZIP CRC error "+broken)
report={"archive":archive.name,"bytes":archive.stat().st_size,"sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),"fileCount":len(files),"npcCount":len(m["entries"]),"zipCRC":"passed","createdAt":datetime.datetime.now(datetime.timezone.utc).isoformat()}
(ROOT/"package-validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False))
