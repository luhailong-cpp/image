# 冰剑少女私有导出与连播工具

本目录只服务 `01_ice_sword_girl`。脚本不会扫描其他角色、选择最高版本、改移动素材或把制作完成视为客户端验收。依赖本机已有 Pillow，无需安装依赖。

## 输入

`example-existing3.partial.json` 是读取三张历史候选的工具示例，不是正式美术选稿。正式选表放本角色目录内任意独立 JSON，内容形状相同：

```json
{
  "schemaVersion": 1,
  "character": "01_ice_sword_girl",
  "status": "partial",
  "exportTransform": {
    "mode": "normalized_whole_canvas",
    "contentScale": 0.88,
    "offsetByDirection": {"E": [61, 61], "W": [61, 61]}
  },
  "sequences": [
    {"action": "hit", "direction": "E", "status": "partial", "frames": [
      {"frame": 1, "file": "staging/hit-E-01-v1.png", "generationRecord": "provenance/receipts/hit-E-01-v1.json", "sha256": "原图实际SHA256"}
    ]},
    {"action": "hit", "direction": "W", "status": "partial", "frames": []},
    {"action": "attack", "direction": "E", "status": "partial", "frames": []},
    {"action": "attack", "direction": "W", "status": "partial", "frames": []},
    {"action": "cast", "direction": "E", "status": "partial", "frames": []},
    {"action": "cast", "direction": "W", "status": "partial", "frames": []}
  ]
}
```

每个槽必须指定实际文件、实际来源 JSON、SHA；`frame` 为从 1 开始的槽号。缺槽保留为空缺，不拿邻帧或重复源顶替。所有六组必须出现，哪怕其中一组目前是空数组。单组齐全后可标 `complete`；发布要求顶层与六组全部 `complete`、68 个槽齐全。

源与记录路径支持角色相对路径、批次内 `characters/01_ice_sword_girl/...` 或角色内绝对路径。来源中的提示词和参考路径允许仓库内只读引用。检查 source/receipt/selection SHA、原生尺寸、生成时间证据、配置/提交/返回值区分、提示词与参考文件存在性。派生记录逐级验证 `derivedFrom` 和 operation。

## 固定整体变换

只接受原生不小于 1024 的方形 RGBA PNG。整张原生画布等比缩至 `round(1024 * contentScale)`，再放到对应方向固定的 `[x,y]` 偏移。全部动作使用同一个比例，每个方向使用固定偏移；1254 和其他原生方形尺寸按同一归一化画布处理。程序不根据每帧包围盒缩放、居中、旋转、变形、镜像或补帧。

示例的 0.88 / [61,61] 仅是候选预检参数，选表作者须通过实际动作比较确认比例和根位置；不代表已通过视觉验收。包围盒仅用于透明/裁切检查。导出不去除半透明边缘；像素重复检查忽略 alpha≤8 的微弱噪声，并检查原图与成品的完全相同可见像素、裁切后完全相同像素、裁切后水平镜像。该检查不能证明姿态独立，也不能发现所有经过扰动的抄帧。

## 调用

以下从仓库根运行；将正式选表路径与每次新的预览路径按实际改好：

```powershell
$py = 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$character = 'D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/01_ice_sword_girl'
$exporter = "$character/tools/export_ice_sword_girl.py"

# 只读预检，partial 可通过已选帧检查，但 complete 始终为 false。
& $py $exporter --selection "$character/selection.json"

# 私有预览，目录必须不存在；支持 partial，并明确显示缺槽。
& $py $exporter --selection "$character/selection.json" --preview-dir "$character/preview/review-01"

# 仅68槽完整后正式导出；不覆盖已有 runtime 或逐图派生回执。
& $py $exporter --selection "$character/selection.json" --publish
```

可附 `--report <本角色目录内不存在的JSON路径>` 保存预检记录。所有输出在角色范围内，已存在的预览目录、报告、runtime 图和派生记录均拒绝覆盖。所有图片先在内存完成验证再写。若写入中途发生系统错误，保留已落盘部分并人工检查，不自动删除或覆盖。

发布输出标准 `runtime/<hit|attack|cast>/<E|W>/<两位帧号>.png` 与 `provenance/receipts/derived/<action>-<direction>-<frame>.json`。回执包括源图/源记录/选表 SHA、原生与导出尺寸、固定变换、像素检查与 pending 视觉状态。

## 连播

打开生成的 `preview/.../index.html`。提供当前段播放、六段连续播放、六段循环、逐帧与 0.5× 慢放；深浅底同时播放。正常速度 hit=40ms、attack=30ms、cast=45ms；慢放时全部时长翻倍，页面始终显示当前速度、帧时长与段时长。

页面先预载所有存在帧，以 `requestAnimationFrame` 和实际经过时间控制顺序；缺槽以占位显示并占用自己的时长，不补帧。进入后台自动暂停。播放日志记录每段目标时长和实际显示过的不同帧数；显示刷新率可能使快速播放跳帧，应结合慢放与逐帧检查。播放日志不自动构成美术通过结论。

截至工具初验，仅用历史 E hit 01/03/06 完成来源、透明、固定导出内存预检：3 已选、65 缺槽、0 发布。详见 `preflight-existing3.json`。未生成新的动作图，未写 staging/runtime/prompts/receipts；尚未执行完整六段视觉验收，客户端未接入、未测试。
